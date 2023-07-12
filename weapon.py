import pygame

class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.sprite_type = 'weapon'
        direction = player.status.split('_')[0]
        #print(direction)


        #graphic
        full_path = f'NinjaAdventure/graphics/weapons/{player.weapon}/{direction}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        # placement
        p_width, p_height = player.rect.size
        w_width, w_height = self.image.get_rect().size
        if direction == 'right':
            self.offset = pygame.math.Vector2(p_width//2, p_height//4)
            self.offset += pygame.math.Vector2(w_width//2, 0)
            
        elif direction == 'left':
            self.offset = pygame.math.Vector2(p_width//-2, p_height//4)
            self.offset += pygame.math.Vector2(w_width//-2, 0)
            
        elif direction == 'down':
            self.offset = pygame.math.Vector2(p_width//-5, p_height//2)
            self.offset += pygame.math.Vector2(0, w_height//2)
            
        elif direction == 'up':
            self.offset = pygame.math.Vector2(p_height//-5, p_height//-2)
            self.offset += pygame.math.Vector2(0, w_height//-2)
        
        elif direction == "victory":
            self.offset = pygame.math.Vector2((p_width//-2), (p_height//-2))
            # For some reason the weapon heights for this victory pose differ a lot!
            # This equation was the easiest way I could find to get the weapons to 
            # appear reliably in the correct position above the player's right hand.
            self.offset += pygame.math.Vector2(8, (((w_height-32)**2)//-73)-2)
        
        else:
            assert("Unexpected Direction")
        self.rect = self.image.get_rect(center=player.rect.center + self.offset)
        self.drawn = False

