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
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade

class Level:
    def __init__(self):

        # get the display surface 
        self.display_surface = pygame.display.get_surface()
        
        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        self.game_paused = False
        
        # sprite setup
        self.player_selector = CharacterSelector()
        self.player_name = "Agent"
        self.player = None
        self.upgrade_menu = None
        self.create_map()

        # user interface 
        self.ui = UI()
        self.upgrade_menu = Upgrade(self.player)
        
        #particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)
        
        self.player_selected = False
        
    def create_map(self):
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()
        layouts = {
            'boundary': import_csv_layout('NinjaAdventure/map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('NinjaAdventure/map/map_Grass.csv'),
            'object': import_csv_layout('NinjaAdventure/map/map_Objects.csv'),
            'entities': import_csv_layout('NinjaAdventure/map/map_Entities.csv')
        }
        graphics = {
            'grass': import_folder('NinjaAdventure/graphics/Grass'),
            'objects': import_folder('NinjaAdventure/graphics/objects')
        }

        for style,layout in layouts.items():
            for row_index,row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x,y),[self.obstacle_sprites],'invisible')
                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites,self.attackable_sprites],'grass',random_grass_image)

                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x,y),[self.visible_sprites,self.obstacle_sprites],'object',surf)
                        if style == 'entities':
                            if col == '394':
                                if self.player:
                                    self.player.kill()
                                    self.player = None
                                self.player = Player(
                                    self.player_name,
                                    (x,y),
                                    [self.visible_sprites],
                                    self.obstacle_sprites,
                                    self.create_attack,
                                    self.destroy_attack,
                                    self.create_magic)
                                if self.upgrade_menu:
                                    self.upgrade_menu = None
                                self.upgrade_menu = Upgrade(self.player)
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

    def create_magic(self,style,strength,cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
        if style == 'flame':
            self.magic_player.flame(self.player, cost, [self.visible_sprites, self.attack_sprites])
    
    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

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
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)
        
        if self.player_selected:
            if not self.game_paused:	
                self.visible_sprites.update()
                self.visible_sprites.enemy_update(self.player)
                self.player_attack_logic()
            else:
                self.upgrade_menu.input()
                self.upgrade_menu.display()
        else:
            self.player_selected = self.player_selector.run_turn()
            self.player_name = self.player_selector.get_selected_name()
            if self.player_selected:
                self.create_map()
            
    def toggle_menu(self):
        self.game_paused = not self.game_paused

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
