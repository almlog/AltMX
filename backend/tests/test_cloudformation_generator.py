"""
Task 4.6: AWS CloudFormation テンプレート生成のTDDテスト
インフラコード自動生成機能のテスト
"""
import pytest
import json
import yaml
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import tempfile
import os

class TestCloudFormationGenerator:
    """CloudFormationテンプレート生成のテスト"""
    
    @pytest.fixture
    def app_config(self):
        """アプリケーション設定"""
        return {
            "app_name": "altmx-demo-app",
            "app_type": "react",
            "runtime": "nodejs18.x",
            "port": 3000,
            "memory": 512,
            "cpu": 256,
            "environment": "production",
            "features": ["database", "cache", "cdn"]
        }
    
    @pytest.fixture
    def aws_config(self):
        """AWS設定"""
        return {
            "region": "ap-northeast-1",
            "vpc_id": "vpc-12345678",
            "subnet_ids": ["subnet-1234", "subnet-5678"],
            "certificate_arn": "arn:aws:acm:ap-northeast-1:123456789012:certificate/abc",
            "domain_name": "demo.altmx.com",
            "route53_zone_id": "Z123456789"
        }
    
    def test_generator_initialization(self):
        """CloudFormation生成サービスの初期化"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        assert generator is not None
        assert hasattr(generator, 'generate_template')
    
    def test_generate_basic_ecs_template(self, app_config, aws_config):
        """基本的なECSテンプレート生成"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        template = generator.generate_ecs_template(app_config, aws_config)
        
        # 基本構造の確認
        assert "AWSTemplateFormatVersion" in template
        assert template["AWSTemplateFormatVersion"] == "2010-09-09"
        assert "Description" in template
        assert "Resources" in template
        
        # ECS関連リソースの確認
        resources = template["Resources"]
        assert "ECSCluster" in resources
        assert "ECSTaskDefinition" in resources
        assert "ECSService" in resources
        assert "ALB" in resources
        assert "TargetGroup" in resources
    
    def test_generate_fargate_task_definition(self, app_config):
        """Fargateタスク定義の生成"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        task_def = generator.generate_task_definition(app_config)
        
        assert task_def["Type"] == "AWS::ECS::TaskDefinition"
        properties = task_def["Properties"]
        
        # Fargate設定
        assert properties["RequiresCompatibilities"] == ["FARGATE"]
        assert properties["NetworkMode"] == "awsvpc"
        assert properties["Cpu"] == str(app_config["cpu"])
        assert properties["Memory"] == str(app_config["memory"])
        
        # コンテナ定義
        container_defs = properties["ContainerDefinitions"]
        assert len(container_defs) > 0
        container = container_defs[0]
        assert container["Name"] == app_config["app_name"]
        assert container["Memory"] == app_config["memory"]
        assert container["PortMappings"][0]["ContainerPort"] == app_config["port"]
    
    def test_generate_alb_configuration(self, app_config, aws_config):
        """Application Load Balancer設定の生成"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        alb_config = generator.generate_alb_configuration(app_config, aws_config)
        
        # ALB本体
        assert "ALB" in alb_config
        alb = alb_config["ALB"]
        assert alb["Type"] == "AWS::ElasticLoadBalancingV2::LoadBalancer"
        assert alb["Properties"]["Type"] == "application"
        assert alb["Properties"]["Scheme"] == "internet-facing"
        
        # リスナー（HTTPS）
        assert "HTTPSListener" in alb_config
        listener = alb_config["HTTPSListener"]
        assert listener["Properties"]["Port"] == 443
        assert listener["Properties"]["Protocol"] == "HTTPS"
        assert aws_config["certificate_arn"] in str(listener["Properties"]["Certificates"])
    
    def test_generate_security_groups(self, aws_config):
        """セキュリティグループ生成"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        security_groups = generator.generate_security_groups(aws_config)
        
        # ALB用セキュリティグループ
        assert "ALBSecurityGroup" in security_groups
        alb_sg = security_groups["ALBSecurityGroup"]
        ingress_rules = alb_sg["Properties"]["SecurityGroupIngress"]
        
        # HTTPS (443) と HTTP (80) を許可
        ports = [rule["FromPort"] for rule in ingress_rules]
        assert 443 in ports
        assert 80 in ports
        
        # ECS用セキュリティグループ
        assert "ECSSecurityGroup" in security_groups
        ecs_sg = security_groups["ECSSecurityGroup"]
        assert "SourceSecurityGroupId" in str(ecs_sg["Properties"]["SecurityGroupIngress"])
    
    def test_generate_auto_scaling_configuration(self, app_config):
        """オートスケーリング設定生成"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        scaling_config = generator.generate_auto_scaling(app_config)
        
        # スケーリングターゲット
        assert "ScalingTarget" in scaling_config
        target = scaling_config["ScalingTarget"]
        assert target["Type"] == "AWS::ApplicationAutoScaling::ScalableTarget"
        assert target["Properties"]["MinCapacity"] == 1
        assert target["Properties"]["MaxCapacity"] == 10
        
        # CPU使用率によるスケーリングポリシー
        assert "CPUScalingPolicy" in scaling_config
        policy = scaling_config["CPUScalingPolicy"]
        assert policy["Properties"]["TargetTrackingScalingPolicyConfiguration"]["TargetValue"] == 70.0
        assert policy["Properties"]["TargetTrackingScalingPolicyConfiguration"]["PredefinedMetricSpecification"]["PredefinedMetricType"] == "ECSServiceAverageCPUUtilization"
    
    def test_generate_environment_variables(self, app_config):
        """環境変数設定の生成"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        env_vars = generator.generate_environment_variables(app_config)
        
        # 基本環境変数
        assert any(var["Name"] == "NODE_ENV" for var in env_vars)
        assert any(var["Name"] == "PORT" for var in env_vars)
        assert any(var["Name"] == "APP_NAME" for var in env_vars)
        
        # CloudFormation参照の環境変数
        cf_ref_vars = [var for var in env_vars if isinstance(var.get("Value"), dict)]
        assert len(cf_ref_vars) > 0  # AWS::Region等のCloudFormation参照があることを確認
    
    def test_generate_cloudwatch_logs(self, app_config):
        """CloudWatchログ設定生成"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        logs_config = generator.generate_cloudwatch_logs(app_config)
        
        assert "LogGroup" in logs_config
        log_group = logs_config["LogGroup"]
        assert log_group["Type"] == "AWS::Logs::LogGroup"
        assert log_group["Properties"]["RetentionInDays"] == 30
        assert app_config["app_name"] in log_group["Properties"]["LogGroupName"]
    
    def test_generate_route53_records(self, aws_config):
        """Route53 DNS設定生成"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        dns_records = generator.generate_route53_records(aws_config)
        
        assert "DNSRecord" in dns_records
        record = dns_records["DNSRecord"]
        assert record["Type"] == "AWS::Route53::RecordSet"
        assert record["Properties"]["Type"] == "A"
        assert record["Properties"]["Name"] == aws_config["domain_name"]
        assert record["Properties"]["HostedZoneId"] == aws_config["route53_zone_id"]
        
        # ALBへのエイリアス設定
        alias = record["Properties"]["AliasTarget"]
        assert "Fn::GetAtt" in str(alias["HostedZoneId"]) or "Ref" in str(alias["HostedZoneId"])
    
    def test_generate_iam_roles(self, app_config):
        """IAMロール生成"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        iam_roles = generator.generate_iam_roles(app_config)
        
        # タスク実行ロール
        assert "TaskExecutionRole" in iam_roles
        exec_role = iam_roles["TaskExecutionRole"]
        assert exec_role["Type"] == "AWS::IAM::Role"
        
        policies = exec_role["Properties"]["ManagedPolicyArns"]
        assert "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy" in policies
        
        # タスクロール（アプリケーション用）
        assert "TaskRole" in iam_roles
        task_role = iam_roles["TaskRole"]
        assert len(task_role["Properties"]["Policies"]) > 0
    
    def test_generate_complete_stack(self, app_config, aws_config):
        """完全なCloudFormationスタック生成"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        stack = generator.generate_complete_stack(app_config, aws_config)
        
        # 全体構造
        assert "AWSTemplateFormatVersion" in stack
        assert "Description" in stack
        assert "Parameters" in stack
        assert "Resources" in stack
        assert "Outputs" in stack
        
        # 必須リソース
        resources = stack["Resources"]
        required_resources = [
            "ECSCluster", "ECSTaskDefinition", "ECSService",
            "ALB", "TargetGroup", "HTTPSListener",
            "ALBSecurityGroup", "ECSSecurityGroup",
            "TaskExecutionRole", "TaskRole",
            "LogGroup"
        ]
        
        for resource in required_resources:
            assert resource in resources, f"Missing required resource: {resource}"
        
        # Outputs
        outputs = stack["Outputs"]
        assert "ApplicationURL" in outputs
        assert "ALBEndpoint" in outputs
    
    def test_validate_generated_template(self, app_config, aws_config):
        """生成されたテンプレートのバリデーション"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        template = generator.generate_complete_stack(app_config, aws_config)
        
        # JSONとして有効か
        json_str = json.dumps(template)
        parsed = json.loads(json_str)
        assert parsed is not None
        
        # YAMLとしても出力可能か
        yaml_str = yaml.dump(template, default_flow_style=False)
        assert len(yaml_str) > 0
    
    def test_template_with_database_integration(self, app_config, aws_config):
        """データベース統合のあるテンプレート"""
        from cloudformation_generator import CloudFormationGenerator
        
        app_config["features"] = ["database"]
        generator = CloudFormationGenerator()
        template = generator.generate_complete_stack(app_config, aws_config)
        
        resources = template["Resources"]
        
        # RDS設定があるか
        assert any("RDS" in key or "Database" in key for key in resources.keys())
        
        # データベース接続の環境変数
        task_def = resources["ECSTaskDefinition"]
        container_defs = task_def["Properties"]["ContainerDefinitions"][0]
        env_vars = container_defs.get("Environment", [])
        
        db_vars = ["DATABASE_URL", "DB_HOST", "DB_PORT", "DB_NAME"]
        for var in db_vars:
            assert any(env["Name"] == var for env in env_vars), f"Missing DB env var: {var}"
    
    def test_rollback_configuration(self, app_config, aws_config):
        """ロールバック設定の確認"""
        from cloudformation_generator import CloudFormationGenerator
        
        generator = CloudFormationGenerator()
        template = generator.generate_complete_stack(app_config, aws_config)
        
        # スタックポリシー
        assert "Metadata" in template
        metadata = template["Metadata"]
        assert "AWS::CloudFormation::Interface" in metadata
        
        # UpdatePolicy（ECSサービス用）
        ecs_service = template["Resources"]["ECSService"]
        if "UpdatePolicy" in ecs_service:
            update_policy = ecs_service["UpdatePolicy"]
            assert "AutoRollbackConfiguration" in update_policy

if __name__ == "__main__":
    # TDD Red Phase
    import subprocess
    result = subprocess.run(["python", "-m", "pytest", __file__, "-v"], 
                          capture_output=True, text=True)
    print("=== CloudFormation Generator TDD Test Results ===")
    print(result.stdout)
    print(result.stderr)
    print(f"Exit code: {result.returncode}")
    print("Tests should FAIL initially - this is expected in TDD Red phase!")