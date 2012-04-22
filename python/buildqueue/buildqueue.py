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


## TODO
# -- add check to create local builddirs
# -- add logging
# -- add build/skip mail
# -- add call to buildstep
# -- add git repo support


verbose = False
QueueLen    = 48
linuxArmQ   = Queue.PriorityQueue(QueueLen)
linuxX86Q   = Queue.PriorityQueue(QueueLen)
windowsX86Q = Queue.PriorityQueue(QueueLen)
branchPreviousBuilds = {}
SubversionUser = ''
SubversionPassword = ''

##################################################################################
class Build:
	def __init__(self, path):
		self.path = path

class ThreadClass(threading.Thread):
	def __init__(self, queue, name):
		threading.Thread.__init__(self)
		self.queue = queue
		self.name = name

	def run(self):
		now = datetime.datetime.now()
		print "%s started at time: %s" % (self.name, now)
		while True:
			# returned value consists of: priority, sortorder, build object
			item = self.queue.get()
			# pretend we're doing something that takes 10-100 ms
			time.sleep(random.randint(10, 100) / 1000.0)
			print self.name + ': done build ' + item[2].path
			self.queue.task_done()

##################################################################################
def get_login( realm, username, may_save ):
	"""callback implementation for Subversion login"""
	return True, SubversionUser, SubversionPassword, True

def addToBuildQueues(svnBranch):
		global linuxArmQ 
		global linuxX86Q 
		global windowsX86Q

		# for now just using one priority. The second argument is used for sorting within a priority level
		try:
			linuxArmQ.put_nowait((1, 1, Build(svnBranch)))
		except Queue.Full:
			if(verbose):
				print 'Linux Arm queue full, skipping: ' + svnBranch

		try:
			linuxX86Q.put_nowait((1, 1, Build(svnBranch)))
		except Queue.Full:
			if(verbose):
				print 'Linux X86 queue full, skipping: ' + svnBranch

		try:
			windowsX86Q.put_nowait((1, 1, Build(svnBranch)))
		except Queue.Full:
			if(verbose):
				print 'Windows X86 queue full, skipping: ' + svnBranch

def addSubversionBuilds(svnRepository, svnUser, svnPassword):
	if(verbose):
		print 'Using Subversion repository: ' + svnRepository
		print 'Using Subversion user      : ' + svnUser
		print 'Using Subversion password  : ' + svnPassword
	
	client = pysvn.Client()
	client.callback_get_login = get_login
	global SubversionUser
	global SubversionPassword

	SubversionUser = svnUser
	SubversionPassword = svnPassword

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

		# check if there was a previous build, and if current revision is newer
		global branchPreviousBuilds

		if branch[0].repos_path in branchPreviousBuilds:
			if branch[0].created_rev.number > branchPreviousBuilds[branch[0].repos_path]:
				addToBuildQueues(branch[0].repos_path)
			else:
				print'Branch ' + branch[0].repos_path + ' is has not been updated. Skipping build'
		else:
			branchPreviousBuilds[branch[0].repos_path] = branch[0].created_rev.number
			addToBuildQueues(branch[0].repos_path)

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
