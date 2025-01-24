from struct import unpack
import sys

#parser for RESL chunk file

def remove_repeated_zeros(in_str):  
    return in_str.rstrip(b'\x00')

def read_animation_resource(f):
    amt = unpack("I", f.read(4))[0]
    for i in range(0, amt):
        unk = unpack("i", f.read(4))[0]
        amt2 = unk
        if unk == -1:
            a = unpack("I", f.read(4))[0]
            b = unpack("I", f.read(4))[0]
            c = unpack("I", f.read(4))[0]
            amt2 = unpack("I", f.read(4))[0]
            #print(f"\t a = {a}, b = {b}, c = {c}, amt2 = {amt2}")
        f.seek(amt2, 1) # array idk
        chk = unpack("h", f.read(2))[0]
        if chk != 0:
            sz = unpack("h", f.read(2))[0]
            f.seek(sz, 1)
        #print(f"\t i = {i}, unk = {unk}, chk = {chk}")

def read_skeletons(f):
    amt = unpack("I", f.read(4))[0]
    for _ in range(0, amt):
        amt2 = unpack("I", f.read(4))[0]
        f.seek(4 * amt2, 1)

def read_iotables(f):
    amt = unpack("I", f.read(4))[0]
    b = unpack("f", f.read(4))[0]
    c = unpack("f", f.read(4))[0]
    #print(f"amt = {amt}, b = {b}, c = {c}")
    f.seek(4*amt, 1)

def read_particle_sys(f):
    amt = unpack("b", f.read(1))[0]
    f.seek(2 * (amt & 0x1F), 1)
    if amt & 0xE0:
        f.seek(1 * (amt & 0x1F), 1)
    
    version = unpack("I", f.read(4))[0]
    if version == 0xFFFF0002:
        #print("emitter ver 2")
        f.seek(8, 1)
        for _ in range(0, 10):
            f.seek(872, 1)
            amt3 = unpack("I", f.read(4))[0]
            f.seek(12* amt3, 1)
    if version == 0xFFFF0003:
        #print("emitter ver 3")
        f.seek(8, 1)
        for _ in range(0, 10):
            f.seek(468, 1)
            amt3 = unpack("I", f.read(4))[0]
            f.seek(8, 1)
            f.seek(12* amt3, 1)

def main(argv):
    f = open(argv[0], 'rb')
    version_prob = unpack("I", f.read(4))[0]
    nTextureResources = unpack("I", f.read(4))[0]
    nVertexBufferResources = unpack("I", f.read(4))[0]
    nAnimations = unpack("I", f.read(4))[0]
    print(f"nTextureResources = {nTextureResources}, nVertexBufferResources={nVertexBufferResources}, nAnimations={nAnimations}")
    
    for _ in range(0, nAnimations):
        read_animation_resource(f)
    
    nSkeletons = unpack("I", f.read(4))[0]
    print("nSkeletons =", nSkeletons)
    
    for _ in range(0, nSkeletons):
        read_skeletons(f)
    
    nIoTables = unpack("I", f.read(4))[0]
    print("nIoTables =", nIoTables)
    
    for _ in range(0, nIoTables):
        read_iotables(f)
    
    nParticleSystems = unpack("I", f.read(4))[0]
    print("nParticleSystems =", nParticleSystems)
    
    for _ in range(0, nParticleSystems):
        read_particle_sys(f)
    

    xpr0_magick = f.read(4)
    if xpr0_magick != b"XPR0":
        print("missing XPR0 header!")
        return
    
    f_offset = unpack("I", f.read(4))[0]
    print("offset", hex(f_offset))
    f.seek(f_offset - 8, 1)
    
    v_base_offset = unpack("H", f.read(2))[0]
    v_ids_amt = unpack("I", f.read(4))[0]
    print("virtual IDs:")
    for i in range(v_ids_amt):
        print("\t", i + v_base_offset, unpack("i", f.read(4))[0])
    
    print("position", hex(f.tell()))
    
   
    f.close()

if __name__ == "__main__":
   main(sys.argv[1:])