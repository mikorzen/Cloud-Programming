terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}


provider "aws" {
  region = var.region  # Ustawienie regionu instancji
}


resource "aws_key_pair" "tf_key" {
  key_name   = var.key_name  # Ustawienie nazwy dla klucza SSH
  public_key = tls_private_key.rsa.public_key_openssh  # Ustawienie klucza publicznego
}


resource "aws_vpc" "vpc" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true  # Włączenie hostname'ów dla DNS
  enable_dns_support   = true  # Włączenie DNS
}


resource "aws_subnet" "subnet" {
  vpc_id                  = aws_vpc.vpc.id
  cidr_block              = cidrsubnet(aws_vpc.vpc.cidr_block, 8, 1)  # Podział CIDR VPC na podsieć
  availability_zone       = var.availability_zone  # Wybór strefy dostępności (us-east-1a)
  map_public_ip_on_launch = true
}


resource "aws_internet_gateway" "gateway" {  # Utworzenie bramy do Internetu
  vpc_id = aws_vpc.vpc.id
}


resource "aws_route_table" "route" {  # Utworzenie tablicy routingu
  vpc_id = aws_vpc.vpc.id

  route {
    cidr_block = "0.0.0.0/0"  # Ustawienie trasy dla wszystkich przez bramę
    gateway_id = aws_internet_gateway.gateway.id
  }
}


resource "aws_main_route_table_association" "association" {  # Ustawienie stworzonej tablicy routingu jako domyślnej
  vpc_id         = aws_vpc.vpc.id
  route_table_id = aws_route_table.route.id
}


resource "aws_security_group" "security" {
  vpc_id = aws_vpc.vpc.id

  ingress {  # Zezwolenie na ruch przychodzący na port 22 (SSH)
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {  # Zezwolenie na ruch przychodzący na port 80 (HTTP)
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {  # Zezwolenie na ruch przychodzący na port 443 (HTTPS)
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {  # Zezwolenie na ruch przychodzący na port 8080 (aplikacja)
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {  # Zezwolenie na ruch wychodzący na wszystkie porty
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "instance" {
  ami                         = var.image_id  # Wybór obrazu AMI dla maszyny (Amazon Linux 2023)
  instance_type               = var.instance_type  # Wybór typu instancji (t2.micro, jedyna opcja dostępna dla free tier)
  subnet_id                   = aws_subnet.subnet.id  # Przypisanie instancji do podsieci
  vpc_security_group_ids      = [aws_security_group.security.id]  # Przypisanie grupy reguł bezpieczeństwa
  key_name                    = var.key_name  # Przypisanie klucza SSH
  associate_public_ip_address = true  # Ustawienie przydzielenia publicznego adresu IP

  tags = {
    Name = var.instance_name  # Ustawienie nazwy instancji
  }
}