import age.game
import age.actor

import sfml as sf
import logging as log
import sys
import argparse

parser = argparse.ArgumentParser(description='AteotoArena')
parser.add_argument('--debug', dest='debug', action='store_true',
                    help='Show debugging information')

args = parser.parse_args()

if args.debug:
    log.basicConfig(level=log.DEBUG)

g = age.game.Game('AteotoArena')

area = sf.IntRect(0,0,g.window.width, g.window.height)

# Login to server.
# Get the player information from the Server and load it.

g.load_map('data/maps/0_0.tmx', area)
g.player_character = age.actor.PCActor(g.level.objects['pc_initial_spawn'].position)
g.player_character.sprite.set_texture_rect(sf.IntRect(0, 128, 64, 64))

g.run()
