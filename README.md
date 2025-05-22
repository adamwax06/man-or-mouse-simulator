# Man or Mouse Game Simulator

A comprehensive Python simulation for the "Man or Mouse" card game with theoretical probability-based strategy optimization.

## Game Overview

"Man or Mouse" is a poker-like game where players must decide whether to "man" (play) or "mouse" (fold) based on the strength of their two-card hand. The game features a non-player entity called "The Peanut" who always plays and can force penalties on players who decide to man.

## Game Rules

- **Players**: 2 to 5 players (plus The Peanut)
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
└── probabilities/
    ├── find_probabilities.py  # Calculates all theoretical win percentages
    └── probabilities.txt      # Complete theoretical probability data
```

## How to Run

You can run the game with various options:

```bash
# Basic run with default settings (mixed strategies)
python3 -m man_or_mouse.run_game

# Run with all MaxEV players (theoretically optimal)
python3 -m man_or_mouse.run_game --strategy maxev

# Run with all simple strategy players
python3 -m man_or_mouse.run_game --strategy simple

# Run with all random players
python3 -m man_or_mouse.run_game --strategy random

# Run with mixed strategies for comparison
python3 -m man_or_mouse.run_game --strategy mixed --rounds 20

# Run with specific game parameters
python3 -m man_or_mouse.run_game --rounds 10 --players 5 --chips 200

# Run with a fixed random seed for reproducibility
python3 -m man_or_mouse.run_game --seed 12345
```

## Available Options

| Option | Description | Default | Valid Values |
|--------|-------------|---------|--------------|
| `--rounds` | Number of rounds to play | 5 | Any positive integer |
| `--players` | Number of players | 4 | 2-5 |
| `--chips` | Initial chips per player | 100 | Any positive integer |
| `--strategy` | Player strategy type | mixed | simple, random, maxev, mixed |
| `--seed` | Random seed for reproducibility | current time | Any integer |

## Built-in Strategies

### 1. **SimpleStrategy**
- Always mans with pairs
- Mans with high cards (A-K)
- Mouse with everything else

### 2. **RandomStrategy**
- Randomly decides to man with configurable probability
- Default: 50% chance to man

### 3. **MaxEVStrategy** ⭐
- **Theoretically optimal strategy** using exact probability calculations
- Uses the complete theoretical win probability dataset
- Makes decisions based on Expected Value: `E[X] = P × (w - l)`
- Where `P` = pot size, `w` = win probability, `l` = loss probability
- **Decision Rule**: Man if `P(win) > P(loss)`, otherwise Mouse
- Automatically adapts to game size (2-5 players + peanut)

## Theoretical Probability Data

The simulator includes a complete dataset of theoretical win probabilities:

- **455 total probability entries** (91 hands × 5 game sizes)
- **Exact mathematical calculations** (no approximation)
- **All possible 2-card hands** from AA (best) to 32 (worst)
- **Game sizes**: 2-6 total participants (1-5 players + peanut)

### Sample Probabilities (4-person game):
```
Hand     Win%       Tie%       Loss%
AA      99.755%     0.245%     0.000%
KK      98.290%     0.242%     1.468%
AK      81.457%     1.939%    16.604%
72       0.102%     0.025%    99.873%
```

## Creating Custom Strategies

You can create your own player strategies by subclassing the `Strategy` class:

```python
class MyCustomStrategy(Strategy):
    def make_decision(self, hand: Hand, game_state: Dict[str, Any]) -> Decision:
        # Access game state information
        pot_size = game_state['pot']
        num_players = len(game_state['players'])
        
        # Your decision logic here
        if some_condition:
            return Decision.MAN
        return Decision.MOUSE
```



## Expected Strategy Performance

Based on theoretical analysis:

1. **MaxEVStrategy**: Should significantly outperform all other strategies
2. **SimpleStrategy**: Reasonable performance with simple heuristics
3. **RandomStrategy**: Performance varies with man probability setting

## Chip Conservation

The simulation includes robust chip conservation verification:

```
Chip Conservation Check:
Initial total chips: 500
Final total chips: 500
Buy-ins during game: 0
Expected final total: 500
✓ Chip conservation verified: All chips are accounted for
```

## Advanced Features

- **Automatic buy-ins** when players run out of chips
- **Detailed round-by-round tracking**
- **Strategy performance metrics**
- **Reproducible games** with seed control
- **Comprehensive error checking**

## Files Overview

- **`card.py`**: Card, Hand, and Deck classes with poker hand evaluation
- **`player.py`**: Player class and all strategy implementations
- **`game.py`**: Core game mechanics and round management
- **`run_game.py`**: Command-line interface and game runner
- **`probabilities/`**: Complete theoretical probability calculations

## Future Enhancements

- Tournament simulation with elimination
- Advanced statistical analysis and visualization
- Machine learning-based adaptive strategies
- Web interface for interactive play
- Strategy parameter optimization

## License

MIT