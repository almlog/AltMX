"""
EC2デプロイサービス
生成されたReactアプリケーションを自動デプロイ
"""

import os
import json
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

class DeploymentService:
    """デプロイメント管理サービス"""
    
    def __init__(self):
        self.base_deploy_path = Path("/home/AltMX-admin/deployments")
        self.base_deploy_path.mkdir(exist_ok=True)
        self.port_range = range(3000, 3100)
        self.deployments = {}  # deployment_id -> deployment_info
        
    def _get_next_available_port(self) -> int:
        """利用可能な次のポートを取得"""
        used_ports = set()
        
        # 既存のデプロイメントのポートを収集
        for deployment in self.deployments.values():
            if deployment.get("port"):
                used_ports.add(deployment["port"])
        
        # netstatで実際に使用中のポートを確認
        try:
            result = subprocess.run(
                ["ss", "-tuln"], 
                capture_output=True, 
                text=True
            )
            for line in result.stdout.split('\n'):
                if ':' in line:
                    parts = line.split()
                    for part in parts:
                        if ':' in part:
                            try:
                                port = int(part.split(':')[-1])
                                used_ports.add(port)
                            except ValueError:
                                pass
        except Exception:
            pass
            
        # 利用可能なポートを探す
        for port in self.port_range:
            if port not in used_ports:
                return port
                
        raise RuntimeError("No available ports in range 3000-3099")
    
    def _create_react_project(self, app_name: str, files: List[Dict[str, str]]) -> Path:
        """Reactプロジェクトを作成"""
        # プロジェクトディレクトリ作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = f"{app_name}_{timestamp}"
        project_path = self.base_deploy_path / project_name
        project_path.mkdir(exist_ok=True)
        
        # package.json作成
        package_json = {
            "name": app_name,
            "version": "1.0.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "typescript": "^4.9.5"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "serve": "serve -s build"
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "react-scripts": "5.0.1",
                "serve": "^14.2.0"
            }
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)
        
        # srcディレクトリ作成
        src_path = project_path / "src"
        src_path.mkdir(exist_ok=True)
        
        # publicディレクトリ作成
        public_path = project_path / "public"
        public_path.mkdir(exist_ok=True)
        
        # index.html作成
        index_html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>AltMX Generated App</title>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>"""
        
        with open(public_path / "index.html", "w") as f:
            f.write(index_html)
        
        # 生成されたファイルを配置
        for file_info in files:
            filename = file_info["filename"]
            content = file_info["content"]
            
            # ファイル拡張子に応じて配置先を決定
            if filename.endswith(('.tsx', '.ts', '.jsx', '.js', '.css')):
                file_path = src_path / filename
            else:
                file_path = public_path / filename
                
            with open(file_path, "w") as f:
                f.write(content)
        
        # index.tsxが無い場合は作成
        if not (src_path / "index.tsx").exists():
            index_tsx = """import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""
            with open(src_path / "index.tsx", "w") as f:
                f.write(index_tsx)
        
        # index.cssが無い場合は作成
        if not (src_path / "index.css").exists():
            index_css = """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}"""
            with open(src_path / "index.css", "w") as f:
                f.write(index_css)
                
        return project_path
    
    async def deploy_app(
        self, 
        app_name: str, 
        files: List[Dict[str, str]],
        instance_type: str = "local",
        region: str = "ap-northeast-1"
    ) -> Dict[str, Any]:
        """アプリケーションをデプロイ"""
        
        deployment_id = f"dep_{uuid.uuid4().hex[:8]}"
        
        try:
            # デプロイメント情報を初期化
            self.deployments[deployment_id] = {
                "id": deployment_id,
                "app_name": app_name,
                "status": "preparing",
                "progress": 10,
                "message": "プロジェクトを準備中...",
                "created_at": datetime.now().isoformat()
            }
            
            # プロジェクト作成
            project_path = self._create_react_project(app_name, files)
            self.deployments[deployment_id]["project_path"] = str(project_path)
            self.deployments[deployment_id]["progress"] = 30
            self.deployments[deployment_id]["message"] = "依存関係をインストール中..."
            
            # npm install実行
            install_result = subprocess.run(
                ["npm", "install"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if install_result.returncode != 0:
                raise RuntimeError(f"npm install failed: {install_result.stderr}")
                
            self.deployments[deployment_id]["progress"] = 60
            self.deployments[deployment_id]["message"] = "アプリケーションをビルド中..."
            
            # ビルド実行
            build_result = subprocess.run(
                ["npm", "run", "build"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if build_result.returncode != 0:
                raise RuntimeError(f"Build failed: {build_result.stderr}")
            
            self.deployments[deployment_id]["progress"] = 80
            self.deployments[deployment_id]["message"] = "サーバーを起動中..."
            
            # 利用可能なポートを取得
            port = self._get_next_available_port()
            self.deployments[deployment_id]["port"] = port
            
            # serveコマンドでアプリを起動
            serve_process = subprocess.Popen(
                ["npx", "serve", "-s", "build", "-l", str(port)],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.deployments[deployment_id]["process_pid"] = serve_process.pid
            
            # 少し待ってサーバーが起動するのを確認
            await asyncio.sleep(2)
            
            # デプロイ完了
            deployment_url = f"http://13.158.137.20:{port}/"
            self.deployments[deployment_id].update({
                "status": "completed",
                "progress": 100,
                "message": "デプロイ完了！",
                "url": deployment_url,
                "completed_at": datetime.now().isoformat()
            })
            
            return {
                "deployment_id": deployment_id,
                "status": "completed",
                "url": deployment_url,
                "message": f"アプリケーションが {deployment_url} でデプロイされました！"
            }
            
        except Exception as e:
            self.deployments[deployment_id].update({
                "status": "failed",
                "message": f"デプロイ失敗: {str(e)}",
                "error": str(e)
            })
            raise
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """デプロイメントステータスを取得"""
        if deployment_id not in self.deployments:
            return {
                "error": "Deployment not found",
                "deployment_id": deployment_id
            }
        
        return self.deployments[deployment_id]
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """全デプロイメントをリスト"""
        return list(self.deployments.values())
    
    def stop_deployment(self, deployment_id: str) -> bool:
        """デプロイメントを停止"""
        if deployment_id not in self.deployments:
            return False
            
        deployment = self.deployments[deployment_id]
        
        # プロセスを停止
        if "process_pid" in deployment:
            try:
                subprocess.run(["kill", str(deployment["process_pid"])])
            except Exception:
                pass
        
        # ステータス更新
        deployment["status"] = "stopped"
        deployment["stopped_at"] = datetime.now().isoformat()
        
        return True

# シングルトンインスタンス
deployment_service = DeploymentService()