"""
Hybrid Agent - Unified integration of all modules for maximum score
Integrates: Logic Inference + Planning + Score Optimization
"""

from typing import List, Tuple, Optional, Set
from Run.Action import Action
from Run.Solution import Solution
from Run.PathPlanner import PathPlanner
from Run.KnowledgeBase import KnowledgeBase
from Run.Cell import Cell
from Run.CellType import CellType


class HybridAgent(Solution):
    """
    Unified agent that integrates all modules for maximum score achievement:
    - Logic Inference (KB-based reasoning)
    - Path Planning (A* with risk-utility)
    - Score Optimization (strategic decision making)
    """
    
    def __init__(self, input_file, output_file):
        super().__init__(input_file, output_file)
        
        # Enhanced state tracking for score optimization
        self.collected_gold = 0
        self.killed_wumpus = 0
        self.total_moves = 0
        self.arrow_used = False
        self.exploration_efficiency = 0.0
        self.has_gold = False  # Track if agent has collected gold
        
        # Strategic objectives priority
        self.objectives = {
            'collect_all_gold': False,
            'kill_all_wumpus': False,
            'minimize_moves': True,
            'safe_exit': True
        }
        
        # Performance metrics
        self.score_components = {
            'gold_bonus': 0,      # +1000 per gold
            'wumpus_bonus': 0,    # +500 per wumpus killed  
            'move_penalty': 0,    # -1 per move
            'death_penalty': 0,   # -1000 if died
            'exit_bonus': 0       # +10 for successful exit
        }
    
    def calculate_current_score(self) -> int:
        """Calculate current estimated score"""
        total_score = 0
        total_score += self.collected_gold * 1000  # Gold bonus
        total_score += self.killed_wumpus * 500   # Wumpus kill bonus
        total_score -= self.total_moves           # Move penalty
        total_score += 10 if self.at_exit() else 0  # Exit bonus
        
        # Additional 1000 point bonus for climbing out with gold
        if self.at_exit() and self.has_gold:
            total_score += 1000  # Extra gold collection completion bonus
            
        return total_score
    
    def at_exit(self) -> bool:
        """Check if agent is at exit position (N-1,0)"""
        from constants import EXIT_DOOR_ROW, EXIT_DOOR_COL
        return self.agent_cell.map_pos == (EXIT_DOOR_ROW, EXIT_DOOR_COL)
    
    def estimate_max_possible_score(self) -> int:
        """Estimate maximum achievable score from current state"""
        # Count remaining gold and wumpus
        remaining_gold = 0
        remaining_wumpus = 0
        
        for row in self.cell_matrix:
            for cell in row:
                if not cell.is_explored():
                    # Estimate based on probability
                    continue
                if cell.exist_Entity(0):  # Gold
                    remaining_gold += 1
                if cell.exist_Entity(2):  # Wumpus
                    remaining_wumpus += 1
        
        # Calculate potential score
        potential_gold_bonus = remaining_gold * 1000
        potential_wumpus_bonus = remaining_wumpus * 500 if not self.arrow_used else 0
        
        # Estimate moves needed (Manhattan distance + exploration)
        estimated_moves = self.estimate_moves_to_complete()
        move_penalty = estimated_moves
        
        current_score = self.calculate_current_score()
        max_possible = current_score + potential_gold_bonus + potential_wumpus_bonus - move_penalty + 10
        
        return max_possible
    
    def estimate_moves_to_complete(self) -> int:
        """Estimate minimum moves needed to complete all objectives"""
        # This is a simplified estimation
        unexplored_cells = sum(1 for row in self.cell_matrix 
                             for cell in row if not cell.is_explored())
        
        # Estimate based on current position and remaining objectives
        moves_to_explore = unexplored_cells // 2  # Optimistic exploration
        moves_to_exit = abs(self.agent_cell.map_pos[0]) + abs(self.agent_cell.map_pos[1])
        
        return moves_to_explore + moves_to_exit
    
    def should_prioritize_gold(self) -> bool:
        """Decide if agent should prioritize gold collection over safety"""
        max_score = self.estimate_max_possible_score()
        current_score = self.calculate_current_score()
        
        # If potential score gain is high, take more risks
        potential_gain = max_score - current_score
        return potential_gain > 500  # Threshold for risk-taking
    
    def should_hunt_wumpus(self) -> bool:
        """Decide if agent should actively hunt wumpus"""
        if self.arrow_used:
            return False
        
        # Hunt wumpus if we can gain significant score
        potential_wumpus_bonus = 500
        estimated_risk = 200  # Risk of dying while hunting
        
        return potential_wumpus_bonus > estimated_risk
    
    def optimize_exploration_strategy(self) -> Optional[Tuple[int, int]]:
        """Choose next exploration target to maximize score efficiency"""
        current_pos = self.agent_cell.map_pos
        explored_positions = set()
        
        for row in self.cell_matrix:
            for cell in row:
                if cell.is_explored():
                    explored_positions.add(cell.map_pos)
        
        # Get candidates from path planner
        candidates = []
        for neighbor_pos in self.planner.get_valid_neighbors(current_pos):
            if neighbor_pos not in explored_positions:
                neighbor_cell = self.cell_matrix[neighbor_pos[0]][neighbor_pos[1]]
                
                # Calculate score-optimized utility
                risk = self.planner.calculate_risk(neighbor_cell)
                base_utility = self.planner.calculate_utility(neighbor_cell)
                
                # Add score-specific bonuses
                score_utility = base_utility
                
                # Bonus for potential gold discovery
                if self.should_prioritize_gold():
                    score_utility += 200  # Higher gold-seeking behavior
                
                # Bonus for wumpus hunting if beneficial
                if self.should_hunt_wumpus() and risk < 600:  # Moderate wumpus risk
                    score_utility += 100
                
                # Penalty for moves (efficiency focus)
                move_penalty = 10
                score_utility -= move_penalty
                
                if risk != float('inf'):
                    efficiency_score = score_utility / (1 + risk * 0.01)
                    candidates.append((neighbor_pos, efficiency_score, risk, score_utility))
        
        if candidates:
            # Sort by score efficiency
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None
    
    def hybrid_backtracking_search(self):
        """Enhanced backtracking with score optimization"""
        # Use parent's logic but with score-optimized decisions
        if self.game_ended:
            return False
            
        self.top_condition()
        self.total_moves += 1  # Track moves for score calculation

        # Check if reached exit
        if self.agent_cell.map_pos[0] == 0 and self.agent_cell.map_pos[1] == 0:
            self.add_action(Action.CLIMB_OUT_OF_THE_CAVE)
            self.game_ended = True
            return False

        # Get valid adjacent cells
        valid_adj_cell_list = self.agent_cell.get_adj_cell(self.cell_matrix)
        temp_adj_cell_list = []

        # Remove parent cell
        if self.agent_cell.parent in valid_adj_cell_list:
            valid_adj_cell_list.remove(self.agent_cell.parent)

        pre_agent_cell = self.agent_cell

        # Enhanced logic inference with score consideration
        if not self.agent_cell.check():
            # Remove confirmed dangerous cells
            for valid_adj_cell in valid_adj_cell_list:
                if valid_adj_cell.is_explored() and valid_adj_cell.exist_Entity(1):
                    temp_adj_cell_list.append(valid_adj_cell)

            for adj_cell in temp_adj_cell_list:
                valid_adj_cell_list.remove(adj_cell)

            temp_adj_cell_list = []

            # Handle stench with score-optimized wumpus hunting
            if self.agent_cell.exist_Entity(4):
                for valid_adj_cell in valid_adj_cell_list:
                    self.append_event_to_output_file('Infer: ' + str(valid_adj_cell.map_pos))
                    self.turn_to(valid_adj_cell)

                    # Infer Wumpus
                    self.add_action(Action.INFER_WUMPUS)
                    not_alpha = [[valid_adj_cell.get_literal(CellType.WUMPUS, '-')]]
                    have_wumpus = self.KB.infer(not_alpha)

                    if have_wumpus:
                        # Score-based decision: shoot only if beneficial
                        if self.should_hunt_wumpus():
                            self.add_action(Action.DETECT_WUMPUS)
                            self.add_action(Action.SHOOT)
                            self.arrow_used = True
                            
                            if valid_adj_cell.exist_Entity(2):  # Successful kill
                                self.killed_wumpus += 1
                                
                            valid_adj_cell.kill_wumpus(self.cell_matrix, self.KB)
                            self.append_event_to_output_file('KB: ' + str(self.KB.KB))
                        else:
                            # Don't shoot, avoid cell
                            temp_adj_cell_list.append(valid_adj_cell)
                    else:
                        # Standard inference logic
                        self.add_action(Action.INFER_NOT_WUMPUS)
                        not_alpha = [[valid_adj_cell.get_literal(CellType.WUMPUS, '+')]]
                        have_no_wumpus = self.KB.infer(not_alpha)

                        if have_no_wumpus:
                            self.add_action(Action.DETECT_NO_WUMPUS)
                        else:
                            if valid_adj_cell not in temp_adj_cell_list:
                                temp_adj_cell_list.append(valid_adj_cell)

            # Handle breeze with enhanced pit inference
            if self.agent_cell.exist_Entity(3):
                for valid_adj_cell in valid_adj_cell_list:
                    if valid_adj_cell not in temp_adj_cell_list:
                        self.append_event_to_output_file('Infer: ' + str(valid_adj_cell.map_pos))
                        self.turn_to(valid_adj_cell)

                        # Infer Pit
                        self.add_action(Action.INFER_PIT)
                        not_alpha = [[valid_adj_cell.get_literal(CellType.PIT, '-')]]
                        have_pit = self.KB.infer(not_alpha)

                        if have_pit:
                            self.add_action(Action.DETECT_PIT)
                            self.add_KB(valid_adj_cell)
                            valid_adj_cell.update_parent(valid_adj_cell)
                            temp_adj_cell_list.append(valid_adj_cell)
                        else:
                            self.add_action(Action.INFER_NOT_PIT)
                            not_alpha = [[valid_adj_cell.get_literal(CellType.PIT, '+')]]
                            have_no_pit = self.KB.infer(not_alpha)

                            if have_no_pit:
                                self.add_action(Action.DETECT_NO_PIT)
                            else:
                                temp_adj_cell_list.append(valid_adj_cell)

        # Remove invalid cells
        temp_adj_cell_list = list(set(temp_adj_cell_list))
        for adj_cell in temp_adj_cell_list:
            valid_adj_cell_list.remove(adj_cell)

        # SCORE-OPTIMIZED EXPLORATION SELECTION
        if valid_adj_cell_list:
            # Use hybrid strategy for cell selection
            explored_positions = set()
            for row in self.cell_matrix:
                for cell in row:
                    if cell.is_explored():
                        explored_positions.add(cell.map_pos)
            
            # Get score-optimized target
            optimal_target = self.optimize_exploration_strategy()
            
            if optimal_target:
                optimal_cell = self.cell_matrix[optimal_target[0]][optimal_target[1]]
                if optimal_cell in valid_adj_cell_list:
                    # Prioritize score-optimal target
                    valid_adj_cell_list.remove(optimal_cell)
                    valid_adj_cell_list.insert(0, optimal_cell)

        # Continue with backtracking
        self.agent_cell.update_child(valid_adj_cell_list)
        for new_cell in self.agent_cell.child:
            if self.game_ended:
                return False
                
            self.move_to(new_cell)
            self.append_event_to_output_file('Move to: ' + str(self.agent_cell.map_pos))

            # Check for immediate exit after move
            if self.agent_cell.map_pos[0] == 0 and self.agent_cell.map_pos[1] == 0:
                self.add_action(Action.CLIMB_OUT_OF_THE_CAVE)
                self.game_ended = True
                return False

            search_result = self.hybrid_backtracking_search()
            if not search_result:
                return False

            if not self.game_ended:
                self.move_to(pre_agent_cell)
                self.append_event_to_output_file('Backtrack: ' + str(pre_agent_cell.map_pos))

        return True
    
    def solve(self):
        """Hybrid solver that maximizes score"""
        # Reset output file
        file = open(self.output_filename, 'w')
        file.close()

        # Use hybrid backtracking search
        game_result = self.hybrid_backtracking_search()
        
        # Score optimization check
        if game_result is not False:
            # Check if we achieved maximum possible score
            final_score = self.calculate_current_score()
            max_possible = self.estimate_max_possible_score()
            
            # If we can still collect gold/kill wumpus, do it
            victory = True
            for row in self.cell_matrix:
                for col in row:
                    if col.exist_Entity(0) or col.exist_Entity(2):
                        victory = False
                        break

            if victory:
                self.add_action(Action.KILL_ALL_WUMPUS_AND_GRAB_ALL_FOOD)
        
        return self.action_list
    
    def top_condition(self):
        """Enhanced top condition with score tracking"""
        super().top_condition()
        
        # Track gold collection
        if self.agent_cell.exist_Entity(0):
            self.collected_gold += 1
            self.has_gold = True  # Set flag when gold is collected
