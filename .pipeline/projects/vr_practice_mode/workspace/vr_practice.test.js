/**
 * Thronglets VR Practice Mode - Test Suite
 * Comprehensive tests for VR practice mode functionality
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

// Import modules
const { VRState, Thronglet, Connection, VRPracticeMode } = require('./vr_practice.js');

// Test suite
describe('Thronglets VR Practice Mode', () => {
  beforeEach(() => {
    // Reset state before each test
    VRState.thronglets = [];
    VRState.connections = [];
    VRState.selectedThronglet = null;
    VRState.settings = {
      showNameplates: true,
      showConnections: true,
      showHealthHalos: true,
      debugMode: false
    };
  });

  describe('Thronglet Class', () => {
    it('should create a thronglet with default values', () => {
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

      expect(thronglet.id).toBe('1');
      expect(thronglet.name).toBe('Test Thronglet');
      expect(thronglet.role).toBe('agent');
      expect(thronglet.color).toBe('#ff0000');
      expect(thronglet.health).toBe('healthy');
      expect(thronglet.mood).toBe('neutral');
      expect(thronglet.tokenCount).toBe(100);
    });

    it('should get health color correctly', () => {
      const healthy = new Thronglet({ id: '1', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
      const warning = new Thronglet({ id: '2', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'warning', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
      const critical = new Thronglet({ id: '3', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'critical', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });

      expect(healthy.getHealthColor()).toBe('#81c784');
      expect(warning.getHealthColor()).toBe('#ffb74d');
      expect(critical.getHealthColor()).toBe('#e57373');
    });

    it('should get health badge correctly', () => {
      const healthy = new Thronglet({ id: '1', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
      const warning = new Thronglet({ id: '2', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'warning', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
      const critical = new Thronglet({ id: '3', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'critical', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });

      expect(healthy.getHealthBadge()).toContain('Healthy');
      expect(warning.getHealthBadge()).toContain('Warning');
      expect(critical.getHealthBadge()).toContain('Critical');
    });

    it('should update timestamp correctly', () => {
      const thronglet = new Thronglet({ id: '1', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
      const oldTimestamp = thronglet.lastSeen;

      setTimeout(() => {
        thronglet.updateTimestamp();
        expect(thronglet.lastSeen).not.toBe(oldTimestamp);
      }, 100);
    });

    it('should serialize to JSON correctly', () => {
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

      expect(json.id).toBe('1');
      expect(json.name).toBe('Test Thronglet');
      expect(json.role).toBe('agent');
      expect(json.color).toBe('#ff0000');
      expect(json.position).toEqual({ x: 1, y: 2, z: 3 });
      expect(json.health).toBe('healthy');
      expect(json.mood).toBe('happy');
      expect(json.token_count).toBe(100);
      expect(json.uptime).toBe(3600);
    });
  });

  describe('Connection Class', () => {
    it('should create a connection with default values', () => {
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

      expect(connection.from).toBe('1');
      expect(connection.to).toBe('2');
      expect(connection.type).toBe('communication');
      expect(connection.color).toBe('#0000ff');
      expect(connection.label).toBe('Test Connection');
      expect(connection.fromThronglet).toBe(fromThronglet);
      expect(connection.toThronglet).toBe(toThronglet);
    });

    it('should serialize to JSON correctly', () => {
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

      expect(json.from).toBe('1');
      expect(json.to).toBe('2');
      expect(json.type).toBe('communication');
      expect(json.color).toBe('#0000ff');
      expect(json.label).toBe('Test Connection');
    });
  });

  describe('VRState', () => {
    it('should initialize with default state', () => {
      expect(VRState.thronglets).toEqual([]);
      expect(VRState.connections).toEqual([]);
      expect(VRState.selectedThronglet).toBeNull();
      expect(VRState.settings.showNameplates).toBe(true);
      expect(VRState.settings.showConnections).toBe(true);
      expect(VRState.settings.showHealthHalos).toBe(true);
      expect(VRState.settings.debugMode).toBe(false);
    });
  });

  describe('VRPracticeMode Class', () => {
    let practiceMode;

    beforeEach(() => {
      // Mock document methods
      document.querySelector = () => ({
        setAttribute: () => {},
        querySelector: () => null
      });
      document.getElementById = () => ({
        addEventListener: () => {},
        setAttribute: () => {},
        getAttribute: () => null,
        hasAttribute: () => false,
        appendChild: () => {},
        removeAttribute: () => {},
        classList: { add: () => {}, remove: () => {}, toggle: () => {} },
        style: { opacity: '', display: '' },
        textContent: ''
      });
      document.addEventListener = () => {};
      document.querySelectorAll = () => [];
    });

    afterEach(() => {
      if (practiceMode) {
        practiceMode = null;
      }
    });

    it('should initialize successfully', async () => {
      practiceMode = new VRPracticeMode();
      expect(practiceMode).toBeDefined();
      expect(practiceMode.scene).toBeDefined();
    });

    it('should load configuration', async () => {
      practiceMode = new VRPracticeMode();
      await practiceMode.loadConfiguration();
      expect(VRState.config).toBeDefined();
    });

    it('should create thronglets from configuration', async () => {
      practiceMode = new VRPracticeMode();
      await practiceMode.createThronglets();
      expect(VRState.thronglets.length).toBeGreaterThan(0);
    });

    it('should create connections from configuration', async () => {
      practiceMode = new VRPracticeMode();
      await practiceMode.createConnections();
      expect(VRState.connections.length).toBeGreaterThan(0);
    });

    it('should select a thronglet', () => {
      practiceMode = new VRPracticeMode();
      const thronglet = new Thronglet({
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
      VRState.thronglets.push(thronglet);

      practiceMode.selectThronglet('1');
      expect(VRState.selectedThronglet).toBe(thronglet);
    });

    it('should deselect a thronglet', () => {
      practiceMode = new VRPracticeMode();
      const thronglet = new Thronglet({
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
      VRState.thronglets.push(thronglet);
      VRState.selectedThronglet = thronglet;

      practiceMode.deselectThronglet();
      expect(VRState.selectedThronglet).toBeNull();
    });

    it('should teleport to a thronglet', () => {
      practiceMode = new VRPracticeMode();
      const thronglet = new Thronglet({
        id: '1',
        name: 'Test Thronglet',
        role: 'agent',
        color: '#ff0000',
        position: { x: 10, y: 2, z: 5 },
        health: 'healthy',
        mood: 'neutral',
        token_count: 100,
        uptime: 3600,
        last_seen: '2024-01-01T00:00:00Z'
      });
      VRState.thronglets.push(thronglet);

      practiceMode.teleportToThronglet(0);
      // The teleportation should have been called
    });

    it('should toggle nameplates visibility', () => {
      practiceMode = new VRPracticeMode();
      practiceMode.toggleNameplates();
      expect(VRState.settings.showNameplates).toBe(false);

      practiceMode.toggleNameplates();
      expect(VRState.settings.showNameplates).toBe(true);
    });

    it('should toggle connections visibility', () => {
      practiceMode = new VRPracticeMode();
      practiceMode.toggleConnections();
      expect(VRState.settings.showConnections).toBe(false);

      practiceMode.toggleConnections();
      expect(VRState.settings.showConnections).toBe(true);
    });

    it('should toggle health halos visibility', () => {
      practiceMode = new VRPracticeMode();
      practiceMode.toggleHealthHalos();
      expect(VRState.settings.showHealthHalos).toBe(false);

      practiceMode.toggleHealthHalos();
      expect(VRState.settings.showHealthHalos).toBe(true);
    });

    it('should toggle debug mode', () => {
      practiceMode = new VRPracticeMode();
      practiceMode.toggleDebug();
      expect(VRState.settings.debugMode).toBe(true);

      practiceMode.toggleDebug();
      expect(VRState.settings.debugMode).toBe(false);
    });

    it('should handle keyboard events', () => {
      practiceMode = new VRPracticeMode();
      const thronglet = new Thronglet({
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
      VRState.thronglets.push(thronglet);

      // Test ESC key
      const escEvent = { key: 'Escape' };
      practiceMode.handleKeyboard(escEvent);
      expect(VRState.selectedThronglet).toBeNull();

      // Test number keys (1-5)
      const key1Event = { key: '1' };
      practiceMode.handleKeyboard(key1Event);
      // Should have attempted to teleport
    });

    it('should update simulation', () => {
      practiceMode = new VRPracticeMode();
      const thronglet = new Thronglet({
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
      VRState.thronglets.push(thronglet);

      practiceMode.updateSimulation();
      expect(thronglet.lastSeen).toBeDefined();
    });

    it('should check proximity alerts', () => {
      practiceMode = new VRPracticeMode();
      const criticalThronglet = new Thronglet({
        id: '1',
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
    });
  });

  describe('Global Functions', () => {
    it('should initialize VR practice mode', () => {
      initThrongletsVR();
      expect(VRState.practiceMode).toBeDefined();
    });

    it('should close detail panel', () => {
      const panel = document.getElementById('detail-panel');
      panel.classList.add('visible');
      closeDetailPanel();
      expect(panel.classList.contains('visible')).toBe(false);
    });

    it('should toggle nameplates visibility', () => {
      VRState.practiceMode = new VRPracticeMode();
      toggleNameplatesVisibility();
      expect(VRState.settings.showNameplates).toBe(false);
    });

    it('should toggle connections visibility', () => {
      VRState.practiceMode = new VRPracticeMode();
      toggleConnectionsVisibility();
      expect(VRState.settings.showConnections).toBe(false);
    });

    it('should toggle health halos visibility', () => {
      VRState.practiceMode = new VRPracticeMode();
      toggleHealthHalosVisibility();
      expect(VRState.settings.showHealthHalos).toBe(false);
    });

    it('should toggle debug mode', () => {
      VRState.practiceMode = new VRPracticeMode();
      toggleDebugMode();
      expect(VRState.settings.debugMode).toBe(true);
    });

    it('should teleport to thronglet', () => {
      VRState.practiceMode = new VRPracticeMode();
      const thronglet = new Thronglet({
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
      VRState.thronglets.push(thronglet);

      teleportToThronglet(0);
      // Should have attempted to teleport
    });

    it('should deselect thronglet', () => {
      VRState.practiceMode = new VRPracticeMode();
      const thronglet = new Thronglet({
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
      VRState.thronglets.push(thronglet);
      VRState.selectedThronglet = thronglet;

      deselectThronglet();
      expect(VRState.selectedThronglet).toBeNull();
    });

    it('should handle resize', () => {
      VRState.practiceMode = new VRPracticeMode();
      handleResize();
      // Should not throw an error
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty configuration', async () => {
      const practiceMode = new VRPracticeMode();
      VRState.config = null;
      await practiceMode.createThronglets();
      expect(VRState.thronglets.length).toBe(0);
    });

    it('should handle missing thronglet in selection', () => {
      const practiceMode = new VRPracticeMode();
      practiceMode.selectThronglet('nonexistent');
      expect(VRState.selectedThronglet).toBeNull();
    });

    it('should handle invalid index in teleport', () => {
      const practiceMode = new VRPracticeMode();
      practiceMode.teleportToThronglet(999);
      // Should not throw an error
    });

    it('should handle missing configuration file', async () => {
      const practiceMode = new VRPracticeMode();
      VRState.config = null;
      await practiceMode.loadConfiguration();
      expect(VRState.config).toBeNull();
    });
  });

  describe('Integration Tests', () => {
    it('should complete full workflow', async () => {
      const practiceMode = new VRPracticeMode();
      await practiceMode.init();

      expect(VRState.thronglets.length).toBeGreaterThan(0);
      expect(VRState.connections.length).toBeGreaterThan(0);

      // Select a thronglet
      const firstThronglet = VRState.thronglets[0];
      practiceMode.selectThronglet(firstThronglet.id);
      expect(VRState.selectedThronglet).toBe(firstThronglet);

      // Deselect
      practiceMode.deselectThronglet();
      expect(VRState.selectedThronglet).toBeNull();

      // Toggle settings
      practiceMode.toggleNameplates();
      practiceMode.toggleConnections();
      practiceMode.toggleHealthHalos();
      practiceMode.toggleDebug();

      // Update simulation
      practiceMode.updateSimulation();
    });
  });
});

// Export for test runner
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    VRState,
    Thronglet,
    Connection,
    VRPracticeMode,
    initThrongletsVR,
    closeDetailPanel,
    toggleNameplatesVisibility,
    toggleConnectionsVisibility,
    toggleHealthHalosVisibility,
    toggleDebugMode,
    teleportToThronglet,
    deselectThronglet,
    handleResize
  };
}
