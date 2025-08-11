import pygame

from constants import CELL_SIZE, ROOT_INPUT, MARGIN, HEIGHT


class Utils:
    def __init__(self):
        pass

    @staticmethod
    def load_image_alpha(path: str, rotate: int = 0, size: int = CELL_SIZE):
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, (size, size))
        image = pygame.transform.rotate(image, rotate)
        return image

    @staticmethod
    def load_image(path: str, rotate: int = 0, size: int = CELL_SIZE):
        image = pygame.image.load(path).convert()
        image = pygame.transform.scale(image, (size, size))
        image = pygame.transform.rotate(image, rotate)
        return image

    @staticmethod
    def readMapInFile(filename: str, cell_size, spacing_cell):
        f = open(ROOT_INPUT + filename, "r")
        # read N
        x = f.readline().split()
        N = int(x[0])
        # end read N

        # read info map
        _map: list[list[str]] = []
        for _ in range(N):
            line = f.readline().split(".")
            _map.append([x.replace('\n', '') for x in line])
        f.close()
        MARGIN['TOP'] = (HEIGHT - N * cell_size - spacing_cell * (N + 1)) // 2
        MARGIN['LEFT'] = MARGIN['TOP']
        return N, _map

    @staticmethod
    def isValid(row, col, N):
        return 0 <= row < N and 0 <= col < N
