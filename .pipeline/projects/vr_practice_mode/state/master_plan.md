# Master Plan: VR Practice Mode

## Goal
Extend the existing Thronglets-as-a-Game into a VR practice environment where players can step inside the thronglet world, interact with thronglets in 3D/VR space, and use the immersive environment to practice real-world system-building tasks (architecture decisions, debugging, deployment workflows) as guided exercises.

## Core Deliverable
A VR application (WebXR-based for broad headset compatibility) that renders the thronglet world in 3D, allows the player to walk around, grab and talk to thronglets, and complete practice scenarios where thronglets represent real infrastructure components (servers, databases, CI pipelines) that the player must "build" and "manage" through VR interactions.

## Architecture Notes
- **Rendering**: A-Frame (WebXR, runs in any headset browser) + Three.js for custom thronglet 3D models. Fallback: Unity WebGL for higher-fidelity headsets.
- **Thronglet representation**: Each thronglet becomes a 3D avatar (animated mesh) with a floating nameplate, relationship lines (glowing threads between thronglets), and a status halo (green/yellow/red ring).
- **Interaction model**: VR controllers (or mouse/touch fallback) for grabbing thronglets, pointing at them to send prompts, and manipulating 3D UI panels for practice scenarios.
- **State sync**: The existing game state (JSON) is the source of truth. The VR layer reads it and renders accordingly. No duplication of game logic.
- **Practice scenarios**: YAML-defined scenarios (similar to Phase 3's scenario mode) that spawn thronglets, set up a world state, and present the player with a task (e.g., "The database thronglet is red — fix it").
- **Integration path**: VR layer is a separate frontend that connects to the existing game backend. The backend doesn't change; the VR layer is a new client.

## Risks
1. **WebXR compatibility**: Not all browsers support WebXR. Mitigation: provide mouse/touch fallback, and use A-Frame's built-in XR support which handles most headset quirks.
2. **3D art assets**: Creating thronglet avatars in 3D is time-consuming. Mitigation: start with simple geometric shapes (spheres, capsules) with animated shaders, iterate on art later.
3. **VR motion sickness**: Fast camera movement or jittery thronglet AI could cause discomfort. Mitiation: teleportation-based movement (no smooth locomotion), smooth thronglet paths, and a comfort mode with vignette.
4. **Scope creep into full VR game**: The practice mode is the goal, not a full VR game engine. Mitigation: strict scope — no multiplayer, no custom physics, no VR social features beyond thronglet interaction.
5. **Performance on standalone headsets**: Quest 2/3 have limited GPU. Mitigation: LOD for thronglet models, simplified shaders, and a "low-poly" mode.

---

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

## Phase 2: VR Thronglet Interaction — Talk, Grab, and Observe

**Description**: Add the ability for the player to interact with thronglets in VR. The player can point at a thronglet to see its details, "grab" it to bring it closer, and send it prompts (via voice or VR keyboard). Thronglets respond with 3D animations (bounce, spin, color flash) and speech bubbles in 3D space.

**Deliverable**:
- **Point-and-look interaction**: When the player aims a controller at a thronglet and holds for 1 second, a detail panel appears next to the thronglet showing:
  - Name, mood, personality traits
  - Current state (wandering, idle, collaborating)
  - Relationship lines to nearby thronglets (visible as glowing threads)
  - Token count
- **Grab mechanic**: Player can grab a thronglet and drag it closer. Releasing it drops it back. Grabbing triggers a "greeting" animation.
- **Prompt sending**: A VR keyboard appears when the player points at a thronglet and taps a "talk" button. The player types a prompt, and the thronglet responds with a speech bubble (3D text above its head) and an animation.
- **Thronglet response system**: Thronglets use the same AI as the 2D game (config-driven personality) but rendered in 3D. Responses are animated: the thronglet bounces, spins, or changes color based on the prompt.
- **Relationship visualization**: Glowing threads between related thronglets (friend = pink thread, rival = red thread, mentor = blue thread). Threads pulse when the relationship is active.
- **Proximity alerts**: When a player approaches a thronglet, a subtle glow appears around it, and a small notification panel shows "Approaching [name]..."

**Dependencies**: Phase 1 (VR world must exist)

**Success criteria**:
- Point at a thronglet for 1 second → see its detail panel with name, mood, personality
- Grab a thronglet and drag it → it follows the controller, releases when dropped
- Type a prompt via VR keyboard → thronglet responds with speech bubble and animation
- Relationship threads are visible between connected thronglets and pulse when active
- All interactions work in both VR and mouse/touch mode
- 60fps on Quest 2 during interactions

**Architecture notes**:
- Point interaction: A-Frame raycaster + `setAttribute` on hover timeout
- Grab: `<a-entity>` with `grab-controls` component (custom A-Frame component)
- VR keyboard: A-Frame's `<a-text>` input component or a custom VR keyboard mesh
- Speech bubbles: `<a-text>` entity positioned above thronglet, fades in/out
- Relationship threads: `<a-cylinder>` entities with custom shader (glowing, pulsing)
- Thronglet AI: Reuse the existing Python backend's AI config; VR layer sends prompts via WebSocket or file polling

---

## Phase 3: Practice Mode — Guided System-Building Scenarios

**Description**: Add the actual "practice mode" — structured scenarios where thronglets represent real infrastructure components, and the player must complete tasks by interacting with them in VR. This is the core of the product. Scenarios are YAML-defined and include a world setup, thronglet roles, and a series of challenges.

**Deliverable**:
- **Scenario engine**: A system that loads YAML scenario definitions and sets up the VR world accordingly:
  - Scenario definition format: `scenario_name`, `description`, `thronglet_roles` (each thronglet maps to a real component: "database", "web server", "CI pipeline"), `initial_state`, `objectives` (list of tasks), `success_conditions`
  - Example scenario: "Deploy a Web App" — player must guide a frontend thronglet, backend thronglet, and database thronglet through a deployment workflow
- **Practice UI**: In VR, the player sees:
  - A "scenario panel" (floating 3D board) showing the current objective
  - Thronglets with role labels (e.g., "DB Thronglet" with a database icon)
  - Task steps displayed as floating cards that the player can "grab" and "complete"
  - Progress tracking: a VR progress bar that fills as objectives are completed
- **Interaction-based task completion**: Tasks are completed through VR interactions:
  - "Connect the database" → player grabs the DB thronglet and drags it to the web server thronglet (creates a connection thread)
  - "Fix the error" → player points at a red thronglet, reads its error message, and drags a "fix" tool (VR wrench icon) to it
  - "Deploy" → player grabs the deploy thronglet and drops it onto a "deployment zone" (marked on the ground)
- **Feedback system**: When a task is completed, the VR world responds:
  - Connected thronglets glow green and form a permanent thread
  - Fixed thronglets change from red to green with a "success" animation
  - A "level up" animation plays with confetti particles
- **Scenario library**: 3 pre-built scenarios:
  1. "Deploy a Web App" — guide 3 thronglets through deployment
  2. "Debug a Production Issue" — diagnose and fix a red thronglet
  3. "Scale Your Infrastructure" — add new thronglets and balance load

**Dependencies**: Phase 2 (interaction system must exist)

**Success criteria**:
- Load any of the 3 scenarios → world sets up correctly with labeled thronglets and objectives
- Complete all objectives in "Deploy a Web App" by interacting with thronglets in VR
- Progress bar updates in real-time as tasks are completed
- Success animation plays when all objectives are done
- Player can restart a scenario from the VR menu
- All scenario interactions work in both VR and mouse/touch mode

**Architecture notes**:
- Scenario definitions: `scenarios/<name>.yaml` with structured schema
- Scenario engine: Python script that loads YAML and generates VR config JSON
- VR config JSON includes: thronglet positions/roles, initial states, task definitions, success conditions
- Task completion: VR interaction events trigger Python backend to validate the action
- Feedback animations: A-Frame animations + custom particle system (A-Frame particle library)
- Scenario library: JSON manifest file listing all available scenarios with thumbnails

---

## Phase 4: Multi-Thronglet Collaboration — Team Practice Mode

**Description**: Extend practice mode to support multiple players in the same VR world. Players can collaborate on scenarios, with each player controlling one or more thronglets. This enables team training, pair debugging, and collaborative architecture planning.

**Deliverable**:
- **Multiplayer VR**: WebRTC-based real-time sync allowing 2-4 players in the same VR instance:
  - Each player has their own camera rig and controller set
  - Players can see each other as VR avatars (simple humanoid shapes)
  - Player names appear above their avatars
  - Players can share the same thronglet (one player controls the thronglet, others observe and advise)
- **Collaborative scenarios**: Scenarios designed for multiple players:
  - "Build a Microservices Architecture" — each player controls one service thronglet, they must coordinate to build the system
  - "Incident Response" — players must work together to diagnose and fix a cascading failure
  - "Code Review" — one player plays the "reviewer thronglet", others play the "developer thronglets"
- **Shared VR UI**: All players see the same scenario panels, progress bars, and thronglet states
- **Voice chat**: WebRTC audio between players (optional, can be disabled for accessibility)
- **Spectator mode**: A 5th player can join as a spectator, observing without controlling anything

**Dependencies**: Phase 3 (scenario engine must exist)

**Success criteria**:
- 2 players can join the same VR world and see each other's avatars
- Both players can interact with thronglets simultaneously
- Collaborative scenarios work with 2+ players
- Progress bar updates for all players
- Spectator mode works (observe without controlling)
- Voice chat is optional and can be toggled per player

**Architecture notes**:
- Multiplayer: A-Frame's `<a-scene>` with `multiplayer` component or custom WebRTC signaling
- Player avatars: Simple humanoid `<a-entity>` with controller-based hands
- State sync: CRDT-based sync for thronglet positions/states, authoritative server for scenario state
- Voice: WebRTC DataChannel for audio, or integrate with Discord/Zoom for production use
- Spectator mode: Camera rig with no controller input, free-look only

---

## Phase 5: Real-World Bridge — Live Infrastructure Practice

**Description**: Connect the VR practice mode to real infrastructure. Thronglets in the VR world reflect the state of real systems (Docker containers, GitHub repos, AWS services). Players practice managing real infrastructure in VR, with the VR layer acting as an immersive dashboard.

**Deliverable**:
- **Real-world thronglet binding**: Each thronglet can be bound to a real system:
  - Docker container → thronglet color reflects container health
  - GitHub repo → thronglet shows PR count, build status
  - AWS service → thronglet shows CPU/memory/request metrics
- **Live VR dashboard**: The VR world updates in real-time based on real system state:
  - Thronglets change color when real systems go down
  - Connection threads between thronglets represent real network connections
  - Speech bubbles show real error messages and logs
- **VR command execution**: Player actions in VR execute real commands:
  - "Deploy" → triggers a real CI/CD pipeline
  - "Scale" → adjusts Docker container count
  - "Restart" → restarts a real service
- **Safety gate**: All real-world actions go through a confirmation step and the existing governance system (constitution.yaml rules)
- **Scenario mode for real systems**: Pre-built scenarios that use real infrastructure:
  - "Monitor your stack" — practice watching real systems in VR
  - "Respond to an outage" — practice incident response with real data
  - "Deploy to production" — practice deployment workflow with real tools

**Dependencies**: Phase 4 (multiplayer and scenario engine must exist)

**Success criteria**:
- A thronglet bound to a real Docker container changes color when the container goes down
- Clicking "deploy" on a thronglet triggers a real CI/CD pipeline
- All real-world actions require confirmation and pass governance checks
- "Monitor your stack" scenario works end-to-end with real infrastructure
- VR dashboard updates in real-time (refresh rate < 5 seconds)

**Architecture notes**:
- Real-world bridge: Existing `Bridge` class from Phase 3 of the main game, extended for VR
- State sync: WebSocket connection between VR layer and game backend
- Command execution: Sandbox-based (Docker-in-Docker) for safety
- Governance: Reuse constitution.yaml rules, add VR-specific safety checks
- Monitoring: Prometheus/Grafana integration for real-time metrics

---

## Summary of Phases

| Phase | Description | Scope | Key Risk |
|-------|-------------|-------|----------|
| 1 | VR World Foundation | Walkable 3D world with thronglet avatars | WebXR compatibility |
| 2 | VR Thronglet Interaction | Point, grab, talk to thronglets in VR | Motion sickness, interaction latency |
| 3 | Practice Mode | Guided scenarios with VR task completion | Scenario design complexity |
| 4 | Multi-Thronglet Collaboration | 2-4 players in same VR world | WebRTC complexity, state sync |
| 5 | Real-World Bridge | Connect VR to real infrastructure | Security, safety, scope creep |

## Recommended Implementation Order
1-2-3-4-5 (sequential, each phase builds on the previous)

## Estimated Effort (per phase)
- Phase 1: 1-2 days (prototype)
- Phase 2: 2-3 days
- Phase 3: 3-4 days
- Phase 4: 3-5 days
- Phase 5: 4-6 days

**Total**: ~13-20 days for a complete VR practice mode.
