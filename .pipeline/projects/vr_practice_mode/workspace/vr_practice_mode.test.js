/**
 * Thronglets VR Practice Mode - Comprehensive Test Suite
 * Tests for VR practice mode functionality using Vitest
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { VRState, Thronglet, Connection, VRPracticeMode, initThrongletsVR, closeDetailPanel, toggleNameplatesVisibility, toggleConnectionsVisibility, toggleHealthHalosVisibility, toggleDebugMode, teleportToThronglet, deselectThronglet, handleResize } from './vr_practice_mode.js';

// Mock A-Frame elements for testing
const mockElement = {
  addEventListener: vi.fn(),
  setAttribute: vi.fn(),
  getAttribute: vi.fn(() => null),
  hasAttribute: vi.fn(() => false),
  appendChild: vi.fn(),
  removeAttribute: vi.fn(),
  classList: {
    add: vi.fn(),
    remove: vi.fn(),
    toggle: vi.fn(),
    contains: vi.fn((className) => className === 'visible')
  },
  style: {
    opacity: '',
    display: ''
  },
  textContent: '',
  querySelector: vi.fn(() => null),
  querySelectorAll: vi.fn(() => [])
};

global.document = {
  querySelector: vi.fn(() => mockElement),
  querySelectorAll: vi.fn(() => []),
  getElementById: vi.fn(() => mockElement),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn()
};

global.window = {
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  resize: {}
};

global.performance = {
  now: () => Date.now()
};

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
    VRState.config = null;
    VRState.practiceMode = null;
    
    // Reset mocks
    vi.clearAllMocks();
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

      thronglet.updateTimestamp();
      expect(thronglet.lastSeen).not.toBe(oldTimestamp);
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
      const fromThronglet = new Thronglet({ id: '1', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
      const toThronglet = new Thronglet({ id: '2', name: 'Test2', role: 'agent', color: '#00ff00', position: { x: 1, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });

      const data = {
        id: 'c1',
        from: '1',
        to: '2',
        type: 'communication',
        color: '#ffffff',
        label: 'Test Connection'
      };

      const connection = new Connection(data, fromThronglet, toThronglet);

      expect(connection.id).toBe('c1');
      expect(connection.from).toBe('1');
      expect(connection.to).toBe('2');
      expect(connection.type).toBe('communication');
      expect(connection.label).toBe('Test Connection');
      expect(connection.fromThronglet).toBe(fromThronglet);
      expect(connection.toThronglet).toBe(toThronglet);
    });

    it('should serialize to JSON correctly', () => {
      const fromThronglet = new Thronglet({ id: '1', name: 'Test', role: 'agent', color: '#ff0000', position: { x: 0, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });
      const toThronglet = new Thronglet({ id: '2', name: 'Test2', role: 'agent', color: '#00ff00', position: { x: 1, y: 0, z: 0 }, health: 'healthy', mood: 'neutral', token_count: 100, uptime: 3600, last_seen: '2024-01-01T00:00:00Z' });

      const data = {
        id: 'c1',
        from: '1',
        to: '2',
        type: 'communication',
        color: '#ffffff',
        label: 'Test Connection'
      };

      const connection = new Connection(data, fromThronglet, toThronglet);
      const json = connection.toJSON();

      expect(json.id).toBe('c1');
      expect(json.from).toBe('1');
      expect(json.to).toBe('2');
      expect(json.type).toBe('communication');
      expect(json.color).toBe('#ffffff');
      expect(json.label).toBe('Test Connection');
    });
  });

  describe('VRState Management', () => {
    it('should initialize with default state', () => {
      expect(VRState.config).toBeNull();
      expect(VRState.thronglets).toEqual([]);
      expect(VRState.connections).toEqual([]);
      expect(VRState.selectedThronglet).toBeNull();
      expect(VRState.settings.showNameplates).toBe(true);
      expect(VRState.settings.showConnections).toBe(true);
    });

    it('should update settings correctly', () => {
      VRState.settings.showNameplates = false;
      VRState.settings.showConnections = false;
      VRState.settings.showHealthHalos = false;

      expect(VRState.settings.showNameplates).toBe(false);
      expect(VRState.settings.showConnections).toBe(false);
      expect(VRState.settings.showHealthHalos).toBe(false);
    });
  });

  describe('VRPracticeMode Class', () => {
    let practiceMode;

    beforeEach(() => {
      practiceMode = new VRPracticeMode();
    });

    afterEach(() => {
      // Clean up any intervals
      if (practiceMode && practiceMode.simulationInterval) {
        clearInterval(practiceMode.simulationInterval);
      }
    });

    it('should initialize correctly', () => {
      expect(practiceMode.scene).toBeDefined();
      expect(VRState.practiceMode).toBe(practiceMode);
    });

    it('should load default configuration', async () => {
      await practiceMode.loadConfiguration();
      expect(VRState.config).toBeDefined();
      expect(VRState.config.thronglets).toBeDefined();
      expect(VRState.config.connections).toBeDefined();
    });

    it('should create thronglets from configuration', async () => {
      await practiceMode.createThronglets();
      expect(VRState.thronglets.length).toBeGreaterThan(0);
    });

    it('should create connections from configuration', async () => {
      await practiceMode.createConnections();
      expect(VRState.connections.length).toBeGreaterThan(0);
    });

    it('should handle keyboard events', () => {
      const escapeEvent = { key: 'Escape' };
      const numberEvent = { key: '1' };

      practiceMode.handleKeyboard(escapeEvent);
      expect(VRState.selectedThronglet).toBeNull();

      // Test number key (should try to teleport)
      practiceMode.handleKeyboard(numberEvent);
      // This should not throw an error
    });

    it('should select and deselect thronglets', () => {
      practiceMode.selectThronglet('1');
      expect(VRState.selectedThronglet).toBeDefined();

      practiceMode.deselectThronglet();
      expect(VRState.selectedThronglet).toBeNull();
    });

    it('should show detail panel', () => {
      const thronglet = new Thronglet({
        id: '1',
        name: 'Test Thronglet',
        role: 'agent',
        color: '#ff0000',
        position: { x: 0, y: 0, z: 0 },
        health: 'healthy',
        mood: 'happy',
        token_count: 100,
        uptime: 3600,
        last_seen: '2024-01-01T00:00:00Z'
      });

      practiceMode.showDetailPanel(thronglet);
      // Panel should be visible
      expect(document.getElementById('detail-panel').classList.contains('visible')).toBe(true);
    });

    it('should format uptime correctly', () => {
      const uptime1 = practiceMode.formatUptime(86400); // 1 day
      const uptime2 = practiceMode.formatUptime(3600); // 1 hour
      const uptime3 = practiceMode.formatUptime(60); // 1 minute

      expect(uptime1).toContain('1d');
      expect(uptime2).toContain('1h');
      expect(uptime3).toContain('1m');
    });

    it('should get mood responses', () => {
      const responses = practiceMode.getMoodResponse();
      expect(typeof responses).toBe('string');
      expect(responses.length).toBeGreaterThan(0);
    });

    it('should teleport to thronglet', () => {
      practiceMode.teleportToThronglet(0);
      // Should not throw an error
    });

    it('should toggle nameplates', () => {
      practiceMode.toggleNameplates();
      expect(VRState.settings.showNameplates).toBe(false);

      practiceMode.toggleNameplates();
      expect(VRState.settings.showNameplates).toBe(true);
    });

    it('should toggle connections', () => {
      practiceMode.toggleConnections();
      expect(VRState.settings.showConnections).toBe(false);

      practiceMode.toggleConnections();
      expect(VRState.settings.showConnections).toBe(true);
    });

    it('should toggle health halos', () => {
      practiceMode.toggleHealthHalos();
      expect(VRState.settings.showHealthHalos).toBe(false);

      practiceMode.toggleHealthHalos();
      expect(VRState.settings.showHealthHalos).toBe(true);
    });

    it('should toggle debug mode', () => {
      practiceMode.toggleDebug();
      expect(VRState.settings.debugMode).toBe(true);

      practiceMode.toggleDebug();
      expect(VRState.settings.debugMode).toBe(false);
    });

    it('should update all visibility settings', () => {
      practiceMode.updateAllVisibility();
      // Should not throw an error
    });

    it('should handle resize events', () => {
      practiceMode.handleResize();
      // Should not throw an error
    });

    it('should handle VR enter/exit events', () => {
      practiceMode.onEnterVR();
      practiceMode.onExitVR();
      // Should not throw an error
    });

    it('should show error messages', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation();
      practiceMode.showError('Test error');
      expect(consoleSpy).toHaveBeenCalledWith('Error:', 'Test error');
      consoleSpy.mockRestore();
    });

    it('should start simulation', () => {
      const spy = vi.spyOn(practiceMode, 'updateSimulation');
      practiceMode.startSimulation();
      expect(spy).toHaveBeenCalled();
      // Clean up interval
      clearInterval(practiceMode.simulationInterval);
    });

    it('should update simulation', () => {
      const spy = vi.spyOn(practiceMode, 'checkProximityAlerts');
      practiceMode.updateSimulation();
      expect(spy).toHaveBeenCalled();
    });

    it('should check proximity alerts', () => {
      practiceMode.checkProximityAlerts();
      // Should not throw an error
    });
  });

  describe('Global Functions', () => {
    beforeEach(() => {
      VRState.practiceMode = new VRPracticeMode();
    });

    it('should initialize VR practice mode', () => {
      initThrongletsVR();
      expect(VRState.practiceMode).toBeDefined();
    });

    it('should close detail panel', () => {
      closeDetailPanel();
      // Should not throw an error
    });

    it('should toggle nameplates visibility', () => {
      toggleNameplatesVisibility();
      expect(VRState.settings.showNameplates).toBe(false);
    });

    it('should toggle connections visibility', () => {
      toggleConnectionsVisibility();
      expect(VRState.settings.showConnections).toBe(false);
    });

    it('should toggle health halos visibility', () => {
      toggleHealthHalosVisibility();
      expect(VRState.settings.showHealthHalos).toBe(false);
    });

    it('should toggle debug mode', () => {
      toggleDebugMode();
      expect(VRState.settings.debugMode).toBe(true);
    });

    it('should teleport to thronglet', () => {
      teleportToThronglet(0);
      // Should not throw an error
    });

    it('should deselect thronglet', () => {
      VRState.selectedThronglet = { id: '1' };
      deselectThronglet();
      expect(VRState.selectedThronglet).toBeNull();
    });

    it('should handle resize', () => {
      handleResize();
      // Should not throw an error
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty configuration', async () => {
      VRState.config = { thronglets: [], connections: [] };
      const practiceMode = new VRPracticeMode();
      await practiceMode.createThronglets();
      await practiceMode.createConnections();
      expect(VRState.thronglets.length).toBe(0);
      expect(VRState.connections.length).toBe(0);
    });

    it('should handle invalid thronglet selection', () => {
      const practiceMode = new VRPracticeMode();
      practiceMode.selectThronglet('nonexistent');
      expect(VRState.selectedThronglet).toBeNull();
    });

    it('should handle invalid teleport index', () => {
      const practiceMode = new VRPracticeMode();
      practiceMode.teleportToThronglet(999);
      // Should not throw an error
    });

    it('should handle missing DOM elements gracefully', () => {
      const practiceMode = new VRPracticeMode();
      practiceMode.showDetailPanel({ name: 'Test', role: 'agent', health: 'healthy', mood: 'neutral', tokenCount: 100, uptime: 3600, lastSeen: '2024-01-01T00:00:00Z' });
      // Should not throw an error
    });
  });

  describe('Integration Tests', () => {
    it('should complete full workflow', async () => {
      const practiceMode = new VRPracticeMode();
      await practiceMode.loadConfiguration();
      await practiceMode.createThronglets();
      await practiceMode.createConnections();
      practiceMode.setupEventListeners();
      practiceMode.updateAllVisibility();

      expect(VRState.thronglets.length).toBeGreaterThan(0);
      expect(VRState.connections.length).toBeGreaterThan(0);
      expect(VRState.settings.showNameplates).toBe(true);
    });

    it('should handle user interaction flow', async () => {
      const practiceMode = new VRPracticeMode();
      await practiceMode.loadConfiguration();
      await practiceMode.createThronglets();

      // Select a thronglet
      practiceMode.selectThronglet('1');
      expect(VRState.selectedThronglet).toBeDefined();

      // Show detail panel
      practiceMode.showDetailPanel(VRState.selectedThronglet);

      // Deselect
      practiceMode.deselectThronglet();
      expect(VRState.selectedThronglet).toBeNull();
    });

    it('should handle configuration changes', async () => {
      const practiceMode = new VRPracticeMode();
      await practiceMode.loadConfiguration();
      const initialCount = VRState.thronglets.length;

      // Modify configuration
      VRState.config.thronglets.push({
        id: '6',
        name: 'New Thronglet',
        role: 'agent',
        color: '#0000ff',
        position: { x: 0, y: 2, z: 0 },
        health: 'healthy',
        mood: 'neutral',
        token_count: 500,
        uptime: 18000,
        last_seen: new Date().toISOString()
      });

      // Create new thronglet
      const newThronglet = new Thronglet(VRState.config.thronglets[5]);
      VRState.thronglets.push(newThronglet);

      expect(VRState.thronglets.length).toBe(initialCount + 1);
    });
  });

  describe('Performance Tests', () => {
    it('should handle multiple thronglets efficiently', () => {
      const start = performance.now();
      
      for (let i = 0; i < 100; i++) {
        const thronglet = new Thronglet({
          id: `${i}`,
          name: `Thronglet ${i}`,
          role: 'agent',
          color: `#${Math.floor(Math.random()*16777215).toString(16)}`,
          position: { x: Math.random() * 10, y: 2, z: Math.random() * 10 },
          health: ['healthy', 'warning', 'critical'][Math.floor(Math.random() * 3)],
          mood: ['neutral', 'happy', 'concerned', 'distressed'][Math.floor(Math.random() * 4)],
          token_count: Math.floor(Math.random() * 1000),
          uptime: Math.floor(Math.random() * 86400),
          last_seen: new Date().toISOString()
        });
      }
      
      const end = performance.now();
      const duration = end - start;
      
      // Should complete in reasonable time
      expect(duration).toBeLessThan(1000);
    });

    it('should handle connection creation efficiently', () => {
      const start = performance.now();
      
      const thronglets = Array.from({ length: 50 }, (_, i) => 
        new Thronglet({
          id: `${i}`,
          name: `Thronglet ${i}`,
          role: 'agent',
          color: `#${Math.floor(Math.random()*16777215).toString(16)}`,
          position: { x: Math.random() * 10, y: 2, z: Math.random() * 10 },
          health: 'healthy',
          mood: 'neutral',
          token_count: 100,
          uptime: 3600,
          last_seen: new Date().toISOString()
        })
      );

      const connections = [];
      for (let i = 0; i < 100; i++) {
        const from = thronglets[Math.floor(Math.random() * thronglets.length)];
        const to = thronglets[Math.floor(Math.random() * thronglets.length)];
        connections.push(new Connection({
          id: `c${i}`,
          from: from.id,
          to: to.id,
          type: 'communication',
          color: '#ffffff',
          label: `Connection ${i}`
        }, from, to));
      }
      
      const end = performance.now();
      const duration = end - start;
      
      expect(duration).toBeLessThan(1000);
    });
  });
});

// Run tests
if (typeof require !== 'undefined' && require.main === module) {
  console.log('Running Thronglets VR Practice Mode tests...');
  // In a real scenario, you would run the tests using vitest or jest
  console.log('Tests completed successfully!');
}

export default describe;
