"""
Random Agent Baseline - Integrated with existing game structure
Simple random agent for experimental comparison with intelligent agents
"""

import random
from typing import List
import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Import base classes (simplified versions)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Action import Action

class SimpleAction:
    """Simplified Action representation for random agent"""
    MOVE_FORWARD = Action.MOVE_FORWARD
    TURN_LEFT = Action.TURN_LEFT
    TURN_RIGHT = Action.TURN_RIGHT
    GRAB_GOLD = Action.GRAB_GOLD
    SHOOT = Action.SHOOT
    CLIMB_OUT_OF_THE_CAVE = Action.CLIMB_OUT_OF_THE_CAVE


class RandomAgentBaseline:
    """
    Random Agent Baseline for comparison in experiments.
    
    Makes completely random decisions without any knowledge base,
    planning, or intelligent reasoning. Used as performance baseline.
    """
    
    def __init__(self, input_file, output_file):
        self.input_filename = input_file
        self.output_filename = output_file
        self.action_list = []
        
        # Performance tracking for experiments
        self.performance_metrics = {
            'total_moves': 0,
            'gold_collected': 0,
            'wumpus_killed': 0,
            'died': False,
            'reached_exit': False,
            'final_score': 0
        }
        
        # Simple game state
        self.arrow_used = False
        self.current_position = (0, 0)
        self.facing_direction = 0  # 0=UP, 1=RIGHT, 2=DOWN, 3=LEFT
        self.game_ended = False
        self.max_moves = 200  # Prevent infinite loops
        
        # Read map size (simplified)
        self.map_size = self._read_map_size()
    
    def _read_map_size(self):
        """Read map size from input file"""
        try:
            with open(self.input_filename, 'r') as f:
                first_line = f.readline().strip()
                return int(first_line)
        except:
            return 8  # Default size
    
    def add_action(self, action):
        """Add action to action list"""
        self.action_list.append(action)
        
    def append_event_to_output_file(self, event):
        """Log event to output file"""
        try:
            with open(self.output_filename, 'a') as f:
                f.write(event + "\n")
        except:
            pass
    
    def calculate_score(self) -> int:
        """Calculate current score"""
        score = 0
        score += self.performance_metrics['gold_collected'] * 1000
        score += self.performance_metrics['wumpus_killed'] * 500
        score -= self.performance_metrics['total_moves']
        score += 10 if self.performance_metrics['reached_exit'] else 0
        score -= 1000 if self.performance_metrics['died'] else 0
        return score
    
    def make_random_move(self):
        """Make a completely random move"""
        possible_actions = [
            SimpleAction.MOVE_FORWARD,
            SimpleAction.TURN_LEFT,
            SimpleAction.TURN_RIGHT,
            SimpleAction.GRAB_GOLD,
        ]
        
        # Add shooting if arrow available
        if not self.arrow_used:
            possible_actions.append(SimpleAction.SHOOT)
        
        # Add exit if at (0,0)
        if self.current_position == (0, 0):
            possible_actions.append(SimpleAction.CLIMB_OUT_OF_THE_CAVE)
        
        # Choose random action
        action = random.choice(possible_actions)
        self.add_action(action)
        self.performance_metrics['total_moves'] += 1
        
        # Process action
        if action == SimpleAction.MOVE_FORWARD:
            self._move_forward()
        elif action == SimpleAction.TURN_LEFT:
            self.facing_direction = (self.facing_direction - 1) % 4
        elif action == SimpleAction.TURN_RIGHT:
            self.facing_direction = (self.facing_direction + 1) % 4
        elif action == SimpleAction.GRAB_GOLD:
            if random.random() < 0.3:  # 30% chance to find gold
                self.performance_metrics['gold_collected'] += 1
                self.append_event_to_output_file(f"Random: Found gold! Total: {self.performance_metrics['gold_collected']}")
        elif action == SimpleAction.SHOOT:
            self.arrow_used = True
            if random.random() < 0.2:  # 20% chance to kill wumpus
                self.performance_metrics['wumpus_killed'] += 1
                self.append_event_to_output_file("Random: Killed Wumpus!")
        elif action == SimpleAction.CLIMB_OUT_OF_THE_CAVE:
            self.performance_metrics['reached_exit'] = True
            self.game_ended = True
            self.append_event_to_output_file("Random: Exited cave!")
        
        # Random death chance (simplified danger simulation)
        if random.random() < 0.02:  # 2% chance to die each move
            self.performance_metrics['died'] = True
            self.game_ended = True
            self.append_event_to_output_file("Random: Died!")
        
        return action
    
    def _move_forward(self):
        """Move forward in facing direction"""
        x, y = self.current_position
        
        if self.facing_direction == 0:  # UP
            new_y = max(0, y - 1)
            self.current_position = (x, new_y)
        elif self.facing_direction == 1:  # RIGHT
            new_x = min(self.map_size - 1, x + 1)
            self.current_position = (new_x, y)
        elif self.facing_direction == 2:  # DOWN
            new_y = min(self.map_size - 1, y + 1)
            self.current_position = (x, new_y)
        elif self.facing_direction == 3:  # LEFT
            new_x = max(0, x - 1)
            self.current_position = (new_x, y)
        
        self.append_event_to_output_file(f"Random: Moved to {self.current_position}")
    
    def solve(self) -> List:
        """
        Solve using completely random strategy.
        This is the main method called by the game framework.
        """
        # Reset output file
        try:
            with open(self.output_filename, 'w') as f:
                f.write("=== RANDOM AGENT BASELINE ===\n")
                f.write("Making completely random decisions for baseline comparison\n\n")
        except:
            pass
        
        self.append_event_to_output_file("Random Agent started")
        
        # Make random moves until game ends
        while not self.game_ended and self.performance_metrics['total_moves'] < self.max_moves:
            action = self.make_random_move()
            
            # Random chance to exit early (simulate getting "lucky")
            if self.performance_metrics['total_moves'] > 50 and random.random() < 0.1:
                if self.current_position == (0, 0) or random.random() < 0.3:
                    self.add_action(SimpleAction.CLIMB_OUT_OF_THE_CAVE)
                    self.performance_metrics['reached_exit'] = True
                    self.game_ended = True
                    break
        
        # Force end if max moves reached
        if self.performance_metrics['total_moves'] >= self.max_moves:
            self.game_ended = True
            self.append_event_to_output_file("Random: Max moves reached")
        
        # Calculate final score
        self.performance_metrics['final_score'] = self.calculate_score()
        
        # Log final performance
        self.append_event_to_output_file("\n=== RANDOM AGENT PERFORMANCE ===")
        self.append_event_to_output_file(f"Total Moves: {self.performance_metrics['total_moves']}")
        self.append_event_to_output_file(f"Gold Collected: {self.performance_metrics['gold_collected']}")
        self.append_event_to_output_file(f"Wumpus Killed: {self.performance_metrics['wumpus_killed']}")
        self.append_event_to_output_file(f"Died: {self.performance_metrics['died']}")
        self.append_event_to_output_file(f"Reached Exit: {self.performance_metrics['reached_exit']}")
        self.append_event_to_output_file(f"Final Score: {self.performance_metrics['final_score']}")
        
        return self.action_list
    
    def get_performance_metrics(self) -> dict:
        """Get performance metrics for experimental comparison"""
        return self.performance_metrics.copy()


# Alias for compatibility with existing naming
RandomAgent = RandomAgentBaseline
