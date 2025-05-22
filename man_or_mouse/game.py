"""
Main game class for Man or Mouse
"""
from typing import List, Dict, Optional, Any
import random

from man_or_mouse.card import Deck, Hand
from man_or_mouse.player import Player, Peanut, Decision


class ManOrMouseGame:
    """Main game class for Man or Mouse"""
    def __init__(self, players: List[Player], verbose: bool = True):
        """
        Initialize a new game
        
        Args:
            players: List of Player objects
            verbose: Whether to print detailed game info
        """
        if not 2 <= len(players) <= 5:
            raise ValueError(f"Game requires 2-5 players, got {len(players)}")
            
        self.players = players
        self.peanut = Peanut()
        self.pot = 0
        self.deck = Deck()
        self.round_num = 0
        self.dealer_idx = -1  # Start at -1 so first round begins with player 0
        self.verbose = verbose
        self.round_history = []
        
        # Track system-wide chips for validation
        self.initial_chip_total = sum(player.chips for player in players)
        self.buy_ins = 0
    
    def play_round(self) -> Dict[str, Any]:
        """
        Play a single round of the game
        
        Returns:
            Dict containing round results
        """
        self.round_num += 1
        
        # Track round data
        round_data = {
            "round": self.round_num,
            "starting_pot": self.pot,
            "player_states": [],
            "hands": {},
            "decisions": {},
            "winner": None,
            "ending_pot": None,
            "buy_ins": 0
        }
        
        # Store initial player states
        for player in self.players:
            round_data["player_states"].append({
                "name": player.name,
                "chips_before": player.chips
            })
        
        # Print round info
        if self.verbose:
            self._print_separator()
            print(f"Round {self.round_num}")
            print(f"Starting pot: {self.pot} chips")
            self._print_separator()
        
        # Rotate dealer
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)
        
        # Collect antes
        if self.verbose:
            print("Players ante up (1 chip each)")
        
        for player in self.players:
            # Check if player needs to buy in to ante
            if player.chips < 1:
                buy_in_amount = max(10, abs(player.chips) + 1)  # Buy in at least 10 chips or enough to cover negative balance
                player.chips += buy_in_amount
                self.buy_ins += buy_in_amount
                round_data["buy_ins"] += buy_in_amount
                
                if self.verbose:
                    print(f"{player.name} buys in for {buy_in_amount} chips (new balance: {player.chips})")
            
            ante = player.ante(1)
            self.pot += ante
            
        # Deal cards
        self.deck = Deck()  # New shuffled deck
        for player in self.players:
            player.receive_cards(self.deck.deal(2))
            round_data["hands"][player.name] = str(player.hand)
            
            if self.verbose:
                print(f"{player.name} receives: {player.hand}")
        
        self.peanut.receive_cards(self.deck.deal(2))
        round_data["hands"][self.peanut.name] = str(self.peanut.hand)
        
        if self.verbose:
            print(f"{self.peanut.name} receives: [hidden]")
            print(f"Current pot: {self.pot} chips")
            self._print_separator()
            print("Players decide:")
        
        # Player decisions
        start_idx = (self.dealer_idx + 1) % len(self.players)
        for i in range(len(self.players)):
            player_idx = (start_idx + i) % len(self.players)
            player = self.players[player_idx]
            
            # Create game state for decision making
            game_state = {
                "round": self.round_num,
                "pot": self.pot,
                "players": self.players,
                "decisions": {p.name: p.decision for p in self.players if p.decision},
                "player_idx": player_idx,
                "dealer_idx": self.dealer_idx
            }
            
            decision = player.decide(game_state)
            round_data["decisions"][player.name] = decision.name
            
            if self.verbose:
                print(f"{player.name} decides to {decision.name}")
        
        # Determine if showdown happens (at least one player "mans")
        active_players = [p for p in self.players if p.decision == Decision.MAN]
        
        if not active_players:
            # No one mans, pot carries forward
            if self.verbose:
                self._print_separator()
                print("No one mans! Pot carries forward.")
                print(f"Pot: {self.pot} chips")
            
            round_data["winner"] = "No showdown"
            round_data["ending_pot"] = self.pot
            
            # Update player states after round
            for player in self.players:
                for state in round_data["player_states"]:
                    if state["name"] == player.name:
                        state["chips_after"] = player.chips
                        state["chip_change"] = player.chips - state["chips_before"]
                        
            self.round_history.append(round_data)
            return round_data
        
        # Showdown happens
        if self.verbose:
            self._print_separator()
            print("Showdown!")
            print(f"{self.peanut.name} reveals: {self.peanut.hand}")
            for player in active_players:
                print(f"{player.name} reveals: {player.hand}")
        
        # Find the winner (including the Peanut)
        winner = None
        for player in active_players:
            if winner is None:
                winner = player
                continue
                
            comparison = player.hand.compare_to(winner.hand)
            if comparison > 0:  # player's hand is better
                winner = player
        
        # Compare with Peanut
        if winner:
            peanut_comparison = self.peanut.hand.compare_to(winner.hand)
            
            if peanut_comparison > 0:  # Peanut wins
                winner = self.peanut
            elif peanut_comparison == 0:  # Tie with Peanut
                winner = None  # Tie means no winner
        
        # Process outcome
        if winner is None:  # Tie scenario
            if self.verbose:
                self._print_separator()
                print("Tie! No winner, pot remains.")
                print(f"Pot: {self.pot} chips")
            
            round_data["winner"] = "Tie"
            round_data["ending_pot"] = self.pot
            
        elif winner == self.peanut:  # Peanut wins
            if self.verbose:
                self._print_separator()
                print(f"{self.peanut.name} wins!")
                print(f"All players who manned must match the pot ({self.pot} chips).")
            
            round_data["winner"] = self.peanut.name
            
            # All active players match the pot
            total_penalties = 0
            for player in active_players:
                # Check if player needs to buy in to pay penalty
                if player.chips < self.pot:
                    buy_in_amount = max(10, self.pot - player.chips)
                    player.chips += buy_in_amount
                    self.buy_ins += buy_in_amount
                    round_data["buy_ins"] += buy_in_amount
                    
                    if self.verbose:
                        print(f"{player.name} buys in for {buy_in_amount} chips to pay penalty (new balance: {player.chips})")
                
                if self.verbose:
                    print(f"{player.name} matches the pot with {self.pot} chips")
                
                # Record penalty before player pays
                total_penalties += self.pot
                player.match_pot(self.pot)
            
            # Add the matched penalties to the pot
            self.pot += total_penalties
            
            if self.verbose and total_penalties > 0:
                print(f"Pot grows by {total_penalties} chips to {self.pot} (penalties added to pot)")
            
            round_data["ending_pot"] = self.pot
            round_data["penalties_collected"] = total_penalties
            
        else:  # Player wins
            # Store pot value before distributing
            prev_pot = self.pot
            
            if self.verbose:
                self._print_separator()
                print(f"{winner.name} wins {prev_pot} chips!")
                
                # Only print the penalty message if there are other active players
                losers = [p for p in active_players if p != winner]
                if losers:
                    print(f"Players who manned and lost must match the pot value ({prev_pot} chips).")
            
            round_data["winner"] = winner.name
            
            # Winner gets pot
            winner.win_pot(prev_pot)
            self.pot = 0  # Reset pot after distributing
            
            # Other active players match the value of what the pot was (penalties go to the next round's pot)
            losers = [p for p in active_players if p != winner]
            total_penalties = 0
            
            for player in losers:
                # Check if player needs to buy in to pay penalty
                if player.chips < prev_pot:
                    buy_in_amount = max(10, prev_pot - player.chips)
                    player.chips += buy_in_amount
                    self.buy_ins += buy_in_amount
                    round_data["buy_ins"] += buy_in_amount
                    
                    if self.verbose:
                        print(f"{player.name} buys in for {buy_in_amount} chips to pay penalty (new balance: {player.chips})")
                
                if self.verbose:
                    print(f"{player.name} matches the pot with {prev_pot} chips")
                
                # Player pays penalty and it goes back into the pot for next round
                player.match_pot(prev_pot)
                total_penalties += prev_pot
                self.pot += prev_pot  # Penalties go to pot for next round
            
            round_data["ending_pot"] = self.pot
            round_data["pot_distributed"] = prev_pot
            round_data["penalties_collected"] = total_penalties
        
        # Update player states after round
        for player in self.players:
            for state in round_data["player_states"]:
                if state["name"] == player.name:
                    state["chips_after"] = player.chips
                    state["chip_change"] = player.chips - state["chips_before"]
        
        # Print final player states
        if self.verbose:
            self._print_separator()
            print("Player chips after round:")
            for player in self.players:
                print(f"{player.name}: {player.chips} chips")
        
        # Reset player decisions for next round
        for player in self.players:
            player.decision = None
        
        # Add round to history
        self.round_history.append(round_data)
        
        return round_data
    
    def play_game(self, num_rounds: int = 5) -> Dict[str, Any]:
        """
        Play a full game for a set number of rounds
        
        Args:
            num_rounds: Number of rounds to play
            
        Returns:
            Dict containing game results
        """
        for _ in range(num_rounds):
            self.play_round()
            
        return self.get_results()
    
    def get_results(self) -> Dict[str, Any]:
        """
        Get the final game results
        
        Returns:
            Dict containing final game state
        """
        results = {
            "rounds_played": self.round_num,
            "final_pot": self.pot,
            "total_buy_ins": self.buy_ins,
            "players": {}
        }
        
        for player in self.players:
            results["players"][player.name] = {
                "chips": player.chips
            }
        
        # Validate chip conservation
        current_chip_total = sum(player.chips for player in self.players) + self.pot
        expected_total = self.initial_chip_total + self.buy_ins
        
        results["chip_conservation"] = {
            "initial_chips": self.initial_chip_total,
            "final_chips": current_chip_total,
            "buy_ins": self.buy_ins,
            "expected_total": expected_total,
            "is_balanced": current_chip_total == expected_total
        }
        
        if self.verbose and current_chip_total != expected_total:
            print("\nWARNING: Chip conservation error!")
            print(f"Initial total: {self.initial_chip_total}")
            print(f"Final total: {current_chip_total}")
            print(f"Buy-ins: {self.buy_ins}")
            print(f"Expected total: {expected_total}")
            print(f"Discrepancy: {current_chip_total - expected_total}")
        
        return results
    
    def _print_separator(self):
        """Print a separator line for better readability"""
        if self.verbose:
            print("\n" + "-" * 50 + "\n")