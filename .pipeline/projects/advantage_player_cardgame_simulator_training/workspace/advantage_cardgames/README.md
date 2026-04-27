# Advantage Card Games

A comprehensive framework for simulating blackjack games and training optimal strategies using Monte Carlo reinforcement learning.

## Features

- **Blackjack Simulation**: Complete blackjack game simulation with realistic rules
- **Monte Carlo Learning**: Reinforcement learning algorithms for strategy optimization
- **State-Value Estimation**: Track and learn state-action values for optimal play
- **Exploration Strategies**: Epsilon-greedy policy for balancing exploration vs exploitation
- **Model Persistence**: Save and load trained models for reuse

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

### Basic Simulation

```python
from advantage_cardgames.simulators import BlackjackGame

# Create a game instance
game = BlackjackGame()

# Play a single round
game.reset()
game.play_round()

# Get results
print(f"Player total: {game.player_hand.total}")
print(f"Dealer total: {game.dealer_hand.total}")
print(f"Result: {game.result}")
```

### Monte Carlo Training

```python
from advantage_cardgames.monte_carlo import MonteCarloTrainer, State, Action

# Create a trainer
trainer = MonteCarloTrainer(epsilon=0.1, seed=42)

# Train for 1000 episodes
stats = trainer.train(num_episodes=1000, verbose=True)
print(f"Trained on {stats['total_episodes']} episodes")
print(f"Average reward: {stats['avg_reward']:.3f}")

# Evaluate the learned policy
eval_results = trainer.evaluate(num_episodes=1000)
print(f"Win rate: {eval_results['win_rate']:.2%}")
```

### Using the Learned Policy

```python
from advantage_cardgames.monte_carlo import State

# Get the best action for a state
state = State(
    player_total=16,
    player_hand_type="hard",
    dealer_upcard=10,
    can_double=False,
    can_split=False,
    can_surrender=True
)

best_action = trainer.get_policy(state)
print(f"Best action: {best_action.value}")

# Get action values
action_values = trainer.get_action_values(state)
print(f"Action values: {action_values}")
```

## Project Structure

```
advantage_cardgames/
├── __init__.py              # Package initialization
├── core/                    # Core game primitives
│   ├── __init__.py
│   ├── card.py            # Card class
│   ├── deck.py            # Deck and shoe management
│   └── hand.py            # Hand representation and logic
├── simulators/             # Game simulations
│   ├── __init__.py
│   └── blackjack.py       # Blackjack game simulation
├── monte_carlo/            # Monte Carlo learning
│   ├── __init__.py
│   └── training.py        # Monte Carlo trainer and estimators
├── pyproject.toml         # Project configuration
└── README.md              # This file
```

## Monte Carlo Learning

The Monte Carlo trainer uses first-visit Monte Carlo control to learn optimal blackjack strategy:

1. **State Representation**: States are defined by player total, hand type (hard/soft/pair), dealer upcard, and available actions
2. **Action Values**: Q-values are tracked for each state-action pair
3. **Exploration**: Epsilon-greedy policy balances exploration and exploitation
4. **Policy Improvement**: Q-values are updated after each episode using returns

### State Features

- `player_total`: Current total of player's hand (1-21, or 22+ for bust)
- `player_hand_type`: Type of hand ('hard', 'soft', 'pair')
- `dealer_upcard`: Dealer's visible card (1-11, where 11 represents Ace)
- `can_double`: Whether doubling is allowed (initial 2 cards)
- `can_split`: Whether splitting is allowed (pair of same rank)
- `can_surrender`: Whether surrender is allowed (initial 2 cards, not blackjack)

### Available Actions

- `HIT`: Take another card
- `STAND`: End player's turn
- `DOUBLE`: Double bet and take exactly one more card
- `SPLIT`: Split pair into two separate hands
- `SURRENDER`: Forfeit half the bet and end hand

## Training Tips

1. **Start with high epsilon**: Begin with epsilon=0.1 to explore the state space
2. **Use decay**: Epsilon decay (default 0.995) gradually shifts to exploitation
3. **Train long enough**: Need thousands of episodes for convergence
4. **Save periodically**: Save trained models to avoid retraining
5. **Evaluate carefully**: Use zero epsilon for evaluation to see true policy quality

## Configuration

### MonteCarloTrainer Parameters

- `epsilon`: Initial exploration rate (default 0.1)
- `epsilon_decay`: Decay factor for epsilon (default 0.995)
- `seed`: Random seed for reproducibility (optional)
- `learning_rate`: Learning rate for Q-value updates (default 1.0)

### Training Parameters

- `num_episodes`: Number of episodes to train (default 1000)
- `verbose`: Print progress updates (default True)
- `save_interval`: Frequency of progress reports (default 100)

## Saving and Loading Models

```python
# Save trained model
trainer.save("blackjack_model.json")

# Load trained model
trainer = MonteCarloTrainer.load("blackjack_model.json")

# Evaluate loaded model
eval_results = trainer.evaluate(num_episodes=1000)
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Blackjack basic strategy as a baseline for comparison
- Monte Carlo control algorithms from reinforcement learning literature
- Card game simulation best practices
