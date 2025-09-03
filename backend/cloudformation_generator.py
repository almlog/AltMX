"""
AWS CloudFormation テンプレート生成サービス - Task 4.6実装
インフラコードを自動生成し、ECS Fargate環境を構築
"""
import json
import yaml
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)

class CloudFormationGenerator:
    """CloudFormationテンプレート生成サービス"""
    
    def __init__(self):
        """初期化"""
        self.template_version = "2010-09-09"
        self.stack_prefix = "AltMX"
        
        # デフォルト設定
        self.default_cpu = 256
        self.default_memory = 512
        self.default_port = 3000
        self.default_min_capacity = 1
        self.default_max_capacity = 10
        self.default_target_cpu = 70.0
        
        # ログ保持期間（日）
        self.log_retention_days = 30
    
    def generate_template(self, app_config: Dict[str, Any], aws_config: Dict[str, Any]) -> Dict[str, Any]:
        """テンプレート生成のエントリーポイント"""
        return self.generate_complete_stack(app_config, aws_config)
    
    def generate_ecs_template(self, app_config: Dict[str, Any], aws_config: Dict[str, Any]) -> Dict[str, Any]:
        """基本的なECSテンプレート生成"""
        template = {
            "AWSTemplateFormatVersion": self.template_version,
            "Description": f"AltMX Generated CloudFormation Template for {app_config.get('app_name', 'app')}",
            "Resources": {}
        }
        
        # ECSクラスター
        template["Resources"]["ECSCluster"] = {
            "Type": "AWS::ECS::Cluster",
            "Properties": {
                "ClusterName": f"{self.stack_prefix}-{app_config['app_name']}-cluster",
                "CapacityProviders": ["FARGATE", "FARGATE_SPOT"],
                "DefaultCapacityProviderStrategy": [
                    {
                        "CapacityProvider": "FARGATE",
                        "Weight": 1,
                        "Base": 1
                    }
                ],
                "ClusterSettings": [
                    {
                        "Name": "containerInsights",
                        "Value": "enabled"
                    }
                ]
            }
        }
        
        # タスク定義
        template["Resources"]["ECSTaskDefinition"] = self.generate_task_definition(app_config)
        
        # ALB関連リソース
        alb_resources = self.generate_alb_configuration(app_config, aws_config)
        template["Resources"].update(alb_resources)
        
        # ECSサービス
        template["Resources"]["ECSService"] = {
            "Type": "AWS::ECS::Service",
            "DependsOn": ["HTTPListener", "HTTPSListener"],
            "Properties": {
                "ServiceName": f"{self.stack_prefix}-{app_config['app_name']}-service",
                "Cluster": {"Ref": "ECSCluster"},
                "TaskDefinition": {"Ref": "ECSTaskDefinition"},
                "DesiredCount": 2,
                "LaunchType": "FARGATE",
                "NetworkConfiguration": {
                    "AwsvpcConfiguration": {
                        "AssignPublicIp": "ENABLED",
                        "SecurityGroups": [{"Ref": "ECSSecurityGroup"}],
                        "Subnets": aws_config.get("subnet_ids", [])
                    }
                },
                "LoadBalancers": [
                    {
                        "ContainerName": app_config["app_name"],
                        "ContainerPort": app_config.get("port", self.default_port),
                        "TargetGroupArn": {"Ref": "TargetGroup"}
                    }
                ],
                "HealthCheckGracePeriodSeconds": 60
            }
        }
        
        return template
    
    def generate_task_definition(self, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """Fargateタスク定義の生成"""
        cpu = str(app_config.get("cpu", self.default_cpu))
        memory = str(app_config.get("memory", self.default_memory))
        
        task_definition = {
            "Type": "AWS::ECS::TaskDefinition",
            "Properties": {
                "Family": f"{self.stack_prefix}-{app_config['app_name']}",
                "RequiresCompatibilities": ["FARGATE"],
                "NetworkMode": "awsvpc",
                "Cpu": cpu,
                "Memory": memory,
                "ExecutionRoleArn": {"Ref": "TaskExecutionRole"},
                "TaskRoleArn": {"Ref": "TaskRole"},
                "ContainerDefinitions": [
                    {
                        "Name": app_config["app_name"],
                        "Image": {"Ref": "ContainerImage"},
                        "Memory": app_config.get("memory", self.default_memory),
                        "PortMappings": [
                            {
                                "ContainerPort": app_config.get("port", self.default_port),
                                "Protocol": "tcp"
                            }
                        ],
                        "Environment": self.generate_environment_variables(app_config),
                        "Secrets": self.generate_secrets_references(app_config),
                        "LogConfiguration": {
                            "LogDriver": "awslogs",
                            "Options": {
                                "awslogs-group": {"Ref": "LogGroup"},
                                "awslogs-region": {"Ref": "AWS::Region"},
                                "awslogs-stream-prefix": "ecs"
                            }
                        },
                        "Essential": True,
                        "HealthCheck": {
                            "Command": ["CMD-SHELL", f"curl -f http://localhost:{app_config.get('port', self.default_port)}/health || exit 1"],
                            "Interval": 30,
                            "Timeout": 5,
                            "Retries": 3,
                            "StartPeriod": 60
                        }
                    }
                ]
            }
        }
        
        return task_definition
    
    def generate_alb_configuration(self, app_config: Dict[str, Any], aws_config: Dict[str, Any]) -> Dict[str, Any]:
        """Application Load Balancer設定の生成"""
        alb_config = {}
        
        # ALB本体
        alb_config["ALB"] = {
            "Type": "AWS::ElasticLoadBalancingV2::LoadBalancer",
            "Properties": {
                "Name": f"{self.stack_prefix}-{app_config['app_name']}-alb",
                "Type": "application",
                "Scheme": "internet-facing",
                "SecurityGroups": [{"Ref": "ALBSecurityGroup"}],
                "Subnets": aws_config.get("subnet_ids", []),
                "Tags": [
                    {"Key": "Name", "Value": f"{self.stack_prefix}-{app_config['app_name']}-alb"},
                    {"Key": "Environment", "Value": app_config.get("environment", "production")},
                    {"Key": "ManagedBy", "Value": "AltMX"}
                ]
            }
        }
        
        # ターゲットグループ
        alb_config["TargetGroup"] = {
            "Type": "AWS::ElasticLoadBalancingV2::TargetGroup",
            "Properties": {
                "Name": f"{self.stack_prefix}-{app_config['app_name']}-tg",
                "Port": app_config.get("port", self.default_port),
                "Protocol": "HTTP",
                "VpcId": aws_config.get("vpc_id"),
                "TargetType": "ip",
                "HealthCheckEnabled": True,
                "HealthCheckIntervalSeconds": 30,
                "HealthCheckPath": "/health",
                "HealthCheckProtocol": "HTTP",
                "HealthCheckTimeoutSeconds": 5,
                "HealthyThresholdCount": 2,
                "UnhealthyThresholdCount": 3,
                "Matcher": {
                    "HttpCode": "200,301,302"
                },
                "TargetGroupAttributes": [
                    {"Key": "deregistration_delay.timeout_seconds", "Value": "30"},
                    {"Key": "stickiness.enabled", "Value": "true"},
                    {"Key": "stickiness.type", "Value": "lb_cookie"},
                    {"Key": "stickiness.lb_cookie.duration_seconds", "Value": "86400"}
                ]
            }
        }
        
        # HTTPリスナー（リダイレクト）
        alb_config["HTTPListener"] = {
            "Type": "AWS::ElasticLoadBalancingV2::Listener",
            "Properties": {
                "LoadBalancerArn": {"Ref": "ALB"},
                "Port": 80,
                "Protocol": "HTTP",
                "DefaultActions": [
                    {
                        "Type": "redirect",
                        "RedirectConfig": {
                            "Port": "443",
                            "Protocol": "HTTPS",
                            "StatusCode": "HTTP_301"
                        }
                    }
                ]
            }
        }
        
        # HTTPSリスナー
        alb_config["HTTPSListener"] = {
            "Type": "AWS::ElasticLoadBalancingV2::Listener",
            "Properties": {
                "LoadBalancerArn": {"Ref": "ALB"},
                "Port": 443,
                "Protocol": "HTTPS",
                "Certificates": [
                    {
                        "CertificateArn": aws_config.get("certificate_arn", "")
                    }
                ],
                "DefaultActions": [
                    {
                        "Type": "forward",
                        "TargetGroupArn": {"Ref": "TargetGroup"}
                    }
                ],
                "SslPolicy": "ELBSecurityPolicy-TLS-1-2-2017-01"
            }
        }
        
        return alb_config
    
    def generate_security_groups(self, aws_config: Dict[str, Any]) -> Dict[str, Any]:
        """セキュリティグループ生成"""
        security_groups = {}
        
        # ALB用セキュリティグループ
        security_groups["ALBSecurityGroup"] = {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Security group for ALB",
                "VpcId": aws_config.get("vpc_id"),
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 80,
                        "ToPort": 80,
                        "CidrIp": "0.0.0.0/0"
                    },
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 443,
                        "ToPort": 443,
                        "CidrIp": "0.0.0.0/0"
                    }
                ],
                "Tags": [
                    {"Key": "Name", "Value": f"{self.stack_prefix}-ALB-SG"}
                ]
            }
        }
        
        # ECS用セキュリティグループ
        security_groups["ECSSecurityGroup"] = {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Security group for ECS tasks",
                "VpcId": aws_config.get("vpc_id"),
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": {"Ref": "ContainerPort"},
                        "ToPort": {"Ref": "ContainerPort"},
                        "SourceSecurityGroupId": {"Ref": "ALBSecurityGroup"}
                    }
                ],
                "Tags": [
                    {"Key": "Name", "Value": f"{self.stack_prefix}-ECS-SG"}
                ]
            }
        }
        
        return security_groups
    
    def generate_auto_scaling(self, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """オートスケーリング設定生成"""
        scaling_config = {}
        
        # スケーリングターゲット
        scaling_config["ScalingTarget"] = {
            "Type": "AWS::ApplicationAutoScaling::ScalableTarget",
            "Properties": {
                "ServiceNamespace": "ecs",
                "ScalableDimension": "ecs:service:DesiredCount",
                "ResourceId": {
                    "Fn::Sub": "service/${ECSCluster}/${ECSService.Name}"
                },
                "MinCapacity": app_config.get("min_capacity", self.default_min_capacity),
                "MaxCapacity": app_config.get("max_capacity", self.default_max_capacity),
                "RoleARN": {"Fn::Sub": "arn:aws:iam::${AWS::AccountId}:role/aws-service-role/ecs.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_ECSService"}
            }
        }
        
        # CPUベースのスケーリングポリシー
        scaling_config["CPUScalingPolicy"] = {
            "Type": "AWS::ApplicationAutoScaling::ScalingPolicy",
            "Properties": {
                "PolicyName": f"{self.stack_prefix}-cpu-scaling-policy",
                "PolicyType": "TargetTrackingScaling",
                "ScalingTargetId": {"Ref": "ScalingTarget"},
                "TargetTrackingScalingPolicyConfiguration": {
                    "TargetValue": app_config.get("target_cpu", self.default_target_cpu),
                    "PredefinedMetricSpecification": {
                        "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
                    },
                    "ScaleInCooldown": 300,
                    "ScaleOutCooldown": 60
                }
            }
        }
        
        # メモリベースのスケーリングポリシー（オプション）
        scaling_config["MemoryScalingPolicy"] = {
            "Type": "AWS::ApplicationAutoScaling::ScalingPolicy",
            "Properties": {
                "PolicyName": f"{self.stack_prefix}-memory-scaling-policy",
                "PolicyType": "TargetTrackingScaling",
                "ScalingTargetId": {"Ref": "ScalingTarget"},
                "TargetTrackingScalingPolicyConfiguration": {
                    "TargetValue": 80.0,
                    "PredefinedMetricSpecification": {
                        "PredefinedMetricType": "ECSServiceAverageMemoryUtilization"
                    },
                    "ScaleInCooldown": 300,
                    "ScaleOutCooldown": 60
                }
            }
        }
        
        return scaling_config
    
    def generate_environment_variables(self, app_config: Dict[str, Any]) -> List[Dict[str, str]]:
        """環境変数設定の生成"""
        env_vars = [
            {"Name": "NODE_ENV", "Value": app_config.get("environment", "production")},
            {"Name": "PORT", "Value": str(app_config.get("port", self.default_port))},
            {"Name": "APP_NAME", "Value": app_config.get("app_name", "altmx-app")},
            {"Name": "RUNTIME", "Value": app_config.get("runtime", "nodejs18.x")},
            {"Name": "LOG_LEVEL", "Value": "info"},
            {"Name": "AWS_REGION", "Value": {"Ref": "AWS::Region"}},
            {"Name": "CLUSTER_NAME", "Value": {"Ref": "ECSCluster"}}
        ]
        
        # データベース設定があれば追加
        if "database" in app_config.get("features", []):
            env_vars.extend([
                {"Name": "DATABASE_URL", "Value": {"Ref": "DatabaseURL"}},
                {"Name": "DB_HOST", "Value": {"Fn::GetAtt": ["RDSInstance", "Endpoint.Address"]}},
                {"Name": "DB_PORT", "Value": "5432"},
                {"Name": "DB_NAME", "Value": app_config.get("app_name", "app").replace("-", "_")}
            ])
        
        # Redis/Cache設定
        if "cache" in app_config.get("features", []):
            env_vars.extend([
                {"Name": "REDIS_HOST", "Value": {"Fn::GetAtt": ["ElastiCacheCluster", "RedisEndpoint.Address"]}},
                {"Name": "REDIS_PORT", "Value": "6379"}
            ])
        
        return env_vars
    
    def generate_secrets_references(self, app_config: Dict[str, Any]) -> List[Dict[str, str]]:
        """Secrets Manager参照の生成"""
        secrets = []
        
        # APIキー等の機密情報
        secret_keys = ["API_KEY", "DATABASE_PASSWORD", "JWT_SECRET", "GITHUB_TOKEN"]
        
        for key in secret_keys:
            secrets.append({
                "Name": key,
                "ValueFrom": {"Fn::Sub": f"arn:aws:secretsmanager:${{AWS::Region}}:${{AWS::AccountId}}:secret:{app_config['app_name']}/{key}"}
            })
        
        return secrets
    
    def generate_cloudwatch_logs(self, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """CloudWatchログ設定生成"""
        logs_config = {}
        
        logs_config["LogGroup"] = {
            "Type": "AWS::Logs::LogGroup",
            "Properties": {
                "LogGroupName": f"/ecs/{app_config['app_name']}",
                "RetentionInDays": self.log_retention_days
            }
        }
        
        return logs_config
    
    def generate_route53_records(self, aws_config: Dict[str, Any]) -> Dict[str, Any]:
        """Route53 DNS設定生成"""
        dns_records = {}
        
        if aws_config.get("domain_name") and aws_config.get("route53_zone_id"):
            dns_records["DNSRecord"] = {
                "Type": "AWS::Route53::RecordSet",
                "Properties": {
                    "HostedZoneId": aws_config["route53_zone_id"],
                    "Name": aws_config["domain_name"],
                    "Type": "A",
                    "AliasTarget": {
                        "DNSName": {"Fn::GetAtt": ["ALB", "DNSName"]},
                        "HostedZoneId": {"Fn::GetAtt": ["ALB", "CanonicalHostedZoneID"]},
                        "EvaluateTargetHealth": True
                    }
                }
            }
        
        return dns_records
    
    def generate_iam_roles(self, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """IAMロール生成"""
        iam_roles = {}
        
        # タスク実行ロール
        iam_roles["TaskExecutionRole"] = {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "RoleName": f"{self.stack_prefix}-{app_config['app_name']}-execution-role",
                "AssumeRolePolicyDocument": {
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
                },
                "ManagedPolicyArns": [
                    "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
                ],
                "Policies": [
                    {
                        "PolicyName": "SecretAccess",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "secretsmanager:GetSecretValue"
                                    ],
                                    "Resource": {"Fn::Sub": f"arn:aws:secretsmanager:${{AWS::Region}}:${{AWS::AccountId}}:secret:{app_config['app_name']}/*"}
                                }
                            ]
                        }
                    }
                ]
            }
        }
        
        # タスクロール（アプリケーション用）
        iam_roles["TaskRole"] = {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "RoleName": f"{self.stack_prefix}-{app_config['app_name']}-task-role",
                "AssumeRolePolicyDocument": {
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
                },
                "Policies": [
                    {
                        "PolicyName": "ApplicationAccess",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "s3:GetObject",
                                        "s3:PutObject",
                                        "s3:DeleteObject"
                                    ],
                                    "Resource": {"Fn::Sub": f"arn:aws:s3:::altmx-{app_config['app_name']}-*/*"}
                                },
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "dynamodb:Query",
                                        "dynamodb:Scan",
                                        "dynamodb:GetItem",
                                        "dynamodb:PutItem",
                                        "dynamodb:UpdateItem",
                                        "dynamodb:DeleteItem"
                                    ],
                                    "Resource": {"Fn::Sub": f"arn:aws:dynamodb:${{AWS::Region}}:${{AWS::AccountId}}:table/{app_config['app_name']}-*"}
                                }
                            ]
                        }
                    }
                ]
            }
        }
        
        return iam_roles
    
    def generate_database_resources(self, app_config: Dict[str, Any], aws_config: Dict[str, Any]) -> Dict[str, Any]:
        """データベース関連リソースの生成"""
        db_resources = {}
        
        # RDSサブネットグループ
        db_resources["DatabaseSubnetGroup"] = {
            "Type": "AWS::RDS::DBSubnetGroup",
            "Properties": {
                "DBSubnetGroupDescription": f"Subnet group for {app_config['app_name']} database",
                "SubnetIds": aws_config.get("subnet_ids", []),
                "Tags": [
                    {"Key": "Name", "Value": f"{self.stack_prefix}-{app_config['app_name']}-db-subnet-group"}
                ]
            }
        }
        
        # RDSセキュリティグループ  
        db_resources["DatabaseSecurityGroup"] = {
            "Type": "AWS::EC2::SecurityGroup",
            "Properties": {
                "GroupDescription": "Security group for database",
                "VpcId": aws_config.get("vpc_id"),
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 5432,
                        "ToPort": 5432,
                        "SourceSecurityGroupId": {"Ref": "ECSSecurityGroup"}
                    }
                ],
                "Tags": [
                    {"Key": "Name", "Value": f"{self.stack_prefix}-{app_config['app_name']}-db-sg"}
                ]
            }
        }
        
        # RDSインスタンス
        db_resources["RDSInstance"] = {
            "Type": "AWS::RDS::DBInstance",
            "Properties": {
                "DBInstanceIdentifier": f"{app_config['app_name']}-database",
                "DBInstanceClass": "db.t3.micro",
                "Engine": "postgres",
                "EngineVersion": "13.7",
                "AllocatedStorage": 20,
                "StorageType": "gp2",
                "StorageEncrypted": True,
                "DBName": app_config.get("app_name", "app").replace("-", "_"),
                "MasterUsername": {"Ref": "DatabaseUsername"},
                "MasterUserPassword": {"Ref": "DatabasePassword"},
                "VPCSecurityGroups": [{"Ref": "DatabaseSecurityGroup"}],
                "DBSubnetGroupName": {"Ref": "DatabaseSubnetGroup"},
                "BackupRetentionPeriod": 7,
                "MultiAZ": False,
                "PubliclyAccessible": False,
                "DeletionProtection": False,
                "Tags": [
                    {"Key": "Name", "Value": f"{self.stack_prefix}-{app_config['app_name']}-db"}
                ]
            }
        }
        
        return db_resources
    
    def generate_complete_stack(self, app_config: Dict[str, Any], aws_config: Dict[str, Any]) -> Dict[str, Any]:
        """完全なCloudFormationスタック生成"""
        stack = {
            "AWSTemplateFormatVersion": self.template_version,
            "Description": f"Complete infrastructure stack for {app_config['app_name']} - Generated by AltMX",
            "Metadata": {
                "AWS::CloudFormation::Interface": {
                    "ParameterGroups": [
                        {
                            "Label": {"default": "Network Configuration"},
                            "Parameters": ["VPCId", "SubnetIds"]
                        },
                        {
                            "Label": {"default": "Application Configuration"},
                            "Parameters": ["ContainerImage", "ContainerPort", "DesiredCount"]
                        }
                    ]
                }
            },
            "Parameters": {
                "VPCId": {
                    "Type": "AWS::EC2::VPC::Id",
                    "Description": "VPC ID",
                    "Default": aws_config.get("vpc_id", "")
                },
                "SubnetIds": {
                    "Type": "List<AWS::EC2::Subnet::Id>",
                    "Description": "Subnet IDs for the application",
                    "Default": ",".join(aws_config.get("subnet_ids", []))
                },
                "ContainerImage": {
                    "Type": "String",
                    "Description": "Docker image for the application",
                    "Default": f"{app_config['app_name']}:latest"
                },
                "ContainerPort": {
                    "Type": "Number",
                    "Description": "Port number for the container",
                    "Default": app_config.get("port", self.default_port)
                },
                "DesiredCount": {
                    "Type": "Number",
                    "Description": "Desired number of tasks",
                    "Default": 2
                },
                "DatabaseUsername": {
                    "Type": "String",
                    "Description": "Database master username",
                    "Default": "dbadmin",
                    "NoEcho": True
                },
                "DatabasePassword": {
                    "Type": "String", 
                    "Description": "Database master password",
                    "NoEcho": True,
                    "MinLength": 8,
                    "MaxLength": 64,
                    "AllowedPattern": "[a-zA-Z0-9]*",
                    "Default": "TempPassword123"
                }
            },
            "Resources": {},
            "Outputs": {}
        }
        
        # リソース追加
        # IAMロール
        stack["Resources"].update(self.generate_iam_roles(app_config))
        
        # セキュリティグループ
        stack["Resources"].update(self.generate_security_groups(aws_config))
        
        # CloudWatchログ
        stack["Resources"].update(self.generate_cloudwatch_logs(app_config))
        
        # ECS関連
        ecs_template = self.generate_ecs_template(app_config, aws_config)
        stack["Resources"].update(ecs_template["Resources"])
        
        # オートスケーリング
        stack["Resources"].update(self.generate_auto_scaling(app_config))
        
        # Route53 - Skip for live demos (DNS propagation risk)
        # if aws_config.get("domain_name"):
        # Route53 DNS は ライブデモでは不要（DNS伝搬時間がかかるため）
        
        # データベース（オプション）
        if "database" in app_config.get("features", []):
            stack["Resources"].update(self.generate_database_resources(app_config, aws_config))
        
        # 出力値
        stack["Outputs"] = {
            "ApplicationURL": {
                "Description": "URL of the application - Ready for immediate use",
                "Value": {"Fn::Sub": "https://${ALB.DNSName}"},
                "Export": {
                    "Name": {"Fn::Sub": "${AWS::StackName}-ApplicationURL"}
                }
            },
            "ALBEndpoint": {
                "Description": "ALB DNS Name",
                "Value": {"Fn::GetAtt": ["ALB", "DNSName"]},
                "Export": {
                    "Name": {"Fn::Sub": "${AWS::StackName}-ALBEndpoint"}
                }
            },
            "ECSClusterName": {
                "Description": "ECS Cluster Name",
                "Value": {"Ref": "ECSCluster"},
                "Export": {
                    "Name": {"Fn::Sub": "${AWS::StackName}-ClusterName"}
                }
            },
            "ECSServiceName": {
                "Description": "ECS Service Name",
                "Value": {"Fn::GetAtt": ["ECSService", "Name"]},
                "Export": {
                    "Name": {"Fn::Sub": "${AWS::StackName}-ServiceName"}
                }
            }
        }
        
        # 条件（Conditions） - Simplified for live demos
        stack["Conditions"] = {
            "HasCertificate": {"Fn::Not": [{"Fn::Equals": [aws_config.get("certificate_arn", ""), ""]}]}
        }
        
        return stack
    
    def export_to_yaml(self, template: Dict[str, Any]) -> str:
        """テンプレートをYAML形式でエクスポート"""
        return yaml.dump(template, default_flow_style=False, sort_keys=False)
    
    def export_to_json(self, template: Dict[str, Any]) -> str:
        """テンプレートをJSON形式でエクスポート"""
        return json.dumps(template, indent=2)
    
    def validate_template(self, template: Dict[str, Any]) -> bool:
        """テンプレートの基本的な検証"""
        required_sections = ["AWSTemplateFormatVersion", "Resources"]
        for section in required_sections:
            if section not in template:
                logger.error(f"Missing required section: {section}")
                return False
        
        if not template["Resources"]:
            logger.error("Template has no resources defined")
            return False
        
        return True