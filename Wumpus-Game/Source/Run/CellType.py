from enum import Enum


class CellType(Enum):
    PIT = 'P'
    BREEZE = 'B'
    WUMPUS = 'W'
    STENCH = 'S'
    GOLD = 'G'
    AGENT = 'A'
    EMPTY = '-'
