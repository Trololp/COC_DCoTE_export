from struct import unpack
import sys

# this script parse DOBS chunk

def remove_repeated_zeros(in_str):  
    return in_str.rstrip(b'\x00')

def main(argv):
    f = open(argv[0], 'rb')
    version_prob = unpack("I", f.read(4))[0]
    amount_DOB_names = unpack("I", f.read(4))[0]
    print("amount_DOB_names = ", amount_DOB_names)
    for i in range(0, amount_DOB_names):
        DOB_name = unpack("256s", f.read(256))[0]
        DOB_id = unpack("I", f.read(4))[0]
        print(DOB_id, remove_repeated_zeros(DOB_name))
    
    unk = unpack("I", f.read(4))[0]
    print("unk = ", unk)
    
    DOB_amt = unpack("H", f.read(2))[0]
    print("DOB_amt = ", DOB_amt)
    
    for _ in range(DOB_amt):
        DOB_type = unpack("I", f.read(4))[0]
        idx = unpack("I", f.read(4))[0]
        sz = unpack("I", f.read(4))[0]
        print("\t", DOB_type, idx, "size = ", sz, "pos =", hex(f.tell()))
        f.seek(sz, 1)
    
    print("pos", hex(f.tell()))
    
    f.close()

if __name__ == "__main__":
   main(sys.argv[1:])