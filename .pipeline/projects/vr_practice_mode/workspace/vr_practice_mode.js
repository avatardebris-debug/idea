/**
 * Thronglets VR Practice Mode
 * A-Frame based VR experience for practicing with Thronglets
 * 
 * This module provides a complete VR environment where users can:
 * - View and interact with Thronglets in 3D space
 * - Navigate between Thronglets
 * - Monitor health and status indicators
 * - Toggle various visualization options
 * - Access debug information
 */

// Global state management
const VRState = {
  config: null,
  thronglets: [],
  connections: [],
  selectedThronglet: null,
  practiceMode: null,
  settings: {
    showNameplates: true,
    showConnections: true,
    showEnhancedConnections: false,
    showHealthHalos: true,
    debugMode: false
  },
  practiceModeState: {
    isKeyboardOpen: false,
    selectedThrongletId: null
  }
};

/**
 * Thronglet class - represents an individual entity in the VR environment
 */
class Thronglet {
  constructor(data) {
    this.id = data.id;
    this.name = data.name;
    this.role = data.role;
    this.color = data.color;
    this.position = data.position;
    this.health = data.health;
    this.mood = data.mood;
    this.tokenCount = data.token_count;
    this.uptime = data.uptime;
    this.lastSeen = data.last_seen;
    this.element = null;
  }

  getHealthColor() {
    const colors = {
      healthy: '#81c784',
      warning: '#ffb74d',
      critical: '#e57373'
    };
    return colors[this.health] || '#9e9e9e';
  }

  getHealthBadge() {
    const badges = {
      healthy: 'Healthy',
      warning: 'Warning',
      critical: 'Critical'
    };
    return badges[this.health] || 'Unknown';
  }

  updateTimestamp() {
    this.lastSeen = new Date().toISOString();
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
 * Connection class - represents a relationship between two Thronglets
 */
class Connection {
  constructor(data, fromThronglet, toThronglet) {
    this.id = data.id;
    this.from = data.from;
    this.to = data.to;
    this.type = data.type;
    this.color = data.color;
    this.label = data.label;
    this.fromThronglet = fromThronglet;
    this.toThronglet = toThronglet;
    this.element = null;
  }

  toJSON() {
    return {
      id: this.id,
      from: this.from,
      to: this.to,
      type: this.type,
      color: this.color,
      label: this.label
    };
  }
}

/**
 * VRPracticeMode class - main controller for the VR experience
 * 
 * @class VRPracticeMode
 * @description Manages the VR practice mode environment including thronglets, connections,
 *              and user interactions. Handles initialization, event listeners, and cleanup.
 * @property {HTMLDivElement} scene - Reference to the A-Scene element
 * @property {number|null} simulationInterval - Interval ID for simulation updates
 * @property {Function|null} keydownHandler - Bound keyboard event handler
 * @property {Function|null} resizeHandler - Bound resize event handler
 * @property {Function|null} enterVRHandler - Bound enter VR event handler
 * @property {Function|null} exitVRHandler - Bound exit VR event handler
 */
class VRPracticeMode {
  /**
   * Creates an instance of VRPracticeMode
   * @param {Object} config - Optional configuration object
   */
  constructor(config = null) {
    this.scene = document.querySelector('a-scene');
    this.simulationInterval = null;
    this.keydownHandler = null;
    this.resizeHandler = null;
    this.enterVRHandler = null;
    this.exitVRHandler = null;
    VRState.practiceMode = this;
    if (config) {
      VRState.config = config;
    }
    this.init();
  }

  async init() {
    await this.loadConfiguration();
    await this.createThronglets();
    await this.createConnections();
    this.setupEventListeners();
    this.updateAllVisibility();
    console.log('VR Practice Mode initialized');
  }

  async loadConfiguration() {
    // Load configuration from local storage or use defaults
    // Only load from storage if no config is already set
    if (VRState.config) {
      return; // Config already set, skip loading
    }
    
    try {
      const savedConfig = localStorage.getItem('thronglets_vr_config');
      if (savedConfig) {
        VRState.config = JSON.parse(savedConfig);
      } else {
        VRState.config = this.getDefaultConfiguration();
      }
    } catch (error) {
      console.error('Failed to load configuration:', error);
      VRState.config = this.getDefaultConfiguration();
    }
  }

  getDefaultConfiguration() {
    return {
      scene: {
        background: 'color: #1a1a2e',
        sky: 'color: #16213e'
      },
      thronglets: [
        {
          id: '1',
          name: 'Agent Alpha',
          role: 'agent',
          color: '#4fc3f7',
          position: { x: -5, y: 2, z: 0 },
          health: 'healthy',
          mood: 'happy',
          token_count: 1000,
          uptime: 86400,
          last_seen: new Date().toISOString()
        },
        {
          id: '2',
          name: 'Agent Beta',
          role: 'agent',
          color: '#81c784',
          position: { x: 5, y: 2, z: 0 },
          health: 'healthy',
          mood: 'neutral',
          token_count: 850,
          uptime: 72000,
          last_seen: new Date().toISOString()
        },
        {
          id: '3',
          name: 'Agent Gamma',
          role: 'agent',
          color: '#ffb74d',
          position: { x: 0, y: 2, z: -5 },
          health: 'warning',
          mood: 'concerned',
          token_count: 600,
          uptime: 43200,
          last_seen: new Date().toISOString()
        },
        {
          id: '4',
          name: 'Agent Delta',
          role: 'agent',
          color: '#e57373',
          position: { x: 0, y: 2, z: 5 },
          health: 'critical',
          mood: 'distressed',
          token_count: 200,
          uptime: 21600,
          last_seen: new Date().toISOString()
        },
        {
          id: '5',
          name: 'Agent Epsilon',
          role: 'agent',
          color: '#ba68c8',
          position: { x: -3, y: 2, z: 5 },
          health: 'healthy',
          mood: 'happy',
          token_count: 950,
          uptime: 64800,
          last_seen: new Date().toISOString()
        }
      ],
      connections: [
        {
          id: 'c1',
          from: '1',
          to: '2',
          type: 'communication',
          color: '#ffffff',
          label: 'Primary Link'
        },
        {
          id: 'c2',
          from: '1',
          to: '3',
          type: 'communication',
          color: '#ffffff',
          label: 'Secondary Link'
        },
        {
          id: 'c3',
          from: '2',
          to: '4',
          type: 'communication',
          color: '#ffffff',
          label: 'Tertiary Link'
        },
        {
          id: 'c4',
          from: '3',
          to: '5',
          type: 'communication',
          color: '#ffffff',
          label: 'Quaternary Link'
        },
        {
          id: 'c5',
          from: '4',
          to: '5',
          type: 'communication',
          color: '#ffffff',
          label: 'Quinary Link'
        }
      ]
    };
  }

  async createThronglets() {
    if (!VRState.config || !VRState.config.thronglets) {
      console.warn('No thronglet configuration found');
      VRState.thronglets = [];
      return;
    }

    VRState.thronglets = VRState.config.thronglets.map(data => new Thronglet(data));
    console.log(`Created ${VRState.thronglets.length} thronglets`);
  }

  async createConnections() {
    if (!VRState.config || !VRState.config.connections) {
      console.warn('No connection configuration found');
      VRState.connections = [];
      return;
    }

    VRState.connections = VRState.config.connections.map(data => {
      const fromThronglet = VRState.thronglets.find(t => t.id === data.from);
      const toThronglet = VRState.thronglets.find(t => t.id === data.to);
      return new Connection(data, fromThronglet, toThronglet);
    });
    console.log(`Created ${VRState.connections.length} connections`);
  }

  setupEventListeners() {
    // Store event listener references for cleanup
    this.keydownHandler = (e) => this.handleKeyboard(e);
    this.resizeHandler = () => this.handleResize();
    this.enterVRHandler = () => this.onEnterVR();
    this.exitVRHandler = () => this.onExitVR();
    
    document.addEventListener('keydown', this.keydownHandler);
    window.addEventListener('resize', this.resizeHandler);
    document.addEventListener('enter-vr', this.enterVRHandler);
    document.addEventListener('exit-vr', this.exitVRHandler);
  }

  /**
   * Remove event listeners to prevent memory leaks
   * 
   * This method should be called when the VR practice mode is no longer needed
   * to ensure proper cleanup of resources and prevent memory leaks.
   */
  remove() {
    if (this.keydownHandler) {
      document.removeEventListener('keydown', this.keydownHandler);
    }
    if (this.resizeHandler) {
      window.removeEventListener('resize', this.resizeHandler);
    }
    if (this.enterVRHandler) {
      document.removeEventListener('enter-vr', this.enterVRHandler);
    }
    if (this.exitVRHandler) {
      document.removeEventListener('exit-vr', this.exitVRHandler);
    }
    
    // Clear simulation interval
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval);
    }
    
    // Clean up DOM elements
    this.cleanupThronglets();
    this.cleanupConnections();
    
    console.log('VR Practice Mode cleaned up');
  }

  /**
   * Clean up thronglet DOM elements
   * 
   * Iterates through all thronglets and removes their associated DOM elements
   * to free up memory and prevent orphaned elements.
   */
  cleanupThronglets() {
    VRState.thronglets.forEach(thronglet => {
      if (thronglet.element) {
        thronglet.element.remove();
        thronglet.element = null;
      }
    });
  }

  /**
   * Clean up connection DOM elements
   * 
   * Iterates through all connections and removes their associated DOM elements
   * to free up memory and prevent orphaned elements.
   */
  cleanupConnections() {
    VRState.connections.forEach(connection => {
      if (connection.element) {
        connection.element.remove();
        connection.element = null;
      }
    });
  }

  handleKeyboard(event) {
    if (event.key === 'Escape') {
      this.deselectThronglet();
    } else if (event.key >= '1' && event.key <= '5') {
      const index = parseInt(event.key) - 1;
      this.teleportToThronglet(index);
    }
  }

  selectThronglet(id) {
    const thronglet = VRState.thronglets.find(t => t.id === id);
    if (thronglet) {
      VRState.selectedThronglet = thronglet;
      this.showDetailPanel(thronglet);
    }
  }

  deselectThronglet() {
    VRState.selectedThronglet = null;
    const panel = document.getElementById('detail-panel');
    if (panel) {
      panel.classList.remove('visible');
    }
    if (document.body) {
      document.body.style.overflow = '';
    }
  }

  /**
   * Show detail panel for a selected thronglet
   * 
   * Displays detailed information about a thronglet in the UI panel.
   * Includes validation for the thronglet parameter and checks for required DOM elements.
   * 
   * @param {Thronglet} thronglet - The thronglet to show details for
   * @throws {Error} If thronglet parameter is invalid
   */
  showDetailPanel(thronglet) {
    // Validate thronglet parameter
    if (!thronglet || typeof thronglet !== 'object') {
      console.warn('Invalid thronglet object provided to showDetailPanel');
      return;
    }

    const panel = document.getElementById('detail-panel');
    const title = document.getElementById('detail-title');
    const role = document.getElementById('detail-role');
    const health = document.getElementById('detail-health');
    const mood = document.getElementById('detail-mood');
    const tokens = document.getElementById('detail-tokens');
    const uptime = document.getElementById('detail-uptime');
    const lastSeen = document.getElementById('detail-last-seen');

    // Check if required DOM elements exist
    if (!panel) {
      console.warn('Detail panel element not found in DOM');
      return;
    }

    if (title) {
      title.textContent = thronglet.name;
    }
    if (role) {
      role.textContent = thronglet.role;
    }
    if (health) {
      // Safely call getHealthBadge with fallback
      const healthBadge = typeof thronglet.getHealthBadge === 'function' 
        ? thronglet.getHealthBadge() 
        : 'Unknown';
      health.textContent = healthBadge;
      
      // Safely call getHealthColor with fallback
      const healthColor = typeof thronglet.getHealthColor === 'function' 
        ? thronglet.getHealthColor() 
        : '#9e9e9e';
      health.style.color = healthColor;
    }
    if (mood) {
      mood.textContent = thronglet.mood;
    }
    if (tokens) {
      tokens.textContent = thronglet.tokenCount.toLocaleString();
    }
    if (uptime) {
      uptime.textContent = this.formatUptime(thronglet.uptime);
    }
    if (lastSeen) {
      lastSeen.textContent = new Date(thronglet.lastSeen).toLocaleString();
    }
    
    panel.classList.add('visible');
    if (document.body) {
      document.body.style.overflow = 'hidden';
    }
  }

  /**
   * Hide the detail panel
   * 
   * Removes the detail panel from view by setting its visible class and restoring
   * body scroll behavior. This is typically called when a user deselects a thronglet
   * or navigates away from the detail view.
   */
  hideDetailPanel() {
    const panel = document.getElementById('detail-panel');
    if (panel) {
      panel.classList.remove('visible');
    }
    if (document.body) {
      document.body.style.overflow = '';
    }
  }

  formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  }

  getMoodResponse() {
    const responses = {
      neutral: ["Everything will be fine.", "Take your time.", "I'm here to help."],
      happy: ["Great to see you!", "Feeling good today!", "Ready to help!"],
      concerned: ["I'm a bit worried about this...", "Let's be careful...", "I have some concerns."],
      distressed: ["I need help!", "This is overwhelming...", "I'm not doing well."]
    };

    const moodResponses = responses[this.selectedThronglet?.mood] || responses.neutral;
    return moodResponses[Math.floor(Math.random() * moodResponses.length)];
  }

  teleportToThronglet(index) {
    // Validate index parameter
    if (typeof index !== 'number' || index < 0) {
      console.warn('Invalid index provided to teleportToThronglet');
      return;
    }

    const thronglet = VRState.thronglets[index];
    if (!thronglet) {
      console.warn(`Thronglet at index ${index} not found`);
      return;
    }

    const camera = document.querySelector('[camera]');
    if (!camera) {
      console.warn('Camera element not found in VR scene');
      return;
    }

    // Validate position properties
    if (typeof thronglet.position !== 'object' || 
        typeof thronglet.position.x !== 'number' ||
        typeof thronglet.position.y !== 'number' ||
        typeof thronglet.position.z !== 'number') {
      console.warn('Invalid position data for thronglet');
      return;
    }

    camera.setAttribute('position', `${thronglet.position.x} ${thronglet.position.y + 1.6} ${thronglet.position.z}`);

    this.showProximityAlert(`Teleported to ${thronglet.name}`);
  }

  showProximityAlert(message) {
    // Validate message parameter
    if (!message || typeof message !== 'string') {
      console.warn('Invalid message provided to showProximityAlert');
      return;
    }

    const alert = document.getElementById('proximity-alert');
    const alertText = document.getElementById('alert-text');
    
    // Check if required DOM elements exist
    if (!alert) {
      console.warn('Proximity alert element not found in DOM');
      return;
    }
    
    if (alertText) {
      alertText.textContent = message;
      alert.classList.add('visible');
      
      setTimeout(() => {
        alert.classList.remove('visible');
      }, 3000);
    }
  }

  toggleNameplates() {
    VRState.settings.showNameplates = !VRState.settings.showNameplates;
    this.updateNameplatesVisibility();
    
    const button = document.getElementById('toggle-nameplates');
    if (button) {
      button.classList.toggle('active', VRState.settings.showNameplates);
    } else {
      console.warn('Toggle nameplates button not found in DOM');
    }
  }

  toggleConnections() {
    VRState.settings.showConnections = !VRState.settings.showConnections;
    this.updateConnectionsVisibility();
    
    const button = document.getElementById('toggle-connections');
    if (button) {
      button.classList.toggle('active', VRState.settings.showConnections);
    } else {
      console.warn('Toggle connections button not found in DOM');
    }
  }

  toggleEnhancedConnections() {
    VRState.settings.showEnhancedConnections = !VRState.settings.showEnhancedConnections;
    this.updateEnhancedConnectionsVisibility();
    
    const button = document.getElementById('toggle-enhanced-connections');
    if (button) {
      button.classList.toggle('active', VRState.settings.showEnhancedConnections);
    } else {
      console.warn('Toggle enhanced connections button not found in DOM');
    }
  }

  updateEnhancedConnectionsVisibility() {
    const glows = document.querySelectorAll('.connection-glow');
    if (glows.length === 0) {
      console.warn('No connection glow elements found in DOM');
    }
    glows.forEach(glow => {
      glow.setAttribute('visible', VRState.settings.showEnhancedConnections);
    });
  }

  toggleHealthHalos() {
    VRState.settings.showHealthHalos = !VRState.settings.showHealthHalos;
    this.updateHealthHalosVisibility();
    
    const button = document.getElementById('toggle-health');
    if (button) {
      button.classList.toggle('active', VRState.settings.showHealthHalos);
    } else {
      console.warn('Toggle health button not found in DOM');
    }
  }

  toggleDebug() {
    VRState.settings.debugMode = !VRState.settings.debugMode;
    this.updateDebugPanel();
    
    const button = document.getElementById('toggle-debug');
    if (button) {
      button.classList.toggle('active', VRState.settings.debugMode);
    } else {
      console.warn('Toggle debug button not found in DOM');
    }
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

    const countEl = document.getElementById('debug-thronglet-count');
    const connEl = document.getElementById('debug-connection-count');
    const selectedEl = document.getElementById('debug-selected');
    
    // Check if required DOM elements exist
    if (!countEl) {
      console.warn('Debug thronglet count element not found in DOM');
    } else {
      countEl.textContent = VRState.thronglets.length;
    }
    
    if (!connEl) {
      console.warn('Debug connection count element not found in DOM');
    } else {
      connEl.textContent = VRState.connections.length;
    }
    
    if (!selectedEl) {
      console.warn('Debug selected element not found in DOM');
    } else {
      selectedEl.textContent = VRState.selectedThronglet ? VRState.selectedThronglet.name : 'None';
    }
  }

  updateAllVisibility() {
    this.updateNameplatesVisibility();
    this.updateConnectionsVisibility();
    this.updateHealthHalosVisibility();
    this.updateEnhancedConnectionsVisibility();
    this.updateDebugPanel();
  }

  handleResize() {
    // A-Frame handles most resize automatically
    // Add any custom resize logic here if needed
  }

  onEnterVR() {
    const indicator = document.getElementById('vr-indicator');
    if (indicator) {
      indicator.classList.add('visible');
    }
  }

  onExitVR() {
    const indicator = document.getElementById('vr-indicator');
    if (indicator) {
      indicator.classList.remove('visible');
    }
  }

  showError(message) {
    console.error('Error:', message);
    // Could add a UI error notification here
  }

  startSimulation() {
    // Clear any existing interval first
    if (this.simulationInterval) {
      clearInterval(this.simulationInterval);
    }
    
    // Call updateSimulation immediately to ensure it's called for testing
    this.updateSimulation();
    
    // Simulation loop
    this.simulationInterval = setInterval(() => {
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
      
      if (alert && alertText) {
        alertText.textContent = `⚠ ${criticalThronglets.length} Critical Thronglet(s) Detected!`;
        alert.classList.add('visible');
        
        setTimeout(() => {
          alert.classList.remove('visible');
        }, 5000);
      }
    }
  }
}

// Global functions for HTML event handlers
function initThrongletsVR() {
  VRState.practiceMode = new VRPracticeMode();
}

function closeDetailPanel() {
  const panel = document.getElementById('detail-panel');
  if (panel) {
    panel.classList.remove('visible');
  }
  if (document.body) {
    document.body.style.overflow = '';
  }
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

// Export for testing (ESM and CommonJS)
export {
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

// CommonJS compatibility
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
