from struct import unpack
import sys

# this script parse DYNL chunk

def remove_repeated_zeros(in_str):  
    return in_str.rstrip(b'\x00')

def get_index_buffer_size(numFaces):
    flag = 0
    if numFaces & 0x40000000:
        numFaces = numFaces & 0xBFFFFFFF
        print("\tdetected odd index buffer, numFaces = ", numFaces)
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
    return sz


def read_morph(f):
    version = unpack("B", f.read(1))[0]
    if(version != 101):
        print("\t\tmorph version != 101")
    m_numTargets = unpack("B", f.read(1))[0]
    m_numVertices = unpack("H", f.read(2))[0]
    print("m_numTargets =", m_numTargets, "m_numVertices =", m_numVertices)
    f.seek(12, 1) # unknown
    a = unpack("B", f.read(1))[0]
    b = unpack("B", f.read(1))[0]
    c = unpack("B", f.read(1))[0]
    flag = unpack("B", f.read(1))[0]
    if flag:
        for _ in range(m_numTargets):
            cnt = unpack("H", f.read(2))[0]
            f.seek(cnt * 2 * (a+b+c + 1), 1)
    else:
        f.seek(m_numTargets * m_numVertices * (a+b+c) * 2, 1)


def read_skinnned(f, index_sz):
    #print("position", hex(f.tell()))
    unk = unpack("I", f.read(4))[0]
    unk2 = unpack("I", f.read(4))[0]
    nFaces = unpack("I", f.read(4))[0]
    nVertices = unpack("I", f.read(4))[0]
    BoneCount = unpack("I", f.read(4))[0]
    uiVBID = unpack("I", f.read(4))[0]
    print("\tunk=", unk, "unk2 =", unk2, "nFaces = ", nFaces, "nVertices =", nVertices, "BoneCount = ", BoneCount, "VBID = ", uiVBID)
    
    #print("position", hex(f.tell()))
    f.seek(index_sz * 2, 1)
    
    pallete_sz = unpack("H", f.read(2))[0]
    bone_combos = unpack("H", f.read(2))[0]
    print("\tpallete_sz = ", pallete_sz, "bone_combos = ", bone_combos)
    for _ in range(bone_combos):
        unk3 = unpack("I", f.read(4))[0]
        unk4 = unpack("I", f.read(4))[0]
        FaceCount = unpack("I", f.read(4))[0]
        unk5 = unpack("I", f.read(4))[0]
        VertexCount = unpack("I", f.read(4))[0]
        print("\t\t", unk3, unk4, unk5, FaceCount, VertexCount)
        f.seek(pallete_sz * 4, 1)
    
    face_influences = unpack("I", f.read(4))[0]
    print("\tface_influences = ", face_influences)
    
    #print("position", hex(f.tell()))
    
    for _ in range(BoneCount):
        f.seek(64, 1) # matrix prob
        f.seek(4, 1)
        
    f.seek(72, 1)
    
    #print("position", hex(f.tell()))
    return

def read_node2(_, f):
    unk = unpack("H", f.read(2))[0]
    unk2 = unpack("H", f.read(2))[0]
    unk3 = unpack("H", f.read(2))[0]
    unk4 = unpack("H", f.read(2))[0]
    unk5 = unpack("H", f.read(2))[0]
    unk6 = unpack("H", f.read(2))[0]
    print("\t", _, unk, unk2, unk3, unk4, unk5, unk6)
    #for _ in range(4):
    #    a,b,c,d = unpack("ffff", f.read(16))
    #    print("\t\t", a, b, c, d)

    #for _ in range(4):
    #    a,b,c,d = unpack("ffff", f.read(16))
    #    print("\t\t", a, b, c, d)
    
    f.seek(128, 1)
    
    return

def read_node(f):
    amt_nodes = unpack("H", f.read(2))[0]
    print("amt_nodes = ", amt_nodes)
    for _ in range(amt_nodes):
        read_node2(_, f)

    

    unk = unpack("I", f.read(4))[0]
    print("unk = ", unk)
    
    num_Tinfos = unpack("H", f.read(2))[0]
    print("numTinfos = ", num_Tinfos)
    for _ in range(num_Tinfos):
        a = unpack("H", f.read(2))[0]
        b = unpack("H", f.read(2))[0]
        c = unpack("H", f.read(2))[0]
        print("\t",_, a, b, c)

    #print("pos", hex(f.tell()))

    n_normal_trishapes = unpack("I", f.read(4))[0]
    print("n_normal_trishapes = ", n_normal_trishapes)
    for _ in range(n_normal_trishapes):
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        read_primitive(f)
        unk = unpack("I", f.read(4))[0]
        bMorph = unpack("B", f.read(1))[0]
        print("\tunk =", unk, "have morph ", bMorph)
        if bMorph:
            read_morph(f)  

    #print("pos", hex(f.tell()))

    n_alpha_trishapes = unpack("I", f.read(4))[0]
    print("n_alpha_trishapes = ", n_alpha_trishapes)
    for _ in range(n_alpha_trishapes):
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        read_primitive(f)
        unk = unpack("I", f.read(4))[0]
        bMorph = unpack("B", f.read(1))[0]
        print("\tunk =", unk, "have morph ", bMorph)
        if bMorph:
            read_morph(f)  

    n_skinned_trishapes = unpack("I", f.read(4))[0]
    print("n_skinned_trishapes = ", n_skinned_trishapes)
    for _ in range(n_skinned_trishapes):
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        index_sz = read_primitive(f)
        unk = unpack("I", f.read(4))[0]
        bMorph = unpack("B", f.read(1))[0]
        print("\tunk =", unk, "have morph ", bMorph)
        if bMorph:
            read_morph(f)
        
        read_skinnned(f, index_sz)
    
    return

def main(argv):
    f = open(argv[0], 'rb')
    version_prob = unpack("I", f.read(4))[0]
    
    amount_prob = unpack("I", f.read(4))[0]
    print("amt = ", amount_prob)
    
    for _ in range(amount_prob):
        read_node(f)
        
    
    
    
    
            

    print("position", hex(f.tell()))
   
    f.close()

if __name__ == "__main__":
   main(sys.argv[1:])