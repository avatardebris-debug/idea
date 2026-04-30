/**
 * Thronglets VR Component
 * A-Frame component for creating and managing Thronglet entities in VR
 */

AFRAME.registerComponent('thronglet-entity', {
  schema: {
    id: {type: 'string', default: ''},
    name: {type: 'string', default: ''},
    role: {type: 'string', default: ''},
    color: {type: 'string', default: '#4fc3f7'},
    health: {type: 'string', default: 'healthy'},
    position: {type: 'vec3', default: {x: 0, y: 2, z: 0}},
    // Configurable animation parameters
    animationDuration: {type: 'number', default: 2000},
    animationScale: {type: 'number', default: 1.1},
    haloScale: {type: 'number', default: 1.2},
    haloDuration: {type: 'number', default: 1500}
  },

  init: function() {
    this.createThrongletEntity();
    this.createNameplate();
    this.createHealthHalo();
    this.setupEventListeners();
    
    // Validate required elements exist
    if (!this.el.querySelector('a-sphere') || !this.el.querySelector('.nameplate') || !this.el.querySelector('.health-halo')) {
      console.error('VRPracticeMode: Required elements not created successfully');
    }
  },

  update: function(oldData) {
    if (oldData.color !== this.data.color) {
      this.updateColor();
    }
    if (oldData.health !== this.data.health) {
      this.updateHealthHalo();
    }
  },

  createThrongletEntity: function() {
    const el = this.el;
    const data = this.data;

    // Create main sphere
    const sphere = document.createElement('a-sphere');
    sphere.setAttribute('radius', '0.5');
    sphere.setAttribute('color', data.color);
    sphere.setAttribute('position', `${data.position.x} ${data.position.y} ${data.position.z}`);
    sphere.setAttribute('data-thronglet-id', data.id);
    sphere.setAttribute('class', 'clickable');
    sphere.setAttribute('animation', `property: scale; to: ${data.animationScale} ${data.animationScale} ${data.animationScale}; dir: alternate; loop: true; dur: ${data.animationDuration}ms; easing: ease-in-out`);
    
    el.appendChild(sphere);

    // Add glow effect
    const glow = document.createElement('a-sphere');
    glow.setAttribute('radius', '0.6');
    glow.setAttribute('color', data.color);
    glow.setAttribute('opacity', '0.3');
    glow.setAttribute('position', `0 0 0.01`);
    glow.setAttribute('class', 'connection-glow');
    glow.setAttribute('visible', 'false');
    
    el.appendChild(glow);
  },

  createNameplate: function() {
    const el = this.el;
    const data = this.data;

    // Create nameplate container
    const nameplate = document.createElement('a-entity');
    nameplate.setAttribute('class', 'nameplate');
    nameplate.setAttribute('position', `0 1.5 0`);
    nameplate.setAttribute('look-at', '[camera]');

    // Create background
    const bg = document.createElement('a-plane');
    bg.setAttribute('width', '2');
    bg.setAttribute('height', '0.8');
    bg.setAttribute('color', 'rgba(26, 26, 46, 0.9)');
    bg.setAttribute('opacity', '0.9');
    bg.setAttribute('rotation', '0 0 0');

    // Create text
    const text = document.createElement('a-text');
    text.setAttribute('value', data.name);
    text.setAttribute('color', '#ffffff');
    text.setAttribute('align', 'center');
    text.setAttribute('width', '180');
    text.setAttribute('position', '0 0 0.01');
    text.setAttribute('font', 'monospace');

    nameplate.appendChild(bg);
    nameplate.appendChild(text);
    el.appendChild(nameplate);
  },

  createHealthHalo: function() {
    const el = this.el;
    const data = this.data;

    // Create health halo
    const halo = document.createElement('a-sphere');
    halo.setAttribute('radius', '0.8');
    halo.setAttribute('color', this.getHealthColor(data.health));
    halo.setAttribute('opacity', '0.4');
    halo.setAttribute('position', `0 0 0.01`);
    halo.setAttribute('class', 'health-halo');
    halo.setAttribute('visible', 'false');
    halo.setAttribute('animation', `property: scale; to: ${data.haloScale} ${data.haloScale} ${data.haloScale}; dir: alternate; loop: true; dur: ${data.haloDuration}ms; easing: ease-in-out`);

    el.appendChild(halo);
  },

  getHealthColor: function(health) {
    const colors = {
      healthy: '#81c784',
      warning: '#ffb74d',
      critical: '#e57373'
    };
    return colors[health] || '#9e9e9e';
  },

  updateColor: function() {
    const data = this.data;
    const sphere = this.el.querySelector('a-sphere');
    const glow = this.el.querySelector('.connection-glow');
    
    if (!sphere || !glow) {
      console.warn('VRPracticeMode: Required elements missing for color update');
      return;
    }
    
    sphere.setAttribute('color', data.color);
    glow.setAttribute('color', data.color);
  },

  updateHealthHalo: function() {
    const data = this.data;
    const halo = this.el.querySelector('.health-halo');
    
    if (!halo) {
      console.warn('VRPracticeMode: Halo element missing for health update');
      return;
    }
    
    halo.setAttribute('color', this.getHealthColor(data.health));
  },

  setupEventListeners: function() {
    const sphere = this.el.querySelector('.clickable');
    if (sphere) {
      // Store listener reference for cleanup
      this.clickListener = () => {
        const id = this.el.getAttribute('data-thronglet-id');
        if (VRState.practiceMode) {
          VRState.practiceMode.selectThronglet(id);
        }
      };
      sphere.addEventListener('click', this.clickListener);
    }
  },

  remove: function() {
    // Cleanup event listeners
    if (this.clickListener && this.el.querySelector('.clickable')) {
      this.el.querySelector('.clickable').removeEventListener('click', this.clickListener);
    }
  }
});

AFRAME.registerComponent('connection-line', {
  schema: {
    from: {type: 'string'},
    to: {type: 'string'},
    color: {type: 'string', default: '#ffffff'},
    label: {type: 'string', default: ''}
  },

  init: function() {
    this.createConnectionLine();
    this.createConnectionLabel();
  },

  createConnectionLine: function() {
    const el = this.el;
    const data = this.data;

    // Find source and target entities
    const fromEntity = document.querySelector(`[data-thronglet-id="${data.from}"]`);
    const toEntity = document.querySelector(`[data-thronglet-id="${data.to}"]`);

    if (!fromEntity || !toEntity) {
      console.warn('Could not find thronglet entities for connection');
      return;
    }

    // Get positions
    const fromPos = fromEntity.object3D.position;
    const toPos = toEntity.object3D.position;

    // Create line
    const line = document.createElement('a-line');
    line.setAttribute('start', `${fromPos.x} ${fromPos.y} ${fromPos.z}`);
    line.setAttribute('end', `${toPos.x} ${toPos.y} ${toPos.z}`);
    line.setAttribute('color', data.color);
    line.setAttribute('width', '0.05');
    line.setAttribute('opacity', '0.6');
    line.setAttribute('class', 'connection-line');
    line.setAttribute('visible', 'false');

    el.appendChild(line);
  },

  createConnectionLabel: function() {
    const el = this.el;
    const data = this.data;

    if (!data.label) return;

    // Find source and target entities
    const fromEntity = document.querySelector(`[data-thronglet-id="${data.from}"]`);
    const toEntity = document.querySelector(`[data-thronglet-id="${data.to}"]`);

    if (!fromEntity || !toEntity) return;

    // Get positions and calculate midpoint
    const fromPos = fromEntity.object3D.position;
    const toPos = toEntity.object3D.position;
    const midX = (fromPos.x + toPos.x) / 2;
    const midY = (fromPos.y + toPos.y) / 2;
    const midZ = (fromPos.z + toPos.z) / 2;

    // Create label
    const label = document.createElement('a-text');
    label.setAttribute('value', data.label);
    label.setAttribute('color', '#ffffff');
    label.setAttribute('align', 'center');
    label.setAttribute('width', '100');
    label.setAttribute('position', `${midX} ${midY + 0.5} ${midZ}`);
    label.setAttribute('look-at', '[camera]');
    label.setAttribute('font', 'monospace');

    el.appendChild(label);
  },

  update: function(oldData) {
    if (oldData.from !== this.data.from || oldData.to !== this.data.to) {
      this.updateLine();
    }
  },

  updateLine: function() {
    const el = this.el;
    const data = this.data;

    const fromEntity = document.querySelector(`[data-thronglet-id="${data.from}"]`);
    const toEntity = document.querySelector(`[data-thronglet-id="${data.to}"]`);

    if (!fromEntity || !toEntity) return;

    const fromPos = fromEntity.object3D.position;
    const toPos = toEntity.object3D.position;

    const line = el.querySelector('a-line');
    if (line) {
      line.setAttribute('start', `${fromPos.x} ${fromPos.y} ${fromPos.z}`);
      line.setAttribute('end', `${toPos.x} ${toPos.y} ${toPos.z}`);
    }
  }
});

AFRAME.registerComponent('thronglet-manager', {
  schema: {
    config: {type: 'object', default: {}}
  },

  init: function() {
    this.createThronglets();
    this.createConnections();
  },

  createThronglets: function() {
    const config = this.data.config;
    if (!config || !config.thronglets) return;

    config.thronglets.forEach(throngletData => {
      const entity = document.createElement('a-entity');
      entity.setAttribute('data-thronglet-id', throngletData.id);
      entity.setAttribute('thronglet-entity', JSON.stringify(throngletData));
      entity.setAttribute('position', `${throngletData.position.x} ${throngletData.position.y} ${throngletData.position.z}`);
      
      this.el.appendChild(entity);
    });
  },

  createConnections: function() {
    const config = this.data.config;
    if (!config || !config.connections) return;

    config.connections.forEach(connectionData => {
      const entity = document.createElement('a-entity');
      entity.setAttribute('connection-line', JSON.stringify(connectionData));
      
      this.el.appendChild(entity);
    });
  }
});