# -*- coding: utf-8 -*-
"""
Created on Thu Jul 05 17:48:50 2012

@author: pmaurier
"""

import pygame
import pygame.locals as pg

from game_engine import Engine

MAP_TILE_WIDTH, MAP_TILE_HEIGHT = 64, 73 # a, b
MAP_TILE_R = 32
MAP_TILE_S = 37
MAP_TILE_H = 18

# Slope of the corner edges
MAP_TILE_M = 1. * MAP_TILE_H / MAP_TILE_R

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
OFFSET_X = WINDOW_WIDTH/2 - 48
OFFSET_Y = WINDOW_HEIGHT/2 - 25

DX = {("r", 1):[16,16,16,16], ("r", -1):[-16,-16,-16,-16],
      ("g", 1):[8,8,8,8], ("g", -1):[-8,-8,-8,-8],
      ("b", 1):[8,8,8,8], ("b", -1):[-8,-8,-8,-8]}
DY = {("r", 1):[0,0,0,0], ("r", -1):[0,0,0,0],
      ("g", 1):[-14,-14,-14,-13], ("g", -1):[14,14,14,13],
      ("b", 1):[14,14,14,13], ("b", -1):[-14,-14,-14,-13]}      

VALID_POS = [(4,0), (3,1), (2,2), (1,3), (0,4), (-1,4), (-2,4), (-3,4), (-4,4),
             (-4,3), (-4,2), (-4,1), (-4,0), (-3,-1), (-2,-2), (-1,-3), (0,-4),
             (1,-4), (2,-4), (3,-4), (4,-4), (4,-3), (4,-2), (4,-1)]

# Mouse buttons
LEFT, MIDDLE, RIGHT = 1,2,3

# Useful functions to convert coordinates
def map_to_screen(x, y):
    """ Converts map coordinates to screen coordinates
        (center of the tile) """
    coord_x = OFFSET_X + MAP_TILE_R * (2 * x + y) + MAP_TILE_R
    coord_y = OFFSET_Y + (MAP_TILE_H + MAP_TILE_S) * y + MAP_TILE_S/2 + MAP_TILE_H 
    return coord_x, coord_y

def screen_to_map(x, y):
    """convert screen coordinates to map coordinates"""
    sect_y = int((y - OFFSET_Y) / (MAP_TILE_H + MAP_TILE_S))        
    sect_x = int((((x - OFFSET_X) /  MAP_TILE_R) - sect_y) / 2)
    
    sect_pxl_y = (y - OFFSET_Y) % (MAP_TILE_H + MAP_TILE_S)
    sect_pxl_x = (x - OFFSET_X - (MAP_TILE_R * (sect_y%2))) % (2 * MAP_TILE_R)

    # Body
    coord_x = sect_x
    coord_y = sect_y
    if sect_pxl_y < (MAP_TILE_H - sect_pxl_x * MAP_TILE_M):
        # Top left
        coord_x = sect_x
        coord_y = sect_y - 1
    elif sect_pxl_y < (- MAP_TILE_H + sect_pxl_x * MAP_TILE_M):
        # Top right
        coord_x = sect_x + 1
        coord_y = sect_y - 1
        
    return coord_x, coord_y

class TileCache(object):
    """Load the tilesets lazily into global cache"""
    def __init__(self,  width=MAP_TILE_WIDTH, height=MAP_TILE_HEIGHT):
        self.width = width
        self.height = height
        self.cache = {}

    def __getitem__(self, filename):
        """Return a table of tiles, load it from disk if needed."""
        key = (filename, self.width, self.height)
        try:
            return self.cache[key]
        except KeyError:
            tile_table = self._load_tile_table(filename, self.width,
                                               self.height)
            self.cache[key] = tile_table
            return tile_table

    def _load_tile_table(self, filename, width, height):
        """Load an image and split it into tiles."""
        image = pygame.image.load(filename).convert_alpha()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, image_width/width):
            line = []
            tile_table.append(line)
            for tile_y in range(0, image_height/height):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        return tile_table

class Ball(pygame.sprite.Sprite):
    def __init__(self, pos=(0, 0), frames=None):
        super(Ball, self).__init__()
        self.frames = [frames[0][0], frames[1][0]]
        self.image = frames[0][0]
        self.rect = self.image.get_rect()
        self.animation = None
        self.direction = None
        self.pos = pos
        self.poked = False
    
    def _get_pos(self):
        """Check the current position of the sprite on the map."""
        return screen_to_map(self.rect.center[0], self.rect.center[1])
    
    def _set_pos(self, position):
        """Set the position of the sprite on the map."""
        self.rect.center = map_to_screen(position[0], position[1])
    
    pos = property(_get_pos, _set_pos)
    
    def stand_animation(self):
        """The default animation."""
        while True:
            # Change to next frame every two ticks
            for frame in self.frames:
                self.image = frame
                yield None
                yield None
    
    def move_animation(self):
        """ The animation when moving """        
        for step in range(4):
#            self.image = self.frames[frame][0]
            yield None
            self.move(DX[self.direction][step], DY[self.direction][step])
    
    def poke_animation(self):
        self.move(DX[self.direction][0], DY[self.direction][0])            
    
    def move(self, dx, dy):
        """ Change the position of the Sprite on the screen """
        self.rect.move_ip(dx, dy)

    def update(self, *args):
        """Run the current animation."""
        
        if self.animation is None:
            self.image = self.frames[0]
        else:
            try:
                self.animation.next()
            except StopIteration:
                self.animation = None

class Pointer(pygame.sprite.Sprite):
    def __init__(self, pos=(0, 0), frames=None):
        super(Pointer, self).__init__()
        if frames:
            self.frames = frames
        print self.frames[0][0]
        self.image = self.frames[0][0]
        self.animation = self.stand_animation()
#        self.animation = None
        self.rect = self.image.get_rect()
        self.pos = pos
    
    def _get_pos(self):
        """Check the current position of the sprite on the map."""
        return screen_to_map(self.rect.center[0], self.rect.center[1])
    
    def _set_pos(self, position):
        """Set the position of the sprite on the map."""
        self.rect.center = map_to_screen(position[0], position[1])
    
    pos = property(_get_pos, _set_pos)
    
    def move_to(self, pos_x, pos_y):
        if self.is_valid(pos_x,pos_y):
            self._set_pos((pos_x, pos_y))
            
    def stand_animation(self):
        """The default animation."""
        while True:
            # Change to next frame every two ticks
            for frame in self.frames[0]:
                self.image = frame
                yield None
                yield None

    def move(self, dx, dy):
        """ Change the position of the Sprite on the screen """
        self.rect.move_ip(dx, dy)

    def update(self, *args):
        """Run the current animation.""" 
        self.animation.next()
                
    def is_valid(self, pos_x, pos_y):
        return (pos_x, pos_y) in VALID_POS

class Game(object):
    """The main game object."""
    
    def __init__(self):
        self.screen = pygame.display.get_surface()
        background_img = pygame.image.load("board.png").convert()
        self.background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.background.blit(background_img, (0, 0))
        self.sprites = pygame.sprite.RenderUpdates()   
        self.pointer = Pointer((4,0), SPRITES["pointer.png"])
        self.sprites.add(self.pointer)
        self.game_over = False
        self.engine = Engine()
        self.pressed_key = None

    def control(self):
        """Handle the controls of the game."""

        keys = pygame.key.get_pressed()

        def pressed(key):
            """Check if the specified key is pressed."""
            return self.pressed_key == key or keys[key]

        def push(ball, d):
            """Push ball in specified direction."""
            ball.direction = d
            ball.animation = ball.move_animation()
        
        def poke(ball, d):
            """ Poke a ball in specified direction."""
            if not ball.poked:
                ball.direction = d
                ball.animation = ball.poke_animation()

        if pressed(pg.K_UP):
            poke(self.ball1, ("g", 1))
            print "up"
        elif pressed(pg.K_DOWN):
            poke(self.ball1, ("g", -1))
            print "down"
        elif pressed(pg.K_LEFT):
            poke(self.ball1, ("r", -1))
            print "left"
        elif pressed(pg.K_RIGHT):
            poke(self.ball1, ("r", 1))
            print "right"
        self.pressed_key = None
    
    def main(self):
        """Run the main loop."""
        clock = pygame.time.Clock()
        
        self.screen.blit(self.background, (0, 0))

        self.ball1 = Ball((1,0), SPRITES["ball1.png"])
        self.sprites.add(self.ball1)
        
        pygame.display.flip()
        
        while not self.game_over:
            self.sprites.clear(self.screen, self.background)
            self.sprites.update()
            dirty = self.sprites.draw(self.screen)
            pygame.display.update(dirty)
            # Wait for one tick of the game clock (30 FPS Max)
            lapse = clock.tick(30)
            if self.ball1.animation == None:
                self.control()
                self.ball1.update()
            # Process pygame events
            for event in pygame.event.get():
                if event.type == pg.QUIT:
                    self.game_over = True
                if event.type == pygame.MOUSEMOTION:
                    x, y = screen_to_map(*event.pos)
                    self.pointer.move_to(x, y)
#                    print x, y
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFT:
                    ball = self.ball1
                    if not ball.poked:
                        ball.direction = ("r", 1)
                        ball.animation = ball.poke_animation()
                        ball.poked = True
                else:
                    ball = self.ball1
                    if ball.poked:
                        ball.direction = (ball.direction[0], ball.direction[1]*-1)
                        ball.animation = ball.poke_animation()
                        ball.poked = False
                    

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    SPRITES = TileCache()
#    cProfile.run("Game().main()")
    
    Game().main()
    