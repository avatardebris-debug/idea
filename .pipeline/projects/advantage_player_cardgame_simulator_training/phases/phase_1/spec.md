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