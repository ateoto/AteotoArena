import sfml as sf

import logging as log
import json
import os

from .animation import AnimationFrame, Animation

NORTH = sf.Vector2f(0, -1)
WEST = sf.Vector2f(-1, 0)
SOUTH = sf.Vector2f(0 , 1)
EAST = sf.Vector2f(1, 0)

class Actor(object):
    """
    Base Actor Class, all Actors should inherit from this
    """

    def __init__(self):
        pass

class VisibleActor(Actor):
    def __init__(self):
        super(VisibleActor, self).__init__()

class MoveableActor(VisibleActor):
    def __init__(self):
        super(MoveableActor, self).__init__()
    
class NPCActor(MoveableActor):
    def __init__(self):
        super(NPCActor, self).__init__()

class PCActor(MoveableActor):
    def __init__(self, animations_file = None, location = None):
        super(PCActor, self).__init__()
        self.timescale = 1
        self.movespeed = 100
        self.location = location
        self.moving_codes = [ sf.Keyboard.W, sf.Keyboard.A, sf.Keyboard.S, sf.Keyboard.D ]
        self.heading = SOUTH
        self.bounding = sf.IntRect(self.location.x, self.location.y, 64, 64)
        self.show = sf.FloatRect(0,0,800,600)

        self.is_moving = False
        self.is_animating = False
        
        self.animation_file = animations_file
        self.animations = {}
        self.current_animation = None

        self.sprite = sf.Sprite(sf.Texture.load_from_file('data/actors/human_male/walkcycle/BODY_animation.png'))
        self.sprite.position = self.location

        self.cached_inv = {}
        self.inventory = None

    def handle_keypress(self, event, dt):
        pass
        """
        if event.code in self.moving_codes:
            if event.code == sf.Keyboard.W:
                if self.moving <> self.directions['NORTH']:
                    self.move(self.directions['NORTH'], dt)
                    self.current_animation = self.animations['walkcycle_north']
                    self.current_animation.animate(dt, loop = True)
                    self.moving = self.directions['NORTH']

            elif event.code == sf.Keyboard.A:
                self.move(self.directions['WEST'], dt)
            elif event.code == sf.Keyboard.S:
                if self.moving <> self.directions['SOUTH']:
                    self.move(self.directions['SOUTH'], dt)
                    self.current_animation = self.animations['walkcycle_south']
                    self.current_animation.animate(dt, loop = True)
                    self.moving = self.directions['SOUTH']

            elif event.code == sf.Keyboard.D:
                self.move(self.directions['EAST'], dt)
        else:
            self.moving = False
            self.current_animation.stop_animation()
        """    

    def update(self, dt, scrollboxes):
        if sf.Keyboard.is_key_pressed(sf.Keyboard.W):
            self.heading = NORTH
            self.move(NORTH, dt)
            if self.bounding.intersects(scrollboxes['north']):
                self.show.top += -1 * self.movespeed * self.timescale * dt
                self.move(SOUTH, dt)

            self.set_animation(self.animations['walk']['north'], dt, loop = True)

        elif sf.Keyboard.is_key_pressed(sf.Keyboard.A):
            self.heading = WEST
            self.move(WEST, dt)
            if self.bounding.intersects(scrollboxes['west']):
                self.show.left += -1 * self.movespeed * self.timescale * dt
                self.move(EAST, dt)

            self.set_animation(self.animations['walk']['west'], dt, loop = True)

        elif sf.Keyboard.is_key_pressed(sf.Keyboard.S):
            self.heading = SOUTH
            self.move(SOUTH, dt)
            if self.bounding.intersects(scrollboxes['south']):
                self.show.top += 1 * self.movespeed * self.timescale * dt
                self.move(NORTH, dt)

            self.set_animation(self.animations['walk']['south'], dt, loop = True)

        elif sf.Keyboard.is_key_pressed(sf.Keyboard.D):
            self.heading = EAST
            self.move(EAST, dt)
            if self.bounding.intersects(scrollboxes['east']):
                self.show.left += 1 * self.movespeed * self.timescale * dt
                self.move(WEST, dt)

            self.set_animation(self.animations['walk']['east'], dt, loop = True)

        else:
            if self.heading == NORTH:
                facing = 'north'
            elif self.heading == WEST:
                facing = 'west'
            elif self.heading == SOUTH:
                facing = 'south'
            elif self.heading == EAST:
                facing = 'east'

            self.set_animation(self.animations['idle'][facing], dt, loop = True)

        if sf.Keyboard.is_key_pressed(sf.Keyboard.L_SHIFT):
            self.timescale = 1.5
        else:
            self.timescale = 1

    def set_animation(self, animation, dt, loop = False):
        if self.is_animating:
            if self.current_animation is not animation:
                self.current_animation.stop_animation()
                self.current_animation = animation
                self.current_animation.animate(dt, loop = loop)
        else:
            self.is_animating = True
            self.current_animation = animation
            self.current_animation.animate(dt, loop = loop)

    def move(self, location_delta, dt):
        self.location += location_delta * self.movespeed * self.timescale * dt
        self.bounding.left, self.bounding.top = self.location.x, self.location.y
        
        self.sprite.position = self.location

    def draw(self, target, states):
        # Maybe this just draws the animation instead of the sprite.
        if self.current_animation is not None:
            self.sprite.set_texture(self.current_animation.sprite.texture)
            self.sprite.set_texture_rect(self.current_animation.sprite.get_texture_rect())
        
        target.draw(self.sprite)

    def load_inventory(self, inventory_file):
        with open(inventory_file, 'r') as invf:
            self.inventory = json.loads(invf.read())

    def build_inventory_images(self):
        with open(self.animations_file, 'r') as af:
            anims = json.loads(af.read())
            for anim in anims:
                base_dir = anim['base']
                base_texture = sf.Texture.load_from_file(os.path.join(base_dir, 'BODY_animation.png'))
                base_size = sf.Vector2f(base_texture.width, base_texture.height)

                rt = sf.RenderTexture(base_size.x, base_size.y)
                rt.clear(sf.Color.TRANSPARENT)

                body = sf.RectangleShape(base_size)
                body.set_texture(base_texture)
                rt.draw(body)
                for slot, item in self.inventory.iteritems():
                    if item is not None:
                        inv = sf.RectangleShape(base_size)
                        inv.set_texture(sf.Texture.load_from_file(os.path.join(base_dir, item)))
                        rt.draw(inv)
                
                rt.display()
                self.cached_inv[anim['name']] = rt.texture.copy_to_image()
                self.cached_inv[anim['name']].save_to_file("DEBUG_{0}.png".format(anim['name']))


    def load_animations(self, clock, animations_file = None):
        if animations_file is None:
            animations_file = self.animations_file
        else:
            self.animations_file = animations_file

        with open(animations_file, 'r') as af:
            anims = json.loads(af.read())

        for anim in anims:
            self.animations.update({anim['name']: {}})

        self.build_inventory_images()

        for anim in anims:
            log.debug("Animation: {0}_{1}".format(anim['name'],anim['direction']))

            frames = []
            for frame in anim['frames']:
                region = sf.IntRect(frame['x'], frame['y'], frame['width'], frame['height'])
                frames.append(AnimationFrame(sf.Texture.load_from_image(self.cached_inv[anim['name']]), frame['duration'], region))

            self.animations[anim['name']].update({anim['direction']: Animation(frames, clock)})

        log.debug(self.animations)

