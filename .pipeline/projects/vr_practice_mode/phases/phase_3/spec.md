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