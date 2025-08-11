"""
Console output utilities for Wumpus World
Provides detailed logging and visualization in console
"""

import time
from constants import *


class ConsoleVisualizer:
    def __init__(self):
        self.step_count = 0
        
    def print_game_state(self, board, action_name=None):
        """Print current game state to console"""
        self.step_count += 1
        
        print("\n" + "="*60)
        print(f"STEP {self.step_count}: {action_name if action_name else 'INIT'}")
        print("="*60)
        
        # Agent status
        agent = board.Agent
        print(f"Agent Position: ({agent.row}, {agent.col})")
        print(f"Agent Direction: {agent.direction}")
        print(f"Has Gold: {'Yes' if agent.has_gold else 'No'}")
        print(f"Score: {board.score}")
        
        # Current percepts
        percepts = self._get_current_percepts(board)
        print(f"Current Percepts: {', '.join(percepts) if percepts else 'None'}")
        
        # World state
        print(f"\nWorld State:")
        print(f"- Wumpus remaining: {len([w for w in board.Wumpus])}")
        print(f"- Pits: {len(board.Pits)}")
        print(f"- Gold remaining: {len(board.Golds)}")
        
        # ASCII map representation
        print(f"\nMap Visualization:")
        self._print_ascii_map(board)
        
        print("\nLegend:")
        print("A=Agent, W=Wumpus, P=Pit, G=Gold, S=Stench, B=Breeze, -=Empty")
        print("-"*60)
        
    def _get_current_percepts(self, board):
        """Get current percepts at agent position"""
        percepts = []
        agent_pos = (board.Agent.row, board.Agent.col)
        
        # Check for stench
        for stench in board.Stenches:
            if (stench.row, stench.col) == agent_pos:
                percepts.append("STENCH")
                break
                
        # Check for breeze
        for breeze in board.Breezes:
            if (breeze.row, breeze.col) == agent_pos:
                percepts.append("BREEZE")
                break
                
        # Check for gold
        for gold in board.Golds:
            if (gold.row, gold.col) == agent_pos:
                percepts.append("GLITTER")
                break
                
        return percepts
        
    def _print_ascii_map(self, board):
        """Print ASCII representation of the map"""
        N = board.matrix_dimension[0]
        
        # Create grid representation
        grid = [['.' for _ in range(N)] for _ in range(N)]
        
        # Mark agent
        grid[board.Agent.row][board.Agent.col] = 'A'
        
        # Mark wumpus
        for wumpus in board.Wumpus:
            if grid[wumpus.row][wumpus.col] == '.':
                grid[wumpus.row][wumpus.col] = 'W'
            else:
                grid[wumpus.row][wumpus.col] += 'W'
                
        # Mark pits
        for pit in board.Pits:
            if grid[pit.row][pit.col] == '.':
                grid[pit.row][pit.col] = 'P'
            else:
                grid[pit.row][pit.col] += 'P'
                
        # Mark gold
        for gold in board.Golds:
            if grid[gold.row][gold.col] == '.':
                grid[gold.row][gold.col] = 'G'
            else:
                grid[gold.row][gold.col] += 'G'
                
        # Mark stenches
        for stench in board.Stenches:
            if grid[stench.row][stench.col] == '.':
                grid[stench.row][stench.col] = 'S'
            elif 'S' not in grid[stench.row][stench.col]:
                grid[stench.row][stench.col] += 'S'
                
        # Mark breezes
        for breeze in board.Breezes:
            if grid[breeze.row][breeze.col] == '.':
                grid[breeze.row][breeze.col] = 'B'
            elif 'B' not in grid[breeze.row][breeze.col]:
                grid[breeze.row][breeze.col] += 'B'
        
        # Print grid with coordinates
        print("   ", end="")
        for col in range(N):
            print(f"{col:2}", end=" ")
        print()
        
        for row in range(N):
            print(f"{row:2} ", end="")
            for col in range(N):
                cell_content = grid[row][col]
                if len(cell_content) > 3:
                    cell_content = cell_content[:3]  # Truncate if too long
                print(f"{cell_content:3}", end="")
            print()
            
    def print_action_details(self, action_name, reasoning=""):
        """Print action details"""
        print(f"\nAction: {action_name}")
        if reasoning:
            print(f"Reasoning: {reasoning}")


# Global console visualizer instance
console_viz = ConsoleVisualizer()
