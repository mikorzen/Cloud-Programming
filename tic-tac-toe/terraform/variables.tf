variable key_name {
    description = "Name of the key pair"
    type        = string
    default     = "tf_key"
}

variable "key_file" {
    description = "Name of the key file"
    type        = string
    default     = "tf_key.pem"
}

variable region {
    description = "AWS region"
    type        = string
    default     = "us-east-1"
}

variable image_id {
    description = "AMI ID"
    type        = string
    default     = "ami-051f8a213df8bc089"
}

variable instance_type {
    description = "Instance type"
    type        = string
    default     = "t2.micro"
}

variable instance_name {
    description = "Name of the instance"
    type        = string
    default     = "TicTacToe"
}

variable availability_zone {
    description = "Availability zone"
    type        = string
    default     = "us-east-1a"
}

variable cidr_block {
    description = "CIDR block for the VPC"
    type        = string
    default     = "10.0.0.0/16"
}