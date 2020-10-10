#!/usr/bin/python3

import argparse

import mca

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Minecraft MCA scan')
parser.add_argument('file')
args = parser.parse_args()

with open(args.file, 'rb') as f:
    offsets = mca.Region.read_chunk_offsets(f)

def visit(x, z, i):
    global offsets
    if offsets[i] != 0:
        print((x,z))

print('Non-empty chunks:')
mca.Region.foreach_chunk(visit)
