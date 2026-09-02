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
files that expand into roughly 10 GB of database. What the instance never does
is **build** anything — the front end is compiled on your machine or in CI and
only the compiled output is shipped.

```{mermaid}
flowchart LR
    DEV["your machine / CI<br/>pnpm build"] -->|rsync dist/| CADDY
    USER((Browser)) -->|443| CADDY
    subgraph EC2["EC2 t4g.small — Docker Compose"]
        CADDY["caddy<br/>TLS + static files"] -->|/api| API["backend<br/>FastAPI"]
        API --> DB[("postgres:18<br/>on EBS gp3")]
        IMPORT["one-off import<br/>docker compose run"] --> DB
    end
    S3[("S3<br/>capanel-…-an/resources")] -->|streamed COPY| IMPORT
    CDE["www3.cde.ca.gov<br/>dashboard files"] --> IMPORT
```

## The instance

**Recommended: `t4g.small` — 2 vCPU Graviton, 2 GiB RAM, in `us-west-2`**, with a
60 GiB gp3 root volume.

Two gigabytes sounds thin for a stack that loads 2.6 GB of research files into a
10 GB database. It works, because of one design decision in the importer and one
in the deployment:

- **The importer never holds a file in memory.** Rows stream from S3 through a
  generator into PostgreSQL's `COPY`. Peak resident memory is bounded by a 64 MB
  spool and a few thousand entity records, not by file size. This is measured
  below, and it is the reason the instance size is not driven by the 2.6 GB.
- **Nothing is built on the instance.** The front end is compiled elsewhere and
  only its `dist/` directory is shipped. The `npm run build` step is what would
  actually demand 2 GB, and it does not happen here.

`us-west-2` because that is where the resources bucket already is. S3-to-EC2
transfer within a region is free, so the import pulls 2.6 GB at no cost.

### Where the 2 GiB goes

| Consumer | Steady | During an import |
| --- | --- | --- |
| PostgreSQL `shared_buffers` | 512 MB | 512 MB |
| PostgreSQL `maintenance_work_mem` | — | up to 256 MB, for the index build after the swap |
| Backend (FastAPI, idle) | ~120 MB | ~120 MB |
| Importer process | — | ~150 MB: the 64 MB subscore spool before it spills to disk, the entity dictionary, psycopg buffers |
| Caddy serving static files | ~15 MB | ~15 MB |
| OS and Docker daemon | ~200 MB | ~200 MB |

That totals roughly 1.3 GB at the peak, leaving headroom for page cache. It is
not generous, and the two rules that keep it working are: **do not run an import
and a front-end build at the same time** (you will not, because there is no build
here), and **do not raise `shared_buffers`** to the quarter-of-RAM figure that is
conventional on larger machines — on 2 GiB that starves everything else.

```{note}
A 10 GB database on 2 GiB of RAM means most reads come from disk rather than
page cache. For this application that is acceptable: the reporting queries are
index lookups on a narrow key, and gp3 gives 3,000 IOPS. Expect a cold query to
take tens of milliseconds rather than single digits. For a prototype shown to a
handful of people, that is invisible.
```

### Burst credits

`t4g` instances are burstable. A `t4g.small` earns 24 CPU credits per hour,
sustaining about 20% of two vCPUs indefinitely. Serving a prototype uses
essentially none of that; an import uses all of it.

Leave **`unlimited` mode on** (the default). The import runs at full speed and
bills roughly $0.05 per vCPU-hour beyond the earned credits — a full import
might add ten cents. Do not switch to `standard` mode to avoid that: the import
would be throttled to a fifth of the CPU and take five times as long.

### Architecture

Graviton means **arm64**. `postgres`, `caddy` and the `ghcr.io/astral-sh/uv`
Python images all publish arm64 builds, and the runtime Python dependencies are
pure Python or ship arm64 wheels (`psycopg[binary]`, `pwdlib`, `openpyxl`).

Build the backend image **on the instance** — it is a small build and does not
need much memory — or with `docker buildx --platform linux/arm64` if you build
it on your machine and push it.

If arm64 becomes a fight, `t3.small` (x86, ~$0.0208/hour) is the equivalent at
about $2/month more.

### Storage

60 GiB gp3, which includes 3,000 IOPS and 125 MB/s at no extra charge:

| Item | Size |
| --- | --- |
| Database at rest | ~10 GiB |
| Import churn — staging tables and WAL, before autovacuum reclaims | ~15 GiB |
| Subscore spool in `/tmp` during the largest file | ~5 GiB |
| Docker images and layers | ~2 GiB |
| OS, logs, swap file, room to breathe | ~10 GiB |

The **subscore spool** is the item people forget. A research file row produces
one result and up to six subscores, and a connection can only run one `COPY` at
a time, so the subscores are written to a `SpooledTemporaryFile` while the
results stream. It holds 64 MB in memory and then spills to disk — which is
exactly the trade that keeps RAM flat, and exactly why the volume needs the
headroom. `/tmp` inside the container must have room, so do not mount it as a
small `tmpfs`.

gp3 volumes expand online, so 60 GiB is a floor. Do not put the database on
instance store — `t4g` has none, and where it exists it is lost on stop.

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

(email-with-ses)=
### Email with SES

The application sends two transactional emails — a password reset and a new
account welcome — plus a test email for checking the configuration. Both are
triggered by a user action and neither should make that user wait.

#### Two ways in, and they are not equivalent

**SES has an SMTP interface.** `app/core/utils.py` already sends through the
`emails` library over SMTP, so pointing it at SES is four environment variables
and no code at all:

```bash
SMTP_HOST=email-smtp.us-west-2.amazonaws.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=<SES SMTP username>
SMTP_PASSWORD=<SES SMTP password>
EMAILS_FROM_EMAIL=noreply@example.org
```

The SMTP credentials are **not** IAM access keys — they are derived from an IAM
user in the SES console, and they are long-lived secrets that have to live in
Parameter Store. That is the one real cost of this route: the instance profile
stops being enough.

**The `boto3` SES API** avoids that. `boto3` is already a dependency for the S3
importer and picks up the instance role automatically, so there is nothing to
store and nothing to rotate. It also returns a message ID you can correlate
against SES's event notifications.

The API route is the better fit here, for the credential reason more than
anything else — the deployment otherwise has no long-lived secrets outside
Parameter Store, and adding a pair for SMTP is a step backwards.

#### Sending in the background

Neither route should be called inline. SES takes tens to hundreds of
milliseconds, and a password-reset endpoint that blocks on it is a
password-reset endpoint that hangs when SES is slow. FastAPI's `BackgroundTasks`
runs the send after the response has been returned:

```python
from fastapi import BackgroundTasks

@router.post("/password-recovery/{email}")
def recover_password(
    email: str, session: SessionDep, background_tasks: BackgroundTasks
) -> Message:
    user = crud.get_user_by_email(session=session, email=email)
    # ... token generation, unchanged ...
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    background_tasks.add_task(
        send_email,
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")
```

`send_email` stays synchronous — `BackgroundTasks` runs a plain `def` in a thread
pool, which is exactly right for a blocking `boto3` call. Making it `async def`
would run it on the event loop and block every other request while SES answers.

```{important}
A background task that raises does so **after** the response has gone out. The
client is told the email was sent; nothing tells the user it was not. Log the
failure inside `send_email` and, for password resets, watch the SES bounce and
complaint rate rather than relying on the endpoint's status code.
```

`BackgroundTasks` is the right amount of machinery for this deployment: the work
is one API call, it is idempotent from the user's point of view (they can ask
for another reset link), and losing it on an instance restart costs a retry
rather than data. A queue — SQS with a worker — is what you would reach for if
the email mattered enough that dropping it were unacceptable, and it is not
worth its own moving parts here.

#### SES configuration

```bash
# Verify the sending domain and get the DKIM records to publish.
aws sesv2 create-email-identity --email-identity example.org --region us-west-2
aws sesv2 get-email-identity --email-identity example.org --region us-west-2 \
  --query 'DkimAttributes.Tokens'
```

Publish the three returned CNAME records, plus an SPF record
(`v=spf1 include:amazonses.com ~all`) and a DMARC record
(`v=DMARC1; p=none; rua=mailto:dmarc@example.org`) on `_dmarc`. Verifying the
domain rather than a single address is what lets you send as any address on it,
and DKIM is what keeps the mail out of spam folders.

**Every new account starts in the SES sandbox**, which only delivers to
addresses you have separately verified and caps you at 200 messages a day. For a
test deployment with a few users that may genuinely be enough — verify the few
recipients and skip the paperwork. To leave it, request production access in the
SES console; approval takes a day or so and asks what you send and how you
handle bounces.

Add this statement to the `capanel-instance` role policy shown earlier:

```json
{
  "Sid": "SendEmail",
  "Effect": "Allow",
  "Action": ["ses:SendEmail"],
  "Resource": "*",
  "Condition": {
    "StringEquals": {"ses:FromAddress": "noreply@example.org"}
  }
}
```

The `ses:FromAddress` condition means a compromised instance cannot send as
anyone else on the domain.

Set the region and sender on the `backend` service in `compose.yaml`:

```yaml
      AWS_REGION: us-west-2
      EMAILS_FROM_EMAIL: noreply@example.org
      EMAILS_FROM_NAME: California Accountability Panel
```

Keep the SES region the same as the instance — a cross-region call adds latency
to a background task for no benefit.

#### Cost

The first 62,000 messages a month are free when sent from an application hosted
on EC2; beyond that it is $0.10 per thousand. At this deployment's volume — a
handful of password resets — **email is free**, and it stays free by a wide
margin. It does not appear in the cost table below for that reason.

## The container files

To be created in `opensacorg/app-capanel-web`.

### Keeping the images small

Three changes account for almost all of it, and the first two are already made
in `pyproject.toml`:

| Change | Saved |
| --- | --- |
| Move the Sphinx toolchain to a `docs` dependency group | ~90 MB — `sphinx`, `pydata-sphinx-theme`, `babel`, `pygments`, `docutils` |
| Drop `pandas` and `google-auth`, which nothing under `app/` imports | ~105 MB — `pandas` pulls `numpy` and `numpy.libs` |
| Build the front end off the instance, so no Node in any image | the whole Node toolchain |

Measured on this project: a full development environment is **416 MB** of
site-packages; a runtime-only install
(`uv sync --frozen --no-default-groups --no-install-project`) is **124 MB**. On
top of a ~120 MB `python3.14-slim` base and the application source, the backend
image lands around **300 MB**, and the `caddy:2-alpine` image serving the front
end is about **50 MB**.

```{note}
`pandas`, `openpyxl` and spreadsheets: the importer reads `.xlsx` through
`openpyxl` in `read_only=True` streaming mode, not through `pandas`. `pandas`
was a leftover declaration. Keeping it out matters twice over — 105 MB of image,
and it removes the temptation to write a `read_excel()` that would load a whole
workbook into a 2 GiB instance.
```

### `backend/Dockerfile`

```dockerfile
# Build stage: uv resolves and installs into /app/.venv.
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS build

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies first, so a code change does not reinstall the world.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-default-groups --no-install-project

# Runtime stage: the virtualenv and the source, no uv, no caches.
FROM python:3.14-slim-trixie

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY --from=build /app/.venv /app/.venv
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

RUN useradd --system --create-home app && chown -R app /app
USER app

EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
```

`--no-default-groups` is what excludes both `dev` and `docs`; plain `--no-dev`
would still install Sphinx. The build stage carries `uv` and its cache and is
thrown away; only the resolved virtualenv crosses into the runtime image.

The runtime stage is deliberately **not** distroless. `alembic` and the ingest
scripts are run as one-off `docker compose run` commands against this same
image, so a shell and the console scripts have to be present. That is worth
perhaps 30 MB and it is the difference between running a migration and not.

### Building the front end off the instance

The front end is static. Compiling it needs about 2 GB of RAM and a full Node
toolchain; serving it needs neither. So it is built on your machine (or in
GitHub Actions, which gives you a 16 GB runner for free) and only the compiled
`dist/` is shipped.

There is **no `frontend/Dockerfile`**. The `web` service runs stock
`caddy:2-alpine` with `dist/` bind-mounted in.

From your machine:

```bash
cd frontend
pnpm install
pnpm build
rsync -az --delete dist/ ec2-user@capanel.example.org:/opt/capanel/dist/
```

`--delete` matters: without it, files removed from a build linger and an old
hashed bundle can be served alongside a new `index.html`.

If SSH is closed (the security group section recommends closing it), tunnel
through SSM instead — no inbound rule, no key pair:

```bash
aws ssm start-session --target i-… \
  --document-name AWS-StartPortForwardingSession \
  --parameters '{"portNumber":["22"],"localPortNumber":["2222"]}'
rsync -az --delete -e "ssh -p 2222" dist/ ec2-user@localhost:/opt/capanel/dist/
```

```{important}
`VITE_API_URL` and `VITE_BASE_PATH` are baked in at build time. Build with
`VITE_API_URL` empty — Caddy serves the front end and the API on one origin, so
the client uses relative URLs and CORS never applies. A build made for a
different origin will fail in the browser with no error on the server.
```

The same `dist/` can be produced by a GitHub Actions job and downloaded as an
artifact, which is worth setting up once the novelty of running `pnpm build` by
hand wears off. Either way the instance is uninvolved.

### `Caddyfile`

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

`/srv` is the `dist/` directory rsynced up from your machine, bind-mounted read
only. Caddy picks up new files immediately, so a front-end deploy is the `rsync`
alone — no rebuild, no restart, no downtime.

### `compose.yaml`

```yaml
name: capanel

services:
  db:
    image: postgres:18-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?Variable not set}
      - POSTGRES_DB=app
    volumes:
      - pgdata:/var/lib/postgresql/data
    # Tuned for 2 GiB total, not for a dedicated database host.
    command:
      - postgres
      - -c
      - shared_buffers=512MB
      - -c
      - effective_cache_size=1GB
      - -c
      - work_mem=16MB
      - -c
      - maintenance_work_mem=256MB
      - -c
      - max_wal_size=4GB
      - -c
      - checkpoint_timeout=15min
      - -c
      - max_connections=40
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
      # FASTAPI_ENV is deliberately unset. Its only accepted value is
      # "development"; leaving it unset is what makes the application refuse to
      # start on a "changethis" secret and keeps the dev-only routes off.
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
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

  # Stock Caddy. The front end is built elsewhere and rsynced into ./dist.
  web:
    image: caddy:2-alpine
    restart: unless-stopped
    environment:
      SITE_ADDRESS: ${SITE_ADDRESS:?set SITE_ADDRESS}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./dist:/srv:ro
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - backend

volumes:
  pgdata:
  caddy_data:
  caddy_config:
```

The PostgreSQL settings are the ones that matter on a small instance:

- **`shared_buffers=512MB`**, a quarter of RAM. The usual advice on a dedicated
  database host is a quarter of RAM too, but here the same 2 GiB also holds the
  backend, Caddy, the OS and an importer. 512 MB is the ceiling before the OOM
  killer starts making decisions for you.
- **`maintenance_work_mem=256MB`** is what the index build after an import's
  atomic swap uses. Lower makes the swap slow; higher risks the import peak.
- **`max_wal_size=4GB`** so a bulk `COPY` does not force a checkpoint every few
  seconds. This costs disk, not memory, which is the right trade here.
- **`max_connections=40`**, down from the default 100. Each backend connection
  reserves memory; the application needs a handful.

`caddy_data` must stay a named volume — it holds the issued certificates, and
losing it on every deploy will get the domain rate-limited by Let's Encrypt.

### `backend/.dockerignore`

```text
.venv/
__pycache__/
*.py[cod]
.env
.git/
docs/
tests/
.pytest_cache/
htmlcov/
```

Without this the build context includes the local virtualenv, and `docs/` alone
is tens of megabytes of built HTML that would be copied into the build context
on every image build. `tests/` is excluded because the runtime image has no test
dependencies to run them with.

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
  --instance-type t4g.small \
  --iam-instance-profile Name=capanel-instance \
  --security-group-ids sg-… \
  --subnet-id subnet-… \
  --associate-public-ip-address \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":60,"VolumeType":"gp3","Encrypted":true,"DeleteOnTermination":false}}]' \
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

On a 2 GiB instance swap is not optional. Nothing here should page under normal
operation, but a 2 GB swap file turns a momentary spike — an import overlapping
an autovacuum, say — into a slow minute instead of an OOM kill that leaves a
half-loaded year in the database.

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Prefer reclaiming page cache over swapping out live processes.
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swappiness.conf
sudo sysctl -p /etc/sysctl.d/99-swappiness.conf
```

### 4. Clone and deploy

```bash
sudo mkdir -p /opt/capanel && sudo chown "$USER" /opt/capanel
git clone https://github.com/opensacorg/app-capanel-web.git /opt/capanel
cd /opt/capanel
./deploy.sh
```

Only the backend image is built here, and it is mostly dependency installation —
a few minutes on a `t4g.small`. Nothing compiles JavaScript.

### 4b. Ship the front end

From your machine, not the instance:

```bash
cd frontend && pnpm install && pnpm build
rsync -az --delete dist/ ec2-user@capanel.example.org:/opt/capanel/dist/
```

Caddy serves the directory directly, so this is the whole front-end deploy. Do
it before the first `docker compose up -d` or the site will 404 until it lands.

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
database around 10 GB. Watch it with `docker stats` in another session.

See {doc}`importing-research-files` for the importer's options, and
{doc}`../data/dashboard` for what the accountability layer contains.

#### Why 2.6 GB of input fits in 2 GiB of RAM

The usual failure mode for an import this size — read the file into a
DataFrame, insert row by row through the ORM, watch the kernel kill it — is
already designed out. `app/ingest/` does the three things that matter:

**Nothing is materialised.** `S3Source.open_text` hands `boto3`'s streaming
response body to a decoder that yields lines; `iter_rows` yields lists;
`_parsed_rows` is a generator; the loader consumes it one row at a time. There
is no point at which more than one row of the file exists as a Python object.
The one exception is deliberate — a dictionary of entity records keyed by CDS
code, a few thousand entries, so schools can be upserted once at the end.

**Rows go in through `COPY`, not `INSERT`.** `psycopg`'s `cursor.copy()` streams
into an unlogged staging table, which is then swapped into place in one
transaction. Millions of individual `INSERT` statements would take hours and
generate WAL to match; `COPY` into an unlogged table generates almost none.

**The one thing that must be buffered is spooled to disk.** A research file row
produces one result row and up to six subscore rows, and a connection can only
run one `COPY` at a time. So subscores are written to a `SpooledTemporaryFile`
while the results stream — 64 MB in RAM, then transparently to disk — and copied
in afterwards. This is the trade that keeps memory flat regardless of file size,
and it is why the volume needs the spool headroom noted under Storage.

Spreadsheets take the same care: `openpyxl` is opened with `read_only=True` and
read through `iter_rows`, which streams the sheet rather than building it.

```{important}
Run imports as `docker compose run --rm`, **not** through the API's
`POST /api/v1/ingest/runs` endpoint. That endpoint exists and correctly returns
`202 Accepted` with a FastAPI background task, but on this instance it is the
wrong tool: the work would run inside the web container, competing with request
handling for two burstable vCPUs, and a restart or deploy mid-import would kill
it silently. A one-off container gets its own process, its own exit code, and
its own logs. `BackgroundTasks` is right for sending an email; an hour-long
ingest wants a job, not a request.
```

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
| `t4g.small`, 730 hours | $12.26 |
| 60 GiB gp3 root volume | $4.80 |
| Public IPv4 address | $3.65 |
| EBS snapshots, ~15 GiB after compression | $0.75 |
| S3 storage, 3 GB | $0.07 |
| SES, a few messages | $0.00 |
| Data transfer out (first 100 GB/month free) | $0.00 |
| **Total** | **~$22** |

Adjustments worth knowing:

- **Stop the instance between demos.** Compute stops billing; the volume and the
  Elastic IP do not. A stopped deployment is about **$9/month** and starts back
  up in under a minute with the database intact. For something you show people
  occasionally, this is the largest saving available and it costs nothing in
  convenience.
- **`t4g.micro`** (1 GiB) is another $6/month cheaper and is where this stops
  working. PostgreSQL with a 512 MB `shared_buffers` plus the backend does not
  fit, and the import will be killed. Do not.
- **One-year no-upfront Savings Plan**: roughly −35% on the compute line, worth
  it only if the instance genuinely stays up.
- **Route 53 hosted zone**: +$0.50/month, avoidable by using an existing
  registrar's DNS.

For comparison, the same application on ECS Fargate behind an ALB with RDS is
$140–160/month. Almost all of that difference is fixed cost that does not shrink
with traffic, which is the wrong shape for a prototype.

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

**Two deploys, and they are independent.** A front-end change is `pnpm build`
plus `rsync` and takes effect immediately, with no restart and no downtime. A
backend change is `./deploy.sh` on the instance, which rebuilds the image and
recreates the containers — a few seconds of downtime, acceptable here. A
zero-downtime rollout needs a second instance and a load balancer, which is
exactly the cost this deployment exists to avoid.

**Keep an eye on memory** after any dependency change: `docker stats` and
`free -m`. On 2 GiB there is roughly 700 MB of headroom, which is comfortable
until something starts holding a file in memory. If `free -m` shows swap in
steady use rather than only during an import, something regressed.

**When it outgrows one instance**, the order to change things is: move Postgres
to RDS first — it is the piece where a single instance failure actually loses
something — then put the API behind an ALB with a second instance, then consider
ECS. The container images do not change in any of those steps.
