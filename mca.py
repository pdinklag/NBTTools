import gzip
import io
import struct
import zlib

import nbt

class Region:
    CHUNKS_X = 32
    CHUNKS_Z = 32
    NUM_CHUNKS = CHUNKS_X * CHUNKS_Z # 1024
    SECT_SIZE = 4 * NUM_CHUNKS       # 4 KiB
    
    def foreach_chunk(visit):
        i = 0
        for z in range(0, Region.CHUNKS_Z):
            for x in range(0, Region.CHUNKS_X):
                visit(x, z, i)
                i += 1
    
    def chunk_index(x, z):
        return Region.CHUNKS_Z * z + x

    def read_chunk_offsets(f):
        offsets = []
        for z in range(0, Region.CHUNKS_Z):
            for x in range(0, Region.CHUNKS_X):
                location = struct.unpack('>i', f.read(4))[0]
                offsets.append(Region.SECT_SIZE * (location >> 8))

        return offsets

    def read_chunk(f):
        # read header
        num  = struct.unpack('>i', f.read(4))[0] - 1
        comp = struct.unpack('b', f.read(1))[0]
        
        # read data and decompress
        data = f.read(num)
        if comp == 1:
            data = gzip.decompress(data)
        elif comp == 2:
            data = zlib.decompress(data)
        else:
            return False

        # read NBT
        with io.BytesIO(data) as fdata:
            return nbt.read(fdata)[0]
    
    def __init__(self):
        self.chunks = []

    def __str__(self):
        return 'Region (X=' + str(self.x) + ',Z=' + str(self.y) + ')'

    def read(self, f):
        # load chunk offsets
        offsets = Region.read_chunk_offsets(f)

        i = 0
        for z in range(0, Region.CHUNKS_Z):
            for x in range(0, Region.CHUNKS_X):
                off = offsets[i]
                if off > 0:
                    # jump to chunk data
                    f.seek(off)
                    
                    # read chunk header
                    self.chunks.append(Region.read_chunk(f))
                else:
                    self.chunks.append(False)

                i += 1

    def chunk(self, x, z):
        return self.chunks[Region.chunk_index(x, z)]
