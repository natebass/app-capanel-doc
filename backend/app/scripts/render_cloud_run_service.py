from __future__ import annotations

import os
from dataclasses import dataclass

from app.scripts.script_utils import ScriptError, env_required, yaml_escape


@dataclass(frozen=True)
class RenderEnv:
    full_service: str
    gcp_region: str
    run_service_account_email: str
    frontend_image: str
    backend_image: str
    cloud_sql_connection_name: str
    environment: str
    project_name: str
    api_v1_str: str
    backend_cors_origins: str
    frontend_host: str
    cloud_sql_db: str
    cloud_sql_user: str
    run_data_imports: str
    run_startup_data_imports: str
    import_gcs_uri: str
    import_resources_local_path: str
    vpc_network: str | None
    vpc_subnet: str | None


TEMPLATE = """apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: ${full_service}
  labels:
    cloud.googleapis.com/location: ${gcp_region}
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/cloudsql-instances: ${cloud_sql_connection_name}
${network_annotations}    spec:
      serviceAccountName: ${run_service_account_email}
      containers:
      - name: frontend
        image: ${frontend_image}
        ports:
        - containerPort: 8080
        startupProbe:
          httpGet:
            path: /
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 12
        livenessProbe:
          httpGet:
            path: /
            port: 8080
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        resources:
          limits:
            cpu: 500m
            memory: 256Mi
      - name: backend
        image: ${backend_image}
        startupProbe:
          httpGet:
            path: /api/v1/utils/health-check/
            port: 9000
          initialDelaySeconds: 20
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 18
        livenessProbe:
          httpGet:
            path: /api/v1/utils/health-check/
            port: 9000
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        env:
        - name: ENVIRONMENT
          value: '${environment}'
        - name: PROJECT_NAME
          value: '${project_name}'
        - name: API_V1_STR
          value: '${api_v1_str}'
        - name: BACKEND_CORS_ORIGINS
          value: '${backend_cors_origins}'
        - name: FRONTEND_HOST
          value: '${frontend_host}'
        - name: CLOUD_SQL_INSTANCE_CONNECTION_NAME
          value: '${cloud_sql_connection_name}'
        - name: POSTGRES_SERVER
          value: "localhost"
        - name: POSTGRES_DB
          value: '${cloud_sql_db}'
        - name: POSTGRES_USER
          value: '${cloud_sql_user}'
        - name: RUN_DATA_IMPORTS
          value: '${run_data_imports}'
        - name: RUN_STARTUP_DATA_IMPORTS
          value: '${run_startup_data_imports}'
        - name: IMPORT_GCS_URI
          value: '${import_gcs_uri}'
        - name: IMPORT_RESOURCES_LOCAL_PATH
          value: '${import_resources_local_path}'
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              key: latest
              name: capanel-secret-key
        - name: FIRST_SUPERUSER
          valueFrom:
            secretKeyRef:
              key: latest
              name: capanel-superuser-email
        - name: FIRST_SUPERUSER_PASSWORD
          valueFrom:
            secretKeyRef:
              key: latest
              name: capanel-superuser-password
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              key: latest
              name: capanel-postgres-password
        resources:
          limits:
            cpu: 1000m
            memory: 2Gi
"""


def build_env() -> RenderEnv:
    return RenderEnv(
        full_service=env_required("FULL_SERVICE"),
        gcp_region=env_required("GCP_REGION"),
        run_service_account_email=env_required("RUN_SERVICE_ACCOUNT_EMAIL"),
        frontend_image=env_required("FRONTEND_IMAGE"),
        backend_image=env_required("BACKEND_IMAGE"),
        cloud_sql_connection_name=env_required("CLOUD_SQL_CONNECTION_NAME"),
        environment=env_required("ENVIRONMENT"),
        project_name=env_required("PROJECT_NAME"),
        api_v1_str=env_required("API_V1_STR"),
        backend_cors_origins=env_required("BACKEND_CORS_ORIGINS"),
        frontend_host=env_required("FRONTEND_HOST"),
        cloud_sql_db=env_required("CLOUD_SQL_DB"),
        cloud_sql_user=env_required("CLOUD_SQL_USER"),
        run_data_imports=env_required("RUN_DATA_IMPORTS"),
        run_startup_data_imports=env_required("RUN_STARTUP_DATA_IMPORTS"),
        import_gcs_uri=env_required("IMPORT_GCS_URI"),
        import_resources_local_path=env_required("IMPORT_RESOURCES_LOCAL_PATH"),
        vpc_network=os.environ.get("VPC_NETWORK") or None,
        vpc_subnet=os.environ.get("VPC_SUBNET") or None,
    )


def network_annotations(env: RenderEnv) -> str:
    if env.vpc_network and env.vpc_subnet:
        return (
            "        run.googleapis.com/network-interfaces: "
            f'\'[{{"network":"{env.vpc_network}","subnetwork":"{env.vpc_subnet}"}}]\'\n'
            "        run.googleapis.com/vpc-access-egress: private-ranges-only\n"
        )
    return ""


def main() -> int:
    env = build_env()
    output = TEMPLATE
    output = output.replace("${full_service}", env.full_service)
    output = output.replace("${gcp_region}", env.gcp_region)
    output = output.replace(
        "${run_service_account_email}", env.run_service_account_email
    )
    output = output.replace("${frontend_image}", env.frontend_image)
    output = output.replace("${backend_image}", env.backend_image)
    output = output.replace(
        "${cloud_sql_connection_name}", env.cloud_sql_connection_name
    )
    output = output.replace("${environment}", yaml_escape(env.environment))
    output = output.replace("${project_name}", yaml_escape(env.project_name))
    output = output.replace("${api_v1_str}", yaml_escape(env.api_v1_str))
    output = output.replace(
        "${backend_cors_origins}", yaml_escape(env.backend_cors_origins)
    )
    output = output.replace("${frontend_host}", yaml_escape(env.frontend_host))
    output = output.replace("${cloud_sql_db}", yaml_escape(env.cloud_sql_db))
    output = output.replace("${cloud_sql_user}", yaml_escape(env.cloud_sql_user))
    output = output.replace("${run_data_imports}", yaml_escape(env.run_data_imports))
    output = output.replace(
        "${run_startup_data_imports}", yaml_escape(env.run_startup_data_imports)
    )
    output = output.replace("${import_gcs_uri}", yaml_escape(env.import_gcs_uri))
    output = output.replace(
        "${import_resources_local_path}", yaml_escape(env.import_resources_local_path)
    )
    output = output.replace("${network_annotations}", network_annotations(env))

    print(output, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ScriptError as exc:
        raise SystemExit(str(exc)) from exc
