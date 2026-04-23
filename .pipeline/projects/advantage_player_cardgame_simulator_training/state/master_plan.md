# Advantage Player Card Game Simulator Training — Master Plan

## Core Deliverable
A Python-based suite of card game simulators (blackjack, video poker, tournament/cash poker, 7-card stud, progressive slot calculator) with Monte Carlo training engine for advantage play. The suite enables users to simulate games at scale, train optimal strategies via Monte Carlo methods, and analyze edge/expected value across game variants.

## Architecture Notes

```
advantage_cardgames/
├── core/                    # Abstract game engine
│   ├── game.py              # Base Game class (deck, hands, rounds, outcomes)
│   ├── deck.py              # Deck, shoe, shuffle strategies
│   ├── hand.py              # Hand evaluation, scoring
│   └── state.py             # Game state serialization
├── simulators/              # Individual game implementations
│   ├── blackjack.py         # Blackjack simulator + basic strategy trainer
│   ├── video_poker.py       # Video poker (Jacks or Better, Deuces Wild, etc.)
│   ├── poker/
│   │   ├── holdem.py        # Texas Hold'em (cash + tournament)
│   │   ├── stud.py          # 7-card Stud
│   │   └── icm.py           # ICM (Independent Chip Model) for tournaments
│   └── slots.py             # Progressive jackpot slot calculator
├── monte_carlo/             # Monte Carlo training engine
│   ├── engine.py            # Core MCTS/simulation loop
│   ├── policy.py            # Policy representation & updates
│   ├── value_net.py         # Optional: neural value approximation
│   └── trainer.py           # Training loop, convergence tracking
├── analysis/                # Analytics & reporting
│   ├── ev_calculator.py     # Expected value computation
│   ├── variance.py          # Variance, standard deviation, ROI
│   └── report.py            # HTML/PDF report generation
├── strategy/                # Strategy management
│   ├── basic_strategy.py    # Precomputed basic strategy tables
│   ├── optimal.py           # Optimal strategy solver (GTO)
│   └── explorer.py          # Exploration/exploitation utilities
├── cli/                     # Command-line interface
│   └── main.py              # CLI entry point
├── tests/
│   ├── test_blackjack.py
│   ├── test_video_poker.py
│   ├── test_poker.py
│   ├── test_monte_carlo.py
│   └── test_integration.py
├── benchmarks/              # Reference results for validation
│   ├── blackjack_basic.json
│   ├── video_poker_paytables.json
│   └── poker_nash_reference.json
├── pyproject.toml
└── requirements.txt
```

**Key design decisions:**
- Pure Python (no heavy dependencies for core). Use `numpy` for vectorized Monte Carlo.
- Leverage `pokerkit` (pip-installable) for poker hand evaluation and `poker-mtt-icM-master` concepts for tournament ICM.
- All games share a common `Game` base class for uniform simulation API.
- Monte Carlo engine is game-agnostic; each game implements a `get_legal_actions()` and `apply_action()` interface.
- Strategy tables stored as JSON for easy loading/export.

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep — too many games | High | Strict phase boundaries; defer 7-card stud and slots to Phase 5 |
| Poker complexity (Nash equilibrium, ICM) | High | Use existing libraries (pokerkit, poker-mtt-icm-master) as reference; don't reimplement from scratch |
| Monte Carlo convergence uncertainty | Medium | Implement convergence diagnostics; allow user-configurable iteration counts |
| Performance with large simulations | Medium | Use numpy vectorization; add progress bars; support chunked processing |
| Strategy accuracy validation | High | Benchmark against known optimal strategies and published EV tables |

---

## Phase 1: Core Engine + Blackjack Simulator

**Description:** Build the foundational game engine and a working blackjack simulator with basic strategy trainer. This is the smallest useful deliverable — a player can simulate blackjack hands, test basic strategy, and see EV results.

**Deliverable:** 
- `core/game.py`, `core/deck.py`, `core/hand.py` — abstract game engine
- `simulators/blackjack.py` — blackjack simulator with configurable rules (dealer stands/hits on 17, number of decks, surrender, etc.)
- `strategy/basic_strategy.py` — precomputed blackjack basic strategy table
- `cli/main.py` — CLI to run blackjack simulations
- Full test suite for Phase 1

**Dependencies:** None (foundation phase)

**Success Criteria:**
- [ ] Deck can be created, shuffled, and dealt correctly
- [ ] Blackjack hand evaluation works (blackjack, bust, push, win, loss)
- [ ] Blackjack simulator runs 100,000+ hands in under 30 seconds
- [ ] Basic strategy is applied correctly and matches known reference tables
- [ ] EV calculation is within 0.1% of published basic strategy EV for standard rules
- [ ] All unit tests pass
- [ ] CLI can run: `python -m advantage_cardgames blackjack --hands 100000 --strategy basic`

---

## Phase 2: Video Poker Simulator + Optimal Strategy Calculator

**Description:** Implement video poker simulator supporting multiple variants (Jacks or Better, Deuces Wild, Bonus Poker, etc.) with a hand-evaluation engine and optimal strategy calculator using Monte Carlo or exhaustive enumeration.

**Deliverable:**
- `simulators/video_poker.py` — video poker simulator with multiple paytable variants
- `core/hand.py` extended with poker hand ranking (pairs, flushes, straights, full houses, etc.)
- `strategy/optimal.py` — optimal hold/discard strategy solver
- `analysis/ev_calculator.py` — EV per paytable variant
- `benchmarks/video_poker_paytables.json` — reference paytables and known EVs

**Dependencies:** Phase 1 (core engine, deck, hand evaluation)

**Success Criteria:**
- [ ] Supports Jacks or Better, Deuces Wild, Bonus Poker, Aces and Faces
- [ ] Hand evaluation matches standard poker hand rankings
- [ ] Optimal strategy matches published strategy charts within 0.01% EV
- [ ] Paytable configuration is flexible (user-defined paytables)
- [ ] EV for full-pay Jacks or Better (9/6) matches known value (~99.54%)
- [ ] CLI: `python -m advantage_cardgames video_poker --variant jacks_or_better --paytable 9_6 --hands 100000`

---

## Phase 3: Poker Suite — Texas Hold'em + ICM

**Description:** Implement Texas Hold'em simulator (cash game and tournament modes) with ICM (Independent Chip Model) for tournament payouts. Leverage `pokerkit` for hand evaluation and study `poker-mtt-icM-master` for ICM implementation.

**Deliverable:**
- `simulators/poker/holdem.py` — Texas Hold'em simulator (cash + tournament)
- `simulators/poker/icm.py` — ICM payout calculator
- `pokerkit` integration for hand evaluation
- `strategy/nash.py` — simplified Nash equilibrium solver for heads-up
- `analysis/variance.py` — tournament variance and ROI analysis

**Dependencies:** Phase 1 (core engine), Phase 2 (hand evaluation)

**Success Criteria:**
- [ ] Cash game Hold'em simulates complete hands (pre-flop through river)
- [ ] Tournament mode supports multi-table scenarios with ICM payouts
- [ ] ICM payouts match known reference calculations (±0.5%)
- [ ] Heads-up Nash equilibrium solver produces reasonable strategy
- [ ] Simulates 10,000 tournament hands in under 60 seconds
- [ ] CLI: `python -m advantage_cardgames poker --mode tournament --players 9 --icm`

---

## Phase 4: Monte Carlo Training Engine

**Description:** Build the core Monte Carlo training engine that can train strategies for any supported game. Implements Monte Carlo Tree Search (MCTS) or policy gradient methods with convergence tracking.

**Deliverable:**
- `monte_carlo/engine.py` — MCTS/simulation loop
- `monte_carlo/policy.py` — policy representation (action-value tables, neural net interface)
- `monte_carlo/trainer.py` — training loop with convergence diagnostics
- `monte_carlo/value_net.py` — optional neural value function (PyTorch, lazy dependency)
- `analysis/report.py` — training progress reports (HTML/JSON)

**Dependencies:** Phases 1-3 (all game simulators must implement `get_legal_actions()` and `apply_action()`)

**Success Criteria:**
- [ ] Training engine trains blackjack strategy to within 0.5% of optimal in < 500K iterations
- [ ] Training engine trains video poker strategy to within 0.1% of optimal
- [ ] Convergence diagnostics (moving average EV, variance reduction) work correctly
- [ ] Training results are reproducible with fixed seed
- [ ] CLI: `python -m advantage_cardgames train --game blackjack --iterations 500000 --output results.json`

---

## Phase 5: Additional Games — 7-Card Stud + Progressive Slots

**Description:** Implement 7-card Stud simulator and progressive jackpot slot machine calculator. These are lower-priority games that expand the suite's coverage.

**Deliverable:**
- `simulators/stud.py` — 7-card Stud simulator
- `simulators/slots.py` — Progressive jackpot slot calculator
- `analysis/ev_calculator.py` extended for slot EV
- Updated benchmarks

**Dependencies:** Phase 1 (core engine)

**Success Criteria:**
- [ ] 7-card Stud simulates complete hands with correct ante/bring-in mechanics
- [ ] Slot calculator supports multiple reel configurations and progressive jackpots
- [ ] Slot EV matches manufacturer-published return percentages
- [ ] Both games work with the Monte Carlo training engine
- [ ] CLI: `python -m advantage_cardgames slots --reels 5 --paylines 20 --jackpot progressive`

---

## Phase 6: Unified Dashboard + Advanced Analytics

**Description:** Build a unified dashboard (CLI-first, optional web) for comparing strategies across games, advanced analytics (variance analysis, bankroll simulation, Kelly criterion), and export capabilities.

**Deliverable:**
- `cli/dashboard.py` — unified dashboard for strategy comparison
- `analysis/bankroll.py` — bankroll simulation with Kelly criterion
- `analysis/comparison.py` — side-by-side strategy comparison
- Export to CSV/HTML/PDF
- Documentation and examples

**Dependencies:** All previous phases

**Success Criteria:**
- [ ] Dashboard can compare blackjack basic strategy vs. trained strategy side-by-side
- [ ] Bankroll simulator with Kelly fraction recommendations
- [ ] Export results to CSV and HTML reports
- [ ] Complete documentation with examples
- [ ] CLI: `python -m advantage_cardgames dashboard --compare blackjack_basic vs blackjack_trained`

---

## Summary

| Phase | Focus | Est. Complexity | Key Output |
|-------|-------|----------------|------------|
| 1 | Core engine + Blackjack | Low | Working blackjack simulator with basic strategy |
| 2 | Video Poker | Medium | Multi-variant video poker with optimal strategy |
| 3 | Poker + ICM | High | Hold'em (cash/tournament) with ICM payouts |
| 4 | Monte Carlo Training | High | Game-agnostic training engine |
| 5 | Additional Games | Medium | 7-card Stud + progressive slots |
| 6 | Dashboard + Analytics | Medium | Unified interface, bankroll tools, export |

**Recommended execution order:** 1 → 2 → 4 → 3 → 5 → 6
(Rationale: Get the training engine (Phase 4) before Phase 3 so poker strategies can benefit from Monte Carlo training early. Phase 5 and 6 are lower priority.)
