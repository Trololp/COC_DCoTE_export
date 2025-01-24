from struct import unpack
import sys
import os

# this script will extract textures from NifExport.pc.naf file
# textures will be in .dds format
# Usage: NAF_dump_textures.py NifExport.pc.naf

def remove_repeated_zeros(in_str):  
    return in_str.rstrip(b'\x00')

def dump_chunk(f, size, name):
    data = f.read(size)
    f2 = open(name, 'wb')
    f2.write(data)
    f2.close
    return

def main(argv):
    f = open(argv[0], 'rb')
    amount = unpack("I", f.read(4))[0]
    
    #print("nVertexBuffers = ", amount)
    
    for _ in range(amount):
        #print("pos ", hex(f.tell()))
        vertex_count = unpack("I", f.read(4))[0]
        flag = unpack("B", f.read(1))[0]
        #print("\tid =", _*2, " flag", flag, "vertex_count = ", vertex_count)
        sz = 20
        if flag:
            sz = 24
        f.seek(sz * vertex_count, 1)
        
        #print("pos ", hex(f.tell()))
        vertex_count = unpack("I", f.read(4))[0]
        flag = unpack("B", f.read(1))[0]
        #print("\tid =", _*2+1, " flag", flag, "vertex_count = ", vertex_count)
        sz = 20
        if flag:
            sz = 24
        f.seek(sz * vertex_count, 1)
        
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
    

    os.makedirs("textures//", exist_ok=True)
    
    amount_textures = unpack("I", f.read(4))[0]
    for _ in range(amount_textures):
        idx = unpack("H", f.read(2))[0]
        sz = unpack("I", f.read(4))[0]
        print("\tidx = ", idx, "sz = ", sz)
        dump_chunk(f, sz, "textures//" + str(idx) + ".dds")
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        

    print("pos ", hex(f.tell()))
   
    f.close()

if __name__ == "__main__":
   main(sys.argv[1:])