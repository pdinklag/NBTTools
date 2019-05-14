#!/usr/bin/python3

import argparse
import gzip
import io
import json
import struct
import zlib

import nbt

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Minecraft MCA scan')
parser.add_argument('file')
args = parser.parse_args()

print('Non-empty chunks:')
with open(args.file, 'rb') as f:
    for z in range(0, 32):
        for x in range(0, 32):
            loc = struct.unpack('>i', f.read(4))[0]
            if loc != 0:
                print((x,z))
