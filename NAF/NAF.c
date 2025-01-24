
// NAF file format for CoC DCoTE

// .naf
DWORD version? // 68

//Rooms RoomList
DWORD rooms_count

// boundaries?
rooms_count {
	1b cSync // must be '*'
	12b bounds_min //vec3
	12b bounds_max //vec3
	4b amt
		16b  // ExtraPlane
		4b amt2
		4b * amt2 // array indexes
	16b // origin?
}

// connections between rooms ?
rooms_count {
	1b cSync // must be '*'
	2b amt
		2b unk
		2b cnt
			4b a
			4b b
			4b c
		
}

1b cSync
2b amt
2b unk
amt {
	2b
	4b
	2b
	2b
}

//TriShapeList
2b numTinfos
	2b idx  //TriShapeTexturingInfo
	2b idx
	2b idx
4b amount2
if amount2:
	1b sync
	1b flags?
	16b origin? //vec4
	2b room_id // probably room index
	2b texture_info_id // probably texture info
	4b NumVerts // numverts should be less than 65535
	4b some_flags?
	4b MasterVBID // vertex base id less than 65535
	4b offset_vtx // offset in vertex base?
	
	4b numFaces //
	// if numFaces & 0x40000000 != 0
	// numberOfPrimitives = numFaces - 2; flag = 1
	// else numberOfPrimitives = numFaces; flag = 0
	// if flag == 0
	//     sz = numberOfPrimitives * 3
	// else 
	//	   sz = numberOfPrimitives + 2
	2b * sz // index buffer?

// .pc.naf

// vertex buffers
4b amount 
	4b vertex_count 
	1b flag // if flag vtx_size = 24, else 20
	if !vertex_count continue
	vtx_size * vertex_count // vertex_buffer
	4b vertex_count2 
	1b flag2 // if flag vtx_size2 = 24, else 20
	if !vertex_count2 continue
	vtx_size2 * vertex_count2 // vertex_buffer2
	1b cSync // must be '*'

// Textures
4b amount
	2b index?
	4b sz
	sz bytes // texture
	cSync // must be '*'

VertexFormat:
20b vertex

8b packedposition
//from shader
real_pos = offset.xyz + from_short(packedposition).xyz * offset.w
4b color
4b UV
4b UV_lightmap


24b
