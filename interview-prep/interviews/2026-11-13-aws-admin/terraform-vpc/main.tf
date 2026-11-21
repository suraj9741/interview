# =====================================================================
# Full AWS network + web server, the classic interview layout:
#
#   VPC 10.0.0.0/16 (ap-south-1)
#   ├── 2 public subnets  (AZ a, b)  → route 0.0.0.0/0 → Internet Gateway
#   │      ALB lives here, plus the NAT gateway
#   └── 2 private subnets (AZ a, b)  → route 0.0.0.0/0 → NAT gateway
#          EC2 app servers live here (no public IP)
#
#   Internet → ALB (SG: 80/443 from anywhere) → EC2 (SG: 80 only from ALB SG)
#   EC2 → NAT GW → IGW → internet   (outbound only, e.g. yum update)
# =====================================================================

# ---------- 1. Terraform + provider + remote state ----------
terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket       = "suraj-tf-state" # must already exist, versioning ON
    key          = "prod/network/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true # S3 native locking (1.10+)
  }
}

provider "aws" {
  region = var.region

  default_tags { # added to every resource
    tags = {
      project = var.project
      managed = "terraform"
    }
  }
}

# ---------- 2. Variables ----------
variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "project" {
  type    = string
  default = "demo"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "public_subnets" { # AZ suffix => CIDR
  type = map(string)
  default = {
    a = "10.0.1.0/24"
    b = "10.0.2.0/24"
  }
}

variable "private_subnets" {
  type = map(string)
  default = {
    a = "10.0.11.0/24"
    b = "10.0.12.0/24"
  }
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

# ---------- 3. Data sources (read, don't create) ----------
data "aws_ami" "al2023" { # latest Amazon Linux 2023
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

# ---------- 4. VPC ----------
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true # the .2 resolver works
  enable_dns_hostnames = true # instances get DNS names

  tags = { Name = "${var.project}-vpc" }
}

# ---------- 5. Internet Gateway (the VPC's door to the internet) ----------
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = { Name = "${var.project}-igw" }
}

# ---------- 6. Subnets (for_each = one per AZ, keyed by "a"/"b") ----------
resource "aws_subnet" "public" {
  for_each = var.public_subnets

  vpc_id                  = aws_vpc.main.id
  cidr_block              = each.value
  availability_zone       = "${var.region}${each.key}" # ap-south-1a, 1b
  map_public_ip_on_launch = true

  tags = { Name = "${var.project}-public-${each.key}" }
}

resource "aws_subnet" "private" {
  for_each = var.private_subnets

  vpc_id            = aws_vpc.main.id
  cidr_block        = each.value
  availability_zone = "${var.region}${each.key}"

  tags = { Name = "${var.project}-private-${each.key}" }
}

# ---------- 7. NAT gateway (outbound internet for private subnets) ----------
resource "aws_eip" "nat" { # fixed public IP for the NAT
  domain = "vpc"

  tags = { Name = "${var.project}-nat-eip" }
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public["a"].id # NAT must sit in a PUBLIC subnet

  tags = { Name = "${var.project}-nat" }

  depends_on = [aws_internet_gateway.igw] # IGW must exist first
}
# Production: one NAT per AZ (for_each over public subnets) so losing
# one AZ doesn't cut the other off. One NAT here to keep cost down.

# ---------- 8. Route tables ----------
# Public: default route to the IGW. This route is what makes a subnet "public".
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = { Name = "${var.project}-public-rt" }
}

# Private: default route to the NAT gateway (outbound only).
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = { Name = "${var.project}-private-rt" }
}
# The "local" route (10.0.0.0/16 → local) is added automatically to both.

# Associations: link each subnet to its route table.
resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  for_each = aws_subnet.private

  subnet_id      = each.value.id
  route_table_id = aws_route_table.private.id
}

# ---------- 9. Security groups ----------
# ALB: HTTP/HTTPS from the internet.
resource "aws_security_group" "alb" {
  name        = "${var.project}-alb-sg"
  description = "Internet to ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Terraform removes AWS's default allow-all egress, so declare it
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# App EC2: port 80 ONLY from the ALB's security group (not from the internet).
resource "aws_security_group" "app" {
  name        = "${var.project}-app-sg"
  description = "ALB to app servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "HTTP from ALB only"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id] # SG reference, survives scaling
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # outbound via NAT (yum, APIs)
  }
}
# No port 22: we connect with SSM Session Manager instead (role below).

# ---------- 10. IAM role for EC2 (SSM access, no SSH keys) ----------
resource "aws_iam_role" "ec2" {
  name = "${var.project}-ec2-role"

  assume_role_policy = jsonencode({ # trust policy: who may assume it
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2" { # the "container" that puts a role on EC2
  name = "${var.project}-ec2-profile"
  role = aws_iam_role.ec2.name
}

# ---------- 11. EC2 app servers (one per private subnet) ----------
resource "aws_instance" "app" {
  for_each = aws_subnet.private

  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  subnet_id              = each.value.id # PRIVATE subnet, no public IP
  vpc_security_group_ids = [aws_security_group.app.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2.name

  metadata_options {
    http_tokens = "required" # IMDSv2 only (blocks SSRF tricks)
  }

  user_data = <<-EOT
    #!/bin/bash
    dnf install -y nginx
    echo "hello from $(hostname)" > /usr/share/nginx/html/index.html
    systemctl enable --now nginx
  EOT

  tags = { Name = "${var.project}-app-${each.key}" }
}

# ---------- 12. Application Load Balancer ----------
resource "aws_lb" "web" {
  name               = "${var.project}-alb"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.alb.id]
  subnets            = [for s in aws_subnet.public : s.id] # needs 2+ AZs
}

resource "aws_lb_target_group" "app" {
  name     = "${var.project}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/"
    matcher             = "200"
    interval            = 15
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_target_group_attachment" "app" {
  for_each = aws_instance.app

  target_group_arn = aws_lb_target_group.app.arn
  target_id        = each.value.id
  port             = 80
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.web.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
# HTTPS: add a listener on 443 with certificate_arn = an ACM cert,
# and change the port-80 listener to a redirect to 443.

# ---------- 13. Outputs ----------
output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = [for s in aws_subnet.public : s.id]
}

output "private_subnet_ids" {
  value = [for s in aws_subnet.private : s.id]
}

output "nat_public_ip" {
  value = aws_eip.nat.public_ip
}

output "alb_dns_name" {
  value = aws_lb.web.dns_name # open this in a browser
}
