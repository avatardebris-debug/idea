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