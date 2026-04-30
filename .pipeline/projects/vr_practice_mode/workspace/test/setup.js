/**
 * Test setup file for Vitest
 * Initializes global mocks and test environment
 */

// Mock A-Frame elements for testing
global.document = {
  querySelector: () => ({
    addEventListener: () => {},
    setAttribute: () => {},
    getAttribute: () => null,
    hasAttribute: () => false,
    appendChild: () => {},
    removeAttribute: () => {}
  }),
  getElementById: () => ({
    addEventListener: () => {},
    setAttribute: () => {},
    getAttribute: () => null,
    hasAttribute: () => false,
    appendChild: () => {},
    removeAttribute: () => {},
    classList: { add: () => {}, remove: () => {}, toggle: () => {} },
    style: { opacity: '', display: '' },
    textContent: ''
  }),
  addEventListener: () => {},
  querySelectorAll: () => []
};

global.window = {
  addEventListener: () => {},
  resize: {}
};

global.performance = {
  now: () => Date.now()
};

// Mock console for test output control
global.console = {
  ...console,
  log: vi.fn(),
  warn: vi.fn(),
  error: vi.fn()
};
