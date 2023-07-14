import pygame 
from settings import *
from tile import Tile
from player import Player, CharacterSelector
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from boss import Boss
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade
from boss import Boss

class Level:
    def __init__(self):

        # get the display surface 
        self.display_surface = pygame.display.get_surface()
        
        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.map_sprites = YSortCameraGroup()
        self.player_sprites = YSortCameraGroup()
        self.boss_sprites = YSortCameraGroup()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = YSortCameraGroup()
        self.attackable_sprites = pygame.sprite.Group()
        self.game_paused = False
        
        # sprite setup
        self.player_selector = CharacterSelector()
        self.player_name = "Agent"
        self.player = None
        self.upgrade_menu = None
        
        self.layouts = {
            'boundary': import_csv_layout('NinjaAdventure/map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('NinjaAdventure/map/map_Grass.csv'),
            'object': import_csv_layout('NinjaAdventure/map/map_Objects.csv'),
            'entities': import_csv_layout('NinjaAdventure/map/map_Entities.csv'),
            'bosses': import_csv_layout('NinjaAdventure/map/map_Bosses.csv') # replace with actual boss folder path if different
        }
        self.graphics = {
            'grass': import_folder('NinjaAdventure/graphics/Grass'),
            'objects': import_folder('NinjaAdventure/graphics/objects')
        }
        
        self.create_map()

        # user interface 
        self.ui = UI()
        self.upgrade_menu = Upgrade(self.player)
        
        #particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)
        
        # game_over
        self.game_over_ticks = 0
        
        self.player_selected = False
        
    def game_is_over(self):
        return not self.player.is_alive() or len(self.boss_sprites)==0
    
    def reset(self):
        self.visible_sprites.empty()
        self.obstacle_sprites.empty()
        self.attack_sprites.empty()
        self.attackable_sprites.empty()
        self.map_sprites.empty()
        self.boss_sprites.empty()
    
    def create_map(self):
        self.reset()
        if self.player:
            self.player.kill()
        self.upgrade_menu = None

        for style,layout in self.layouts.items():
            for row_index,row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x,y),[self.obstacle_sprites],'invisible')
                        
                        if style == 'grass':
                            random_grass_image = choice(self.graphics['grass'])
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites,self.attackable_sprites, self.map_sprites],'grass',random_grass_image)

                        if style == 'object':
                            surf = self.graphics['objects'][int(col)]
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites, self.map_sprites],'object',surf)
                        
                        if style == 'entities':
                            if col == '394':
                                self.player = Player(
                                    self.player_name,
                                    (x,y),
                                    [self.visible_sprites],
                                    self.obstacle_sprites,
                                    self.create_attack,
                                    self.destroy_attack,
                                    self.create_magic)
                                self.upgrade_menu = Upgrade(self.player)
                            
                            elif col == '500': 
                                boss_name = 'big_joe'
                                Boss(boss_name,
                                        (x,y),
                                        [self.visible_sprites,self.attackable_sprites, self.boss_sprites],
                                        self.obstacle_sprites,
                                        self.damage_player,
                                        self.trigger_death_particles,
                                        self.add_exp
                                        )
                            
                            else:
                                if col == '390': monster_name = 'bamboo'
                                elif col == '391': monster_name = 'spirit'
                                elif col == '392': monster_name ='raccoon'
                                else: monster_name = 'squid'
                                Enemy(monster_name,
                                    (x,y),
                                    [self.visible_sprites,self.attackable_sprites],
                                    self.obstacle_sprites,
                                    self.damage_player,
                                    self.trigger_death_particles,
                                    self.add_exp)
                            
    def create_attack(self):
        self.current_attack = Weapon(self.player,[self.visible_sprites,self.attack_sprites])
        self.player.current_attack = self.current_attack

    def create_magic(self,style,strength,cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
        if style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])
    
    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None
        self.player.clear_attack()

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite,self.attackable_sprites,False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        # This section determines what happens when an attackable sprite gets hit
                        
                        if target_sprite.sprite_type == 'grass':
                            
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 75)
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos - offset,[self.visible_sprites])
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player,attack_sprite.sprite_type)

    def damage_player(self,amount,attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()

            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

    def trigger_death_particles(self, pos, particle_type):
        #IN A LIST?
        self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])

    def add_exp(self, amount):
        self.player.exp += amount
    
    def display(self):
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)
        
    def run(self):
        # update and draw the game
        if not self.game_is_over():
            self.visible_sprites.custom_draw(self.player)
            self.ui.display(self.player)
            if self.player_selected:
                if not self.game_paused:	
                    self._run_game_play()
                elif self.player.is_alive():
                    self._run_pause_menu()
            else:
                self._run_player_selection()
        else:
            if len(self.boss_sprites) == 0:
                self._run_victory()
            else:
                self._run_defeat()
                
    def _run_game_play(self):
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(self.player)
        self.player_attack_logic()
        
    def _run_player_selection(self):
        self.player_selected = self.player_selector.run_turn()
        self.player_name = self.player_selector.get_selected_name()
        if self.player_selected:
            self.create_map()
        # self.player_selected = True
        # self.player.health = 10
    
    def _run_pause_menu(self):
        self.upgrade_menu.input()
        self.upgrade_menu.display()
        
    def _run_defeat(self):
        self.map_sprites.custom_draw(self.player)
        self.player.update()
        if self.game_over_ticks == 0:
            self.deathShroud = Shroud(self.display_surface.get_width(),self.display_surface.get_height(), "Game Over!", "Press space to continue.")
            self.destroy_attack()
        if self.deathShroud.is_transparent():    
            self.deathShroud.update()
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.create_map()
                self.player_selected=False
                self.deathShroud.clear()
                self.player_selector.clear()
        if self.game_over_ticks < 200:
            self.deathShroud.draw(self.display_surface)
        else:
            self.deathShroud.draw(self.display_surface, True)
        
        self.player.draw(self.display_surface)
        
        self.game_over_ticks +=1
        
    def _run_victory(self):
        # timing logic
        if self.game_over_ticks == 0:
            self.deathShroud = Shroud(self.display_surface.get_width(),self.display_surface.get_height(), "VICTORY!!!", "Press space to continue.")
            self.player.declare_victory()
            self.destroy_attack()
        
        elif self.game_over_ticks == 175:
            self.create_attack()
        
        if self.game_over_ticks < 200: 
            draw_message = False
        else:
            draw_message = True
        
        self.player.update()
        
        if self.deathShroud.is_transparent():    
            self.deathShroud.update()
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.game_over_ticks = -1
                self.create_map()
                self.player_selected=False
                self.deathShroud.clear()
                self.player_selector.clear()
                
        
        # Draw map
        self.map_sprites.custom_draw(self.player)
        self.deathShroud.draw(self.display_surface, draw_message)
        self.player.draw(self.display_surface)
        
        self.game_over_ticks +=1
        
    def toggle_menu(self):
        self.game_paused = not self.game_paused
        
class Shroud:
    def __init__(self, width:int, height:int, 
                 title:str, message:str,
                 change_amount:int=1):
        
        self.title = title
        self.message = message
        self.opacity_percent = 0
        self.opacity_change = change_amount
        self.surface = pygame.Surface((width,height), pygame.SRCALPHA)
        
    def is_transparent(self):
        return self.opacity_percent < 100
    
    def clear(self):
        self.opacity_percent = 0
    
    def update(self):
        if self.opacity_change > 0:
            if self.opacity_percent < 100-self.opacity_change:
                self.opacity_percent += self.opacity_change
            else:
                self.opacity_percent = 100
        elif self.opacity_change < 0:
            if self.opacity_percent > self.opacity_change:
                self.opacity_percent += self.opacity_change
            else:
                self.opacity_percent = 0
        self.surface.fill((0,0,0,self.opacity_percent*2.55))
        if self.opacity_change >= 90:
            self.draw_title
        if self.opacity_percent == 100:
            self.draw_message
        
    def draw_title(self):
        title_surface:pygame.Surface = G_O_TITLE_FONT.render(self.title, False, G_O_TITLE_COLOR)
        title_rect = title_surface.get_rect(midtop=self.surface.get_rect().center + pygame.math.Vector2(0, -150))
        self.surface.blit(title_surface, title_rect)
    
    def draw_message(self):
        title_surface:pygame.Surface = G_O_MESSAGE_FONT.render(self.message, False, G_O_MESSAGE_COLOR)
        title_rect = title_surface.get_rect(midtop=self.surface.get_rect().center + pygame.math.Vector2(0, 50))
        self.surface.blit(title_surface, title_rect)

    def draw(self, display_surface:pygame.Surface, draw_message=False):
        
        if self.opacity_percent > 85:
            self.draw_title()
        if draw_message: self.draw_message()
        display_surface.blit(self.surface, (0, 0))

class YSortCameraGroup(pygame.sprite.Group):
	def __init__(self):

		# general setup 
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.half_width = self.display_surface.get_size()[0] // 2
		self.half_height = self.display_surface.get_size()[1] // 2
		self.offset = pygame.math.Vector2()

		# creating the floor
		self.floor_surf = pygame.image.load('NinjaAdventure/graphics/tilemap/ground.png').convert()
		self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))

	def custom_draw(self,player):

		# getting the offset 
		self.offset.x = player.rect.centerx - self.half_width
		self.offset.y = player.rect.centery - self.half_height

		# drawing the floor
		floor_offset_pos = self.floor_rect.topleft - self.offset
		self.display_surface.blit(self.floor_surf,floor_offset_pos)

		# for sprite in self.sprites():
		for sprite in sorted(self.sprites(),key = lambda sprite: sprite.rect.centery):
			offset_pos = sprite.rect.topleft - self.offset
			self.display_surface.blit(sprite.image,offset_pos)

	def enemy_update(self,player):
		enemy_sprites = [sprite for sprite in self.sprites() if hasattr(sprite,'sprite_type') and sprite.sprite_type == 'enemy']
		for enemy in enemy_sprites:
			enemy.enemy_update(player)
