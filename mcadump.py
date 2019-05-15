#!/usr/bin/python3

import argparse
import json
import struct

import mca

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Minecraft MCA dump')
parser.add_argument('file')
parser.add_argument('x', type=int)
parser.add_argument('z', type=int)
args = parser.parse_args()

if args.x < 0 or args.x >= 32 or args.z < 0 or args.z >= 32:
    print('x/z must be between 0 and 31')
    exit(1)

i = args.x + args.z * 32

with open(args.file, 'rb') as f:
    # get location
    f.seek(4 * i)
    loc = struct.unpack('>i', f.read(4))[0]
    
    if loc == 0:
        print('chunk is empty')
        exit(0)
    
    # extract offset and go there
    off = 4096 * (loc >> 8)
    f.seek(off)
    
    chunk = mca.Region.read_chunk(f)
    if chunk:
        print(json.dumps(chunk.dump(), indent=4, sort_keys=True))
    else:
        print('failed to read chunk')
