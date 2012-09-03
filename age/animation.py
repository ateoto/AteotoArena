import sfml as sf

class AnimationFrame(object):
    def __init__(self, texture, duration, region):
        self.texture = texture
        self.duration = duration
        if region is None:
            self.region = sf.IntRect(0,0,texture.width, texture.height)
        else:
            self.region = region

class Animation(sf.Sprite):
    def __init__(self, frames, clock, loop = False):
        self.clock = clock
        self.frames = frames
        self.current_frame = 0
        self.loop = loop
        super(Animation, self).__init__(self.frames[self.current_frame].texture)
        self.texture_rect = self.frames[self.current_frame].region

    def animate(self, dt):
        self.texture = self.frames[self.current_frame].texture
        self.texture_rect = self.frames[self.current_frame].region
        self.current_frame += 1
        frame_count = len(self.frames)

        if self.current_frame > frame_count and self.loop:
            self.current_frame = 0

        if self.current_frame <= frame_count:
            self.clock.schedule_once(self.animate, self.frames[self.current_frame].duration)

    def stop_animation(self):
        self.clock.unschedule(self.animate)
