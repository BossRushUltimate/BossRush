import pygame
from settings import *
from entity import Entity
from support import import_folder

class Boss(Entity):
# This sets up the name of the monster as well as the monster's position.
    def __init__(self,monster_name,position,groups,obstacle_sprites,damage_player, trigger_death_particles, add_exp):
        super().__init__(groups)
        self.sprite_type = 'enemy'

        # This sets up the graphics
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]

        # This gets the movement and stats of the monster.
        self.rect = self.image.get_rect(topleft = position)
        self.hitbox = self.rect.inflate(0,-10)
        self.obstacle_sprites = obstacle_sprites

        # Monster stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.experience = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']
        self.attack_type = monster_info['attack_type']

        # This is how the player interacts with the monster
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 420
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_exp = add_exp

        # Invincibility Timer
        self.hit = False
        self.vulnerable = False
        self.hit_time = None
        self.invincibility_duration = 300
        
        # sounds
        self.death_sound = pygame.mixer.Sound('NinjaAdventure/audio/death.wav')
        self.hit_sound = pygame.mixer.Sound('NinjaAdventure/audio/hit.wav')
        self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])
        self.death_sound.set_volume(0.2)
        self.hit_sound.set_volume(0.2)
        self.attack_sound.set_volume(0.3)

        #Phases
        self.phase = 1
        self.phase_time = 5000
        self.phase_start_time = pygame.time.get_ticks()
        
    # This gets the graphics, I still need to update the filepath for getting the monsters to display on the screen.
    def import_graphics(self,name):
        self.animations = {'idle':[], 'move':[], 'attack':[]}
        monster_path = f"NinjaAdventure/graphics/monsters/{name}/"
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(monster_path + animation)

    # This coordinates the direction the monster and player are facing as well as how far the player is from the monster.
    def get_player_distance_direction(self,player):
        enemy_vector = pygame.math.Vector2(self.rect.center)
        player_vector = pygame.math.Vector2(player.rect.center)
        distance = (player_vector - enemy_vector).magnitude()

        if distance > 0:
            direction = (player_vector - enemy_vector).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance,direction)

    def get_status(self, player):
        distance = self.get_player_distance_direction(player)[0]

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def actions(self,player):
        if self.status == 'attack':
            self.attack_time = pygame.time.get_ticks()
            self.damage_player(self.attack_damage, self.attack_type)
            self.attack_sound.play()
        elif self.phase == 1:
            self.vulnerable = False
            self.direction = self.get_player_distance_direction(player)[1]
        elif self.phase == 2:
            self.direction = -self.get_player_distance_direction(player)[1] 
        elif self.phase == 3:
            self.status = 'idle'
            self.vulnerable = True
            self.direction = self.get_player_distance_direction(player)[1] - self.get_player_distance_direction(player)[1]  # Always 0   
        else:
            self.direction = pygame.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]
        
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0
            
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

        #Flicker
        if self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if self.phase == 1:
            current_time = pygame.time.get_ticks()
            if current_time - self.phase_time >= self.phase_start_time:
                self.phase += 1
                self.phase_start_time = pygame.time.get_ticks()

        if self.phase == 2:
            current_time = pygame.time.get_ticks() 
            if current_time - self.phase_time >= self.phase_start_time:
                self.phase += 1
                self.phase_start_time = pygame.time.get_ticks()
                
        if self.phase == 3: 
            current_time = pygame.time.get_ticks()
            if current_time - 1000 >= self.phase_start_time:
                self.phase = 1
                self.phase_start_time = pygame.time.get_ticks()

    def get_damage(self,player,attack_type):
        if self.vulnerable:
            self.hit_sound.play()
            self.direction = self.get_player_distance_direction(player)[1]
            if attack_type == 'weapon':
                self.health -= 100
                self.phase = 1

            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_exp(self.experience)
            self.death_sound.play()

    def update(self):
        self.move(self.speed)
        self.animate()
        self.cooldowns()
        self.check_death()

    def enemy_update(self,player):
        self.get_status(player)
        self.actions(player)