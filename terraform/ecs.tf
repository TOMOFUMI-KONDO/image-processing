//resource "aws_ecs_cluster" "main" {
//  name = var.project
//
//  tags = {
//    Project = var.project
//  }
//}

// https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_container_instance.html
// clusterへのinstanceの登録がうまくできなかったので、現状cluster+instanceの作成だけweb consoleから行っています
data "aws_ecs_cluster" "main" {
  cluster_name = var.project
}

resource "aws_ecs_service" "main" {
  name            = var.project
  cluster         = data.aws_ecs_cluster.main.arn
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = 1
  launch_type     = "EC2"

  network_configuration {
    subnets         = [aws_subnet.public_a.id, aws_subnet.public_c.id]
    security_groups = [aws_security_group.ecs.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.main.arn
    container_name   = "nginx"
    container_port   = 80
  }

  depends_on = [aws_lb_target_group.main]

  tags = {
    Project = var.project
  }
}

resource "aws_ecs_task_definition" "main" {
  family                   = var.project
  requires_compatibilities = ["EC2"]
  network_mode             = "awsvpc"
  execution_role_arn       = data.aws_iam_role.ecsTaskExecutionRole.arn

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = var.container_image_uri.app
      essential = true
      cpu       = 3072
      memory    = 60000
      resourceRequirements = [{
        type  = "GPU"
        value = "1"
      }]
      environment = [
        { name : "APP_ENV", value : "production" },
        { name : "S3_BUCKET ", value : var.s3_bucket },
        { name : "TZ1 ", value : "Asia/Tokyo" }
      ]
      logConfiguration = {
        logDriver : "awslogs",
        options : {
          awslogs-region : "ap-northeast-1",
          awslogs-stream-prefix : "app",
          awslogs-group : "/zoom-deco/ecs/app"
        }
      },
    },
    {
      name      = "nginx"
      image     = var.container_image_uri.nginx
      essential = true
      // TODO: port mappingの仕組みについて確認する
      portMappings = [
        {
          protocol      = "tcp"
          containerPort = 80
          hostPort      = 80
        }
      ]
      cpu    = 512
      memory = 300
      environment = [
        { name : "TZ1", value : "Asia/Tokyo" }
      ]
      logConfiguration = {
        logDriver : "awslogs",
        options : {
          awslogs-region : "ap-northeast-1",
          awslogs-stream-prefix : "nginx",
          awslogs-group : "/zoom-deco/ecs/nginx"
        }
      }
    }
  ])

  depends_on = [aws_cloudwatch_log_group.app, aws_cloudwatch_log_group.nginx]

  tags = {
    Project = var.project
  }
}

data "aws_iam_role" "ecsTaskExecutionRole" {
  name = "ecsTaskExecutionRole"
}

resource "aws_security_group" "ecs" {
  description = "This is a security group for ecs."
  name        = "${var.project}-sg-ecs"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = [var.cidr_default_gateway.ipv4] #tfsec:ignore:AWS009
    ipv6_cidr_blocks = [var.cidr_default_gateway.ipv6] #tfsec:ignore:AWS009
  }

  tags = {
    Name    = "${var.project}-sg-ecs"
    project = var.project
  }
}

resource "aws_security_group_rule" "ssh" {
  description       = "This allows ssh from admin."
  security_group_id = aws_security_group.ecs.id
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = [var.my_global_ip]
}

resource "aws_security_group_rule" "ecs_http" {
  description              = "This allows http ALB."
  security_group_id        = aws_security_group.ecs.id
  type                     = "ingress"
  from_port                = 80
  to_port                  = 80
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.public_alb.id
}
