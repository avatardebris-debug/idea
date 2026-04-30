# Thronglets VR Practice Mode

A virtual reality practice environment for interacting with Thronglets in a 3D space.

## Overview

The VR Practice Mode provides an immersive environment where users can:
- **Visualize** Thronglets as 3D entities in a virtual forest environment
- **Interact** with Thronglets through teleportation and selection
- **Monitor** Thronglet health, mood, and token counts in real-time
- **Explore** connections between Thronglets through visual links
- **Practice** VR navigation and interaction techniques

## Features

### Core Functionality

1. **3D Thronglet Visualization**
   - Each Thronglet is represented as a colored sphere with a nameplate
   - Health status is indicated by colored halos (green/yellow/red)
   - Connection lines show relationships between Thronglets
   - Smooth animations and visual feedback

2. **Interactive Selection**
   - Click on Thronglets to select them
   - Detail panel shows comprehensive information about selected Thronglet
   - Proximity alerts warn about nearby Thronglets

3. **Teleportation System**
   - Press keys 1-5 to teleport to specific Thronglets
   - Smooth camera transitions between locations
   - Maintain orientation while teleporting

4. **Simulation Loop**
   - Real-time updates to Thronglet positions and states
   - Dynamic health and mood changes
   - Token count tracking

5. **UI Controls**
   - Toggle nameplates visibility
   - Toggle connection lines visibility
   - Toggle health halos visibility
   - Debug mode for monitoring system state

### Technical Implementation

- **A-Frame Framework**: Built on A-Frame for WebVR compatibility
- **Three.js**: 3D rendering engine
- **Custom Components**: Thronglet entity and connection line components
- **State Management**: Centralized VRState for practice mode control

## Usage

### Starting the VR Practice Mode

```javascript
// Initialize VR Practice Mode
initThrongletsVR();

// Enable practice mode
VRState.practiceMode.enable();

// Start simulation
VRState.practiceMode.startSimulation();
```

### Selecting a Thronglet

```javascript
// Select by ID
VRState.practiceMode.selectThronglet('thronglet-1');

// Get thronglet data
const thronglet = VRState.practiceMode.getThrongletById('thronglet-1');
console.log(thronglet.name); // 'Thronglet 1'
```

### Teleportation

```javascript
// Teleport to specific thronglet
VRState.practiceMode.teleportToThronglet('thronglet-1');

// Or use keyboard shortcuts (1-5)
```

### UI Controls

- **Nameplates**: Toggle visibility of Thronglet name labels
- **Connections**: Toggle visibility of connection lines
- **Health**: Toggle visibility of health status halos
- **Debug**: Toggle debug panel with system statistics

## Architecture

### Components

1. **VRState**: Central state management for VR practice mode
2. **PracticeMode**: Main controller for the VR environment
3. **Thronglet**: Data model for individual Thronglets
4. **Connection**: Data model for connections between Thronglets
5. **ThrongletEntity**: A-Frame component for rendering Thronglets
6. **ConnectionLine**: A-Frame component for rendering connections

### Data Flow

```
User Input → VRState → PracticeMode → Update Thronglets → Render
                                                        ↓
                                                    A-Frame Scene
```

## Testing

Run the test suite:

```bash
npm test
```

Run with coverage:

```bash
npm run test:coverage
```

Tests cover:
- VRState initialization and state management
- PracticeMode simulation and control
- Thronglet and Connection data models
- UI functions and keyboard controls

## Keyboard Controls

| Key | Action |
|-----|--------|
| 1-5 | Teleport to Thronglet |
| ESC | Deselect current Thronglet |
| WASD | Move camera (when not in VR) |

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## VR Headset Support

- Oculus Rift
- HTC Vive
- Samsung Gear VR
- Google Daydream
- Any WebXR-compatible headset

## Performance

- Optimized for 60 FPS
- Efficient rendering with A-Frame
- Minimal memory footprint
- Smooth animations and transitions

## Future Enhancements

- [ ] Multi-user collaboration
- [ ] Custom environment themes
- [ ] Advanced interaction gestures
- [ ] Haptic feedback integration
- [ ] Recording and playback of sessions

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Support

For issues and questions, please open an issue on the repository.
