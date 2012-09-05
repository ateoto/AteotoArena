import age.game
import age.actor
import age.animation

import sfml as sf

import logging as log
import sys
import argparse
import os

parser = argparse.ArgumentParser(description='AteotoArena')
parser.add_argument('--debug', dest='debug', action='store_true',
                    help='Show debugging information')
parser.add_argument('--fullscreen', dest='fullscreen', action='store_true',
                    help='Start in fullscreen mode')

args = parser.parse_args()

if args.debug:
    log.basicConfig(level=log.DEBUG)
if args.fullscreen:
    res = sf.Vector2f(1920,1080)
else:
    res = sf.Vector2f(800, 600)

g = age.game.Game('AteotoArena', res, fullscreen = args.fullscreen)

render_area = sf.IntRect(0, 0, g.window.width * 2, g.window.height * 2)

g.load_map('data/maps/0_0.tmx', render_area)
g.player = age.actor.PCActor(location = g.level.objects['pc_initial_spawn'].position)
g.player.load_inventory('inventory.json') #This is temporary until networked.
g.load_animations('data/actors/human_male/animations.json')

g.run()
