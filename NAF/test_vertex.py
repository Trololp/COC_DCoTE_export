from struct import unpack
import sys


def remove_repeated_zeros(in_str):  
    return in_str.rstrip(b'\x00')

def dump_vertexes(f, vertex_count):
    for _ in range(vertex_count):
        xyz = unpack("HHH", f.read(6))
        f.seek(2, 1) # 0
        #f.seek(4, 1) # color
        rgba = unpack("BBBB", f.read(4))
        UV_1 = unpack("HH", f.read(4))
        UV_2 = unpack("HH", f.read(4))
        #UV_3 = unpack("HH", f.read(4))
        print("x =", xyz[0], "y =" ,xyz[1], "z =", xyz[2], "U = ", UV_1[0], "V = ", UV_1[1], "R ", rgba[0], "G ", rgba[1], "B ", rgba[2]) 

def main(argv):
    f = open(argv[0], 'rb')
    amount = unpack("I", f.read(4))[0]
    
    #print("nVertexBuffers = ", amount)
    
    for _ in range(amount):
        #print("pos ", hex(f.tell()))
        vertex_count = unpack("I", f.read(4))[0]
        flag = unpack("B", f.read(1))[0]
        print("\tid =", _*2, " flag", flag, "vertex_count = ", vertex_count)
        sz = 20
        if flag:
            sz = 24
        dump_vertexes(f, vertex_count)
        
        break;
    

    print("pos ", hex(f.tell()))
   
    f.close()

if __name__ == "__main__":
   main(sys.argv[1:])