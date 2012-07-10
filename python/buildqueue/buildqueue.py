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


## TODO
# -- add check to create local builddirs
# -- add build/skip mail
# -- add call to buildstep
# -- add git repo support
# -- replace while true with decent condition
# -- let threads stop gracefully
# -- add windows build

QueueLen    = 48
linuxArmQ   = Queue.PriorityQueue(QueueLen)
linuxX86Q   = Queue.PriorityQueue(QueueLen)
branchPreviousBuilds = {}
SubversionUser = ''
SubversionPassword = ''
log = logging.getLogger()

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

	def run(self):
		now = datetime.datetime.now()
		log.debug("%s started at time: %s" % (self.name, now))
		while True:
			# returned value consists of: priority, sortorder, build object
			item = self.queue.get()

			# pretend we're doing something that takes 10-100 ms
			time.sleep(random.randint(10, 100) / 1000.0)

			log.debug(self.name + ': done build ' + item[2].name)
			self.queue.task_done()

##################################################################################
def get_login( realm, username, may_save ):
	"""callback implementation for Subversion login"""
	return True, SubversionUser, SubversionPassword, True

def addToBuildQueues(branchName, branchPath):
		global linuxArmQ 
		global linuxX86Q 
		#global windowsX86Q

		# for now just using one priority. The second argument is used for sorting within a priority level
		try:
			linuxArmQ.put_nowait((1, 1, Build(branchName, branchPath)))
		except Queue.Full:
				log.debug('Linux Arm queue full, skipping: ' + branchName)

		try:
			linuxX86Q.put_nowait((1, 1, Build(branchName, branchPath)))
		except Queue.Full:
				log.debug('Linux X86 queue full, skipping: ' + branchName)

def addSubversionBuilds(svnRepository, svnUser, svnPassword):
	log.debug('Using Subversion repository: ' + svnRepository)
	log.debug('Using Subversion user      : ' + svnUser)
	log.debug('Using Subversion password  : ' + svnPassword)
	
	client = pysvn.Client()
	client.callback_get_login = get_login
	global SubversionUser
	global SubversionPassword

	SubversionUser = svnUser
	SubversionPassword = svnPassword

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

	svnRepository = None
	svnUser       = None
	svnPassword   = None
	loglevel      = 'debug'

	for o, a in opts:
		if o in ("-l", "--log"):
			loglevel = a 
		elif o in ("-h", "--help"):
			usage()
		elif o in ("-r", "--subversionrepository"):
			svnRepository = a
		elif o in ("-u", "--subversionuser"):
			svnUser = a
		elif o in ("-p", "--subversionpassword"):
			svnPassword = a
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
	log.addHandler(fh)

	log.debug('starting main loop')

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

	while True:
		addSubversionBuilds(svnRepository, svnUser, svnPassword)
		time.sleep(10)

##################################################################################
if __name__ == '__main__':
	if(len(sys.argv[1:]) < 3):
		usage()
	main()
