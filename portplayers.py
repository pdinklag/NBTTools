#!/usr/bin/python3

import argparse
import gzip
import json
import os
import shutil
import sys

import nbt

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description='Port players from one world to another')

parser.add_argument('old_world')
parser.add_argument('new_world')
parser.add_argument('--filter-dimension', type=str, default='')
args = parser.parse_args()

# Check old playerdata directory
old_playerdata_dir = os.path.join(args.old_world, 'playerdata')
if not os.path.isdir(old_playerdata_dir):
    print('Directory of old world not found: ' + old_playerdata_dir)
    sys.exit(-1)

# Check new world directory
if not os.path.isdir(args.new_world):
    print('Directory of new world not found: ' + args.new_world)
    sys.exit(-1)

# test if directories are the same
backup = (args.old_world == args.new_world)

# Check new world's level.dat
level_file = os.path.join(args.new_world, 'level.dat')
if not os.path.isfile(level_file):
    print('New world\'s level.dat not found: ' + level_file)

# Load new world's level.dat
with gzip.open(level_file, 'rb') as f:
    level = nbt.read(f)[0].get(['Data'])

# Find or create new playerdata directory
playerdata_dir = os.path.join(args.new_world, 'playerdata')
if not os.path.isdir(playerdata_dir):
    os.mkdir(playerdata_dir)

# Get spawn of new world
spawn = [level.get(['SpawnX']).value,
         level.get(['SpawnY']).value,
         level.get(['SpawnZ']).value]

print('Spawn of new world is at ' + str(spawn))

# Process all players
for filename in os.listdir(old_playerdata_dir):
    if not filename.endswith('.dat'):
        continue

    try:
        # Read player data
        with gzip.open(os.path.join(old_playerdata_dir, filename), 'rb') as f:
            player = nbt.read(f)[0]

        # filter
        if len(args.filter_dimension) > 0 and str(player.get('Dimension').value) != args.filter_dimension:
            continue
        
        # print message
        print('Porting ' + filename + ' ...')

        # relocate player to new world
        player.set('SpawnX', nbt.Int(spawn[0])) # reset player's spawn
        player.set('SpawnY', nbt.Int(spawn[1]))
        player.set('SpawnZ', nbt.Int(spawn[2]))
        player.set('SpawnDimension', nbt.String('minecraft:overworld'))
        player.set('SpawnForced', nbt.Byte(1))  # force this new spawn
        player.set('Dimension', nbt.String('minecraft:overworld'))     # teleport to overworld
        player.set('Pos', nbt.List(nbt.ID_DOUBLE, [
            nbt.Double(spawn[0]),
            nbt.Double(spawn[1]),
            nbt.Double(spawn[2])])) # "tp" to new spawn

        # reset player state
        player.set('Air', nbt.Short(300))
        player.set('FallDistance', nbt.Float(0.0))
        player.set('FallFlying', nbt.Byte(0))
        player.set('Fire', nbt.Short(-20)) # yes, this is the default
        player.set('foodExhaustionLevel', nbt.Float(0.0))
        player.set('foodLevel', nbt.Int(20))
        player.set('foodSaturationLevel', nbt.Float(5.0)) # default
        player.set('foodTickTimer', nbt.Int(0))
        player.set('Health', nbt.Float(20.0))
        player.set('Invulnerable', nbt.Byte(0))
        player.set('Motion', nbt.List(nbt.ID_DOUBLE,
            [nbt.Double(0.0), nbt.Double(0.0), nbt.Double(0.0)]))
        player.set('OnGround', nbt.Byte(1))
        player.set('playerGameType', nbt.Int(0)) # survival
        player.set('Score', nbt.Int(0))
        player.set('Sleeping', nbt.Byte(0))

        player.remove('ActiveEffects') # remove any active effects
        player.remove('Riding') # we're also no longer riding anything

        # maybe create backup if old and new world are the same
        outFilename = os.path.join(playerdata_dir, filename)
        
        if backup:
            shutil.copyfile(outFilename, outFilename + '.bak')

        # write player data
        with gzip.open(outFilename, 'wb') as f:
            nbt.write(f, player)

    except Exception as e:
        print('Error processing ' + filename + ': ' + str(e))
