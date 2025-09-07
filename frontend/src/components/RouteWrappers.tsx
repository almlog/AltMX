/**
 * AltMX - Route Wrappers
 * ルーター統合用のラッパーコンポーネント
 * 各画面に必要なpropsのデフォルト値を提供
 */

import React from 'react'
import OpeningScreen from './OpeningScreen/OpeningScreen'
import BreakScreen from './BreakScreen/BreakScreen'
import EndingScreen from './EndingScreen/EndingScreen'
import NotFoundScreen from './ErrorScreen/NotFoundScreen'
import BadRequestErrorScreen from './ErrorScreen/BadRequestErrorScreen'
import InternalServerErrorScreen from './ErrorScreen/InternalServerErrorScreen'
import ServiceUnavailableScreen from './ErrorScreen/ServiceUnavailableScreen'

// OpeningScreen用ラッパー
export const OpeningScreenWrapper: React.FC = () => {
  return (
    <OpeningScreen 
      showBootSequence={true}
    />
  )
}

// BreakScreen用ラッパー
export const BreakScreenWrapper: React.FC = () => {
  const handleComplete = () => {
    console.log('Break completed')
  }

  return (
    <BreakScreen 
      onComplete={handleComplete}
    />
  )
}

// EndingScreen用ラッパー
export const EndingScreenWrapper: React.FC = () => {
  const mockSessionStats = {
    toolsCreated: 5,
    linesGenerated: 1247,
    sessionDuration: 30,
    successRate: 96.5
  }

  const mockCreatedTools = [
    { name: 'REST APIクライアント', type: 'API Tool', complexity: 'medium' as const },
    { name: 'データバリデーター', type: 'Utility', complexity: 'simple' as const },
    { name: 'CI/CDパイプライン', type: 'DevOps', complexity: 'complex' as const }
  ]

  const mockNextActions = [
    { 
      type: 'consultation' as const, 
      title: '無料相談予約', 
      url: 'https://altmx.ai/consultation',
      qrCode: 'data:image/png;base64,test-qr-code'
    },
    { 
      type: 'download' as const, 
      title: '開発資料DL', 
      url: 'https://altmx.ai/resources'
    },
    { 
      type: 'community' as const, 
      title: 'コミュニティ参加', 
      url: 'https://community.altmx.ai'
    }
  ]

  const handleComplete = () => {
    console.log('Ending completed')
  }

  return (
    <EndingScreen 
      sessionStats={mockSessionStats}
      createdTools={mockCreatedTools}
      nextActions={mockNextActions}
      onComplete={handleComplete}
    />
  )
}

// NotFoundScreen用ラッパー（すでに統合済み）
export const NotFoundScreenWrapper: React.FC = () => {
  return <NotFoundScreen />
}

// BadRequestErrorScreen用ラッパー
export const BadRequestErrorScreenWrapper: React.FC = () => {
  const handleRecordingSwitch = () => {
    console.log('Recording switch requested from BadRequest')
  }

  const handleRetry = () => {
    console.log('Retry requested from BadRequest')
  }

  return (
    <BadRequestErrorScreen 
      onRecordingSwitch={handleRecordingSwitch}
      onRetry={handleRetry}
    />
  )
}

// InternalServerErrorScreen用ラッパー
export const InternalServerErrorScreenWrapper: React.FC = () => {
  const handleRecordingSwitch = () => {
    console.log('Recording switch requested from InternalServerError')
  }

  const handleEmergencyMode = () => {
    console.log('Emergency mode requested from InternalServerError')
  }

  return (
    <InternalServerErrorScreen 
      onRecordingSwitch={handleRecordingSwitch}
      onEmergencyMode={handleEmergencyMode}
    />
  )
}

// ServiceUnavailableScreen用ラッパー
export const ServiceUnavailableScreenWrapper: React.FC = () => {
  const handleRecordingSwitch = () => {
    console.log('Recording switch requested from ServiceUnavailable')
  }

  const handleWaitAndRetry = () => {
    console.log('Wait and retry requested from ServiceUnavailable')
  }

  return (
    <ServiceUnavailableScreen 
      onRecordingSwitch={handleRecordingSwitch}
      onWaitAndRetry={handleWaitAndRetry}
    />
  )
}