# Thronglets VR Practice Mode

A virtual reality simulation environment for monitoring and managing Thronglets. This project provides a comprehensive VR interface for visualizing, interacting with, and managing Thronglets in a simulated 3D environment.

## Features

- **VR Simulation Environment**: Real-time 3D visualization of Thronglets and their connections
- **Interactive Interface**: Select, inspect, and interact with Thronglets in VR space
- **Health Monitoring**: Visual health indicators and proximity alerts for critical Thronglets
- **Connection Visualization**: Display and manage connections between Thronglets
- **Configuration Management**: Load and apply configuration files for custom scenarios
- **Keyboard Controls**: Intuitive keyboard shortcuts for navigation and interaction
- **Debug Mode**: Comprehensive debugging tools for development and troubleshooting
- **Test Suite**: Comprehensive test coverage for all components

## Installation

### Prerequisites

- Node.js >= 14.0.0
- npm or yarn

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd vr_practice_mode
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the test suite:
   ```bash
   npm test
   ```

## Usage

### Starting the VR Practice Mode

```bash
npm start
```

### Development Mode

```bash
npm run dev
```

### Running Tests

```bash
npm test
```

#### Test Options

- `npm run test:watch` - Run tests in watch mode
- `npm run test:verbose` - Run tests with verbose output
- `npm run test:coverage` - Run tests with coverage report

## Configuration

### Configuration File Format

Create a `config.json` file in the project root:

```json
{
  "thronglets": [
    {
      "id": "1",
      "name": "Agent Alpha",
      "role": "agent",
      "color": "#ff0000",
      "position": { "x": 0, "y": 0, "z": 0 },
      "health": "healthy",
      "mood": "neutral",
      "token_count": 100,
      "uptime": 3600,
      "last_seen": "2024-01-01T00:00:00Z"
    }
  ],
  "connections": [
    {
      "from": "1",
      "to": "2",
      "type": "communication",
      "color": "#0000ff",
      "label": "Alpha-Beta Link"
    }
  ]
}
```

### Configuration Options

#### Thronglet Properties

- `id` (string, required): Unique identifier for the Thronglet
- `name` (string, required): Display name of the Thronglet
- `role` (string): Role of the Thronglet (e.g., "agent", "controller")
- `color` (string): Hex color code for the Thronglet
- `position` (object): 3D position coordinates
  - `x` (number): X coordinate
  - `y` (number): Y coordinate
  - `z` (number): Z coordinate
- `health` (string): Health status ("healthy", "warning", "critical")
- `mood` (string): Current mood of the Thronglet
- `token_count` (number): Number of tokens associated with the Thronglet
- `uptime` (number): Uptime in seconds
- `last_seen` (string): ISO 8601 timestamp of last activity

#### Connection Properties

- `from` (string): ID of the source Thronglet
- `to` (string): ID of the destination Thronglet
- `type` (string): Type of connection (e.g., "communication", "data_transfer")
- `color` (string): Hex color code for the connection line
- `label` (string): Display label for the connection

## Keyboard Controls

| Key | Action |
|-----|--------|
| `ESC` | Deselect current Thronglet |
| `1-9` | Teleport to Thronglet by index |
| `N` | Toggle nameplates visibility |
| `C` | Toggle connections visibility |
| `H` | Toggle health halos visibility |
| `D` | Toggle debug mode |

## API Reference

### VRState

Global state management object.

```javascript
VRState = {
  thronglets: [],
  connections: [],
  selectedThronglet: null,
  settings: {
    showNameplates: true,
    showConnections: true,
    showHealthHalos: true,
    debugMode: false
  },
  config: null,
  practiceMode: null
}
```

### Thronglet Class

Represents a Thronglet in the VR environment.

```javascript
class Thronglet {
  constructor(data)
  getHealthColor(): string
  getHealthBadge(): string
  updateTimestamp(): void
  toJSON(): object
}
```

### Connection Class

Represents a connection between two Thronglets.

```javascript
class Connection {
  constructor(data, fromThronglet, toThronglet)
  toJSON(): object
}
```

### VRPracticeMode Class

Main class for managing the VR practice mode.

```javascript
class VRPracticeMode {
  constructor()
  init(): void
  loadConfiguration(): void
  createThronglets(): void
  createConnections(): void
  selectThronglet(id: string): void
  deselectThronglet(): void
  teleportToThronglet(index: number): void
  toggleNameplates(): void
  toggleConnections(): void
  toggleHealthHalos(): void
  toggleDebug(): void
  handleKeyboard(event: KeyboardEvent): void
  updateSimulation(): void
  checkProximityAlerts(): void
}
```

### Global Functions

```javascript
initThrongletsVR(): void
closeDetailPanel(): void
toggleNameplatesVisibility(): void
toggleConnectionsVisibility(): void
toggleHealthHalosVisibility(): void
toggleDebugMode(): void
teleportToThronglet(index: number): void
deselectThronglet(): void
handleResize(): void
```

## Testing

### Test Coverage

The test suite covers:

- Thronglet class instantiation and methods
- Connection class instantiation and methods
- VRState initialization and state management
- VRPracticeMode initialization and methods
- Global functions
- Edge cases (empty configurations, missing data, invalid inputs)
- Integration tests (full workflow scenarios)

### Running Tests

```bash
npm test
```

### Test Output

Tests output detailed results including:

- Test name and status (pass/fail)
- Expected vs actual values for failed tests
- Summary statistics (total, passed, failed, success rate)
- Detailed failure information

## Architecture

### Component Structure

```
vr_practice_mode/
├── vr_practice.js          # Main application logic
├── vr_practice_runner.js   # Test runner
├── package.json            # Project configuration
└── README.md               # Documentation
```

### Data Flow

1. **Initialization**: VRState is initialized with default values
2. **Configuration Loading**: Configuration file is loaded and parsed
3. **Thronglet Creation**: Thronglets are created from configuration data
4. **Connection Creation**: Connections are established between Thronglets
5. **Simulation Loop**: Thronglets are updated and proximity alerts are checked
6. **User Interaction**: Keyboard events trigger various actions

### State Management

The VRState object serves as the central state management system:

- **thronglets**: Array of Thronglet instances
- **connections**: Array of Connection instances
- **selectedThronglet**: Currently selected Thronglet
- **settings**: User preferences and display options
- **config**: Loaded configuration data
- **practiceMode**: VRPracticeMode instance

## Troubleshooting

### Common Issues

#### Configuration file not found

- Ensure `config.json` exists in the project root
- Check file permissions
- Verify JSON syntax is valid

#### Thronglets not appearing

- Check configuration file for valid thronglet data
- Verify position coordinates are valid numbers
- Ensure Thronglet class is properly instantiated

#### Connections not displaying

- Verify connection `from` and `to` IDs match existing Thronglet IDs
- Check connection color is a valid hex code
- Ensure `showConnections` setting is enabled

#### Keyboard controls not working

- Ensure the application has focus
- Check browser console for errors
- Verify keyboard event listeners are properly attached

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything passes
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on the repository.

## Acknowledgments

- Thronglets Team
- VR Community
- Open Source Contributors
