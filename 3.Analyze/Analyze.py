import os
import shutil
import getopt
import sys
import time


dir = ".\\input"
output = ".\\output.txt"
BBcount = 0
modules = {}
basicblocks = {}
results = []
	


#Conf
def help():
	print "Possible arguments: GenBpFiles.py [-h] [-d DIR] [-o FILE]"
	print " -h      Prints this message to you"
	print " -d DIR  Directory that contains coverage files"
	print " -o FILE Result file"
	
	
try:                                
	opts, args = getopt.getopt(sys.argv[1:], "hd:o:", [])
except:
	help()
	sys.exit()
for opt, arg in opts:
	if opt in("-h"):
		help()
		sys.exit()
	if opt in("-o"):
		output = arg
	if opt in("-d"):
		dir = arg	

#Prep
filelist = os.listdir(dir)
		
#First pass through
lastTime = time.time()
for fname in filelist:
	f = open(dir + "/" + fname)
	
	#module list
	line = f.readline()
	modules = {}
	while line != "" and line[2] != "|":
		moduleName = line[:line.find("|")].lower()
		moduleCode = line[line.find("|")+1:line.find("|")+3]
		modules[moduleCode] = moduleName
		if moduleName not in basicblocks:
			basicblocks[moduleName] = {}
		line = f.readline()
		
	#basicblock
	while line.strip() != "":
		moduleCode = line[0:2]
		bb = line[3:11]
		moduleName = modules[moduleCode].lower()
		if bb not in basicblocks[moduleName]:
			basicblocks[moduleName][bb] = False
			BBcount += 1
		line = f.readline()
	f.close()
		
print "First analysis"
print "  Files: %d" % len(filelist)
print "  BasicBlocks: %d" % BBcount
print "  Time spent: %d sec" % (time.time() - lastTime)


#Real analysis
fout = open(output, 'w')
while BBcount>0:
	best = 0;
	bestName = None
	
	lastTime = time.time()
	#Scan
	for fname in filelist:
		if fname in results:
			continue
		current = 0
		f = open(dir + "/" + fname)
	
		#module list
		line = f.readline()
		modules = {}
		while line != "" and line[2] != "|":
			moduleName = line[:line.find("|")].lower()
			moduleCode = line[line.find("|")+1:line.find("|")+3]
			modules[moduleCode] = moduleName
			if moduleName not in basicblocks:
				basicblocks[moduleName] = {}
			line = f.readline()
		
		#basicblock
		while line.strip() != "":
			moduleCode = line[0:2]
			bb = line[3:11]
			moduleName = modules[moduleCode].lower()
			if not basicblocks[moduleName][bb]:
				current += 1
			line = f.readline()
			
		if current > best:
			best = current
			bestName = fname
			
		f.close()
	
	#Best coverage file
	f = open(dir + "/" + bestName)
	
	#module list
	line = f.readline()
	modules = {}
	while line != "" and line[2] != "|":
		moduleName = line[:line.find("|")].lower()
		moduleCode = line[line.find("|")+1:line.find("|")+3]
		modules[moduleCode] = moduleName
		if moduleName not in basicblocks:
			basicblocks[moduleName] = {}
		line = f.readline()
		
	#basicblock
	while line.strip() != "":
		moduleCode = line[0:2]
		bb = line[3:11]
		moduleName = modules[moduleCode].lower()
		basicblocks[moduleName][bb] = True
		line = f.readline()
		
	f.close()		
	BBcount -= best
	results.append(bestName)
	print "%06d[%03d sec]: %s covered %d basicblocks, %d left" % (len(results), (time.time() - lastTime), bestName, best, BBcount)
	fout.write("%s\n" % bestName)

fout.close()
	