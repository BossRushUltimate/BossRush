import pygame
pygame.init()
pyFont = pygame.font.Font 
# game setup
WIDTH = 1280
HEIGHT = 720
FPS = 60
TILESIZE = 64
UPGRADE_MULTIPLIER = 1.2

HITBOX_OFFSET = {
    'player': -26,
    'object': -40,
    'grass': -10,
    'invisible': 0}

# ui
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT = 'NinjaAdventure/graphics/font/joystix.ttf'
UI_FONT_SIZE = 18

# general colors
WATER_COLOR = '#71ddee'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
UPGRADE_BG_COLOR = UI_BG_COLOR
UPGRADE_SELECTED_BG_COLOR = "#EEEEEE"
UPGRADE_BAR_COLOR = "#880808"
UPGRADE_BAR_PROJECTION_COLOR = "#89CFF0"
TEXT_COLOR = '#EEEEEE'

# ui colors
HEALTH_COLOR = 'red'
ENERGY_COLOR = 'blue'
UI_BORDER_COLOR_ACTIVE = 'gold'

# Gameover screen
G_O_TITLE_FONT = pyFont(UI_FONT, 72)
G_O_MESSAGE_FONT = pyFont(UI_FONT, UI_FONT_SIZE)
G_O_TITLE_COLOR = "#8a0303"
G_O_MESSAGE_COLOR = "#EEEEEE"

# weapons 
weapon_data = {
    'sword': {'cooldown': 100, 'damage': 15,'graphic':'NinjaAdventure/graphics/weapons/sword/full.png'},
    'lance': {'cooldown': 400, 'damage': 30,'graphic':'NinjaAdventure/graphics/weapons/lance/full.png'},
    'axe': {'cooldown': 300, 'damage': 20, 'graphic':'NinjaAdventure/graphics/weapons/axe/full.png'},
    'rapier':{'cooldown': 50, 'damage': 8, 'graphic':'NinjaAdventure/graphics/weapons/rapier/full.png'},
    'sai':{'cooldown': 80, 'damage': 10, 'graphic':'NinjaAdventure/graphics/weapons/sai/full.png'}}

# magic
magic_data = {
    'flame' : {'strength' : 5, 'cost' : 20, 'graphic':'NinjaAdventure/graphics/particles/flame/fire.png'},
    'heal' : {'strength' : 20, 'cost' : 10, 'graphic':'NinjaAdventure/graphics/particles/heal/heal.png'}
}
monster_data = {
    'squid': {'health': 100,'exp':100,'damage':20,'attack_type': 'slash', 'attack_sound':'NinjaAdventure/audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 80, 'notice_radius': 360},
    'raccoon': {'health': 300,'exp':250,'damage':40,'attack_type': 'claw',  'attack_sound':'NinjaAdventure/audio/attack/claw.wav','speed': 2, 'resistance': 3, 'attack_radius': 120, 'notice_radius': 400},
    'spirit': {'health': 100,'exp':110,'damage':8,'attack_type': 'thunder', 'attack_sound':'NinjaAdventure/audio/attack/fireball.wav', 'speed': 4, 'resistance': 3, 'attack_radius': 60, 'notice_radius': 350},
    'bamboo': {'health': 70,'exp':120,'damage':6,'attack_type': 'leaf_attack', 'attack_sound':'NinjaAdventure/audio/attack/slash.wav', 'speed': 3, 'resistance': 3, 'attack_radius': 50, 'notice_radius': 300},
    'big_joe': {'health': 500,'exp':550,'damage':75,'attack_type': 'claw',  'attack_sound':'NinjaAdventure/audio/attack/claw.wav','speed': 5, 'resistance': 5, 'attack_radius': 135, 'notice_radius': 750}
    }