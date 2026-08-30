# Google Cloud Run Deployment Guide

This project is deployed to **Google Cloud Run** using scripts in `backend/app/scripts/gcp`.
The key point is:

- `deploy_cloud_run.py` is the main deployment entry point.
- `render_cloud_run_service.py` is used automatically by the deploy script.
- `provision_cloud_run.py` is for initial infrastructure provisioning.

## Prerequisites

- A **Google Cloud Platform (GCP)** project.
- The **gcloud CLI** installed and authenticated (`gcloud auth login`).
- **Docker** installed (for local builds if not using Cloud Build).
- **uv** installed.
- A configured `.env` file (see [Environment Variables](environment-variables.rst)).

## Which Script Should I Run?

### `deploy_cloud_run.py` (main deployment script)

Use `backend/app/scripts/gcp/deploy_cloud_run.py` for normal deployments. It handles:

1. Enabling required GCP APIs.
2. Creating/checking Artifact Registry.
3. Ensuring the GCS import bucket exists.
4. Building and pushing Backend and Frontend Docker images.
5. Deploying the Database Init Job (Cloud Run Job).
6. Deploying the Manual Init Trigger (Cloud Function).
7. Deploying the Combined Service (Cloud Run Service).

### `render_cloud_run_service.py` (helper used automatically)

`render_cloud_run_service.py` renders the Cloud Run service YAML (frontend + backend containers) from environment variables.
You do **not** need to run it manually during standard deployment; `deploy_cloud_run.py` calls it internally.

### `provision_cloud_run.py` (infrastructure provisioning)

`provision_cloud_run.py` is primarily for first-time setup or reprovisioning foundational GCP resources, such as:

- Artifact Registry repository.
- Service accounts and IAM bindings.
- VPC peering for private networking.
- Cloud SQL instance, database, and user.
- GCS import bucket (if needed).

If your infrastructure already exists, you can usually skip provisioning and run `deploy_cloud_run.py` directly.

## Recommended Workflow

### First-time setup

1. Run `provision_cloud_run.py` to create required infrastructure.
2. Run `deploy_cloud_run.py` to build and deploy app components.

### Existing infrastructure

1. Run `deploy_cloud_run.py` directly.
2. If deployment reports missing core resources (for example Cloud SQL, service accounts, networking), run provisioning and retry.

## `deploy_cloud_run.py` Usage

```bash
# Deploy only the combined service (Backend + Frontend)
uv run backend/app/scripts/gcp/deploy_cloud_run.py .env --full-only

# Deploy only the initialization resources
uv run backend/app/scripts/gcp/deploy_cloud_run.py .env --init-trigger-only

# Deploy everything (service + init resources)
uv run backend/app/scripts/gcp/deploy_cloud_run.py .env
```

## Deployment Modes

### Full Service Only (`--full-only`)

Builds backend/frontend images and deploys the combined Cloud Run service. Use when updating application or UI without changing init resources.

### Init Trigger Only (`--init-trigger-only`)

Deploys manual database initialization/import resources:

- **Backend Image** for the init job.
- **Cloud Run Job** that executes the import pipeline.
- **Cloud Function** HTTP endpoint that triggers the job.

### All Resources (default)

Running without mode flags deploys/updates both service and initialization resources.

## Database Initialization

After the initial deployment, apply the migrations and load the assessment data with the research file importer.
See [Importing Research Files](importing-research-files.rst).

```bash
# Get the function URL from deployment output or gcloud
FUNCTION_URL=$(gcloud functions describe capanel-full-init-trigger --region us-west1 --gen2 --format="value(serviceConfig.uri)")

# Trigger initialization
curl -X POST -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$FUNCTION_URL"
```

## Secrets Management

Sensitive values are stored in **Google Secret Manager**. `deploy_cloud_run.py` expects specific secrets and maps them into Cloud Run environment variables.

Managed secrets:

- **`capanel-secret-key`** → `SECRET_KEY`
- **`capanel-postgres-password`** → `POSTGRES_PASSWORD`

Create or update secrets with:

```bash
uv run backend/app/scripts/gcp/create_secrets.py .env
```

This script reads `SECRET_KEY` and `CLOUD_SQL_PASSWORD` from `.env`, uploads values to Secret Manager, and grants access to the Cloud Run service account.

## URLs and Access

After deployment:

- **Frontend**: `https://<your-service-url>`
- **Backend API docs**: `https://<your-service-url>/docs`
- **Manual init trigger**: URL is shown in deployment output
