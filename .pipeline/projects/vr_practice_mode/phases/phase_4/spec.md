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

