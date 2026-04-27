/**
 * Thronglets VR Practice Mode - Test Runner
 * Executes test suite and reports results
 */

const fs = require('fs');
const path = require('path');

// Test results tracking
const testResults = {
  passed: 0,
  failed: 0,
  total: 0,
  tests: []
};

// Colors for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

// Helper functions
function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logSuccess(message) {
  log(message, 'green');
}

function logError(message) {
  log(message, 'red');
}

function logWarning(message) {
  log(message, 'yellow');
}

function logInfo(message) {
  log(message, 'blue');
}

function logDebug(message) {
  log(message, 'cyan');
}

// Test assertion functions
function assertEqual(actual, expected, message) {
  testResults.total++;
  const passed = actual === expected;
  
  if (passed) {
    testResults.passed++;
    logSuccess(`✓ ${message}`);
  } else {
    testResults.failed++;
    logError(`✗ ${message}`);
    logError(`  Expected: ${expected}`);
    logError(`  Actual: ${actual}`);
  }
  
  testResults.tests.push({
    name: message,
    passed,
    expected,
    actual
  });
  
  return passed;
}

function assertNotEqual(actual, expected, message) {
  testResults.total++;
  const passed = actual !== expected;
  
  if (passed) {
    testResults.passed++;
    logSuccess(`✓ ${message}`);
  } else {
    testResults.failed++;
    logError(`✗ ${message}`);
    logError(`  Expected: ${expected}`);
    logError(`  Actual: ${actual}`);
  }
  
  testResults.tests.push({
    name: message,
    passed,
    expected,
    actual
  });
  
  return passed;
}

function assertTrue(actual, message) {
  testResults.total++;
  const passed = Boolean(actual);
  
  if (passed) {
    testResults.passed++;
    logSuccess(`✓ ${message}`);
  } else {
    testResults.failed++;
    logError(`✗ ${message}`);
    logError(`  Expected: true`);
    logError(`  Actual: ${actual}`);
  }
  
  testResults.tests.push({
    name: message,
    passed,
    expected: true,
    actual
  });
  
  return passed;
}

function assertFalse(actual, message) {
  testResults.total++;
  const passed = !Boolean(actual);
  
  if (passed) {
    testResults.passed++;
    logSuccess(`✓ ${message}`);
  } else {
    testResults.failed++;
    logError(`✗ ${message}`);
    logError(`  Expected: false`);
    logError(`  Actual: ${actual}`);
  }
  
  testResults.tests.push({
    name: message,
    passed,
    expected: false,
    actual
  });
  
  return passed;
}

function assertNotNull(actual, message) {
  testResults.total++;
  const passed = actual !== null && actual !== undefined;
  
  if (passed) {
    testResults.passed++;
    logSuccess(`✓ ${message}`);
  } else {
    testResults.failed++;
    logError(`✗ ${message}`);
    logError(`  Expected: not null/undefined`);
    logError(`  Actual: ${actual}`);
  }
  
  testResults.tests.push({
    name: message,
    passed,
    expected: 'not null/undefined',
    actual
  });
  
  return passed;
}

function assertNull(actual, message) {
  testResults.total++;
  const passed = actual === null || actual === undefined;
  
  if (passed) {
    testResults.passed++;
    logSuccess(`✓ ${message}`);
  } else {
    testResults.failed++;
    logError(`✗ ${message}`);
    logError(`  Expected: null/undefined`);
    logError(`  Actual: ${actual}`);
  }
  
  testResults.tests.push({
    name: message,
    passed,
    expected: 'null/undefined',
    actual
  });
  
  return passed;
}

function assertArrayLength(actual, expected, message) {
  testResults.total++;
  const passed = Array.isArray(actual) && actual.length === expected;
  
  if (passed) {
    testResults.passed++;
    logSuccess(`✓ ${message}`);
  } else {
    testResults.failed++;
    logError(`✗ ${message}`);
    logError(`  Expected length: ${expected}`);
    logError(`  Actual length: ${Array.isArray(actual) ? actual.length : 'N/A'}`);
  }
  
  testResults.tests.push({
    name: message,
    passed,
    expected,
    actual
  });
  
  return passed;
}

function assertContains(actual, expected, message) {
  testResults.total++;
  const passed = Array.isArray(actual) && actual.includes(expected);
  
  if (passed) {
    testResults.passed++;
    logSuccess(`✓ ${message}`);
  } else {
    testResults.failed++;
    logError(`✗ ${message}`);
    logError(`  Expected to contain: ${expected}`);
    logError(`  Actual: ${actual}`);
  }
  
  testResults.tests.push({
    name: message,
    passed,
    expected,
    actual
  });
  
  return passed;
}

function assertStringContains(actual, expected, message) {
  testResults.total++;
  const passed = typeof actual === 'string' && actual.includes(expected);
  
  if (passed) {
    testResults.passed++;
    logSuccess(`✓ ${message}`);
  } else {
    testResults.failed++;
    logError(`✗ ${message}`);
    logError(`  Expected to contain: ${expected}`);
    logError(`  Actual: ${actual}`);
  }
  
  testResults.tests.push({
    name: message,
    passed,
    expected,
    actual
  });
  
  return passed;
}

// Mock environment setup
function setupMockEnvironment() {
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
}

// Test suite execution
function runTestSuite() {
  logInfo('========================================');
  logInfo('Thronglets VR Practice Mode - Test Suite');
  logInfo('========================================\n');

  setupMockEnvironment();

  // Import modules
  const { VRState, Thronglet, Connection, VRPracticeMode } = require('./vr_practice.js');

  logInfo('Running Thronglet Class Tests...\n');
  runThrongletTests(VRState, Thronglet);

  logInfo('\nRunning Connection Class Tests...\n');
  runConnectionTests(VRState, Thronglet, Connection);

  logInfo('\nRunning VRState Tests...\n');
  runVRStateTests(VRState);

  logInfo('\nRunning VRPracticeMode Class Tests...\n');
  runVRPracticeModeTests(VRState, Thronglet, Connection, VRPracticeMode);

  logInfo('\nRunning Global Functions Tests...\n');
  runGlobalFunctionsTests(VRState, Thronglet, VRPracticeMode);

  logInfo('\nRunning Edge Cases Tests...\n');
  runEdgeCaseTests(VRState, Thronglet, VRPracticeMode);

  logInfo('\nRunning Integration Tests...\n');
  runIntegrationTests(VRState, Thronglet, VRPracticeMode);

  // Print summary
  printSummary();
}

function runThrongletTests(VRState, Thronglet) {
  // Test 1: Create thronglet with default values
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
  assertEqual(thronglet.id, '1', 'Thronglet ID should be "1"');
  assertEqual(thronglet.name, 'Test Thronglet', 'Thronglet name should be "Test Thronglet"');
  assertEqual(thronglet.role, 'agent', 'Thronglet role should be "agent"');
  assertEqual(thronglet.color, '#ff0000', 'Thronglet color should be "#ff0000"');
  assertEqual(thronglet.health, 'healthy', 'Thronglet health should be "healthy"');
  assertEqual(thronglet.mood, 'neutral', 'Thronglet mood should be "neutral"');
  assertEqual(thronglet.tokenCount, 100, 'Thronglet token count should be 100');

  // Test 2: Get health color
  const healthy = new Thronglet({ ...data, id: '2', health: 'healthy' });
  const warning = new Thronglet({ ...data, id: '3', health: 'warning' });
  const critical = new Thronglet({ ...data, id: '4', health: 'critical' });

  assertEqual(healthy.getHealthColor(), '#81c784', 'Healthy thronglet health color should be green');
  assertEqual(warning.getHealthColor(), '#ffb74d', 'Warning thronglet health color should be orange');
  assertEqual(critical.getHealthColor(), '#e57373', 'Critical thronglet health color should be red');

  // Test 3: Get health badge
  const healthyBadge = healthy.getHealthBadge();
  const warningBadge = warning.getHealthBadge();
  const criticalBadge = critical.getHealthBadge();

  assertStringContains(healthyBadge, 'Healthy', 'Healthy badge should contain "Healthy"');
  assertStringContains(warningBadge, 'Warning', 'Warning badge should contain "Warning"');
  assertStringContains(criticalBadge, 'Critical', 'Critical badge should contain "Critical"');

  // Test 4: Update timestamp
  const oldTimestamp = thronglet.lastSeen;
  thronglet.updateTimestamp();
  assertTrue(thronglet.lastSeen !== oldTimestamp, 'Timestamp should be updated');

  // Test 5: Serialize to JSON
  const json = thronglet.toJSON();
  assertEqual(json.id, '1', 'JSON ID should be "1"');
  assertEqual(json.name, 'Test Thronglet', 'JSON name should be "Test Thronglet"');
  assertEqual(json.role, 'agent', 'JSON role should be "agent"');
  assertEqual(json.color, '#ff0000', 'JSON color should be "#ff0000"');
  assertEqual(json.position.x, 0, 'JSON position x should be 0');
  assertEqual(json.position.y, 0, 'JSON position y should be 0');
  assertEqual(json.position.z, 0, 'JSON position z should be 0');
  assertEqual(json.health, 'healthy', 'JSON health should be "healthy"');
  assertEqual(json.mood, 'neutral', 'JSON mood should be "neutral"');
  assertEqual(json.token_count, 100, 'JSON token_count should be 100');
  assertEqual(json.uptime, 3600, 'JSON uptime should be 3600');
}

function runConnectionTests(VRState, Thronglet, Connection) {
  const fromThronglet = new Thronglet({
    id: '1',
    name: 'Test 1',
    role: 'agent',
    color: '#ff0000',
    position: { x: 0, y: 0, z: 0 },
    health: 'healthy',
    mood: 'neutral',
    token_count: 100,
    uptime: 3600,
    last_seen: '2024-01-01T00:00:00Z'
  });

  const toThronglet = new Thronglet({
    id: '2',
    name: 'Test 2',
    role: 'agent',
    color: '#00ff00',
    position: { x: 1, y: 0, z: 0 },
    health: 'healthy',
    mood: 'neutral',
    token_count: 100,
    uptime: 3600,
    last_seen: '2024-01-01T00:00:00Z'
  });

  const data = {
    from: '1',
    to: '2',
    type: 'communication',
    color: '#0000ff',
    label: 'Test Connection'
  };

  const connection = new Connection(data, fromThronglet, toThronglet);

  assertEqual(connection.from, '1', 'Connection from should be "1"');
  assertEqual(connection.to, '2', 'Connection to should be "2"');
  assertEqual(connection.type, 'communication', 'Connection type should be "communication"');
  assertEqual(connection.color, '#0000ff', 'Connection color should be "#0000ff"');
  assertEqual(connection.label, 'Test Connection', 'Connection label should be "Test Connection"');
  assertEqual(connection.fromThronglet, fromThronglet, 'Connection fromThronglet should match');
  assertEqual(connection.toThronglet, toThronglet, 'Connection toThronglet should match');

  // Test serialization
  const json = connection.toJSON();
  assertEqual(json.from, '1', 'JSON from should be "1"');
  assertEqual(json.to, '2', 'JSON to should be "2"');
  assertEqual(json.type, 'communication', 'JSON type should be "communication"');
  assertEqual(json.color, '#0000ff', 'JSON color should be "#0000ff"');
  assertEqual(json.label, 'Test Connection', 'JSON label should be "Test Connection"');
}

function runVRStateTests(VRState) {
  // Reset state
  VRState.thronglets = [];
  VRState.connections = [];
  VRState.selectedThronglet = null;
  VRState.settings = {
    showNameplates: true,
    showConnections: true,
    showHealthHalos: true,
    debugMode: false
  };

  assertArrayLength(VRState.thronglets, 0, 'VRState thronglets should be empty');
  assertArrayLength(VRState.connections, 0, 'VRState connections should be empty');
  assertNull(VRState.selectedThronglet, 'VRState selectedThronglet should be null');
  assertTrue(VRState.settings.showNameplates, 'VRState showNameplates should be true');
  assertTrue(VRState.settings.showConnections, 'VRState showConnections should be true');
  assertTrue(VRState.settings.showHealthHalos, 'VRState showHealthHalos should be true');
  assertFalse(VRState.settings.debugMode, 'VRState debugMode should be false');
}

function runVRPracticeModeTests(VRState, Thronglet, Connection, VRPracticeMode) {
  const practiceMode = new VRPracticeMode();

  assertNotNull(practiceMode, 'VRPracticeMode instance should be created');
  assertNotNull(practiceMode.scene, 'VRPracticeMode scene should be defined');

  // Test load configuration
  VRState.config = null;
  practiceMode.loadConfiguration();
  // Configuration should be loaded (or remain null if not found)

  // Test create thronglets
  VRState.config = {
    thronglets: [
      {
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
      }
    ],
    connections: []
  };

  practiceMode.createThronglets();
  assertArrayLength(VRState.thronglets, 1, 'Should have 1 thronglet after creation');

  // Test create connections
  const fromThronglet = VRState.thronglets[0];
  const toThronglet = new Thronglet({
    id: '2',
    name: 'Test 2',
    role: 'agent',
    color: '#00ff00',
    position: { x: 1, y: 0, z: 0 },
    health: 'healthy',
    mood: 'neutral',
    token_count: 100,
    uptime: 3600,
    last_seen: '2024-01-01T00:00:00Z'
  });
  VRState.thronglets.push(toThronglet);

  VRState.config.connections = [
    {
      from: '1',
      to: '2',
      type: 'communication',
      color: '#0000ff',
      label: 'Test Connection'
    }
  ];

  practiceMode.createConnections();
  assertArrayLength(VRState.connections, 1, 'Should have 1 connection after creation');

  // Test select thronglet
  practiceMode.selectThronglet('1');
  assertNotNull(VRState.selectedThronglet, 'Selected thronglet should not be null');
  assertEqual(VRState.selectedThronglet.id, '1', 'Selected thronglet ID should be "1"');

  // Test deselect thronglet
  practiceMode.deselectThronglet();
  assertNull(VRState.selectedThronglet, 'Selected thronglet should be null after deselect');

  // Test teleport to thronglet
  const testThronglet = new Thronglet({
    id: '3',
    name: 'Test Thronglet 3',
    role: 'agent',
    color: '#ff0000',
    position: { x: 10, y: 2, z: 5 },
    health: 'healthy',
    mood: 'neutral',
    token_count: 100,
    uptime: 3600,
    last_seen: '2024-01-01T00:00:00Z'
  });
  VRState.thronglets.push(testThronglet);

  practiceMode.teleportToThronglet(2);
  // Should have attempted to teleport

  // Test toggle nameplates
  practiceMode.toggleNameplates();
  assertFalse(VRState.settings.showNameplates, 'showNameplates should be false after toggle');

  practiceMode.toggleNameplates();
  assertTrue(VRState.settings.showNameplates, 'showNameplates should be true after toggle');

  // Test toggle connections
  practiceMode.toggleConnections();
  assertFalse(VRState.settings.showConnections, 'showConnections should be false after toggle');

  practiceMode.toggleConnections();
  assertTrue(VRState.settings.showConnections, 'showConnections should be true after toggle');

  // Test toggle health halos
  practiceMode.toggleHealthHalos();
  assertFalse(VRState.settings.showHealthHalos, 'showHealthHalos should be false after toggle');

  practiceMode.toggleHealthHalos();
  assertTrue(VRState.settings.showHealthHalos, 'showHealthHalos should be true after toggle');

  // Test toggle debug mode
  practiceMode.toggleDebug();
  assertTrue(VRState.settings.debugMode, 'debugMode should be true after toggle');

  practiceMode.toggleDebug();
  assertFalse(VRState.settings.debugMode, 'debugMode should be false after toggle');

  // Test keyboard events
  const escEvent = { key: 'Escape' };
  practiceMode.handleKeyboard(escEvent);
  assertNull(VRState.selectedThronglet, 'Selected thronglet should be null after ESC');

  const key1Event = { key: '1' };
  practiceMode.handleKeyboard(key1Event);
  // Should have attempted to teleport

  // Test update simulation
  const thronglet = new Thronglet({
    id: '4',
    name: 'Test Thronglet 4',
    role: 'agent',
    color: '#ff0000',
    position: { x: 0, y: 0, z: 0 },
    health: 'healthy',
    mood: 'neutral',
    token_count: 100,
    uptime: 3600,
    last_seen: '2024-01-01T00:00:00Z'
  });
  VRState.thronglets.push(thronglet);

  practiceMode.updateSimulation();
  assertNotNull(thronglet.lastSeen, 'Thronglet lastSeen should be updated');

  // Test check proximity alerts
  const criticalThronglet = new Thronglet({
    id: '5',
    name: 'Critical Thronglet',
    role: 'agent',
    color: '#ff0000',
    position: { x: 0, y: 0, z: 0 },
    health: 'critical',
    mood: 'neutral',
    token_count: 100,
    uptime: 3600,
    last_seen: '2024-01-01T00:00:00Z'
  });
  VRState.thronglets.push(criticalThronglet);

  practiceMode.checkProximityAlerts();
  // Should have detected critical thronglet
}

function runGlobalFunctionsTests(VRState, Thronglet, VRPracticeMode) {
  // Test initThrongletsVR
  initThrongletsVR();
  assertNotNull(VRState.practiceMode, 'VRState.practiceMode should be defined');

  // Test closeDetailPanel
  const panel = document.getElementById('detail-panel');
  panel.classList.add('visible');
  closeDetailPanel();
  assertFalse(panel.classList.contains('visible'), 'Panel should not be visible after close');

  // Test toggleNameplatesVisibility
  VRState.practiceMode = new VRPracticeMode();
  toggleNameplatesVisibility();
  assertFalse(VRState.settings.showNameplates, 'showNameplates should be false');

  // Test toggleConnectionsVisibility
  toggleConnectionsVisibility();
  assertFalse(VRState.settings.showConnections, 'showConnections should be false');

  // Test toggleHealthHalosVisibility
  toggleHealthHalosVisibility();
  assertFalse(VRState.settings.showHealthHalos, 'showHealthHalos should be false');

  // Test toggleDebugMode
  toggleDebugMode();
  assertTrue(VRState.settings.debugMode, 'debugMode should be true');

  // Test teleportToThronglet
  const testThronglet = new Thronglet({
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
  });
  VRState.thronglets.push(testThronglet);

  teleportToThronglet(0);
  // Should have attempted to teleport

  // Test deselectThronglet
  VRState.selectedThronglet = testThronglet;
  deselectThronglet();
  assertNull(VRState.selectedThronglet, 'Selected thronglet should be null');

  // Test handleResize
  handleResize();
  // Should not throw an error
}

function runEdgeCaseTests(VRState, Thronglet, VRPracticeMode) {
  // Test empty configuration
  const practiceMode = new VRPracticeMode();
  VRState.config = null;
  practiceMode.createThronglets();
  assertArrayLength(VRState.thronglets, 0, 'Should have 0 thronglets with empty config');

  // Test missing thronglet in selection
  const practiceMode2 = new VRPracticeMode();
  practiceMode2.selectThronglet('nonexistent');
  assertNull(VRState.selectedThronglet, 'Selected thronglet should be null for nonexistent ID');

  // Test invalid index in teleport
  const practiceMode3 = new VRPracticeMode();
  practiceMode3.teleportToThronglet(999);
  // Should not throw an error

  // Test missing configuration file
  const practiceMode4 = new VRPracticeMode();
  VRState.config = null;
  practiceMode4.loadConfiguration();
  // Configuration should remain null
}

function runIntegrationTests(VRState, Thronglet, VRPracticeMode) {
  const practiceMode = new VRPracticeMode();
  practiceMode.init();

  assertArrayLength(VRState.thronglets, 0, 'Should have 0 thronglets (mocked)');
  assertArrayLength(VRState.connections, 0, 'Should have 0 connections (mocked)');

  // Select a thronglet
  const firstThronglet = new Thronglet({
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
  });
  VRState.thronglets.push(firstThronglet);

  practiceMode.selectThronglet(firstThronglet.id);
  assertNotNull(VRState.selectedThronglet, 'Selected thronglet should not be null');
  assertEqual(VRState.selectedThronglet.id, '1', 'Selected thronglet ID should be "1"');

  // Deselect
  practiceMode.deselectThronglet();
  assertNull(VRState.selectedThronglet, 'Selected thronglet should be null after deselect');

  // Toggle settings
  practiceMode.toggleNameplates();
  practiceMode.toggleConnections();
  practiceMode.toggleHealthHalos();
  practiceMode.toggleDebug();

  // Update simulation
  practiceMode.updateSimulation();
  // Should complete without errors
}

function printSummary() {
  logInfo('\n========================================');
  logInfo('Test Summary');
  logInfo('========================================');
  
  const percentage = testResults.total > 0 
    ? ((testResults.passed / testResults.total) * 100).toFixed(1) 
    : 0;
  
  logInfo(`Total Tests: ${testResults.total}`);
  logSuccess(`Passed: ${testResults.passed}`);
  logError(`Failed: ${testResults.failed}`);
  logInfo(`Success Rate: ${percentage}%`);
  
  if (testResults.failed > 0) {
    logInfo('\nFailed Tests:');
    testResults.tests.forEach(test => {
      if (!test.passed) {
        logError(`  - ${test.name}`);
        logError(`    Expected: ${test.expected}`);
        logError(`    Actual: ${test.actual}`);
      }
    });
  }
  
  logInfo('\n========================================');
  
  if (testResults.failed === 0) {
    logSuccess('All tests passed! ✓');
    process.exit(0);
  } else {
    logError(`${testResults.failed} test(s) failed! ✗`);
    process.exit(1);
  }
}

// Run test suite
runTestSuite();
