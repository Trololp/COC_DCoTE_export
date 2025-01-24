from struct import unpack
import sys

#parser for NifExport.naf file

def remove_repeated_zeros(in_str):  
    return in_str.rstrip(b'\x00')



def read_room_1(f):
    b_min = unpack("fff", f.read(12))
    b_max = unpack("fff", f.read(12))
    print("\tbounds min ", b_min[0], b_min[1], b_min[2])
    print("\tbounds max ", b_max[0], b_max[1], b_max[2])
    extra_planes = unpack("I", f.read(4))[0]
    for _ in range(extra_planes):
        plane_prob = unpack("ffff", f.read(16))

        amt2 = unpack("I", f.read(4))[0]
        print("\t\tplane ", plane_prob[0], plane_prob[1], plane_prob[2], plane_prob[3], "cnt ", amt2)
        #for __ in range(amt2):
        #    print(" ", unpack("I", f.read(4)))
        f.seek(4 * amt2, 1)

    plane_prob = unpack("ffff", f.read(16))
    print("\t\torigin ", plane_prob[0], plane_prob[1], plane_prob[2], plane_prob[3])
    

    
def read_room_2(f):
    amt = unpack("H", f.read(2))[0]
    print("amt ", amt)
    for _ in range(amt):
        unk = unpack("H", f.read(2))[0]
        cnt = unpack("H", f.read(2))[0]
        print("\tunk, cnt", unk, cnt)
        for _ in range(cnt):
            a = unpack("I", f.read(4))[0]
            b = unpack("I", f.read(4))[0]
            c = unpack("I", f.read(4))[0]
            print("\t\ta, b, c ", a, b, c)



def get_index_buffer_size(numFaces):
    flag = 0
    if numFaces & 0x40000000:
        print("detected odd index buffer")
        numFaces = numFaces & 0xBFFFFFFF
        flag = 1
    
    if flag:
        return numFaces
    else:
        return numFaces * 3
    

def read_primitive(f):
    flags = unpack("B", f.read(1))[0]
    origin = unpack("ffff", f.read(16))
    print("\tflags = ", flags) 
    print("\torigin ", origin[0], origin[1], origin[2], origin[3])
    unk1 = unpack("H", f.read(2))[0]
    unk2 = unpack("H", f.read(2))[0]
    numVerts = unpack("I", f.read(4))[0]
    unk3 = unpack("I", f.read(4))[0]
    MasterVBID = unpack("I", f.read(4))[0]
    unk4 = unpack("I", f.read(4))[0]
    numFaces = unpack("I", f.read(4))[0]
    print("\t ", unk1, unk2, "num_vtx = ", numVerts, unk3, "vbid = ", MasterVBID, unk4, "numFaces = ", numFaces)
    sz = get_index_buffer_size(numFaces)
    f.seek(sz * 2, 1)

def main(argv):
    f = open(argv[0], 'rb')
    version_prob = unpack("I", f.read(4))[0]
    rooms_count = unpack("I", f.read(4))[0]
    
    for _ in range(rooms_count):
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        read_room_1(f)

    for _ in range(rooms_count):
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        read_room_2(f)


    cSync = unpack("B", f.read(1))[0]
    if(cSync != ord('*')): # '*'
        print("Read sync failure")
    
    amt = unpack("H", f.read(2))[0]
    if(amt > 0):
        print("have unknown part!")
    f.seek(2, 1) # unknown
    for _ in range(amt):
        f.seek(10, 1) # unknown
   
    num_Tinfos = unpack("H", f.read(2))[0]
    print("numTinfos = ", num_Tinfos)
    for _ in range(num_Tinfos):
        a = unpack("H", f.read(2))[0]
        b = unpack("H", f.read(2))[0]
        c = unpack("H", f.read(2))[0]
        print("\t",_, a, b, c)
    

    
    num_index_buffers = unpack("I", f.read(4))[0]
    print("num_index_buffers = ", num_index_buffers)
    for _ in range(num_index_buffers):
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        read_primitive(f)
        

    print("pos ", hex(f.tell()))
   
    f.close()

if __name__ == "__main__":
   main(sys.argv[1:])