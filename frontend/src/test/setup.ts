import '@testing-library/jest-dom'
import { vi } from 'vitest'

// Global fetch mock for all tests
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ mode: 'chat', message: 'Test mode' })
  })
) as any