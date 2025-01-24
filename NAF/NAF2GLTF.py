from struct import unpack,pack
import sys
import json
import os

# This script will export NifExport.naf file to GLTF file format.
# For export you need 3 files, banks.inf, NifExport.naf, NifExport.pc.naf
# all files should be in script folder
# open terminal and type NAF2GLTF.py NifExport.naf
# in directory `export` will be gltf files, each represent single room.
# room indexes and names can be found in rooms.txt
# notice: banks.inf hardcoded in code. 
# for dynamic objects use other script, DYNL2GLTF.py
# For exporting textures use NAF_dump_textures.py, then place textures
# folder to folder containing gltf files for proper loading of textures.


g_file_lenght = 0
g_rooms_count = 0
g_texture_count = 0
room_bounds = []
g_uv_scales = []
file_name = ""
f2 = None
f3 = None


def make_blank_gltf_json():
    json_d = {}
    json_d["asset"] = {"generator":"Bruh v0.1", "version":"2.0"}
    json_d["scene"] = 0
    json_d["scenes"] = []
    json_d["nodes"] = []

    json_d["meshes"] = []
    json_d["accessors"] = []
    json_d["bufferViews"] = []
    json_d["buffers"] = []
    json_d["textures"] = []
    json_d["images"] = []
    json_d["materials"] = []
    return json_d


def f_skip_vtx_buff(f):
    vtx_count = unpack("I", f.read(4))[0]
    flag = unpack("B", f.read(1))[0]
    vtx_size = 20
    if flag:
        vtx_size = 24
    f.seek(vtx_size * vtx_count, 1)

def f_goto_vtx(f, vtx_buff_id, offset):
    f.seek(4, 0)
    for _ in range(vtx_buff_id // 2):
        f_skip_vtx_buff(f)
        f_skip_vtx_buff(f)
        cSync = unpack("B", f.read(1))[0]
        if cSync != ord('*'):
            print("Error, file out of sync")
            print(hex(f.tell()))
            return 0
    
    if(vtx_buff_id % 2 == 1):
        f_skip_vtx_buff(f)
    
    vtx_count = unpack("I", f.read(4))[0]
    
    if(offset > vtx_count):
        print("error, offset > vtx_count")
        return 0
    
    flag = unpack("B", f.read(1))[0]
    vtx_size = 20
    if flag:
        vtx_size = 24
    f.seek(vtx_size * offset, 1)
    return flag
  
  
    

def transform_vertex_pos(vertex, k, offset):
    x = (vertex[0]) / 32767.0 * k + offset[0]
    y = (vertex[1]) / 32767.0 * k + offset[1]
    z = (vertex[2]) / 32767.0 * k + offset[2]
    
    return [x, y, z]

def get_uv_scales(f):
    global g_uv_scales
    scales = []
    f_lines = f.readlines()
    count = (len(f_lines) - 1) // 7
    
    f_lines = f_lines[1:]
    
    for i in range(count):
        uv_scale_factors = []
        uv_scale_factors.append(float(f_lines[1 + i * 7]))
        uv_scale_factors.append(float(f_lines[2 + i * 7]))
        scales.append(uv_scale_factors)
    
    g_uv_scales = scales
    return scales
    

def transform_UVs(UVs, scale_factors):
    u = (UVs[0]) / 32767.0 * scale_factors[0]
    v = (UVs[1]) / 32767.0 * scale_factors[1]
    return [u, v]
  
def vtx_write_to_file(f, f2, flag, count, k, offset, scale_factors):
    for _ in range(count):
        xyz = unpack("hhh", f.read(6))
        #f.seek(14, 1) # 0
        f.seek(6, 1) # 0, color
        #rgba = unpack("BBBB", f.read(4))
        UV_1 = unpack("hh", f.read(4))
        f.seek(4, 1)
        #UV_2 = unpack("HH", f.read(4))
        if flag:
            f.seek(4, 1)
        #    UV_3 = unpack("HH", f.read(4))
        t_xyz = transform_vertex_pos(xyz, k, offset)
        t_uv = transform_UVs(UV_1, scale_factors)
        f2.write(pack("fffff", t_xyz[0], t_xyz[1], t_xyz[2], t_uv[0], t_uv[1]))
        

def write_vtx_to_file(n, f, f2):
    vtx_count = n["vtx_count"]
    offset = n["offset_vtx"]
    buff_id = n["vtx_buff_id"]
    #print("vtx_buff_id", buff_id, "offset_vtx", offset)
    flag = f_goto_vtx(f, buff_id, offset)
    vtx_offset_f2 = f2.tell()
    vtx_write_to_file(f, f2, flag, vtx_count, n["room_k"], n["room_offset"], n["uv_scale"])
    return vtx_offset_f2

def read_room_1(f):
    b_min = unpack("fff", f.read(12))
    b_max = unpack("fff", f.read(12))
    extra_planes = unpack("I", f.read(4))[0]
    for _ in range(extra_planes):
        f.seek(16,1)
        amt2 = unpack("I", f.read(4))[0]
        f.seek(amt2 * 4, 1)
    #f.seek(16,1)
    origin = unpack("ffff", f.read(16))
    return [b_min, b_max, origin]

def read_room_2(f):
    amt = unpack("H", f.read(2))[0]
    for _ in range(amt):
        unk = unpack("H", f.read(2))[0]
        cnt = unpack("H", f.read(2))[0]
        f.seek(12 * cnt, 1)

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

def write_idx_to_file(f,f2, count):
    f2.write(f.read(count))

def read_primitive(f):
    global f2
    global f3
    global room_bounds
    global g_uv_scales
    f3.seek(4)
    flags = unpack("B", f.read(1))[0]
    origin = unpack("ffff", f.read(16))
    room_id = unpack("H", f.read(2))[0]
    texture_info_id = unpack("H", f.read(2))[0]
    numVerts = unpack("I", f.read(4))[0]
    some_flags = unpack("I", f.read(4))[0]
    MasterVBID = unpack("I", f.read(4))[0]
    offset_vtx = unpack("I", f.read(4))[0]
    numFaces = unpack("I", f.read(4))[0]
    sz = get_index_buffer_size(numFaces)
    idx_offset_f2 = f2.tell()
    write_idx_to_file(f, f2, sz * 2)

    #print(room_id)
    uv_scale = g_uv_scales[MasterVBID]
    #f.seek(sz * 2, 1)
    mesh_t = {"vtx_buff_id": MasterVBID, "vtx_count": numVerts, "idx_count": sz, "offset_vtx": offset_vtx, \
              "offset": origin, "k": origin[3], "room_id": room_id, "vtx_offset_f2":0, "idx_offset_f2":idx_offset_f2,\
              "room_k": room_bounds[room_id][2][3], "room_offset": room_bounds[room_id][2], "tinfo": texture_info_id, \
              "uv_scale": uv_scale}
                
                
    mesh_t["vtx_offset_f2"] = write_vtx_to_file(mesh_t, f3, f2)  
    return mesh_t


def create_mesh_list(f):
    global g_rooms_count
    global room_bounds
    f.seek(0)
    version_prob = unpack("I", f.read(4))[0]
    g_rooms_count = unpack("I", f.read(4))[0]
    mesh_list = []
    
    
    for _ in range(g_rooms_count):
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        room_bounds.append(read_room_1(f))

    for _ in range(g_rooms_count):
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
    #print("numTinfos = ", num_Tinfos)
    tinfo_arr = []
    for _ in range(num_Tinfos):
        a = unpack("H", f.read(2))[0] # diffuse
        b = unpack("H", f.read(2))[0] # lightmap
        c = unpack("H", f.read(2))[0] # details
        tinfo_arr.append(a)
        #print("\t",_, a, b, c)
    
    
    
    num_index_buffers = unpack("I", f.read(4))[0]
    #print("num_index_buffers = ", num_index_buffers)
    for _ in range(num_index_buffers):
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        mesh_t = read_primitive(f)
        if tinfo_arr[mesh_t["tinfo"]] != 0xFFFF:
            mesh_t["texture_id"] = tinfo_arr[mesh_t["tinfo"]]
        else:
            mesh_t["texture_id"] = 0
        mesh_list.append(mesh_t)
        

    return mesh_list

def get_rooms_count(f):
    f.seek(0)
    version_prob = unpack("I", f.read(4))[0]
    rooms_count = unpack("I", f.read(4))[0]
    return room_count

def get_texture_count(f):
    f.seek(0)
    vtx_buff_count = unpack("I", f.read(4))[0]
    for _ in range(vtx_buff_count):
        f_skip_vtx_buff(f)
        f_skip_vtx_buff(f)
        cSync = unpack("B", f.read(1))[0]
        if cSync != ord('*'):
            print("Error, file out of sync")
            print(hex(f.tell()))
            return 0
    
    texture_count = unpack("I", f.read(4))[0]
    return texture_count
    
def make_gltf_json(json_d, meshes, room_id):
    global f2
    global room_bounds
    global file_name
    global g_file_lenght
    global g_texture_count
    
    f2_size = g_file_lenght
    json_d["buffers"] = [{"byteLength": f2_size, "uri": file_name + ".bin"}]
    r_meshes = []
    
    for m in meshes:
        if m["room_id"] == room_id:
            r_meshes.append(m)
    
    for m in r_meshes:
        json_d["bufferViews"].append({"buffer":0, "byteLength": m["vtx_count"] * 20, \
        "byteStride": 20, "byteOffset": m["vtx_offset_f2"], "target": 34962}) #
        json_d["bufferViews"].append({"buffer":0, "byteLength": m["idx_count"] * 2, \
        "byteOffset": m["idx_offset_f2"], "target": 34963})
        
    buf_view_n = 0
    for m in r_meshes:
        acc_t = {"bufferView": buf_view_n,
            "componentType": 5126,
            "byteOffset": 0,
            "count": m["vtx_count"],
            "min": [room_bounds[room_id][0][0], room_bounds[room_id][0][1], room_bounds[room_id][0][2]],
            "max": [room_bounds[room_id][1][0], room_bounds[room_id][1][1], room_bounds[room_id][1][2]],
            "type":"VEC3"}
        
        json_d["accessors"].append(acc_t)
        acc_uv = {"bufferView" : buf_view_n,
            "byteOffset": 12,
            "componentType" : 5126,
            "count" : m["vtx_count"],
            "type" : "VEC2"}
        json_d["accessors"].append(acc_uv)
        buf_view_n += 1
        acc_t2 = {"bufferView": buf_view_n,
            "componentType": 5123,
            "count": m["idx_count"],
            "type":"SCALAR"}
        buf_view_n += 1
        json_d["accessors"].append(acc_t2)

    mesh_id = 0
    buf_view_n = 0
    for m in r_meshes:
        mesh_t = {"name": f"mesh_{mesh_id}",
                  "primitives": [ {
                  "attributes" : {"POSITION":buf_view_n, "TEXCOORD_0": buf_view_n + 1},
                  "indices": buf_view_n + 2,
                  "material": m["texture_id"] } ]}
        buf_view_n += 3
        mesh_id += 1
        json_d["meshes"].append(mesh_t)
    
    children_list = []
    for i in range(len(r_meshes)):
        children_list.append(i + 1)
    
    json_d["nodes"].append({"name" : "room", "children": children_list})


    mesh_id = 0
    for m in r_meshes:
        node_t = {"name": f"mesh_{mesh_id}"} #, "translation": m["offset"]
        node_t["mesh"] = mesh_id
        mesh_id += 1
        json_d["nodes"].append(node_t)

    json_d["scenes"] = [{"name":"Scene",
	                    "nodes":[0]}]
    json_d["scene"] = 0
    
    for i in range(g_texture_count):
        json_d["images"].append({"uri": f"textures\{i}.dds"})
        json_d["textures"].append({"source": i})
        mat_t =         {
            "doubleSided":False,
            "name":"Material",
            "pbrMetallicRoughness":{
                "baseColorTexture":{
                    "index": i
                },
                "metallicFactor":0.0,
                "roughnessFactor":0.5
            }
        }
        json_d["materials"].append(mat_t)
        
    
    
    
    return
    
    
    
def main(argv):
    global f2
    global f3
    global file_name
    global g_file_lenght
    global g_rooms_count
    global g_texture_count
    
    f4 = open("banks.inf", 'r')
    get_uv_scales(f4)
    f4.close()
    
    f = open(argv[0], 'rb')
    dot_index = argv[0].rfind('.')
    file_name = argv[0][:dot_index]
    f3 = open(argv[0][:dot_index] + ".pc.naf", 'rb')
    
    exp_dir = "export//" + file_name + "//"
    os.makedirs(exp_dir, exist_ok=True)
    
    f2 = open(exp_dir + file_name + ".bin", 'wb')
    #    f2 = open("NAF.bin", 'wb')
    
    g_texture_count = get_texture_count(f3)
    
    
    
    mesh_list = create_mesh_list(f)
    g_file_lenght = f2.tell()
    f2.close()
    
    print(g_rooms_count)
    
    for rm in range(g_rooms_count):
        json_d = make_blank_gltf_json()
        make_gltf_json(json_d, mesh_list, rm)
        
        f2 = open(exp_dir + str(rm) + ".gltf", "w")
        json.dump(json_d, f2)
        f2.close()
        
    
    f.close()
    f3.close()

if __name__ == "__main__":
   main(sys.argv[1:])