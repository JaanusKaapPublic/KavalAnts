import os
import shutil
import getopt
import sys
import time


dir = ".\\input"
tmpDir = ".\\tmp"
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

#Create tmp dirs
if not os.path.exists(tmpDir + "0"):
	os.makedirs(tmpDir + "0")
if not os.path.exists(tmpDir + "1"):
	os.makedirs(tmpDir + "1")
		
#Prep
filelist = os.listdir(dir)
tmpCount = 0x1
		
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
freport = open(output, 'w')
srcDir = dir
destDir = tmpDir + "0"
while BBcount>0:
	best = 0;
	bestName = None	
	lastTime = time.time()
	
	#Find largest file
	for fname in filelist:
		if fname in results:
			continue
		size = os.path.getsize(srcDir + "/" + fname)
		if size > best:
			best = size
			bestName = fname			
			
	#Best coverage file
	f = open(srcDir + "/" + bestName)	
	best = 0
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
		best+=1		
	f.close()
			
	
	#Remove covered blocks
	for fname in filelist:
		f = open(srcDir + "/" + fname, "r")
		fout = open(destDir + "/" + fname, "w")	
		#module list
		line = f.readline()
		modules = {}
		while line != "" and line[2] != "|":
			fout.write(line)
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
				fout.write(line)
			line = f.readline()			
		f.close()
		fout.close()
	
	BBcount -= best
	results.append(bestName)
	print "%06d[%03d sec]: %s covered %d basicblocks, %d left" % (len(results), (time.time() - lastTime), bestName, best, BBcount)
	freport.write("%s\n" % bestName)
	destDir = tmpDir + str(tmpCount)
	tmpCount = tmpCount ^ 0x1
	srcDir = tmpDir + str(tmpCount)

freport.close()
	