import pygame
from constants import *


class AgentKnowledgeDisplay:
    """Display agent's knowledge and inferred information about the world"""
    
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pygame.font.Font(FONT_2, 16)
        self.small_font = pygame.font.Font(FONT_2, 12)
        self.title_font = pygame.font.Font(FONT_2, 18)
        
        # Action history scrolling
        self.scroll_position = 0
        self.max_history_display = 15
        
    def scroll_up(self):
        self.scroll_position = max(0, self.scroll_position - 1)
        
    def scroll_down(self):
        self.scroll_position += 1
        
    def draw(self, screen, agent, board, current_action=None, action_history=None):
        """Draw comprehensive agent knowledge panel with action tracking"""
        # Background
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
        # Split into two columns
        left_width = self.width // 2 - 15
        right_x = self.x + left_width + 20
        
        # LEFT COLUMN - Agent Status and World Knowledge
        # Title
        title = self.title_font.render("AGENT STATUS", True, BLACK)
        screen.blit(title, (self.x + 10, self.y + 5))
        
        y_offset = 35
        
        # Agent status
        status_text = [
            f"Position: ({agent.row}, {agent.col})",
            f"Direction: {agent.direction}",
            f"Has Gold: {'Yes' if agent.has_gold else 'No'}",
            f"Score: {board.score}",
        ]
        
        for text in status_text:
            surface = self.small_font.render(text, True, BLACK)
            screen.blit(surface, (self.x + 10, self.y + y_offset))
            y_offset += 18
            
        # Current percepts
        y_offset += 15
        percept_title = self.font.render("CURRENT PERCEPTS:", True, RED)
        screen.blit(percept_title, (self.x + 10, self.y + y_offset))
        y_offset += 20
        
        percepts = self._get_current_percepts(agent, board)
        for percept in percepts:
            surface = self.small_font.render(percept, True, BLUE)
            screen.blit(surface, (self.x + 10, self.y + y_offset))
            y_offset += 16
            
        # World knowledge
        y_offset += 15
        info_title = self.font.render("WORLD KNOWLEDGE:", True, RED)
        screen.blit(info_title, (self.x + 10, self.y + y_offset))
        y_offset += 20
        
        info_items = [
            f"Wumpus remaining: {len(board.Wumpus)}",
            f"Pits detected: {len(board.Pits)}",
            f"Gold remaining: {len(board.Golds)}",
            f"Map size: {board.matrix_dimension[0]}x{board.matrix_dimension[1]}",
        ]
        
        for item in info_items:
            surface = self.small_font.render(item, True, BLACK)
            screen.blit(surface, (self.x + 10, self.y + y_offset))
            y_offset += 16
            
        # RIGHT COLUMN - Current Action and Action History
        action_title = self.title_font.render("ACTION TRACKING", True, BLACK)
        screen.blit(action_title, (right_x, self.y + 5))
        
        right_y_offset = 35
        
        # Current action
        if current_action:
            curr_title = self.font.render("CURRENT ACTION:", True, GREEN)
            screen.blit(curr_title, (right_x, self.y + right_y_offset))
            right_y_offset += 20
            
            curr_action_display = current_action.replace("_", " ")
            action_surface = self.small_font.render(curr_action_display, True, GREEN)
            screen.blit(action_surface, (right_x, self.y + right_y_offset))
            right_y_offset += 25
        
        # Action history  
        history_title = self.font.render("ACTION HISTORY:", True, RED)
        screen.blit(history_title, (right_x, self.y + right_y_offset))
        right_y_offset += 20
        
        if action_history:
            # Calculate which actions to show based on scroll
            start_idx = max(0, len(action_history) - self.max_history_display - self.scroll_position)
            end_idx = len(action_history) - self.scroll_position
            visible_actions = action_history[start_idx:end_idx]
            
            for i, action in enumerate(visible_actions):
                if right_y_offset + 16 > self.y + self.height - 10:
                    break
                    
                # Number the actions
                action_text = f"{start_idx + i + 1:2d}. {action}"
                action_surface = self.small_font.render(action_text, True, BLACK)
                screen.blit(action_surface, (right_x, self.y + right_y_offset))
                right_y_offset += 16
                
            # Show scroll indicator
            if len(action_history) > self.max_history_display:
                scroll_text = f"(Scroll: {self.scroll_position})"
                scroll_surface = self.small_font.render(scroll_text, True, GREY)
                screen.blit(scroll_surface, (right_x, self.y + self.height - 25))
        else:
            no_history = self.small_font.render("No actions yet", True, GREY)
            screen.blit(no_history, (right_x, self.y + right_y_offset))
            
        # Draw separator line
        pygame.draw.line(screen, GREY, 
                        (self.x + left_width + 10, self.y + 10),
                        (self.x + left_width + 10, self.y + self.height - 10), 2)
        
    def _get_current_percepts(self, agent, board):
        """Get current percepts at agent's position"""
        percepts = []
        
        # Check for stench
        for stench in board.Stenches:
            if stench.row == agent.row and stench.col == agent.col:
                percepts.append("• STENCH")
                break
                
        # Check for breeze  
        for breeze in board.Breezes:
            if breeze.row == agent.row and breeze.col == agent.col:
                percepts.append("• BREEZE")
                break
                
        # Check for gold
        for gold in board.Golds:
            if gold.row == agent.row and gold.col == agent.col:
                percepts.append("• GLITTER")
                break
                
        if not percepts:
            percepts.append("• None")
            
        return percepts
