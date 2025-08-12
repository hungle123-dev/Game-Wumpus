import pygame

import utils
from Entity.Agent import Agent
from Entity.AgentKnowledgeDisplay import AgentKnowledgeDisplay
from Entity.Arrow import Arrow
from Entity.Breeze import Breeze
from Entity.Cell import Cell
from Entity.ConsoleVisualizer import console_viz
from Entity.Door import Door
from Entity.Gold import Gold

from Entity.Pit import Pit
from Entity.Stench import Stench
from Entity.ViewImageAction import ImageAction
from Entity.Wall import Wall
from Entity.Wumpus import Wumpus
from Run.Action import Action
from Run.HybridAgent import HybridAgent
from Run.RandomAgentSimple import RandomAgentBaseline
from constants import *

DDX = [(0, 1), (0, -1), (-1, 0), (1, 0)]


def remove_entity(entity, pos):
    flag = -1
    for idx, e in enumerate(entity):
        if e.getRC() == pos:
            flag = idx
            break
    if flag != -1:
        entity.pop(flag)


class Board(object):
    def __init__(self, filename="map1.txt", outputfile="result1.txt"):
        self.delay = False
        self.score = 0
        self.end_action = None
        self.spacing = SPACING_CELL
        self.cell_dimension = CELL_SIZE
        self.matrix_dimension = (NUMBER_CELL, NUMBER_CELL)
        self.width = ((self.cell_dimension * self.matrix_dimension[1]) + (self.spacing * (self.matrix_dimension[1] + 1))
                      + MARGIN["LEFT"])
        self.height = (
                (self.cell_dimension * self.matrix_dimension[0]) + (self.spacing * (self.matrix_dimension[0] + 1))
                + MARGIN['TOP'])

        self.map = None
        self.current_action = None
        self.action_history = []
        self.game_won = False  # NEW: Flag to track if game is won
        # AgentKnowledgeDisplay will be initialized after MESSAGE_WINDOW is set
        self.knowledge_display = None
        self.image_action = None
        self.change_animation = True
        # other position entity
        self.Walls = []
        self.Cells = []
        self.Golds = []
        self.Pits = []
        self.Wumpus = []
        self.Agent = None
        self.Door = None
        self.Breezes = []
        self.Stenches = []
        self.Arrow = None
        # AGENT SELECTION: Change this to switch between agents
        use_random_agent = False  # Set to True for Random Agent, False for Hybrid Agent
        
        if use_random_agent:
            # Random Agent Baseline for comparison
            self.action_list = RandomAgentBaseline(f'{ROOT_INPUT}{filename}',
                                        f'{ROOT_OUTPUT}{outputfile}').solve()
            print("🎲 Using Random Agent Baseline")
        else:
            # Hybrid Intelligent Agent
            self.action_list = HybridAgent(f'{ROOT_INPUT}{filename}',
                                        f'{ROOT_OUTPUT}{outputfile}').solve()
            print("🧠 Using Hybrid Intelligent Agent")

        self.createBoardGame(filename)

        MESSAGE_WINDOW['TOP'] = MARGIN['TOP'] + self.spacing
        MESSAGE_WINDOW['BOTTOM'] = HEIGHT - MARGIN['TOP'] - self.spacing
        MESSAGE_WINDOW['LEFT'] = self.width + MARGIN['LEFT'] - self.spacing
        
        # Now initialize AgentKnowledgeDisplay with correct MESSAGE_WINDOW values
        self.knowledge_display = AgentKnowledgeDisplay(
            MESSAGE_WINDOW['LEFT'] + 10, 
            MESSAGE_WINDOW['TOP'] + 10, 
            WIDTH - MESSAGE_WINDOW['LEFT'] - 30, 
            HEIGHT - MESSAGE_WINDOW['TOP'] - 115
        )
        
        # Print initial game state to console
        # console_viz.print_game_state(self, "GAME_START")  # Đã tắt console output

    def createBoardGame(self, filename):
        N, _map = utils.Utils.readMapInFile(filename, self.cell_dimension, self.spacing)
        self.matrix_dimension = (N, N)
        self.map = _map

        for row in range(N):
            for col in range(N):
                cell = self.map[row][col]
                # create floor game
                self.Cells.append(Cell(row, col, 1) if GOLD in cell else Cell(row, col))
                self.Walls.append(Wall(row, col))
                if GOLD in cell:
                    self.Golds.append(Gold(row, col))
                if AGENT in cell and self.Agent is None:
                    self.Agent = Agent(row, col, N)
                    # NEW: Don't create Door at agent position anymore
                if PIT in cell:
                    self.Pits.append(Pit(row, col))
                if WUMPUS in cell:
                    self.Wumpus.append(Wumpus(row, col))
                if BREEZE in cell:
                    self.Breezes.append(Breeze(row, col))
                if STENCH in cell:
                    self.Stenches.append(Stench(row, col))
        
        # NEW: Always create Door at (0,0) - the exit position
        self.Door = Door(0, 0)

    def draw(self, screen: pygame):
        pygame.draw.rect(screen, PURPLE, pygame.Rect(self.width + MARGIN['LEFT'] - self.spacing, MARGIN['TOP'] +
                                                     self.spacing, WIDTH - self.width,
                                                     HEIGHT - MARGIN['TOP'] * 2 - self.spacing * 2))
        for cell in self.Cells:
            cell.draw(screen)
        for stench in self.Stenches:
            stench.draw(screen)
        for breeze in self.Breezes:
            breeze.draw(screen)
        for gold in self.Golds:
            gold.draw(screen)
        for pit in self.Pits:
            pit.draw(screen)
        for wum in self.Wumpus:
            wum.draw(screen)
        for wall in self.Walls:
            wall.draw(screen)

        self.Door.draw(screen)
        self.Agent.draw(screen)
        if self.Arrow is not None:
            self.Arrow.draw(screen)

        # draw score
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        text_surface = my_font.render('Score: {Score}'.format(Score=self.score), False, RED)
        screen.blit(text_surface, (WIDTH - 200 - text_surface.get_width() // 2, 0))

        if not self.change_animation and self.end_action is not None:
            self.handle_end_game(screen)

        # Draw image action if available
        if self.image_action is not None and self.change_animation:
            self.image_action.draw(screen)

        # Draw agent knowledge display (now replaces ListView and Message)
        if self.knowledge_display is not None:
            self.knowledge_display.draw(screen, self.Agent, self, self.current_action, self.action_history)

        remove_entity(self.Walls, self.Agent.getRC())

    def scroll_up(self):
        # Now handled by knowledge display
        if self.knowledge_display is not None:
            self.knowledge_display.scroll_up()

    def scroll_down(self):
        # Now handled by knowledge display  
        if self.knowledge_display is not None:
            self.knowledge_display.scroll_down()

    def handle_end_game(self, screen):
        my_font = pygame.font.Font(FONT_1, 100)
        if self.end_action == Action.FALL_INTO_PIT:
            text_surface = my_font.render('DEFEAT', False, RED)
            screen.blit(text_surface, (WIDTH - 400, HEIGHT - 270))
        elif self.end_action == Action.CLIMB_OUT_OF_THE_CAVE:
            text_surface = my_font.render('DONE !', False, YELLOW)
            screen.blit(text_surface, (WIDTH - 390, HEIGHT - 270))

    def get_neighborhood_wumpus(self, row, col):
        result = []
        for (d_r, d_c) in DDX:
            new_row = d_r + row
            new_col = d_c + col
            for stench in self.Stenches:
                if stench.getRC() == [new_row, new_col]:
                    result.append(stench)

        return result

    def get_neighborhood_stench(self, row, col):
        result = []
        for (d_r, d_c) in DDX:
            new_row = d_r + row
            new_col = d_c + col
            for wum in self.Wumpus:
                if wum.getRC() == [new_row, new_col]:
                    result.append(wum)

        return result

    def kill_wumpus(self):
        pos_to = self.Agent.getNextPos()
        # remove_entity(self.Walls, pos_to)
        remove_entity(self.Wumpus, pos_to)
        stench_around = self.get_neighborhood_wumpus(pos_to[0], pos_to[1])

        for stench in stench_around:
            pos = stench.getRC()
            if len(self.get_neighborhood_stench(pos[0], pos[1])) <= 0:
                remove_entity(self.Stenches, pos)

    def move(self):
        # NEW: If game is won, don't process any more moves
        if self.game_won:
            return False
            
        self.delay = False
        self.Arrow = None
        self.message = None

        if len(self.action_list) == 0:
            # No more actions - game is finishing
            self.change_animation = False
            return False

        action = self.action_list.pop(0)
        self.end_action = action

        if action == Action.TURN_RIGHT:
            self.Agent.turn_to(Action.TURN_RIGHT)
            self.score += POINT["TURN_RIGHT"]
        elif action == Action.TURN_LEFT:
            self.Agent.turn_to(Action.TURN_LEFT)
            self.score += POINT["TURN_LEFT"]
        elif action == Action.TURN_UP:
            self.Agent.turn_to(Action.TURN_UP)
            self.score += POINT["TURN_UP"]
        elif action == Action.TURN_DOWN:
            self.Agent.turn_to(Action.TURN_DOWN)
            self.score += POINT["TURN_DOWN"]

        # Move forward action
        elif action == Action.MOVE_FORWARD:
            self.Agent.move_forward()
            self.score += POINT["MOVE_FORWARD"]
            
            # CRITICAL: Check collision with Wumpus after moving
            agent_pos = (self.Agent.row, self.Agent.col)
            for wumpus in self.Wumpus:
                if wumpus.row == agent_pos[0] and wumpus.col == agent_pos[1]:
                    # Agent collided with Wumpus - DEATH!
                    print(f"💀 COLLISION! Agent at {agent_pos} collided with Wumpus!")
                    self.score += POINT["DYING"]  # Heavy penalty (-1000)
                    self.end_action = Action.BE_EATEN_BY_WUMPUS  # Set death action
                    return False  # End game immediately
            
            # Check collision with Pit after moving
            for pit in self.Pits:
                if pit.row == agent_pos[0] and pit.col == agent_pos[1]:
                    # Agent fell into pit - DEATH!
                    print(f"💀 FALL! Agent at {agent_pos} fell into pit!")
                    self.score += POINT["DYING"]  # Heavy penalty (-1000)
                    self.end_action = Action.FALL_INTO_PIT  # Set death action
                    return False  # End game immediately
            
            # NEW: Check if agent reached exit door (0,0) after moving
            if self.Agent.row == 0 and self.Agent.col == 0:
                # Agent reached exit door - STOP EVERYTHING!
                self.game_won = True  # Set won flag
                self.action_list.clear()  # Clear all remaining actions
                self.change_animation = False  # Stop animation
                self.end_action = Action.CLIMB_OUT_OF_THE_CAVE  # Set end action
                print("🎉 GAME WON! Agent reached exit door (0,0)")  # Debug
                return False  # End game immediately

        # Climb out the cave
        elif action == Action.CLIMB_OUT_OF_THE_CAVE:
            if self.Agent.has_gold:
                self.score += POINT["CLIMB_WITH_GOLD"]
            else:
                self.score += POINT["CLIMB_WITHOUT_GOLD"]

        # grab gold action
        elif action == Action.GRAB_GOLD:
            pos = self.Agent.getRC()
            remove_entity(self.Golds, pos)
            self.Agent.has_gold = True
            self.score += POINT["PICK_GOLD"]
            self.delay = True

        # infer pit or wumpus
        elif action == Action.DETECT_PIT or action == Action.DETECT_WUMPUS:
            pos = self.Agent.getNextPos()
            remove_entity(self.Walls, pos)

        # shoot
        elif action == Action.SHOOT:
            pos_to = self.Agent.getNextPos()
            pos_from = self.Agent.getRC()
            self.Arrow = Arrow(pos_from, pos_to)
            self.score += POINT["SHOOT"]
            
            # COMPREHENSIVE FIX: Check actual Wumpus collision at shoot time
            wumpus_hit = False
            
            for wumpus in self.Wumpus[:]:  # Use slice copy to avoid modification during iteration
                if wumpus.row == pos_to[0] and wumpus.col == pos_to[1]:
                    # Actually hit a Wumpus at current position!
                    self.Wumpus.remove(wumpus)  # Remove from actual list
                    wumpus_hit = True
                    break
            
            if wumpus_hit:
                # Update stenches after killing Wumpus - comprehensive update
                self.update_stenches()

        # kill wumpus (legacy - now handled in SHOOT action)
        elif action == Action.KILL_WUMPUS:
            # This should not be reached with new logic, but keep for compatibility
            self.kill_wumpus()
            self.delay = True

        # kill wumpus (legacy - now handled in SHOOT action)
        elif action == Action.KILL_WUMPUS:
            # This should not be reached with new logic, but keep for compatibility
            self.kill_wumpus()
            self.delay = True

        # fall into pit
        elif action == Action.FALL_INTO_PIT:
            self.score += POINT["DYING"]

        # Update action tracking
        if action:
            # Handle both Action objects and strings for compatibility
            if hasattr(action, 'name'):
                self.current_action = action.name
                action_display = action.name.replace("_", " ")
            else:
                # For string actions (fallback)
                self.current_action = str(action)
                action_display = str(action).replace("_", " ")
            
            self.action_history.append(action_display)
            
            # Limit action history to prevent memory issues  
            if len(self.action_history) > 50:
                self.action_history.pop(0)
        
        # Keep image action for visual feedback
        if self.image_action is not None and self.change_animation:
            # This will be drawn separately if needed
            pass
        self.image_action = ImageAction(action)
        
        # Print current game state to console
        # console_viz.print_game_state(self, action.name)  # Đã tắt console output

        return True
    
    def is_valid_cell(self, row, col):
        # Kiểm tra có nằm trong map không
        if row < 0 or row >= self.matrix_dimension[0] or col < 0 or col >= self.matrix_dimension[1]:
            return False
        # Kiểm tra có phải tường không
        for wall in self.Walls:
            if wall.row == row and wall.col == col:
                return False
        # Kiểm tra có phải hố không
        for pit in self.Pits:
            if pit.row == row and pit.col == col:
                return False
        # Nếu không phải tường, không phải hố, không ra ngoài map thì hợp lệ
        return True
    
    def update_stenches(self):
        self.Stenches.clear()
        for wumpus in self.Wumpus:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                row = wumpus.row + dx
                col = wumpus.col + dy
                # Kiểm tra hợp lệ, không ra ngoài map, không trùng tường
                if 0 <= row < self.matrix_dimension[0] and 0 <= col < self.matrix_dimension[1]:
                    is_wall = any(wall.row == row and wall.col == col for wall in self.Walls)
                    if not is_wall:
                        self.Stenches.append(Stench(row, col))
