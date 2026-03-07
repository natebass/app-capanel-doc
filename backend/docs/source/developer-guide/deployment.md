# FastAPI Project - Deployment

This project is designed to be deployed to **Google Cloud Run**. The deployment process is automated using a Python script that builds container images and manages the necessary GCP resources.

## Prerequisites

*   A **Google Cloud Platform (GCP)** project.
*   The **gcloud CLI** installed and authenticated (`gcloud auth login`).
*   **Docker** installed (for local builds if not using Cloud Build).
*   **uv** installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
*   The `.env` file configured with your project details (see [Environment Variables](environment-variables.rst)).

## Deployment Script

The main deployment tool is `backend/app/scripts/gcp/deploy_cloud_run.py`. It handles:

1.  Enabling required GCP APIs.
2.  Creating an Artifact Registry repository.
3.  Ensuring the GCS bucket for data import exists.
4.  Building and pushing Backend and Frontend Docker images.
5.  Deploying the Database Init Job (Cloud Run Job).
6.  Deploying the Manual Init Trigger (Cloud Function).
7.  Deploying the Combined Service (Cloud Run Service).

### Usage

You can run the deployment script using `uv`:

```bash
# Deploy only the combined service (Backend + Frontend)
uv run backend/app/scripts/gcp/deploy_cloud_run.py .env --full-only

# Deploy only the backend initialization resources
uv run backend/app/scripts/gcp/deploy_cloud_run.py .env --init-trigger-only

# Deploy everything (Full service + Init resources)
uv run backend/app/scripts/gcp/deploy_cloud_run.py .env
```

## Deployment Modes

### Full Service Only (`--full-only`)
This mode builds the backend and frontend images and deploys them as a single Cloud Run service. It is useful for updating the application logic or user interface without affecting the database initialization pipeline.

### Init Trigger Only (`--init-trigger-only`)
This mode deploys the resources required for manual database initialization and data imports:
*   **Backend Image**: Used by the init job.
*   **Cloud Run Job**: Executes the import pipeline.
*   **Cloud Function**: Provides an HTTP endpoint to trigger the job manually.

### All Resources (Default)
Running the script without specific flags will deploy/update all components of the system.

## Database Initialization

After the initial deployment, you must initialize the database and run the data import pipeline. You can do this by invoking the Manual Init Trigger Cloud Function. Detailed examples using `curl` and `gcloud` are available in [Triggering Data Imports](triggering-data-imports.rst).

```bash
# Get the function URL from the deployment output or gcloud
FUNCTION_URL=$(gcloud functions describe capanel-full-init-trigger --region us-west1 --gen2 --format="value(serviceConfig.uri)")

# Trigger the initialization
curl -X POST -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$FUNCTION_URL"
```

## Secrets Management

Sensitive values are managed via **Google Secret Manager**. The deployment script (`deploy_cloud_run.py`) expects specific secrets to exist and maps them to environment variables in the Cloud Run service.

The following secrets are managed:

*   **`capanel-secret-key`**: Maps to `SECRET_KEY`.
*   **`capanel-postgres-password`**: Maps to `POSTGRES_PASSWORD` (used by the backend to connect to Cloud SQL).

You can create or update these secrets using the provided utility:

```bash
uv run backend/app/scripts/gcp/create_secrets.py .env
```

This script reads the values from your `.env` file (`SECRET_KEY` and `CLOUD_SQL_PASSWORD`), uploads them to Secret Manager, and grants the necessary access to the Cloud Run service account.

## URLs and Access

Once deployed, your application will be available at the URL provided by Cloud Run.

*   **Frontend**: `https://<your-service-url>`
*   **Backend API Docs**: `https://<your-service-url>/docs`
*   **Manual Init Trigger**: Provided after deployment.
