// Test setup file for shared components
// Mocks browser APIs not available in jsdom

// Mock CSRF token cookie
Object.defineProperty(document, 'cookie', {
  writable: true,
  value: 'csrf_token=test-csrf-token',
})

// Mock global fetch
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve({ message: {} }),
  })
)

// Mock getComputedStyle to return CSS variable values
const cssVarMap = {
  '--primary': '#4F46E5',
  '--success': '#10B981',
  '--warning': '#F59E0B',
  '--error': '#EF4444',
  '--info': '#3B82F6',
  '--secondary': '#9333EA',
  '--text-primary': '#0F172A',
  '--text-secondary': '#64748B',
  '--bg-card': '#FFFFFF',
}

const originalGetComputedStyle = window.getComputedStyle
window.getComputedStyle = (element, pseudoElt) => {
  const style = originalGetComputedStyle(element, pseudoElt)
  const originalGetPropertyValue = style.getPropertyValue.bind(style)
  style.getPropertyValue = (prop) => {
    if (cssVarMap[prop]) return cssVarMap[prop]
    return originalGetPropertyValue(prop)
  }
  return style
}

// Mock MutationObserver
class MockMutationObserver {
  constructor(callback) {
    this._callback = callback
  }
  observe() {}
  disconnect() {}
}
global.MutationObserver = MockMutationObserver

// Mock ResizeObserver (needed by ApexCharts)
class MockResizeObserver {
  constructor(callback) {
    this._callback = callback
  }
  observe() {}
  unobserve() {}
  disconnect() {}
}
global.ResizeObserver = MockResizeObserver
