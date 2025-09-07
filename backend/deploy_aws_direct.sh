#!/bin/bash
# Direct AWS CLI Deployment Script for AltMX Production
# Simple and straightforward approach as requested by user

set -e  # Exit on any error

# Configuration
STACK_NAME="altmx-production"
REGION="ap-northeast-1"
TEMPLATE_FILE="generated_template.json"

echo "Starting AltMX Production Deployment using direct AWS CLI..."
echo "Stack Name: $STACK_NAME"
echo "Region: $REGION"

# Check if template exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template file $TEMPLATE_FILE not found"
    exit 1
fi

# Validate template first
echo "Validating CloudFormation template..."
aws cloudformation validate-template \
    --template-body file://$TEMPLATE_FILE \
    --region $REGION

if [ $? -ne 0 ]; then
    echo "Template validation failed"
    exit 1
fi

echo "Template validation successful"

# Generate unique deployment ID for resource names
DEPLOYMENT_ID=$(date +%Y%m%d%H%M%S)
echo "Deployment ID: $DEPLOYMENT_ID"

# Deploy the stack
echo "Creating CloudFormation stack..."
aws cloudformation create-stack \
    --stack-name $STACK_NAME \
    --template-body file://$TEMPLATE_FILE \
    --parameters \
        ParameterKey=ContainerImage,ParameterValue="altmx-production:latest" \
        ParameterKey=DesiredCount,ParameterValue="1" \
        ParameterKey=ContainerPort,ParameterValue="3000" \
        ParameterKey=DatabaseUsername,ParameterValue="altmxadmin" \
        ParameterKey=DatabasePassword,ParameterValue="TempPass123" \
    --tags \
        Key=Environment,Value=production \
        Key=Project,Value=AltMX \
        Key=DeploymentId,Value=$DEPLOYMENT_ID \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION

if [ $? -ne 0 ]; then
    echo "Stack creation failed"
    exit 1
fi

echo "Stack creation initiated successfully"

# Monitor stack creation
echo "Monitoring stack creation progress..."
aws cloudformation wait stack-create-complete \
    --stack-name $STACK_NAME \
    --region $REGION

if [ $? -eq 0 ]; then
    echo "Stack creation completed successfully!"
    
    # Get stack outputs
    echo "Retrieving stack outputs..."
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs'
    
    # Get Application URL if available
    APP_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
        --output text)
    
    if [ ! -z "$APP_URL" ]; then
        echo "Application URL: $APP_URL"
    fi
    
    echo "Deployment completed successfully!"
else
    echo "Stack creation failed or timed out"
    
    # Get stack events to show what went wrong
    echo "Stack events:"
    aws cloudformation describe-stack-events \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'StackEvents[0:10].[Timestamp,ResourceStatus,ResourceStatusReason]' \
        --output table
    
    exit 1
fi