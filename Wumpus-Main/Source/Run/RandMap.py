import random
import heapq
from typing import List, Tuple, Set
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils
from constants import ROOT_INPUT

DDX = [(0, 1), (0, -1), (-1, 0), (1, 0)]


class AStarNode:
    """Node class for A* pathfinding algorithm"""
    def __init__(self, pos: Tuple[int, int], g_cost: float = 0, h_cost: float = 0, parent=None):
        self.pos = pos
        self.g_cost = g_cost  # Cost from start to current node
        self.h_cost = h_cost  # Heuristic cost from current node to goal
        self.f_cost = g_cost + h_cost  # Total cost
        self.parent = parent
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        return self.pos == other.pos


def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """Calculate Manhattan distance between two positions"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def get_neighbors(pos: Tuple[int, int], N: int) -> List[Tuple[int, int]]:
    """Get valid neighboring positions"""
    neighbors = []
    for dr, dc in DDX:
        new_r, new_c = pos[0] + dr, pos[1] + dc
        if 0 <= new_r < N and 0 <= new_c < N:
            neighbors.append((new_r, new_c))
    return neighbors


def astar_pathfinding(start: Tuple[int, int], goal: Tuple[int, int], N: int, 
                     obstacles: Set[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
    """
    A* pathfinding algorithm to find optimal path from start to goal
    
    Args:
        start: Starting position (row, col)
        goal: Goal position (row, col)  
        N: Grid size
        obstacles: Set of positions to avoid (optional)
    
    Returns:
        List of positions representing the optimal path
    """
    if obstacles is None:
        obstacles = set()
    
    # Priority queue for open nodes
    open_list = []
    heapq.heappush(open_list, AStarNode(start, 0, manhattan_distance(start, goal)))
    
    # Sets for tracking visited and open nodes
    closed_set = set()
    open_set = {start}
    
    # Dictionary for quick node lookup
    nodes = {start: AStarNode(start, 0, manhattan_distance(start, goal))}
    
    while open_list:
        # Get node with lowest f_cost
        current = heapq.heappop(open_list)
        open_set.remove(current.pos)
        closed_set.add(current.pos)
        
        # Check if we reached the goal
        if current.pos == goal:
            # Reconstruct path
            path = []
            while current:
                path.append(current.pos)
                current = current.parent
            return path[::-1]  # Reverse to get start->goal path
        
        # Explore neighbors
        for neighbor_pos in get_neighbors(current.pos, N):
            # Skip if neighbor is obstacle or already visited
            if neighbor_pos in obstacles or neighbor_pos in closed_set:
                continue
            
            # Calculate costs
            tentative_g = current.g_cost + 1  # Cost of moving to neighbor
            h_cost = manhattan_distance(neighbor_pos, goal)
            
            # If neighbor not in open set or we found a better path
            if neighbor_pos not in open_set:
                neighbor = AStarNode(neighbor_pos, tentative_g, h_cost, current)
                nodes[neighbor_pos] = neighbor
                heapq.heappush(open_list, neighbor)
                open_set.add(neighbor_pos)
            elif tentative_g < nodes[neighbor_pos].g_cost:
                # Update existing node with better path
                neighbor = nodes[neighbor_pos]
                neighbor.g_cost = tentative_g
                neighbor.f_cost = tentative_g + h_cost
                neighbor.parent = current
    
    # No path found - fallback to simple L-shaped path
    return create_simple_path(start, goal)


def create_simple_path(start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    Fallback: Create simple L-shaped path when A* fails
    """
    path = []
    current_r, current_c = start
    goal_r, goal_c = goal
    
    # Add starting position
    path.append((current_r, current_c))
    
    # Move horizontally first
    while current_c != goal_c:
        if current_c < goal_c:
            current_c += 1
        else:
            current_c -= 1
        path.append((current_r, current_c))
    
    # Then move vertically
    while current_r != goal_r:
        if current_r < goal_r:
            current_r += 1
        else:
            current_r -= 1
        path.append((current_r, current_c))
    
    return path


def create_safe_path(start_r: int, start_c: int, end_r: int, end_c: int, N: int) -> List[Tuple[int, int]]:
    """
    Create optimal safe path using A* algorithm
    """
    start = (start_r, start_c)
    goal = (end_r, end_c)
    
    # Use A* to find optimal path
    path = astar_pathfinding(start, goal, N)
    
    # Ensure path is valid
    if not path or path[0] != start or path[-1] != goal:
        # Fallback to simple path if A* fails
        path = create_simple_path(start, goal)
    
    return path


def random_Map(N: int = 8, map_name: str = "randMap.txt", K: int = 2, p: float = 0.2) -> None:
    """
    Generate random N x N Wumpus World map with GUARANTEED safe path
    Args:
        N: Grid size (default 10)
        map_name: Output file name
        K: Number of Wumpus (default 2)
        p: Pit density factor (default 0.2) - unused, will be calculated based on map size
    
    NEW LOGIC:
    - Agent spawns randomly anywhere
    - Exit door is always at (0,0) - top-left corner
    - Number of pits = (N*N - 2) * 0.2
    - GUARANTEED safe path from agent spawn to exit door
    """
    _map = [['' for _ in range(N)] for _ in range(N)]
    
    # Calculate number of pits based on map size
    total_cells = N * N
    num_pits = int((total_cells - 2) * 0.2)  # (kích thước map - 2) * 0.2
    
    print(f"Map size: {N}x{N} = {total_cells} cells")
    print(f"Number of pits to place: {num_pits}")
    
    # Step 1: Set exit door position
    exit_r = 0    # Top row
    exit_c = 0    # Left column
    
    # Step 2: Choose random agent spawn position (not at exit)
    agent_r, agent_c = None, None
    attempts = 0
    while agent_r is None and attempts < 100:
        temp_r = random.randint(0, N-1)
        temp_c = random.randint(0, N-1)
        # Agent cannot spawn at exit door position
        if not (temp_r == exit_r and temp_c == exit_c):
            agent_r = temp_r
            agent_c = temp_c
        attempts += 1
    
    # Fallback if no valid position found
    if agent_r is None:
        agent_r = N - 1  # Bottom row
        agent_c = N - 1  # Right column
    
    # Step 3: Create GUARANTEED safe path from agent to exit using simple pathfinding
    safe_path = create_safe_path(agent_r, agent_c, exit_r, exit_c, N)
    
    # Step 4: Mark all safe path cells and their neighbors as protected
    protected_cells = set()
    for (r, c) in safe_path:
        protected_cells.add((r, c))
        # Add adjacent cells to protected zone
        for (d_r, d_c) in DDX:
            new_r = r + d_r
            new_c = c + d_c
            if utils.Utils.isValid(new_r, new_c, N):
                protected_cells.add((new_r, new_c))
    
    # Step 5: Place agent
    _map[agent_r][agent_c] = 'A'
    # Step 6: Place K Wumpus randomly (not in protected cells)
    wumpus_count = 0
    attempts = 0
    while wumpus_count < K and attempts < 100:
        row = random.randint(0, N-1)
        col = random.randint(0, N-1)
        if (row, col) not in protected_cells and 'W' not in _map[row][col]:
            _map[row][col] += 'W'
            wumpus_count += 1
            # Add stench to adjacent cells (only if not protected)
            for (d_r, d_c) in DDX:
                neighbor_row = row + d_r
                neighbor_col = col + d_c
                if utils.Utils.isValid(neighbor_row, neighbor_col, N):
                    # Only add stench if not in protected safe path
                    if (neighbor_row, neighbor_col) not in safe_path:
                        if 'S' not in _map[neighbor_row][neighbor_col]:
                            _map[neighbor_row][neighbor_col] += 'S'
        attempts += 1
    
    # Step 7: Place exact number of pits (not in protected cells)
    pit_count = 0
    attempts = 0
    available_cells = []
    
    # Collect all available cells for pit placement
    for row in range(N):
        for col in range(N):
            if ((row, col) not in protected_cells and 
                'W' not in _map[row][col] and 
                'A' not in _map[row][col]):
                available_cells.append((row, col))
    
    print(f"Available cells for pit placement: {len(available_cells)}")
    
    # Randomly select cells for pit placement
    if len(available_cells) >= num_pits:
        selected_pit_cells = random.sample(available_cells, num_pits)
        
        for pit_row, pit_col in selected_pit_cells:
            _map[pit_row][pit_col] += 'P'
            pit_count += 1
            
            # Add breeze to adjacent cells (only if not protected)
            for (d_r, d_c) in DDX:
                neighbor_row = pit_row + d_r
                neighbor_col = pit_col + d_c
                if utils.Utils.isValid(neighbor_row, neighbor_col, N):
                    # Only add breeze if not in protected safe path
                    if (neighbor_row, neighbor_col) not in safe_path:
                        if 'B' not in _map[neighbor_row][neighbor_col]:
                            _map[neighbor_row][neighbor_col] += 'B'
    else:
        print(f"Warning: Not enough available cells for {num_pits} pits. Only {len(available_cells)} available.")
        # Place as many pits as possible
        for pit_row, pit_col in available_cells:
            _map[pit_row][pit_col] += 'P'
            pit_count += 1
            
            # Add breeze to adjacent cells
            for (d_r, d_c) in DDX:
                neighbor_row = pit_row + d_r
                neighbor_col = pit_col + d_c
                if utils.Utils.isValid(neighbor_row, neighbor_col, N):
                    if (neighbor_row, neighbor_col) not in safe_path:
                        if 'B' not in _map[neighbor_row][neighbor_col]:
                            _map[neighbor_row][neighbor_col] += 'B'
    
    print(f"Actually placed pits: {pit_count}")
    
    # Step 8: Place exactly one gold (can be anywhere except cells with pit or wumpus)
    gold_placed = False
    attempts = 0
    while not gold_placed and attempts < 100:
        row = random.randint(0, N-1)
        col = random.randint(0, N-1)
        if 'P' not in _map[row][col] and 'W' not in _map[row][col]:
            _map[row][col] += 'G'
            gold_placed = True
        attempts += 1

    # Step 9: Fill empty cells
    for row in range(N):
        for col in range(N):
            if len(_map[row][col]) == 0:
                _map[row][col] = '-'
                
    # Debug: Print map generation information
    print(f"Generated map using A* pathfinding:")
    print(f"Agent spawn: ({agent_r}, {agent_c})")
    print(f"Exit door: ({exit_r}, {exit_c})")
    print(f"Map size: {N}x{N} = {total_cells} cells")
    print(f"Wumpus placed: {wumpus_count}/{K}")
    print(f"Pits placed: {pit_count}/{num_pits}")
    print(f"A* optimal path length: {len(safe_path)} cells")
    print(f"Protected cells (path + buffer): {len(protected_cells)} cells")
    print(f"Path: {' -> '.join([f'({r},{c})' for r, c in safe_path])}")
    
    # Write file only once
    file = open(f'{ROOT_INPUT}{map_name}', 'w')
    file.write(f'{N}\n')
    for row in range(N):
        for col in range(N):
            file.write(_map[row][col])
            if col != N - 1:
                file.write('.')
        if row != N - 1:
            file.write('\n')
    file.close()


if __name__ == "__main__":
    # Test different map sizes
    for size in [4, 6, 8, 10]:
        print(f"\n=== Testing map size {size}x{size} ===")
        random_Map(size, f"test_{size}.txt", 1)
        print(f"Expected pits: {int(((size * size) - 2) * 0.2)}")
        print("-" * 50)
