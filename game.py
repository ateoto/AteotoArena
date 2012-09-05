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
g.player = age.actor.PCActor(g.level.objects['pc_initial_spawn'].position)
g.player.load_inventory('inventory.json') #This is temporary until networked.
g.player.load_animations('data/actors/human_male/animations.json', g.clock)

walkcycle_dir = 'data/actors/human_male/walkcycle'

textures = [
        os.path.join(walkcycle_dir, 'BODY_animation.png'),
        os.path.join(walkcycle_dir, 'FEET_shoes_brown.png'),
        os.path.join(walkcycle_dir, 'LEGS_pants_greenish.png'),
        os.path.join(walkcycle_dir, 'TORSO_leather_armor_torso.png'),
        os.path.join(walkcycle_dir, 'TORSO_leather_armor_shoulders.png'),
        os.path.join(walkcycle_dir, 'TORSO_leather_armor_bracers.png'),
]

g.load_animations('animations.json', textures)

g.run()
