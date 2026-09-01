---
description: Deploying the California Accountability Panel with Docker on a single AWS EC2 instance.
---

# Deploying on AWS

The deployment is one EC2 instance running the whole application under Docker
Compose: PostgreSQL, the FastAPI backend, and a Caddy container that serves the
built front end and reverse-proxies `/api` to the backend. Research files live
in S3 and are read from there by the importer.

```{warning}
The Dockerfiles and the Compose file described here **do not live in this
repository**. This repository is a documentation mirror; the container files
belong in `opensacorg/app-capanel-web`. Everything below is the specification
for what to create there, written out in full so it can be copied.
```

## Why one instance

This is a test deployment for a handful of users, on an account with no free
tier, so every service that bills by the hour has to earn its place:

- **No RDS.** A `db.t4g.medium` with 100 GB of storage is roughly $80/month on
  its own — more than the entire single-instance deployment. PostgreSQL in a
  container on an EBS volume costs the volume and nothing else. The database
  holds nothing that cannot be rebuilt from S3 and the state's web server
  except user accounts, so losing it is an inconvenience, not a disaster.
- **No load balancer.** An Application Load Balancer is about $20/month before
  it carries a byte. Caddy on the instance terminates TLS with an automatically
  renewed Let's Encrypt certificate.
- **No ECS or Fargate.** A single-node cluster adds a control plane and task
  definitions to reason about without adding anything a Compose file does not
  already do. Moving to ECS later is a repackaging job, not a rewrite: the same
  images run there unchanged.
- **No NAT gateway.** The instance sits in a public subnet with a security
  group, at $0/month, instead of a private subnet behind a $33/month NAT.

The shape to keep in mind is that this application is read-mostly and small in
request terms, but its *import* is large: 2.6 GB of caret-delimited statewide
files that expand into roughly 10 GB of database. Sizing is driven by the
import, not by traffic.

```{mermaid}
flowchart LR
    USER((Browser)) -->|443| CADDY
    subgraph EC2["EC2 t4g.large — Docker Compose"]
        CADDY["caddy<br/>TLS + static front end"] -->|/api| API["backend<br/>FastAPI"]
        API --> DB[("postgres:18<br/>on EBS gp3")]
        IMPORT["one-off import<br/>docker compose run"] --> DB
    end
    S3[("S3<br/>capanel-…-an/resources")] -->|gateway endpoint| IMPORT
    CDE["www3.cde.ca.gov<br/>dashboard files"] --> IMPORT
```

## The instance

**Recommended: `t4g.large` — 2 vCPU Graviton, 8 GiB RAM, in `us-west-2`**, with
a 100 GiB gp3 root volume.

`us-west-2` because that is where the resources bucket already is. S3-to-EC2
transfer within a region is free, so keeping the compute in the bucket's region
turns a 2.6 GB pull into a no-cost operation; pulling it across regions would
cost about $0.05 per import and be markedly slower.

### Why 8 GiB

| Consumer | Working set |
| --- | --- |
| PostgreSQL | `shared_buffers` at 2 GB, plus `maintenance_work_mem` for the index builds an import triggers |
| Research file import | Streams rows, but spools subscores to a temporary file only after 64 MB, and holds one entity record per school — a few thousand — in memory |
| Dashboard and local-indicator imports | `pandas` + `openpyxl` read whole `.xlsx` workbooks into memory; the largest is a few hundred MB expanded |
| Caddy and the backend | A few hundred MB between them |

A 4 GiB `t4g.medium` does run this, and is the right choice if you want to
halve the compute bill and are willing to import one file at a time and never
build the front end on the box. Below 4 GiB the import gets killed by the OOM
killer partway through and leaves a half-loaded year behind.

### Burst credits are the real constraint

`t4g` instances are burstable. A `t4g.large` earns 36 CPU credits per hour,
which sustains about 30% of two vCPUs indefinitely. An import runs both cores
flat out for tens of minutes and will drain the credit balance.

Two ways to handle that, and the first is fine:

1. **Leave `unlimited` mode on** (it is the default). The instance keeps running
   at full speed and bills a surcharge of about $0.04 per vCPU-hour beyond the
   earned credits. A one-hour full import that exhausts its balance costs
   perhaps $0.08 extra. This is the recommended option: it is simpler and the
   surcharge is noise.
2. **Resize for the import.** Stop the instance, change the type to `m7g.large`
   (non-burstable, same 2 vCPU / 8 GiB, ~$0.082/hour), import, and change back.
   Worth it only if you import daily.

If imports become routine, skip the dance and run `m7g.large` permanently — it
is about $11/month more than `t4g.large` and removes a whole category of
"why is this suddenly slow".

### Architecture

Graviton means **arm64**. Every image in the stack has an official arm64 build
(`postgres`, `caddy`, `node`, and the `ghcr.io/astral-sh/uv` Python images), and
the Python dependencies here are either pure Python or ship arm64 wheels
(`psycopg[binary]`, `pandas`, `pwdlib`). Build the images **on the instance**,
or with `docker buildx --platform linux/arm64` if you build elsewhere — an
x86 image will not run.

If any of that turns into a fight, `t3.large` (x86, ~$0.083/hour) is the
equivalent and costs about $11/month more.

### Storage

100 GiB gp3, which includes 3,000 IOPS and 125 MB/s at no extra charge:

| Item | Size |
| --- | --- |
| Database at rest | ~10 GiB |
| Import churn — the staged copy plus WAL, before autovacuum reclaims | ~15 GiB |
| Cached research files, if pulled to disk | ~3 GiB |
| Docker images and build cache | ~8 GiB |
| OS, logs, room to breathe | ~10 GiB |

That leaves roughly half the volume free, which is deliberate: a Postgres volume
that fills up stops accepting writes, and growing a volume mid-import is not a
pleasant thing to do. gp3 volumes can be expanded online later, so starting at
100 GiB is a floor, not a commitment.

Do not put the database on instance store. `t4g` and `m7g` do not have any, and
where it exists it is lost on stop.

## AWS configuration

### S3 — the resources bucket

The bucket already exists:

```text
s3://capanel-007361225089-us-west-2-an/
  resources/
    california-state/       # ~2.6 GB — CAASPP and ELPAC statewide research files
      sb_ca2024_all_csv_ela_v1.txt
      sb_ca2024_all_csv_math_v1.txt
      sb_ca2025_all_csv_ela_v1.txt
      sb_ca2025_all_csv_math_v1.txt
      cast_ca2024_all_csv_v1.txt
      caa_ca2024_all_csv_v1.txt
      caas_ca2024_all_csv_v1.txt
      csa_ca2024_all_csv_v1.txt
      …
    cde-2024/               # ~104 MB — California School Dashboard workbooks
    cde-2025/               # ~123 MB
```

Three gigabytes in S3 Standard is about **$0.07/month**. There is no reason to
add lifecycle rules, Intelligent-Tiering, or Glacier transitions at this size —
the per-object monitoring charge for Intelligent-Tiering would cost more than
the storage. Revisit if the bucket passes a few hundred GB.

Do confirm the basics, since the account is carrying real uploaded data:

```bash
aws s3api put-public-access-block \
  --bucket capanel-007361225089-us-west-2-an \
  --public-access-block-configuration \
  "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

aws s3api put-bucket-versioning \
  --bucket capanel-007361225089-us-west-2-an \
  --versioning-configuration Status=Enabled
```

Versioning matters more than it looks: the state republishes corrected files
under the same name, and the importer keys on size and entity tag, so a
corrected file reloads itself automatically while the superseded version stays
recoverable. Default SSE-S3 encryption is on for all new buckets and needs no
action.

Uploading a new administration year is one command:

```bash
aws s3 sync "./resources/california-state" s3://capanel-007361225089-us-west-2-an/resources/california-state/
```

### VPC and the S3 gateway endpoint

Default VPC, public subnet, auto-assigned public IPv4. Add a **gateway VPC
endpoint for S3** — it is free, and it keeps the import's traffic off the
public path entirely:

```bash
aws ec2 create-vpc-endpoint \
  --vpc-id vpc-… \
  --service-name com.amazonaws.us-west-2.s3 \
  --route-table-ids rtb-…
```

### Security group

```bash
aws ec2 create-security-group \
  --group-name capanel-web \
  --description "CA Panel single-instance deployment" \
  --vpc-id vpc-…

# HTTP and HTTPS from anywhere: Caddy needs :80 reachable for the ACME challenge.
aws ec2 authorize-security-group-ingress --group-id sg-… \
  --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id sg-… \
  --protocol tcp --port 443 --cidr 0.0.0.0/0
```

**Do not open port 22.** Use **SSM Session Manager** instead: attach the
`AmazonSSMManagedInstanceCore` policy to the instance role and connect with
`aws ssm start-session --target i-…`. It needs no inbound rule, no key pair, and
no bastion, and it logs every session. Postgres port 5432 is never exposed —
the database listens only on the Compose network.

### IAM — the instance role

Create a role `capanel-instance` with `AmazonSSMManagedInstanceCore` attached,
plus this inline policy, and give the instance its instance profile. `boto3`
uses the default credential chain, so the role is picked up with no keys
anywhere on disk.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadResources",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::capanel-007361225089-us-west-2-an/resources/*"
    },
    {
      "Sid": "ListResources",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::capanel-007361225089-us-west-2-an",
      "Condition": {"StringLike": {"s3:prefix": ["resources/*", "resources"]}}
    },
    {
      "Sid": "WriteBackups",
      "Effect": "Allow",
      "Action": ["s3:PutObject"],
      "Resource": "arn:aws:s3:::capanel-007361225089-us-west-2-an/backups/*"
    },
    {
      "Sid": "ReadParameters",
      "Effect": "Allow",
      "Action": ["ssm:GetParameter", "ssm:GetParametersByPath"],
      "Resource": "arn:aws:ssm:us-west-2:007361225089:parameter/capanel/*"
    },
    {
      "Sid": "DecryptParameters",
      "Effect": "Allow",
      "Action": ["kms:Decrypt"],
      "Resource": "*",
      "Condition": {
        "StringEquals": {"kms:ViaService": "ssm.us-west-2.amazonaws.com"}
      }
    }
  ]
}
```

### Secrets — Parameter Store, not Secrets Manager

Secrets Manager charges $0.40 per secret per month. SSM Parameter Store standard
parameters, including `SecureString`, are free. For four secrets that is $19/year
of difference for no benefit at this scale.

```bash
aws ssm put-parameter --name /capanel/secret-key \
  --type SecureString --value "$(openssl rand -hex 32)"
aws ssm put-parameter --name /capanel/postgres-password \
  --type SecureString --value "$(openssl rand -hex 24)"
aws ssm put-parameter --name /capanel/first-superuser-password \
  --type SecureString --value "…"
```

The instance materialises them into the `.env` that Compose reads — see
{ref}`the deploy script <capanel-deploy-script>` below.

### Elastic IP and DNS

Allocate an Elastic IP and associate it, so a stop/start does not change the
address. Every public IPv4 address now bills at $0.005/hour whether or not it is
elastic, so this costs the same as the auto-assigned one it replaces.

Point an `A` record at it. A Route 53 hosted zone is $0.50/month; an existing
registrar's DNS is free and works just as well for a test deployment.

### CloudWatch

Skip the CloudWatch agent. Container logs are in `docker compose logs`, and
custom metrics and log ingestion both bill by volume. Two things are worth
having:

- A **billing alarm** — the one alarm that matters on an account with no free
  tier. Ten free alarms are included.
- An `awslogs` driver on the `backend` service only, if you want request logs to
  outlive the instance. At this traffic level that is well under $1/month.

## The container files

To be created in `opensacorg/app-capanel-web`.

### `backend/Dockerfile`

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Dependencies first, so a code change does not re-resolve the lock file.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY alembic.ini ./
COPY app ./app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
```

Two notes. The image is deliberately **not** distroless or multi-stage: the
importer is run as a one-off `docker compose run` in this same image, and having
`uv`, a shell, and `alembic` present is what makes that possible. And `--no-dev`
drops `pytest`, `ruff`, and `ty`, but keeps Sphinx, which is a runtime
dependency in `pyproject.toml` — worth revisiting if image size matters.

### `frontend/Dockerfile`

The front end is a static build. It is compiled in a Node stage and the output
is copied into the Caddy image that also serves it, so there is no Node in the
running container.

```dockerfile
FROM node:24-trixie-slim AS build
ENV PNPM_HOME=/pnpm PATH="/pnpm:$PATH"
RUN corepack enable
WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,target=/pnpm/store \
    pnpm install --frozen-lockfile

COPY . .
# Same origin in this deployment: Caddy proxies /api to the backend, so the
# generated client can use relative URLs and no CORS is involved.
ARG VITE_API_URL=""
ARG VITE_BASE_PATH="/"
RUN pnpm build

FROM caddy:2-alpine
COPY --from=build /app/dist /srv
COPY Caddyfile /etc/caddy/Caddyfile
```

```{important}
Building the front end needs about 2 GB of RAM. On a `t4g.medium` that is the
step most likely to be killed. Either build on a `t4g.large` and keep the image,
or build in CI and push to ECR.
```

### `frontend/Caddyfile`

```text
{$SITE_ADDRESS} {
	encode zstd gzip

	handle /api/* {
		reverse_proxy backend:8000
	}
	handle /docs* {
		reverse_proxy backend:8000
	}
	handle /redoc* {
		reverse_proxy backend:8000
	}

	handle {
		root * /srv
		try_files {path} /index.html
		file_server
	}
}
```

`try_files {path} /index.html` is what makes a hard reload of a deep client-side
route work. `SITE_ADDRESS` is the public hostname; Caddy obtains and renews the
certificate for it automatically, which is why port 80 has to stay open.

### `compose.yaml`

```yaml
name: capanel

services:
  db:
    image: postgres:18-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-capanel}
      POSTGRES_USER: ${POSTGRES_USER:-capanel}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    command:
      - postgres
      - -c
      - shared_buffers=2GB
      - -c
      - work_mem=64MB
      - -c
      - maintenance_work_mem=1GB
      - -c
      - max_wal_size=4GB
      - -c
      - checkpoint_timeout=15min
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-capanel}"]
      interval: 10s
      timeout: 5s
      retries: 10

  backend:
    build:
      context: ./backend
    restart: unless-stopped
    env_file: .env
    environment:
      ENVIRONMENT: production
      DATABASE_URL: postgresql://${POSTGRES_USER:-capanel}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB:-capanel}
      RESEARCH_FILE_SOURCE_URI: s3://capanel-007361225089-us-west-2-an/resources/california-state
      AWS_REGION: us-west-2
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import urllib.request as r; r.urlopen('http://localhost:8000/api/v1/utils/health-check/')\""]
      interval: 30s
      timeout: 5s
      retries: 5
      start_period: 30s

  web:
    build:
      context: ./frontend
      args:
        VITE_API_URL: ""
        VITE_BASE_PATH: "/"
    restart: unless-stopped
    environment:
      SITE_ADDRESS: ${SITE_ADDRESS:?set SITE_ADDRESS}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - backend

volumes:
  pgdata:
  caddy_data:
  caddy_config:
```

The Postgres tuning is for 8 GiB: `shared_buffers` at a quarter of RAM,
`maintenance_work_mem` at 1 GB so index builds after an import are not paged,
and `max_wal_size` raised to 4 GB so a bulk load does not force a checkpoint
every few seconds. On a 4 GiB instance halve `shared_buffers` and
`maintenance_work_mem`.

`caddy_data` must be a named volume. It holds the issued certificates, and
losing it on every deploy will get the domain rate-limited by Let's Encrypt.

### `backend/.dockerignore` and `frontend/.dockerignore`

```text
.venv/
node_modules/
dist/
__pycache__/
*.py[cod]
.env
.git/
docs/build/
.pytest_cache/
htmlcov/
playwright-report/
```

Without these, the build context includes the local virtualenv and
`node_modules` and the image build slows to a crawl.

(capanel-deploy-script)=
### `deploy.sh`

The one script that runs on the instance. It pulls secrets from Parameter Store
into `.env`, then rebuilds and restarts.

```bash
#!/usr/bin/env bash
set -euo pipefail

REGION=us-west-2
cd /opt/capanel

param() {
	aws ssm get-parameter --region "$REGION" --name "$1" --with-decryption \
		--query Parameter.Value --output text
}

cat > .env <<ENV
SITE_ADDRESS=capanel.example.org
POSTGRES_DB=capanel
POSTGRES_USER=capanel
POSTGRES_PASSWORD=$(param /capanel/postgres-password)
SECRET_KEY=$(param /capanel/secret-key)
FIRST_SUPERUSER=admin@example.org
FIRST_SUPERUSER_PASSWORD=$(param /capanel/first-superuser-password)
PROJECT_NAME=California Accountability Panel
FRONTEND_HOST=https://capanel.example.org
BACKEND_CORS_ORIGINS=https://capanel.example.org
ENV
chmod 600 .env

git pull --ff-only
docker compose build
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python app/scripts/initial_data.py
docker compose up -d
docker image prune -f
```

Migrations run as a one-off task rather than in the container's entrypoint. With
one instance the difference is small, but it keeps a failed migration from
crash-looping the service and makes the failure visible in the deploy output.

## Bringing up the instance

### 1. Launch

```bash
aws ec2 run-instances \
  --region us-west-2 \
  --image-id resolve:ssm:/aws/service/canonical/ubuntu/server/24.04/stable/current/arm64/hvm/ebs-gp3/ami-id \
  --instance-type t4g.large \
  --iam-instance-profile Name=capanel-instance \
  --security-group-ids sg-… \
  --subnet-id subnet-… \
  --associate-public-ip-address \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100,"VolumeType":"gp3","Encrypted":true,"DeleteOnTermination":false}}]' \
  --credit-specification CpuCredits=unlimited \
  --metadata-options "HttpTokens=required" \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=capanel}]'
```

`DeleteOnTermination=false` means an accidental terminate leaves the database
volume behind to be reattached. `HttpTokens=required` forces IMDSv2, which
closes the SSRF-to-credentials path that IMDSv1 leaves open.

### 2. Connect and install Docker

```bash
aws ssm start-session --target i-…
```

```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
echo "deb [arch=arm64 signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo usermod -aG docker "$USER"
```

Log out and back in for the group to take effect.

### 3. Add swap

2 GB of swap on a 100 GiB volume costs nothing and is the difference between a
front-end build that finishes and one the OOM killer takes out.

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 4. Clone and deploy

```bash
sudo mkdir -p /opt/capanel && sudo chown "$USER" /opt/capanel
git clone https://github.com/opensacorg/app-capanel-web.git /opt/capanel
cd /opt/capanel
./deploy.sh
```

The first build takes 10–15 minutes on a `t4g.large`, most of it the front end.

### 5. Load the data

The schema is empty at this point. Load it in the order the layers depend on —
assessment first, then accountability. The importers are safe to re-run: a file
whose size and entity tag are unchanged is skipped.

```bash
cd /opt/capanel

# Assessment: CAASPP and ELPAC statewide research files, from S3.
docker compose run --rm backend python app/scripts/ingest_research_files.py \
  --source s3://capanel-007361225089-us-west-2-an/resources/california-state

# Accountability: California School Dashboard indicators.
docker compose run --rm backend python app/scripts/ingest_dashboard_files.py --year 2024
docker compose run --rm backend python app/scripts/ingest_dashboard_files.py --year 2025

# LCFF local indicators, growth model, census-day enrollment.
docker compose run --rm backend python app/scripts/ingest_local_indicators.py --year 2025
docker compose run --rm backend python app/scripts/ingest_growth.py
docker compose run --rm backend python app/scripts/ingest_enrollment.py
```

The dashboard, growth, and enrollment importers default to reading from
`www3.cde.ca.gov` directly, so no local copy is needed. Pass
`--source s3://capanel-007361225089-us-west-2-an/resources/cde-2025` to use the
uploaded workbooks instead — worth doing if the state's server is slow or if you
want the import pinned to the files you have already checked.

Expect the research file import to take on the order of an hour and to leave the
database around 10 GB. Watch it with `docker stats` in another session; if
Postgres is the bottleneck rather than the CPU, raise `maintenance_work_mem`.

See {doc}`importing-research-files` for the importer's options, and
{doc}`../data/dashboard` for what the accountability layer contains.

### 6. Verify

```bash
curl -fsS https://capanel.example.org/api/v1/utils/health-check/
docker compose ps
docker compose logs -n 50 backend
```

## Backups

Two layers, both cheap.

**EBS snapshots** through Data Lifecycle Manager — a daily snapshot with 7 days
of retention, which is a whole-instance restore in one step. Snapshots are
incremental and compressed; expect $1–2/month.

**Logical dumps to S3**, because a snapshot cannot be restored into anything but
another EBS volume, and a `pg_dump` can:

```bash
docker compose exec -T db pg_dump -U capanel -Fc capanel \
  | aws s3 cp - "s3://capanel-007361225089-us-west-2-an/backups/capanel-$(date -u +%Y%m%dT%H%M%SZ).dump"
```

Compressed, that is around 2 GB. A weekly cron job with a 30-day lifecycle
expiry on the `backups/` prefix keeps it under a dollar a month.

The thing actually worth backing up is the **user accounts table** — everything
else in the database is reproducible from the bucket and the state's web server.
A rebuild is: fresh instance, `alembic upgrade head`, run the importers.

## Costs

`us-west-2` on-demand, no free tier, running continuously:

| Item | Monthly |
| --- | --- |
| `t4g.large`, 730 hours | $49.06 |
| 100 GiB gp3 root volume | $8.00 |
| Public IPv4 address | $3.65 |
| EBS snapshots, ~20 GiB after compression | $1.00 |
| S3 storage, 3 GB | $0.07 |
| Data transfer out (first 100 GB/month free) | $0.00 |
| **Total** | **~$62** |

Adjustments worth knowing:

- **`t4g.medium` instead**: −$24.50/month, at the cost of 4 GiB of headroom.
- **Stop the instance when not testing**: the compute charge stops, EBS and the
  Elastic IP do not. A stopped deployment costs about **$13/month**, and starts
  back up in under a minute with the database intact. For a test deployment used
  a few days a month this is the single biggest saving available.
- **One-year no-upfront Reserved Instance or Savings Plan**: roughly −35% on the
  compute line, if the instance is genuinely staying up.
- **Route 53 hosted zone**: +$0.50/month, avoidable by using an existing
  registrar's DNS.

For comparison, the same application on ECS Fargate behind an ALB with RDS is
$140–160/month — more than twice the price for a deployment serving a handful of
users, and most of that difference is fixed cost that does not shrink with
traffic.

## Operational notes

**Watch the imports.** `ingest_runs` and `ingest_files` record every run and its
status. After an import, check for rows with status `failed` before trusting the
data.

**Reference data is cached** for five minutes in the API, so a new year appears
shortly after an import without a restart.

**Do not put the state's published figures through the projection.**
`app/service/dashboard_projection.py` exists only for years CDE has not
released; a deployment that disagrees with caschooldashboard.org is a bug. See
{doc}`../data/dashboard`.

**Updating the application** is `./deploy.sh`. There is a few seconds of
downtime while the containers restart, which is acceptable here; a zero-downtime
rollout needs a second instance and a load balancer, and that is exactly the
cost this deployment is avoiding.

**When it outgrows one instance**, the order to change things is: move Postgres
to RDS first — it is the piece where a single instance failure actually loses
something — then put the API behind an ALB with a second instance, then consider
ECS. The container images do not change in any of those steps.
