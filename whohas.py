#!/usr/bin/python3
import argparse
import gzip
import json
import os
import re
import sys

import nbt

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description='Find players who have a certain named item in their inventory')

parser.add_argument('world')
parser.add_argument('name')
args = parser.parse_args()

# Make regex
pattern = re.compile(args.name)

# Check playerdata directory
playerdata_dir = os.path.join(args.world, 'playerdata')
if not os.path.isdir(playerdata_dir):
    print('Directory of world not found: ' + playerdata_dir)
    sys.exit(-1)

def scan_inventory(filename, pattern, inv, where):
    if inv:
        for item in inv.value:
            id = item.get('id').value
            display = item.get(['tag','display','Name'])
            if display:
                # what idiot at Mojang puts JSON into NBT tags?
                display = json.loads(display.value)
                if 'text' in display:
                    display = display['text']
                    if re.search(pattern, display):
                        print(filename + ': ' +
                            display + ' (' + id + ')' +
                            ' found in ' + where)

# Process all players
for filename in os.listdir(playerdata_dir):
    try:
        # Read player data
        with gzip.open(os.path.join(playerdata_dir, filename), 'rb') as f:
            player = nbt.read(f)[0]

        # check inventory
        scan_inventory(
            filename, pattern, player.get('Inventory'), 'Inventory')
        scan_inventory(
            filename, pattern, player.get('EnderItems'), 'Ender Chest')

    except Exception as e:
        print('Error processing ' + filename + ': ' + str(e))
