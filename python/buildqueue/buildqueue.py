#!/usr/bin/env python

import os
import getopt
import sys
import datetime
import time
import threading
import pysvn
import Queue

verbose = False
QueueLen    = 48
linuxArmQ   = Queue.PriorityQueue(QueueLen)
linuxX86Q   = Queue.PriorityQueue(QueueLen)
windowsX86Q = Queue.PriorityQueue(QueueLen)

##################################################################################
class Build:
	def __init__(self, path, revision):
		self.path = path
		self.previousRevision = revision

class ThreadClass(threading.Thread):
	def __init__(self, queue, name):
		threading.Thread.__init__(self)
		self.queue = queue
		self.name = name

	def run(self):
		now = datetime.datetime.now()
		print "%s started at time: %s" % (self.name, now)
		while True:
			build = self.queue.get()
			print self.name + ': received build ' + build.path + ' with rev: ' + str(build.previousRevision)
			self.queue.task_done()

##################################################################################
def addSubversionBuilds(svnRepository, svnUser, svnPassword):
	if(verbose):
		print 'Using Subversion repository: ' + svnRepository
		print 'Using Subversion user      : ' + svnUser
		print 'Using Subversion password  : ' + svnPassword
	
	client = pysvn.Client()
	# find branch names
	branchList = client.list(svnRepository + '/branches', depth=pysvn.depth.immediates)

	# find branch revisions
	branchRevisionList = []

	for branch in branchList[1:]:
		try:
				branchRevisionList += client.list( branch[0].path + '/3-Code', depth=pysvn.depth.empty)
		except pysvn.ClientError, e:
			# convert to a string
			print 'Error: ' + str(e)

	branchRevisionList += client.list(svnRepository + '/trunk/3-Code', depth=pysvn.depth.empty)

	for branch in branchRevisionList[:]:
		if(verbose):
			print 'Found branch: ' +  branch[0].repos_path + ' with revision ' + str(branch[0].created_rev.number)
		global linuxArmQ 
		global linuxX86Q 
		global windowsX86Q

		linuxArmQ.put(Build(branch[0].repos_path, branch[0].created_rev.number))
		linuxX86Q.put(Build(branch[0].repos_path, branch[0].created_rev.number))
		windowsX86Q.put(Build(branch[0].repos_path, branch[0].created_rev.number))

def usage():
	print ''
	print 'A threaded continuous buildserver'
	print ''
	print '-h, --help                 = print this help message'
	print '-v, --verbose              = be verbose'
	print '-r, --subversionrepository = use the given subversion repository'
	print '-u, --subversionuser       = use the given subversion user'
	print '-p, --subversionpassword   = use the given subversion password'
	print ''
	sys.exit()

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hr:u:p:v", ["help", "subversionrepository", "subversionuser", "subversionpassword", "verbose"])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()

	svnRepository = None
	svnUser       = None
	svnPassword   = None

	for o, a in opts:
		if o in ("-v", "--verbose"):
			global verbose
			verbose = True
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


	linux_armQ = ThreadClass(linuxArmQ, 'linux-arm')
	linux_armQ.setDaemon(True)
	linux_armQ.start()
	linux_x86Q = ThreadClass(linuxX86Q, 'linux-x86')
	linux_x86Q.setDaemon(True)
	linux_x86Q.start()
	windows_x86Q = ThreadClass(windowsX86Q, 'windows-x86')
	windows_x86Q.setDaemon(True)
	windows_x86Q.start()

	while True:
		addSubversionBuilds(svnRepository, svnUser, svnPassword)
		time.sleep(10)

	linux_armQ.join()
	linux_x86Q.join()
	windows_x86Q.join()

##################################################################################
if __name__ == '__main__':
	if(len(sys.argv[1:]) < 3):
		usage()
	main()
