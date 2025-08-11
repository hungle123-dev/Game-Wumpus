from Run.Action import Action
from Run.Base import Base
from Run.Cell import Cell
from Run.CellType import CellType
from Run.KnowledgeBase import KnowledgeBase


class Solution(Base):
    def __init__(self, input_file, output_file):
        super().__init__(output_file)
        self.KB = KnowledgeBase()
        self.game_ended = False  # NEW: Flag to track if game has ended
        self.is_advance_mode = "advance.txt" in input_file  # NEW: Check if advance mode
        self.read_map(input_file)

    def KB_logic_1(self, cell: Cell):
        # BASE KNOWLEDGE: (P ^ -W) v (-P ^ W)
        # P ^ -W
        sign_pit = '-'
        if cell.exist_Entity(1):
            self.KB.add_clause([cell.get_literal(CellType.WUMPUS, '-')])
            sign_pit = '+'
        self.KB.add_clause([cell.get_literal(CellType.PIT, sign_pit)])
        # -P ^ W
        sign_wumpus = '-'
        if cell.exist_Entity(2):
            self.KB.add_clause([cell.get_literal(CellType.PIT, '-')])
            sign_wumpus = '+'
        self.KB.add_clause([cell.get_literal(CellType.WUMPUS, sign_wumpus)])

        # Check the above constraint.
        if sign_pit == sign_wumpus == '+':
            raise TypeError('Pit and Wumpus can not appear at the same cell.')

    def KB_logic_2(self, cell: Cell):
        # PL: Breeze?
        if cell.exist_Entity(3):
            self.KB.add_clause([cell.get_literal(CellType.BREEZE, '+')])
        else:
            self.KB.add_clause([cell.get_literal(CellType.BREEZE, '-')])

        # PL: Stench?
        if cell.exist_Entity(4):
            self.KB.add_clause([cell.get_literal(CellType.STENCH, '+')])
        else:
            self.KB.add_clause([cell.get_literal(CellType.STENCH, '-')])

    def KB_logic_3(self, cell: Cell, neighbor_cells: list[Cell]):
        # If this cell have Breeze
        # BASE KNOWLEDGE: B <=> Pa v Pb v Pc v Pd
        if cell.exist_Entity(3):
            # (B => Pa v Pb v Pc v Pd) <=> (-B v Pa v Pb v Pc v Pd)
            clause = [neighbor.get_literal(CellType.PIT, '+') for neighbor in neighbor_cells]
            clause.append(cell.get_literal(CellType.BREEZE, '-'))
            self.KB.add_clause(clause)

            # (Pa v Pb v Pc v Pd => B) <=> ((-Pa ^ -Pb ^ -Pc ^ -Pd) v B)
            for neighbor in neighbor_cells:
                self.KB.add_clause([cell.get_literal(CellType.BREEZE, '+'), neighbor.get_literal(CellType.PIT, '-')])

        else:
            # This cell no have Breeze
            # BASE KNOWLEDGE: -Pa ^ -Pb ^ -Pc ^ -Pd
            for neighbor in neighbor_cells:
                self.KB.add_clause([neighbor.get_literal(CellType.PIT, '-')])

    def KB_logic_4(self, cell: Cell, neighbor_cells: list[Cell]):
        # If this cell have Stench
        # BASE KNOWLEDGE: S <=> Wa v Wb v Wc v Wd
        if cell.exist_Entity(4):
            # (S => Wa v Wb v Wc v Wd) <=> (-S v Wa v Wb v Wc v Wd)
            clause = [neighbor.get_literal(CellType.WUMPUS, '+') for neighbor in neighbor_cells]
            clause.append(cell.get_literal(CellType.STENCH, '-'))
            self.KB.add_clause(clause)

            # (Wa v Wb v Wc v Wd => S) <=> ((-Wa ^ -Wb ^ -Wc ^ -Wd) v S)
            for neighbor in neighbor_cells:
                self.KB.add_clause([cell.get_literal(CellType.STENCH, '+'), neighbor.get_literal(CellType.WUMPUS, '-')])
        else:
            # This cell no have Stench
            # BASE KNOWLEDGE: -Wa ^ -Wb ^ -Wc ^ -Wd
            for neighbor in neighbor_cells:
                self.KB.add_clause([neighbor.get_literal(CellType.WUMPUS, '-')])

    def add_KB(self, cell: Cell):
        neighbor_cells: list[Cell] = cell.get_adj_cell(self.cell_matrix)

        self.KB_logic_1(cell)
        self.KB_logic_2(cell)
        self.KB_logic_3(cell, neighbor_cells)
        self.KB_logic_4(cell, neighbor_cells)

        self.append_event_to_output_file(str(self.KB.KB))

    def top_condition(self):
        # if current step of agent have wumpus => game is finish, agent dies
        if self.agent_cell.exist_Entity(2):
            self.add_action(Action.BE_EATEN_BY_WUMPUS)
            return False

        # if current step of agent have pit => game is finish, agent dies
        if self.agent_cell.exist_Entity(1):
            self.add_action(Action.FALL_INTO_PIT)
            return False

        # if current step of agent have gold => agent grab gold
        if self.agent_cell.exist_Entity(0):
            self.add_action(Action.GRAB_GOLD)
            # delete gold
            self.agent_cell.grab_gold()

        # if current step of agent feel Stench => agent perceives Stench
        if self.agent_cell.exist_Entity(4):
            self.add_action(Action.PERCEIVE_STENCH)
            
            # NEW: In advance mode with moving Wumpus, aggressively shoot at threats
            if self.is_advance_mode:
                self.append_event_to_output_file("ADVANCE MODE: Auto-defending against moving Wumpus!")
                adj_cells = self.agent_cell.get_adj_cell(self.cell_matrix)
                shots_fired = 0
                
                for adj_cell in adj_cells:
                    # Skip if this is where we came from
                    if adj_cell == self.agent_cell.parent:
                        continue
                        
                    # Skip if we know it's safe (explored and no Wumpus)
                    if adj_cell.is_explored() and not adj_cell.exist_Entity(2):
                        continue
                        
                    # Shoot at unexplored cells or suspected Wumpus locations
                    self.turn_to(adj_cell)
                    self.add_action(Action.SHOOT)
                    shots_fired += 1
                    
                    # REMOVED: All prediction logic for KILL_WUMPUS
                    # Hit detection is now 100% handled at shoot time in Board.py
                    
                    # Limit shots to prevent infinite loop
                    if shots_fired >= 4:
                        break
                        
                self.append_event_to_output_file(f"Fired {shots_fired} defensive shots")

        # if current step of agent feel Breeze => agent perceives Breeze
        if self.agent_cell.exist_Entity(3):
            self.add_action(Action.PERCEIVE_BREEZE)

        # mark this cell explored and percepts to the KB
        if not self.agent_cell.is_explored():
            self.agent_cell.explore()
            self.add_KB(self.agent_cell)

    def backtracking_search(self):
        # NEW: Check game ended flag first
        if self.game_ended:
            return False
            
        self.top_condition()

        # NEW: Check if agent reached exit door (0,0) - END GAME IMMEDIATELY
        if self.agent_cell.map_pos[0] == 0 and self.agent_cell.map_pos[1] == 0:
            self.add_action(Action.CLIMB_OUT_OF_THE_CAVE)
            self.game_ended = True  # Set flag to prevent further processing
            return False  # End game immediately when reaching (0,0)

        # Initialize valid_adj_cell_list.
        valid_adj_cell_list = self.agent_cell.get_adj_cell(self.cell_matrix)

        temp_adj_cell_list = []
        # Delete node parent in list cell (Because from parent -> this cell => dont move again)
        if self.agent_cell.parent in valid_adj_cell_list:
            valid_adj_cell_list.remove(self.agent_cell.parent)

        # Store previous agent's cell.
        pre_agent_cell = self.agent_cell

        if not self.agent_cell.check():
            # if this cell have breeze or stench
            valid_adj_cell: Cell
            temp_adj_cell_list = []
            # delete cell have pit in next step
            for valid_adj_cell in valid_adj_cell_list:
                if valid_adj_cell.is_explored() and valid_adj_cell.exist_Entity(1):
                    temp_adj_cell_list.append(valid_adj_cell)

            for adj_cell in temp_adj_cell_list:
                valid_adj_cell_list.remove(adj_cell)

            temp_adj_cell_list = []
            if self.agent_cell.exist_Entity(4):
                # this cell is stench => check adj have wumpus or infer this
                for valid_adj_cell in valid_adj_cell_list:
                    self.append_event_to_output_file('Infer: ' + str(valid_adj_cell.map_pos))
                    self.turn_to(valid_adj_cell)

                    # Infer Wumpus
                    self.add_action(Action.INFER_WUMPUS)
                    not_alpha = [[valid_adj_cell.get_literal(CellType.WUMPUS, '-')]]
                    have_wumpus = self.KB.infer(not_alpha)

                    # if this cell have wumpus
                    if have_wumpus:
                        # Detect Wumpus
                        self.add_action(Action.DETECT_WUMPUS)

                        # Shoot this Wumpus
                        self.add_action(Action.SHOOT)
                        # REMOVED: No longer pre-generate KILL_WUMPUS action
                        # Hit detection now happens at actual shoot time in Board.py
                        valid_adj_cell.kill_wumpus(self.cell_matrix, self.KB)
                        self.append_event_to_output_file('KB: ' + str(self.KB.KB))
                    else:
                        # Dont can detect exact wumpus
                        self.add_action(Action.INFER_NOT_WUMPUS)
                        # Try to detect this cell don't have wumpus
                        not_alpha = [[valid_adj_cell.get_literal(CellType.WUMPUS, '+')]]
                        have_no_wumpus = self.KB.infer(not_alpha)

                        # If we can infer no Wumpus
                        if have_no_wumpus:
                            self.add_action(Action.DETECT_NO_WUMPUS)
                        else:
                            # Don't know exact => don't try move to this cell
                            if valid_adj_cell not in temp_adj_cell_list:
                                temp_adj_cell_list.append(valid_adj_cell)

            # if this cell until have stench => try to shoot all valid cell around this cell
            if self.agent_cell.exist_Entity(4):
                # first step: find all adj_cell don't know what is this
                adj_cell_list = self.agent_cell.get_adj_cell(self.cell_matrix)
                if self.agent_cell.parent in adj_cell_list:
                    adj_cell_list.remove(self.agent_cell.parent)

                explored_cell_list = []
                for adj_cell in adj_cell_list:
                    if adj_cell.is_explored():
                        explored_cell_list.append(adj_cell)
                for explored_cell in explored_cell_list:
                    adj_cell_list.remove(explored_cell)

                # second step: try shoot until don't have stench
                adj_cell: Cell
                for adj_cell in adj_cell_list:
                    self.append_event_to_output_file('Try: ' + str(adj_cell.map_pos))
                    self.turn_to(adj_cell)
                    self.add_action(Action.SHOOT)
                    # REMOVED: No longer pre-generate KILL_WUMPUS action
                    # Hit detection now happens at actual shoot time in Board.py
                    if adj_cell.exist_Entity(2):
                        # this cell have wumpus - update KB but don't assume kill
                        adj_cell.kill_wumpus(self.cell_matrix, self.KB)
                        self.append_event_to_output_file('KB: ' + str(self.KB.KB))

                    if not self.agent_cell.exist_Entity(4):
                        # don't have stench
                        self.agent_cell.update_child([adj_cell])
                        break

            # if this cell have Breeze => try to infer Pit
            if self.agent_cell.exist_Entity(3):
                for valid_adj_cell in valid_adj_cell_list:
                    self.append_event_to_output_file('Infer: ' + str(valid_adj_cell.map_pos))
                    self.turn_to(valid_adj_cell)

                    # infer pit
                    self.add_action(Action.INFER_PIT)
                    not_alpha = [[valid_adj_cell.get_literal(CellType.PIT, '-')]]
                    have_pit = self.KB.infer(not_alpha)

                    # if we can infer pit
                    if have_pit:
                        # detect pit
                        self.add_action(Action.DETECT_PIT)
                        valid_adj_cell.explore()
                        self.add_KB(valid_adj_cell)
                        valid_adj_cell.update_parent(valid_adj_cell)
                        temp_adj_cell_list.append(valid_adj_cell)
                    else:
                        # Infer not Pit.
                        self.add_action(Action.INFER_NOT_PIT)
                        not_alpha = [[valid_adj_cell.get_literal(CellType.PIT, '+')]]
                        have_no_pit = self.KB.infer(not_alpha)

                        # If we can infer not Pit.
                        if have_no_pit:
                            # Detect no Pit.
                            self.add_action(Action.DETECT_NO_PIT)

                        # If we can not infer not Pit.
                        else:
                            # Discard these cells from the valid_adj_cell_list.
                            temp_adj_cell_list.append(valid_adj_cell)

        temp_adj_cell_list = list(set(temp_adj_cell_list))
        # delete all cell not valid
        for adj_cell in temp_adj_cell_list:
            valid_adj_cell_list.remove(adj_cell)

        # try move to all valid cell with backtracking
        self.agent_cell.update_child(valid_adj_cell_list)
        for new_cell in self.agent_cell.child:
            # NEW: Check if game already ended
            if self.game_ended:
                return False
                
            self.move_to(new_cell)
            self.append_event_to_output_file('Move to: ' + str(self.agent_cell.map_pos))

            # NEW: Check if we reached (0,0) after moving - STOP IMMEDIATELY!
            if self.agent_cell.map_pos[0] == 0 and self.agent_cell.map_pos[1] == 0:
                self.add_action(Action.CLIMB_OUT_OF_THE_CAVE)
                self.game_ended = True  # Set flag
                return False  # End game immediately, DON'T continue to backtrack!

            search_result = self.backtracking_search()
            if not search_result:
                return False  # Propagate the end game signal

            # NEW: Only backtrack if game hasn't ended
            if not self.game_ended:
                self.move_to(pre_agent_cell)
                self.append_event_to_output_file('Backtrack: ' + str(pre_agent_cell.map_pos))

        return True

    def navigate_to_exit(self):
        """Navigate agent back to exit door at (0,0) using explored safe cells"""
        target_pos = [0, 0]  # Exit door position
        current_pos = self.agent_cell.map_pos
        
        # If already at exit, no need to navigate
        if current_pos == target_pos:
            return
        
        # Limit attempts to prevent infinite loops
        max_attempts = 50
        attempts = 0
        
        while self.agent_cell.map_pos != target_pos and attempts < max_attempts:
            attempts += 1
            
            # Find the target cell
            target_cell = None
            for row in self.cell_matrix:
                for cell in row:
                    if cell.map_pos == target_pos:
                        target_cell = cell
                        break
                if target_cell:
                    break
            
            if target_cell and target_cell.is_explored():
                # Target is already explored and safe, move directly
                self.move_to(target_cell)
                break
            else:
                # Target not explored yet, find closest safe explored cell
                adj_cells = self.agent_cell.get_adj_cell(self.cell_matrix)
                
                # Find closest SAFE cell to target
                best_cell = None
                min_distance = float('inf')
                
                for adj_cell in adj_cells:
                    # Check if cell is safe (explored and no pit/wumpus)
                    if (adj_cell.is_explored() and 
                        not adj_cell.exist_Entity(1) and  # No pit
                        not adj_cell.exist_Entity(2)):    # No wumpus
                        
                        # Calculate Manhattan distance to target
                        distance = abs(adj_cell.map_pos[0] - target_pos[0]) + abs(adj_cell.map_pos[1] - target_pos[1])
                        if distance < min_distance:
                            min_distance = distance
                            best_cell = adj_cell
                
                if best_cell:
                    self.move_to(best_cell)
                    # Continue in the loop (not recursive call)
                else:
                    # No safe path found, break to avoid infinite loop
                    break
        
        # Final check: if not at target after all attempts, try direct move if target is explored
        if self.agent_cell.map_pos != target_pos:
            target_cell = self.cell_matrix[target_pos[0]][target_pos[1]]
            if target_cell.is_explored():
                self.move_to(target_cell)

    def solve(self):
        # rest file
        file = open(self.output_filename, 'w')
        file.close()

        # Main game loop - agent explores until reaching (0,0) or completing objectives
        game_result = self.backtracking_search()
        
        # If game didn't end by reaching (0,0), check for victory conditions
        if game_result is not False:
            victory = True
            for row in self.cell_matrix:
                col: Cell
                for col in row:
                    # if until have gold or wumpus
                    if col.exist_Entity(0) or col.exist_Entity(2):
                        victory = False
                        break

            if victory:
                self.add_action(Action.KILL_ALL_WUMPUS_AND_GRAB_ALL_FOOD)

        # NOTE: No need for additional climb logic here
        # Game ends immediately when agent reaches (0,0) in backtracking_search()

        return self.action_list
