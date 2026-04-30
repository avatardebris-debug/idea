/**
 * Test Setup File
 * Configures the test environment for VR Practice Mode tests
 */

// Mock A-Frame
global.AFRAME = {
  registerComponent: jest.fn(),
  registerSystem: jest.fn(),
  registerBehavior: jest.fn()
};

// Mock Three.js
global.THREE = {
  Vector3: class Vector3 {
    constructor(x = 0, y = 0, z = 0) {
      this.x = x;
      this.y = y;
      this.z = z;
    }
  },
  Scene: class Scene {},
  Camera: class Camera {},
  WebGLRenderer: class WebGLRenderer {}
};

// Mock DOM elements
global.document = {
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  querySelector: jest.fn(),
  querySelectorAll: jest.fn(),
  createElement: jest.fn(),
  getElementById: jest.fn()
};

global.window = {
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  resize: jest.fn()
};

// Mock A-Frame scene
global.document.querySelector = (selector) => {
  if (selector === 'a-scene') {
    return {
      addEventListener: jest.fn(),
      object3D: {
        position: { x: 0, y: 0, z: 0 }
      }
    };
  }
  return null;
};

// Mock A-Frame entity
global.document.createElement = (tag) => {
  return {
    setAttribute: jest.fn(),
    appendChild: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    getAttribute: jest.fn(),
    setAttribute: jest.fn(),
    object3D: {
      position: { x: 0, y: 0, z: 0 }
    }
  };
};

// Mock event target
global.HTMLElement = class HTMLElement {
  constructor() {
    this.classList = {
      add: jest.fn(),
      remove: jest.fn(),
      toggle: jest.fn(),
      contains: jest.fn()
    };
    this.style = {};
    this.textContent = '';
  }
};

// Mock console
global.console = {
  ...console,
  log: jest.fn(),
  warn: jest.fn(),
  error: jest.fn()
};

// Mock Date
global.Date.now = jest.fn(() => Date.now());

// Mock Math
global.Math.random = jest.fn(() => 0.5);

// Mock requestAnimationFrame
global.requestAnimationFrame = jest.fn((cb) => setTimeout(cb, 16));
global.cancelAnimationFrame = jest.fn((id) => clearTimeout(id));

// Mock localStorage
global.localStorage = {
  getItem: jest.fn(() => null),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};

// Mock performance
global.performance = {
  now: jest.fn(() => Date.now())
};

// Mock navigator
global.navigator = {
  vrDisplay: null,
  getVRDisplays: jest.fn(() => Promise.resolve([]))
};

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe() {}
  disconnect() {}
  takeRecords() {
    return [];
  }
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe() {}
  disconnect() {}
  unobserve() {}
};

// Mock custom elements
global.customElements = {
  define: jest.fn(),
  get: jest.fn()
};

// Mock fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: jest.fn(() => Promise.resolve({}))
  })
);

// Mock XMLHttpRequest
global.XMLHttpRequest = class XMLHttpRequest {
  open() {}
  send() {}
  setRequestHeader() {}
  addEventListener() {}
  removeEventListener() {}
};

// Mock WebSocket
global.WebSocket = class WebSocket {
  constructor() {
    this.readyState = 1;
  }
  send() {}
  close() {}
};

// Mock AudioContext
global.AudioContext = class AudioContext {
  constructor() {}
  createOscillator() {
    return {
      connect: jest.fn(),
      start: jest.fn(),
      stop: jest.fn()
    };
  }
  createGain() {
    return {
      connect: jest.fn(),
      gain: { value: 1 }
    };
  }
};

// Mock Audio
global.Audio = class Audio {
  constructor(src) {
    this.src = src;
  }
  play() {
    return Promise.resolve();
  }
  pause() {}
};

// Mock Video
global.Video = class Video {
  constructor(src) {
    this.src = src;
  }
  play() {
    return Promise.resolve();
  }
  pause() {}
};

// Mock MediaDevices
global.navigator.mediaDevices = {
  getUserMedia: jest.fn(() => Promise.reject(new Error('Not implemented')))
};

// Mock Geolocation
global.navigator.geolocation = {
  getCurrentPosition: jest.fn(() => {}),
  watchPosition: jest.fn(() => {})
};

// Mock Touch
global.Touch = class Touch {
  constructor() {}
};

// Mock TouchList
global.TouchList = class TouchList {
  constructor() {}
};

// Mock PointerEvent
global.PointerEvent = class PointerEvent {
  constructor(type, params) {
    this.type = type;
    this.clientX = params?.clientX || 0;
    this.clientY = params?.clientY || 0;
  }
};

// Mock MouseEvent
global.MouseEvent = class MouseEvent {
  constructor(type, params) {
    this.type = type;
    this.clientX = params?.clientX || 0;
    this.clientY = params?.clientY || 0;
  }
};

// Mock KeyboardEvent
global.KeyboardEvent = class KeyboardEvent {
  constructor(type, params) {
    this.type = type;
    this.key = params?.key || '';
    this.code = params?.code || '';
  }
};

// Mock CustomEvent
global.CustomEvent = class CustomEvent {
  constructor(type, params) {
    this.type = type;
    this.detail = params?.detail || {};
  }
};

// Mock Event
global.Event = class Event {
  constructor(type) {
    this.type = type;
  }
};

// Mock AnimationFrame
global.animationFrame = {
  request: jest.fn(),
  cancel: jest.fn()
};

// Mock CSS
global.getComputedStyle = jest.fn(() => ({
  getPropertyValue: jest.fn(),
  fontSize: '16px'
}));

// Mock querySelector
global.document.getElementById = (id) => {
  const mockElement = {
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      toggle: jest.fn(),
      contains: jest.fn(() => false)
    },
    style: {},
    textContent: '',
    innerHTML: '',
    appendChild: jest.fn(),
    removeChild: jest.fn(),
    remove: jest.fn(),
    setAttribute: jest.fn(),
    getAttribute: jest.fn(() => null),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(() => true),
    focus: jest.fn(),
    blur: jest.fn(),
    click: jest.fn(),
    scrollIntoView: jest.fn(),
    getBoundingClientRect: jest.fn(() => ({
      top: 0,
      left: 0,
      width: 100,
      height: 100
    }))
  };

  if (id === 'toggle-nameplates' || id === 'toggle-connections' || id === 'toggle-health' || id === 'toggle-debug' || id === 'toggle-vr' || id === 'detail-panel' || id === 'proximity-alert' || id === 'debug-panel' || id === 'vr-indicator' || id === 'loading-screen' || id === 'detail-title' || id === 'detail-role' || id === 'detail-health' || id === 'detail-mood' || id === 'detail-tokens' || id === 'detail-uptime' || id === 'detail-last-seen' || id === 'alert-text' || id === 'debug-thronglet-count' || id === 'debug-connection-count' || id === 'debug-selected' || id === 'detail-mood') {
    return mockElement;
  }
  return null;
};

// Mock A-Frame scene loaded event
global.document.querySelector = (selector) => {
  if (selector === 'a-scene') {
    return {
      addEventListener: jest.fn(),
      object3D: {
        position: { x: 0, y: 0, z: 0 }
      }
    };
  }
  return null;
};

// Mock A-Frame entity
global.document.createElement = (tag) => {
  return {
    setAttribute: jest.fn(),
    appendChild: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    getAttribute: jest.fn(),
    setAttribute: jest.fn(),
    object3D: {
      position: { x: 0, y: 0, z: 0 }
    }
  };
};

// Mock A-Frame component registration
global.AFRAME.registerComponent = jest.fn();
global.AFRAME.registerSystem = jest.fn();
global.AFRAME.registerBehavior = jest.fn();

// Mock A-Frame entity methods
global.AFRAME.entities = {
  get: jest.fn(),
  create: jest.fn(),
  destroy: jest.fn()
};

// Mock A-Frame scene methods
global.AFRAME.scenes = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame systems
global.AFRAME.systems = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame components
global.AFRAME.components = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame behaviors
global.AFRAME.behaviors = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame utils
global.AFRAME.utils = {
  entity: {
    get: jest.fn(),
    create: jest.fn(),
    destroy: jest.fn()
  },
  selector: {
    get: jest.fn()
  },
  query: {
    get: jest.fn()
  }
};

// Mock A-Frame events
global.AFRAME.events = {
  emit: jest.fn(),
  on: jest.fn(),
  off: jest.fn()
};

// Mock A-Frame assets
global.AFRAME.assets = {
  get: jest.fn(),
  add: jest.fn()
};

// Mock A-Frame materials
global.AFRAME.materials = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame geometries
global.AFRAME.geometries = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame textures
global.AFRAME.textures = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame sounds
global.AFRAME.sounds = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame videos
global.AFRAME.videos = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame images
global.AFRAME.images = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame models
global.AFRAME.models = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame animations
global.AFRAME.animations = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame physics
global.AFRAME.physics = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame VR
global.AFRAME.VR = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame AR
global.AFRAME.AR = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame XR
global.AFRAME.XR = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame input
global.AFRAME.input = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame camera
global.AFRAME.camera = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame renderer
global.AFRAME.renderer = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame loop
global.AFRAME.loop = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame stats
global.AFRAME.stats = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame debug
global.AFRAME.debug = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame config
global.AFRAME.config = {
  get: jest.fn(),
  create: jest.fn()
};

// Mock A-Frame version
global.AFRAME.version = '1.4.0';

// Mock A-Frame version info
global.AFRAME.versionInfo = {
  major: 1,
  minor: 4,
  patch: 0
};

// Mock A-Frame version string
global.AFRAME.versionString = '1.4.0';

// Mock A-Frame version date
global.AFRAME.versionDate = '2023-01-01';

// Mock A-Frame version commit
global.AFRAME.versionCommit = 'abc123';

// Mock A-Frame version branch
global.AFRAME.versionBranch = 'main';

// Mock A-Frame version author
global.AFRAME.versionAuthor = 'Thronglets Team';

// Mock A-Frame version license
global.AFRAME.versionLicense = 'MIT';

// Mock A-Frame version repository
global.AFRAME.versionRepository = 'https://github.com/thronglets/vr-practice-mode';

// Mock A-Frame version issues
global.AFRAME.versionIssues = 'https://github.com/thronglets/vr-practice-mode/issues';

// Mock A-Frame version homepage
global.AFRAME.versionHomepage = 'https://github.com/thronglets/vr-practice-mode#readme';

// Mock A-Frame version keywords
global.AFRAME.versionKeywords = ['vr', 'aframe', 'threejs', 'thronglets', 'practice-mode', 'webvr'];

// Mock A-Frame version dependencies
global.AFRAME.versionDependencies = {
  aframe: '^1.4.0',
  'aframe-environment-component': '^1.3.2'
};

// Mock A-Frame version devDependencies
global.AFRAME.versionDevDependencies = {
  jest: '^29.7.0',
  eslint: '^8.56.0',
  'http-server': '^14.1.1'
};

// Mock A-Frame version scripts
global.AFRAME.versionScripts = {
  start: 'npx http-server workspace -p 8080 -o',
  test: 'jest',
  test:watch: 'jest --watch',
  lint: 'eslint workspace/*.js',
  lint:fix: 'eslint workspace/*.js --fix',
  build: 'echo "No build required for this project"',
  serve: 'npx http-server workspace -p 8080'
};

// Mock A-Frame version author
global.AFRAME.versionAuthor = 'Thronglets Team';

// Mock A-Frame version license
global.AFRAME.versionLicense = 'MIT';

// Mock A-Frame version repository
global.AFRAME.versionRepository = 'https://github.com/thronglets/vr-practice-mode';

// Mock A-Frame version bugs
global.AFRAME.versionBugs = 'https://github.com/thronglets/vr-practice-mode/issues';

// Mock A-Frame version homepage
global.AFRAME.versionHomepage = 'https://github.com/thronglets/vr-practice-mode#readme';

// Mock A-Frame version jest
global.AFRAME.versionJest = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['./tests/setup.js'],
  testMatch: ['**/tests/**/*.test.js'],
  collectCoverageFrom: ['workspace/*.js'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};

// Mock A-Frame version description
global.AFRAME.versionDescription = 'VR Practice Mode for Thronglets - A virtual reality environment for interacting with Thronglets';

// Mock A-Frame version main
global.AFRAME.versionMain = 'workspace/vr_practice_mode.js';

// Mock A-Frame version name
global.AFRAME.versionName = 'thronglets-vr-practice-mode';

// Mock A-Frame version version
global.AFRAME.versionVersion = '1.0.0';

// Mock A-Frame version keywords
global.AFRAME.versionKeywords = ['vr', 'aframe', 'threejs', 'thronglets', 'practice-mode', 'webvr'];

// Mock A-Frame version author
global.AFRAME.versionAuthor = 'Thronglets Team';

// Mock A-Frame version license
global.AFRAME.versionLicense = 'MIT';

// Mock A-Frame version repository
global.AFRAME.versionRepository = 'https://github.com/thronglets/vr-practice-mode';

// Mock A-Frame version bugs
global.AFRAME.versionBugs = 'https://github.com/thronglets/vr-practice-mode/issues';

// Mock A-Frame version homepage
global.AFRAME.versionHomepage = 'https://github.com/thronglets/vr-practice-mode#readme';

// Mock A-Frame version jest
global.AFRAME.versionJest = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['./tests/setup.js'],
  testMatch: ['**/tests/**/*.test.js'],
  collectCoverageFrom: ['workspace/*.js'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};

// Mock A-Frame version description
global.AFRAME.versionDescription = 'VR Practice Mode for Thronglets - A virtual reality environment for interacting with Thronglets';

// Mock A-Frame version main
global.AFRAME.versionMain = 'workspace/vr_practice_mode.js';

// Mock A-Frame version name
global.AFRAME.versionName = 'thronglets-vr-practice-mode';

// Mock A-Frame version version
global.AFRAME.versionVersion = '1.0.0';
