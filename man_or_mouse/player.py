"""
Player and strategy classes for Man or Mouse game
"""
from enum import Enum, auto
from typing import Dict, List, Optional, Any
import random

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