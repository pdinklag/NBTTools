import struct

ID_END        = 0
ID_BYTE       = 1
ID_SHORT      = 2
ID_INT        = 3
ID_LONG       = 4
ID_FLOAT      = 5
ID_DOUBLE     = 6
ID_BYTE_ARRAY = 7
ID_STRING     = 8
ID_LIST       = 9
ID_COMPOUND   = 10
ID_INT_ARRAY  = 11
ID_LONG_ARRAY = 12

class NBTException(Exception):
    pass

# base
class Tag:
    def dump(self):
        return self.value

# 0x00
class End(Tag):
    def __init__(self, name):
        pass

    def read(self, f):
        pass

# 0x01
class Byte(Tag):
    def __init__(self, name):
        self.name = name
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('b', f.read(1))[0]

# 0x02
class Short(Tag):
    def __init__(self, name):
        self.name = name
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('>h', f.read(2))[0]

# 0x03
class Int(Tag):
    def __init__(self, name):
        self.name = name
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('>i', f.read(4))[0]

# 0x04
class Long(Tag):
    def __init__(self, name):
        self.name = name
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('>q', f.read(8))[0]

# 0x05
class Float(Tag):
    def __init__(self, name):
        self.name = name
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('>f', f.read(4))[0]

# 0x06
class Double(Tag):
    def __init__(self, name):
        self.name = name
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('>d', f.read(8))[0]

# 0x07
class ByteArray(Tag):
    def __init__(self, name):
        self.name = name
        self.value = []

    def read(self, f):
        self.value = []

        num = struct.unpack('>i', f.read(4))[0]
        while num > 0:
            self.value.append(struct.unpack('b', f.read(1))[0])
            num -= 1

# 0x08
class String(Tag):
    def __init__(self, name):
        self.name = name
        self.value = ''

    def read(self, f):
        stringLen = struct.unpack('>h', f.read(2))[0]
        if stringLen > 0:
            self.value = f.read(stringLen).decode('utf-8')
        else:
            self.value = ''

# 0x09
class List(Tag):
    def __init__(self, name):
        self.name = name
        self.value = []

    def read(self, f):
        self.value = []

        typeId   = struct.unpack('b', f.read(1))[0]
        num = struct.unpack('>i', f.read(4))[0]
        while num > 0:
            item = create(typeId)
            item.read(f)
            self.value.append(item)
            num -= 1

    def dump(self):
        data = []
        for item in self.value:
            data.append(item.dump())

        return data

# 0x0A
class Compound(Tag):
    def __init__(self, name):
        self.name = name
        self.value = {}

    def read(self, f):
        self.value = {}
        while True:
            item = read(f)
            if isinstance(item, End):
                break
            else:
                self.value[item.name] = item

    def dump(self):
        data = {}
        for _, item in self.value.items():
            data[item.name] = item.dump()

        return data

# 0x0B
class IntArray(Tag):
    def __init__(self, name):
        self.name = name
        self.value = []

    def read(self, f):
        self.value = []

        num = struct.unpack('>i', f.read(4))[0]
        while num > 0:
            self.value.append(struct.unpack('>i', f.read(4))[0])
            num -= 1

# 0x0C
class LongArray(Tag):
    def __init__(self, name):
        self.name = name
        self.value = []

    def read(self, f):
        self.value = []

        num = struct.unpack('>i', f.read(4))[0]
        while num > 0:
            self.value.append(struct.unpack('>q', f.read(8))[0])
            num -= 1

# get NBT from id
def create(tagId, name = ''):
    if tagId == ID_END:          return End(name)
    elif tagId == ID_BYTE:       return Byte(name)
    elif tagId == ID_SHORT:      return Short(name)
    elif tagId == ID_INT:        return Int(name)
    elif tagId == ID_LONG:       return Long(name)
    elif tagId == ID_FLOAT:      return Float(name)
    elif tagId == ID_DOUBLE:     return Double(name)
    elif tagId == ID_BYTE_ARRAY: return ByteArray(name)
    elif tagId == ID_STRING:     return String(name)
    elif tagId == ID_LIST:       return List(name)
    elif tagId == ID_COMPOUND:   return Compound(name)
    elif tagId == ID_INT_ARRAY:  return IntArray(name)
    elif tagId == ID_LONG_ARRAY: return LongArray(name)
    else: raise NBTException('invalid tag id ' + str(tagId))

# read NBT
def read(f):
    tagId = struct.unpack('b', f.read(1))[0]
    name = ''
    if tagId > ID_END:
        tagNameLen = struct.unpack('>h', f.read(2))[0]
        if tagNameLen > 0:
            name = f.read(tagNameLen).decode('utf-8')

    tag = create(tagId, name)
    tag.read(f)
    return tag

