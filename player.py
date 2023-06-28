import pygame
from settings import *
from entity import Entity
#from tile import *
from support import import_folder

class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        super().__init__(groups)
        self.image = pygame.image.load('NinjaAdventure/Actor/Characters/GreenNinja/forwardninja.png').convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -26)

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
        self.health = self.stats['health'] * 0.5
        self.energy = self.stats['energy'] * 0.8
        self.exp = 0
        
        # damage timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500
    
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
                print(new_stat_value)
                
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
            if not 'idle' in self.status and not 'attack' in self.status:
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
        character_path = "NinjaAdventure/graphics/player/"
        self.animations = {'up': [], 'down':[], 'left':[], 'right':[], 'right_idle':[],
                           'left_idle':[], 'up_idle':[], 'down_idle':[], 'right_attack':[],
                           'left_attack':[], 'up_attack':[], 'down_attack':[]}
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
            self.frame_index = 0

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
        if not self.attacking:
            self.input()
            self.move(self.stats["speed"])
        self.cooldowns()
        self.get_status()
        self.animate()
        self.energy_recovery()