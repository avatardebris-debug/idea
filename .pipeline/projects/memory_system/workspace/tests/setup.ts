import '@testing-library/jest-dom';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock window.confirm
window.confirm = jest.fn(() => true);

// Mock window.URL.createObjectURL
URL.createObjectURL = jest.fn(() => 'mock-url');
