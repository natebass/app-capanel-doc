# Security Emergency Procedures

This guide outlines the strategies and actions to take in case of a security incident or credential exposure.

## Forced Password Reset Strategy

In the event of a credential exposure or as a proactive security measure, you can force a password reset for specific
users or all active users.

### How to use strategy

1. **Run migration**: Ensure the database schema supports the password reset flag.
2. **Trigger reset**: A security admin calls `POST /api/v1/login/force-password-reset` with either:
    * `affected_emails`: A list of specific user emails.
    * `include_all_active_users: true`: To force a reset for all users.
3. **User experience**: Flagged users will see a warning in their settings and will be guided to change their password
   upon their next login or interaction.
4. **Automatic clearing**: A successful password change will clear the forced reset flag automatically.

## Security Emergency Actions

If specific credentials are known to be exposed, follow these steps immediately. The
deployment stores its secrets in AWS Systems Manager Parameter Store — see
[Environment Variables](environment-variables.rst) and [Deploying on AWS](aws-deployment.md).

### 1. Rotate exposed credentials immediately

* **Generate fresh values first**: Use `rotate_exposed_secrets.py` to generate replacements in one pass (for example
  `--target local-db --target secret-key`, or `--target all`).
* **Update local env values**: Put generated values into `.env` (`POSTGRES_PASSWORD`, `FIRST_SUPERUSER_PASSWORD`,
  `SECRET_KEY`) and rotate `VITE_STRAPI_API_KEY` as needed. Local `.env` files are for local development only.
* **Update Parameter Store**: Overwrite the deployed values so the instance picks them up on the next deploy.

  ```bash
  aws ssm put-parameter --name /capanel/secret-key --type SecureString \
    --overwrite --value "$(openssl rand -hex 32)"
  aws ssm put-parameter --name /capanel/postgres-password --type SecureString \
    --overwrite --value "$(openssl rand -hex 24)"
  ```

### 2. Apply the rotation to the running deployment

* **Re-run the deploy script**: `./deploy.sh` on the instance rewrites `.env` from Parameter Store and recreates the
  containers, so both the backend and PostgreSQL come up on the new values.
* **Change the database password itself**: rotating the parameter changes what the backend *sends*. The PostgreSQL role
  has to be changed to match, or the two drift apart:

  ```bash
  docker compose exec db psql -U capanel -c "ALTER ROLE capanel WITH PASSWORD 'new-value';"
  ```

  Do this before recreating the backend, then run `./deploy.sh`.

### 3. Recycle access paths

* **Revoke IAM credentials**: The instance authenticates with its instance profile, so there should be no long-lived
  access keys to rotate. If any exist, deactivate them with `aws iam update-access-key --status Inactive` and delete
  them after cutover rather than leaving them in place.
* **Re-key SSH**: There is no SSH access to revoke — the instance is reached through SSM Session Manager and port 22 is
  closed. If a key pair was added at some point, remove it from `~/.ssh/authorized_keys` and close the rule.
* **Force user password resets**: Use the procedure at the top of this page if application accounts are implicated.

### 4. Verify compromise closure

* **Confirm access denial**: Verify that the old database password no longer works.
* **Confirm functionality**: Confirm that app/admin login and database connectivity work correctly with the new
  credentials.
* **Audit logs**: Review CloudTrail for `ssm:GetParameter`, `s3:GetObject` and IAM activity during the exposure window,
  and `docker compose logs backend` for unexpected authenticated requests.

### 5. Prevent repeat incidents

* **Secret hygiene**: Never commit real secrets to the repository or include them in examples.
* **Environment separation**: Continue using `.env` files only for local development; deployed configuration must be
  sourced from Parameter Store. The `.env` that `deploy.sh` writes on the instance is generated, mode `600`, and never
  committed.
* **Automated scanning**: Add secret scanning to pre-commit hooks and CI pipelines (e.g., `gitleaks` or `trufflehog`)
  and block pushes if secrets are found.
