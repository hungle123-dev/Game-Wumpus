import sys

import pygame

from Entity.Board import Board
from Menu.Button import Button
from Menu.Button2 import Button2
from Menu.Item import Item
from Run.RandMap import random_Map
from constants import (NAME_WINDOW, FPS, WIDTH, HEIGHT, ICON_NAME, BLACK, MESSAGE_WINDOW, MARGIN, BG_IMAGE, FONT_3, RED,
                       WHITE, FONT_1, NAME_ITEM, YELLOW, NUMBER_CELL, DEFAULT_WUMPUS_COUNT, DEFAULT_PIT_PROBABILITY)

# --------------------- initial pygame -----------------------------
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption(NAME_WINDOW)
pygame.display.set_icon(pygame.image.load(ICON_NAME))
screen = pygame.display.set_mode((WIDTH, HEIGHT))


# -------------------- end initial pygame --------------------------


# ---------------------- create global data --------------------------------


# ---------------------- end create global data ----------------------------


def quit_click():
    pygame.quit()
    sys.exit(0)


class Game:
    def __init__(self):
        self.running = False
        self.running_menu = True
        self.board = None
        self.status = "START_MENU"
        self.delay = 10
        self.map_name = None
        self.result_name = None
        self.clicked = False
        self.pause = False
        self.agent_action_count = 0

        bg = pygame.image.load(BG_IMAGE)
        self.bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))

        # Screen Home
        self.btnStart = Button2((WIDTH - 350) // 2, (HEIGHT - 100) // 2 - HEIGHT // 6, 350, 100, screen,
                                60, 'START', self.start_click, WHITE)
        self.btnQuit = Button2((WIDTH - 350) // 2, (HEIGHT - 100) // 2 + HEIGHT // 6 + 30, 350, 100, screen,
                               60, 'QUIT', quit_click, WHITE)

        # Screen Choose map
        self.btnBackHome = Button2(20, HEIGHT - 120, 200, 100, screen,
                                   60, 'BACK', self.back_home_click, WHITE)

        # Random, Advance and Comparison maps available with proper spacing
        self.btnMapRand = Button2((WIDTH - 300) // 2, (HEIGHT - 100) // 2 - 120, 300, 100, screen,
                                60, 'RANDOM', self.choose_rand_map, WHITE)
        self.btnAdvance = Button2((WIDTH - 300) // 2, (HEIGHT - 100) // 2, 300, 100, screen,
                                60, 'ADVANCE', self.choose_advance_map, WHITE)
        self.btnComparison = Button2((WIDTH - 300) // 2, (HEIGHT - 100) // 2 + 120, 300, 100, screen,
                                60, 'COMPARISON', self.choose_comparison, WHITE)
        # Screen End Game
        self.btnBack = None
        self.btnRestart = None
        self.btnPause = None
        self.btnContinue = None

    def initBtnEndGame(self):
        self.btnBack = Button(MESSAGE_WINDOW['LEFT'] + 30, MESSAGE_WINDOW['BOTTOM'] - 100, 200, 60, screen,
                              40, 'BACK', self.back_click)
        self.btnRestart = Button(WIDTH - 250, MESSAGE_WINDOW['BOTTOM'] - 100, 200, 60, screen,
                                 40, 'RESTART', self.restart_click)
        self.btnPause = Button2(MESSAGE_WINDOW['LEFT'] + (WIDTH - MESSAGE_WINDOW['LEFT'] - 200) // 2,
                                MESSAGE_WINDOW['BOTTOM'] - 100, 200, 70, screen,
                                40, 'PAUSE', self.pause_click, WHITE)
        self.btnContinue = Button2(MESSAGE_WINDOW['LEFT'] + (WIDTH - MESSAGE_WINDOW['LEFT'] - 220) // 2,
                                   MESSAGE_WINDOW['BOTTOM'] - 100, 220, 70, screen,
                                   40, 'CONTINUE', self.continue_click, WHITE)

    def pause_click(self):
        if self.clicked:
            self.pause = True
            self.clicked = False
            # Pause functionality - no need for scrollbar since we removed ListView

    def continue_click(self):
        if self.clicked:
            self.pause = False
            self.clicked = False
            # Continue functionality - no need for scrollbar since we removed ListView

    def choose_rand_map(self):
        if self.clicked:
            self.map_name = "randMap.txt"
            # Use new parameters for random map generation
            random_Map(NUMBER_CELL, self.map_name, DEFAULT_WUMPUS_COUNT, DEFAULT_PIT_PROBABILITY)
            self.result_name = "resultRandMap.txt"
            self.status = "RUN_GAME"
            pygame.display.set_caption(NAME_WINDOW + ' - Random map')
    
    def choose_advance_map(self):
        if self.clicked:
            self.map_name = "advance.txt"
            self.result_name = "advance.txt"
            self.status = "RUN_GAME"
            pygame.display.set_caption(NAME_WINDOW + ' - Advance Map')

    def choose_comparison(self):
        if self.clicked:
            self.map_name = "randMap.txt"
            # Generate random map for comparison
            random_Map(NUMBER_CELL, self.map_name, DEFAULT_WUMPUS_COUNT, DEFAULT_PIT_PROBABILITY)
            self.result_name = "resultComparison.txt"
            self.status = "RUN_GAME"
            pygame.display.set_caption(NAME_WINDOW + ' - Comparison Mode')

    def move(self):
        if not self.board.move():
            self.status = "END_GAME"
        
        # ENHANCED FIX: Only move Wumpus at specific action intervals to reduce race conditions
        if self.status != "END_GAME" and not self.board.game_won:
            self.agent_action_count += 1
            
            # Move Wumpus every 5 actions, but only if no actions are pending
            # This reduces the chance of race conditions during shooting sequences
            if (self.map_name == "advance.txt" and 
                self.agent_action_count % 5 == 0 and
                len(self.board.action_list) <= 1):  # Allow 1 action pending (current action)
                for wumpus in self.board.Wumpus:
                    # print(f"Moving Wumpus")  # Hidden for cleaner output
                    wumpus.move_random(self.board)
        # elif self.board.game_won:
        #     print("🛑 Game won - Wumpus movement STOPPED")  # Hidden to prevent spam

    def back_click(self):
        self.status = "CHOOSE_MAP"
        self.running_menu = True
        self.running = False
        self.menu()

    def back_home_click(self):
        if self.clicked:
            self.status = "START_MENU"

    def start_click(self):
        if self.clicked:
            self.status = "CHOOSE_MAP"
            self.clicked = False

    def restart_click(self):
        MARGIN["LEFT"] = 0
        self.status = "RUN_GAME"
        self.delay = 10
        self.board = Board(self.map_name, self.result_name)

    def run(self) -> None:
        self.clicked = False
        self.delay = 10
        while self.running:
            # re-draw window
            self.clicked = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.running_menu = True
                    self.status = "START_MENU"
                    self.menu()
                    # TODO: show menu latest
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.clicked = True
                    if event.button == 4:
                        self.board.scroll_up()
                    elif event.button == 5:
                        self.board.scroll_down()

            screen.fill(BLACK)
            self.board.draw(screen)

            if self.status == 'END_GAME':
                self.btnBack.process()
                self.btnRestart.process()
                pygame.display.flip()
                clock.tick(300)
            else:
                if self.delay <= 0 and not self.pause:
                    self.btnPause.process()
                elif self.pause:
                    self.btnContinue.process()
                pygame.display.flip()
                clock.tick(FPS)
            # ----------------------------

            if self.board.delay:
                pygame.time.delay(500)
            # delay game
            if self.delay > 0:
                self.delay -= 1
                continue

            # Agent move
            if not self.pause:
                self.move()

    def menu(self):
        pygame.display.set_caption(NAME_WINDOW)
        my_font = pygame.font.Font(FONT_3, 120)
        text_surface = my_font.render('WUMPUS WORLD', False, RED)
        while self.running_menu:
            self.clicked = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running_menu = False
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.clicked = True

            # re-draw window
            screen.blit(self.bg, (0, 0))
            if self.status != "START_MENU":
                self.btnBackHome.process()
            if self.status == "START_MENU":
                screen.blit(text_surface, ((WIDTH - text_surface.get_width()) // 2, 30))
                self.btnStart.process()
                self.btnQuit.process()
            elif self.status == "CHOOSE_MAP":
                self.btnMapRand.process()
                self.btnAdvance.process()
                self.btnComparison.process()
            elif self.status == "RUN_GAME":
                self.running_menu = False
                self.running = True
                self.pause = False
                MARGIN['LEFT'] = 0
                self.board = Board(self.map_name, self.result_name)
                self.initBtnEndGame()
                self.run()

            pygame.display.flip()
            clock.tick(300)
            # ----------------------------
