import pygame
from settings import *
from player import Player

class Upgrade:
    def __init__(self, player:Player) -> None:
        # General Setup
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.attribute_names = list(self.player.stats.keys())
        self.max_col = len(self.attribute_names)
        self.max_row = 1 # pending update to include more rows
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        
        # Stat Box Dimensions
        dimensions = self.display_surface.get_size()
        self.height =  dimensions[1] * 0.8
        self.width = dimensions[0] // self.max_col
        self.create_items()
        
        # Selection
        self.selected_row = 0
        self.selected_col = 0
        self.cooldown_time = 15
        self.cooldown = 0
        
        
        
    def input(self):
        keys = pygame.key.get_pressed()
        if self.cooldown <= 0:
            if keys[pygame.K_RIGHT]:
                self.selected_col += 1
                self.selected_col %= self.max_col
                self.cooldown = self.cooldown_time
            elif keys[pygame.K_LEFT]:
                self.selected_col -= 1
                self.selected_col %= self.max_col
                self.cooldown = self.cooldown_time
            elif keys[pygame.K_UP]:
                self.selected_row += 1
                self.selected_row %= self.max_row
                self.cooldown = self.cooldown_time
            elif keys[pygame.K_DOWN]:
                self.selected_row -= 1
                self.selected_row %= self.max_row
                self.cooldown = self.cooldown_time
            elif keys[pygame.K_SPACE]:
                self.player.upgrade_stat(self.attribute_names[self.selected_col])
                self.cooldown = self.cooldown_time
        else:

            self.cooldown -= 1
        
    def create_items(self):
        self.item_list = []
        dimensions = self.display_surface.get_size()
        item_width = dimensions[0] // (self.max_col - 1)
        item_height =  dimensions[1] * 0.8
        gap_width = item_width // (self.max_col+1)
        gap_height = 10
        mid_x = dimensions[0]//2
        
        y1 = dimensions[1] // 10
        y2 = y1 + item_height
        
        self.item_index_order = [-2, 2, -1, 1, 0]
        
        
        # Back left item
        x1 = mid_x-(7*item_width//4)
        x2 = x1 + item_width - gap_width
        y_gap = 2*gap_height
        self.item_list.append(MenuItem(x1, y1+y_gap, x2, y2-y_gap, False, self.font))
        
        # Back right item
        x1 = mid_x+(3*item_width//4)
        x2 = x1 + item_width - gap_width
        y_gap = gap_height * 2
        self.item_list.append(MenuItem(x1, y1+y_gap, x2, y2-y_gap, False, self.font))
        
        # Middle left Item
        x1 = mid_x-(5*item_width//4)
        x2 = x1 + item_width - (gap_width//2)
        y_gap = gap_height
        self.item_list.append(MenuItem(x1, y1+y_gap, x2, y2-y_gap, False, self.font))
        
        # Middle right item
        x1 = mid_x+item_width//4
        x2 = x1 + item_width - (gap_width//2)
        y_gap = gap_height
        self.item_list.append(MenuItem(x1, y1+y_gap, x2, y2-y_gap, False, self.font))
        
        # Foremost item
        x1 = mid_x-item_width//2
        x2 = x1 + item_width
        self.item_list.append(MenuItem(x1, y1, x2, y2, True, self.font))
        
        
        
        # for i in range(self.max_col-1):
        #     x2 = x1 + item_width
        #     self.item_list.append(MenuItem(x1, y1, x2, y2, i, self.font))
        #     print(f"({x1}, {y1}) - ({x2}, {y2})")
        #     x1 = x2 + gap_width
              
    def display(self):
        for i in range(5):
            index = self.selected_col + self.item_index_order[i]
            index %= self.max_col
            item:MenuItem = self.item_list[i]
            # Get attributes
            name = self.attribute_names[index]
            value = self.player.stats[name]
            max_value = self.player.max_stats[name]
            cost = self.player.upgrade_cost[name]
            
            item.display(self.display_surface, name, value, max_value, cost)
        

class MenuItem:
    def __init__(self, x1, y1, x2, y2, is_active, font) -> None:
        width  = x2-x1
        height = y2-y1
        
        self.rect = pygame.Rect(x1, y1, width, height)
        
        self.width = width
        self.height = height
        self.index = 0
        self.is_active = is_active
        self.font:pygame.font.Font = font
    
    def display_bar(self, surface, value, max_value, selected):
        color = UPGRADE_BAR_COLOR
        bar_height = self.height*.9
        completion = value/max_value
        completion_value = round(100*completion, 1)
        top_point = self.rect.midbottom - pygame.math.Vector2(0, bar_height)
        bottom_point = self.rect.midtop + pygame.math.Vector2(0, bar_height)
        bar_height = self.height*.8
        value_point = bottom_point - pygame.math.Vector2(0, bar_height*completion)
        left = self.rect.midtop[0] - 20
        right = self.rect.midtop[0] + 20
        # Draw completed portion
        pygame.draw.line(surface, color, bottom_point, value_point, 8)
        
        # Draw value line
        pygame.draw.line(surface, color, (left, value_point[1]), (right, value_point[1]), 4)
        
        # Draw incomplete portion
        pygame.draw.line(surface, color, value_point, top_point, 4)
        
        if selected and max_value != value:
            projection_point = (bottom_point[0] , 
                                bottom_point[1]-bar_height*completion*UPGRADE_MULTIPLIER
                                )
            if projection_point[1] < top_point[1]:
                projection_point = top_point
            pygame.draw.line(surface, UPGRADE_BAR_PROJECTION_COLOR, value_point, projection_point, 8)
        
        # Draw top line
        pygame.draw.line(surface, color, (left, top_point[1]), (right, top_point[1]), 4)
        # draw bottom line
        pygame.draw.line(surface, color, (left, bottom_point[1]), (right, bottom_point[1]), 4)
    
    def display_name(self, surface, name, cost, selected):
        font_color = TEXT_COLOR if not selected else UI_BG_COLOR
        # Title
        title_surface:pygame.Surface = self.font.render(name, False, font_color)
        title_rect = title_surface.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))
        
        # cost
        cost_surface:pygame.Surface = self.font.render(f"Upgrade Cost: {int(cost)}", False, font_color)
        cost_size = cost_surface.get_size()
        cost_width = cost_size[0]
        cost_rect = title_surface.get_rect(midtop=self.rect.midbottom - pygame.math.Vector2(cost_width//3, 35))
        
        # Draw
        if not selected:
            surface.blit(title_surface, title_rect)
            surface.blit(cost_surface, cost_rect)
        else:
            surface.blit(title_surface, title_rect)
            surface.blit(cost_surface, cost_rect)
    
    def display(self, surface, name, value, max_value, cost):
        color = UPGRADE_BG_COLOR if not self.is_active else UPGRADE_SELECTED_BG_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        self.display_name(surface, name, cost, self.is_active)
        self.display_bar(surface, value, max_value, self.is_active)