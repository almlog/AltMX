/**
 * Test Utilities for Component Testing
 * TDD Helper Functions
 */

import React from 'react'
import { render as rtlRender, RenderOptions } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { RouteProvider } from '../contexts/RouteContext'

/**
 * Custom render function that wraps components with necessary providers
 * Ensures all context-dependent components can be tested properly
 */
export function renderWithProviders(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <MemoryRouter initialEntries={['/']}>
        <RouteProvider>
          {children}
        </RouteProvider>
      </MemoryRouter>
    )
  }

  return rtlRender(ui, { wrapper: Wrapper, ...options })
}

// Re-export everything from @testing-library/react
export * from '@testing-library/react'
// Override render with our custom version
export { renderWithProviders as render }