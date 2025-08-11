import random

import utils
from constants import ROOT_INPUT

DDX = [(0, 1), (0, -1), (-1, 0), (1, 0)]


def random_Map(N: int = 10, map_name: str = "randMap.txt") -> None:
    _map = [['' for _ in range(10)] for _ in range(10)]
    agent_r = random.randint(0, 9)
    agent_c = random.randint(0, 9)
    for row in range(N):
        for col in range(N):
            flag = True
            for (d_r, d_c) in DDX:
                new_r = agent_r + d_r
                new_c = agent_c + d_c
                if row == new_r and col == new_c:
                    flag = False
                    break
            if not flag:
                continue
            if row == agent_r and col == agent_c:
                _map[row][col] += 'A'
            elif random.randint(1, 20) % 11 == 0:
                # wumpus here
                _map[row][col] += 'W'
                _map[row][col].replace('S', '')
                # add stench
                for (d_r, d_c) in DDX:
                    neighbor_row = row + d_r
                    neighbor_col = col + d_c
                    if utils.Utils.isValid(neighbor_row, neighbor_col, N):
                        if _map[neighbor_row][neighbor_col].find('S') == -1:
                            _map[neighbor_row][neighbor_col] += 'S'
            elif random.randint(1, 20) % 9 == 0:
                # pit here
                _map[row][col] += 'P'
                # add stench
                for (d_r, d_c) in DDX:
                    neighbor_row = row + d_r
                    neighbor_col = col + d_c
                    if utils.Utils.isValid(neighbor_row, neighbor_col, N):
                        if _map[neighbor_row][neighbor_col].find('B') == -1:
                            _map[neighbor_row][neighbor_col] += 'B'
            elif random.randint(1, 20) % 3 == 0:
                _map[row][col] += 'G'

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
