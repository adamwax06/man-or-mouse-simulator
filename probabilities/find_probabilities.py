#!/usr/bin/env python3
"""
Man or Mouse Exact Win Probability Calculator (Theoretical)

Calculates exact theoretical win probabilities for all possible 2-card hands
against 1-5 other players (plus the peanut). Suits are ignored.
Uses optimized exact enumeration for perfect accuracy.
"""

from itertools import product
from collections import defaultdict
import time
from functools import lru_cache

class Hand:
    """Represents a 2-card hand (suit-agnostic) with ranking capabilities."""
    
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    RANK_VALUES = {rank: i for i, rank in enumerate(RANKS)}
    
    def __init__(self, rank1, rank2):
        # Always store higher rank first for consistency
        values = [self.RANK_VALUES[rank1], self.RANK_VALUES[rank2]]
        values.sort(reverse=True)
        self.high_rank = self.RANKS[values[0]]
        self.low_rank = self.RANKS[values[1]]
        self.high_value = values[0]
        self.low_value = values[1]
    
    def __str__(self):
        return f"{self.high_rank}{self.low_rank}"
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        return self.high_value == other.high_value and self.low_value == other.low_value
    
    def __hash__(self):
        return hash((self.high_value, self.low_value))
    
    def is_pair(self):
        """Check if hand is a pair."""
        return self.high_rank == self.low_rank
    
    def get_rank_tuple(self):
        """Return tuple for hand comparison."""
        if self.is_pair():
            return (1, self.high_value, self.high_value)
        else:
            return (0, self.high_value, self.low_value)
    
    def beats(self, other_hand):
        """Check if this hand beats another hand."""
        return self.get_rank_tuple() > other_hand.get_rank_tuple()
    
    def ties(self, other_hand):
        """Check if this hand ties with another hand."""
        return self.get_rank_tuple() == other_hand.get_rank_tuple()

def generate_all_hands():
    """Generate all possible 2-card hands (suit-agnostic)."""
    hands = []
    ranks = Hand.RANKS
    
    # Generate pairs
    for rank in ranks:
        hands.append(Hand(rank, rank))
    
    # Generate non-pairs (high card first)
    for i in range(len(ranks)):
        for j in range(i + 1, len(ranks)):
            hands.append(Hand(ranks[j], ranks[i]))
    
    return hands

@lru_cache(maxsize=None)
def count_hand_combinations(hand_tuple, cards_used_tuple):
    """
    Cached function to count ways to make a hand given cards already used.
    Uses tuples for hashability.
    """
    # Convert back from tuple
    high_rank, low_rank = hand_tuple
    cards_used = dict(cards_used_tuple)
    
    if high_rank == low_rank:  # Pair
        available = 4 - cards_used.get(high_rank, 0)
        if available < 2:
            return 0
        return available * (available - 1) // 2
    else:  # Non-pair
        available_high = 4 - cards_used.get(high_rank, 0)
        available_low = 4 - cards_used.get(low_rank, 0)
        return available_high * available_low

def cards_used_to_tuple(cards_used_dict):
    """Convert cards_used dict to sorted tuple for hashing."""
    return tuple(sorted(cards_used_dict.items()))

def calculate_exact_probabilities(player_hand, num_opponents):
    """
    Calculate exact theoretical probabilities using dynamic programming.
    """
    all_hands = generate_all_hands()
    
    # Initialize player card usage
    player_usage = defaultdict(int)
    if player_hand.is_pair():
        player_usage[player_hand.high_rank] = 2
    else:
        player_usage[player_hand.high_rank] = 1
        player_usage[player_hand.low_rank] = 1
    
    # Use dynamic programming with memoization
    # State: (opponent_index, cards_used_tuple) -> {wins, ties, losses, total_weight}
    memo = {}
    
    def dp(opponent_idx, cards_used, has_better_opponent, has_tied_opponent):
        """
        Dynamic programming function to calculate outcomes.
        Returns (wins, ties, losses, total_combinations)
        """
        cards_tuple = cards_used_to_tuple(cards_used)
        state = (opponent_idx, cards_tuple, has_better_opponent, has_tied_opponent)
        
        if state in memo:
            return memo[state]
        
        if opponent_idx == num_opponents:
            # Base case: all opponents assigned, determine final outcome
            if has_better_opponent:
                result = (0, 0, 1, 1)  # Player loses
            elif has_tied_opponent:
                result = (0, 1, 0, 1)  # Player ties
            else:
                result = (1, 0, 0, 1)  # Player wins
            memo[state] = result
            return result
        
        total_wins = 0
        total_ties = 0 
        total_losses = 0
        total_combinations = 0
        
        # Try each possible hand for current opponent
        for opp_hand in all_hands:
            hand_tuple = (opp_hand.high_rank, opp_hand.low_rank)
            ways = count_hand_combinations(hand_tuple, cards_tuple)
            
            if ways == 0:
                continue
            
            # Update cards used for this opponent
            new_cards_used = cards_used.copy()
            if opp_hand.is_pair():
                new_cards_used[opp_hand.high_rank] += 2
            else:
                new_cards_used[opp_hand.high_rank] += 1
                new_cards_used[opp_hand.low_rank] += 1
            
            # Determine this opponent's relationship to player
            new_has_better = has_better_opponent or opp_hand.beats(player_hand)
            new_has_tied = has_tied_opponent or opp_hand.ties(player_hand)
            
            # Recursively calculate for remaining opponents
            sub_wins, sub_ties, sub_losses, sub_total = dp(
                opponent_idx + 1, 
                new_cards_used, 
                new_has_better, 
                new_has_tied
            )
            
            total_wins += ways * sub_wins
            total_ties += ways * sub_ties
            total_losses += ways * sub_losses
            total_combinations += ways * sub_total
        
        result = (total_wins, total_ties, total_losses, total_combinations)
        memo[state] = result
        return result
    
    wins, ties, losses, total = dp(0, player_usage, False, False)
    
    if total == 0:
        return {"win": 0.0, "tie": 0.0, "loss": 0.0}
    
    return {
        "win": wins / total,
        "tie": ties / total,
        "loss": losses / total
    }

def calculate_exact_probabilities_iterative(player_hand, num_opponents):
    """
    Alternative iterative approach for very large opponent counts.
    Uses multinomial coefficient calculations.
    """
    all_hands = generate_all_hands()
    
    # Group hands by their relationship to player hand
    better_hands = []
    tied_hands = []
    worse_hands = []
    
    for hand in all_hands:
        if hand.beats(player_hand):
            better_hands.append(hand)
        elif hand.ties(player_hand):
            tied_hands.append(hand)
        else:
            worse_hands.append(hand)
    
    # Calculate card usage by player
    player_usage = defaultdict(int)
    if player_hand.is_pair():
        player_usage[player_hand.high_rank] = 2
    else:
        player_usage[player_hand.high_rank] = 1
        player_usage[player_hand.low_rank] = 1
    
    total_wins = 0
    total_ties = 0
    total_losses = 0
    total_combinations = 0
    
    # For each possible distribution of opponent hands
    max_possible = {}
    for rank in Hand.RANKS:
        max_possible[rank] = 4 - player_usage.get(rank, 0)
    
    # This is still complex for 5 opponents, so we'll use the DP approach
    # but with better optimization
    return calculate_exact_probabilities(player_hand, num_opponents)

def main():
    """Calculate and save exact win/tie/loss probabilities for all hands to probabilities.txt."""
    
    all_hands = generate_all_hands()
    
    # Sort hands by strength (best first)
    all_hands.sort(key=lambda h: h.get_rank_tuple(), reverse=True)
    
    # Open file for writing
    with open('probabilities.txt', 'w') as f:
        f.write("Man or Mouse - Exact Theoretical Win Probabilities\n")
        f.write("=" * 70 + "\n\n")
        
        for num_players in range(2, 7):  # 2-6 total players (including you)
            num_opponents = num_players - 1
            f.write(f"Probabilities for a {num_players} person game:\n")
            f.write("-" * 70 + "\n")
            f.write("Hand     Win%       Tie%       Loss%\n")
            f.write("-" * 70 + "\n")
            
            start_time = time.time()
            print(f"Calculating {num_players} person game probabilities...")
            
            for i, hand in enumerate(all_hands):
                probs = calculate_exact_probabilities(player_hand=hand, num_opponents=num_opponents)
                
                f.write(f"{str(hand):6} {probs['win']:8.3%}   {probs['tie']:8.3%}   {probs['loss']:8.3%}\n")
                
                # Progress indicator for longer calculations
                if num_opponents >= 3 and (i + 1) % 15 == 0:
                    elapsed = time.time() - start_time
                    remaining = len(all_hands) - (i + 1)
                    eta = elapsed * remaining / (i + 1) if i > 0 else 0
                    print(f"  ... {i+1}/{len(all_hands)} hands calculated, ETA: {eta:.1f}s")
            
            elapsed = time.time() - start_time
            f.write(f"\nCompleted in {elapsed:.2f} seconds\n\n")
            print(f"  Completed {num_players} person game in {elapsed:.2f} seconds")
            
            # Clear cache between different game sizes to manage memory
            count_hand_combinations.cache_clear()
        
        f.write("\nCalculation complete! All probabilities are exact theoretical values.\n")
    
    print("\nAll probabilities have been saved to 'probabilities.txt'")

if __name__ == "__main__":
    main()