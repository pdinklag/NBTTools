#!/usr/bin/python3

import argparse
import gzip
import json

import nbt

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Minecraft NBT dump')
parser.add_argument('file')
args = parser.parse_args()

def nbtdump(f):
    data = nbt.read(f)
    print(json.dumps(data.dump(), indent=4, sort_keys=True))

# Read NBT file and dump as JSON
try:
    with gzip.open(args.file, 'rb') as f:
        nbtdump(f)
except OSError:
    # not gzipped
    with open(args.file, 'rb') as f:
        nbtdump(f)
