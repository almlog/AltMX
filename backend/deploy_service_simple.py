"""
シンプルなEC2デプロイサービス
生成されたReactアプリケーションを軽量かつ高速にデプロイ
"""

import os
import json
import subprocess
import uuid
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import asyncio

class SimpleDeploymentService:
    """シンプルなデプロイメント管理サービス"""
    
    def __init__(self):
        self.base_deploy_path = Path("/home/AltMX-admin/deployments")
        self.base_deploy_path.mkdir(exist_ok=True)
        self.port_range = range(3000, 3100)
        self.deployments = {}
        
    def _get_next_available_port(self) -> int:
        """利用可能な次のポートを取得"""
        used_ports = {d.get("port") for d in self.deployments.values() if d.get("port")}
        
        for port in self.port_range:
            if port not in used_ports:
                # 実際にポートが使用されていないか確認
                result = subprocess.run(
                    ["ss", "-tuln"], 
                    capture_output=True, 
                    text=True
                )
                if f":{port}" not in result.stdout:
                    return port
                    
        raise RuntimeError("No available ports")
    
    async def deploy_simple_app(
        self, 
        app_name: str, 
        files: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """シンプルなHTMLデプロイ"""
        
        deployment_id = f"dep_{uuid.uuid4().hex[:8]}"
        
        try:
            # プロジェクトディレクトリ作成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = f"{app_name}_{timestamp}"
            project_path = self.base_deploy_path / project_name
            project_path.mkdir(exist_ok=True)
            
            # index.html作成（React appをバンドル）
            app_tsx = next((f["content"] for f in files if f["filename"] == "App.tsx"), "")
            app_css = next((f["content"] for f in files if f["filename"] == "App.css"), "")
            
            # TypeScript型アノテーションを削除してJSXに変換
            import re
            # import文とexport文を削除（ブラウザでは不要）
            app_jsx = re.sub(r'import.*?;', '', app_tsx, flags=re.MULTILINE)
            app_jsx = re.sub(r'export\s+default\s+\w+;?', '', app_jsx, flags=re.MULTILINE)
            
            # 基本的な型アノテーション削除
            app_jsx = re.sub(r': React\.FC\s*=', ' =', app_jsx)
            app_jsx = re.sub(r'<Todo\[\]>', '', app_jsx)
            app_jsx = re.sub(r'\(id: number\)', '(id)', app_jsx)
            app_jsx = re.sub(r'useState<[^>]+>', 'useState', app_jsx)
            # interface定義をコメント化
            app_jsx = re.sub(r'interface\s+\w+\s*{[^}]*}', '// TypeScript interface removed for browser compatibility', app_jsx, flags=re.DOTALL)
            # 変数の型アノテーション削除
            app_jsx = re.sub(r':\s*\w+\s*=', ' =', app_jsx)  # `: Todo =` -> ` =`
            app_jsx = re.sub(r'const\s+(\w+):\s*\w+\s*=', r'const \1 =', app_jsx)  # `const newTodo: Todo =` -> `const newTodo =`
            # 改行の修正と空行削除
            app_jsx = app_jsx.replace('useState // }', 'useState')
            app_jsx = re.sub(r'\n\s*\n\s*\n', '\n\n', app_jsx)  # 複数の空行を削除
            app_jsx = app_jsx.strip()  # 先頭と末尾の空白削除
            
            index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{app_name} - AltMX Generated</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        {app_css}
    </style>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
        const {{ useState }} = React;
        
        {app_jsx}
        
        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>"""
            
            with open(project_path / "index.html", "w") as f:
                f.write(index_html)
            
            # ポート取得
            port = self._get_next_available_port()
            
            # Python HTTPサーバーで起動
            serve_process = subprocess.Popen(
                ["python3", "-m", "http.server", str(port)],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # デプロイ情報を保存
            deployment_url = f"http://18.180.87.189:{port}/"
            self.deployments[deployment_id] = {
                "id": deployment_id,
                "app_name": app_name,
                "status": "completed",
                "url": deployment_url,
                "port": port,
                "process_pid": serve_process.pid,
                "project_path": str(project_path),
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "deployment_id": deployment_id,
                "status": "completed",
                "url": deployment_url,
                "message": f"✅ デプロイ成功！ {deployment_url} でアクセス可能です"
            }
            
        except Exception as e:
            return {
                "deployment_id": deployment_id,
                "status": "failed",
                "message": f"デプロイ失敗: {str(e)}",
                "error": str(e)
            }
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """デプロイメントステータスを取得"""
        return self.deployments.get(deployment_id, {
            "error": "Deployment not found",
            "deployment_id": deployment_id
        })
    
    def list_deployments(self) -> List[Dict[str, Any]]:
        """全デプロイメントをリスト"""
        return list(self.deployments.values())
    
    def stop_deployment(self, deployment_id: str) -> bool:
        """デプロイメントを停止"""
        if deployment_id not in self.deployments:
            return False
            
        deployment = self.deployments[deployment_id]
        
        if "process_pid" in deployment:
            try:
                subprocess.run(["kill", str(deployment["process_pid"])])
            except Exception:
                pass
        
        deployment["status"] = "stopped"
        return True

# シングルトンインスタンス
simple_deployment_service = SimpleDeploymentService()