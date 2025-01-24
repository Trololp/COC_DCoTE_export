from struct import unpack,pack
import sys
import json
import os


# this script will convert dynamic scenery objects to gltf file.
# Need to unpack .xdb file first, get RESL, DYNL, and pc.xdb files
# and put them to script folder. then edit this file.

# usage: DYNL2GLTF.py example
# will make example.gltf in export folder

# notice .gltf will require textures\ folder and e_textures\ folder
# next to it, for proper textures loading

# edit these
PC_XDB_file_name = "MISC03_ASYLUM_CUTSCENE_FEDS.pc.xbd"
DYNL_file_name = "DYNL"
RESL_file_name = "RESL_20"

g_file_lenght = 0
file_name = ""
f2 = None
f3 = None
pc_xdb_file = None
id_to_vtx_map = {}
id_to_texture_map = {}
g_out_texture_max_range = 0
g_extra_texture_count = 0

def make_blank_gltf_json():
    json_d = {}
    json_d["asset"] = {"generator":"Bruh v0.1", "version":"2.0"}
    json_d["scene"] = 0
    json_d["scenes"] = []
    json_d["nodes"] = []
    # miss materials for now
    json_d["meshes"] = []
    json_d["accessors"] = []
    json_d["bufferViews"] = []
    json_d["buffers"] = []
    json_d["textures"] = []
    json_d["images"] = []
    json_d["materials"] = []
    return json_d





def get_index_buffer_size(numFaces):
    flag = 0
    if numFaces & 0x40000000:
        #print("detected odd index buffer")
        numFaces = numFaces & 0xBFFFFFFF
        flag = 1
    
    if flag:
        return numFaces
    else:
        return numFaces * 3

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

def get_virtual_id_table(f):
    f.seek(0)
    version_prob = unpack("I", f.read(4))[0]
    nTextureResources = unpack("I", f.read(4))[0]
    nVertexBufferResources = unpack("I", f.read(4))[0]
    nAnimations = unpack("I", f.read(4))[0]
    #print(f"nTextureResources = {nTextureResources}, nVertexBufferResources={nVertexBufferResources}, nAnimations={nAnimations}")
    
    for _ in range(0, nAnimations):
        read_animation_resource(f)
    
    nSkeletons = unpack("I", f.read(4))[0]
    #print("nSkeletons =", nSkeletons)
    
    for _ in range(0, nSkeletons):
        read_skeletons(f)
    
    nIoTables = unpack("I", f.read(4))[0]
    #print("nIoTables =", nIoTables)
    
    for _ in range(0, nIoTables):
        read_iotables(f)
    
    nParticleSystems = unpack("I", f.read(4))[0]
    #print("nParticleSystems =", nParticleSystems)
    
    for _ in range(0, nParticleSystems):
        read_particle_sys(f)
    

    xpr0_magick = f.read(4)
    if xpr0_magick != b"XPR0":
        print("missing XPR0 header!")
        return
    
    f_offset = unpack("I", f.read(4))[0]
    #print("offset", hex(f_offset))
    f.seek(f_offset - 8, 1)
    
    v_base_offset = unpack("H", f.read(2))[0]
    v_ids_amt = unpack("I", f.read(4))[0]
    #print("virtual IDs:")
    virtual_ids = {}
    for i in range(v_ids_amt):
        virtual_ids[i + v_base_offset] = unpack("i", f.read(4))[0]
    
    return virtual_ids, nTextureResources, nVertexBufferResources

def make_mapping_to_pc_xdb(f, virtual_ids, n_textures, n_vertex):
    f.seek(0)
    
    texture_offsets = []
    
    for _ in range(0, n_textures):
        idx = unpack("H", f.read(2))[0]
        magick = f.read(4)
        width = unpack("H", f.read(2))[0]
        height = unpack("H", f.read(2))[0]
        sz = unpack("I", f.read(4))[0]
        
        texture_offset = f.tell()
        texture_offsets.append([idx, texture_offset])
        f.seek(sz, 1)
    
    vertex_buffer_offsets_n_sz = []
    for _ in range(0, n_vertex):
        unk =  unpack("H", f.read(2))[0]
        unk2 = unpack("I", f.read(4))[0]
        sz = unpack("I", f.read(4))[0]
        
        vertex_buffer_offset = f.tell()
        vertex_buffer_offsets_n_sz.append([vertex_buffer_offset, unk2])
        f.seek(sz, 1)
        
    
    id_to_vtx_map = {}
    id_to_texture_map = {}
    for id, buff_id in virtual_ids.items():
        if buff_id < n_vertex:
            id_to_vtx_map[id] = vertex_buffer_offsets_n_sz[buff_id]
    
    for id, buff_id in virtual_ids.items():
        if buff_id < n_textures:
            id_to_texture_map[id] = texture_offsets[buff_id]
    
    return id_to_vtx_map, id_to_texture_map
    
def transform_vertex_pos(vertex, k, offset):
    x = (vertex[0]) / 32768.0 * k + offset[0]
    y = (vertex[1]) / 32768.0 * k + offset[1]
    z = (vertex[2]) / 32768.0 * k + offset[2]
    
    return [x, y, z]

def transform_UVs(UVs):
    u = (UVs[0]) / 32767.0 * 100.0
    v = (UVs[1]) / 32767.0 * 100.0
    return [u, v]

def vtx_write_to_file(f, f2, count, k, offset):
    for _ in range(count):
        xyz = unpack("hhh", f.read(6))
        f.seek(6, 1)
        UVs = unpack("hh", f.read(4))
        f.seek(4, 1)
        #f.seek(14, 1) # 0
        t_xyz = transform_vertex_pos(xyz, k, offset)
        t_UV = transform_UVs(UVs)
        f2.write(pack("fffff", t_xyz[0], t_xyz[1], t_xyz[2], t_UV[0], t_UV[1]))
        
def matrix_to_offset(mat):
    offset = [mat[0][3], mat[1][3], mat[2][3]]
    return

def write_vtx_to_file(n, f, f2, vtx_offset):
    vtx_count = n["vtx_count"]
    offset = n["offset_vtx"]
    buff_id = n["vtx_buff_id"]
    #print("vtx_buff_id", buff_id, "offset_vtx", offset)
    f.seek(vtx_offset)
    vtx_offset_f2 = f2.tell()
    vtx_write_to_file(f, f2, vtx_count, n["k"], n["offset"])
    return vtx_offset_f2

def write_idx_to_file(f,f2, count):
    f2.write(f.read(count))

def read_primitive(f, t_info_arr):
    global pc_xdb_file
    global f2
    global id_to_vtx_map
    global id_to_texture_map
    flags = unpack("B", f.read(1))[0]
    origin = unpack("ffff", f.read(16))
    room_id = unpack("H", f.read(2))[0]
    texture_info_id = unpack("H", f.read(2))[0]
    
    texure_id = 0
    
    outer_texture = False
    
    if t_info_arr[texture_info_id] >= 0x8000:
        outer_texture = True
        texture_id = t_info_arr[texture_info_id] - 0x8000
    else:
        texture_id = id_to_texture_map[t_info_arr[texture_info_id]][0]
        
    numVerts = unpack("I", f.read(4))[0]
    some_flags = unpack("I", f.read(4))[0]
    MasterVBID = unpack("I", f.read(4))[0]
    offset_vtx = unpack("I", f.read(4))[0]
    numFaces = unpack("I", f.read(4))[0]
    sz = get_index_buffer_size(numFaces)
    
    vtx_offset = 0
    if MasterVBID in id_to_vtx_map:
        if id_to_vtx_map[MasterVBID][1] == 20:
            vtx_offset = id_to_vtx_map[MasterVBID][0] + 20 * offset_vtx
        else:
            f.seek(sz * 2, 1)
            return {"skip": 1, "idx_count": sz }
    else:
        print("Error no vbid in id_to_vtx_map!")
    
    idx_offset_f2 = f2.tell()
    write_idx_to_file(f, f2, sz * 2)

    #print(room_id)

    #f.seek(sz * 2, 1)
    mesh_t = {"skip": 0, "vtx_buff_id": MasterVBID, "vtx_count": numVerts, "idx_count": sz, "offset_vtx": offset_vtx, \
               "offset": origin, "k": origin[3], "room_id": room_id, "vtx_offset_f2":0, "idx_offset_f2":idx_offset_f2,
               "offset_vtx_pc_xdb": vtx_offset, "texture_outer": outer_texture, "texture_id": texture_id}
    mesh_t["vtx_offset_f2"] = write_vtx_to_file(mesh_t, pc_xdb_file, f2, vtx_offset)  
    return mesh_t

def read_morph(f):
    version = unpack("B", f.read(1))[0]
    if(version != 101):
        print("\t\tmorph version != 101")
    m_numTargets = unpack("B", f.read(1))[0]
    m_numVertices = unpack("H", f.read(2))[0]
    #print("m_numTargets =", m_numTargets, "m_numVertices =", m_numVertices)
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
    #print("\tunk=", unk, "unk2 =", unk2, "nFaces = ", nFaces, "nVertices =", nVertices, "BoneCount = ", BoneCount, "VBID = ", uiVBID)
    
    #print("position", hex(f.tell()))
    f.seek(index_sz * 2, 1)
    
    pallete_sz = unpack("H", f.read(2))[0]
    bone_combos = unpack("H", f.read(2))[0]
    #print("\tpallete_sz = ", pallete_sz, "bone_combos = ", bone_combos)
    for _ in range(bone_combos):
        unk3 = unpack("I", f.read(4))[0]
        unk4 = unpack("I", f.read(4))[0]
        FaceCount = unpack("I", f.read(4))[0]
        unk5 = unpack("I", f.read(4))[0]
        VertexCount = unpack("I", f.read(4))[0]
        #print("\t\t", unk3, unk4, unk5, FaceCount, VertexCount)
        f.seek(pallete_sz * 4, 1)
    
    face_influences = unpack("I", f.read(4))[0]
    #print("\tface_influences = ", face_influences)
    
    #print("position", hex(f.tell()))
    
    for _ in range(BoneCount):
        f.seek(64, 1) # matrix prob
        f.seek(4, 1)
        
    f.seek(72, 1)
    
    #print("position", hex(f.tell()))
    return

def read_node2(f):
    f.seek(8, 1)
    mesh_id = unpack("H", f.read(2))[0]
    f.seek(2, 1)
    
    f.seek(64, 1) # matrix
    
    w, h = 4, 4
    Matrix = [[0 for x in range(w)] for y in range(h)] 
    
    for y in range(4):
        for x in range(4):
            Matrix[x][y] = unpack("f", f.read(4))[0]
    
    return mesh_id, Matrix
    #f.seek(128, 1)

def read_node(f):
    global pc_xdb_file
    global f2
    global g_out_texture_max_range
    amt_nodes = unpack("H", f.read(2))[0]
    print("amt_nodes = ", amt_nodes)
    node_mesh_dict = {}
    
    for _ in range(amt_nodes):
        mesh_id, Matrix = read_node2(f)
        node_mesh_dict[mesh_id] = Matrix
    
    #f.seek(140 * amt_nodes, 1)

    unk = unpack("I", f.read(4))[0]
    #print("unk = ", unk)
    
    num_Tinfos = unpack("H", f.read(2))[0]
    t_info_arr = []
    #print("numTinfos = ", num_Tinfos)
    for _ in range(num_Tinfos):
        a = unpack("H", f.read(2))[0]
        b = unpack("H", f.read(2))[0]
        c = unpack("H", f.read(2))[0]
        if a >= 0x8000:
            if g_out_texture_max_range < a - 0x8000:
                g_out_texture_max_range = a - 0x8000
        t_info_arr.append(a)
        #print("\t",_, a, b, c)

    mesh_list = []

    #print("pos", hex(f.tell()))

    n_normal_trishapes = unpack("I", f.read(4))[0]
    print("n_normal_trishapes = ", n_normal_trishapes)
    for _ in range(n_normal_trishapes):
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        mesh_t = read_primitive(f, t_info_arr)
        mesh_id = unpack("I", f.read(4))[0]
        mesh_t["matrix"] = node_mesh_dict[mesh_id]
        if not mesh_t["skip"]:
            mesh_list.append(mesh_t)
        bMorph = unpack("B", f.read(1))[0]
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
        mesh_t = read_primitive(f, t_info_arr)
        mesh_id = unpack("I", f.read(4))[0]
        mesh_t["matrix"] = node_mesh_dict[mesh_id]
        if not mesh_t["skip"]:
            mesh_list.append(mesh_t)
        bMorph = unpack("B", f.read(1))[0]
        if bMorph:
            read_morph(f)  

    n_skinned_trishapes = unpack("I", f.read(4))[0]
    print("n_skinned_trishapes = ", n_skinned_trishapes)
    for _ in range(n_skinned_trishapes):
        cSync = unpack("B", f.read(1))[0]
        if(cSync != ord('*')): # '*'
            print("Read sync failure")
            break
        mesh_t = read_primitive(f, t_info_arr)
        mesh_id = unpack("I", f.read(4))[0]
        mesh_t["matrix"] = node_mesh_dict[mesh_id]
        if not mesh_t["skip"]:
            mesh_list.append(mesh_t)
        index_sz = mesh_t["idx_count"]
        bMorph = unpack("B", f.read(1))[0]
        if bMorph:
            read_morph(f)
        
        read_skinnned(f, index_sz)
    
    
    
    return mesh_list

def create_mesh_list(f):
    f.seek(0)
    version_prob = unpack("I", f.read(4))[0]

    amount_prob = unpack("I", f.read(4))[0]
    #print("amt = ", amount_prob)
    
    mesh_list = []
    for _ in range(amount_prob):
        mesh_list.extend(read_node(f))

    return mesh_list

def matrix_to_list(mat):
    list_f = []
    for y in range(4):
        for x in range(4):
            list_f.append(mat[x][y])
    return list_f
    
def make_gltf_json(json_d, meshes):
    global f2
    global file_name
    global g_file_lenght
    global g_extra_texture_count
    global g_out_texture_max_range
    
    f2_size = g_file_lenght
    json_d["buffers"] = [{"byteLength": f2_size, "uri": file_name + ".bin"}]
    r_meshes = meshes
    
    for m in r_meshes:
        json_d["bufferViews"].append({"buffer":0, "byteLength": m["vtx_count"] * 20, \
        "byteStride": 20, "byteOffset": m["vtx_offset_f2"], "target":34962})
        json_d["bufferViews"].append({"buffer":0, "byteLength": m["idx_count"] * 2, \
        "byteOffset": m["idx_offset_f2"], "target":34963})
        
    buf_view_n = 0
    for m in r_meshes:
        acc_t = {"bufferView": buf_view_n,
            "componentType": 5126,
            "count": m["vtx_count"],
            "min": [-9999.0, -9999.0, -9999.0],
            "max": [ 9999.0,  9999.0,  9999.0],
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
                  "material": m["texture_id"] if m["texture_outer"] else m["texture_id"] + g_out_texture_max_range,
                  "mode" : 5} ]}
        buf_view_n += 3
        mesh_id += 1
        json_d["meshes"].append(mesh_t)
    
    children_list = []
    for i in range(len(r_meshes)):
        children_list.append(i + 1)
    
    json_d["nodes"].append({"name" : "room", "children": children_list})


    mesh_id = 0
    for m in r_meshes:
        node_t = {"name": f"mesh_{mesh_id}" , "matrix": matrix_to_list(m["matrix"])}
        node_t["mesh"] = mesh_id
        mesh_id += 1
        json_d["nodes"].append(node_t)

    json_d["scenes"] = [{"name":"Scene",
	                    "nodes":[0]}]
    json_d["scene"] = 0
    
    for i in range(g_out_texture_max_range):
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
    
    for i in range(g_out_texture_max_range, g_out_texture_max_range + g_extra_texture_count):
        json_d["images"].append({"uri": f"e_textures\{i - g_out_texture_max_range}.dds"})
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
    global id_to_vtx_map 
    global id_to_texture_map
    global pc_xdb_file
    global g_file_lenght
    global file_name
    global g_extra_texture_count
    f = open(RESL_file_name, 'rb')
    f3 = open(PC_XDB_file_name, 'rb')
    pc_xdb_file = f3
    exp_dir = "export//"
    os.makedirs(exp_dir, exist_ok=True)
    
    virtual_ids, nTextureResources, nVertexBufferResources = get_virtual_id_table(f)
    g_extra_texture_count = nTextureResources
    id_to_vtx_map, id_to_texture_map = make_mapping_to_pc_xdb(f3, virtual_ids, nTextureResources, nVertexBufferResources)
    
    #print(id_to_vtx_map)
    file_name = argv[0]
    f2 = open(exp_dir + argv[0] + ".bin", 'wb')
    #    f2 = open("NAF.bin", 'wb')
    
    
    
    f = open(DYNL_file_name, 'rb')
    mesh_list = create_mesh_list(f)
    #print(mesh_list)
    g_file_lenght = f2.tell()
    f2.close()
    
    
    json_d = make_blank_gltf_json()
    make_gltf_json(json_d, mesh_list)
        
    f2 = open(exp_dir + argv[0] + ".gltf", "w")
    json.dump(json_d, f2)
    f2.close()
    
    f.close()
    f3.close()

if __name__ == "__main__":
   main(sys.argv[1:])