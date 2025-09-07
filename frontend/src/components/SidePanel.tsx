/**
 * AltMX - サイドパネル（AltMXステータス + トークログ）
 * 仕様書: /src/ui/02-main-vaporwave.md
 */

import type { FC } from 'react'
import AltMXStatusPanel from './AltMXStatusPanel'
import TalkLogPanel from './TalkLogPanel'
import TurboModeButton from './TurboModeButton'

interface SidePanelProps {
  altmxStatus: {
    recognition: 'online' | 'offline'
    generation: 'turbo' | 'normal' | 'eco'
    quality: 'maximum' | 'high' | 'medium'
    speed: number
  }
  talkLog: Array<{
    type: 'user' | 'ai'
    message: string
    timestamp: Date
  }>
  isTurboMode: boolean
  onTurboToggle: () => void
  onSendMessage: (message: string) => void
}

const SidePanel: FC<SidePanelProps> = ({
  altmxStatus,
  talkLog,
  isTurboMode,
  onTurboToggle,
  onSendMessage
}) => {
  return (
    <div className="side-panel">
      <div className="side-panel-content">
        {/* AltMXステータス表示 */}
        <AltMXStatusPanel status={altmxStatus} />

        {/* ターボモードボタン */}
        <TurboModeButton 
          isActive={isTurboMode}
          onToggle={onTurboToggle}
        />

        {/* トークログ */}
        <TalkLogPanel 
          talkLog={talkLog}
          onSendMessage={onSendMessage}
        />
      </div>
    </div>
  )
}

export default SidePanel