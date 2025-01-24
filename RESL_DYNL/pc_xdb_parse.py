from struct import unpack
import sys
import os

# Call of Cthulhu DCoTE, .pc.xdb unpacker

# use this to unpack textures
# first run resl_parser and retrieve number of textures
# then edit this file and run to unpack textures from .pc.xdb file

NUMBER_OF_TEXTURES = 28

def swap_4b(_4b_arr):
    strochenka = bytearray(b'0000')
    strochenka[0] = _4b_arr[3]
    strochenka[1] = _4b_arr[2]
    strochenka[2] = _4b_arr[1]
    strochenka[3] = _4b_arr[0]
    return bytes(strochenka)

def chnk_name(offset, _4b_arr):
    
    name = f"{str(_4b_arr, 'utf-8')}_{offset}"
    return name

def dump_chunk(f, size, name):
    data = f.read(size)
    f2 = open(name, 'wb')
    f2.write(data)
    f2.close
    return

def main(argv):
    f = open(argv[0], 'rb');
    # textures
    os.makedirs("e_textures\\", exist_ok=True)
    
    print("texture")
    for _ in range(0, NUMBER_OF_TEXTURES):
        #print("pos", hex(f.tell()))
        idx = unpack("H", f.read(2))[0]
        magick = chnk_name(0, f.read(4))
        width = unpack("H", f.read(2))[0]
        height = unpack("H", f.read(2))[0]
        sz = unpack("I", f.read(4))[0]
        
        dump_chunk(f, sz, "e_textures\\" + str(idx) + ".dds")
        #f.seek(sz, 1)
        print("\t", idx, magick, width, height, sz)
    
    return
    print("vertex buffers")
    for _ in range(0, 25):
        unk =  unpack("H", f.read(2))[0]
        unk2 = unpack("I", f.read(4))[0]
        sz = unpack("I", f.read(4))[0]
        #dump_chunk(f, sz, str(f.tell()) + ".vtx")
        print("\t", unk, unk2, sz)
        f.seek(sz, 1)
    
    #print("offset", hex(f.tell()))
    
    f.close()

if __name__ == "__main__":
   main(sys.argv[1:])