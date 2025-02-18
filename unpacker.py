from struct import unpack
import sys

# Call of Cthulhu DCoTE, .xdb unpacker
# usage unpacker.py xdb_file
# file format
# signature 'CHNK'; from chunk?
# DWORD version;
# DWORD n_chunks; number of chunks
# chunks...

# chunk format
# signature 4b
# lenght of data 4b
# data (lenght of data)b 

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
    hdr = f.read(8)
    if (hdr[0:4] != b'KNHC'): 
        print('this is not a .xdb file')
        return
    
    n_chunks = unpack("I", f.read(4))[0]
    print(f"n_chunks = {n_chunks}")
    
    for i in range(n_chunks):
        signature = swap_4b(f.read(4))
        size_of_data = unpack("I", f.read(4))[0]
        print(signature, size_of_data)
        dump_chunk(f, size_of_data, chnk_name(f.tell(), signature))
    
    f.close()

if __name__ == "__main__":
   main(sys.argv[1:])