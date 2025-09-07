# AltMX コードスタイル規約

## TypeScript/React 規約

### ファイル命名規則
- **コンポーネント**: PascalCase (`AltMXAgent.tsx`)
- **Hooks**: camelCase with use prefix (`useAltMXChat.ts`)
- **Utils**: camelCase (`altmxHelpers.ts`)
- **Types**: PascalCase (`AltMXTypes.ts`)

### コンポーネント規約
```tsx
// 関数コンポーネント with TypeScript
interface AltMXAgentProps {
  message: string;
  onResponse: (response: string) => void;
}

export const AltMXAgent: React.FC<AltMXAgentProps> = ({ 
  message, 
  onResponse 
}) => {
  // Hook calls at top
  const [isThinking, setIsThinking] = useState(false);
  
  // Event handlers
  const handleSpeak = useCallback(() => {
    // implementation
  }, []);

  return (
    <div className="altmx-agent">
      {/* JSX */}
    </div>
  );
};
```

### 型定義規約
```tsx
// Strict typing required
interface AltMXResponse {
  id: string;
  content: string;
  timestamp: Date;
  dialect?: SapporoDialectType;
}

// Union types for state management
type AltMXStatus = 'idle' | 'thinking' | 'speaking' | 'error';
```

### カスタムHooks規約
```tsx
export const useAltMXChat = () => {
  const [messages, setMessages] = useState<AltMXMessage[]>([]);
  
  return {
    messages,
    sendMessage,
    clearMessages,
  } as const; // readonly return
};
```

## Python/FastAPI 規約

### ファイル命名規則
- **モデル**: snake_case (`altmx_models.py`)
- **API**: snake_case (`altmx_api.py`)
- **サービス**: snake_case (`altmx_service.py`)

### APIエンドポイント規約
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/altmx", tags=["altmx"])

class AltMXRequest(BaseModel):
    message: str
    dialect_level: Optional[int] = 1

class AltMXResponse(BaseModel):
    response: str
    thinking_time: float
    dialect_used: bool

@router.post("/chat", response_model=AltMXResponse)
async def chat_with_altmx(request: AltMXRequest):
    """AltMXエージェントとのチャット"""
    try:
        # implementation
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 型ヒント規約
```python
from typing import List, Dict, Optional, Union
from datetime import datetime

def process_sapporo_dialect(
    text: str, 
    level: int = 1
) -> Dict[str, Union[str, bool]]:
    """札幌なまり処理"""
    return {
        "processed_text": processed,
        "dialect_applied": True
    }
```

## テスト規約

### テストファイル命名
- **Frontend**: `*.test.tsx` or `*.spec.tsx`
- **Backend**: `test_*.py`

### テスト構造
```tsx
// React Testing Library
describe('AltMXAgent', () => {
  it('should display message correctly', () => {
    render(<AltMXAgent message="test" onResponse={jest.fn()} />);
    expect(screen.getByText('test')).toBeInTheDocument();
  });
});
```

```python
# pytest
class TestAltMXService:
    def test_generate_response(self):
        service = AltMXService()
        response = service.generate_response("こんにちは")
        assert response.dialect_used == True
```

## 共通規約

### コメント規約
- 必要最小限のコメント
- 「なぜ」を説明、「何を」は避ける
- 札幌なまりの実装部分は詳細コメント必須

### エラーハンドリング
- すべての外部API呼び出しでtry-catch
- ユーザーフレンドリーなエラーメッセージ
- 札幌なまりでエラーも表現（「ちょっと調子悪いわ」等）