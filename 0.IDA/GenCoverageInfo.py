from idautils import *
import os

if not os.path.exists("KavalAntsBB"):
    os.makedirs("KavalAntsBB")

filename = idaapi.get_root_filename().lower()
base = idaapi.get_imagebase()
BBcount = 0
Fcount = 0

file = open("KavalAntsBB/" + filename + ".bb", 'w')
file.write(filename)
for segment_ea in Segments():
	segment = idaapi.getseg(segment_ea)
	if segment.perm & idaapi.SEGPERM_EXEC == 0:
		continue
	
	for location in Functions(SegStart(segment.startEA), SegEnd(segment.startEA)):
		Fcount += 1
		blocks = idaapi.FlowChart(idaapi.get_func(location))
		for block in blocks:
			#print "BB at " + hex(block.startEA)
			#print " MEMORY OFFSET:" + hex(block.startEA - base)
			#print " FILE OFFSET: " + hex(idaapi.get_fileregion_offset(block.startEA))
			#print " ORIGINAL VALUE: " + hex(idaapi.get_byte(block.startEA))
			BBcount += 1
			line = "%08X|%08X|%02X" % ((block.startEA - base), (idaapi.get_fileregion_offset(block.startEA)), (idaapi.get_byte(block.startEA)))
			file.write("\n" + line)
file.close()
print "Discovered %d basic blocks in %d functions" % (BBcount, Fcount)