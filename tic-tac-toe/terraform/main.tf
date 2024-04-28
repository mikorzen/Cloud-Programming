terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}


provider "aws" {
  region = var.region # Ustawienie regionu instancji
}


data "aws_vpc" "vpc" {
  default = true # Ustawienie domyślnej sieci VPC
}


resource "aws_security_group" "security" {
  vpc_id = data.aws_vpc.vpc.id

  ingress { # Zezwolenie na ruch przychodzący na port 22 (SSH)
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress { # Zezwolenie na ruch przychodzący na port 80 (HTTP)
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress { # Zezwolenie na ruch przychodzący na port 443 (HTTPS)
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress { # Zezwolenie na ruch przychodzący na port 8080 (aplikacja)
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress { # Zezwolenie na ruch wychodzący na wszystkie porty
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


data "aws_subnets" "subnets" { # Pobranie informacji o podsieciach w VPC
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.vpc.id]
  }
}


resource "aws_ecr_repository" "ecr" {
  name = "tictactoe-repo" # Utworzenie repozytorium ECR (Elastic Container Registry)
}


resource "aws_alb" "lb" {
  name               = "tictactoe-lb"                   # Utworzenie Load Balancera
  load_balancer_type = "application"                    # Ustawienie typu Load Balancera
  security_groups    = [aws_security_group.security.id] # Ustawienie grupy zabezpieczeń
  subnets            = data.aws_subnets.subnets.ids     # Ustawienie podsieci
}


resource "aws_alb_target_group" "lb_target_group" {
  name     = "tictactoe-tg" # Utworzenie grupy docelowej Load Balancera
  port     = 80             # Ustawienie portu
  protocol = "HTTP"         # Ustawienie protokołu
  vpc_id   = data.aws_vpc.vpc.id
}


resource "aws_alb_listener" "lb_listener" {
  load_balancer_arn = aws_alb.lb.arn # Przypisanie Load Balancera do słuchacza
  port              = "80"           #
  protocol          = "HTTP"         # Nasłuchiwanie na HTTP

  default_action {
    type             = "forward"                                # Ustawienie akcji słuchacza
    target_group_arn = aws_alb_target_group.lb_target_group.arn # Przypisanie grupy docelowej
  }
}


resource "aws_ecs_cluster" "ecs_cluster" {
  name = "tictactoe-cluster" # Utworzenie klastra ECS (Elastic Container Service)
}


resource "aws_ecs_task_definition" "ecs_task" {
  family                   = var.ecs_task_name    # Utworzenie definicji zadania ECS
  network_mode             = var.ecs_network_mode # Ustawienie trybu sieciowego
  requires_compatibilities = [var.ecs_type]       # Ustawienie kompatybilności z Fargate

  execution_role_arn = "arn:aws:iam::861864057306:role/LabRole" # Ustawienie roli wykonawczej dla zadania

  container_definitions = jsonencode([ # Konfiguracja kontenera
    {
      name   = var.ecs_container_name
      image  = "${aws_ecr_repository.ecr.repository_url}:latest" # Ustawienie obrazu Dockerowego
      cpu    = var.ecs_cpu                                       # Ustawienie CPU
      memory = var.ecs_memory                                    # Ustawienie pamięci
      port_mappings = [{                                         # Mapowanie portów
        container_port = 8080
        host_port      = 8080
        protocol       = "tcp"
      }]
    }
  ])

  cpu    = var.ecs_cpu    # Ustawienie CPU dla całego zadania
  memory = var.ecs_memory # Ustawienie pamięci dla całego zadania
}


resource "aws_ecs_service" "ecs_service" {
  name            = var.ecs_service_name
  cluster         = aws_ecs_cluster.ecs_cluster.id       # Ustawienie klastra ECS dla serwisu
  task_definition = aws_ecs_task_definition.ecs_task.arn # Ustawienie definicji zadania dla serwisu
  desired_count   = var.ecs_service_instance_count       # Ustawienie liczby instancji kontenera
  launch_type     = var.ecs_type                         # Ustawienie typu uruchomienia kontenera

  network_configuration { # Konfiguracja sieciowa serwisu
    subnets          = data.aws_subnets.subnets.ids
    security_groups  = [aws_security_group.security.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_alb_target_group.lb_target_group.arn
    container_name   = var.ecs_container_name
    container_port   = 8080
  }
}
