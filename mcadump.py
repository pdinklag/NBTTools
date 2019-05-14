#!/usr/bin/python3

import argparse
import gzip
import io
import json
import struct
import zlib

import nbt

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
    
    # read chunk header
    num  = struct.unpack('>i', f.read(4))[0] - 1
    comp = struct.unpack('b', f.read(1))[0]
    
    # read and decompress chunk data
    data = f.read(num)
    if comp == 1:
        data = gzip.decompress(data)
    elif comp == 2:
        data = zlib.decompress(data)
    else:
        print('unknown chunk compression scheme')
        exit(1)
    
    with io.BytesIO(data) as fdata:
        chunk = nbt.read(fdata)[0]
        print(json.dumps(chunk.dump(), indent=4, sort_keys=True))
