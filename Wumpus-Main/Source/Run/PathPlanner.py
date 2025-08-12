import heapq
from typing import List, Tuple, Set, Optional
from Run.Cell import Cell
from Run.CellType import CellType


class PlanningNode:
    """Node class for planning with cost, risk, and utility"""
    def __init__(self, pos: Tuple[int, int], g_cost: float = 0, h_cost: float = 0, 
                 risk_cost: float = 0, utility: float = 0, parent=None):
        self.pos = pos
        self.g_cost = g_cost  # Actual cost from start
        self.h_cost = h_cost  # Heuristic cost to goal
        self.risk_cost = risk_cost  # Risk penalty
        self.utility = utility  # Expected utility
        
        # CORRECTED: Proper cost-risk-utility balance
        # f = g + h + risk - utility
        # But we need to handle infinite risk specially
        if risk_cost == float('inf'):
            self.f_cost = float('inf')  # Absolutely avoid dangerous cells
        else:
            # Balance factors: movement cost + heuristic + risk penalty - utility gain
            self.f_cost = g_cost + h_cost + (risk_cost * 0.5) - (utility * 0.3)
        
        self.parent = parent
    
    def __lt__(self, other):
        # Handle infinite costs
        if self.f_cost == float('inf') and other.f_cost == float('inf'):
            return False  # Equal infinite costs
        if self.f_cost == float('inf'):
            return False  # This node is worse
        if other.f_cost == float('inf'):
            return True   # This node is better
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return self.pos == other.pos


class PathPlanner:
    """Planning Module implementing A* with cost, risk, and expected utility"""
    
    def __init__(self, cell_matrix: List[List[Cell]], kb):
        self.cell_matrix = cell_matrix
        self.kb = kb
        self.N = len(cell_matrix)
    
    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Manhattan distance heuristic"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def calculate_risk(self, cell: Cell) -> float:
        """Calculate risk cost for a cell based on pit/wumpus probability"""
        if cell.is_explored():
            # Known cell risks
            if cell.exist_Entity(1):  # Pit
                return float('inf')  # Infinite risk - absolutely avoid
            if cell.exist_Entity(2):  # Wumpus  
                return float('inf')  # Infinite risk - absolutely avoid
            return 0.0  # Safe explored cell
        
        # Unexplored cell - use KB inference to estimate risk
        risk = 0.0
        
        # Check if we can PROVE cell is safe
        safe_from_pit = False
        safe_from_wumpus = False
        
        # Try to prove NO PIT
        alpha_no_pit = [[cell.get_literal(CellType.PIT, '-')]]
        if self.kb.infer(alpha_no_pit):
            safe_from_pit = True
        
        # Try to prove NO WUMPUS  
        alpha_no_wumpus = [[cell.get_literal(CellType.WUMPUS, '-')]]
        if self.kb.infer(alpha_no_wumpus):
            safe_from_wumpus = True
        
        # If we can prove safety, low risk
        if safe_from_pit and safe_from_wumpus:
            return 10.0  # Small exploration cost
        
        # Try to prove DANGER exists
        alpha_pit = [[cell.get_literal(CellType.PIT, '+')]]
        alpha_wumpus = [[cell.get_literal(CellType.WUMPUS, '+')]]
        
        if self.kb.infer(alpha_pit):
            risk += 1000.0  # Proven pit
        elif not safe_from_pit:
            risk += 300.0  # Uncertain about pit
            
        if self.kb.infer(alpha_wumpus):
            risk += 800.0  # Proven wumpus
        elif not safe_from_wumpus:
            risk += 200.0  # Uncertain about wumpus
        
        return risk
    
    def calculate_utility(self, cell: Cell) -> float:
        """Calculate expected utility for a cell"""
        utility = 0.0
        
        if cell.is_explored():
            if cell.exist_Entity(0):  # Gold
                utility += 1000.0  # High utility for gold
            # Explored cells have baseline utility for safe movement
            utility += 5.0
            return utility
        
        # Unexplored cell - calculate expected utility based on:
        # 1. Information gain from exploration
        # 2. Potential gold discovery
        # 3. Strategic position value
        
        # Base exploration utility
        utility += 50.0  # Information gain value
        
        # Gold discovery potential
        # Check if this cell could contain gold based on glitter in adjacent cells
        adj_cells = cell.get_adj_cell(self.cell_matrix)
        glitter_nearby = False
        for adj_cell in adj_cells:
            if adj_cell.is_explored():
                # In Wumpus world, glitter indicates adjacent gold
                # This would need to be implemented based on game rules
                # For now, use proximity to unexplored areas as proxy
                utility += 2.0  # Small bonus for being near explored areas
        
        # Strategic position utility - prefer cells that open up more exploration
        unexplored_neighbors = 0
        for adj_cell in adj_cells:
            if not adj_cell.is_explored():
                unexplored_neighbors += 1
        
        # Higher utility for cells that open up more exploration options
        utility += unexplored_neighbors * 10.0
        
        # Distance-based utility - prefer cells closer to unexplored frontier
        utility += self.calculate_frontier_proximity(cell)
        
        return utility
    
    def calculate_frontier_proximity(self, cell: Cell) -> float:
        """Calculate utility based on proximity to exploration frontier"""
        # Simple implementation: higher utility for cells near unexplored areas
        pos = cell.map_pos
        proximity_bonus = 0.0
        
        # Check in expanding radius for unexplored cells
        for radius in range(1, min(4, self.N)):
            unexplored_count = 0
            total_checked = 0
            
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    if abs(dr) == radius or abs(dc) == radius:  # Only border cells
                        new_r, new_c = pos[0] + dr, pos[1] + dc
                        if 0 <= new_r < self.N and 0 <= new_c < self.N:
                            total_checked += 1
                            check_cell = self.cell_matrix[new_r][new_c]
                            if not check_cell.is_explored():
                                unexplored_count += 1
            
            if total_checked > 0:
                frontier_ratio = unexplored_count / total_checked
                proximity_bonus += frontier_ratio * (10.0 / radius)  # Closer = higher bonus
        
        return proximity_bonus
    
    def get_valid_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get valid neighboring positions"""
        neighbors = []
        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]  # Right, Left, Up, Down
        
        for dr, dc in directions:
            new_r, new_c = pos[0] + dr, pos[1] + dc
            if 0 <= new_r < self.N and 0 <= new_c < self.N:
                neighbors.append((new_r, new_c))
        return neighbors
    
    def plan_optimal_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Plan optimal path using A* with cost, risk, and utility considerations
        
        Args:
            start: Starting position (row, col)
            goal: Goal position (row, col)
        
        Returns:
            List of positions representing optimal path, or None if no path found
        """
        # Priority queue for open nodes
        open_list = []
        start_cell = self.cell_matrix[start[0]][start[1]]
        start_risk = self.calculate_risk(start_cell)
        start_utility = self.calculate_utility(start_cell)
        start_h = self.manhattan_distance(start, goal)
        
        start_node = PlanningNode(start, 0, start_h, start_risk, start_utility)
        heapq.heappush(open_list, start_node)
        
        # Sets for tracking visited and open nodes
        closed_set = set()
        open_set = {start}
        
        # Dictionary for quick node lookup
        nodes = {start: start_node}
        
        while open_list:
            # Get node with lowest f_cost (best cost-risk-utility balance)
            current = heapq.heappop(open_list)
            open_set.remove(current.pos)
            closed_set.add(current.pos)
            
            # Check if we reached the goal
            if current.pos == goal:
                # Reconstruct optimal path
                path = []
                while current:
                    path.append(current.pos)
                    current = current.parent
                return path[::-1]  # Reverse to get start->goal path
            
            # Explore neighbors
            for neighbor_pos in self.get_valid_neighbors(current.pos):
                # Skip if already visited
                if neighbor_pos in closed_set:
                    continue
                
                neighbor_cell = self.cell_matrix[neighbor_pos[0]][neighbor_pos[1]]
                
                # Skip if definitely dangerous (explored pit/wumpus)
                if (neighbor_cell.is_explored() and 
                    (neighbor_cell.exist_Entity(1) or neighbor_cell.exist_Entity(2))):
                    continue
                
                # Calculate costs with proper weighting
                move_cost = 1.0  # Base movement cost
                tentative_g = current.g_cost + move_cost
                h_cost = self.manhattan_distance(neighbor_pos, goal)
                risk_cost = self.calculate_risk(neighbor_cell)
                utility = self.calculate_utility(neighbor_cell)
                
                # Skip cells with infinite risk (guaranteed dangerous)
                if risk_cost == float('inf'):
                    continue
                
                # If neighbor not in open set or we found a better path
                if neighbor_pos not in open_set:
                    neighbor_node = PlanningNode(neighbor_pos, tentative_g, h_cost, 
                                               risk_cost, utility, current)
                    nodes[neighbor_pos] = neighbor_node
                    heapq.heappush(open_list, neighbor_node)
                    open_set.add(neighbor_pos)
                elif tentative_g < nodes[neighbor_pos].g_cost:
                    # Update existing node with better path
                    neighbor_node = nodes[neighbor_pos]
                    neighbor_node.g_cost = tentative_g
                    neighbor_node.risk_cost = risk_cost
                    neighbor_node.utility = utility
                    # Recalculate f_cost with updated values
                    if risk_cost == float('inf'):
                        neighbor_node.f_cost = float('inf')
                    else:
                        neighbor_node.f_cost = tentative_g + h_cost + (risk_cost * 0.5) - (utility * 0.3)
                    neighbor_node.parent = current
        
        # No path found
        return None
    
    def plan_safe_exploration(self, current_pos: Tuple[int, int], 
                            explored_cells: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        Plan next safe cell to explore based on risk-utility analysis
        
        Args:
            current_pos: Current agent position
            explored_cells: Set of already explored positions
        
        Returns:
            Best next position to explore, or None if no safe options
        """
        candidates = []
        
        # Get all adjacent unexplored cells
        for neighbor_pos in self.get_valid_neighbors(current_pos):
            if neighbor_pos not in explored_cells:
                neighbor_cell = self.cell_matrix[neighbor_pos[0]][neighbor_pos[1]]
                
                risk = self.calculate_risk(neighbor_cell)
                utility = self.calculate_utility(neighbor_cell)
                
                # Skip cells with infinite risk (guaranteed dangerous)
                if risk == float('inf'):
                    continue
                
                # Only consider reasonably safe cells (risk threshold)
                risk_threshold = 500.0  # Adjustable based on game strategy
                if risk < risk_threshold:
                    # Calculate exploration score: utility / (1 + risk)
                    # Higher utility and lower risk = better score
                    if risk == 0:
                        score = utility  # No risk division
                    else:
                        score = utility / (1 + risk * 0.01)  # Normalize risk impact
                    
                    candidates.append((neighbor_pos, score, risk, utility))
        
        # Return best candidate based on score
        if candidates:
            # Sort by score (utility/risk ratio) descending, then by risk ascending
            candidates.sort(key=lambda x: (-x[1], x[2]))
            return candidates[0][0]
        
        # If no good candidates, try with relaxed risk threshold
        relaxed_candidates = []
        for neighbor_pos in self.get_valid_neighbors(current_pos):
            if neighbor_pos not in explored_cells:
                neighbor_cell = self.cell_matrix[neighbor_pos[0]][neighbor_pos[1]]
                risk = self.calculate_risk(neighbor_cell)
                
                # Skip only infinite risk cells
                if risk != float('inf'):
                    utility = self.calculate_utility(neighbor_cell)
                    score = utility / (1 + risk * 0.01) if risk > 0 else utility
                    relaxed_candidates.append((neighbor_pos, score, risk, utility))
        
        if relaxed_candidates:
            relaxed_candidates.sort(key=lambda x: (-x[1], x[2]))
            return relaxed_candidates[0][0]
        
        return None
