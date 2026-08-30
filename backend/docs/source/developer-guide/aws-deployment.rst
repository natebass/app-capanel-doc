.. meta::
   :description lang=en: Hosting the California Accountability Panel on AWS with research files in S3.

Deploying on AWS
================================================================

The point of this deployment is that new assessment data arrives by **uploading
a file to a bucket**.  Nothing is parsed on a workstation and no database dump
is pushed: the research files live in S3, the application reads them from there,
and an import turns them into rows.

Architecture
------------

.. mermaid::

   flowchart LR
       CDE["caaspp-elpac.ets.org<br/>research files"] -->|download once per year| S3[("S3<br/>ca-panel-resources")]
       S3 -->|s3:ObjectCreated| EB[EventBridge rule]
       EB --> IMPORT["ECS task<br/>ingest_research_files.py"]
       IMPORT -->|COPY| RDS[("RDS PostgreSQL")]
       API["ECS service<br/>FastAPI"] --> RDS
       ALB[Application Load Balancer] --> API
       CF[CloudFront] --> ALB
       CF --> WEB[("S3<br/>frontend build")]
       USER((Browser)) --> CF

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Piece
     - Service
   * - Research files
     - S3 bucket, versioned, private.
   * - Database
     - RDS for PostgreSQL 16 or later.
   * - API
     - ECS Fargate service behind an Application Load Balancer.
   * - Importer
     - The same container image, run as a one-off ECS task.
   * - Frontend
     - Static build in S3, served through CloudFront.
   * - Secrets
     - Secrets Manager for the database URL and application secret key.

The importer runs as a separate task rather than inside the API service because
a statewide administration takes minutes and gigabytes of I/O to load, and
should not compete with request traffic or be bounded by a request timeout.

The bucket
----------

Create a private, versioned bucket and lay the research files out by
administration year:

.. code-block:: text

   s3://ca-panel-resources/
     research-files/
       2024/
         sb_ca2024_all_csv_ela_v1.zip
         sb_ca2024_all_csv_math_v1.zip
         cast_ca2024_all_csv_v1.zip
         caa_ca2024_all_csv_v1.zip
         caas_ca2024_all_csv_v1.zip
         csa_ca2024_all_csv_v1.zip
       2025/
         ...

The prefix structure is for humans; the importer recurses and identifies each
file from its name and header.  Keep the published file names.

.. code-block:: bash

   aws s3api create-bucket \
     --bucket ca-panel-resources \
     --region us-west-2 \
     --create-bucket-configuration LocationConstraint=us-west-2

   aws s3api put-public-access-block \
     --bucket ca-panel-resources \
     --public-access-block-configuration \
     "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

   aws s3api put-bucket-versioning \
     --bucket ca-panel-resources \
     --versioning-configuration Status=Enabled

   aws s3api put-bucket-encryption \
     --bucket ca-panel-resources \
     --server-side-encryption-configuration \
     '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

Uploading a new administration is then one command:

.. code-block:: bash

   aws s3 sync ./resources/california-state s3://ca-panel-resources/research-files/2026/ \
     --exclude "*" --include "*_ca2026_*"

Versioning matters here: if the state republishes a corrected file, the previous
version stays recoverable, and the importer notices the new entity tag and
reloads that file automatically.

Lifecycle
~~~~~~~~~

Research files are cold after they have been imported.  A lifecycle rule keeps
storage cheap without losing the source of truth:

.. code-block:: json

   {
     "Rules": [
       {
         "ID": "archive-research-files",
         "Filter": {"Prefix": "research-files/"},
         "Status": "Enabled",
         "Transitions": [
           {"Days": 60, "StorageClass": "STANDARD_IA"},
           {"Days": 180, "StorageClass": "GLACIER_IR"}
         ],
         "NoncurrentVersionExpiration": {"NoncurrentDays": 365}
       }
     ]
   }

.. warning::

   Objects in Glacier Instant Retrieval can be read directly, but if you move
   files to Glacier Flexible Retrieval or Deep Archive the importer will fail on
   them until they are restored.  Stop at Glacier Instant Retrieval unless you
   are prepared to restore before re-importing.

IAM
---

The task role needs read access to the prefix and nothing else:

.. code-block:: json

   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "ReadResearchFiles",
         "Effect": "Allow",
         "Action": ["s3:GetObject"],
         "Resource": "arn:aws:s3:::ca-panel-resources/research-files/*"
       },
       {
         "Sid": "ListResearchFiles",
         "Effect": "Allow",
         "Action": ["s3:ListBucket"],
         "Resource": "arn:aws:s3:::ca-panel-resources",
         "Condition": {"StringLike": {"s3:prefix": ["research-files/*"]}}
       },
       {
         "Sid": "ReadSecrets",
         "Effect": "Allow",
         "Action": ["secretsmanager:GetSecretValue"],
         "Resource": "arn:aws:secretsmanager:us-west-2:*:secret:capanel/*"
       }
     ]
   }

The application uses the default credential chain, so on ECS the task role is
picked up automatically — no keys in the environment.

The database
------------

.. code-block:: bash

   aws rds create-db-instance \
     --db-instance-identifier capanel \
     --engine postgres \
     --engine-version 17.4 \
     --db-instance-class db.t4g.medium \
     --allocated-storage 100 \
     --storage-type gp3 \
     --db-name capanel \
     --master-username capanel_admin \
     --manage-master-user-password \
     --no-publicly-accessible \
     --backup-retention-period 7

Sizing notes:

* Two administration years of every test occupy roughly **8.4 GB** — 4.9 GB in
  ``assessment_subscores`` and 3.5 GB in ``assessment_results``, about half of
  each being index.  Allow around 4 GB per additional year, plus headroom for
  the staged copy an import holds while it swaps the new rows in and for
  autovacuum to reclaim the replaced ones.
* Imports are write-heavy and short.  ``db.t4g.medium`` with gp3 storage is
  enough for a nightly or annual import; if imports are frequent, raise
  ``max_wal_size`` so the load does not force constant checkpoints.
* Reporting queries are index lookups over a narrow key, so read performance
  depends far more on having the indexes than on instance size.

Run migrations before the first import:

.. code-block:: bash

   aws ecs run-task \
     --cluster capanel \
     --task-definition capanel-migrate \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-…],securityGroups=[sg-…]}"

where the task definition's command is ``uv run alembic upgrade head``.

The import task
---------------

Register a task definition that runs the importer with the same image as the
API:

.. code-block:: json

   {
     "family": "capanel-import",
     "requiresCompatibilities": ["FARGATE"],
     "networkMode": "awsvpc",
     "cpu": "2048",
     "memory": "8192",
     "taskRoleArn": "arn:aws:iam::…:role/capanel-task",
     "executionRoleArn": "arn:aws:iam::…:role/capanel-execution",
     "containerDefinitions": [
       {
         "name": "import",
         "image": "…dkr.ecr.us-west-2.amazonaws.com/capanel:latest",
         "command": ["uv", "run", "app/scripts/ingest_research_files.py"],
         "environment": [
           {"name": "ENVIRONMENT", "value": "production"},
           {
             "name": "RESEARCH_FILE_SOURCE_URI",
             "value": "s3://ca-panel-resources/research-files"
           }
         ],
         "secrets": [
           {
             "name": "DATABASE_URL",
             "valueFrom": "arn:aws:secretsmanager:…:secret:capanel/database-url"
           },
           {
             "name": "SECRET_KEY",
             "valueFrom": "arn:aws:secretsmanager:…:secret:capanel/secret-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/capanel-import",
             "awslogs-region": "us-west-2",
             "awslogs-stream-prefix": "import"
           }
         }
       }
     ]
   }

Memory matters: the importer spools subscore rows to a temporary file once they
outgrow 64 MB, and holds one entity record per school in memory — a few thousand
— so 8 GB is comfortable for the largest Smarter Balanced file.

Ephemeral storage defaults to 20 GB on Fargate, which is enough for the spool
and for staging a ZIP archive.  Raise ``ephemeralStorage`` if you add many more
tests.

Running it on upload
--------------------

Point EventBridge at the bucket so an upload starts an import:

.. code-block:: json

   {
     "source": ["aws.s3"],
     "detail-type": ["Object Created"],
     "detail": {
       "bucket": {"name": ["ca-panel-resources"]},
       "object": {"key": [{"prefix": "research-files/"}]}
     }
   }

with an ECS ``RunTask`` target using the ``capanel-import`` task definition.

.. important::

   Enable EventBridge notifications on the bucket
   (``put-bucket-notification-configuration`` with
   ``EventBridgeConfiguration``), otherwise the rule never fires.

Uploading a whole administration at once fires one event per object.  Two
mitigations, either of which is enough:

* Give the rule a **5-minute dead-letter-backed batch window** by targeting a
  Step Functions state machine that waits and then runs a single task.  A single
  run loads everything that changed, so a delay costs nothing.
* Or drop the rule and run the import on a schedule instead — an EventBridge
  Scheduler rule at, say, 03:00 daily.  The importer skips unchanged files, so a
  daily run does no work on the days nothing was uploaded.

The scheduled form is the simpler of the two and is the recommended default:

.. code-block:: bash

   aws scheduler create-schedule \
     --name capanel-import-nightly \
     --schedule-expression "cron(0 3 * * ? *)" \
     --flexible-time-window '{"Mode":"OFF"}' \
     --target file://import-target.json

An import can also be started by hand from the API — see
:doc:`importing-research-files`.

The API service
---------------

Run the FastAPI application as an ECS Fargate service behind an Application Load
Balancer, with the health check pointed at ``/api/v1/utils/health-check/``.

Environment:

.. list-table::
   :header-rows: 1
   :widths: 38 62

   * - Variable
     - Value
   * - ``ENVIRONMENT``
     - ``production``
   * - ``DATABASE_URL``
     - From Secrets Manager.
   * - ``SECRET_KEY``
     - From Secrets Manager.
   * - ``FRONTEND_HOST``
     - The CloudFront domain.
   * - ``BACKEND_CORS_ORIGINS``
     - The CloudFront domain.
   * - ``RESEARCH_FILE_SOURCE_URI``
     - The bucket prefix, so the API can start an import.

.. note::

   ``ENVIRONMENT=production`` makes the application refuse to start with default
   secrets, and disables the local-only routes.

Two tasks behind the load balancer is enough to survive a deployment; the
reporting endpoints are read-only and cache-friendly, and every response carries
``Cache-Control: public, max-age=300``.

The frontend
------------

Build the frontend and publish it to a second bucket served by CloudFront:

.. code-block:: bash

   cd frontend
   pnpm install
   VITE_API_URL=https://api.example.org pnpm build
   aws s3 sync dist/ s3://ca-panel-web/ --delete
   aws cloudfront create-invalidation --distribution-id E… --paths "/*"

Route ``/api/*`` on the same distribution to the load balancer so the browser
sees one origin, or set ``BACKEND_CORS_ORIGINS`` to the CloudFront domain and
call the API directly.

Costs
-----

Rough monthly order of magnitude in ``us-west-2``, for a public dashboard with
light traffic:

.. list-table::
   :header-rows: 1
   :widths: 40 20 40

   * - Item
     - Approx.
     - Notes
   * - RDS ``db.t4g.medium``, 100 GB gp3
     - $80
     - The largest line. A single-AZ instance halves it; a reserved instance
       cuts it further.
   * - ECS Fargate, 2 API tasks
     - $35
     - 0.5 vCPU / 1 GB each.
   * - ECS Fargate, import task
     - < $1
     - Minutes per run.
   * - S3 storage
     - < $1
     - A few GB of research files.
   * - CloudFront + ALB
     - $25
     - Mostly the load balancer's hourly charge.

The importer's egress is free — S3 to ECS in the same region — which is the main
reason to keep the bucket and the compute in one region.

Operational notes
-----------------

**Watch the import.**  ``ingest_runs`` and ``ingest_files`` record every run.
Alarm on a run whose status is ``failed``, or on the absence of a successful run
in the past week.

**Reference data is cached.**  The API caches the assessment catalogue for five
minutes; after an import, the new year appears within that window without a
restart.

**Restoring.**  The database holds nothing that is not reproducible from the
bucket except user accounts.  A rebuild is: restore or recreate RDS, run
``alembic upgrade head``, run the import task.

**Scaling further.**  If the fact tables grow past a few years and queries slow,
partition ``assessment_results`` and ``assessment_subscores`` by ``test_year``
with declarative list partitioning.  The importer's delete-and-replace becomes a
partition swap, and reporting queries prune to a single year.  Nothing in the
application depends on the tables being unpartitioned.
