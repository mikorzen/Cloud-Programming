variable "key_name" {
  description = "Name of the key pair"
  type        = string
  default     = "tf_key"
}

variable "key_file" {
  description = "Name of the key file"
  type        = string
  default     = "tf_key.pem"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "ecr_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "tictactoe-repo"
}

variable "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
  default     = "tictactoe-cluster"
}

variable "ecs_task_name" {
  description = "Name of the ECS task"
  type        = string
  default     = "tictactoe-task"
}

variable "ecs_network_mode" {
  description = "Network mode for the ECS task"
  type        = string
  default     = "awsvpc"
}

variable "ecs_type" {
  description = "Type of the ECS task"
  type        = string
  default     = "FARGATE"
}

variable "ecs_container_name" {
  description = "Name of the ECS container"
  type        = string
  default     = "tictactoe-container"
}


variable "ecs_cpu" {
  description = "CPU units for the ECS task"
  type        = number
  default     = 256
}

variable "ecs_memory" {
  description = "Memory for the ECS task"
  type        = number
  default     = 512
}

variable "ecs_service_name" {
  description = "Name of the ECS service"
  type        = string
  default     = "tictactoe-service"
}

variable "ecs_service_instance_count" {
  description = "Number of instances for the ECS service"
  type        = number
  default     = 1
}
