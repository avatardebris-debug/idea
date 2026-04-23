# Phase 1 Tasks — Shuffler Tracker Teacher

## Phase 1: Core Deck and Shuffle Visualization System

### Task 1: Create project structure and configuration
- **What to build**: Directory structure and configuration files for the shuffler tracker teacher project
- **Files**:
  - `phases/phase_1/tasks.md` (this file)
  - `workspace/shuffler_tracker/__init__.py`
  - `workspace/shuffler_tracker/config.py`
- **Acceptance criteria**:
  - Project directory structure is created
  - Config file contains basic settings (deck size, shuffle iterations, visualization parameters)
  - __init__.py makes the package importable

### Task 2: Implement Card class
- **What to build**: A Card class representing individual playing cards
- **Files**:
  - `workspace/shuffler_tracker/models/card.py`
- **Acceptance criteria**:
  - Card has rank (2-10, J, Q, K, A) and suit (hearts, diamonds, clubs, spades)
  - Card has proper string representation (e.g., "A♠", "K♥")
  - Card supports equality comparison
  - Card can be serialized/deserialized to JSON

### Task 3: Implement Deck class
- **What to build**: A Deck class representing a standard 52-card deck
- **Files**:
  - `workspace/shuffler_tracker/models/deck.py`
- **Acceptance criteria**:
  - Deck contains exactly 52 unique cards
  - Deck can be created fresh or from a list
  - Deck supports shuffling (Fisher-Yates algorithm)
  - Deck supports cutting at a specific position
  - Deck can be serialized/deserialized to JSON

### Task 4: Implement ShuffleCut class
- **What to build**: A class to represent and analyze shuffle cuts
- **Files**:
  - `workspace/shuffler_tracker/models/shuffle_cut.py`
- **Acceptance criteria**:
  - Represents a cut operation with left_half_size and right_half_size
  - Validates that left + right = total deck size
  - Computes cut_ratio (left/total)
  - Can be serialized/deserialized to JSON

### Task 5: Implement Shuffle Simulator
- **What to build**: A simulator that performs multiple shuffle trials with stochastic cut variation
- **Files**:
  - `workspace/shuffler_tracker/simulator.py`
- **Acceptance criteria**:
  - Can run N shuffle iterations
  - Each iteration performs a random cut with variation around 26/26 (e.g., 20/30, 30/20)
  - Cut distribution is statistically centered around 26/26
  - Returns list of ShuffleCut results with statistics (mean, std, distribution)
  - Configurable cut variation range (default ±6 cards)

### Task 6: Create basic visualization module
- **What to build**: A visualization module to display shuffle results
- **Files**:
  - `workspace/shuffler_tracker/visualizer.py`
- **Acceptance criteria**:
  - Can visualize a single deck before and after shuffle
  - Can visualize cut distribution as a histogram
  - Output can be saved as PNG images
  - Uses matplotlib for rendering

### Task 7: Create main entry point
- **What to build**: A CLI or script to run the shuffler tracker
- **Files**:
  - `workspace/shuffler_tracker/main.py`
- **Acceptance criteria**:
  - Can run a specified number of shuffle iterations
  - Can output results to console and save visualizations
  - Accepts command-line arguments for configuration
  - Prints summary statistics after completion

### Task 8: Write tests for Phase 1
- **What to build**: Unit tests for all Phase 1 components
- **Files**:
  - `workspace/tests/test_card.py`
  - `workspace/tests/test_deck.py`
  - `workspace/tests/test_shuffle_cut.py`
  - `workspace/tests/test_simulator.py`
  - `workspace/tests/test_visualizer.py`
- **Acceptance criteria**:
  - All tests pass
  - Test coverage is >80% for core classes
  - Tests verify Card uniqueness in Deck
  - Tests verify Fisher-Yates shuffling randomness
  - Tests verify cut distribution statistics
