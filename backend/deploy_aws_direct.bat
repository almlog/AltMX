@echo off
REM Direct AWS CLI Deployment Script for AltMX Production (Windows)
REM Simple and straightforward approach as requested by user

setlocal

REM Configuration
set STACK_NAME=altmx-production
set REGION=ap-northeast-1
set TEMPLATE_FILE=generated_template.json

echo Starting AltMX Production Deployment using direct AWS CLI...
echo Stack Name: %STACK_NAME%
echo Region: %REGION%

REM Check if template exists
if not exist "%TEMPLATE_FILE%" (
    echo Error: Template file %TEMPLATE_FILE% not found
    exit /b 1
)

REM Validate template first
echo Validating CloudFormation template...
aws cloudformation validate-template --template-body file://%TEMPLATE_FILE% --region %REGION%
if errorlevel 1 (
    echo Template validation failed
    exit /b 1
)
echo Template validation successful

REM Generate unique deployment ID for resource names
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set DEPLOYMENT_ID=%YYYY%%MM%%DD%%HH%%Min%%Sec%
echo Deployment ID: %DEPLOYMENT_ID%

REM Deploy the stack
echo Creating CloudFormation stack...
aws cloudformation create-stack ^
    --stack-name %STACK_NAME% ^
    --template-body file://%TEMPLATE_FILE% ^
    --parameters ^
        ParameterKey=ContainerImage,ParameterValue="altmx-production:latest" ^
        ParameterKey=DesiredCount,ParameterValue="1" ^
        ParameterKey=ContainerPort,ParameterValue="3000" ^
        ParameterKey=DatabaseUsername,ParameterValue="altmxadmin" ^
        ParameterKey=DatabasePassword,ParameterValue="TempPass123" ^
    --tags ^
        Key=Environment,Value=production ^
        Key=Project,Value=AltMX ^
        Key=DeploymentId,Value=%DEPLOYMENT_ID% ^
    --capabilities CAPABILITY_NAMED_IAM ^
    --region %REGION%

if errorlevel 1 (
    echo Stack creation failed
    exit /b 1
)

echo Stack creation initiated successfully

REM Monitor stack creation
echo Monitoring stack creation progress...
aws cloudformation wait stack-create-complete ^
    --stack-name %STACK_NAME% ^
    --region %REGION%

if not errorlevel 1 (
    echo Stack creation completed successfully!
    
    REM Get stack outputs
    echo Retrieving stack outputs...
    aws cloudformation describe-stacks ^
        --stack-name %STACK_NAME% ^
        --region %REGION% ^
        --query "Stacks[0].Outputs"
    
    REM Get Application URL if available
    for /f "tokens=*" %%i in ('aws cloudformation describe-stacks --stack-name %STACK_NAME% --region %REGION% --query "Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue" --output text 2^>nul') do set APP_URL=%%i
    
    if not "%APP_URL%"=="" (
        echo Application URL: %APP_URL%
    )
    
    echo Deployment completed successfully!
) else (
    echo Stack creation failed or timed out
    
    REM Get stack events to show what went wrong
    echo Stack events:
    aws cloudformation describe-stack-events ^
        --stack-name %STACK_NAME% ^
        --region %REGION% ^
        --query "StackEvents[0:10].[Timestamp,ResourceStatus,ResourceStatusReason]" ^
        --output table
    
    exit /b 1
)

endlocal