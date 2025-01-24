
DynamicResourceList
0
4 nVertexBuffers
8 
C nTextureResources
10
14 nAnimations
18
1C nSkeletons
20
24 nIoTables
28
2C nParticleSystems




// loader vtbl 0x6A7674

loader:
vtbl
0x00 loader_read
0x04 loader_write
0x08 loader_setfp
0x0C loader_getfp
0x10 loader_get_file_size
0x14 loader_is_at_EOF
0x18 loader_readstring // end of string is \n



loader_struct
0x00 vtbl_p

0x0C DWORD bytes_writen; // bytes readen?
0x10 bool m_bChunkOpen // 
0x1C hFile // handle to file
0x20 unk 


'RESL' 1280525650

'LSER' 1380275020

".\\HfeDynamicResourceList.cpp"
// RESL - RESoure List?
 

4b version? // version - 5
4b nTextureResources
4b nVertexBufferResources
4b nAnimations
// animations loading 
	4b amt // 01
		4b unk1 // -1
		if unk1 == -1
			4b a // 0x10000
			4b b // 0
			4b c // 0
			4b amt2 // 0x173
		else amt2 = unk1
		amt2 bytes // array animation?
		2b amt3 // 0
		if amt3 != 0
			2b size
			size bytes // string?
			
// animation frames prob
2b unk
2b cnt
4b t // float 
cnt bytes // id bones?

			
//0x57C94
4b nSkeletons
// skeletons loading
	4b amt
		4b amt2
			4b * amt2 // array bone ids?
4b nIoTables
// IoTables loading 
	4b amt
	4b b
	4b c // float 
	if amt
		4b * amt // array float

4b nParticleSystems
// ParticleSystems loading 
	1b amt// & 0x1F
	2b * (amt & 0x1F) // array 
	if amt & 0xE0 != 0:
		1b * (amt & 0x1F) // array
	4b version
	if version == 0xFFFF0002:
		4b
		4b
		n = 10 {
			32b
			n = 32 {
				4b
			} // 128b
			24b
			16b
			16b
			12b
			32b
			4b
			12b
			12b
			12b
			4b
			4b
			4b
			256b
			32b
			96b
			128b
			32b
			2b
			2b
			12b
			4b amt3 
			12b * amt3
		}
	if version == 0xFFFF0003
		4b
		4b
		n = 10 {
			32b
			n = 32 {
				4b
			}
			16b
			16b
			16b
			12b
			40b
			32b
			128b
			32b
			2b
			2b
			12b
			4b amt3
			4b
			4b
			12b * amt3
		}

// 0x598777
// XPR_HEADER
"XPR0" magick value
DWORD offset_from_current_position
DWORD unk

//set file pointer to offset_in_file - 12 + current
0x6AC800 + 0x598777 = C44F77
0x5ADDC + 0x3CB000 = 425DDC

2b m_nVirtualIDOffset
4b m_nVirtualIDs
4b * m_nVirtualIDs // array virtualIDs

pc.xdb file format

//texture resources
nTextureResources 
	2b idx
	4b magick
	2b width
	2b height
	4b size
	size bytes //image
nVertexBufferResources
	2b idx?
	4b vtx_size?
	4b size
	size bytes // vertex buffer


