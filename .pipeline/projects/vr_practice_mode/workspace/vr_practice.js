/**
 * Thronglets VR Practice Mode — Main Application
 *
 * Loads vr_config.json, builds the A-Frame scene, creates thronglet avatars,
 * handles VR camera rig with teleportation, and runs all animations.
 *
 * Task 1: Point-and-look interaction — raycaster hover, detail panel, proximity alerts
 */

(function () {
  'use strict';

  // ─── Configuration ────────────────────────────────────────────────────────

  let CONFIG = null;
  let THRONGLET_ENTITIES = {};
  let CONNECTION_LINES = [];
  let ANIMATION_FRAME = null;
  let LAST_TIME = 0;

  // ─── Interaction State ───────────────────────────────────────────────────

  let hoveredThrongletId = null;
  let selectedThrongletId = null;
  let proximityAlertActive = false;
  let proximityAlertThrongletId = null;
  let lastProximityAlertTime = 0;
  const PROXIMITY_ALERT_COOLDOWN = 5000; // ms
  const PROXIMITY_CRITICAL_DISTANCE = 3.0; // meters
  const PROXIMITY_WARNING_DISTANCE = 5.0; // meters
  const HOVER_DISTANCE_THRESHOLD = 8.0; // meters for raycaster hover

  // ─── Initialization ───────────────────────────────────────────────────────

  async function init() {
    try {
      // Load configuration
      CONFIG = await loadConfig();

      // Generate grid texture
      generateGridTexture();

      // Create thronglet avatars
      createThronglets();

      // Create connection lines
      createConnections();

      // Setup VR detection and controls
      setupVRControls();

      // Setup interaction handlers
      setupInteractionHandlers();

      // Start animation loop
      LAST_TIME = performance.now();
      ANIMATION_LOOP();

      // Hide loading overlay
      const overlay = document.getElementById('loading-overlay');
      overlay.classList.add('hidden');
      setTimeout(() => overlay.remove(), 700);

      console.log('[Thronglets VR] Initialized successfully');
    } catch (err) {
      console.error('[Thronglets VR] Initialization failed:', err);
      const overlay = document.getElementById('loading-overlay');
      overlay.innerHTML = `
        <h1 style="color: #e57373;">⚠️ Error</h1>
        <p style="color: #ccc; max-width: 400px; text-align: center;">
          Failed to load VR world.<br><br>
          <code style="color: #e57373;">${err.message}</code>
        </p>
      `;
    }
  }

  // ─── Config Loading ───────────────────────────────────────────────────────

  async function loadConfig() {
    const response = await fetch('vr_config.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}: vr_config.json not found`);
    return response.json();
  }

  // ─── Grid Texture Generation ──────────────────────────────────────────────

  function generateGridTexture() {
    const canvas = document.getElementById('grid-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const size = canvas.width;

    // Background
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, size, size);

    // Grid lines
    const gridSize = 32; // pixels per grid cell
    ctx.strokeStyle = 'rgba(79, 195, 247, 0.15)';
    ctx.lineWidth = 1;

    for (let i = 0; i <= size; i += gridSize) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, size);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(size, i);
      ctx.stroke();
    }

    // Major grid lines (every 4 cells)
    ctx.strokeStyle = 'rgba(79, 195, 247, 0.3)';
    ctx.lineWidth = 2;

    for (let i = 0; i <= size; i += gridSize * 4) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i, size);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(0, i);
      ctx.lineTo(size, i);
      ctx.stroke();
    }

    // Update the A-Frame material
    const mixin = document.getElementById('grid-texture');
    if (mixin) {
      mixin.setAttribute('material', 'src', `#${canvas.id}`);
    }
  }

  // ─── Thronglet Avatar Creation ────────────────────────────────────────────

  function createThronglets() {
    const container = document.getElementById('thronglets-container');
    if (!container || !CONFIG?.thronglets) return;

    CONFIG.thronglets.forEach((thronglet, index) => {
      const entity = document.createElement('a-entity');
      entity.setAttribute('id', `thronglet_${index}`);
      entity.setAttribute('position', `${thronglet.position.x} ${thronglet.position.y} ${thronglet.position.z}`);
      entity.setAttribute('class', 'thronglet');
      entity.setAttribute('data-thronglet-id', index);
      entity.setAttribute('data-health', thronglet.health);
      entity.setAttribute('data-role', thronglet.role);

      // Create the visual avatar
      createAvatar(entity, thronglet);

      // Create nameplate
      createNameplate(entity, thronglet);

      // Create halo (for critical health)
      if (thronglet.health < 30) {
        createHalo(entity, thronglet);
      }

      container.appendChild(entity);
      THRONGLET_ENTITIES[index] = entity;
    });
  }

  function createAvatar(entity, thronglet) {
    // Main body (capsule-like shape using cylinder + spheres)
    const body = document.createElement('a-entity');
    body.setAttribute('class', 'thronglet-body');

    // Cylinder body
    const cylinder = document.createElement('a-cylinder');
    cylinder.setAttribute('radius', '0.3');
    cylinder.setAttribute('height', '0.8');
    cylinder.setAttribute('position', '0 0.4 0');
    cylinder.setAttribute('material', `color: ${getRoleColor(thronglet.role)}; opacity: 0.8; shader: flat`);
    body.appendChild(cylinder);

    // Sphere head
    const head = document.createElement('a-sphere');
    head.setAttribute('radius', '0.25');
    head.setAttribute('position', '0 1.0 0');
    head.setAttribute('material', `color: ${getRoleColor(thronglet.role)}; opacity: 0.9; shader: flat`);
    body.appendChild(head);

    // Eyes
    const leftEye = document.createElement('a-sphere');
    leftEye.setAttribute('radius', '0.05');
    leftEye.setAttribute('position', '-0.08 1.05 0.2');
    leftEye.setAttribute('material', 'color: #ffffff; shader: flat');
    body.appendChild(leftEye);

    const rightEye = document.createElement('a-sphere');
    rightEye.setAttribute('radius', '0.05');
    rightEye.setAttribute('position', '0.08 1.05 0.2');
    rightEye.setAttribute('material', 'color: #ffffff; shader: flat');
    body.appendChild(rightEye);

    // Eye pupils
    const leftPupil = document.createElement('a-sphere');
    leftPupil.setAttribute('radius', '0.025');
    leftPupil.setAttribute('position', '-0.08 1.05 0.24');
    leftPupil.setAttribute('material', 'color: #000000; shader: flat');
    body.appendChild(leftPupil);

    const rightPupil = document.createElement('a-sphere');
    rightPupil.setAttribute('radius', '0.025');
    rightPupil.setAttribute('position', '0.08 1.05 0.24');
    rightPupil.setAttribute('material', 'color: #000000; shader: flat');
    body.appendChild(rightPupil);

    entity.appendChild(body);
  }

  function createNameplate(entity, thronglet) {
    const nameplate = document.createElement('a-entity');
    nameplate.setAttribute('class', 'thronglet-nameplate');
    nameplate.setAttribute('position', '0 1.8 0');
    nameplate.setAttribute('look-at', '#camera');

    // Background plane
    const bgPlane = document.createElement('a-plane');
    bgPlane.setAttribute('width', '1.2');
    bgPlane.setAttribute('height', '0.4');
    bgPlane.setAttribute('position', '0 0 0');
    bgPlane.setAttribute('material', `color: rgba(15, 15, 35, 0.8); opacity: 0.9; shader: flat`);
    nameplate.appendChild(bgPlane);

    // Name text
    const nameText = document.createElement('a-text');
    nameText.setAttribute('value', thronglet.name);
    nameText.setAttribute('align', 'center');
    nameText.setAttribute('color', '#ffffff');
    nameText.setAttribute('width', '1.2');
    nameText.setAttribute('position', '0 0.1 0.01');
    nameText.setAttribute('font', 'monospace');
    nameText.setAttribute('side', 'double');
    nameplate.appendChild(nameText);

    // Health bar background
    const healthBg = document.createElement('a-plane');
    healthBg.setAttribute('width', '1.0');
    healthBg.setAttribute('height', '0.08');
    healthBg.setAttribute('position', '0 -0.12 0.01');
    healthBg.setAttribute('material', 'color: #333333; opacity: 0.8; shader: flat');
    nameplate.appendChild(healthBg);

    // Health bar fill
    const healthFill = document.createElement('a-plane');
    healthFill.setAttribute('width', `${(thronglet.health / 100).toFixed(2)}`);
    healthFill.setAttribute('height', '0.06');
    healthFill.setAttribute('position', `${-0.5 + (thronglet.health / 100) * 0.5} -0.12 0.015`);
    healthFill.setAttribute('material', `color: ${getHealthColor(thronglet.health)}; opacity: 0.9; shader: flat`);
    nameplate.appendChild(healthFill);

    entity.appendChild(nameplate);
  }

  function createHalo(entity, thronglet) {
    const halo = document.createElement('a-entity');
    halo.setAttribute('class', 'thronglet-halo');
    halo.setAttribute('position', '0 0.5 0');

    const ring = document.createElement('a-ring');
    ring.setAttribute('radiusInner', '0.5');
    ring.setAttribute('radiusOuter', '0.55');
    ring.setAttribute('color', '#f44336');
    ring.setAttribute('opacity', '0.5');
    ring.setAttribute('rotation', '-90 0 0');
    halo.appendChild(ring);

    entity.appendChild(halo);
  }

  // ─── Connection Lines ──────────────────────────────────────────────────────

  function createConnections() {
    const container = document.getElementById('connections-container');
    if (!container || !CONFIG?.connections) return;

    CONFIG.connections.forEach((conn) => {
      const fromEntity = THRONGLET_ENTITIES[conn.from];
      const toEntity = THRONGLET_ENTITIES[conn.to];
      if (!fromEntity || !toEntity) return;

      const line = document.createElement('a-entity');
      line.setAttribute('class', 'connection-line');
      line.setAttribute('line', `start: 0 0 0; end: 0 0 0; color: ${getRoleColor(CONFIG.thronglets[conn.from].role)}; opacity: 0.3; shader: flat`);
      line.setAttribute('position', '0 0.5 0');
      line.setAttribute('from-thronglet', conn.from);
      line.setAttribute('to-thronglet', conn.to);

      container.appendChild(line);
      CONNECTION_LINES.push(line);
    });
  }

  // ─── VR Controls ──────────────────────────────────────────────────────────

  function setupVRControls() {
    const scene = document.getElementById('scene');
    const cameraRig = document.getElementById('camera-rig');
    const reticle = document.getElementById('reticle');

    // Detect VR mode
    scene.addEventListener('enter-vr', () => {
      document.getElementById('desktop-controls').style.display = 'none';
      document.getElementById('vr-controls').style.display = 'inline';
      setupVRTeleportation(scene, cameraRig, reticle);
    });

    scene.addEventListener('exit-vr', () => {
      document.getElementById('desktop-controls').style.display = 'inline';
      document.getElementById('vr-controls').style.display = 'none';
    });

    // Desktop teleportation
    scene.addEventListener('click', (event) => {
      if (scene.is('vr-mode')) return;

      const raycaster = new THREE.Raycaster();
      const camera = document.getElementById('camera');
      const vector = new THREE.Vector3();

      // Get mouse position from click event
      const mouse = new THREE.Vector2();
      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

      vector.setFromCamera(mouse, camera);
      raycaster.set(camera.getWorldPosition(new THREE.Vector3()), vector.direction);

      const intersects = raycaster.intersectObject(scene.getObjectByName('ground-plane'));
      if (intersects.length > 0) {
        const point = intersects[0].point;
        cameraRig.setAttribute('position', `${point.x} ${cameraRig.getAttribute('position').y} ${point.z}`);
      }
    });
  }

  function setupVRTeleportation(scene, cameraRig, reticle) {
    // Add VR controllers
    const controller0 = scene.querySelector('a-entity[controller]') || document.createElement('a-entity');
    controller0.setAttribute('controller', 'hand-tracking');
    controller0.setAttribute('class', 'vr-controller');
    scene.appendChild(controller0);

    // Teleportation ray
    const teleportRay = document.createElement('a-entity');
    teleportRay.setAttribute('class', 'vr-teleport-ray');
    teleportRay.setAttribute('line', 'start: 0 0 0; end: 0 0 -3; color: #4fc3f7; opacity: 0.5');
    teleportRay.setAttribute('position', '0 0 -0.5');
    teleportRay.setAttribute('rotation', '-90 0 0');
    scene.appendChild(teleportRay);

    // Teleportation target
    const teleportTarget = document.createElement('a-entity');
    teleportTarget.setAttribute('class', 'vr-teleport-target');
    teleportTarget.setAttribute('ring', 'radiusInner: 0.1; radiusOuter: 0.15; color: #4fc3f7; opacity: 0.3');
    teleportTarget.setAttribute('position', '0 0 -3');
    teleportTarget.setAttribute('rotation', '-90 0 0');
    teleportTarget.setAttribute('visible', 'false');
    scene.appendChild(teleportTarget);

    // Handle teleportation
    scene.addEventListener('click', (event) => {
      if (!event.target.closest('a-entity')?.getAttribute('class')?.includes('vr-controller')) return;

      const raycaster = new THREE.Raycaster();
      const controller = event.target.closest('a-entity');
      const controllerPos = new THREE.Vector3();
      controller.getWorldPosition(controllerPos);

      const controllerDir = new THREE.Vector3();
      controller.getWorldDirection(controllerDir);

      raycaster.set(controllerPos, controllerDir);

      const intersects = raycaster.intersectObject(scene.getObjectByName('ground-plane'));
      if (intersects.length > 0) {
        const point = intersects[0].point;
        cameraRig.setAttribute('position', `${point.x} ${cameraRig.getAttribute('position').y} ${point.z}`);
      }
    });
  }

  // ─── Interaction Handlers ────────────────────────────────────────────────

  function setupInteractionHandlers() {
    const camera = document.getElementById('camera');
    if (!camera) return;

    // Raycaster for hover detection
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    // Update raycaster on mouse move
    window.addEventListener('mousemove', (event) => {
      if (document.getElementById('scene').is('vr-mode')) return;

      mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);

      // Check for thronglet intersections
      const throngletEntities = Object.values(THRONGLET_ENTITIES);
      const intersects = raycaster.intersectObjects(throngletEntities, true);

      let foundThronglet = null;
      if (intersects.length > 0) {
        // Walk up to find the thronglet entity
        let obj = intersects[0].object;
        while (obj && obj !== document.body) {
          if (obj.classList?.contains('thronglet')) {
            foundThronglet = obj;
            break;
          }
          obj = obj.parent;
        }
      }

      // Handle hover state changes
      if (foundThronglet) {
        const throngletId = parseInt(foundThronglet.getAttribute('data-thronglet-id'));
        if (hoveredThrongletId !== throngletId) {
          // Un-hover previous
          if (hoveredThrongletId !== null) {
            unhoverThronglet(hoveredThrongletId);
          }
          // Hover new
          hoverThronglet(throngletId);
          hoveredThrongletId = throngletId;
        }
      } else {
        // No thronglet hovered
        if (hoveredThrongletId !== null) {
          unhoverThronglet(hoveredThrongletId);
          hoveredThrongletId = null;
        }
      }
    });

    // Click to select/throttle thronglet
    window.addEventListener('click', (event) => {
      if (document.getElementById('scene').is('vr-mode')) return;

      if (hoveredThrongletId !== null) {
        selectThronglet(hoveredThrongletId);
      } else {
        deselectThronglet();
      }
    });

    // Proximity check in animation loop
    setInterval(() => {
      checkProximity();
    }, 1000);
  }

  function hoverThronglet(throngletId) {
    const entity = THRONGLET_ENTITIES[throngletId];
    if (!entity) return;

    // Highlight effect
    const body = entity.querySelector('.thronglet-body');
    if (body) {
      body.setAttribute('animation', 'property: scale; to: 1.1 1.1 1.1; dur: 200; easing: easeOutQuad');
    }

    // Show hover indicator
    const hoverIndicator = document.getElementById('hover-indicator');
    if (hoverIndicator) {
      hoverIndicator.classList.add('visible');
    }

    // Show detail panel
    showDetailPanel(throngletId);
  }

  function unhoverThronglet(throngletId) {
    const entity = THRONGLET_ENTITIES[throngletId];
    if (!entity) return;

    // Reset highlight
    const body = entity.querySelector('.thronglet-body');
    if (body) {
      body.setAttribute('animation', 'property: scale; to: 1 1 1; dur: 200; easing: easeOutQuad');
    }

    // Hide hover indicator
    const hoverIndicator = document.getElementById('hover-indicator');
    if (hoverIndicator) {
      hoverIndicator.classList.remove('visible');
    }
  }

  function selectThronglet(throngletId) {
    selectedThrongletId = throngletId;
    const entity = THRONGLET_ENTITIES[throngletId];
    if (!entity) return;

    // Pulse effect
    const body = entity.querySelector('.thronglet-body');
    if (body) {
      body.setAttribute('animation', 'property: scale; to: 1.2 1.2 1.2; dur: 100; easing: easeOutQuad; loop: 1');
      setTimeout(() => {
        body.setAttribute('animation', 'property: scale; to: 1.1 1.1 1.1; dur: 200; easing: easeOutQuad');
      }, 100);
    }

    // Show detail panel
    showDetailPanel(throngletId);
  }

  function deselectThronglet() {
    selectedThrongletId = null;
    hideDetailPanel();
  }

  function showDetailPanel(throngletId) {
    const entity = THRONGLET_ENTITIES[throngletId];
    if (!entity) return;

    const thronglet = CONFIG.thronglets[throngletId];
    if (!thronglet) return;

    const panel = document.getElementById('detail-panel');
    if (!panel) return;

    // Update panel content
    document.getElementById('panel-avatar-icon').textContent = getRoleEmoji(thronglet.role);
    document.getElementById('panel-avatar-icon').style.background = getRoleColor(thronglet.role);
    document.getElementById('panel-name').textContent = thronglet.name;
    document.getElementById('panel-role-detail').textContent = thronglet.role;
    document.getElementById('panel-health').textContent = `${thronglet.health}%`;
    document.getElementById('panel-health').className = `stat-value ${getHealthClass(thronglet.health)}`;
    document.getElementById('panel-uptime').textContent = formatUptime(thronglet.uptime);
    document.getElementById('panel-last-seen').textContent = formatLastSeen(thronglet.lastSeen);
    document.getElementById('panel-location').textContent = `${thronglet.position.x.toFixed(1)}, ${thronglet.position.z.toFixed(1)}`;

    // Show panel
    panel.classList.add('visible');
  }

  function hideDetailPanel() {
    const panel = document.getElementById('detail-panel');
    if (panel) {
      panel.classList.remove('visible');
    }
  }

  function checkProximity() {
    const camera = document.getElementById('camera');
    if (!camera) return;

    const cameraPos = camera.getAttribute('position');
    if (!cameraPos) return;

    let closestThronglet = null;
    let closestDistance = Infinity;

    // Find closest thronglet
    Object.entries(THRONGLET_ENTITIES).forEach(([id, entity]) => {
      const pos = entity.getAttribute('position');
      if (!pos) return;

      const dx = cameraPos.x - pos.x;
      const dy = cameraPos.y - pos.y;
      const dz = cameraPos.z - pos.z;
      const distance = Math.sqrt(dx * dx + dy * dy + dz * dz);

      if (distance < closestDistance) {
        closestDistance = distance;
        closestThronglet = parseInt(id);
      }
    });

    if (closestThronglet === null) {
      hideProximityAlert();
      return;
    }

    const thronglet = CONFIG.thronglets[closestThronglet];
    if (!thronglet) return;

    const now = performance.now();

    // Check for critical state
    if (thronglet.health < 30 && closestDistance < PROXIMITY_CRITICAL_DISTANCE) {
      if (proximityAlertThrongletId !== closestThronglet || now - lastProximityAlertTime > PROXIMITY_ALERT_COOLDOWN) {
        showProximityAlert('critical', thronglet);
        proximityAlertThrongletId = closestThronglet;
        lastProximityAlertTime = now;
      }
    }
    // Check for warning state
    else if (thronglet.health < 60 && closestDistance < PROXIMITY_WARNING_DISTANCE) {
      if (proximityAlertThrongletId !== closestThronglet || now - lastProximityAlertTime > PROXIMITY_ALERT_COOLDOWN) {
        showProximityAlert('warning', thronglet);
        proximityAlertThrongletId = closestThronglet;
        lastProximityAlertTime = now;
      }
    } else {
      hideProximityAlert();
    }
  }

  function showProximityAlert(type, thronglet) {
    const alert = document.getElementById('proximity-alert');
    if (!alert) return;

    alert.textContent = type === 'critical'
      ? `⚠️ ${thronglet.name} is in Critical State!`
      : `⚠️ ${thronglet.name} needs Attention`;

    alert.className = type === 'critical' ? 'visible' : 'visible warning';
    proximityAlertActive = true;
  }

  function hideProximityAlert() {
    const alert = document.getElementById('proximity-alert');
    if (alert) {
      alert.classList.remove('visible', 'warning');
    }
    proximityAlertActive = false;
    proximityAlertThrongletId = null;
  }

  // ─── Animation Loop ────────────────────────────────────────────────────────

  function ANIMATION_LOOP() {
    ANIMATION_FRAME = requestAnimationFrame(ANIMATION_LOOP);

    const now = performance.now();
    const delta = (now - LAST_TIME) / 1000;
    LAST_TIME = now;

    // Update connection lines
    updateConnectionLines();

    // Update nameplate billboards
    updateBillboards();

    // Pulse critical health halos
    pulseCriticalHalos(now);

    // Update hover indicator position
    updateHoverIndicator();
  }

  function updateBillboards() {
    const camera = document.getElementById('camera');
    if (!camera) return;

    const cameraPos = camera.getAttribute('position');
    if (!cameraPos) return;

    // Update all nameplates to face camera
    document.querySelectorAll('.thronglet-nameplate').forEach((nameplate) => {
      const pos = nameplate.getAttribute('position');
      if (!pos) return;

      const dx = cameraPos.x - pos.x;
      const dy = cameraPos.y - pos.y;
      const dz = cameraPos.z - pos.z;

      const yaw = Math.atan2(dx, dz) * 180 / Math.PI;
      const pitch = Math.atan2(dy, Math.sqrt(dx * dx + dz * dz)) * 180 / Math.PI;

      nameplate.setAttribute('rotation', `${pitch} ${yaw} 0`);
    });
  }

  function pulseCriticalHalos(time) {
    const pulse = Math.sin(time / 500) * 0.3 + 0.7;

    document.querySelectorAll('.thronglet-halo').forEach((halo) => {
      const parent = halo.parentElement;
      if (parent?.getAttribute('id')?.includes('thronglet_3')) { // Data (critical)
        halo.setAttribute('opacity', pulse.toString());
      }
    });
  }

  function updateHoverIndicator() {
    const indicator = document.getElementById('hover-indicator');
    if (!indicator || !indicator.classList.contains('visible')) return;

    // The indicator is already positioned via CSS, so we just need to ensure it's visible
    // when hovering over a thronglet
  }

  function updateConnectionLines() {
    CONNECTION_LINES.forEach((line) => {
      const fromId = parseInt(line.getAttribute('from-thronglet'));
      const toId = parseInt(line.getAttribute('to-thronglet'));

      const fromEntity = THRONGLET_ENTITIES[fromId];
      const toEntity = THRONGLET_ENTITIES[toId];

      if (!fromEntity || !toEntity) return;

      const fromPos = fromEntity.getAttribute('position');
      const toPos = toEntity.getAttribute('position');

      if (!fromPos || !toPos) return;

      // Calculate line endpoints
      const dx = toPos.x - fromPos.x;
      const dy = toPos.y - fromPos.y;
      const dz = toPos.z - fromPos.z;
      const length = Math.sqrt(dx * dx + dy * dy + dz * dz);

      line.setAttribute('line', `end: 0 0 ${-length}`);
      line.setAttribute('position', `${fromPos.x} ${fromPos.y + 0.5} ${fromPos.z}`);
      line.setAttribute('rotation', `${Math.atan2(dy, Math.sqrt(dx * dx + dz * dz)) * 180 / Math.PI} ${Math.atan2(dx, dz) * 180 / Math.PI} 0`);
    });
  }

  // ─── Utility Functions ────────────────────────────────────────────────────

  function getRoleColor(role) {
    const colors = {
      'Compute': '#4fc3f7',
      'Storage': '#81c784',
      'Network': '#ffb74d',
      'Data': '#e57373',
      'Control': '#ba68c8'
    };
    return colors[role] || '#ffffff';
  }

  function getHealthColor(health) {
    if (health >= 70) return '#4caf50';
    if (health >= 30) return '#ff9800';
    return '#f44336';
  }

  function getHealthClass(health) {
    if (health >= 70) return 'healthy';
    if (health >= 30) return 'warning';
    return 'critical';
  }

  function getRoleEmoji(role) {
    const emojis = {
      'Compute': '🖥️',
      'Storage': '💾',
      'Network': '🌐',
      'Data': '📊',
      'Control': '🎛️'
    };
    return emojis[role] || '🤖';
  }

  function formatUptime(seconds) {
    if (!seconds) return 'N/A';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  }

  function formatLastSeen(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return `${Math.floor(diff / 86400000)}d ago`;
  }

  // ─── Start ──────────────────────────────────────────────────────────────────

  // Wait for A-Frame to be ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Handle window resize
  window.addEventListener('resize', () => {
    const camera = document.getElementById('camera');
    if (camera) {
      camera.setAttribute('fov', '70');
    }
  });

})();
