# Man or Mouse Game Simulator

A simple Python simulation for the "Man or Mouse" card game.

## Game Overview

"Man or Mouse" is a poker-like game where players must decide whether to "man" (play) or "mouse" (fold) based on the strength of their two-card hand. The game features a non-player entity called "The Peanut" who always plays and can force penalties on players who decide to man.

## Game Rules

- **Players**: 2 to 6 players (plus The Peanut)
- **Objective**: Win chips by "manning" and revealing a stronger hand than opponents and The Peanut
- **Setup**: Standard 52-card deck, each player antes 1 chip per round
- **The Peanut**: A non-player entity that always plays but can't win chips
- **Gameplay**: 
  - Each player receives 2 cards and decides to "man" or "mouse"
  - Players who "mouse" fold and take no further part in the round
  - If a player wins, they collect the pot and other players who "manned" must match the pot value (these matching payments go to the next round's pot)
  - If The Peanut wins, no one collects the pot (it carries forward) and all players who "manned" must match the pot (adding to it for the next round)
  - If no one "mans", the pot carries forward to the next round
  - If there's a tie for the best hand, no penalties are paid and the pot remains for the next round

## Project Structure

```
man-or-mouse/
├── README.md
├── requirements.txt
└── man_or_mouse/
    ├── __init__.py
    ├── card.py      # Card and hand representations
    ├── player.py    # Player classes and strategies
    ├── game.py      # Main game mechanics
    └── run_game.py  # Demo script to run a game
```

## How to Run

You can run the game with various options:

```bash
# Basic run with default settings
python3 -m man_or_mouse.run_game

# Run with a specific number of rounds
python3 -m man_or_mouse.run_game --rounds 10

# Run with a different number of players
python3 -m man_or_mouse.run_game --players 6

# Run with different starting chips
python3 -m man_or_mouse.run_game --chips 200

# Run with a fixed random seed for reproducibility
python3 -m man_or_mouse.run_game --seed 12345

# Combine options
python3 -m man_or_mouse.run_game --rounds 8 --players 3 --chips 150
```

## Available Options

| Option | Description | Default |
|--------|-------------|---------|
| `--rounds` | Number of rounds to play | 5 |
| `--players` | Number of players (2-6) | 4 |
| `--chips` | Initial chips per player | 100 |
| `--seed` | Random seed for reproducibility | based on current time |

## Creating Custom Strategies

You can create your own player strategies by subclassing the `Strategy` class in `player.py` and implementing the `make_decision` method.

Example:

```python
class MyStrategy(Strategy):
    def make_decision(self, hand: Hand, game_state: Dict[str, Any]) -> Decision:
        # Your decision logic here
        if some_condition:
            return Decision.MAN
        return Decision.MOUSE
```

## Built-in Strategies

1. **SimpleStrategy**: Always mans with pairs and high cards (A-K)
2. **RandomStrategy**: Randomly decides to man with configurable probability

## Chip Conservation

The simulation includes a chip conservation check at the end to ensure that all chips are properly accounted for throughout the game:

```
Chip Conservation Check:
Initial total chips: 400
Final total chips: 400
Expected final total: 400
✓ Chip conservation verified: All chips are accounted for
```

## Future Enhancements

- More sophisticated strategies
- Tournament simulation
- Statistical analysis of strategy performance
- Visualization of game results

## License

MIT