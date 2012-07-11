#!/usr/bin/env python

# This is a small Python project to implement automatic continuous build for my projects.
# I currently have 3 types of builds: linux arm, linux x86 and windows x86. This tool
# needs to check the branches periodically to see if I have committed anywhere, and 
# automatically start a build.

import os
import getopt
import sys
import datetime
import time
import threading
import pysvn
import Queue
import random
import logging
import errno
import subprocess


## TODO
# -- add check to create local builddirs
# -- add build/skip mail
# -- add git repo support
# -- replace while true with decent condition
# -- let threads stop gracefully
# -- add windows build

##################################################################################
class Build:
	def __init__(self, name, path):
		self.name = name
		self.path = path

class ThreadClass(threading.Thread):
	def __init__(self, queue, name):
		threading.Thread.__init__(self)
		self.queue = queue
		self.name = name
		self.client = pysvn.Client()

	def run(self):
		self.client.callback_get_login = get_login
		now = datetime.datetime.now()
		log.debug("%s started at time: %s" % (self.name, now))
		exportpath = os.environ['HOME'] + '/' + self.name + '/buildscripts'
		try:
			os.makedirs(exportpath)
		except OSError, e:
			if e.errno == errno.EEXIST:
				pass
			else: raise

		while True:
			# returned value consists of: priority, sortorder, build object
			item = self.queue.get()
			buildscript = exportpath + '/' + item[2].name + '-build2.cmake'
			
			# export the buildscript that will perform the actual build of the branch
			try:
				self.client.export(item[2].path + '/3-Code/31-Build-Tools/Scripts/build2.cmake', buildscript, recurse=False)
			except pysvn.ClientError, e:
				log.debug("Failed to export the buildscript for " + item[2].name + ':' + str(e))
				self.queue.task_done()
				continue

			# run the buildscript
			try:
				retcode = subprocess.call(["ctest --script " + buildscript + ",arch=" + self.name + "\;configonly"], shell=True)
				if retcode < 0:
					log.debug(self.name + " " + item[2].name + " was terminated by signal: " + str(-retcode))
					self.queue.task_done()
					continue	
				else:
					log.debug(self.name + " " + item[2].name + " returned: " + str(retcode))
					self.queue.task_done()
					continue
			except OSError, e:
				log.debug(self.name + " " + item[2].name + " execution failed: " + e)
				self.queue.task_done()
				continue	

			log.debug(self.name + " " + item[2].name + ': done build ' + item[2].name)
			self.queue.task_done()

##################################################################################
# callback needed for the subversion client
def get_login( realm, username, may_save ):
	"""callback implementation for Subversion login"""
	return True, SubversionUser, SubversionPassword, True

def addToBuildQueues(branchName, branchPath):
		# for now just using one priority. The second argument is used for sorting within a priority level
		try:
			linuxArmQ.put_nowait((1, 1, Build(branchName, branchPath)))
		except Queue.Full:
				log.debug('Linux Arm queue full, skipping: ' + branchName)

		try:
			linuxX86Q.put_nowait((1, 1, Build(branchName, branchPath)))
		except Queue.Full:
				log.debug('Linux X86 queue full, skipping: ' + branchName)

def addSubversionBuilds(svnRepository):
	client = pysvn.Client()
	client.callback_get_login = get_login

	# find branch names (returns a list of tuples)
	branchList = client.list(svnRepository + '/branches', depth=pysvn.depth.immediates)

	# skip the first entry in the list as it is /branches (the directory in the repo)
	for branch in branchList[1:]:
		log.debug('Found branch: ' +  os.path.basename(branch[0].repos_path) + ' created at revision ' + str(branch[0].created_rev.number))
		addToBuildQueues(os.path.basename(branch[0].repos_path), svnRepository + branch[0].repos_path)
	
	addToBuildQueues('trunk', svnRepository + '/trunk')

def usage():
	print ''
	print 'A threaded continuous buildserver'
	print ''
	print '-h, --help                 = print this help message'
	print '-l, --log                  = set loglevel (debug, info, warning, error, critical)'
	print '-r, --subversionrepository = use the given subversion repository'
	print '-u, --subversionuser       = use the given subversion user'
	print '-p, --subversionpassword   = use the given subversion password'
	print ''
	sys.exit()

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hr:u:p:l:", ["help", "subversionrepository", "subversionuser", "subversionpassword", "log"])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()

	global SubversionUser
	global SubversionPassword
	SubversionRepository = None
	loglevel      = 'debug'

	for o, a in opts:
		if o in ("-l", "--log"):
			loglevel = a 
		elif o in ("-h", "--help"):
			usage()
		elif o in ("-r", "--subversionrepository"):
			SubversionRepository = a
		elif o in ("-u", "--subversionuser"):
			SubversionUser = a
		elif o in ("-p", "--subversionpassword"):
			SubversionPassword = a
		else:
			assert False, "unhandled option"

	# setup logging for both console and file
	numeric_level = getattr(logging, loglevel.upper(), None)
	if not isinstance(numeric_level, int):
		    raise ValueError('Invalid log level: %s' % loglevel)

	logging.basicConfig(format='%(levelname)s: %(message)s', level=numeric_level)
	fh  = logging.FileHandler('buildbot.log')
	fh_fmt = logging.Formatter("%(levelname)s\t: %(message)s")
	fh.setFormatter(fh_fmt)

	global log
	log = logging.getLogger()

	log.addHandler(fh)

	log.debug('starting main loop')

	QueueLen    = 48 # just a stab at a sane queue length
	global linuxArmQ
	global linuxX86Q

	linuxArmQ   = Queue.PriorityQueue(QueueLen)
	linuxX86Q   = Queue.PriorityQueue(QueueLen)

	# Start build queue threads
	linux_armQ = ThreadClass(linuxArmQ, 'linux-arm')
	linux_x86Q = ThreadClass(linuxX86Q, 'linux-x86')

	# let threads be killed when main is killed
	linux_armQ.setDaemon(True)
	linux_x86Q.setDaemon(True)

	try:
		linux_armQ.start()
		linux_x86Q.start()
	except (KeyboardInterrupt, SystemExit):
		linux_armQ.join()
		linux_x86Q.join()
		sys.exit()

	log.debug('Using Subversion repository: ' + SubversionRepository)
	log.debug('Using Subversion user      : ' + SubversionUser)
	log.debug('Using Subversion password  : ' + SubversionPassword)

	while True:
		addSubversionBuilds(SubversionRepository)
		time.sleep(10)


##################################################################################
if __name__ == '__main__':
	if(len(sys.argv[1:]) < 3):
		usage()
	main()
