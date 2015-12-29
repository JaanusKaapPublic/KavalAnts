import os
import shutil


baseExecDir = "./"
baseBbDir = "./KavalAntsBB"

#Load BB files
print "Loading all BB files"
bbFiles = {}
confFiles = {}
for bbFile in os.listdir(baseBbDir):
	f = open(baseBbDir + "/" + bbFile, "r")
	fname = f.readline().strip()
	bbFiles[fname] = []
	confFiles[fname] = baseBbDir + "/" + bbFile
	f.close()
	
#Find files
print "Finding files to modify"
for root, subFolder, files in os.walk(baseExecDir):
	for item in files:
		if item in bbFiles:
			bbFiles[item].append(str(os.path.join(baseExecDir, root, item)))
			
#Any file not found
for fname in bbFiles:
	if len(bbFiles[fname]) == 0:
		print ">>>No file named '%s' was found" % fname
		del bbFiles[fname]
		del confFiles[f.readline().strip()]
	
#Lets start the modifications
for fname in bbFiles:
	for target in bbFiles[fname]:
		print "Modifying %s based of BB-s in %s" % (target, confFiles[fname])
		shutil.copyfile(target, target + "_original")
		f = open(confFiles[fname], "r")
		fa = open(target, "r+b")
		
		f.readline()
		for line in f:
			offset = int(line[9:17], 16)
			fa.seek(offset)
			fa.write(chr(0xCC))
			
		f.close()
		fa.close()
print "DONE"