from xml.etree import ElementTree

import sfml as sf

from base64 import b64decode
import StringIO
import gzip
import struct
import time
import os
import logging as log
import math

class TiledTile(object):
    def __init__(self, gid, texture):
        self.texture = texture
        self.gid = gid

class TiledCell(sf.Sprite):
    def __init__(self, pos, texture):
        super(TiledCell, self).__init__(texture)
        self.position = pos

class MapObject(object):
    def __init__(self, name, type, location, properties):
        self.name = name
        self.type = type
        self.location = location
        self.position = sf.Vector2f(self.location.left, self.location.top)
        self.properties = properties


class TiledLayerIterator:
    def __init__(self, layer):
        self.layer = layer
        self.i, self.j = 0, 0
    def next(self):
        if self.i == self.layer.rows:
            self.j += 1
            self.i = 0
        if self.j == self.layer.columns:
            raise StopIteration()
        value = self.layer[self.i, self.j]
        self.i += 1

        return value

class TiledLayer(object):
    def __init__(self, rows, columns):
        self.cells = {}
        self.rows = rows
        self.columns = columns
        self.visible = True
        self.drawable = sf.RectangleShape(sf.Vector2f(rows * 32, columns * 32))
        self.raw_data = ''

    def __iter__(self):
        return TiledLayerIterator(self)

    def __getitem__(self, pos):
        return self.cells.get(pos)

class TiledTileset:
    def __init__(self, first_gid, image):
        self.first_gid = first_gid
        self.image = sf.Image.load_from_file(image)
        self.tiles = {}
        local_id = 0
        for y in range(0, self.image.height / 32):
            for x in range(0, self.image.width / 32):
                global_id = int(self.first_gid) + local_id
                area = sf.IntRect(x * 32, y * 32, 32, 32)
                tile_texture = sf.Texture.load_from_image(self.image, area)
                self.tiles.update({global_id : tile_texture})
                local_id += 1

class TiledMap:
    def __init__(self, filename, area = None):
        self.layers = []
        self.tiles = {}
        self.objects = {}
        self.area = area
        self.load_started = time.time()
        self.load_from_file(filename)

    def load_from_file(self, filename):
        tree = ElementTree.parse(filename)
        root = tree.getroot()

        map_dir = os.path.dirname(filename)

        self.width = int(root.attrib.get('width'))
        self.height = int(root.attrib.get('height'))
        self.tilewidth = int(root.attrib.get('tilewidth'))
        self.tileheight = int(root.attrib.get('tileheight'))
        self.pixel_width = int(self.width * self.tilewidth)
        self.pixel_height = int(self.height * self.tileheight)

        # Need to load tilesets.
        for tileset in root.findall('tileset'):
            firstgid = tileset.attrib.get('firstgid')
            source = tileset.attrib.get('source')
            tileset_file = os.path.join(map_dir, source)
            ts_tree = ElementTree.parse(os.path.join(map_dir, source))
            ts_root = ts_tree.getroot()
            image = ts_root.findall('image')[0].attrib.get('source')
            image = os.path.join(map_dir, image)
            ts = TiledTileset(firstgid, image)
            self.tiles.update(ts.tiles)

        log.info('Tilesets loaded')

        for layer in root.findall('layer'):
            tl = TiledLayer(self.width, self.height)
            tl.name = layer.attrib.get('name')

            load_start_time = time.time()
            data = layer.find('data').text.rstrip().lstrip()
            data = b64decode(data)
            data = gzip.GzipFile(fileobj=StringIO.StringIO(data))
            data = data.read()
            log.debug(len(data))
            data = struct.unpack('<%di' % (len(data)/4,), data)
            log.debug(len(data))
            tl.raw_data = data
            log.debug("Unpacked data in {0} seconds".format(time.time() - load_start_time))

            drawable_x_range = range(self.area.left / 32, int(math.ceil(self.area.width / 32)) + 1)
            drawable_y_range = range(self.area.top / 32, int(math.ceil(self.area.height / 32)) + 1)

            for i, gid in enumerate(data):
                if gid < 1: continue
                x = i  % self.width
                y = i // self.width
 
                if x in drawable_x_range and y in drawable_y_range:
                    if gid in self.tiles.keys():
                        tl.cells[x,y] = TiledCell((x * 32, y * 32), self.tiles[gid])
            log.debug("Finished Loading data in {0} seconds.".format(time.time() - load_start_time))
    

            render_start_time = time.time()
            rt = sf.RenderTexture(self.area.width, self.area.height)
            rt.clear(sf.Color.TRANSPARENT)
    
            for y in drawable_y_range:
                for x in drawable_x_range:
                    cell = tl[x,y]

                    if cell is not None:
                        rt.draw(cell)
            log.debug("Finished rendering layer in {0} seconds.".format(time.time() - render_start_time))
            """
            for cell in tl:
                if cell is not None:
                    rt.draw(cell)
            """

            rt.display()
            tl.drawable.set_texture(sf.Texture.load_from_image(rt.texture.copy_to_image()))

            tl.drawable.size = sf.Vector2f(800, 600)
            tl.drawable.texture_rect = sf.IntRect(0,0,800,600)
            
            self.layers.append(tl)
            
        log.info('Layers loaded')

        for group in root.findall('objectgroup'):
            for object in group.findall('object'):
                o = MapObject(object.attrib.get('name'),
                                object.attrib.get('type'),
                                sf.IntRect(int(object.attrib.get('x')),
                                            int(object.attrib.get('y')),
                                            int(object.attrib.get('width')),
                                            int(object.attrib.get('height'))),
                                [])

                for properties in object.findall('properties'):
                    for property in properties.findall('property'):
                        o.properties.append({'name' : property.attrib.get('name'),
                                             'value': property.attrib.get('value')})

                self.objects.update({o.name: o})

        log.info('Objects loaded')

        self.load_finished = time.time()
        load_time = self.load_finished - self.load_started
        log.info('Level finished loading in {0} seconds.'.format(load_time))

    def update(self, player):
        """
        Here we set the map area to the player's location, determine if we need to load more of the map, and so on.
        """
        pass

    def draw(self, target, states):
        for layer in self.layers:
            if layer.visible:
                target.draw(layer.drawable)
