# Security Emergency Procedures

This guide outlines the strategies and actions to take in case of a security incident or credential exposure.

## Forced Password Reset Strategy

In the event of a credential exposure or as a proactive security measure, you can force a password reset for specific users or all active users.

### How to use strategy

1.  **Run migration**: Ensure the database schema supports the password reset flag.
2.  **Trigger reset**: A security admin calls `POST /api/v1/login/force-password-reset` with either:
    *   `affected_emails`: A list of specific user emails.
    *   `include_all_active_users: true`: To force a reset for all users.
3.  **User experience**: Flagged users will see a warning in their settings and will be guided to change their password upon their next login or interaction.
4.  **Automatic clearing**: A successful password change will clear the forced reset flag automatically.

## Security Emergency Actions

If specific credentials are known to be exposed, follow these steps immediately.

### 1. Rotate exposed credentials immediately

*   **Generate fresh values first**: Use `rotate_exposed_secrets.py` to generate the exposed values in one pass (for example `--target gcloud --target local-db --target secret-key`, or `--target all`).
*   **Update local env values**: Put generated values into `.env` (`CLOUD_SQL_PASSWORD`, `POSTGRES_PASSWORD`, `FIRST_SUPERUSER_PASSWORD`, `SECRET_KEY`) and rotate `VITE_STRAPI_API_KEY` as needed.
*   **Apply Cloud SQL password rotation in GCP**: Run `rotate_gcp_credentials.py --rotate-cloud-sql-password` (or `--all`) after `.env` has the new `CLOUD_SQL_PASSWORD`.

### 2. Update secret distribution

*   **Push rotated DB password**: Update Secret Manager with `rotate_gcp_credentials.py --update-secret-manager` (or `--all`) so `capanel-postgres-password` matches the newly generated value.
*   **Update app secrets**: Run `create_secrets.py` after rotating values so `capanel-secret-key` (and related app secrets) are synchronized in Secret Manager for Cloud Run.

### 3. Recycle runtime and access paths

*   **Restart Cloud Run services**: Restart services after secret updates (`--restart-service ...` or `--all`) so new values are picked up.
*   **Service Account Keys**: List service-account keys and remove old ones after cutover (`--list-sa-keys`, `--delete-sa-key ...`).
*   **New Keys**: Create a new SA key only if absolutely required (`--create-sa-key`); otherwise, prefer keyless authentication.

### 4. Verify compromise closure

*   **Confirm access denial**: Verify that the old database password no longer works.
*   **Confirm functionality**: Confirm that app/admin login and database connectivity work correctly with the new credentials.
*   **Audit logs**: Review Cloud Audit Logs for any suspicious key or secret access during the exposure window.

### 5. Prevent repeat incidents

*   **Secret hygiene**: Never commit real secrets to the repository or include them in examples.
*   **Environment separation**: Continue using `.env` files only for local development; production configuration must be sourced from Secret Manager.
*   **Automated scanning**: Add secret scanning to pre-commit hooks and CI pipelines (e.g., `gitleaks` or `trufflehog`) and block pushes if secrets are found.
