# AWS ECS And Dynatrace Pilot

This guide deploys two Lumens reference containers to AWS ECS Fargate:

```text
Internet -> ALB -> Java Spring Boot BFF -> Cloud Map -> Python FastAPI integration
                         |                                  |
                         +----------- OTLP/HTTP ------------+
                                              |
                                              v
                                      Dynatrace OTLP endpoint
```

The Java BFF is public through an Application Load Balancer. The FastAPI integration service is private and discovered through AWS Cloud Map. Both tasks run in private subnets and use a NAT gateway for Dynatrace egress. The Java image includes a pinned OpenTelemetry Java Agent, while the Python image uses the official FastAPI instrumentor and OTLP SDK configuration.

## What You Need

1. An AWS account and a region. The Terraform baseline defaults to two Availability Zones and one NAT gateway, which incurs AWS charges.
2. An AWS bootstrap identity with permission to create S3, DynamoDB, IAM, and GitHub OIDC resources. Use it once for `infra/bootstrap`.
3. A GitHub repository and permission to configure GitHub Actions variables, secrets, and the `aws-pilot` environment.
4. A Dynatrace trial tenant.
5. A Dynatrace OTLP endpoint and an API token with current ingest permissions for the signals you plan to test. Confirm current token scopes in Dynatrace documentation.
6. Docker access in GitHub Actions and AWS account permissions through the generated GitHub OIDC role.

## Bootstrap Terraform State And GitHub OIDC

Copy the example and set values that are unique to your environment:

```powershell
Copy-Item infra/bootstrap/terraform.tfvars.example infra/bootstrap/terraform.tfvars
terraform -chdir=infra/bootstrap init
terraform -chdir=infra/bootstrap apply
```

Record these outputs:

```powershell
terraform -chdir=infra/bootstrap output
```

The bootstrap role policy is intentionally broad enough to create the pilot infrastructure. Restrict it to naming prefixes and required AWS resources before a production rollout.

## Configure GitHub

Create a GitHub environment named `aws-pilot` and protect it with approval if appropriate.

Add these GitHub Actions **variables**:

| Variable | Value |
|---|---|
| `AWS_REGION` | Deployment region, such as `eu-west-1` |
| `AWS_GITHUB_DEPLOY_ROLE_ARN` | `github_deploy_role_arn` bootstrap output |
| `TF_STATE_BUCKET` | `state_bucket` bootstrap output |
| `TF_LOCK_TABLE` | `lock_table` bootstrap output |
| `LUMENS_NAME_PREFIX` | Unique lowercase deployment prefix, for example `lumens-pilot` |
| `DYNATRACE_OTLP_ENDPOINT` | Full Dynatrace OTLP endpoint, ending in `/api/v2/otlp` |
| `DYNATRACE_HEADERS_SECRET_NAME` | `lumens/dynatrace/otlp-headers` or your chosen secret name |

Add this GitHub Actions **secret**:

| Secret | Value |
|---|---|
| `DYNATRACE_OTLP_HEADERS` | `Authorization=Api-Token <Dynatrace token>` |

The deployment workflow copies this value to AWS Secrets Manager. ECS injects it into tasks as `OTEL_EXPORTER_OTLP_HEADERS`. The value is never placed in Terraform variables, Terraform state, task definitions, image layers, source code, or CloudWatch logs.

## Deploy

Run the GitHub Actions workflow **deploy-ecs-pilot**, or push an approved change to `main` affecting application or infrastructure files.

The workflow:

1. Creates ECR repositories and the empty Secrets Manager secret container.
2. Builds and pushes immutable Java and Python container images.
3. Writes the Dynatrace header secret to Secrets Manager.
4. Applies ECS, networking, ALB, Cloud Map, task-definition, log-group, and service infrastructure.
5. Outputs the public BFF URL.

## Test The Deployment

Copy the `BFF URL` workflow output and call:

```powershell
Invoke-RestMethod http://<alb-dns-name>/enrich
```

Expected response:

```json
{
  "outcome": "success"
}
```

Then verify in AWS:

- Both ECS services have one healthy task.
- The ALB target group reports the Java BFF healthy.
- CloudWatch log groups show no secret values.

Then verify in Dynatrace:

- Services appear as `<prefix>-java-bff` and `<prefix>-python-integration`.
- A call to `/enrich` creates a Java server span, Java HTTP client span, Python server span, and Python internal operation span.
- Trace context is shared across both services.
- `lumens.operation.executions` and `lumens.operation.duration` are present.
- No token, authorization header, request body, or raw customer identifier appears in telemetry.

## Destroy The Pilot

Use the same backend configuration used by CI, then destroy from a controlled administrative environment:

```powershell
terraform -chdir=infra/ecs destroy
```

ECR repositories use `force_delete` for a pilot. The bootstrap state bucket, lock table, GitHub OIDC provider, and deployment role are intentionally separate and must be destroyed explicitly only when no longer needed.
