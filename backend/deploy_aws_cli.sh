#!/bin/bash

# AltMX AWS Production Deployment using AWS CLI
# Simple and direct approach - no Python orchestration

set -e  # Exit on any error

echo "=== AltMX AWS Production Deployment ==="
echo "Using direct AWS CLI approach"

# Using existing AWS CLI configuration

# Configuration
AWS_REGION="ap-northeast-1"
APP_NAME="altmx-prod"
DEPLOYMENT_ID=$(date +%Y%m%d-%H%M%S)
STACK_NAME="${APP_NAME}-${DEPLOYMENT_ID}"

echo "Deployment ID: $DEPLOYMENT_ID"
echo "Stack Name: $STACK_NAME"

# 1. Create VPC
echo "Step 1: Creating VPC..."
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --region $AWS_REGION \
  --query 'Vpc.VpcId' \
  --output text)
echo "VPC Created: $VPC_ID"

# Tag VPC
aws ec2 create-tags --resources $VPC_ID --tags Key=Name,Value="${APP_NAME}-vpc" --region $AWS_REGION

# 2. Create Internet Gateway
echo "Step 2: Creating Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway \
  --region $AWS_REGION \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)
echo "Internet Gateway Created: $IGW_ID"

# Attach IGW to VPC
aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID --region $AWS_REGION

# 3. Create Public Subnet
echo "Step 3: Creating Public Subnet..."
PUBLIC_SUBNET_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone ${AWS_REGION}a \
  --region $AWS_REGION \
  --query 'Subnet.SubnetId' \
  --output text)
echo "Public Subnet Created: $PUBLIC_SUBNET_ID"

# 4. Create Private Subnet
echo "Step 4: Creating Private Subnet..."
PRIVATE_SUBNET_ID=$(aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone ${AWS_REGION}c \
  --region $AWS_REGION \
  --query 'Subnet.SubnetId' \
  --output text)
echo "Private Subnet Created: $PRIVATE_SUBNET_ID"

# 5. Create Route Table for Public Subnet
echo "Step 5: Creating Route Table..."
ROUTE_TABLE_ID=$(aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --region $AWS_REGION \
  --query 'RouteTable.RouteTableId' \
  --output text)
echo "Route Table Created: $ROUTE_TABLE_ID"

# Add route to Internet Gateway
aws ec2 create-route \
  --route-table-id $ROUTE_TABLE_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID \
  --region $AWS_REGION

# Associate route table with public subnet
aws ec2 associate-route-table \
  --subnet-id $PUBLIC_SUBNET_ID \
  --route-table-id $ROUTE_TABLE_ID \
  --region $AWS_REGION

# 6. Create Security Group
echo "Step 6: Creating Security Group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
  --group-name "${APP_NAME}-sg" \
  --description "AltMX Production Security Group" \
  --vpc-id $VPC_ID \
  --region $AWS_REGION \
  --query 'GroupId' \
  --output text)
echo "Security Group Created: $SECURITY_GROUP_ID"

# Add rules to security group
aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region $AWS_REGION

aws ec2 authorize-security-group-ingress \
  --group-id $SECURITY_GROUP_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0 \
  --region $AWS_REGION

# 7. Create ECR Repository
echo "Step 7: Creating ECR Repository..."
aws ecr create-repository \
  --repository-name $APP_NAME \
  --region $AWS_REGION || echo "ECR Repository may already exist"

# 8. Build and Push Docker Image
echo "Step 8: Building and Pushing Docker Image..."
ECR_URI=$(aws ecr describe-repositories \
  --repository-names $APP_NAME \
  --region $AWS_REGION \
  --query 'repositories[0].repositoryUri' \
  --output text)
echo "ECR URI: $ECR_URI"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

# Build image
docker build -t $APP_NAME .

# Tag and push
docker tag $APP_NAME:latest $ECR_URI:latest
docker tag $APP_NAME:latest $ECR_URI:$DEPLOYMENT_ID
docker push $ECR_URI:latest
docker push $ECR_URI:$DEPLOYMENT_ID

# 9. Create ECS Cluster
echo "Step 9: Creating ECS Cluster..."
aws ecs create-cluster \
  --cluster-name $APP_NAME \
  --region $AWS_REGION

# 10. Create IAM Execution Role
echo "Step 10: Creating ECS Execution Role..."
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

EXECUTION_ROLE_ARN=$(aws iam create-role \
  --role-name "${APP_NAME}-execution-role" \
  --assume-role-policy-document file://trust-policy.json \
  --region $AWS_REGION \
  --query 'Role.Arn' \
  --output text) || \
EXECUTION_ROLE_ARN=$(aws iam get-role \
  --role-name "${APP_NAME}-execution-role" \
  --query 'Role.Arn' \
  --output text)

echo "Execution Role ARN: $EXECUTION_ROLE_ARN"

# Attach policy to role
aws iam attach-role-policy \
  --role-name "${APP_NAME}-execution-role" \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy \
  --region $AWS_REGION

# Wait for role to be available
echo "Waiting for IAM role to propagate..."
sleep 10

# 11. Create Task Definition
echo "Step 11: Creating ECS Task Definition..."
cat > task-definition.json << EOF
{
  "family": "${APP_NAME}-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "$EXECUTION_ROLE_ARN",
  "containerDefinitions": [
    {
      "name": "${APP_NAME}-container",
      "image": "$ECR_URI:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/${APP_NAME}",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

# Create CloudWatch Log Group
aws logs create-log-group \
  --log-group-name "/ecs/${APP_NAME}" \
  --region $AWS_REGION || echo "Log group may already exist"

# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json \
  --region $AWS_REGION

# 12. Create ECS Service
echo "Step 12: Creating ECS Service..."
aws ecs create-service \
  --cluster $APP_NAME \
  --service-name "${APP_NAME}-service" \
  --task-definition "${APP_NAME}-task" \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$PUBLIC_SUBNET_ID],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
  --region $AWS_REGION

echo ""
echo "=== Deployment Summary ==="
echo "App Name: $APP_NAME"
echo "Deployment ID: $DEPLOYMENT_ID"
echo "VPC ID: $VPC_ID"
echo "Public Subnet: $PUBLIC_SUBNET_ID"
echo "Private Subnet: $PRIVATE_SUBNET_ID"
echo "Security Group: $SECURITY_GROUP_ID"
echo "ECR URI: $ECR_URI"
echo "Execution Role: $EXECUTION_ROLE_ARN"
echo ""
echo "Checking service status..."
aws ecs describe-services \
  --cluster $APP_NAME \
  --services "${APP_NAME}-service" \
  --region $AWS_REGION

echo ""
echo "=== Deployment Complete! ==="
echo "Check ECS console for service status and public IP"

# Clean up temporary files
rm -f trust-policy.json task-definition.json

echo "Deployment completed successfully!"