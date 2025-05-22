"""
Player and strategy classes for Man or Mouse game
"""
from enum import Enum, auto
from typing import Dict, List, Optional, Any
import random
import os

from man_or_mouse.card import Hand, Card


class Decision(Enum):
    """Player decision: Man or Mouse"""
    MAN = auto()
    MOUSE = auto()


class Strategy:
    """Base strategy class for player decision making"""
    def make_decision(self, hand: Hand, game_state: Dict[str, Any]) -> Decision:
        """
        Make a decision based on hand and game state
        
        Args:
            hand: The player's hand
            game_state: Current game state (pot, players, etc.)
            
        Returns:
            Decision: MAN or MOUSE
        """
        raise NotImplementedError("Strategy must implement make_decision method")


class RandomStrategy(Strategy):
    """Randomly decides to man or mouse with configurable probability"""
    def __init__(self, man_probability: float = 0.5):
        self.man_probability = man_probability
    
    def make_decision(self, hand: Hand, game_state: Dict[str, Any]) -> Decision:
        if random.random() < self.man_probability:
            return Decision.MAN
        return Decision.MOUSE


class SimpleStrategy(Strategy):
    """
    Simple strategy based on hand strength
    - Always mans with any pair
    - Mans with high cards A-K
    - Mouse with everything else
    """
    def make_decision(self, hand: Hand, game_state: Dict[str, Any]) -> Decision:
        # Man with any pair
        if hand.rank_type.name == "PAIR":
            return Decision.MAN
            
        # Man with high cards A-K
        high_card = hand.cards[0].rank.value
        if high_card >= 13:  # King or better
            return Decision.MAN
            
        # Mouse with everything else
        return Decision.MOUSE


class MaxEVStrategy(Strategy):
    """
    Maximum Expected Value strategy using theoretical probabilities
    
    E[X] = P * (w - l) where:
    - P = pot size
    - w = probability of winning
    - l = probability of losing
    
    Strategy: Man if P(win) > P(loss), otherwise Mouse
    """
    
    def __init__(self, probabilities_file: str = "probabilities/probabilities.txt"):
        """
        Initialize MaxEV strategy with probability data
        
        Args:
            probabilities_file: Path to file containing theoretical probabilities
        """
        self.probabilities = self._load_probabilities(probabilities_file)
    
    def _load_probabilities(self, filepath: str) -> Dict[int, Dict[str, Dict[str, float]]]:
        """
        Load theoretical probabilities from probabilities.txt file
        
        Returns:
            Dict structure: {num_players: {hand_str: {win: float, tie: float, loss: float}}}
        """
        probabilities = {}
        
        if not os.path.exists(filepath):
            print(f"Warning: Probabilities file {filepath} not found. Using fallback strategy.")
            return {}
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            lines = content.split('\n')
            current_players = None
            
            for line in lines:
                line = line.strip()
                
                # Check for game size header
                if "Probabilities for a" in line and "person game:" in line:
                    # Extract number of players
                    words = line.split()
                    for i, word in enumerate(words):
                        if word.isdigit():
                            current_players = int(word)
                            probabilities[current_players] = {}
                            break
                    continue
                
                # Parse probability data lines
                if current_players and line and not line.startswith('Hand') and not line.startswith('---') and not line.startswith('Completed'):
                    parts = line.split()
                    if len(parts) >= 4:
                        try:
                            hand_str = parts[0]
                            win_pct = float(parts[1].rstrip('%'))
                            tie_pct = float(parts[2].rstrip('%'))
                            loss_pct = float(parts[3].rstrip('%'))
                            
                            probabilities[current_players][hand_str] = {
                                'win': win_pct / 100.0,  # Convert percentage to decimal
                                'tie': tie_pct / 100.0,
                                'loss': loss_pct / 100.0
                            }
                        except (ValueError, IndexError):
                            continue
            
            print(f"MaxEV Strategy: Loaded probabilities for {len(probabilities)} game sizes")
            for players, hands in probabilities.items():
                print(f"  {players} players: {len(hands)} hands")
            
            return probabilities
            
        except Exception as e:
            print(f"Error loading probabilities: {e}")
            return {}
    
    def _hand_to_string(self, hand: Hand) -> str:
        """
        Convert a Hand object to the string format used in probabilities file
        
        Args:
            hand: Hand object
            
        Returns:
            String representation (e.g., "AA", "AK", "72")
        """
        # Sort cards by rank value (highest first)
        sorted_cards = sorted(hand.cards, key=lambda c: c.rank.value, reverse=True)
        
        # Convert to string format
        if len(sorted_cards) != 2:
            raise ValueError("Hand must have exactly 2 cards")
        
        card1, card2 = sorted_cards
        
        # Handle rank names and convert to probability file format
        rank1 = self._rank_to_string(card1.rank)
        rank2 = self._rank_to_string(card2.rank)
        
        return f"{rank1}{rank2}"
    
    def _rank_to_string(self, rank) -> str:
        """Convert rank enum to string used in probabilities file"""
        if rank.name == "TEN":
            return "10"
        elif rank.name == "JACK":
            return "J"
        elif rank.name == "QUEEN":
            return "Q"
        elif rank.name == "KING":
            return "K"
        elif rank.name == "ACE":
            return "A"
        else:
            return str(rank.value)
    
    def make_decision(self, hand: Hand, game_state: Dict[str, Any]) -> Decision:
        """
        Make decision based on expected value calculation
        
        Args:
            hand: Player's hand
            game_state: Current game state including number of players
            
        Returns:
            Decision: MAN if E[X] > 0, MOUSE otherwise
        """
        # Get number of players from game state (including the player making the decision)
        # Add 1 because game_state['players'] doesn't include the peanut
        num_players = len(game_state.get('players', [])) + 1  # +1 for the peanut
        
        # Fallback to SimpleStrategy if no probability data
        if not self.probabilities or num_players not in self.probabilities:
            # print(f"Warning: No probability data for {num_players} players, using simple fallback")
            return self._fallback_strategy(hand)
        
        # Convert hand to string format
        try:
            hand_str = self._hand_to_string(hand)
        except Exception as e:
            print(f"Error converting hand to string: {e}")
            return self._fallback_strategy(hand)
        
        # Look up probabilities
        if hand_str not in self.probabilities[num_players]:
            print(f"Warning: No data for hand {hand_str} with {num_players} players")
            return self._fallback_strategy(hand)
        
        probs = self.probabilities[num_players][hand_str]
        win_prob = probs['win']
        loss_prob = probs['loss']
        
        # Expected value calculation: E[X] = P * (w - l)
        # Since we're only comparing to 0, we can ignore pot size P
        # Decision: Man if w > l (positive expected value)
        if win_prob > loss_prob:
            return Decision.MAN
        else:
            return Decision.MOUSE
    
    def _fallback_strategy(self, hand: Hand) -> Decision:
        """
        Fallback strategy when probability data is unavailable
        Uses simple heuristics
        """
        # Man with any pair
        if hand.rank_type.name == "PAIR":
            return Decision.MAN
            
        # Man with high cards A-K
        high_card = hand.cards[0].rank.value
        if high_card >= 13:  # King or better
            return Decision.MAN
            
        # Mouse with everything else
        return Decision.MOUSE


class Player:
    """Player class for Man or Mouse game"""
    def __init__(self, name: str, strategy: Strategy, initial_chips: int = 100):
        self.name = name
        self.strategy = strategy
        self.chips = initial_chips
        self.hand = None
        self.decision = None
    
    def receive_cards(self, cards: List[Card]):
        """Receive dealt cards"""
        self.hand = Hand(cards)
    
    def decide(self, game_state: Dict) -> Decision:
        """Make a decision based on strategy"""
        self.decision = self.strategy.make_decision(self.hand, game_state)
        return self.decision
    
    def win_pot(self, amount: int):
        """Player wins the pot"""
        self.chips += amount
    
    def match_pot(self, amount: int):
        """
        Player must match the pot
        This payment goes into the next round's pot (not to any other player)
        """
        self.chips -= amount
        # Note: The pot itself is managed in the game class, not here
    
    def ante(self, amount: int = 1) -> int:
        """Pay ante to join the round"""
        self.chips -= amount
        return amount
    
    def __str__(self):
        return f"{self.name} ({self.chips} chips)"


class Peanut:
    """The Peanut non-player entity"""
    def __init__(self):
        self.hand = None
        self.name = "The Peanut"
    
    def receive_cards(self, cards: List[Card]):
        """Receive dealt cards"""
        self.hand = Hand(cards)
    
    def __str__(self):
        return self.name