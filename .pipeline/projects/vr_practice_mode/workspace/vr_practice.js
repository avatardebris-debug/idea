/**
 * Thronglets VR Practice Mode
 * Interactive 3D visualization and simulation environment
 * 
 * @author Thronglets Development Team
 * @version 1.0.0
 */

// Global state management
const VRState = {
  thronglets: [],
  connections: [],
  selectedThronglet: null,
  config: null,
  settings: {
    showNameplates: true,
    showConnections: true,
    showHealthHalos: true,
    debugMode: false
  },
  proximityAlerts: [],
  lastUpdate: Date.now()
};

/**
 * Thronglet class representing a single entity in the simulation
 */
class Thronglet {
  constructor(data) {
    this.id = data.id;
    this.name = data.name;
    this.role = data.role;
    this.color = data.color;
    this.position = { ...data.position };
    this.health = data.health;
    this.mood = data.mood;
    this.tokenCount = data.token_count;
    this.uptime = data.uptime;
    this.lastSeen = data.last_seen;
    this.mesh = null;
    this.halo = null;
    this.nameplate = null;
    this.updateTimestamp();
  }

  updateTimestamp() {
    this.lastSeen = new Date().toISOString();
  }

  getHealthColor() {
    const colors = {
      healthy: '#81c784',
      warning: '#ffb74d',
      critical: '#e57373'
    };
    return colors[this.health] || '#ffffff';
  }

  getHealthBadge() {
    const badges = {
      healthy: '<span class="health-badge" style="background: #81c784;">✓ Healthy</span>',
      warning: '<span class="health-badge" style="background: #ffb74d;">⚠ Warning</span>',
      critical: '<span class="health-badge" style="background: #e57373;">✗ Critical</span>'
    };
    return badges[this.health] || '<span class="health-badge">Unknown</span>';
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      role: this.role,
      color: this.color,
      position: this.position,
      health: this.health,
      mood: this.mood,
      token_count: this.tokenCount,
      uptime: this.uptime,
      last_seen: this.lastSeen
    };
  }
}

/**
 * Connection class representing relationships between thronglets
 */
class Connection {
  constructor(data, fromThronglet, toThronglet) {
    this.from = data.from;
    this.to = data.to;
    this.type = data.type;
    this.color = data.color;
    this.label = data.label;
    this.fromThronglet = fromThronglet;
    this.toThronglet = toThronglet;
    this.line = null;
  }

  toJSON() {
    return {
      from: this.from,
      to: this.to,
      type: this.type,
      color: this.color,
      label: this.label
    };
  }
}

/**
 * VR Practice Mode main controller
 */
class VRPracticeMode {
  constructor() {
    this.scene = document.querySelector('a-scene');
    this.throngletsContainer = document.getElementById('thronglets-container');
    this.connectionsContainer = document.getElementById('connections-container');
    this.init();
  }

  async init() {
    try {
      await this.loadConfiguration();
      await this.createEnvironment();
      await this.createThronglets();
      await this.createConnections();
      this.setupEventHandlers();
      this.startSimulation();
      this.updateDebugPanel();
      console.log('✓ VR Practice Mode initialized successfully');
    } catch (error) {
      console.error('✗ Failed to initialize VR Practice Mode:', error);
      this.showError('Failed to initialize VR Practice Mode');
    }
  }

  async loadConfiguration() {
    try {
      const response = await fetch('config.json');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      VRState.config = await response.json();
      VRState.settings = VRState.config.settings || VRState.settings;
      console.log('✓ Configuration loaded:', VRState.config.metadata.description);
    } catch (error) {
      console.warn('⚠ Could not load config.json, using defaults');
      VRState.config = null;
    }
  }

  async createEnvironment() {
    // Set environment based on config
    if (VRState.config && VRState.config.world) {
      const world = VRState.config.world;
      
      // Set ground size
      const ground = document.getElementById('ground');
      if (ground) {
        ground.setAttribute('width', world.ground_size);
        ground.setAttribute('height', world.ground_size);
      }

      // Set sky color
      this.scene.setAttribute('environment', `skyColor: ${world.sky_color}`);
      
      // Configure fog
      if (world.fog_enabled) {
        this.scene.setAttribute('fog', `type: linear; color: ${world.fog_color}; density: ${world.fog_density}`);
      }

      // Configure lighting
      if (world.lighting) {
        const ambient = this.scene.querySelector('[light="type: ambient"]');
        const directional = this.scene.querySelector('[light="type: directional"]');
        
        if (ambient) {
          ambient.setAttribute('color', world.lighting.ambient);
        }
        if (directional) {
          directional.setAttribute('color', world.lighting.directional);
          directional.setAttribute('intensity', world.lighting.directional_intensity);
        }
      }
    }
  }

  async createThronglets() {
    if (!VRState.config || !VRState.config.thronglets) {
      console.warn('⚠ No thronglets data in configuration');
      return;
    }

    const container = this.throngletsContainer;
    
    for (const data of VRState.config.thronglets) {
      const thronglet = new Thronglet(data);
      VRState.thronglets.push(thronglet);
      
      // Create 3D mesh
      await this.createThrongletMesh(thronglet, container);
      
      // Create health halo if needed
      if (thronglet.health !== 'healthy' && VRState.settings.showHealthHalos) {
        await this.createHealthHalo(thronglet);
      }
      
      // Create nameplate
      if (VRState.settings.showNameplates) {
        await this.createNameplate(thronglet);
      }
    }

    console.log(`✓ Created ${VRState.thronglets.length} thronglets`);
  }

  async createThrongletMesh(thronglet, container) {
    const entity = document.createElement('a-entity');
    entity.setAttribute('position', `${thronglet.position.x} ${thronglet.position.y} ${thronglet.position.z}`);
    entity.setAttribute('class', 'selectable thronglet');
    entity.setAttribute('data-id', thronglet.id);
    
    // Create main body (cube)
    const body = document.createElement('a-box');
    body.setAttribute('color', thronglet.color);
    body.setAttribute('width', '1.5');
    body.setAttribute('height', '1.5');
    body.setAttribute('depth', '1.5');
    body.setAttribute('class', 'thronglet-body');
    entity.appendChild(body);

    // Add glow effect
    const glow = document.createElement('a-entity');
    glow.setAttribute('position', '0 0 0.76');
    glow.setAttribute('light', `type: point; color: ${thronglet.color}; intensity: 0.5; distance: 5`);
    entity.appendChild(glow);

    container.appendChild(entity);
    thronglet.mesh = entity;
  }

  async createHealthHalo(thronglet) {
    const halo = document.createElement('a-entity');
    halo.setAttribute('position', `${thronglet.position.x} ${thronglet.position.y + 1} ${thronglet.position.z}`);
    halo.setAttribute('light', `type: point; color: ${thronglet.getHealthColor()}; intensity: 1; distance: 3`);
    halo.setAttribute('class', 'health-halo');
    halo.setAttribute('data-id', thronglet.id);
    
    this.throngletsContainer.appendChild(halo);
    thronglet.halo = halo;
  }

  async createNameplate(thronglet) {
    const nameplate = document.createElement('a-entity');
    nameplate.setAttribute('position', `${thronglet.position.x} ${thronglet.position.y + 2} ${thronglet.position.z}`);
    nameplate.setAttribute('text', `
      align: center;
      color: #ffffff;
      fontSize: 0.5;
      value: ${thronglet.name};
      width: 4;
    `);
    nameplate.setAttribute('class', 'nameplate');
    nameplate.setAttribute('data-id', thronglet.id);
    
    this.throngletsContainer.appendChild(nameplate);
    thronglet.nameplate = nameplate;
  }

  async createConnections() {
    if (!VRState.config || !VRState.config.relationships) {
      console.warn('⚠ No relationships data in configuration');
      return;
    }

    const container = this.connectionsContainer;
    
    for (const data of VRState.config.relationships) {
      const fromThronglet = VRState.thronglets.find(t => t.id === data.from);
      const toThronglet = VRState.thronglets.find(t => t.id === data.to);
      
      if (fromThronglet && toThronglet) {
        const connection = new Connection(data, fromThronglet, toThronglet);
        VRState.connections.push(connection);
        
        // Create connection line
        await this.createConnectionLine(connection, container);
      }
    }

    console.log(`✓ Created ${VRState.connections.length} connections`);
  }

  async createConnectionLine(connection, container) {
    const fromPos = connection.fromThronglet.position;
    const toPos = connection.toThronglet.position;
    
    // Calculate line properties
    const distance = Math.sqrt(
      Math.pow(toPos.x - fromPos.x, 2) +
      Math.pow(toPos.y - fromPos.y, 2) +
      Math.pow(toPos.z - fromPos.z, 2)
    );
    
    const angle = Math.atan2(toPos.z - fromPos.z, toPos.x - fromPos.x);
    const midX = (fromPos.x + toPos.x) / 2;
    const midY = (fromPos.y + toPos.y) / 2 + 0.5;
    const midZ = (fromPos.z + toPos.z) / 2;

    const line = document.createElement('a-line');
    line.setAttribute('color', connection.color);
    line.setAttribute('opacity', '0.6');
    line.setAttribute('width', '0.1');
    line.setAttribute('position', `${midX} ${midY} ${midZ}`);
    line.setAttribute('rotation', `0 ${angle * (180 / Math.PI)} 0`);
    line.setAttribute('scale', `1 ${distance} 1`);
    line.setAttribute('class', 'connection-line');
    line.setAttribute('data-from', connection.from);
    line.setAttribute('data-to', connection.to);
    
    container.appendChild(line);
    connection.line = line;
  }

  setupEventHandlers() {
    // Raycaster click handler
    const cursor = document.getElementById('cursor');
    cursor.addEventListener('click', (event) => {
      const target = event.detail.target;
      if (target && target.hasAttribute('data-id')) {
        const throngletId = target.getAttribute('data-id');
        this.selectThronglet(throngletId);
      }
    });

    // Keyboard handlers
    document.addEventListener('keydown', (event) => {
      this.handleKeyboard(event);
    });

    // Window resize handler
    window.addEventListener('resize', () => {
      this.handleResize();
    });

    // VR mode handlers
    document.addEventListener('enter-vr', () => {
      this.onEnterVR();
    });

    document.addEventListener('exit-vr', () => {
      this.onExitVR();
    });
  }

  handleKeyboard(event) {
    // Teleport to thronglets (1-5)
    if (event.key >= '1' && event.key <= '5') {
      const index = parseInt(event.key) - 1;
      if (VRState.thronglets[index]) {
        this.teleportToThronglet(index);
      }
    }

    // Deselect on ESC
    if (event.key === 'Escape') {
      this.deselectThronglet();
    }

    // Toggle settings
    if (event.key === 'N' || event.key === 'n') {
      this.toggleNameplates();
    }
    if (event.key === 'C' || event.key === 'c') {
      this.toggleConnections();
    }
    if (event.key === 'H' || event.key === 'h') {
      this.toggleHealthHalos();
    }
    if (event.key === 'D' || event.key === 'd') {
      this.toggleDebug();
    }
  }

  selectThronglet(id) {
    const thronglet = VRState.thronglets.find(t => t.id === id);
    if (!thronglet) return;

    // Deselect previous
    if (VRState.selectedThronglet) {
      this.deselectThronglet();
    }

    VRState.selectedThronglet = thronglet;
    this.showDetailPanel(thronglet);
    this.updateDebugPanel();

    // Highlight selection
    if (thronglet.mesh) {
      thronglet.mesh.setAttribute('animation', 'property: scale; to: 1.2 1.2 1.2; dur: 200; easing: easeOutQuad');
    }
  }

  deselectThronglet() {
    if (VRState.selectedThronglet) {
      const thronglet = VRState.selectedThronglet;
      
      // Reset scale
      if (thronglet.mesh) {
        thronglet.mesh.setAttribute('animation', 'property: scale; to: 1 1 1; dur: 200; easing: easeOutQuad');
      }

      // Hide detail panel
      closeDetailPanel();
      
      VRState.selectedThronglet = null;
      this.updateDebugPanel();
    }
  }

  showDetailPanel(thronglet) {
    const panel = document.getElementById('detail-panel');
    const content = document.getElementById('panel-content');
    
    // Update panel content
    document.getElementById('panel-name').textContent = thronglet.name;
    document.getElementById('panel-role').textContent = thronglet.role;
    document.getElementById('panel-health').innerHTML = thronglet.getHealthBadge();
    document.getElementById('panel-mood').textContent = thronglet.mood;
    document.getElementById('panel-tokens').textContent = thronglet.tokenCount;
    document.getElementById('panel-position').textContent = 
      `X: ${thronglet.position.x.toFixed(2)}, Y: ${thronglet.position.y.toFixed(2)}, Z: ${thronglet.position.z.toFixed(2)}`;

    // Show panel
    panel.classList.add('visible');
    document.body.style.overflow = 'hidden';
  }

  teleportToThronglet(index) {
    const thronglet = VRState.thronglets[index];
    if (!thronglet) return;

    const camera = document.querySelector('[camera]');
    if (camera) {
      camera.setAttribute('position', `${thronglet.position.x} ${thronglet.position.y + 1.6} ${thronglet.position.z}`);
    }

    // Show proximity alert
    this.showProximityAlert(`Teleported to ${thronglet.name}`);
  }

  showProximityAlert(message) {
    const alert = document.getElementById('proximity-alert');
    const alertText = document.getElementById('alert-text');
    
    alertText.textContent = message;
    alert.classList.add('visible');
    
    setTimeout(() => {
      alert.classList.remove('visible');
    }, 3000);
  }

  toggleNameplates() {
    VRState.settings.showNameplates = !VRState.settings.showNameplates;
    this.updateNameplatesVisibility();
    
    const button = document.getElementById('toggle-nameplates');
    button.classList.toggle('active', VRState.settings.showNameplates);
  }

  toggleConnections() {
    VRState.settings.showConnections = !VRState.settings.showConnections;
    this.updateConnectionsVisibility();
    
    const button = document.getElementById('toggle-connections');
    button.classList.toggle('active', VRState.settings.showConnections);
  }

  toggleHealthHalos() {
    VRState.settings.showHealthHalos = !VRState.settings.showHealthHalos;
    this.updateHealthHalosVisibility();
    
    const button = document.getElementById('toggle-health');
    button.classList.toggle('active', VRState.settings.showHealthHalos);
  }

  toggleDebug() {
    VRState.settings.debugMode = !VRState.settings.debugMode;
    this.updateDebugPanel();
    
    const button = document.getElementById('toggle-debug');
    button.classList.toggle('active', VRState.settings.debugMode);
  }

  updateNameplatesVisibility() {
    const nameplates = document.querySelectorAll('.nameplate');
    nameplates.forEach(nameplate => {
      nameplate.setAttribute('visible', VRState.settings.showNameplates);
    });
  }

  updateConnectionsVisibility() {
    const connections = document.querySelectorAll('.connection-line');
    connections.forEach(connection => {
      connection.setAttribute('visible', VRState.settings.showConnections);
    });
  }

  updateHealthHalosVisibility() {
    const halos = document.querySelectorAll('.health-halo');
    halos.forEach(halo => {
      halo.setAttribute('visible', VRState.settings.showHealthHalos);
    });
  }

  updateDebugPanel() {
    if (!VRState.settings.debugMode) return;

    document.getElementById('debug-thronglet-count').textContent = VRState.thronglets.length;
    document.getElementById('debug-connection-count').textContent = VRState.connections.length;
    document.getElementById('debug-selected').textContent = 
      VRState.selectedThronglet ? VRState.selectedThronglet.name : 'None';
  }

  handleResize() {
    // A-Frame handles most resize automatically
    // Add any custom resize logic here if needed
  }

  onEnterVR() {
    const indicator = document.getElementById('vr-indicator');
    indicator.classList.add('visible');
  }

  onExitVR() {
    const indicator = document.getElementById('vr-indicator');
    indicator.classList.remove('visible');
  }

  showError(message) {
    console.error('Error:', message);
    // Could add a UI error notification here
  }

  startSimulation() {
    // Simulation loop
    setInterval(() => {
      this.updateSimulation();
    }, 1000); // Update every second
  }

  updateSimulation() {
    // Update thronglet states
    VRState.thronglets.forEach(thronglet => {
      thronglet.updateTimestamp();
    });

    // Check for proximity alerts
    this.checkProximityAlerts();

    // Update debug panel
    this.updateDebugPanel();
  }

  checkProximityAlerts() {
    // Check for critical thronglets
    const criticalThronglets = VRState.thronglets.filter(t => t.health === 'critical');
    
    if (criticalThronglets.length > 0) {
      const alert = document.getElementById('proximity-alert');
      const alertText = document.getElementById('alert-text');
      
      alertText.textContent = `⚠ ${criticalThronglets.length} Critical Thronglet(s) Detected!`;
      alert.classList.add('visible');
      
      setTimeout(() => {
        alert.classList.remove('visible');
      }, 5000);
    }
  }
}

// Global functions for HTML event handlers
function initThrongletsVR() {
  VRState.practiceMode = new VRPracticeMode();
}

function closeDetailPanel() {
  const panel = document.getElementById('detail-panel');
  panel.classList.remove('visible');
  document.body.style.overflow = '';
}

function toggleNameplatesVisibility() {
  if (VRState.practiceMode) {
    VRState.practiceMode.toggleNameplates();
  }
}

function toggleConnectionsVisibility() {
  if (VRState.practiceMode) {
    VRState.practiceMode.toggleConnections();
  }
}

function toggleHealthHalosVisibility() {
  if (VRState.practiceMode) {
    VRState.practiceMode.toggleHealthHalos();
  }
}

function toggleDebugMode() {
  if (VRState.practiceMode) {
    VRState.practiceMode.toggleDebug();
  }
}

function teleportToThronglet(index) {
  if (VRState.practiceMode) {
    VRState.practiceMode.teleportToThronglet(index);
  }
}

function deselectThronglet() {
  if (VRState.practiceMode) {
    VRState.practiceMode.deselectThronglet();
  }
}

function handleResize() {
  if (VRState.practiceMode) {
    VRState.practiceMode.handleResize();
  }
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    VRState,
    Thronglet,
    Connection,
    VRPracticeMode
  };
}
