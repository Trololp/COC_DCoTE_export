from struct import unpack
import sys

#parser for NifExport.pc.naf file

def remove_repeated_zeros(in_str):  
    return in_str.rstrip(b'\x00')



def main(argv):
    f = open(argv[0], 'rb')
    amount = unpack("I", f.read(4))[0]
    
    print("nVertexBuffers = ", amount)
    
    for _ in range(amount):
        print("pos ", hex(f.tell()))
        vertex_count = unpack("I", f.read(4))[0]
        flag = unpack("B", f.read(1))[0]
        print("\tid =", _*2, " flag", flag, "vertex_count = ", vertex_count)
        sz = 20
        if flag:
            sz = 24
        f.seek(sz * vertex_count, 1)
        
        print("pos ", hex(f.tell()))
        vertex_count = unpack("I", f.read(4))[0]
        flag = unpack("B", f.read(1))[0]
        print("\tid =", _*2+1, " flag", flag, "vertex_count = ", vertex_count)
        sz = 20
        if flag:
            sz = 24
        f.seek(sz * vertex_count, 1)
        
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        
    amount_textures = unpack("I", f.read(4))[0]
    for _ in range(amount_textures):
        idx = unpack("H", f.read(2))[0]
        sz = unpack("I", f.read(4))[0]
        print("\tidx = ", idx, "sz = ", sz)
        f.seek(sz, 1)
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        

    print("pos ", hex(f.tell()))
   
    f.close()

if __name__ == "__main__":
   main(sys.argv[1:])