import { useState } from 'react'

function App() {
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState<{ user: string; altmx: string }[]>([])

  const sendMessage = async () => {
    if (!message.trim()) return

    // Add user message to history
    const newHistory = [...chatHistory, { user: message, altmx: '考え中...' }]
    setChatHistory(newHistory)

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          use_sapporo_dialect: true
        })
      })

      const data = await response.json()
      
      // Update with AltMX response
      newHistory[newHistory.length - 1].altmx = data.response
      setChatHistory([...newHistory])
    } catch (error) {
      console.error('Error:', error)
      newHistory[newHistory.length - 1].altmx = 'ちょっと調子悪いわ...'
      setChatHistory([...newHistory])
    }

    setMessage('')
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-altmx-blue mb-2">AltMX</h1>
          <p className="text-gray-300">AI協働開発ライブデモンストレーションシステム MVP</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Chat Interface */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">AltMX Console</h2>
            
            {/* Car Visualization Placeholder */}
            <div className="bg-gray-700 rounded p-4 mb-4 text-center">
              <div className="text-6xl mb-2">🏎️</div>
              <p className="text-sm text-gray-400">AltMX スポーツカー (ライト点滅対応予定)</p>
            </div>

            {/* Chat History */}
            <div className="h-64 overflow-y-auto bg-gray-700 rounded p-4 mb-4">
              {chatHistory.length === 0 ? (
                <p className="text-gray-400 italic">なんまら話しかけてよ〜</p>
              ) : (
                chatHistory.map((chat, index) => (
                  <div key={index} className="mb-4">
                    <div className="bg-blue-600 rounded p-2 mb-2">
                      <strong>しゅんぺい:</strong> {chat.user}
                    </div>
                    <div className="bg-altmx-blue text-black rounded p-2">
                      <strong>AltMX:</strong> {chat.altmx}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="メッセージを入力..."
                className="flex-1 bg-gray-700 rounded px-4 py-2 text-white placeholder-gray-400"
              />
              <button
                onClick={sendMessage}
                className="bg-altmx-blue text-black px-6 py-2 rounded font-semibold hover:bg-blue-400"
              >
                送信
              </button>
            </div>
          </div>

          {/* Live Preview */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Live Preview</h2>
            <div className="bg-gray-700 rounded p-4 h-80 flex items-center justify-center">
              <p className="text-gray-400">生成されたコードのプレビューがここに表示されます</p>
            </div>
          </div>
        </div>

        {/* Status Bar */}
        <div className="mt-8 bg-gray-800 rounded-lg p-4">
          <div className="flex justify-between items-center">
            <span className="text-green-400">● Backend: Connected</span>
            <span className="text-altmx-blue">AltMX v1.0 MVP</span>
            <span className="text-gray-400">TDD Ready</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
