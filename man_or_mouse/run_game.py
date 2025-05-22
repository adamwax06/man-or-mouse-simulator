"""
Sample script to run a Man or Mouse game
"""
import random
import time
import argparse
from typing import List, Dict

from man_or_mouse.player import Player, RandomStrategy, SimpleStrategy, MaxEVStrategy
from man_or_mouse.game import ManOrMouseGame


def main():
    """Run a simple Man or Mouse game demo"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run a Man or Mouse game simulation")
    parser.add_argument("--seed", type=int, help="Random seed for reproducibility")
    parser.add_argument("--rounds", type=int, default=5, help="Number of rounds to play")
    parser.add_argument("--players", type=int, default=4, help="Number of players")
    parser.add_argument("--chips", type=int, default=100, help="Initial chips per player")
    parser.add_argument("--strategy", type=str, default="mixed", 
                       choices=["simple", "random", "maxev", "mixed"],
                       help="Strategy type: simple, random, maxev, or mixed")
    args = parser.parse_args()
    
    # Set random seed or use current time for true randomness
    seed = args.seed if args.seed is not None else int(time.time())
    random.seed(seed)
    
    print(f"Game initialized with random seed: {seed}")
    
    # Create players with different strategies
    player_names = ["Alice", "Bob", "Charlie", "Dave", "Eve", "Frank"]
    
    # Define strategy configurations
    if args.strategy == "simple":
        strategies_info = [
            ("SimpleStrategy", SimpleStrategy()),
            ("SimpleStrategy", SimpleStrategy()),
            ("SimpleStrategy", SimpleStrategy()),
            ("SimpleStrategy", SimpleStrategy())
        ]
    elif args.strategy == "random":
        strategies_info = [
            ("RandomStrategy(0.5)", RandomStrategy(man_probability=0.5)),
            ("RandomStrategy(0.5)", RandomStrategy(man_probability=0.5)),
            ("RandomStrategy(0.5)", RandomStrategy(man_probability=0.5)),
            ("RandomStrategy(0.5)", RandomStrategy(man_probability=0.5))
        ]
    elif args.strategy == "maxev":
        strategies_info = [
            ("MaxEVStrategy", MaxEVStrategy()),
            ("MaxEVStrategy", MaxEVStrategy()),
            ("MaxEVStrategy", MaxEVStrategy()),
            ("MaxEVStrategy", MaxEVStrategy())
        ]
    else:  # mixed
        strategies_info = [
            ("MaxEVStrategy", MaxEVStrategy()),
            ("SimpleStrategy", SimpleStrategy()),
            ("RandomStrategy(0.7)", RandomStrategy(man_probability=0.7)),
            ("RandomStrategy(0.3)", RandomStrategy(man_probability=0.3))
        ]
    
    # Ensure we don't try to create more players than we have names for
    num_players = min(args.players, len(player_names))
    
    players = [
        Player(f"{player_names[i]} ({strategies_info[i % len(strategies_info)][0]})", 
               strategies_info[i % len(strategies_info)][1], 
               initial_chips=args.chips)
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
    
    print("\nPlayer chips and net winnings:")
    
    # Calculate net winnings for each player
    player_results = []
    for name, data in results['players'].items():
        final_chips = data['chips']
        buy_ins = data.get('total_buy_ins', 0)  # Individual buy-ins per player
        net_winnings = final_chips - args.chips - buy_ins  # final - initial - buy_ins
        
        player_results.append({
            'name': name,
            'final_chips': final_chips,
            'buy_ins': buy_ins,
            'net_winnings': net_winnings
        })
    
    # Sort by net winnings (highest first)
    player_results.sort(key=lambda x: x['net_winnings'], reverse=True)
    
    # Find the winner
    winner = player_results[0]
    
    for result in player_results:
        name = result['name']
        final_chips = result['final_chips']
        buy_ins = result['buy_ins']
        net_winnings = result['net_winnings']
        
        # Extract strategy from player name if it contains strategy info
        if "(" in name and ")" in name:
            player_name = name.split("(")[0].strip()
            strategy = name.split("(")[1].split(")")[0]
            
            if buy_ins > 0:
                print(f"{player_name}: {final_chips} chips (bought in {buy_ins}) = {net_winnings:+d} net (Strategy: {strategy})")
            else:
                print(f"{player_name}: {final_chips} chips = {net_winnings:+d} net (Strategy: {strategy})")
        else:
            if buy_ins > 0:
                print(f"{name}: {final_chips} chips (bought in {buy_ins}) = {net_winnings:+d} net")
            else:
                print(f"{name}: {final_chips} chips = {net_winnings:+d} net")
    
    # Announce the winner
    winner_name = winner['name']
    if "(" in winner_name and ")" in winner_name:
        winner_display = winner_name.split("(")[0].strip()
    else:
        winner_display = winner_name
        
    print(f"\n🏆 Winner: {winner_display} with {winner['net_winnings']:+d} net chips!")
    
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