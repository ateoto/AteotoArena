import sfml as sf
import logging as log
import json

class AnimationFrame(object):
    def __init__(self, duration, region, texture = None):
        self.duration = duration
        self.region = region
        if texture is not None:
            self.drawable = sf.RectangleShape((texture.width, texture.height))
            self.drawable.set_texture(texture)


class Animation(object):
    def __init__(self, frames, clock):
        self.clock = clock
        self.frames = frames
        self.current_frame = 0
        self.drawable = self.frames[self.current_frame].drawable
        self.drawable.texture_rect = self.frames[self.current_frame].region
        log.debug('Animation loaded. {0} frames.'.format(len(self.frames)))

    def animate(self, dt = None, loop = False):
        last_frame = False
        self.drawable = self.frames[self.current_frame].drawable
        self.drawable.texture_rect = self.frames[self.current_frame].region
        #log.debug(self.texture_rect)
        self.current_frame += 1
        frame_count = len(self.frames)

        if self.current_frame >= frame_count and not loop:
            self.current_frame = 0
            last_frame = True

        if self.current_frame >= frame_count and loop:
            self.current_frame = 0

        if not last_frame or loop:
            self.clock.schedule_once(self.animate, self.frames[self.current_frame].duration, loop = loop)

    def stop_animation(self):
        self.clock.unschedule(self.animate)
