import sfml as sf
from .map import TiledMap
from .clock import GameClock
from .ui import UI
from .animation import Animation
import logging as log

import json

class Game(object):
    def __init__(self, title, res = sf.Vector2f(800, 600), fullscreen = False):
        if fullscreen:
            style = sf.Style.FULLSCREEN
        else:
            style = sf.Style.CLOSE

        self.clock = GameClock()
        self.window = sf.RenderWindow(sf.VideoMode(res.x, res.y), title, style)

        self.running = False
        self.player = None
        self.level = None
        self.ui = UI(sf.Vector2f(self.window.width, self.window.height))
        self.fullscreen = False
        self.show = sf.FloatRect(0,0,self.window.width, self.window.height)
        # Build scrolling borders
        w_percent = self.window.width * 0.30
        h_percent = self.window.height * 0.30
        self.scrollboxes = {'north': sf.IntRect(0, 0, self.window.width, h_percent),
                            'south': sf.IntRect(0, self.window.height - h_percent, self.window.width, h_percent),
                            'west': sf.IntRect(0 , h_percent, w_percent, self.window.height - h_percent * 2 ),
                            'east': sf.IntRect(self.window.width - w_percent, h_percent, w_percent, self.window.height - h_percent * 2)}

    def load_map(self, map_file, area):
        self.window.active = False
        self.level = TiledMap(map_file, area)
        self.window.active = True

    def load_animations(self, animations_file, textures):
        # This is just to see if RenderTextures will work from here.
        ani_dict = json.loads(open(animations_file, 'r').read())
        self.player.animations.update({
            'idle' : {
                'north': Animation.load_from_dict(ani_dict['idle']['north'], textures, self.clock),
                'west': Animation.load_from_dict(ani_dict['idle']['west'], textures, self.clock),
                'south': Animation.load_from_dict(ani_dict['idle']['south'], textures, self.clock),
                'east': Animation.load_from_dict(ani_dict['idle']['east'], textures, self.clock)
            },
            'walk' : {
                'north' : Animation.load_from_dict(ani_dict['walk']['north'], textures, self.clock),
                'west' : Animation.load_from_dict(ani_dict['walk']['west'], textures, self.clock),
                'south' : Animation.load_from_dict(ani_dict['walk']['south'], textures, self.clock),
                'east' : Animation.load_from_dict(ani_dict['walk']['east'], textures, self.clock)
            }})
        self.window.active = True

    def update(self, dt):
        pass

    def handle_input(self, dt):
        for event in self.window.iter_events():
            if event.type == sf.Event.CLOSED:
                self.running = False

            if event.type == sf.Event.RESIZED:
                if self.level:
                    self.level.render_area = sf.IntRect(0, 0, event.width * 2, event.height * 2)

            if event.type == sf.Event.KEY_PRESSED:
                if event.code == sf.Keyboard.ESCAPE:
                    self.running = False

                elif event.code == sf.Keyboard.F11:
                    if not self.fullscreen:
                        self.window.create(sf.VideoMode.get_desktop_mode(), 'My Game', sf.Style.FULLSCREEN)
                    else:
                        self.window.create(sf.VideoMode(800, 600), 'My Game', sf.Style.CLOSE)

                    self.fullscreen = not self.fullscreen
                
                if self.player:
                    self.player.handle_keypress(event, dt)

    def run(self):
        self.running = True

        # Update the Clock every second
        self.clock.schedule_interval(self.clock.calculate_fps, 1)

        fps_text = sf.Text('FPS:', sf.Font.load_from_file('data/fonts/ttf-inconsolata.otf'), 20)


        """
        db_b_t = sf.RectangleShape((self.top_bound.width, self.top_bound.height))
        db_b_t.position = (self.top_bound.left, self.top_bound.top)
        db_b_t.fill_color = sf.Color(135,17,17,40)

        db_b_b = sf.RectangleShape((self.bottom_bound.width, self.bottom_bound.height))
        db_b_b.position = (self.bottom_bound.left, self.bottom_bound.top)
        db_b_b.fill_color = sf.Color(135, 17, 16, 40)

        db_b_l = sf.RectangleShape((self.left_bound.width, self.left_bound.height))
        db_b_l.position = (self.left_bound.left, self.left_bound.top)
        db_b_l.fill_color = sf.Color(135, 17, 16, 40)

        db_b_r = sf.RectangleShape((self.right_bound.width, self.right_bound.height))
        db_b_r.position = (self.right_bound.left, self.right_bound.top)
        db_b_r.fill_color = sf.Color(135, 17, 16, 40)
        """


        while self.running:
            delta_time = self.clock.update()
            """
            if delta_time.as_seconds() < 0.01:
                dt = 0.01
            else:
                dt = delta_time.as_seconds()
            """
            dt = delta_time.as_seconds()
            self.handle_input(dt)
            self.update(dt)

            self.window.clear(sf.Color(94, 94, 94))

            if self.level is not None:
                self.level.update(dt, self.player.show)
                self.window.draw(self.level)

            if self.player is not None:
                self.player.update(dt, self.scrollboxes)
                self.window.draw(self.player)

            """
            self.window.draw(db_b_t)
            self.window.draw(db_b_b)
            self.window.draw(db_b_l)
            self.window.draw(db_b_r)
            """

            fps_text.string = 'FPS: {0}'.format(self.clock.fps)
            self.window.draw(fps_text)

            self.window.display()
