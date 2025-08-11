import random

import utils
from constants import ROOT_INPUT

DDX = [(0, 1), (0, -1), (-1, 0), (1, 0)]


def random_Map(N: int = 10, map_name: str = "randMap.txt", K: int = 2, p: float = 0.2) -> None:
    """
    Generate random N x N Wumpus World map
    Args:
        N: Grid size (default 10)
        map_name: Output file name
        K: Number of Wumpus (default 2)
        p: Pit probability (default 0.2)
    """
    _map = [['' for _ in range(N)] for _ in range(N)]
    # Agent always starts at (0,0) - bottom left in matrix is (N-1, 0)
    agent_r = N - 1  # Bottom row
    agent_c = 0      # Left column
    
    # Place agent at starting position
    _map[agent_r][agent_c] = 'A'
    
    # Create list of safe cells (agent position and adjacent cells)
    safe_cells = {(agent_r, agent_c)}
    for (d_r, d_c) in DDX:
        new_r = agent_r + d_r
        new_c = agent_c + d_c
        if utils.Utils.isValid(new_r, new_c, N):
            safe_cells.add((new_r, new_c))
    
    # Place K Wumpus randomly (not in safe cells)
    wumpus_count = 0
    attempts = 0
    while wumpus_count < K and attempts < 100:
        row = random.randint(0, N-1)
        col = random.randint(0, N-1)
        if (row, col) not in safe_cells and 'W' not in _map[row][col]:
            _map[row][col] += 'W'
            wumpus_count += 1
            # Add stench to adjacent cells
            for (d_r, d_c) in DDX:
                neighbor_row = row + d_r
                neighbor_col = col + d_c
                if utils.Utils.isValid(neighbor_row, neighbor_col, N):
                    if 'S' not in _map[neighbor_row][neighbor_col]:
                        _map[neighbor_row][neighbor_col] += 'S'
        attempts += 1
    
    # Place pits with probability p (not in safe cells or cells with Wumpus)
    for row in range(N):
        for col in range(N):
            if (row, col) not in safe_cells and 'W' not in _map[row][col]:
                if random.random() < p:  # Use proper probability
                    _map[row][col] += 'P'
                    # Add breeze to adjacent cells
                    for (d_r, d_c) in DDX:
                        neighbor_row = row + d_r
                        neighbor_col = col + d_c
                        if utils.Utils.isValid(neighbor_row, neighbor_col, N):
                            if 'B' not in _map[neighbor_row][neighbor_col]:
                                _map[neighbor_row][neighbor_col] += 'B'
    
    # Place exactly one gold (can be anywhere except cells with pit or wumpus)
    gold_placed = False
    attempts = 0
    while not gold_placed and attempts < 100:
        row = random.randint(0, N-1)
        col = random.randint(0, N-1)
        if 'P' not in _map[row][col] and 'W' not in _map[row][col]:
            _map[row][col] += 'G'
            gold_placed = True
        attempts += 1

    for row in range(N):
        for col in range(N):
            if len(_map[row][col]) == 0:
                _map[row][col] = '-'
    # write file
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
