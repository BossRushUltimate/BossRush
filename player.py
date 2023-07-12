import pygame
from settings import *
from entity import Entity
from support import import_folder
import os
PLAYER_DIRECTORY = "NinjaAdventure\graphics\player"

class Player(Entity):
    def __init__(self, name, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        super().__init__(groups)
        
        self.image = pygame.image.load(f'{PLAYER_DIRECTORY}\\{name}\\down_idle\\idle_down.png').convert_alpha()
        self.name = name
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])

        self.frame_index = 0
        self.animation_speed = .15

        self.status = 'down'

        # graphics setup
        self.import_player_assets()

        # movement
        self.direction = pygame.math.Vector2()
        self.attacking = False
        self.attack_cooldown = 150
        self.attack_time = pygame.time.get_ticks()
        self.obstacle_sprites = obstacle_sprites
        
        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200
        
        # import a sound
        self.weapon_attack_sound = pygame.mixer.Sound('NinjaAdventure/audio/sword.wav')
        self.weapon_attack_sound.set_volume(0.4)

        # magic
        self.creat_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.magic_switch_time = None

        # stats
        self.stats = {'health': 100, 'energy': 60, 'attack': 10, 'magic': 4, 'speed': 5}
        self.max_stats = {'health': 300, 'energy': 140, 'attack': 20, 'magic': 10, 'speed': 10}
        self.upgrade_cost = {'health': 100, 'energy': 100, 'attack': 100, 'magic': 100, 'speed': 100}
        self.health = self.stats['health'] * 0.05
        self.energy = self.stats['energy'] * 0.8
        self.exp = 0
        
        # damage timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500
    
    def is_alive(self):
        return self.health >= 0
    
    def upgrade_stat(self, stat):
        
        if stat in self.stats:
            cost = self.upgrade_cost[stat]
            if self.exp >= cost:
                # Consume exp
                self.exp -= cost
                
                # Update stat value
                new_stat_value = self.stats[stat] * UPGRADE_MULTIPLIER
                stat_increase = new_stat_value - self.stats[stat]
                self.stats[stat] *= UPGRADE_MULTIPLIER
                
                # Increase actual stat value if stat is depreciable
                if stat == "health":
                    self.health += stat_increase
                elif stat == "energy":
                    self.energy += stat_increase
                    
                # Increase cost for next upgrade of same stat
                self.upgrade_cost[stat]  *= 1.5
                # print(new_stat_value)
                
                # Prevent stats from exceeding maximums
                max = self.max_stats[stat]
                val = self.stats[stat]
                if val > max:
                    self.stats[stat] = max
        else:
            return -1

    def input(self):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
            self.status = 'up'
            #self.image = pygame.image.load('NinjaAdventure/Actor/Characters/GreenNinja/backwardninja.png').convert_alpha()
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
            self.status = 'down'
            #self.image = pygame.image.load('NinjaAdventure/Actor/Characters/GreenNinja/forwardninja.png').convert_alpha()
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
            self.status = 'right'
            #self.image = pygame.image.load('NinjaAdventure/Actor/Characters/GreenNinja/right.png').convert_alpha()
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'
            #self.image = pygame.image.load('NinjaAdventure/Actor/Characters/GreenNinja/left.png').convert_alpha()
        else:
            self.direction.x = 0

        # attack input
        if keys[pygame.K_SPACE] and not self.attacking:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            self.create_attack()
            self.weapon_attack_sound.play()
        
        if keys[pygame.K_LCTRL] and not self.attacking:
            self.attacking = True
            self.attack_time = pygame.time.get_ticks()
            style = list(magic_data.keys())[self.magic_index]
            strength = list(magic_data.values())[self.magic_index]['strength'] + self.stats['magic']
            cost = list(magic_data.values())[self.magic_index]['cost']
            self.creat_magic(style, strength, cost)

        if keys[pygame.K_q] and self.can_switch_weapon:
            self.can_switch_weapon = False
            self.weapon_switch_time = pygame.time.get_ticks()

            if self.weapon_index < len(list(weapon_data.keys())) - 1:
                self.weapon_index += 1
            else:
                self.weapon_index = 0

            self.weapon = list(weapon_data.keys())[self.weapon_index]

        if keys[pygame.K_e] and self.can_switch_magic:
            self.can_switch_magic = False
            self.magic_switch_time = pygame.time.get_ticks()

            if self.magic_index < len(list(magic_data.keys())) - 1:
                self.magic_index += 1
            else:
                self.magic_index = 0

            self.magic = list(magic_data.keys())[self.magic_index]

    def get_status(self):
        #idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status and not "death" in self.status:
                self.status = self.status + '_idle'

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    #overwrite idle
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center
        
    def import_player_assets(self):
        character_path = f"{PLAYER_DIRECTORY}\\{self.name}\\"
        self.animations = {'up': [], 'down':[], 'left':[], 'right':[], 'right_idle':[],
                           'left_idle':[], 'up_idle':[], 'down_idle':[], 'right_attack':[],
                           'left_attack':[], 'up_attack':[], 'down_attack':[], "death": []}
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # moving left
                        self.hitbox.left = sprite.hitbox.right
                
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # moving up
                        self.hitbox.top = sprite.hitbox.bottom

    def animate(self):
        animation = self.animations[self.status]

        #loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if not "death" in self.status:
                self.frame_index = 0
            else:
                self.frame_index = len(animation)-1

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

        # flicker
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        base_damage = self.stats['attack']
        weapon_damage = weapon_data[self.weapon]['damage']
        return base_damage + weapon_damage
    
    def get_full_magic_damage(self):
        base_damage = self.stats['magic']
        spell_damage = magic_data[self.magic]['strength']
        return base_damage + spell_damage

    def energy_recovery(self):
        if self.energy < self.stats['energy']:
            self.energy += 0.005 * self.stats['magic']
        else:
            self.energy = self.stats['energy']

    def update(self):
        if not self.attacking and self.is_alive():
            self.input()
            self.move(self.stats["speed"])
        self.cooldowns()
        self.get_status()
        self.animate()
        self.energy_recovery()
        if not self.is_alive():
            self.status = "death"
            self.vulnerable = False

    def draw(self, surface:pygame.Surface):
        dimensions = self.image.get_size()
        destination = surface.get_rect().center + pygame.math.Vector2(dimensions[0]//-2, dimensions[1]//-2)
        surface.blit(self.image, destination)

class CharacterSelector:
    def __init__(self) -> None:
        # General Setup
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        
        # Create CharacterTiles
        self.frame_list = []
        self.wrap_frames = []
        self.character_list = []
        self.max_col = 5
        self.max_row = 6
        self.character_offset = self.max_col*-1
        self.create_items()
        print(self.wrap_frames)
        
        # scrolling details
        self.scroll_amount = 11
        self.dy = 0
        
        # Selection
        self.selected_index = 0
        self.max_index = len(self.character_list)
        dimensions = self.display_surface.get_size()
        self.height =  dimensions[1] * 0.8
        self.width = dimensions[0] // self.max_col
        self.cooldown_time = 15
        self.cooldown = -1
        
        # Quit?
        self.selection_finished = False
        print(
            f"cols    = {self.max_col}",
            f"rows    = {self.max_row}",
            f"ac_row  = {len(self.frame_list[0])}",
            sep="\n"
        )
        
    def input(self):
        keys = pygame.key.get_pressed()
        if self.cooldown < 0:
            if keys[pygame.K_RIGHT]:
                self.selected_index += 1
                if self.selected_index % self.max_col == 0:
                    self.selected_index -= self.max_col
                self.cooldown = self.cooldown_time
            
            elif keys[pygame.K_LEFT]:
                self.selected_index -= 1
                if self.selected_index % self.max_col == self.max_col-1:
                    self.selected_index += self.max_col
                self.cooldown = self.cooldown_time
            
            elif keys[pygame.K_UP]:
                self.selected_index -= self.max_col
                self.selected_index %= self.max_index
                self.dy += self.scroll_amount
                self.cooldown = self.cooldown_time
            
            elif keys[pygame.K_DOWN]:
                self.selected_index += self.max_col
                self.selected_index %= self.max_index
                self.dy -= self.scroll_amount
                self.cooldown = self.cooldown_time
                
            elif keys[pygame.K_SPACE]:
                self.selection_finished = True
                self.cooldown = self.cooldown_time
        elif self.cooldown > 0:
            # print(f"cd: {self.cooldown}\ndy: {self.dy}\n")
            self.cooldown -= 1
            if self.dy != 0:
                self.scroll()
        else:
            if self.dy != 0:
                self.finish_scroll()
                self.dy = 0
                print("finishing")
            self.cooldown -= 1

    def finish_scroll(self):
        self.character_offset += self.max_col * (-1 if self.dy > 0 else 1)
        self.character_offset %= self.max_index
        i_frame = 0
        for row in self.frame_list:
            for frame in row:
                frame.set_y_offset(0)
                i_frame+=1
        for frame in self.wrap_frames:
            frame.set_y_offset(0)
            
    def scroll(self):
        for row in self.frame_list:
            for frame in row:
                frame.scroll_y(self.dy)
            
        for frame in self.wrap_frames:
            frame.scroll_y(self.dy)
            
    def get_selected_name(self):
        return self.character_list[self.selected_index].name
        
    def create_items(self):
        dimensions = self.display_surface.get_size()
        width = dimensions[0] // 6
        height =  dimensions[1] // 5
        gap = width // 7
        
        x_space = width + gap
        y_space = height + gap
        
        x0 = gap
        y0 = gap - y_space
        
        i_frame = 0
        frame_row = []
        
        for i in range(self.max_row):
            y = y0 + (y_space*i)
            for j in range(self.max_col):
                x = x0 + (x_space*j)
                frame_row.append(MenuFrame(x, y, x+width, y+height, self.font))
            self.frame_list.append(frame_row)
            frame_row = []
                    
        
        
        for entry in os.scandir(PLAYER_DIRECTORY):
            if entry.is_dir():
                name = os.path.basename(entry.path)
                self.character_list.append(CharacterInfo(name))
                
    def display(self):
        i_draw = self.character_offset
        for row in self.frame_list:
            for frame in row:
                self.character_list[i_draw].draw(self.display_surface, frame, i_draw==self.selected_index)
                i_draw += 1
                if i_draw >= self.max_index:
                    i_draw = 0
        
        if self.dy != 0:
            i_draw -= self.max_col
            if i_draw < 0:
                i_draw = self.max_index - 1 +i_draw
            for frame in self.wrap_frames:
                self.character_list[i_draw].draw(self.display_surface, frame, i_draw==self.selected_index)
                i_draw += 1
                if i_draw >= self.max_index:
                        i_draw = 0
            
    def clear(self):
        self.selection_finished = False
        
    def run_turn(self):
        self.input()
        self.display()
        return self.selection_finished

class CharacterTile:
    def __init__(self, x1, y1, x2, y2, name, font) -> None:
        width  = x2-x1
        height = y2-y1
        
        self.rect = pygame.Rect(x1, y1, width, height)
        self.x = x1
        self.y = y1
        self.width = width
        self.height = height
        
        self.font:pygame.font.Font = font
        
        self.name = name
        
        # animations
        self.frame = 0
        self.tick = 0
        self.ticks_per_frame = 5
        self.idle_sprite = pygame.image.load(f"{PLAYER_DIRECTORY}\\{name}\\down_idle\\idle_down.png").convert_alpha()
        self.active_sprites = []
        
        directory = f"{PLAYER_DIRECTORY}\\{name}\\down"
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) and filename.lower().endswith('.png'):
                self.active_sprites.append(pygame.image.load(file_path).convert_alpha())
        
    def display_sprite(self, surface, is_active):
        if not is_active:
            surface.blit(self.idle_sprite, self.rect.center)
        else:
            current_sprite = self.active_sprites[self.frame]
            surface.blit(current_sprite, self.rect.center)
            self.tick += 1
            if self.tick >= self.ticks_per_frame:
                self.tick = 0 
                self.frame += 1
                self.frame %= len(self.active_sprites)
    
    def display_name(self, surface, is_active):
        font_color = TEXT_COLOR if not is_active else UI_BG_COLOR
        # Title
        title_surface:pygame.Surface = self.font.render(self.name, False, font_color)
        title_rect = title_surface.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0, 20))
         
        # Draw
        if not is_active:
            surface.blit(title_surface, title_rect)
        else:
            surface.blit(title_surface, title_rect)
    
    def display(self, surface, is_active):
        color = UPGRADE_BG_COLOR if not is_active else UPGRADE_SELECTED_BG_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        self.display_name(surface, is_active)
        self.display_sprite(surface, is_active)
        
    def scroll_y(self, amount):
        self.y += amount
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
class MenuFrame:
    def __init__(self, x1, y1, x2, y2, font) -> None:
        width  = x2-x1
        height = y2-y1
        
        self.width = width
        self.height = height
        
        self.x = x1
        self.y = y1
        
        self.y_offset = 0
        self.x_offset = 0
        
        self.update_rect()
        
        
        self.font:pygame.font.Font = font

    def set_y_offset(self, offset:int):
        print("setting offset")
        self.y_offset = offset
        self.update_rect()
    
    def scroll_y(self, dy):
        if abs(self.y_offset + dy) < self.height:
            self.y_offset += dy
        self.update_rect()
        
    def update_rect(self):
        self.rect =  pygame.Rect(
                                 self.x+self.x_offset, 
                                 self.y+self.y_offset, 
                                 self.width, 
                                 self.height
                                )

class CharacterInfo:
    def __init__(self, name):
        self.name = name
        
        # animations
        self.frame = 0
        self.tick = 0
        self.ticks_per_frame = 5
        self.idle_sprite = pygame.image.load(f"{PLAYER_DIRECTORY}\\{name}\\down_idle\\idle_down.png").convert_alpha()
        self.active_sprites = []
        directory = f"{PLAYER_DIRECTORY}\\{name}\\down"
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) and filename.lower().endswith('.png'):
                self.active_sprites.append(pygame.image.load(file_path).convert_alpha())
                
    def display_sprite(self, surface:pygame.Surface, is_active:bool, frame:MenuFrame):
        if not is_active:
            surface.blit(self.idle_sprite, frame.rect.center)
        else:
            current_sprite = self.active_sprites[self.frame]
            surface.blit(current_sprite, frame.rect.center)
            self.tick += 1
            if self.tick >= self.ticks_per_frame:
                self.tick = 0 
                self.frame += 1
                self.frame %= len(self.active_sprites)
    
    def display_name(self, surface:pygame.Surface, is_active:bool, frame:MenuFrame):
        font_color = TEXT_COLOR if not is_active else UI_BG_COLOR
        # Title
        title_surface:pygame.Surface = frame.font.render(self.name, False, font_color)
        title_rect = title_surface.get_rect(midtop=frame.rect.midtop + pygame.math.Vector2(0, 20))
         
        # Draw
        if not is_active:
            surface.blit(title_surface, title_rect)
        else:
            surface.blit(title_surface, title_rect)
    
    def draw(self, surface, frame:MenuFrame, is_active:bool):
        color = UPGRADE_BG_COLOR if not is_active else UPGRADE_SELECTED_BG_COLOR
        pygame.draw.rect(surface, color, frame.rect)
        pygame.draw.rect(surface, UI_BORDER_COLOR, frame.rect, 4)
        self.display_name(surface, is_active, frame)
        self.display_sprite(surface, is_active, frame)
    
    