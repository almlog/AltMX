# AltMX アーキテクチャ分析と改善案

## 現状の問題点

### 1. チャット vs ライブコーディングの分岐が曖昧

**現在の実装**:
```typescript
// キーワードベースの判定（不十分）
if any(keyword in request.message.lower() for keyword in [
    'create', 'build', 'make', 'generate', 'develop', 'code', 'app', 'component'
]):
    // コード生成モード
```

**問題**:
- 「create a user account」でもコード生成モードになってしまう
- 「Make it blue」のようなデザイン変更でも誤判定
- ユーザーの意図が不明確

### 2. 複数アプリの管理体系が不統一

**現在の状況**:
```
/home/AltMX-admin/deployments/
├── todo-app-test_20250906_143301/     # タイムスタンプベース命名
├── todo-app-test_20250906_143336/     # 同じアプリの重複
├── professional-todo-app_20250906_151150/  # 異なる命名規則
```

**問題**:
- アプリの関係性が不明
- バージョン管理なし
- デプロイ履歴の追跡困難
- ストレージの無駄遣い

### 3. プロジェクト構造の設計思想が不明確

**現在の配置**:
```
/home/AltMX-admin/
├── AltMX/                    # メインプロジェクト
│   ├── frontend/            # AltMX自体のフロントエンド
│   └── backend/             # AltMX自体のバックエンド
└── deployments/             # 生成されたアプリ（別階層）
```

**問題**:
- 生成アプリがメインプロジェクトから分離
- 一元管理できない
- バックアップ・移行が複雑

## 改善案

### 1. 明確な分岐システム

#### A. セッションモード導入
```typescript
interface ChatSession {
  id: string;
  mode: 'chat' | 'live_coding' | 'code_review';
  context?: ProjectContext;
  user_id: string;
  created_at: Date;
}

// ユーザーが明示的にモード選択
@app.post("/api/session/start")
async def start_session(mode: SessionMode, project_id?: string)
```

#### B. インテント分析強化
```typescript
// AI-powered intent classification
const analyzeIntent = (message: string): IntentResult => {
  const codeGenerationSignals = [
    'build an app',
    'create a component', 
    'generate code for',
    'implement feature',
    'write a function'
  ];
  
  const chatSignals = [
    'how do I',
    'what is', 
    'explain',
    'help me understand'
  ];
  
  return {
    intent: 'code_generation' | 'chat' | 'ambiguous',
    confidence: 0.85,
    suggested_action: 'ask_for_clarification'
  };
};
```

### 2. プロジェクト管理システム

#### A. 階層的プロジェクト構造
```
/home/AltMX-admin/AltMX/
├── core/                           # AltMXシステム本体
│   ├── frontend/
│   └── backend/
├── workspace/                      # ユーザープロジェクト群
│   ├── projects/
│   │   ├── todo-management/        # プロジェクト名
│   │   │   ├── metadata.json      # プロジェクト情報
│   │   │   ├── versions/           # バージョン管理
│   │   │   │   ├── v1.0.0/
│   │   │   │   ├── v1.1.0/
│   │   │   │   └── latest -> v1.1.0
│   │   │   └── deployments/        # デプロイ履歴
│   │   │       ├── prod/
│   │   │       └── staging/
│   │   └── chat-application/
│   └── templates/                  # 再利用可能テンプレート
└── generated/                      # 一時生成ファイル
```

#### B. プロジェクトメタデータ管理
```typescript
interface ProjectMetadata {
  id: string;
  name: string;
  description: string;
  type: 'react-app' | 'vue-app' | 'vanilla-js' | 'component-library';
  created_at: Date;
  updated_at: Date;
  versions: Version[];
  current_version: string;
  deployments: Deployment[];
  tags: string[];
  dependencies: Dependency[];
  live_coding_sessions: LiveCodingSession[];
}

interface Version {
  version: string;
  created_at: Date;
  changes: string;
  files: GeneratedFile[];
  deployment_url?: string;
  performance_metrics?: PerformanceMetrics;
}
```

### 3. 統合開発環境アーキテクチャ

#### A. ワークスペース中心設計
```typescript
class AltMXWorkspace {
  // プロジェクト管理
  createProject(name: string, type: ProjectType): Project
  listProjects(): Project[]
  getProject(id: string): Project
  deleteProject(id: string): void
  
  // バージョン管理
  createVersion(projectId: string, changes: string): Version
  deployVersion(projectId: string, version: string, env: 'staging' | 'prod'): Deployment
  
  // ライブコーディング
  startLiveCoding(projectId: string): LiveCodingSession
  updateLiveCode(sessionId: string, changes: CodeChange[]): void
  deployLiveSession(sessionId: string): Deployment
}
```

#### B. 統合API設計
```typescript
// 統一されたプロジェクト操作API
@app.post("/api/workspace/projects")
async def create_project(request: CreateProjectRequest): ProjectResponse

@app.get("/api/workspace/projects")  
async def list_projects(): ProjectListResponse

@app.post("/api/workspace/projects/{project_id}/versions")
async def create_version(project_id: str, changes: VersionRequest): VersionResponse

@app.post("/api/workspace/projects/{project_id}/live-coding")
async def start_live_coding(project_id: str): LiveCodingSessionResponse
```

## 提案する新アーキテクチャ

### 1. セッション管理レイヤー
- ユーザー明示的なモード選択
- コンテキスト保持
- セッション間のデータ継承

### 2. プロジェクト管理レイヤー  
- Git-likeなバージョン管理
- メタデータ駆動の管理
- 階層的組織化

### 3. デプロイメント管理レイヤー
- 環境別デプロイ（staging/prod）
- ロールバック機能
- パフォーマンス監視

### 4. ライブコーディング統合
- リアルタイム更新
- 履歴追跡
- 観客参加機能

## 実装優先度

### Phase 1: 基盤整備
1. プロジェクト管理システム実装
2. 新しいディレクトリ構造への移行
3. メタデータ管理機能

### Phase 2: UX改善
1. セッションモード導入
2. 明確な分岐UI実装
3. プロジェクト一覧・管理画面

### Phase 3: 高度機能
1. バージョン管理システム
2. 環境別デプロイ
3. ライブコーディング強化

## 期待される効果

### 開発体験向上
- 明確な作業モード分離
- プロジェクトの体系的管理
- バージョン履歴の追跡可能

### 運用効率化
- ストレージ使用量最適化
- デプロイ管理の自動化
- 障害時の迅速な復旧

### ライブコーディング品質向上
- プロジェクト継続性の確保
- 観客へのより良い体験提供
- 教育的価値の最大化

---

この設計により、AltMXは真の統合開発環境として進化します。