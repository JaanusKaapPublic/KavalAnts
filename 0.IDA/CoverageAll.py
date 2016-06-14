import os
from subprocess import call

idaPro = 'C:\\Program Files\\IDA 6.8\\idaq.exe'
codeCov = 'c:\\Work\\FF\\GenCoverageInfo.py' 
binDir = "C:\\Work\\FF\\bin\\"

for root, subFolder, files in os.walk(binDir):
	for item in files:
		fname = os.path.join(binDir, root, item)
		f=open(fname, "rb")
		if f.read(2) == 'MZ':
			print "Analysing '%s'" % fname
			#cmdLine = '"%s" -S"%s" -A "%s"' % (idaPro, codeCov, fname)			
			#print cmdLine
			#os.system(cmdLine)
			call([idaPro, '-S"' + codeCov + '"', '-A', fname])
		f.close()