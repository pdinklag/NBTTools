#!/usr/bin/python3

import argparse
import gzip
import json

import nbt

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Minecraft NBT dump')
parser.add_argument('file')
args = parser.parse_args()

# Read NBT file and dump as JSON
with gzip.open(args.file, 'rb') as f:
    data = nbt.read(f)
    print(json.dumps(data.dump(), indent=4))

