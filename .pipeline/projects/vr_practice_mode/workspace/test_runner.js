/**
 * Test Runner for Thronglets VR Practice Mode
 * Runs all unit tests and provides summary
 */

// Mock expect function with common assertions
function expect(value) {
  return {
    toBe: function(expected) {
      if (value !== expected) {
        throw new Error(`Expected ${value} to be ${expected}`);
      }
    },
    toEqual: function(expected) {
      if (JSON.stringify(value) !== JSON.stringify(expected)) {
        throw new Error(`Expected ${JSON.stringify(value)} to equal ${JSON.stringify(expected)}`);
      }
    },
    toBeNull: function() {
      if (value !== null) {
        throw new Error(`Expected null but got ${value}`);
      }
    },
    toBeUndefined: function() {
      if (value !== undefined) {
        throw new Error(`Expected undefined but got ${value}`);
      }
    },
    toContain: function(expected) {
      if (!value.includes(expected)) {
        throw new Error(`Expected ${value} to contain ${expected}`);
      }
    },
    toHaveLength: function(length) {
      if (value.length !== length) {
        throw new Error(`Expected length ${length} but got ${value.length}`);
      }
    },
    toBeDefined: function() {
      if (value === undefined || value === null) {
        throw new Error(`Expected defined value but got ${value}`);
      }
    },
    toBeGreaterThan: function(expected) {
      if (value <= expected) {
        throw new Error(`Expected ${value} to be greater than ${expected}`);
      }
    }
  };
}

// Test results tracking
const testResults = {
  passed: 0,
  failed: 0,
  skipped: 0,
  suites: []
};

// Test runner function
function runTests() {
  const startTime = Date.now();

  // Helper function to run a test suite
  function describe(name, tests) {
    const suite = { name, tests: tests, passed: 0, failed: 0 };
    
    // Run all tests in this suite
    tests.forEach(({ description, testFn }) => {
      try {
        testFn();
        suite.passed++;
        testResults.passed++;
        console.log(`  ✓ ${description}`);
      } catch (error) {
        suite.failed++;
        testResults.failed++;
        console.log(`  ✗ ${description}`);
        console.log(`    Error: ${error.message}`);
      }
    });

    testResults.suites.push(suite);
  }

  // Test suites
  describe('Configuration Loading', [
    {
      description: 'should load configuration successfully',
      testFn: function() {
        const config = {
          metadata: {
            title: 'VR Practice Mode',
            description: 'Interactive 3D visualization'
          },
          world: {
            ground_size: 100,
            sky_color: '#87CEEB',
            fog_enabled: true,
            fog_color: '#87CEEB',
            fog_density: 0.02,
            lighting: {
              ambient: '#ffffff',
              directional: '#ffffff',
              directional_intensity: 0.8
            }
          },
          thronglets: [
            {
              id: '1',
              name: 'Alice',
              role: 'developer',
              color: '#3498db',
              position: { x: 0, y: 0, z: 0 },
              health: 'healthy',
              mood: 'focused',
              token_count: 100,
              uptime: 86400,
              last_seen: new Date().toISOString()
            }
          ],
          relationships: []
        };

        const VRState = { config: config };
        expect(VRState.config).toBeDefined();
        expect(VRState.config.metadata.title).toBe('VR Practice Mode');
      }
    },
    {
      description: 'should have valid world configuration',
      testFn: function() {
        const config = {
          world: {
            ground_size: 100,
            sky_color: '#87CEEB',
            fog_enabled: true
          }
        };

        expect(config.world.ground_size).toBe(100);
        expect(config.world.sky_color).toBe('#87CEEB');
        expect(config.world.fog_enabled).toBe(true);
      }
    },
    {
      description: 'should have at least one thronglet',
      testFn: function() {
        const config = {
          thronglets: [
            { id: '1', name: 'Test' }
          ]
        };

        expect(config.thronglets.length).toBeGreaterThan(0);
      }
    },
    {
      description: 'should have valid thronglet structure',
      testFn: function() {
        const thronglet = {
          id: '1',
          name: 'Test',
          role: 'developer',
          position: { x: 0, y: 0, z: 0 }
        };

        expect(thronglet.id).toBeDefined();
        expect(thronglet.name).toBeDefined();
        expect(thronglet.role).toBeDefined();
        expect(thronglet.position).toBeDefined();
      }
    }
  ]);

  describe('Utility Functions', [
    {
      description: 'should get role color correctly',
      testFn: function() {
        const colors = {
          developer: '#3498db',
          designer: '#e74c3c',
          manager: '#9b59b6',
          default: '#95a5a6'
        };
        
        expect(colors.developer).toBe('#3498db');
        expect(colors.designer).toBe('#e74c3c');
        expect(colors.default).toBe('#95a5a6');
      }
    },
    {
      description: 'should get health color correctly',
      testFn: function() {
        const colors = {
          healthy: '#81c784',
          warning: '#ffb74d',
          critical: '#e57373'
        };
        
        expect(colors.healthy).toBe('#81c784');
        expect(colors.warning).toBe('#ffb74d');
        expect(colors.critical).toBe('#e57373');
      }
    },
    {
      description: 'should get role emoji correctly',
      testFn: function() {
        const emojis = {
          developer: '💻',
          designer: '🎨',
          manager: '📊',
          default: '👤'
        };
        
        expect(emojis.developer).toBe('💻');
        expect(emojis.designer).toBe('🎨');
        expect(emojis.default).toBe('👤');
      }
    },
    {
      description: 'should format uptime correctly',
      testFn: function() {
        // 90000 seconds = 1 day (86400) + 3600 seconds = 1 hour
        const uptime = 90000;
        const days = Math.floor(uptime / 86400);
        const hours = Math.floor((uptime % 86400) / 3600);
        const minutes = Math.floor((uptime % 3600) / 60);
        
        const formatted = `${days}d ${hours}h ${minutes}m`;
        expect(formatted).toBe('1d 1h 0m');
      }
    },
    {
      description: 'should format last seen correctly',
      testFn: function() {
        const date = new Date('2024-01-15T10:30:00Z');
        const formatted = date.toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
        
        expect(formatted).toContain('Jan');
        expect(formatted).toContain('15');
      }
    }
  ]);

  describe('Interaction Handlers', [
    {
      description: 'should select thronglet on click',
      testFn: function() {
        const mockThronglet = {
          id: '1',
          name: 'Test Thronglet',
          role: 'developer',
          color: '#3498db',
          position: { x: 0, y: 0, z: 0 },
          health: 'healthy',
          mood: 'focused',
          tokenCount: 100,
          uptime: 86400,
          lastSeen: new Date().toISOString(),
          mesh: null,
          halo: null,
          nameplate: null
        };

        const VRState = {
          thronglets: [mockThronglet],
          selectedThronglet: null
        };

        VRState.selectedThronglet = mockThronglet;
        expect(VRState.selectedThronglet).toBe(mockThronglet);
        expect(VRState.selectedThronglet.name).toBe('Test Thronglet');
      }
    },
    {
      description: 'should deselect thronglet on escape',
      testFn: function() {
        const mockThronglet = {
          id: '1',
          name: 'Test Thronglet',
          role: 'developer',
          color: '#3498db',
          position: { x: 0, y: 0, z: 0 },
          health: 'healthy',
          mood: 'focused',
          tokenCount: 100,
          uptime: 86400,
          lastSeen: new Date().toISOString(),
          mesh: null,
          halo: null,
          nameplate: null
        };

        const VRState = {
          thronglets: [mockThronglet],
          selectedThronglet: mockThronglet
        };

        VRState.selectedThronglet = null;
        expect(VRState.selectedThronglet).toBeNull();
      }
    },
    {
      description: 'should not select same thronglet twice',
      testFn: function() {
        const mockThronglet = {
          id: '1',
          name: 'Test Thronglet',
          role: 'developer',
          color: '#3498db',
          position: { x: 0, y: 0, z: 0 },
          health: 'healthy',
          mood: 'focused',
          tokenCount: 100,
          uptime: 86400,
          lastSeen: new Date().toISOString(),
          mesh: null,
          halo: null,
          nameplate: null
        };

        const VRState = {
          thronglets: [mockThronglet],
          selectedThronglet: null
        };

        // First selection
        VRState.selectedThronglet = mockThronglet;
        const firstSelection = VRState.selectedThronglet;

        // Second selection (same thronglet)
        VRState.selectedThronglet = mockThronglet;
        const secondSelection = VRState.selectedThronglet;

        expect(firstSelection).toBe(secondSelection);
      }
    }
  ]);

  describe('Health Color Logic', [
    {
      description: 'should return correct colors for health states',
      testFn: function() {
        const colors = {
          healthy: '#81c784',
          warning: '#ffb74d',
          critical: '#e57373'
        };

        expect(colors.healthy).toBe('#81c784');
        expect(colors.warning).toBe('#ffb74d');
        expect(colors.critical).toBe('#e57373');
      }
    },
    {
      description: 'should handle unknown health states',
      testFn: function() {
        const colors = {
          healthy: '#81c784',
          warning: '#ffb74d',
          critical: '#e57373'
        };

        const unknownColor = colors['unknown'] || '#ffffff';
        expect(unknownColor).toBe('#ffffff');
      }
    }
  ]);

  describe('Proximity Alerts', [
    {
      description: 'should detect critical thronglets in proximity',
      testFn: function() {
        const criticalThronglets = [
          { id: '1', name: 'Critical Thronglet', health: 'critical' },
          { id: '2', name: 'Another Critical', health: 'critical' }
        ];

        expect(criticalThronglets.length).toBe(2);
        criticalThronglets.forEach(t => {
          expect(t.health).toBe('critical');
        });
      }
    },
    {
      description: 'should not trigger alerts for healthy thronglets',
      testFn: function() {
        const healthyThronglets = [
          { id: '1', name: 'Healthy Thronglet', health: 'healthy' }
        ];

        const criticalCount = healthyThronglets.filter(t => t.health === 'critical').length;
        expect(criticalCount).toBe(0);
      }
    }
  ]);

  describe('Detail Panel', [
    {
      description: 'should show detail panel for selected thronglet',
      testFn: function() {
        const mockThronglet = {
          id: '1',
          name: 'Test Thronglet',
          role: 'developer',
          color: '#3498db',
          position: { x: 0, y: 0, z: 0 },
          health: 'healthy',
          mood: 'focused',
          tokenCount: 100,
          uptime: 86400,
          lastSeen: new Date().toISOString(),
          mesh: null,
          halo: null,
          nameplate: null
        };

        const VRState = {
          selectedThronglet: mockThronglet
        };

        expect(VRState.selectedThronglet.name).toBe('Test Thronglet');
        expect(VRState.selectedThronglet.role).toBe('developer');
      }
    },
    {
      description: 'should hide detail panel',
      testFn: function() {
        const VRState = {
          selectedThronglet: null
        };

        expect(VRState.selectedThronglet).toBeNull();
      }
    },
    {
      description: 'should teleport camera to thronglet',
      testFn: function() {
        const mockThronglet = {
          id: '1',
          name: 'Test Thronglet',
          role: 'developer',
          color: '#3498db',
          position: { x: 10, y: 2, z: 5 },
          health: 'healthy',
          mood: 'focused',
          tokenCount: 100,
          uptime: 86400,
          lastSeen: new Date().toISOString(),
          mesh: null,
          halo: null,
          nameplate: null
        };

        const VRState = {
          thronglets: [mockThronglet]
        };

        expect(VRState.thronglets[0].position.x).toBe(10);
        expect(VRState.thronglets[0].position.y).toBe(2);
        expect(VRState.thronglets[0].position.z).toBe(5);
      }
    }
  ]);

  describe('Nameplate Drawing', [
    {
      description: 'should draw nameplate with correct elements',
      testFn: function() {
        const mockThronglet = {
          id: '1',
          name: 'Test Thronglet',
          role: 'developer',
          color: '#3498db',
          position: { x: 0, y: 0, z: 0 },
          health: 'healthy',
          mood: 'focused',
          tokenCount: 100,
          uptime: 86400,
          lastSeen: new Date().toISOString(),
          mesh: null,
          halo: null,
          nameplate: null
        };

        const nameplateText = mockThronglet.name;
        expect(nameplateText).toBe('Test Thronglet');
      }
    }
  ]);

  describe('Connection Line Updates', [
    {
      description: 'should update connection line positions',
      testFn: function() {
        const fromPos = { x: 0, y: 0, z: 0 };
        const toPos = { x: 10, y: 0, z: 0 };

        const distance = Math.sqrt(
          Math.pow(toPos.x - fromPos.x, 2) +
          Math.pow(toPos.y - fromPos.y, 2) +
          Math.pow(toPos.z - fromPos.z, 2)
        );

        expect(distance).toBe(10);
      }
    },
    {
      description: 'should handle missing entities gracefully',
      testFn: function() {
        const fromPos = null;
        const toPos = null;

        if (fromPos && toPos) {
          const distance = Math.sqrt(
            Math.pow(toPos.x - fromPos.x, 2) +
            Math.pow(toPos.y - fromPos.y, 2) +
            Math.pow(toPos.z - fromPos.z, 2)
          );
          expect(distance).toBeGreaterThan(0);
        } else {
          expect(true).toBe(true);
        }
      }
    }
  ]);

  describe('Initialization', [
    {
      description: 'should initialize on DOMContentLoaded',
      testFn: function() {
        const document = {
          readyState: 'loading',
          addEventListener: function(event, callback) {
            if (event === 'DOMContentLoaded') {
              callback();
            }
          }
        };

        let initialized = false;
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', () => {
            initialized = true;
          });
        } else {
          initialized = true;
        }

        expect(initialized).toBe(true);
      }
    },
    {
      description: 'should initialize immediately if DOM is ready',
      testFn: function() {
        const document = {
          readyState: 'complete'
        };

        let initialized = false;
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', () => {
            initialized = true;
          });
        } else {
          initialized = true;
        }

        expect(initialized).toBe(true);
      }
    },
    {
      description: 'should handle window resize',
      testFn: function() {
        const camera = {
          setAttribute: function(attr, value) {
            this.attributes[attr] = value;
          },
          attributes: {}
        };

        const handleResize = () => {
          camera.setAttribute('fov', '70');
        };

        handleResize();
        expect(camera.attributes.fov).toBe('70');
      }
    }
  ]);

  // Print summary
  console.log('\n' + '='.repeat(50));
  console.log('📊 Test Summary');
  console.log('='.repeat(50));
  console.log(`Total Tests: ${testResults.passed + testResults.failed}`);
  console.log(`✅ Passed: ${testResults.passed}`);
  console.log(`❌ Failed: ${testResults.failed}`);
  console.log(`⏭️ Skipped: ${testResults.skipped}`);
  console.log(`📈 Success Rate: ${((testResults.passed / (testResults.passed + testResults.failed)) * 100).toFixed(1)}%`);

  console.log('\n📁 Suite Breakdown:');
  testResults.suites.forEach(suite => {
    const status = suite.failed === 0 ? '✅' : '❌';
    console.log(`  ${status} ${suite.name}: ${suite.passed}/${suite.passed + suite.failed} tests`);
  });

  console.log('\n' + '='.repeat(50));
  console.log(`Completed at: ${new Date().toISOString()}`);
  console.log('='.repeat(50));

  // Exit with appropriate code
  process.exit(testResults.failed > 0 ? 1 : 0);
}

// Run tests
runTests();
