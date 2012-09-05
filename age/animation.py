import sfml as sf
import logging as log
import json

class AnimationFrame(object):
    def __init__(self, texture, duration, region = None):
        self.texture = texture
        self.duration = duration
        self.region = region

class Animation(object):
    def __init__(self, frames, clock):
        self.clock = clock
        self.frames = frames
        self.current_frame = 0
        self.sprite = sf.Sprite(self.frames[self.current_frame].texture)
        self.sprite.set_texture_rect(self.frames[self.current_frame].region)
        log.debug('Animation loaded. {0} frames.'.format(len(self.frames)))

    @classmethod
    def load_from_dict(self, animation_dict, texturelist, clock, drop):
        log.debug(animation_dict['name'])
        
        # First step is to build the compiled textures. So lets load them up.
        sprites = []
        sizes = []

        for t in texturelist:
            s = sf.Sprite(sf.Texture.load_from_file(t))
            sprites.append(s)
            sizes.append(sf.Vector2f(s.texture.width, s.texture.height))

        largest_x = sorted(sizes, key = lambda k: k.x)[0].x
        largest_y = sorted(sizes, key = lambda k: k.y)[0].y
        

        # I haven't had the issue yet, but there's going to be a problem when
        # there are different sizes for layers, the smaller ones won't
        # line up.

        rt = sf.RenderTexture(576, 256)
        log.debug(rt)
        rt.clear(sf.Color.TRANSPARENT)
        for s in sprites:
            rt.draw(s)
        
        rt.display()
    
        drop.append(rt)
        log.debug('copying image')
        compiled_image = rt.texture.copy_to_image()
        
        compiled_image.save_to_file("debug_{0}.png".format(animation_dict['name']))
        compiled_texture = sf.Texture.load_from_image(compiled_image)
        drop.append(compiled_texture)

        frames = []

        for frame in animation_dict['frames']:
            area = sf.IntRect(frame['x'], frame['y'], frame['width'], frame['height'])
            frames.append(AnimationFrame(compiled_texture, frame['duration'], area))
        
        drop.append(frames)

        return Animation(frames, clock)

    def save_to_dict(self, name):
        ani = { 'name' : name,
                'textures' : [],
                'frames': []}
        for frame in self.frames:
            ani['frames'].append({
                    'x': frame.region.left,
                    'y': frame.region.top,
                    'width': frame.region.width,
                    'height': frame.region.height
                    })

        return ani

    def animate(self, dt = None, loop = False):
        last_frame = False
        self.sprite.set_texture(self.frames[self.current_frame].texture)
        self.sprite.set_texture_rect(self.frames[self.current_frame].region)
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
