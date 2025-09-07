/**
 * AltMX - AI協働開発ライブデモンストレーションシステム メインアプリケーション
 * React Router統合版: ヴェイパーウェイブUI + ルーティングシステム
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { RouteProvider } from './contexts/RouteContext'
import { 
  OpeningScreenWrapper,
  BreakScreenWrapper,
  EndingScreenWrapper,
  NotFoundScreenWrapper,
  BadRequestErrorScreenWrapper,
  InternalServerErrorScreenWrapper,
  ServiceUnavailableScreenWrapper
} from './components/RouteWrappers'
import VaporwaveMainScreen from './components/VaporwaveMainScreen'
import './styles/vaporwave-main.css'
import './styles/error-screens.css'

function App() {
  return (
    <BrowserRouter>
      <RouteProvider>
        <Routes>
          {/* オープニング画面 - システム起動 */}
          <Route path="/" element={<OpeningScreenWrapper />} />
          
          {/* メイン画面 - ヴェイパーウェイブUI */}
          <Route path="/main" element={<VaporwaveMainScreen />} />
          <Route path="/main/:viewMode" element={<VaporwaveMainScreen />} />
          
          {/* 休憩画面 - 5分タイマー */}
          <Route path="/break" element={<BreakScreenWrapper />} />
          
          {/* エンディング画面 - 神聖な締めくくり */}
          <Route path="/ending" element={<EndingScreenWrapper />} />
          
          {/* HTTPエラー画面 - 各テーマ */}
          <Route path="/error/404" element={<NotFoundScreenWrapper />} />
          <Route path="/error/400" element={<BadRequestErrorScreenWrapper />} />
          <Route path="/error/500" element={<InternalServerErrorScreenWrapper />} />
          <Route path="/error/503" element={<ServiceUnavailableScreenWrapper />} />
          
          {/* 未定義パス - 404にリダイレクト */}
          <Route path="*" element={<NotFoundScreenWrapper />} />
        </Routes>
      </RouteProvider>
    </BrowserRouter>
  )
}

export default App