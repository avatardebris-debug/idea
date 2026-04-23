# Phase 1 Tasks

- [ ] Task 1: Project scaffolding
  - What: Create pyproject.toml, package directory structure, and base __init__.py files
  - Files: pyproject.toml, gameagent/__init__.py, gameagent/env/__init__.py, gameagent/agent/__init__.py, gameagent/cli/__init__.py
  - Done when: `pip install -e .` succeeds from the project root and `import gameagent` works without errors

- [ ] Task 2: Game environment core
  - What: Implement GridWorld environment with a gymnasium-compatible interface — state representation, action space (UP/DOWN/LEFT/RIGHT/INTERACT), observation space, reward logic, and goal/obstacle placement
  - Files: gameagent/env/grid_world.py, gameagent/env/types.py
  - Done when: GridWorld can be instantiated, reset() returns a valid observation, step() with valid actions returns (obs, reward, done, info), and the agent can reach a goal tile in a deterministic test

- [ ] Task 3: Agent interface and baseline agent
  - What: Implement BaseAgent abstract class with act(obs) → action interface, and a RandomAgent concrete implementation that selects random valid actions
  - Files: gameagent/agent/base.py, gameagent/agent/random_agent.py
  - Done when: RandomAgent can be instantiated and called with observations from GridWorld, returning valid actions; BaseAgent enforces act() via abstract method

- [ ] Task 4: Simulation loop and data collection
  - What: Implement EpisodeRunner that runs full episodes (reset → step until done), collects trajectories (obs, action, reward, next_obs, done tuples), and computes episode stats (total reward, steps, success)
  - Files: gameagent/sim/runner.py, gameagent/sim/types.py
  - Done when: EpisodeRunner.run_episode() returns a complete trajectory; EpisodeRunner.run_multiple() returns stats for multiple episodes; RandomAgent achieves >0 reward in at least 80% of 50 episodes on a 10x10 grid with a single goal

- [ ] Task 5: CLI entry point and unit tests
  - What: Implement CLI with `ga sim run` (runs a simulation and prints stats) and `ga sim stats` (prints summary), plus unit tests for GridWorld, RandomAgent, and EpisodeRunner
  - Files: gameagent/cli/main.py, tests/test_grid_world.py, tests/test_random_agent.py, tests/test_runner.py
  - Done when: `ga sim run` executes a 100-step simulation and prints total reward/steps/success; all three test files pass with `pytest`
