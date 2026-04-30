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

##