from idautils import *
from idaapi import *
import os

autoWait()

baseDir = ".\"

if not os.path.exists(baseDir + "KavalAntsBB"):
    os.makedirs(baseDir + "KavalAntsBB")

filename = idaapi.get_root_filename().lower()
base = idaapi.get_imagebase()
allBlocks = {}
BBcount = 0
Fcount = 0

file = open(baseDir + "KavalAntsBB/" + filename + ".bb", 'w')
file.write(filename)
for segment_ea in Segments():
	segment = idaapi.getseg(segment_ea)
	if segment.perm & idaapi.SEGPERM_EXEC == 0:
		continue
	
	for location in Functions(SegStart(segment.startEA), SegEnd(segment.startEA)):
		Fcount += 1
		blocks = idaapi.FlowChart(idaapi.get_func(location))
		for block in blocks:
			BBcount += 1
			if block.startEA not in allBlocks:
				if GetMnem(block.startEA) == "":
					print "Skipping %08X because this is not code" % (block.startEA)
					print "    " + GetDisasm(block.startEA)
					break
				line = "%08X|%08X|%02X" % ((block.startEA - base), (idaapi.get_fileregion_offset(block.startEA)), (idaapi.get_byte(block.startEA)))
				file.write("\n" + line)
				allBlocks[block.startEA] = True
file.close()
print "Discovered %d basic blocks in %d functions" % (BBcount, Fcount)
qexit()