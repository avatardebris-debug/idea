#!/usr/bin/env node
/**
 * Thronglets VR Practice Mode - Test Runner
 * Runs the test suite and reports results
 */

const fs = require('fs');
const path = require('path');

// Command line arguments
const args = process.argv.slice(2);
const watchMode = args.includes('--watch');
const verbose = args.includes('--verbose');
const coverage = args.includes('--coverage');

// Test results tracking
let totalTests = 0;
let passedTests = 0;
let failedTests = 0;
let testResults = [];

// Color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

/**
 * Simple assertion library
 */
const assert = {
  equal: (actual, expected, message) => {
    totalTests++;
    const passed = actual == expected;
    if (passed) {
      passedTests++;
    } else {
      failedTests++;
    }
    testResults.push({
      name: message || `Expected ${expected} but got ${actual}`,
      passed,
      actual,
      expected
    });
    if (verbose || !passed) {
      console.log(`  ${passed ? colors.green + '✓' : colors.red + '✗'} ${message || `Expected ${expected} but got ${actual}`}`);
    }
    return passed;
  },

  deepEqual: (actual, expected, message) => {
    totalTests++;
    const passed = JSON.stringify(actual) === JSON.stringify(expected);
    if (passed) {
      passedTests++;
    } else {
      failedTests++;
    }
    testResults.push({
      name: message || `Expected ${JSON.stringify(expected)} but got ${JSON.stringify(actual)}`,
      passed,
      actual,
      expected
    });
    if (verbose || !passed) {
      console.log(`  ${passed ? colors.green + '✓' : colors.red + '✗'} ${message || `Expected ${JSON.stringify(expected)} but got ${JSON.stringify(actual)}`}`);
    }
    return passed;
  },

  isTrue: (value, message) => {
    totalTests++;
    const passed = value === true;
    if (passed) {
      passedTests++;
    } else {
      failedTests++;
    }
    testResults.push({
      name: message || `Expected true but got ${value}`,
      passed,
      actual: value,
      expected: true
    });
    if (verbose || !passed) {
      console.log(`  ${passed ? colors.green + '✓' : colors.red + '✗'} ${message || `Expected true but got ${value}`}`);
    }
    return passed;
  },

  isFalse: (value, message) => {
    totalTests++;
    const passed = value === false;
    if (passed) {
      passedTests++;
    } else {
      failedTests++;
    }
    testResults.push({
      name: message || `Expected false but got ${value}`,
      passed,
      actual: value,
      expected: false
    });
    if (verbose || !passed) {
      console.log(`  ${passed ? colors.green + '✓' : colors.red + '✗'} ${message || `Expected false but got ${value}`}`);
    }
    return passed;
  },

  isNull: (value, message) => {
    totalTests++;
    const passed = value === null;
    if (passed) {
      passedTests++;
    } else {
      failedTests++;
    }
    testResults.push({
      name: message || `Expected null but got ${value}`,
      passed,
      actual: value,
      expected: null
    });
    if (verbose || !passed) {
      console.log(`  ${passed ? colors.green + '✓' : colors.red + '✗'} ${message || `Expected null but got ${value}`}`);
    }
    return passed;
  },

  isUndefined: (value, message) => {
    totalTests++;
    const passed = value === undefined;
    if (passed) {
      passedTests++;
    } else {
      failedTests++;
    }
    testResults.push({
      name: message || `Expected undefined but got ${value}`,
      passed,
      actual: value,
      expected: undefined
    });
    if (verbose || !passed) {
      console.log(`  ${passed ? colors.green + '✓' : colors.red + '✗'} ${message || `Expected undefined but got ${value}`}`);
    }
    return passed;
  },

  isDefined: (value, message) => {
    totalTests++;
    const passed = value !== undefined && value !== null;
    if (passed) {
      passedTests++;
    } else {
      failedTests++;
    }
    testResults.push({
      name: message || `Expected defined value but got ${value}`,
      passed,
      actual: value,
      expected: 'defined'
    });
    if (verbose || !passed) {
      console.log(`  ${passed ? colors.green + '✓' : colors.red + '✗'} ${message || `Expected defined value but got ${value}`}`);
    }
    return passed;
  },

  notEqual: (actual, expected, message) => {
    totalTests++;
    const passed = actual != expected;
    if (passed) {
      passedTests++;
    } else {
      failedTests++;
    }
    testResults.push({
      name: message || `Expected ${actual} to not equal ${expected}`,
      passed,
      actual,
      expected
    });
    if (verbose || !passed) {
      console.log(`  ${passed ? colors.green + '✓' : colors.red + '✗'} ${message || `Expected ${actual} to not equal ${expected}`}`);
    }
    return passed;
  },

  contains: (actual, expected, message) => {
    totalTests++;
    const passed = actual.includes(expected);
    if (passed) {
      passedTests++;
    } else {
      failedTests++;
    }
    testResults.push({
      name: message || `Expected ${actual} to contain ${expected}`,
      passed,
      actual,
      expected
    });
    if (verbose || !passed) {
      console.log(`  ${passed ? colors.green + '✓' : colors.red + '✗'} ${message || `Expected ${actual} to contain ${expected}`}`);
    }
    return passed;
  },

  greaterThan: (actual, expected, message) => {
    totalTests++;
    const passed = actual > expected;
    if (passed) {
      passedTests++;
    } else {
      failedTests++;
    }
    testResults.push({
      name: message || `Expected ${actual} to be greater than ${expected}`,
      passed,
      actual,
      expected
    });
    if (verbose || !passed) {
      console.log(`  ${passed ? colors.green + '✓' : colors.red + '✗'} ${message || `Expected ${actual} to be greater than ${expected}`}`);
    }
    return passed;
  }
};

// Mock globals for testing
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

// Import modules
const { VRState, Thronglet, Connection, VRPracticeMode, initThrongletsVR, closeDetailPanel, toggleNameplatesVisibility, toggleConnectionsVisibility, toggleHealthHalosVisibility, toggleDebugMode, teleportToThronglet, deselectThronglet, handleResize } = require('./vr_practice.js');

// Test suite
console.log(colors.cyan + '\n🧪 Thronglets VR Practice Mode - Test Suite' + colors.reset);
console.log('=' .repeat(60) + '\n');

// Helper function to run a test
function test(description, fn) {
  console.log(colors.blue + `  ${description}` + colors.reset);
  try {
    fn();
  } catch (error) {
    totalTests++;
    failedTests++;
    console.log(`    ${colors.red}✗ Error: ${error.message}` + colors.reset);
    testResults.push({
      name: description,
      passed: false,
      error: error.message
    });
  }
}

// Helper function to run an async test
async function asyncTest(description, fn) {
  console.log(colors.blue + `  ${description}` + colors.reset);
  try {
    await fn();
  } catch (error) {
    totalTests++;
    failedTests++;
    console.log(`    ${colors.red}✗ Error: ${error.message}` + colors.reset);
    testResults.push({
      name: description,
      passed: false,
      error: error.message
    });
  }
}

// Reset state helper
function resetState() {
  VRState.thronglets = [];
  VRState.connections = [];
  VRState.selectedThronglet = null;
  VRState.settings = {
    showNameplates: true,
    showConnections: true,
    showHealthHalos: true,
    debugMode: false
  };
  VRState.config = null;
  VRState.practiceMode = null;
}

// Create test thronglet helper
function createTestThronglet(overrides = {}) {
  const data = {
    id: '1',
    name: 'Test Thronglet',
    role: 'agent',
    color: '#ff0000',
    position: { x: 0, y: 0, z: 0 },
    health: 'healthy',
    mood: 'neutral',
    token_count: 100,
    uptime: 3600,
    last_seen: '2024-01-01T00:00:00Z',
    ...overrides
  };
  return new Thronglet(data);
}

// ==================== Thronglet Class Tests ====================
console.log(colors.yellow + '\n📦 Thronglet Class Tests' + colors.reset);

test('should create a thronglet with default values', () => {
  const data = {
    id: '1',
    name: 'Test Thronglet',
    role: 'agent',
    color: '#ff0000',
    position: { x: 0, y: 0, z: 0 },
    health: 'healthy',
    mood: 'neutral',
    token_count: 100,
    uptime: 3600,
    last_seen: '2024-01-01T00:00:00Z'
  };

  const thronglet = new Thronglet(data);

  assert.equal(thronglet.id, '1', 'id should be 1');
  assert.equal(thronglet.name, 'Test Thronglet', 'name should be Test Thronglet');
  assert.equal(thronglet.role, 'agent', 'role should be agent');
  assert.equal(thronglet.color, '#ff0000', 'color should be #ff0000');
  assert.equal(thronglet.health, 'healthy', 'health should be healthy');
  assert.equal(thronglet.mood, 'neutral', 'mood should be neutral');
  assert.equal(thronglet.tokenCount, 100, 'tokenCount should be 100');
});

test('should get health color correctly', () => {
  const healthy = new Thronglet({ id: '1', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
  const warning = new Thronglet({ id: '2', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'warning', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
  const critical = new Thronglet({ id: '3', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'critical', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });

  assert.equal(healthy.getHealthColor(), '#81c784', 'healthy should be green');
  assert.equal(warning.getHealthColor(), '#ffb74d', 'warning should be orange');
  assert.equal(critical.getHealthColor(), '#e57373', 'critical should be red');
});

test('should get health badge correctly', () => {
  const healthy = new Thronglet({ id: '1', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
  const warning = new Thronglet({ id: '2', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'warning', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
  const critical = new Thronglet({ id: '3', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'critical', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });

  assert.contains(healthy.getHealthBadge(), 'Healthy', 'healthy badge should contain Healthy');
  assert.contains(warning.getHealthBadge(), 'Warning', 'warning badge should contain Warning');
  assert.contains(critical.getHealthBadge(), 'Critical', 'critical badge should contain Critical');
});

test('should serialize to JSON correctly', () => {
  const thronglet = new Thronglet({
    id: '1',
    name: 'Test Thronglet',
    role: 'agent',
    color: '#ff0000',
    position: { x: 1, y: 2, z: 3 },
    health: 'healthy',
    mood: 'happy',
    token_count: 100,
    uptime: 3600,
    last_seen: '2024-01-01T00:00:00Z'
  });

  const json = thronglet.toJSON();

  assert.equal(json.id, '1', 'id should be 1');
  assert.equal(json.name, 'Test Thronglet', 'name should be Test Thronglet');
  assert.equal(json.role, 'agent', 'role should be agent');
  assert.equal(json.color, '#ff0000', 'color should be #ff0000');
  assert.deepEqual(json.position, { x: 1, y: 2, z: 3 }, 'position should match');
  assert.equal(json.health, 'healthy', 'health should be healthy');
  assert.equal(json.mood, 'happy', 'mood should be happy');
  assert.equal(json.token_count, 100, 'token_count should be 100');
  assert.equal(json.uptime, 3600, 'uptime should be 3600');
});

// ==================== Connection Class Tests ====================
console.log(colors.yellow + '\n🔗 Connection Class Tests' + colors.reset);

test('should create a connection with default values', () => {
  const fromThronglet = new Thronglet({ id: '1', name: 'Test 1', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
  const toThronglet = new Thronglet({ id: '2', name: 'Test 2', role: 'agent', color: '#00ff00', position: { x: 1, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });

  const data = {
    from: '1',
    to: '2',
    type: 'communication',
    color: '#0000ff',
    label: 'Test Connection'
  };

  const connection = new Connection(data, fromThronglet, toThronglet);

  assert.equal(connection.from, '1', 'from should be 1');
  assert.equal(connection.to, '2', 'to should be 2');
  assert.equal(connection.type, 'communication', 'type should be communication');
  assert.equal(connection.color, '#0000ff', 'color should be #0000ff');
  assert.equal(connection.label, 'Test Connection', 'label should be Test Connection');
  assert.equal(connection.fromThronglet, fromThronglet, 'fromThronglet should match');
  assert.equal(connection.toThronglet, toThronglet, 'toThronglet should match');
});

test('should serialize to JSON correctly', () => {
  const fromThronglet = new Thronglet({ id: '1', name: 'Test 1', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
  const toThronglet = new Thronglet({ id: '2', name: 'Test 2', role: 'agent', color: '#00ff00', position: { x: 1, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });

  const data = {
    from: '1',
    to: '2',
    type: 'communication',
    color: '#0000ff',
    label: 'Test Connection'
  };

  const connection = new Connection(data, fromThronglet, toThronglet);
  const json = connection.toJSON();

  assert.equal(json.from, '1', 'from should be 1');
  assert.equal(json.to, '2', 'to should be 2');
  assert.equal(json.type, 'communication', 'type should be communication');
  assert.equal(json.color, '#0000ff', 'color should be #0000ff');
  assert.equal(json.label, 'Test Connection', 'label should be Test Connection');
});

// ==================== VRState Tests ====================
console.log(colors.yellow + '\n📊 VRState Tests' + colors.reset);

test('should initialize with default state', () => {
  resetState();
  assert.deepEqual(VRState.thronglets, [], 'thronglets should be empty array');
  assert.deepEqual(VRState.connections, [], 'connections should be empty array');
  assert.isNull(VRState.selectedThronglet, 'selectedThronglet should be null');
  assert.isTrue(VRState.settings.showNameplates, 'showNameplates should be true');
  assert.isTrue(VRState.settings.showConnections, 'showConnections should be true');
  assert.isTrue(VRState.settings.showHealthHalos, 'showHealthHalos should be true');
  assert.isFalse(VRState.settings.debugMode, 'debugMode should be false');
});

// ==================== VRPracticeMode Class Tests ====================
console.log(colors.yellow + '\n🎮 VRPracticeMode Class Tests' + colors.reset);

test('should initialize successfully', async () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  assert.isDefined(practiceMode, 'practiceMode should be defined');
  assert.isDefined(practiceMode.scene, 'scene should be defined');
});

test('should load configuration', async () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  await practiceMode.loadConfiguration();
  assert.isDefined(VRState.config, 'config should be defined');
});

test('should create thronglets from configuration', async () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  await practiceMode.createThronglets();
  assert.greaterThan(VRState.thronglets.length, 0, 'should have thronglets');
});

test('should create connections from configuration', async () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  await practiceMode.createConnections();
  assert.greaterThan(VRState.connections.length, 0, 'should have connections');
});

test('should select a thronglet', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  const thronglet = createTestThronglet({ id: '1' });
  VRState.thronglets.push(thronglet);

  practiceMode.selectThronglet('1');
  assert.equal(VRState.selectedThronglet, thronglet, 'selectedThronglet should match');
});

test('should deselect a thronglet', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  const thronglet = createTestThronglet({ id: '1' });
  VRState.thronglets.push(thronglet);
  VRState.selectedThronglet = thronglet;

  practiceMode.deselectThronglet();
  assert.isNull(VRState.selectedThronglet, 'selectedThronglet should be null');
});

test('should teleport to a thronglet', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  const thronglet = createTestThronglet({ id: '1', position: { x: 10, y: 2, z: 5 } });
  VRState.thronglets.push(thronglet);

  practiceMode.teleportToThronglet(0);
  // The teleportation should have been called
});

test('should toggle nameplates visibility', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  practiceMode.toggleNameplates();
  assert.isFalse(VRState.settings.showNameplates, 'showNameplates should be false');

  practiceMode.toggleNameplates();
  assert.isTrue(VRState.settings.showNameplates, 'showNameplates should be true');
});

test('should toggle connections visibility', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  practiceMode.toggleConnections();
  assert.isFalse(VRState.settings.showConnections, 'showConnections should be false');

  practiceMode.toggleConnections();
  assert.isTrue(VRState.settings.showConnections, 'showConnections should be true');
});

test('should toggle health halos visibility', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  practiceMode.toggleHealthHalos();
  assert.isFalse(VRState.settings.showHealthHalos, 'showHealthHalos should be false');

  practiceMode.toggleHealthHalos();
  assert.isTrue(VRState.settings.showHealthHalos, 'showHealthHalos should be true');
});

test('should toggle debug mode', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  practiceMode.toggleDebug();
  assert.isTrue(VRState.settings.debugMode, 'debugMode should be true');

  practiceMode.toggleDebug();
  assert.isFalse(VRState.settings.debugMode, 'debugMode should be false');
});

test('should handle keyboard events', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  const thronglet = createTestThronglet({ id: '1' });
  VRState.thronglets.push(thronglet);

  // Test ESC key
  const escEvent = { key: 'Escape' };
  practiceMode.handleKeyboard(escEvent);
  assert.isNull(VRState.selectedThronglet, 'selectedThronglet should be null after ESC');
});

test('should update simulation', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  const thronglet = createTestThronglet({ id: '1' });
  VRState.thronglets.push(thronglet);

  practiceMode.updateSimulation();
  assert.isDefined(thronglet.lastSeen, 'lastSeen should be defined');
});

test('should check proximity alerts', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  const criticalThronglet = createTestThronglet({ id: '1', health: 'critical' });
  VRState.thronglets.push(criticalThronglet);

  practiceMode.checkProximityAlerts();
  // Should have detected critical thronglet
});

// ==================== Global Functions Tests ====================
console.log(colors.yellow + '\n🌐 Global Functions Tests' + colors.reset);

test('should initialize VR practice mode', () => {
  resetState();
  initThrongletsVR();
  assert.isDefined(VRState.practiceMode, 'practiceMode should be defined');
});

test('should close detail panel', () => {
  const panel = { classList: { add: () => {}, remove: () => {}, toggle: () => {} } };
  panel.classList.add('visible');
  closeDetailPanel();
  // Panel should have been hidden
});

test('should toggle nameplates visibility', () => {
  resetState();
  VRState.practiceMode = new VRPracticeMode();
  toggleNameplatesVisibility();
  assert.isFalse(VRState.settings.showNameplates, 'showNameplates should be false');
});

test('should toggle connections visibility', () => {
  resetState();
  VRState.practiceMode = new VRPracticeMode();
  toggleConnectionsVisibility();
  assert.isFalse(VRState.settings.showConnections, 'showConnections should be false');
});

test('should toggle health halos visibility', () => {
  resetState();
  VRState.practiceMode = new VRPracticeMode();
  toggleHealthHalosVisibility();
  assert.isFalse(VRState.settings.showHealthHalos, 'showHealthHalos should be false');
});

test('should toggle debug mode', () => {
  resetState();
  VRState.practiceMode = new VRPracticeMode();
  toggleDebugMode();
  assert.isTrue(VRState.settings.debugMode, 'debugMode should be true');
});

test('should teleport to thronglet', () => {
  resetState();
  VRState.practiceMode = new VRPracticeMode();
  const thronglet = createTestThronglet({ id: '1' });
  VRState.thronglets.push(thronglet);

  teleportToThronglet(0);
  // Should have attempted to teleport
});

test('should deselect thronglet', () => {
  resetState();
  VRState.practiceMode = new VRPracticeMode();
  const thronglet = createTestThronglet({ id: '1' });
  VRState.thronglets.push(thronglet);
  VRState.selectedThronglet = thronglet;

  deselectThronglet();
  assert.isNull(VRState.selectedThronglet, 'selectedThronglet should be null');
});

test('should handle resize', () => {
  resetState();
  VRState.practiceMode = new VRPracticeMode();
  handleResize();
  // Should not throw an error
});

// ==================== Edge Cases Tests ====================
console.log(colors.yellow + '\n⚠️ Edge Cases Tests' + colors.reset);

test('should handle empty configuration', async () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  VRState.config = null;
  await practiceMode.createThronglets();
  assert.equal(VRState.thronglets.length, 0, 'should have no thronglets');
});

test('should handle missing thronglet in selection', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  practiceMode.selectThronglet('nonexistent');
  assert.isNull(VRState.selectedThronglet, 'selectedThronglet should be null');
});

test('should handle invalid index in teleport', () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  practiceMode.teleportToThronglet(999);
  // Should not throw an error
});

test('should handle missing configuration file', async () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  VRState.config = null;
  await practiceMode.loadConfiguration();
  assert.isNull(VRState.config, 'config should be null');
});

// ==================== Integration Tests ====================
console.log(colors.yellow + '\n🔗 Integration Tests' + colors.reset);

test('should complete full workflow', async () => {
  resetState();
  const practiceMode = new VRPracticeMode();
  await practiceMode.init();

  assert.greaterThan(VRState.thronglets.length, 0, 'should have thronglets');
  assert.greaterThan(VRState.connections.length, 0, 'should have connections');

  // Select a thronglet
  const firstThronglet = VRState.thronglets[0];
  practiceMode.selectThronglet(firstThronglet.id);
  assert.equal(VRState.selectedThronglet, firstThronglet, 'selectedThronglet should match');

  // Deselect
  practiceMode.deselectThronglet();
  assert.isNull(VRState.selectedThronglet, 'selectedThronglet should be null');

  // Toggle settings
  practiceMode.toggleNameplates();
  practiceMode.toggleConnections();
  practiceMode.toggleHealthHalos();
  practiceMode.toggleDebug();

  // Update simulation
  practiceMode.updateSimulation();
});

// ==================== Test Results ====================
console.log('\n' + '='.repeat(60));
console.log(colors.cyan + '\n📊 Test Results' + colors.reset);
console.log('='.repeat(60));
console.log(`Total tests: ${totalTests}`);
console.log(`${colors.green}Passed: ${passedTests}${colors.reset}`);
console.log(`${colors.red}Failed: ${failedTests}${colors.reset}`);
console.log(`Success rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);

if (failedTests > 0) {
  console.log('\n' + colors.red + 'Failed tests:' + colors.reset);
  testResults.filter(r => !r.passed).forEach(result => {
    console.log(`  - ${result.name}`);
    if (result.error) {
      console.log(`    Error: ${result.error}`);
    }
  });
}

console.log('\n' + '='.repeat(60));

// Exit with appropriate code
process.exit(failedTests > 0 ? 1 : 0);
