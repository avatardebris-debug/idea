## Phase 1: VR World Foundation — The Walkable Thronglet World

**Description**: Build the minimal VR experience: a 3D world where the player can put on a headset and see thronglets standing around. This is the "hello world" of VR practice mode. The player can look around, walk (teleport), and see thronglets as 3D avatars. No interaction yet — just presence.

**Deliverable**:
- A-Frame HTML application (`vr_practice.html`) that renders a 3D world with:
  - A ground plane with a grid texture (matching the 2D world's aesthetic)
  - 3-5 thronglet avatars as 3D objects (initially simple colored capsules with floating nameplates)
  - VR camera rig with teleportation-based movement (left/right controller triggers)
  - Thronglets rendered with a status halo (green/yellow/red ring around the avatar)
  - A simple skybox (gradient or simple scene)
  - Mouse/touch fallback for non-VR testing
- The thronglet positions and colors are loaded from the existing game state JSON (or a static config for now)
- The application runs in any WebXR-capable browser (Chrome on Quest, Firefox Reality, etc.)

**Dependencies**: None (standalone VR prototype)

**Success criteria**:
- Put on any WebXR headset → see a 3D world with 5 colored thronglet avatars
- Use controller triggers to teleport around the world
- Each thronglet has a visible nameplate and status halo
- Mouse/touch mode works for non-VR testing
- Application loads in under 3 seconds on a Quest 2

**Architecture notes**:
- Use A-Frame 1.5+ with `<a-scene embedded vr-mode-ui="enabled: false">`
- Thronglet avatars: `<a-entity>` with `<a-cylinder>` body + `<a-sphere>` head + `<a-text>` nameplate
- Status halo: `<a-torus>` ring that rotates slowly, colored by thronglet health
- Teleportation: A-Frame's built-in `<a-entity laser-controls="hand: left">` + raycaster-based teleport
- Config: `vr_config.json` maps thronglet IDs to 3D positions and colors

---