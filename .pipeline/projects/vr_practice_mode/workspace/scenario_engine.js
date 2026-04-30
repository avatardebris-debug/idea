/**
 * Scenario Engine for VR Practice Mode
 * Manages loading, parsing, and executing practice scenarios
 */

class ScenarioEngine {
  constructor(scene, throngletsManager) {
    this.scene = scene;
    this.throngletsManager = throngletsManager;
    this.currentScenario = null;
    this.scenarioManifest = null;
    this.objectives = [];
    this.completedObjectives = new Set();
    this.currentObjectiveIndex = 0;
    this.scenarioState = {};
    this.score = 0;
    this.isRunning = false;
    
    // Load scenario manifest
    this.loadManifest();
  }

  async loadManifest() {
    try {
      const response = await fetch('scenarios/manifest.json');
      this.scenarioManifest = await response.json();
      console.log('Scenario manifest loaded:', this.scenarioManifest);
    } catch (error) {
      console.error('Failed to load scenario manifest:', error);
    }
  }

  async loadScenario(scenarioId) {
    try {
      const scenarioFile = this.scenarioManifest.scenarios.find(s => s.id === scenarioId)?.file;
      if (!scenarioFile) {
        throw new Error(`Scenario ${scenarioId} not found in manifest`);
      }

      const response = await fetch(`scenarios/${scenarioFile}`);
      const yamlContent = await response.text();
      
      // Simple YAML parser (basic implementation)
      const scenarioData = this.parseYAML(yamlContent);
      
      await this.initializeScenario(scenarioData);
      return scenarioData;
    } catch (error) {
      console.error('Failed to load scenario:', error);
      throw error;
    }
  }

  parseYAML(content) {
    // Simple YAML parser for our specific format
    const lines = content.split('\n');
    const result = {};
    let currentSection = null;
    let currentObject = null;
    let currentArray = null;
    let arrayKey = null;

    for (const line of lines) {
      const trimmed = line.trim();
      
      // Skip empty lines and comments
      if (!trimmed || trimmed.startsWith('#')) continue;

      // Check indentation level
      const indent = line.search(/\S/);
      const keyMatch = trimmed.match(/^(\w[\w-]*):(.*)$/);

      if (indent === 0 && keyMatch) {
        // Top-level key
        const [, key, value] = keyMatch;
        const val = value.trim();
        
        if (val === '' || val.startsWith('#')) {
          // This is a section header
          currentSection = key;
          result[currentSection] = [];
          currentArray = result[currentSection];
          arrayKey = null;
        } else {
          // Simple key-value
          result[key] = val;
        }
      } else if (indent === 2 && currentSection && keyMatch) {
        // Array item key
        const [, key, value] = keyMatch;
        const val = value.trim();
        
        if (val === '' || val.startsWith('#')) {
          // Start of object in array
          currentObject = {};
          currentArray.push(currentObject);
          arrayKey = key;
        } else {
          // Simple key-value in object
          currentObject[key] = val;
        }
      } else if (indent === 4 && currentObject && keyMatch) {
        // Nested key-value
        const [, key, value] = keyMatch;
        const val = value.trim();
        
        if (val === '' || val.startsWith('#')) {
          // Nested object
          currentObject[key] = {};
          currentObject = currentObject[key];
        } else {
          currentObject[key] = val;
        }
      } else if (indent === 6 && currentObject && keyMatch) {
        // Deeply nested key-value
        const [, key, value] = keyMatch;
        const val = value.trim();
        
        if (val === '' || val.startsWith('#')) {
          currentObject[key] = {};
          currentObject = currentObject[key];
        } else {
          currentObject[key] = val;
        }
      }
    }

    return result;
  }

  async initializeScenario(scenarioData) {
    this.currentScenario = scenarioData;
    this.objectives = scenarioData.objectives || [];
    this.completedObjectives.clear();
    this.currentObjectiveIndex = 0;
    this.score = 0;
    this.isRunning = true;

    // Clear existing thronglets
    this.throngletsManager.clearThronglets();

    // Create thronglets from scenario
    if (scenarioData.thronglet_roles) {
      for (const role of scenarioData.thronglet_roles) {
        this.throngletsManager.createThronglet({
          id: role.id,
          name: role.name,
          role: role.role,
          color: role.color,
          position: role.position,
          health: role.health,
          mood: 'neutral',
          token_count: 100,
          uptime: 3600,
          last_seen: new Date().toISOString(),
          icon: role.icon,
          description: role.description
        });
      }
    }

    // Initialize state
    this.scenarioState = {
      connections: scenarioData.initial_state?.connections || [],
      current_objective: scenarioData.initial_state?.current_objective || '',
      ...scenarioData.initial_state
    };

    // Update UI
    this.updateObjectiveDisplay();
    this.updateScoreDisplay();
    this.showObjectiveNotification();

    console.log('Scenario initialized:', scenarioData.name);
  }

  updateObjectiveDisplay() {
    const currentObjective = this.objectives[this.currentObjectiveIndex];
    if (currentObjective) {
      document.getElementById('current-objective-title').textContent = currentObjective.title;
      document.getElementById('current-objective-desc').textContent = currentObjective.description;
    }
  }

  showObjectiveNotification() {
    const currentObjective = this.objectives[this.currentObjectiveIndex];
    if (currentObjective) {
      const notification = document.getElementById('objective-notification');
      if (notification) {
        notification.innerHTML = `
          <div class="objective-notification">
            <h3>🎯 Objective: ${currentObjective.title}</h3>
            <p>${currentObjective.description}</p>
            <p class="points">+${currentObjective.points} points</p>
          </div>
        `;
        notification.classList.add('visible');
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
          notification.classList.remove('visible');
        }, 10000);
      }
    }
  }

  updateScoreDisplay() {
    const scoreElement = document.getElementById('scenario-score');
    if (scoreElement) {
      scoreElement.textContent = `Score: ${this.score}`;
    }
  }

  completeObjective(objectiveId) {
    if (this.completedObjectives.has(objectiveId)) return;

    const objective = this.objectives.find(o => o.id === objectiveId);
    if (objective) {
      this.completedObjectives.add(objectiveId);
      this.score += objective.points;
      this.updateScoreDisplay();
      
      console.log(`Objective completed: ${objective.title} (+${objective.points} points)`);
      
      // Move to next objective
      this.currentObjectiveIndex++;
      
      if (this.currentObjectiveIndex < this.objectives.length) {
        this.updateObjectiveDisplay();
        this.showObjectiveNotification();
      } else {
        this.checkSuccessConditions();
      }
    }
  }

  checkSuccessConditions() {
    if (!this.currentScenario.success_conditions) return;

    for (const condition of this.currentScenario.success_conditions) {
      if (this.evaluateCondition(condition.condition)) {
        this.showSuccessMessage(condition.message);
        this.isRunning = false;
        return;
      }
    }
  }

  evaluateCondition(condition) {
    switch (condition) {
      case 'all_connected':
        return this.completedObjectives.size === this.objectives.length;
      case 'health_checked':
        return this.completedObjectives.has('monitor_health');
      case 'alert_responded':
        return this.completedObjectives.has('respond_alert');
      case 'service_restored':
        return this.completedObjectives.has('restore_service');
      case 'build_started':
        return this.completedObjectives.has('start_build');
      case 'tests_passed':
        return this.completedObjectives.has('run_tests');
      case 'deployment_complete':
        return this.completedObjectives.has('deploy_app');
      case 'notification_sent':
        return this.completedObjectives.has('notify_success');
      default:
        return false;
    }
  }

  showSuccessMessage(message) {
    const successPanel = document.getElementById('success-panel');
    if (successPanel) {
      successPanel.querySelector('.success-message').textContent = message;
      successPanel.classList.add('visible');
    }
  }

  resetScenario() {
    this.isRunning = false;
    this.completedObjectives.clear();
    this.currentObjectiveIndex = 0;
    this.score = 0;
    this.updateScoreDisplay();
    
    // Hide success panel
    const successPanel = document.getElementById('success-panel');
    if (successPanel) {
      successPanel.classList.remove('visible');
    }
  }

  getScenarioInfo() {
    return {
      name: this.currentScenario?.name,
      description: this.currentScenario?.description,
      score: this.score,
      completedObjectives: this.completedObjectives.size,
      totalObjectives: this.objectives.length,
      isRunning: this.isRunning
    };
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ScenarioEngine;
}
