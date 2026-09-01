# Google Cloud

**Google Cloud is not a supported deployment target.** The application is
deployed with Docker on an EC2 instance — see [Deploying on AWS](aws-deployment.md).

The project ran on Cloud Run for a while, against Cloud SQL for PostgreSQL, with
research files in a GCS bucket and secrets in Secret Manager. That deployment is
retired: no Cloud Run service is kept warm, no Cloud SQL instance is running, and
none of the documentation elsewhere in this guide assumes Google Cloud.

What is left of it:

- `backend/app/scripts/gcloud/` holds the Google-specific script helpers —
  service and Cloud SQL defaults, `gcloud` executable discovery, the Cloud Run
  YAML escaping. Nothing outside that package imports from it, so it can be
  deleted in one step if Cloud Run is ruled out for good.
- The generic script helpers those files used to share — path discovery, `.env`
  parsing, subprocess handling — now live in `backend/app/scripts/script_utils.py`
  and are used by the ordinary prestart and client-generation scripts.

Cloud Run may come back as a second target later: it suits this application,
which is a stateless read-mostly API in front of a Postgres database, and the
container images built for Docker would run there unchanged. The blockers are
the database and the import, not the web tier — Cloud SQL storage for a 10 GB
database plus a bucket of research files costs more than the single EC2 instance
that currently carries both, and the importer wants a long-running task rather
than a request-scoped one. Reviving it means restoring the provisioning and
deploy scripts into `backend/app/scripts/gcloud/`, not rewriting the application.
