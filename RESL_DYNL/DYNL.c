1280203076
1146703436


//scenenode structure
2b type?
2b node_parent_id
2b node_child_id
2b id
2b	mesh_id
2b	//usually 0
64b matrix
64b matrix

//DYNL
// ".\\HfeSceneObjectDynamic.cpp"
// DYNL chunk format
4b amount?

2b amt
if amt == 0xFFFF ret
	140b scene_node //



4b unk
2b numTinfos
	2b diffuse_idx
	2b lightmap_idx
	2b detail_idx // texture indexes
4b nTriShapesNormal // normal tri shapes
	1b cSync // must be '*'
	1b flags
	16b origin? //vec4
	2b room_id? // probably room index
	2b texture_info_id? // probably texture info
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
	2b * sz // index buffer

	4b mesh_id // mesh_id from nodes
	1b bVertexMorph
	if bVertexMorph
		//HfeVertexMorpher
		1b version // 101
		1b m_numTargets // <= 16
		2b m_numVertices // must be expected num vertices
		4b
		4b
		4b
		1b a
		1b b 
		1b c
		1b flag
		if flag
			m_numTargets {
				2b cnt
				(a+b+c + 1) * 2 * cnt// array some
			}
		else
			m_numTargets * m_numVertices * (a+b+c) * 2 // array

4b nTriShapesAlpha // Number of alpha tri shapes
	same as TriShapesNormal		

4b nTriShapesSkinned // Number of skinned tri shapes
	same as TriShapesNormal
	4b unk
	4b unk2
	4b nFaces
	4b nVertices
	4b BoneCount
	4b uiVBID
	
	2b * sz // index buffer
	
	2b pallete_sz // pallete size < 64
	2b bone_combos // number of bone combos < 32
	bone_combos {
		4b
		4b
		4b FaceCount
		4b
		4b VertexCount
		4 * pallete_sz bytes // array
	}
	4b face_influences// < 4
	BoneCount {
		64b // matrix?
		if a3 // == 0
			1b len
			len bytes string // bone name?
		else
			4b id? // bone id?
	}
	68b unk... // skip
	2b unk // unused
	2b unk // unused
	

	