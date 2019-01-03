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

def read_str(f):
    strlen = struct.unpack('>h', f.read(2))[0]
    if strlen > 0:
        return f.read(strlen).decode('utf-8')
    else:
        return ''

def write_str(f, str):
    strlen = len(str)
    f.write(struct.pack('>h', strlen))
    if strlen > 0:
        f.write(str.encode('utf-8'))

# base
class Tag:
    def __str__(self):
        return type(self).__name__ + '(' + str(self.value) + ')'

    def __repr__(self):
        return self.__str__()

    def get(self, path):
        if len(path) > 0:
            raise NBTException('tag is not a container')
        else:
            return self

    def dump(self):
        return self.value

# 0x00
class End(Tag):
    def __init__(self):
        self.id = ID_END

    def __str__(self):
        return 'End()'

    def read(self, f):
        pass

    def write(self, f):
        pass

# 0x01
class Byte(Tag):
    def __init__(self):
        self.id = ID_BYTE
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('b', f.read(1))[0]

    def write(self, f):
        f.write(struct.pack('b', self.value))

# 0x02
class Short(Tag):
    def __init__(self):
        self.id = ID_SHORT
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('>h', f.read(2))[0]

    def write(self, f):
        f.write(struct.pack('>h', self.value))

# 0x03
class Int(Tag):
    def __init__(self):
        self.id = ID_INT
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('>i', f.read(4))[0]

    def write(self, f):
        f.write(struct.pack('>i', self.value))

# 0x04
class Long(Tag):
    def __init__(self):
        self.id = ID_LONG
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('>q', f.read(8))[0]

    def write(self, f):
        f.write(struct.pack('>q', self.value))

# 0x05
class Float(Tag):
    def __init__(self):
        self.id = ID_FLOAT
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('>f', f.read(4))[0]

    def write(self, f):
        f.write(struct.pack('>f', self.value))

# 0x06
class Double(Tag):
    def __init__(self):
        self.id = ID_DOUBLE
        self.value = 0

    def read(self, f):
        self.value = struct.unpack('>d', f.read(8))[0]

    def write(self, f):
        f.write(struct.pack('>d', self.value))

# 0x07
class ByteArray(Tag):
    def __init__(self):
        self.id = ID_BYTE_ARRAY
        self.value = []

    def read(self, f):
        self.value = []

        num = struct.unpack('>i', f.read(4))[0]
        while num > 0:
            self.value.append(struct.unpack('b', f.read(1))[0])
            num -= 1

    def write(self, f):
        f.write(struct.pack('>i', len(self.value)))
        for b in self.value:
            f.write(struct.pack('b', b))

# 0x08
class String(Tag):
    def __init__(self):
        self.id = ID_STRING
        self.value = ''

    def read(self, f):
        self.value = read_str(f)

    def write(self, f):
        write_str(f, self.value)

# 0x09
class List(Tag):
    def __init__(self):
        self.id = ID_LIST
        self.itemTypeId = ID_END
        self.value = []

    def read(self, f):
        self.value = []
        self.itemTypeId = struct.unpack('b', f.read(1))[0]
        num = struct.unpack('>i', f.read(4))[0]
        while num > 0:
            item = create(self.itemTypeId)
            item.read(f)
            self.value.append(item)
            num -= 1

    def write(self, f):
        f.write(struct.pack('b', self.itemTypeId))
        f.write(struct.pack('>i', len(self.value)))
        for tag in self.value:
            tag.write(f)

    def get(self, path):
        if len(path) > 0:
            index = path[0]
            if index < len(self.value):
                return self.value[index].get(path[1:])
            else:
                return False
        else:
            return self

    def dump(self):
        data = []
        for item in self.value:
            data.append(item.dump())

        return data

# 0x0A
class Compound(Tag):
    def __init__(self):
        self.id = ID_COMPOUND
        self.value = {}

    def read(self, f):
        self.value = {}
        while True:
            (item, name) = read(f)
            if isinstance(item, End):
                break
            else:
                self.value[name] = item

    def write(self, f):
        for name, item in self.value.items():
            write(f, item, name)

        write(f, End())

    def get(self, path):
        if len(path) > 0:
            name = path[0]
            if name in self.value:
                return self.value[name].get(path[1:])
            else:
                return False
        else:
            return self

    def dump(self):
        data = {}
        for name, item in self.value.items():
            data[name] = item.dump()

        return data

# 0x0B
class IntArray(Tag):
    def __init__(self):
        self.id = ID_INT_ARRAY
        self.value = []

    def read(self, f):
        self.value = []

        num = struct.unpack('>i', f.read(4))[0]
        while num > 0:
            self.value.append(struct.unpack('>i', f.read(4))[0])
            num -= 1

    def write(self, f):
        f.write(struct.pack('>i', len(self.value)))
        for i in self.value:
            f.write(struct.pack('>i', i))
# 0x0C
class LongArray(Tag):
    def __init__(self):
        self.id = ID_LONG_ARRAY
        self.value = []

    def read(self, f):
        self.value = []

        num = struct.unpack('>i', f.read(4))[0]
        while num > 0:
            self.value.append(struct.unpack('>q', f.read(8))[0])
            num -= 1

    def write(self, f):
        f.write(struct.pack('>i', len(self.value)))
        for l in self.value:
            f.write(struct.pack('>q', l))

# get NBT from id
def create(tagId):
    if tagId == ID_END:          return End()
    elif tagId == ID_BYTE:       return Byte()
    elif tagId == ID_SHORT:      return Short()
    elif tagId == ID_INT:        return Int()
    elif tagId == ID_LONG:       return Long()
    elif tagId == ID_FLOAT:      return Float()
    elif tagId == ID_DOUBLE:     return Double()
    elif tagId == ID_BYTE_ARRAY: return ByteArray()
    elif tagId == ID_STRING:     return String()
    elif tagId == ID_LIST:       return List()
    elif tagId == ID_COMPOUND:   return Compound()
    elif tagId == ID_INT_ARRAY:  return IntArray()
    elif tagId == ID_LONG_ARRAY: return LongArray()
    else: raise NBTException('invalid tag id ' + str(tagId))

# read NBT
def read(f):
    tagId = struct.unpack('b', f.read(1))[0]
    name = ''
    if tagId > ID_END:
        name = read_str(f)

    tag = create(tagId)
    tag.read(f)
    return (tag, name)

# write NBT
def write(f, tag, name = ''):
    f.write(struct.pack('b', tag.id))
    if tag.id > ID_END:
        write_str(f, name)

    tag.write(f)
