import sfml as sf
from .map import TiledMap
from .clock import GameClock
from .ui import UI
import logging as log

class Game(object):
    def __init__(self, title):
        self.clock = GameClock()
        self.window = sf.RenderWindow(sf.VideoMode(800, 600), title, sf.Style.CLOSE)

        self.running = False
        self.player_character = None
        self.level = None
        self.ui = UI(sf.Vector2f(self.window.width, self.window.height))
        self.fullscreen = False


    def load_map(self, map_file, area):
        self.window.active = False
        self.level = TiledMap(map_file, area)
        self.window.active = True

    def update(self, dt):
        pass

    def handle_input(self, dt):
        for event in self.window.iter_events():
            if event.type == sf.Event.CLOSED:
                self.running = False

            if event.type == sf.Event.KEY_PRESSED:
                if event.code == sf.Keyboard.ESCAPE:
                    self.running = False

                elif event.code == sf.Keyboard.F11:
                    if not self.fullscreen:
                        self.window.create(sf.VideoMode.get_desktop_mode(), 'My Game', sf.Style.FULLSCREEN)
                    else:
                        self.window.create(sf.VideoMode(800, 600), 'My Game', sf.Style.CLOSE)

                    self.fullscreen = not self.fullscreen
                    

                if self.player_character:
                    self.player_character.handle_input(event, dt)

    def run(self):
        self.running = True

        # Update the Clock every second
        self.clock.schedule_interval(self.clock.calculate_fps, 1)

        fps_text = sf.Text('FPS:', sf.Font.load_from_file('data/fonts/ttf-inconsolata.otf'), 20)

        while self.running:
            delta_time = self.clock.update()

            if delta_time.as_seconds() < 0.01:
                dt = 0.01
            else:
                dt = delta_time.as_seconds()
 
            self.handle_input(dt)
            self.update(dt)
            #print(self.clock.fps)

            self.window.clear(sf.Color(94, 94, 94))

            if self.level is not None:
                self.window.draw(self.level)

            if self.player_character is not None:
                self.window.draw(self.player_character)

            fps_text.string = 'FPS: {0}'.format(self.clock.fps)
            self.window.draw(fps_text)

            self.window.display()
