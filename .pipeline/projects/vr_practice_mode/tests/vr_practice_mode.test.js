/**
 * VR Practice Mode Tests
 * Tests for the VR practice mode functionality
 */

describe('VR Practice Mode', () => {
  describe('VRState', () => {
    it('should initialize with default values', () => {
      expect(VRState).toBeDefined();
      expect(VRState.practiceMode).toBeDefined();
      expect(VRState.practiceMode.enabled).toBe(false);
      expect(VRState.practiceMode.simulationRunning).toBe(false);
    });

    it('should enable practice mode', () => {
      VRState.practiceMode.enable();
      expect(VRState.practiceMode.enabled).toBe(true);
    });

    it('should disable practice mode', () => {
      VRState.practiceMode.enable();
      VRState.practiceMode.disable();
      expect(VRState.practiceMode.enabled).toBe(false);
    });
  });

  describe('PracticeMode', () => {
    let practiceMode;

    beforeEach(() => {
      practiceMode = new PracticeMode();
    });

    describe('startSimulation', () => {
      it('should start the simulation loop', () => {
        practiceMode.startSimulation();
        expect(practiceMode.simulationRunning).toBe(true);
      });

      it('should create initial thronglets', () => {
        practiceMode.startSimulation();
        expect(practiceMode.thronglets.size).toBeGreaterThan(0);
      });

      it('should create initial connections', () => {
        practiceMode.startSimulation();
        expect(practiceMode.connections.size).toBeGreaterThan(0);
      });
    });

    describe('stopSimulation', () => {
      it('should stop the simulation loop', () => {
        practiceMode.startSimulation();
        practiceMode.stopSimulation();
        expect(practiceMode.simulationRunning).toBe(false);
      });
    });

    describe('selectThronglet', () => {
      it('should select a thronglet by ID', () => {
        practiceMode.startSimulation();
        const firstThrongletId = Array.from(practiceMode.thronglets.keys())[0];
        practiceMode.selectThronglet(firstThrongletId);
        expect(practiceMode.selectedThrongletId).toBe(firstThrongletId);
      });

      it('should update the selected thronglet', () => {
        practiceMode.startSimulation();
        const throngletId = 'thronglet-1';
        practiceMode.selectThronglet(throngletId);
        expect(practiceMode.selectedThrongletId).toBe(throngletId);
      });
    });

    describe('deselectThronglet', () => {
      it('should deselect the current thronglet', () => {
        practiceMode.startSimulation();
        practiceMode.selectThronglet('thronglet-1');
        practiceMode.deselectThronglet();
        expect(practiceMode.selectedThrongletId).toBe(null);
      });
    });

    describe('getThrongletById', () => {
      it('should return a thronglet by ID', () => {
        practiceMode.startSimulation();
        const firstThrongletId = Array.from(practiceMode.thronglets.keys())[0];
        const thronglet = practiceMode.getThrongletById(firstThrongletId);
        expect(thronglet).toBeDefined();
        expect(thronglet.id).toBe(firstThrongletId);
      });

      it('should return null for non-existent ID', () => {
        practiceMode.startSimulation();
        const thronglet = practiceMode.getThrongletById('non-existent');
        expect(thronglet).toBeNull();
      });
    });

    describe('getThrongletsNearby', () => {
      it('should return thronglets within proximity radius', () => {
        practiceMode.startSimulation();
        const selectedId = Array.from(practiceMode.thronglets.keys())[0];
        const nearby = practiceMode.getThrongletsNearby(selectedId, 5);
        expect(Array.isArray(nearby)).toBe(true);
      });
    });

    describe('updateSimulation', () => {
      it('should update all thronglets', () => {
        practiceMode.startSimulation();
        const initialCount = practiceMode.thronglets.size;
        practiceMode.updateSimulation(16); // ~60fps
        expect(practiceMode.thronglets.size).toBe(initialCount);
      });

      it('should update thronglet positions', () => {
        practiceMode.startSimulation();
        practiceMode.updateSimulation(16);
        practiceMode.thronglets.forEach(thronglet => {
          expect(thronglet.position).toBeDefined();
        });
      });
    });

    describe('createThronglet', () => {
      it('should create a new thronglet', () => {
        const newThronglet = practiceMode.createThronglet({
          id: 'test-thronglet',
          name: 'Test Thronglet',
          role: 'test',
          color: '#ff0000',
          health: 'healthy'
        });
        expect(newThronglet.id).toBe('test-thronglet');
        expect(newThronglet.name).toBe('Test Thronglet');
      });
    });

    describe('createConnection', () => {
      it('should create a new connection', () => {
        practiceMode.startSimulation();
        const throngletIds = Array.from(practiceMode.thronglets.keys());
        if (throngletIds.length >= 2) {
          const connection = practiceMode.createConnection({
            from: throngletIds[0],
            to: throngletIds[1],
            label: 'Test Connection'
          });
          expect(connection.from).toBe(throngletIds[0]);
          expect(connection.to).toBe(throngletIds[1]);
        }
      });
    });

    describe('updateThrongletHealth', () => {
      it('should update thronglet health status', () => {
        practiceMode.startSimulation();
        const throngletId = Array.from(practiceMode.thronglets.keys())[0];
        practiceMode.updateThrongletHealth(throngletId, 'warning');
        const thronglet = practiceMode.getThrongletById(throngletId);
        expect(thronglet.health).toBe('warning');
      });
    });

    describe('updateThrongletMood', () => {
      it('should update thronglet mood', () => {
        practiceMode.startSimulation();
        const throngletId = Array.from(practiceMode.thronglets.keys())[0];
        practiceMode.updateThrongletMood(throngletId, 'happy');
        const thronglet = practiceMode.getThrongletById(throngletId);
        expect(thronglet.mood).toBe('happy');
      });
    });

    describe('teleportToThronglet', () => {
      it('should teleport camera to thronglet position', () => {
        practiceMode.startSimulation();
        const throngletId = Array.from(practiceMode.thronglets.keys())[0];
        const thronglet = practiceMode.getThrongletById(throngletId);
        practiceMode.teleportToThronglet(throngletId);
        expect(practiceMode.lastTeleportTarget).toBe(throngletId);
      });
    });

    describe('getThrongletStats', () => {
      it('should return thronglet statistics', () => {
        practiceMode.startSimulation();
        const throngletId = Array.from(practiceMode.thronglets.keys())[0];
        const stats = practiceMode.getThrongletStats(throngletId);
        expect(stats.id).toBe(throngletId);
        expect(stats.name).toBeDefined();
        expect(stats.role).toBeDefined();
        expect(stats.health).toBeDefined();
        expect(stats.mood).toBeDefined();
        expect(stats.tokenCount).toBeDefined();
        expect(stats.uptime).toBeDefined();
        expect(stats.lastSeen).toBeDefined();
      });
    });

    describe('getProximityAlert', () => {
      it('should return proximity alert for nearby thronglets', () => {
        practiceMode.startSimulation();
        const selectedId = Array.from(practiceMode.thronglets.keys())[0];
        const nearby = practiceMode.getThrongletsNearby(selectedId, 5);
        const alert = practiceMode.getProximityAlert(selectedId, nearby);
        expect(alert).toBeDefined();
        expect(alert.throngletCount).toBeGreaterThan(0);
      });
    });
  });

  describe('Thronglet', () => {
    it('should create a thronglet with default values', () => {
      const thronglet = new Thronglet({
        id: 'test-1',
        name: 'Test',
        role: 'test',
        color: '#ff0000'
      });
      expect(thronglet.id).toBe('test-1');
      expect(thronglet.name).toBe('Test');
      expect(thronglet.role).toBe('test');
      expect(thronglet.color).toBe('#ff0000');
      expect(thronglet.health).toBe('healthy');
      expect(thronglet.mood).toBe('neutral');
      expect(thronglet.tokenCount).toBe(0);
      expect(thronglet.uptime).toBe(0);
    });

    it('should update thronglet position', () => {
      const thronglet = new Thronglet({
        id: 'test-1',
        name: 'Test',
        role: 'test',
        color: '#ff0000'
      });
      thronglet.position = { x: 1, y: 2, z: 3 };
      expect(thronglet.position.x).toBe(1);
      expect(thronglet.position.y).toBe(2);
      expect(thronglet.position.z).toBe(3);
    });

    it('should update thronglet health', () => {
      const thronglet = new Thronglet({
        id: 'test-1',
        name: 'Test',
        role: 'test',
        color: '#ff0000'
      });
      thronglet.health = 'warning';
      expect(thronglet.health).toBe('warning');
    });

    it('should update thronglet mood', () => {
      const thronglet = new Thronglet({
        id: 'test-1',
        name: 'Test',
        role: 'test',
        color: '#ff0000'
      });
      thronglet.mood = 'happy';
      expect(thronglet.mood).toBe('happy');
    });

    it('should increment token count', () => {
      const thronglet = new Thronglet({
        id: 'test-1',
        name: 'Test',
        role: 'test',
        color: '#ff0000'
      });
      thronglet.tokenCount = 10;
      thronglet.tokenCount = 15;
      expect(thronglet.tokenCount).toBe(15);
    });

    it('should update uptime', () => {
      const thronglet = new Thronglet({
        id: 'test-1',
        name: 'Test',
        role: 'test',
        color: '#ff0000'
      });
      thronglet.uptime = 100;
      expect(thronglet.uptime).toBe(100);
    });

    it('should update last seen timestamp', () => {
      const thronglet = new Thronglet({
        id: 'test-1',
        name: 'Test',
        role: 'test',
        color: '#ff0000'
      });
      thronglet.lastSeen = Date.now();
      expect(thronglet.lastSeen).toBeGreaterThan(0);
    });
  });

  describe('Connection', () => {
    it('should create a connection', () => {
      const connection = new Connection({
        from: 'thronglet-1',
        to: 'thronglet-2',
        label: 'Test Connection'
      });
      expect(connection.from).toBe('thronglet-1');
      expect(connection.to).toBe('thronglet-2');
      expect(connection.label).toBe('Test Connection');
    });

    it('should have a unique ID', () => {
      const connection1 = new Connection({
        from: 'thronglet-1',
        to: 'thronglet-2',
        label: 'Test 1'
      });
      const connection2 = new Connection({
        from: 'thronglet-1',
        to: 'thronglet-2',
        label: 'Test 2'
      });
      expect(connection1.id).not.toBe(connection2.id);
    });
  });

  describe('UI Functions', () => {
    describe('toggleNameplatesVisibility', () => {
      it('should toggle nameplates visibility', () => {
        toggleNameplatesVisibility();
        const btn = document.getElementById('toggle-nameplates');
        expect(btn.classList.contains('active')).toBe(true);
      });
    });

    describe('toggleConnectionsVisibility', () => {
      it('should toggle connections visibility', () => {
        toggleConnectionsVisibility();
        const btn = document.getElementById('toggle-connections');
        expect(btn.classList.contains('active')).toBe(true);
      });
    });

    describe('toggleHealthHalosVisibility', () => {
      it('should toggle health halos visibility', () => {
        toggleHealthHalosVisibility();
        const btn = document.getElementById('toggle-health');
        expect(btn.classList.contains('active')).toBe(true);
      });
    });

    describe('toggleDebugMode', () => {
      it('should toggle debug mode', () => {
        toggleDebugMode();
        const panel = document.getElementById('debug-panel');
        expect(panel.classList.contains('visible')).toBe(true);
      });
    });

    describe('openDetailPanel', () => {
      it('should open the detail panel', () => {
        openDetailPanel('test-id');
        const panel = document.getElementById('detail-panel');
        expect(panel.classList.contains('visible')).toBe(true);
      });
    });

    describe('closeDetailPanel', () => {
      it('should close the detail panel', () => {
        closeDetailPanel();
        const panel = document.getElementById('detail-panel');
        expect(panel.classList.contains('visible')).toBe(false);
      });
    });

    describe('updateDetailPanel', () => {
      it('should update the detail panel with thronglet data', () => {
        const throngletData = {
          id: 'test-1',
          name: 'Test Thronglet',
          role: 'test',
          health: 'healthy',
          mood: 'happy',
          tokenCount: 10,
          uptime: 100,
          lastSeen: Date.now()
        };
        updateDetailPanel(throngletData);
        expect(document.getElementById('detail-title').textContent).toBe('Test Thronglet');
        expect(document.getElementById('detail-role').textContent).toBe('test');
        expect(document.getElementById('detail-health').textContent).toBe('healthy');
        expect(document.getElementById('detail-mood').textContent).toBe('happy');
        expect(document.getElementById('detail-tokens').textContent).toBe('10');
        expect(document.getElementById('detail-uptime').textContent).toBe('100');
      });
    });

    describe('showProximityAlert', () => {
      it('should show proximity alert', () => {
        showProximityAlert('test-id', 3);
        const alert = document.getElementById('proximity-alert');
        expect(alert.classList.contains('visible')).toBe(true);
      });
    });

    describe('hideProximityAlert', () => {
      it('should hide proximity alert', () => {
        hideProximityAlert();
        const alert = document.getElementById('proximity-alert');
        expect(alert.classList.contains('visible')).toBe(false);
      });
    });

    describe('updateDebugPanel', () => {
      it('should update debug panel with stats', () => {
        updateDebugPanel(5, 10, 'test-id');
        expect(document.getElementById('debug-thronglet-count').textContent).toBe('5');
        expect(document.getElementById('debug-connection-count').textContent).toBe('10');
        expect(document.getElementById('debug-selected').textContent).toBe('test-id');
      });
    });

    describe('handleResize', () => {
      it('should handle window resize', () => {
        handleResize();
        // Should not throw an error
      });
    });
  });

  describe('Keyboard Controls', () => {
    describe('handleKeyboardControls', () => {
      it('should handle number keys for teleportation', () => {
        const event = {
          key: '1',
          preventDefault: () => {}
        };
        handleKeyboardControls(event);
        // Should not throw an error
      });

      it('should handle ESC key for deselection', () => {
        const event = {
          key: 'Escape',
          preventDefault: () => {}
        };
        handleKeyboardControls(event);
        // Should not throw an error
      });
    });
  });
});

// Mock A-Frame for testing
global.AFRAME = {
  registerComponent: () => {},
  registerSystem: () => {}
};

// Mock Three.js for testing
global.THREE = {
  Vector3: class Vector3 {
    constructor(x, y, z) {
      this.x = x;
      this.y = y;
      this.z = z;
    }
  }
};
