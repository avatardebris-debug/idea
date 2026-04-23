# Thronglets VR Practice Mode

A VR practice environment where thronglets represent infrastructure components. Built with A-Frame for cross-platform VR/AR/desktop support.

## Quick Start

### Desktop Browser (Chrome, Firefox, Edge)

1. Open a terminal in this directory
2. Start a local HTTP server:

```bash
# Python 3
python3 -m http.server 8080

# Node.js
npx serve .

# Or just open vr_practice.html directly in your browser
```

3. Navigate to `http://localhost:8080`

### Meta Quest (VR Mode)

1. Upload the entire `vr_practice_mode/workspace/` directory to your Quest's web server, or use a local network server accessible from the Quest
2. Open the Meta Quest Browser
3. Navigate to the URL (e.g., `http://your-server-ip:8080`)
4. Click the VR button (glasses icon) in the bottom-right corner
5. Use controller triggers to teleport and joysticks to move

### WebXR-Compatible Browsers

- **Desktop**: Chrome 79+, Firefox 98+, Edge 79+
- **Mobile**: Chrome for Android, Samsung Internet
- **VR**: Meta Quest Browser, Pico Browser

## Controls

### Desktop Mode
| Action | Control |
|--------|---------|
| Move | `W` `A` `S` `D` keys |
| Look around | Mouse (click to capture) |
| Teleport | Click on the ground |
| Release cursor | `ESC` |

### VR Mode (Meta Quest)
| Action | Control |
|--------|---------|
| Move | Left joystick |
| Teleport | Right trigger (point + release) |
| Look around | Head movement |

## Thronglets

| Name | Role | Health | Color |
|------|------|--------|-------|
| Arch | System Architect | 🟢 Healthy | #4fc3f7 |
| Deploy | CI/CD Pipeline | 🟡 Warning | #81c784 |
| Data | Database Server | 🔴 Critical | #ffb74d |
| Cache | Redis Cache | 🟢 Healthy | #e57373 |
| Monitor | Observability Stack | 🟢 Healthy | #ba68c8 |

## Verification Checklist

### Desktop Browser Tests

- [ ] **Load time**: Page loads in under 3 seconds (check browser DevTools Network tab)
- [ ] **5 avatars visible**: All 5 thronglets appear at their configured positions
- [ ] **Distinct colors**: Each thronglet has a unique, clearly visible color
- [ ] **Nameplates readable**: Names, roles, and health status are visible and readable
- [ ] **Halos visible**: Status halos (green/yellow/red) are visible above each thronglet
- [ ] **Halos rotating**: Halos rotate continuously (observe for 5+ seconds)
- [ ] **Body sway**: Thronglets gently bob up and down
- [ ] **Mouse look**: Click and drag to look around the world
- [ ] **WASD movement**: Press W/A/S/D to move the camera
- [ ] **Click teleport**: Click on the ground to teleport the camera
- [ ] **ESC release**: Press ESC to release mouse capture
- [ ] **No console errors**: Open DevTools Console — no errors or warnings

### VR Mode Tests (Meta Quest)

- [ ] **VR session starts**: Clicking the VR button enters immersive mode
- [ ] **All thronglets visible**: All 5 avatars are visible in VR
- [ ] **Teleportation works**: Point controller at ground, press trigger to teleport
- [ ] **Teleport ray visible**: A blue ray extends from the controller
- [ ] **Teleport target visible**: A ring appears where you'll teleport to
- [ ] **Joystick movement**: Left joystick moves the camera rig
- [ ] **Nameplates readable**: Names are readable from various distances
- [ ] **Halos visible**: Status halos are visible and rotating
- [ ] **No motion sickness**: No excessive nausea after 2+ minutes of use
- [ ] **Performance**: Stable 72+ FPS (check Quest Developer Hub)

### Cross-Platform Tests

- [ ] **Responsive**: Works on different screen sizes (desktop, tablet, phone)
- [ ] **No layout issues**: No overlapping elements or clipped content
- [ ] **Config loads**: All thronglet data loads from vr_config.json
- [ ] **Connections visible**: Dashed lines connect thronglets per config relationships
- [ ] **Fog effect**: Distant thronglets fade into the fog naturally
- [ ] **Lighting**: No overexposed or completely dark areas

## File Structure

```
vr_practice_mode/
├── phases/
│   └── phase_1/
│       ├── spec.md          # Phase specification
│       └── tasks.md         # Task checklist
├── state/
│   ├── current_idea.json    # Current project state
│   ├── current_phase.json   # Phase tracking
│   └── master_plan.md       # Overall project plan
└── workspace/
    ├── vr_config.json       # Thronglet configuration (source of truth)
    ├── vr_practice.html     # Main HTML file
    ├── vr_practice.js       # Application logic
    └── README.md            # This file
```

## Architecture

### vr_config.json
The single source of truth for the VR world. Defines:
- World settings (ground size, sky color, fog)
- Thronglet definitions (position, color, health, personality)
- Relationships between thronglets (connection lines)

### vr_practice.html
A-Frame scene with:
- A-Frame 1.6.0 renderer with WebXR support
- Procedural grid texture (canvas-generated)
- Multi-source lighting (ambient, directional, hemisphere)
- Camera rig with WASD controls and look controls
- Loading overlay and info panel

### vr_practice.js
Application logic:
- Config loading and parsing
- Grid texture generation (canvas API)
- Thronglet avatar creation (capsule body, sphere head, halo, nameplate)
- Connection line rendering (dynamic positioning)
- VR camera rig setup
- Teleportation (desktop click + VR controller)
- Animation loop (halo rotation, body sway, billboarding, health pulsing)

## Troubleshooting

### "vr_config.json not found"
- Make sure you're serving files via HTTP (not opening the file directly)
- Check that vr_config.json is in the same directory as vr_practice.html

### "WebXR not supported"
- Use Chrome 79+ or Firefox 98+
- For VR, use a Meta Quest browser or a WebXR-compatible headset

### "Thronglets not visible"
- Check browser DevTools Console for errors
- Verify vr_config.json is valid JSON
- Ensure the HTTP server is running

### "Poor VR performance"
- Close other browser tabs
- Reduce fog density in vr_config.json
- Check for console errors that may indicate rendering issues

## Dependencies

- **A-Frame 1.6.0**: 3D/VR framework (loaded from CDN)
- **A-Frame Extras 7.2.0**: Additional components (loaded from CDN)
- **Three.js**: 3D engine (bundled with A-Frame)

No build step or package manager required.

## License

MIT
