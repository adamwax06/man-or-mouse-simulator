"""
Card representations for Man or Mouse game
"""
from enum import Enum, auto
from dataclasses import dataclass
import random
from typing import List


class Suit(Enum):
    """Card suits"""
    CLUBS = auto()
    DIAMONDS = auto()
    HEARTS = auto()
    SPADES = auto()
    
    def __str__(self):
        return self.name.capitalize()[0]


class Rank(Enum):
    """Card ranks from 2 to Ace"""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    
    def __str__(self):
        if self.value <= 10:
            return str(self.value)
        return self.name[0]


@dataclass
class Card:
    """Card representation with rank and suit"""
    rank: Rank
    suit: Suit
    
    def __str__(self):
        return f"{self.rank}{self.suit}"
    
    def __lt__(self, other):
        return self.rank.value < other.rank.value


class Deck:
    """Standard deck of 52 playing cards"""
    def __init__(self):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        self.shuffle()
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def deal(self, n=1) -> List[Card]:
        """Deal n cards from the deck"""
        if n > len(self.cards):
            raise ValueError(f"Cannot deal {n} cards, only {len(self.cards)} left")
        return [self.cards.pop() for _ in range(n)]


class HandRank(Enum):
    """Hand ranking enum"""
    HIGH_CARD = auto()
    PAIR = auto()


class Hand:
    """Poker hand evaluation for Man or Mouse"""
    def __init__(self, cards: List[Card]):
        if len(cards) != 2:
            raise ValueError(f"Hand must have exactly 2 cards, got {len(cards)}")
        self.cards = sorted(cards, reverse=True)  # Sort cards by rank, highest first
    
    @property
    def rank_type(self) -> HandRank:
        """Determine hand type: pair or high card"""
        if self.cards[0].rank == self.cards[1].rank:
            return HandRank.PAIR
        return HandRank.HIGH_CARD
    
    def compare_to(self, other) -> int:
        """
        Compare this hand to another
        Returns: 1 if this hand wins, -1 if other hand wins, 0 if tie
        """
        # Pairs beat non-pairs
        if self.rank_type == HandRank.PAIR and other.rank_type == HandRank.HIGH_CARD:
            return 1
        if self.rank_type == HandRank.HIGH_CARD and other.rank_type == HandRank.PAIR:
            return -1
            
        # If both are pairs, higher pair wins
        if self.rank_type == HandRank.PAIR and other.rank_type == HandRank.PAIR:
            return self._compare_ranks(other)
            
        # If both are high cards, compare highest card
        return self._compare_ranks(other)
    
    def _compare_ranks(self, other) -> int:
        """Compare card ranks between hands"""
        for i in range(len(self.cards)):
            if self.cards[i].rank.value > other.cards[i].rank.value:
                return 1
            if self.cards[i].rank.value < other.cards[i].rank.value:
                return -1
        return 0  # Tie
    
    def __str__(self):
        return f"{self.cards[0]} {self.cards[1]}"