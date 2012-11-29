#!/usr/bin/env python

# This is a small Python project to implement automatic continuous build for my projects.
# I currently have 3 types of builds: linux arm, linux x86 and windows x86. This tool
# needs to check the branches periodically to see if I have committed anywhere, and 
# automatically start a build.

import os
import shutil
import sys
from datetime import datetime,date
import time
import threading
import pysvn
import Queue
import logging
import errno
import subprocess
import ConfigParser
import logging.handlers
import pickle # for timestamp
import copy
import socket
import HTMLgen

# prints stacktraces for each thread
# acquired from http://code.activestate.com/recipes/577334-how-to-debug-deadlocked-multi-threaded-programs/
#sys.path.append('/path/to/tracemodule')
#import stacktracer

## TODO
# -- add git repo support
# -- replace while true with decent condition
# -- remove log output from terminal

##################################################################################
class BuildQueue(Queue.PriorityQueue):
	''' Wrapper class for Queue to filter out double entries '''
	def __init__(self, queuelength, platform):
		Queue.PriorityQueue.__init__(self, queuelength)
		self.builds = {} # maintain a hash of branches added to sift out doubles
		self.lock = threading.Lock()
		self.platform = platform
		self.current = ""
	
	def enqueue(self, item):
		# if a build is in the queue then don't add it again
		self.lock.acquire()
		try:
			if(self.builds[item[2].name]):
				# the queue already contains the branch meant for nightly as 'experimental'
				# change the buildtype of the one already in the queue to 'nightly'
				if(item[2].buildtype == 'nightly'):
					self.builds[item[2].name].setBuildType('nightly')
				else:
					log.debug('Branch ' + item[2].name + ' is already in the ' + self.platform + ' queue - skipping')
		except KeyError:
			# else put it in the buildqueue
			self.put_nowait(item)
			self.builds[item[2].name] = True
		self.lock.release()

	def dequeue(self):
		self.lock.acquire()
		item = self.get_nowait()
		del self.builds[item[2].name]
		self.current = item[2].name
		self.lock.release()
		return item

	def getPlatform(self):
		return self.platform

	def asList(self):
		queueAsString = self.platform + ":\n"
		for elem in self.queue:
			queueAsString += elem[2].getName() + "\n"

		queueAsString += " currently building: " + self.current + "\n"

		return queueAsString

	def asHTML(self):
			return self.list().replace("\n", "<br>")

class Build:
	def __init__(self, name, path, buildtype):
		self.name = name
		self.path = path
		self.buildtype = buildtype
		self.newbuild = False
		self.platform = ""

	def setPlatform(self, platform):
		self.platform = platform

	def getPlatform(self):
		return self.platform

	def getName(self):
		return self.name

	def setBuildType(self, buildtype):
		self.buildtype = buildtype

	def isNewBuild(self):
		return self.newbuild

	def prebuild(self):
		pass

	def build(self):
		pass

class SubversionBuild(Build):
	def __init__(self, name, path, buildtype):
		Build.__init__(self, name, path, buildtype)
		self.path = str(config.get('subversion', 'repository')) + path
		self.buildscript = ""

	def prebuild(self):
		if(self.platform == ''):
				log.warning("could not do prebuild for: " + name + " platform not set")
				return False

		self.exportpath = os.path.normpath(os.path.expandvars(str(config.get('general','pivotdirectory')) + '/' + self.platform + '/buildscripts'))
		self.buildscript = self.exportpath + '/' + self.name + '-build-stage2.cmake'

		try:
			os.makedirs(self.exportpath)
		except OSError, e:
			if e.errno == errno.EEXIST:
				pass
			else:
				return False

		if(not subversionClient.exportBuildScript(self.name, self.path + '/' + str(config.get('general','buildscript')), self.buildscript)):
			return False

		# check if this is a 'new' buildscript
		for line in open(self.buildscript):
			if "SERVERBUILD" in line:
				self.newbuild = True
				log.debug(self.platform + " " + self.name + " detected an new style buildscript")
				break

		return True

	def build(self):
		# run the buildscript
		try:
			command = "ctest"
			argument1 = "--script"
			argument2 = self.buildscript + ",platform=" + self.platform + ";branch=" + self.name + ";repo=" + self.path.replace('svn://','') + ";repotype=svn" + ";server" + ";" + self.buildtype
			#log.debug("cmdline: " + command + ' ' + argument1 + argument2)
			retcode = subprocess.call([command, argument1, argument2])

			if retcode < 0:
				log.warning(self.platform + " " + self.name + " was terminated by signal: " + str(-retcode))
				return
			else:
				log.info(self.platform + " " + self.name + " returned: " + str(retcode))
				return
		except OSError, e:
			log.warning(self.platform + " " + self.name + " execution failed: " + str(e))
			return

class GitBuild(Build):
	def __init__(self, name, path, buildtype):
		Build.__init__(self, name, path, buildtype)
		self.path = str(config.get('git', 'repository')) + path
		self.buildscript = ""

	def prebuild(self):
		pass

	def build(self):
		pass

class QueueThreadClass(threading.Thread):
	def __init__(self, queue, name):
		threading.Thread.__init__(self)
		self.queue = queue
		self.name = name
		self.stop_event = threading.Event()

	def stop(self):
		self.stop_event.set()

	def run(self):
		log.debug("%s started at time: %s" % (self.name, datetime.now()))

		while not self.stop_event.isSet():
			# returned value consists of: priority, sortorder, build object
			if not self.queue.empty():
				item = self.queue.dequeue()

				if(not item[2].prebuild()):
					self.queue.task_done()
					continue

				if(item[2].isNewBuild()):
					item[2].build()
					self.queue.task_done()
					continue
				else:
					log.debug(self.name + " " + item[2].getName() + " detected an old style buildscript - skipping")
					self.queue.task_done()
			else:
				time.sleep(30)

class SocketThreadClass(threading.Thread):
	def __init__(self, port):
		threading.Thread.__init__(self)
		self.port = port
		self.stop_event = threading.Event()

	def stop(self):
		self.stop_event.set()

	def run(self):
		log.debug("%s started at time: %s" % (self.name, datetime.now()))
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(('', self.port))
		s.listen(1)

		while not self.stop_event.isSet():
			try:
				conn, addr = s.accept()
				while 1:
					data = conn.recv(1024)

					if data:
						if "list" in data:
							for bqueue in BuildQueues[:]:
								log.debug(bqueue.asList())
								conn.sendall(bqueue.asList())
					else:
						break
			except socket.error, e:
				log.warning('failure on socket: ' + str(e))

			#try:
			#	doc = HTMLgen.SimpleDocument(title="BuildQueue")
			#	for bqueue in BuildQueues[:]:
			#		doc.append(bqueue.asHTML())

			#	conn.sendall(str(doc))
			#	doc = ""
			#except socket.timeout:
			#	break


			conn.close()

# Wrapper class to implement blocking locks
class SubversionClient():
	def __init__(self):
		self.client = pysvn.Client()
		self.client.callback_get_login = self.get_login
		self.svnRepository = str(config.get('subversion', 'repository'))
		self.lock = threading.Lock()

	# callback needed for the subversion client
	def get_login( realm, username, may_save ):
		"""callback implementation for Subversion login"""
		return True, config.get('subversion', 'user'), config.get('subversion', 'password'), True

	def getBranchList(self):
		log.debug('get branchlist in:')
		self.lock.acquire()
		branchList = []

		# find branch names (returns a list of tuples)
		try:
			branchList = self.client.list(self.svnRepository + '/branches', depth=pysvn.depth.immediates)
		except pysvn.ClientError, e:
			log.warning('Failed to get the branchlist: ' + str(e))

		self.lock.release()
		log.debug('get branchlist out:')
		return branchList

	def exportBuildScript(self, name, path, buildscript):
		log.debug('get buildscript in: ' + path)
		self.lock.acquire()
		# export the buildscript that will perform the actual build of the branch
		try:
			self.client.export(path, buildscript, force=True, recurse=False)
		except pysvn.ClientError, e:
			log.warning("Failed to export the buildscript for " + name + ':' + str(e))
			self.lock.release()
			return False

		self.lock.release()
		log.debug('get buildscript out: ' + path)
		return True

class Builds():
	def __init__(self, lastNightlyTime):
		self.lastNightlyTime = lastNightlyTime

	def processBuilds(self):
		print "process default builds"

class SubversionBuilds(Builds):
	def __init__(self, lastNightlyTime):
		Builds.__init__(self, lastNightlyTime)

	def processBuilds(self):
		# Nightly
		if checkNightlyTimestamp(self.lastNightlyTime, datetime.now()):
			addToBuildQueues(SubversionBuild('trunk', '/trunk', 'nightly'))
			self.lastNightlyTime = getNightlyTimestamp()
			log.info('Inserted nightly')
		else:
			addToBuildQueues(SubversionBuild('trunk', '/trunk', 'experimental'))

		branchList = subversionClient.getBranchList()

		# may have failed if server could not be reached
		if branchList:
			# skip the first entry in the list as it is /branches (the directory in the repo)
			for branch in branchList[1:]:
				log.debug('Found branch: ' +  os.path.basename(branch[0].repos_path) + ' created at revision ' + str(branch[0].created_rev.number))
				addToBuildQueues(SubversionBuild(os.path.basename(branch[0].repos_path), branch[0].repos_path, 'experimental'))

			# clean up builddirectories for which no branch exists anymore
			for queue in BuildQueues[:]:
				builddirpath = os.path.normpath(os.path.expandvars(str(config.get('general','pivotdirectory')) + '/' + queue.getPlatform() + '/build'))
				builddirList = os.listdir(builddirpath)
				for branch in branchList[1:]:
					try:
						builddirList.remove(os.path.basename(branch[0].repos_path))
					except:
						log.info(queue.getPlatform() + ': no builddir exists for ' + os.path.basename(branch[0].repos_path))

				try:
					builddirList.remove('trunk')
				except:
					log.info(queue.getPlatform() + ': no builddir exists for trunk')

				for builddir in builddirList[:]:
					try:
						log.info(queue.getPlatform() + ': removing build directory for: ' + builddirpath + '/' + builddir)
						shutil.rmtree(builddirpath + '/' + builddir)
					except OSError, e:
						log.warning(queue.getPlatform() + ': failed to remove build directory for: ' + builddirpath + '/' + builddir + ' :' + str(e))

class GitBuilds():
	def __init__(self, lastNightlyTime):
		Builds.__init__(self, lastNightlyTime)

	def processBuilds(self):
		print "processed Git builds"

##################################################################################
def addToBuildQueues(build):
	for bqueue in BuildQueues[:]:
		try:
			buildcopy = copy.copy(build)
			buildcopy.setPlatform(bqueue.getPlatform())
			# for now just using one priority. The second argument is used for sorting within a priority level
			bqueue.enqueue((1, 1, buildcopy))
		except Queue.Full:
			log.warning(bqueue.name + ' queue full, skipping: ' + buildcopy.name)

def writeDefaultConfig():
	try:
		defaultConfig = open(os.path.expanduser('~/buildqueue.examplecfg'), 'w')
		defaultConfig.write('[general]\n')
		defaultConfig.write('pivotdirectory : \n')
		defaultConfig.write('buildscript : \n')
		defaultConfig.write('# loglevel may be one of: debug, info, warning, error, critical\n')
		defaultConfig.write('loglevel   : \n')
		defaultConfig.write('port : \n')
		defaultConfig.write('[subversion]\n')
		defaultConfig.write('repository : <repository url>\n')
		defaultConfig.write('user       : <username>\n')
		defaultConfig.write('password   : <password>\n')
		defaultConfig.write('[git]\n')
		defaultConfig.write('repository : <repository url>\n')
		defaultConfig.close()
		print 'Default configuration written as: ' + defaultConfig.name
	except IOError, e:
		print 'Failed to write default configuration: ' + str(e)

	sys.exit()

def getNightlyTimestamp():
	lastNightlyTime = datetime(date.today().year, date.today().month, date.today().day, 1, 0, 0)
	lastNightlyFile = 'buildqueue.nightlytimestamp'

	if os.path.exists(lastNightlyFile):
		try:
			f = open(lastNightlyFile, 'r+b')
			lastNightlyTime = pickle.load(f)
			f.close()
		except IOError, e:
			log.warning("Could not read nightly timestamp file, using today")
	else:
		updateNightlyTimestamp(lastNightlyTime)

	return lastNightlyTime

def updateNightlyTimestamp(lastNightlyTime):
	lastNightlyFile = 'buildqueue.nightlytimestamp'

	try:
		f = open(lastNightlyFile, 'wb')
		pickle.dump(lastNightlyTime, f)
		f.close()
	except IOError, e:
		log.warning("Could not write nightly timestamp file, using today")

def checkNightlyTimestamp(lastNightlyTime, currentTime):
	delta = currentTime - lastNightlyTime

	if(delta.total_seconds() > (24 * 3600)):
		newNightlyTime = datetime(date.today().year, date.today().month, date.today().day, 1, 0, 0)
		updateNightlyTimestamp(newNightlyTime)
		return True
	else:
		return False

def main():
	#stacktracer.trace_start("trace.html",interval=5,auto=True)

	global config
	config = ConfigParser.SafeConfigParser()
	configfiles = config.read(['/etc/buildqueue', os.path.expanduser('~/.buildqueue')])
	if (len(configfiles) == 0):
		print 'No config files found'
		writeDefaultConfig()
		sys.exit()

	try:
		config.get('general', 'port')
		config.get('general', 'buildscript')
		config.get('general', 'loglevel')
		config.get('general', 'pivotdirectory')
		config.get('subversion', 'repository')
		config.get('subversion', 'user')
		config.get('subversion', 'password')
	except ConfigParser.Error, e:
		print str(e)
		writeDefaultConfig()

	# setup logging for both console and file
	numeric_level = getattr(logging, str(config.get('general', 'loglevel')).upper(), None)
	if not isinstance(numeric_level, int):
		    raise ValueError('Invalid log level: %s' % config.get('general', 'loglevel'))

	messageFormat = '%(asctime)s %(levelname)-8s %(message)s'
	dateTimeFormat = '%d-%m-%Y %H:%M:%S'

	# setup logger with default console logger
	logging.basicConfig(level=numeric_level,
			format= messageFormat,
			datefmt= dateTimeFormat)

	global log
	log = logging.getLogger()

	fh = logging.handlers.RotatingFileHandler('buildbot.log', maxBytes=1048576, backupCount=5)
	fh.setFormatter(logging.Formatter(messageFormat, dateTimeFormat))
	log.addHandler(fh)

	log.debug('starting main loop')

	global subversionClient
	subversionClient = SubversionClient()

	QueueLen    = 48 # just a stab at a sane queue length
	global BuildQueues
	BuildQueues = []

	if sys.platform[:5] == 'linux':
		BuildQueues.append(BuildQueue(QueueLen, 'linux-arm'))
		BuildQueues.append(BuildQueue(QueueLen, 'linux-x86'))
	elif sys.platform[:3] == 'win':
		BuildQueues.append(BuildQueue(QueueLen, 'windows-x86'))
	else:
		log.warning("Unknown platform, don't know which buildqueue to start")
		sys.exit()

	Threads = []
	# Start build queue threads
	for queue in BuildQueues[:]:
		Threads.append(QueueThreadClass(queue, queue.getPlatform()))

	# Start socket to show buildqueues
	Threads.append(SocketThreadClass(config.getint('general', 'port')))

	for thread in Threads[:]
	try:
		thread.start()
		# let threads be killed when main is killed
		thread.setDaemon(True)
	except (KeyboardInterrupt, SystemExit):
		thread.stop()
		thread.join()
		return

	lastNightlyTime = getNightlyTimestamp()
	subversionBuilds = SubversionBuilds(lastNightlyTime)

	while True:
		subversionBuilds.processBuilds()
		time.sleep(30)

	#stacktracer.trace_stop()

##################################################################################
if __name__ == '__main__':
	main()
