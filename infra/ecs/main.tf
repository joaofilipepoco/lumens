locals {
  name = var.name_prefix
  tags = merge({ Project = "Lumens", ManagedBy = "Terraform" }, var.tags)
  otlp_environment = [
    { name = "OTEL_EXPORTER_OTLP_PROTOCOL", value = "http/protobuf" },
    { name = "OTEL_EXPORTER_OTLP_ENDPOINT", value = var.dynatrace_otlp_endpoint }
  ]
  otlp_header_secret = [{
    name      = "OTEL_EXPORTER_OTLP_HEADERS"
    valueFrom = aws_secretsmanager_secret.dynatrace_headers.arn
  }]
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "this" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags                 = merge(local.tags, { Name = "${local.name}-vpc" })
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
  tags   = local.tags
}

resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.this.id
  cidr_block              = cidrsubnet(aws_vpc.this.cidr_block, 8, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags                    = merge(local.tags, { Name = "${local.name}-public-${count.index}" })
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.this.id
  cidr_block        = cidrsubnet(aws_vpc.this.cidr_block, 8, count.index + 10)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags              = merge(local.tags, { Name = "${local.name}-private-${count.index}" })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id
  tags   = local.tags
}
resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this.id
}
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
resource "aws_eip" "nat" {
  domain = "vpc"
  tags   = local.tags
}
resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
  depends_on    = [aws_internet_gateway.this]
  tags          = local.tags
}
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.this.id
  tags   = local.tags
}
resource "aws_route" "private_nat" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.this.id
}
resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

resource "aws_ecr_repository" "bff" {
  name                 = "${local.name}-java-bff"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = true
  tags                 = local.tags
}
resource "aws_ecr_repository" "integration" {
  name                 = "${local.name}-python-integration"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = true
  tags                 = local.tags
}
resource "aws_ecs_cluster" "this" {
  name = "${local.name}-cluster"
  tags = local.tags
}
resource "aws_service_discovery_private_dns_namespace" "this" {
  name = "${local.name}.local"
  vpc  = aws_vpc.this.id
  tags = local.tags
}
resource "aws_service_discovery_service" "integration" {
  name = "python-integration"
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.this.id
    dns_records {
      ttl  = 10
      type = "A"
    }
    routing_policy = "MULTIVALUE"
  }
}

resource "aws_security_group" "alb" {
  name   = "${local.name}-alb"
  vpc_id = aws_vpc.this.id
  tags   = local.tags
}
resource "aws_vpc_security_group_ingress_rule" "alb_http" {
  security_group_id = aws_security_group.alb.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}
resource "aws_vpc_security_group_egress_rule" "alb_all" {
  security_group_id = aws_security_group.alb.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
resource "aws_security_group" "bff" {
  name   = "${local.name}-bff"
  vpc_id = aws_vpc.this.id
  tags   = local.tags
}
resource "aws_vpc_security_group_ingress_rule" "bff_alb" {
  security_group_id            = aws_security_group.bff.id
  referenced_security_group_id = aws_security_group.alb.id
  from_port                    = 8080
  to_port                      = 8080
  ip_protocol                  = "tcp"
}
resource "aws_vpc_security_group_egress_rule" "bff_all" {
  security_group_id = aws_security_group.bff.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}
resource "aws_security_group" "integration" {
  name   = "${local.name}-integration"
  vpc_id = aws_vpc.this.id
  tags   = local.tags
}
resource "aws_vpc_security_group_ingress_rule" "integration_bff" {
  security_group_id            = aws_security_group.integration.id
  referenced_security_group_id = aws_security_group.bff.id
  from_port                    = 8081
  to_port                      = 8081
  ip_protocol                  = "tcp"
}
resource "aws_vpc_security_group_egress_rule" "integration_all" {
  security_group_id = aws_security_group.integration.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_lb" "this" {
  name               = "${local.name}-alb"
  load_balancer_type = "application"
  subnets            = aws_subnet.public[*].id
  security_groups    = [aws_security_group.alb.id]
  tags               = local.tags
}
resource "aws_lb_target_group" "bff" {
  name        = "${local.name}-bff"
  port        = 8080
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.this.id
  health_check {
    path    = "/actuator/health"
    matcher = "200"
  }
  tags = local.tags
}
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.bff.arn
  }
}

data "aws_iam_policy_document" "task_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}
resource "aws_iam_role" "execution" {
  name               = "${local.name}-ecs-execution"
  assume_role_policy = data.aws_iam_policy_document.task_assume.json
  tags               = local.tags
}
resource "aws_iam_role_policy_attachment" "execution" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
resource "aws_iam_role" "task" {
  name               = "${local.name}-ecs-task"
  assume_role_policy = data.aws_iam_policy_document.task_assume.json
  tags               = local.tags
}
resource "aws_secretsmanager_secret" "dynatrace_headers" {
  name = var.dynatrace_headers_secret_name
  tags = local.tags
}
data "aws_iam_policy_document" "execution_secret" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = [aws_secretsmanager_secret.dynatrace_headers.arn]
  }
}
resource "aws_iam_role_policy" "execution_secret" {
  name   = "read-dynatrace-headers"
  role   = aws_iam_role.execution.id
  policy = data.aws_iam_policy_document.execution_secret.json
}

resource "aws_cloudwatch_log_group" "bff" {
  name              = "/ecs/${local.name}-java-bff"
  retention_in_days = 14
  tags              = local.tags
}
resource "aws_cloudwatch_log_group" "integration" {
  name              = "/ecs/${local.name}-python-integration"
  retention_in_days = 14
  tags              = local.tags
}

resource "aws_ecs_task_definition" "integration" {
  family                   = "${local.name}-python-integration"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn
  container_definitions = jsonencode([{
    name             = "python-integration", image = "${aws_ecr_repository.integration.repository_url}:${var.image_tag}", essential = true,
    portMappings     = [{ containerPort = 8081 }],
    environment      = concat(local.otlp_environment, [{ name = "OTEL_SERVICE_NAME", value = "${local.name}-python-integration" }]),
    secrets          = local.otlp_header_secret,
    logConfiguration = { logDriver = "awslogs", options = { awslogs-group = aws_cloudwatch_log_group.integration.name, awslogs-region = var.aws_region, awslogs-stream-prefix = "ecs" } },
    healthCheck      = { command = ["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8081/health')\""], interval = 30, timeout = 5, retries = 3, startPeriod = 20 }
  }])
  tags = local.tags
}
resource "aws_ecs_service" "integration" {
  name            = "${local.name}-python-integration"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.integration.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.integration.id]
    assign_public_ip = false
  }
  service_registries { registry_arn = aws_service_discovery_service.integration.arn }
  tags = local.tags
}

resource "aws_ecs_task_definition" "bff" {
  family                   = "${local.name}-java-bff"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn
  container_definitions = jsonencode([{
    name             = "java-bff", image = "${aws_ecr_repository.bff.repository_url}:${var.image_tag}", essential = true,
    portMappings     = [{ containerPort = 8080 }],
    environment      = concat(local.otlp_environment, [{ name = "OTEL_SERVICE_NAME", value = "${local.name}-java-bff" }, { name = "LUMENS_OBSERVABILITY_MODE", value = "platform-managed" }, { name = "PYTHON_INTEGRATION_URL", value = "http://python-integration.${aws_service_discovery_private_dns_namespace.this.name}:8081" }]),
    secrets          = local.otlp_header_secret,
    logConfiguration = { logDriver = "awslogs", options = { awslogs-group = aws_cloudwatch_log_group.bff.name, awslogs-region = var.aws_region, awslogs-stream-prefix = "ecs" } }
  }])
  tags = local.tags
}
resource "aws_ecs_service" "bff" {
  name            = "${local.name}-java-bff"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.bff.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.bff.id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.bff.arn
    container_name   = "java-bff"
    container_port   = 8080
  }
  depends_on = [aws_lb_listener.http]
  tags       = local.tags
}

output "bff_url" { value = "http://${aws_lb.this.dns_name}" }
output "bff_repository_url" { value = aws_ecr_repository.bff.repository_url }
output "integration_repository_url" { value = aws_ecr_repository.integration.repository_url }
output "dynatrace_headers_secret_arn" { value = aws_secretsmanager_secret.dynatrace_headers.arn }
