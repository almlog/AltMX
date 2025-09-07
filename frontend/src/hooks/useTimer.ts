/**
 * AltMX - タイマーカスタムフック
 * 休憩画面・エンディング画面で使用
 */

import { useState, useEffect, useCallback } from 'react'

interface UseTimerReturn {
  timeRemaining: number
  isRunning: boolean
  start: () => void
  pause: () => void
  reset: () => void
}

export const useTimer = (initialTime: number, onComplete?: () => void): UseTimerReturn => {
  const [timeRemaining, setTimeRemaining] = useState(initialTime)
  const [isRunning, setIsRunning] = useState(false)

  useEffect(() => {
    let interval: NodeJS.Timeout

    if (isRunning && timeRemaining > 0) {
      interval = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            setIsRunning(false)
            onComplete?.()
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }

    return () => clearInterval(interval)
  }, [isRunning, timeRemaining, onComplete])

  const start = useCallback(() => {
    setIsRunning(true)
  }, [])

  const pause = useCallback(() => {
    setIsRunning(false)
  }, [])

  const reset = useCallback(() => {
    setTimeRemaining(initialTime)
    setIsRunning(false)
  }, [initialTime])

  return {
    timeRemaining,
    isRunning,
    start,
    pause,
    reset
  }
}