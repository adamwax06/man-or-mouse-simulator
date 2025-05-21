"""
Sample script to run a Man or Mouse game
"""
import random
import time
import argparse
from typing import List, Dict

from man_or_mouse.player import Player, RandomStrategy, SimpleStrategy
from man_or_mouse.game import ManOrMouseGame


def main():
    """Run a simple Man or Mouse game demo"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a Man or Mouse game simulation")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--rounds", type=int, default=5, help="Number of rounds to play")
    parser.add_argument("--players", type=int, default=4, help="Number of players")
    parser.add_argument("--chips", type=int, default=100, help="Initial chips per player")
    args = parser.parse_args()
    
    # Set random seed or use current time for true randomness
    seed = args.seed if args.seed is not None else int(time.time())
    random.seed(seed)
    
    print(f"Game initialized with random seed: {seed}")
    
    # Create players with different strategies
    player_names = ["Alice", "Bob", "Charlie", "Dave", "Eve", "Frank"]
    strategies = [
        SimpleStrategy(),
        RandomStrategy(man_probability=0.7),
        RandomStrategy(man_probability=0.3),
        SimpleStrategy()
    ]
    
    # Ensure we don't try to create more players than we have names for
    num_players = min(args.players, len(player_names))
    
    players = [
        Player(player_names[i], strategies[i % len(strategies)], initial_chips=args.chips)
        for i in range(num_players)
    ]
    
    # Create and run game
    game = ManOrMouseGame(players, verbose=True)
    results = game.play_game(num_rounds=args.rounds)
    
    # Print final results
    print("\n" + "=" * 50)
    print("FINAL GAME RESULTS")
    print("=" * 50)
    print(f"Rounds played: {results['rounds_played']}")
    print(f"Final pot: {results['final_pot']} chips")
    
    if results.get('total_buy_ins', 0) > 0:
        print(f"Total buy-ins: {results['total_buy_ins']} chips")
    
    print("\nPlayer chips:")
    
    # Sort players by chips
    sorted_players = sorted(
        [(name, data['chips']) for name, data in results['players'].items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    for name, chips in sorted_players:
        print(f"{name}: {chips} chips")
    
    # Print chip conservation check
    if 'chip_conservation' in results:
        print("\nChip Conservation Check:")
        conservation = results['chip_conservation']
        print(f"Initial total chips: {conservation['initial_chips']}")
        print(f"Final total chips: {conservation['final_chips']}")
        
        if conservation['buy_ins'] > 0:
            print(f"Buy-ins during game: {conservation['buy_ins']}")
            
        print(f"Expected final total: {conservation['expected_total']}")
        
        if conservation['is_balanced']:
            print("✓ Chip conservation verified: All chips are accounted for")
        else:
            print(f"⚠ Chip conservation error: Discrepancy of {conservation['final_chips'] - conservation['expected_total']} chips")


if __name__ == "__main__":
    main()