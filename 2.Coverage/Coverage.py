import os
from winappdbg import Debug, Crash, win32, HexDump
from time import time
from winappdbg.util import MemoryAddresses



class Coverage:
	bbFiles = {}
	bbFilesBreakpints = []
	bbFilesData = {}
	modules = []
	fileOutput = None

	#load basic blocks
	def loadBB(self, baseBbDir):
		self.bbFiles = {}
		count = 0
		for bbFile in os.listdir(baseBbDir):
			f = open(baseBbDir + "/" + bbFile, "r")
			fname = f.readline().strip()
			self.bbFiles[fname] = count
			self.bbFilesBreakpints.append({})
			rvaHighest = 0
			for line in f:
				rva = int(line[0:8], 16)
				val = int(line[18:20], 16)
				self.bbFilesBreakpints[count][rva] = val
				if rva > rvaHighest:
					rvaHighest = rva
			self.bbFilesData[fname] = [rvaHighest + 10, count]
			count += 1
			f.close()
	
	#Register module (original exe image or dll)
	def registerModule(self, filename, baseaddr):
		if filename not in self.bbFiles:
			return
		print "  Image %s has breakpoints defined" % filename
		self.modules.append([baseaddr,baseaddr+self.bbFilesData[filename][0], self.bbFilesData[filename][1]])
		print "  Image has breakpoints from %08X to %08X with index %d" % (baseaddr,baseaddr+self.bbFilesData[filename][0],self.bbFilesData[filename][1])
		
	#Handle a breakpoint
	def breakpoint(self, location):
		index = None
		for i in xrange(len(self.modules)):
			if location>=self.modules[i][0] and location<=self.modules[i][1]:
				index = i
				break
		if index == None:
			return None	
		rva = location - self.modules[index][0]
		if rva not in self.bbFilesBreakpints[index]:
			return None
		self.fileOutput.write("%02X|%08X\n" % (index, rva))
		return self.bbFilesBreakpints[index][rva]
		
	def startFileRec(self, filename):
		self.modules = []
		self.fileOutput = open(filename, "w")
		for image in self.bbFiles:
			self.fileOutput.write("%s|%02X\n" % (image, self.bbFiles[image]))
		
	def endFileRec(self):
		self.fileOutput.close()		
	
	#Start program
	def start(self, execFile, waitTime = 6, recFilename = "output.txt"):	
		self.startFileRec(recFilename)
		debugger = Debug( bKillOnExit = True )
		mainProc = debugger.execv( execFile, bFollow = True )
		event = None
		endTime = time() + waitTime
		while time() < endTime:
			if not mainProc.is_alive():
				break
			try:
				event = debugger.wait(1000)
			except WindowsError, e:
				if e.winerror in (win32.ERROR_SEM_TIMEOUT, win32.WAIT_TIMEOUT):
					continue
				raise
			
			if event.get_event_code() == win32.LOAD_DLL_DEBUG_EVENT:
				module = event.get_module()
				print "DLL %s loaded on base %08X" % (module.get_name(), module.get_base())
				self.registerModule(module.get_name(), module.get_base())
			elif event.get_event_code() == win32.CREATE_PROCESS_DEBUG_EVENT:
				tmp = event.get_filename().split("\\")
				modName = tmp[len(tmp)-1]
				print "Process %s loaded on base %08X" % (modName, event.raw.u.CreateProcessInfo.lpBaseOfImage)
				self.registerModule(modName,event.raw.u.CreateProcessInfo.lpBaseOfImage)
			elif event.get_event_code() == win32.EXCEPTION_DEBUG_EVENT and event.get_exception_code() == win32.STATUS_BREAKPOINT:
				pc = event.get_thread().get_pc()-1
				val = self.breakpoint(pc)
				if val != None:
					event.get_process().write(pc, chr(val))
					event.get_thread().set_pc(pc)
			else:
				print event.get_event_code()
	
			try:
				debugger.dispatch()
			except:
				pass
			finally:
				debugger.cont()
		self.endFileRec()
		
cov = Coverage()
cov.loadBB("./KavalAntsBB")
cov.start(["./Winobj.exe"], 30)