#!/usr/bin/env python

# This is a small Python project to implement automatic continuous build for my projects.
# I currently have 3 types of builds: linux arm, linux x86 and windows x86. This tool
# needs to check the branches periodically to see if I have committed anywhere, and 
# automatically start a build.

import os
import sys
import datetime
import time
import threading
import pysvn
import Queue
import logging
import errno
import subprocess
import smtplib
from email.mime.text import MIMEText
import ConfigParser


## TODO
# -- add git repo support
# -- replace while true with decent condition
# -- let threads stop gracefully
# -- add windows build
# -- replace queue throttling with better alternative (wrap queue class and add 
#    internal check if item is on queue for instance)

##################################################################################
class Build:
	def __init__(self, name, path, lastauthor):
		self.name = name
		self.path = path
		self.lastauthor = lastauthor

class ThreadClass(threading.Thread):
	def __init__(self, queue, name):
		threading.Thread.__init__(self)
		self.queue = queue
		self.name = name
		self.client = pysvn.Client()

	def send_email(self, time, branch, to ):
		msg = MIMEText("Hi,\n your build on branch %s has %s" % ( branch, time ) )

		msg['Subject'] = 'Build report : the build on %s has %s' % ( branch, time )
		msg['From'] = "do-not-reply" + str(config.get('general', 'maildomain'))
		msg['To'] = to + str(config.get('general', 'maildomain'))

		# Send the message via our own SMTP server, but don't include the
		# envelope header.
		s = smtplib.SMTP('localhost')
		s.sendmail("do-not-reply" + str(config.get('general', 'maildomain')), to, msg.as_string())
		s.quit()

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
				retcode = subprocess.call(["ctest --script " + buildscript + ",platform=" + self.name + "\;branch=" + item[2].name + "\;repo=" + item[2].path.replace('svn://','') + "\;repotype=svn" + "\;configonly"], shell=True)
				if retcode < 0:
					log.debug(self.name + " " + item[2].name + " was terminated by signal: " + str(-retcode))
					self.queue.task_done()
					continue	
				else:
					log.debug(self.name + " " + item[2].name + " returned: " + str(retcode))
					self.send_email("finished", item[2].name, item[2].lastauthor)
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
	return True, config.get('subversion', 'user'), config.get('subversion', 'password'), True

def send_email( time, branch, to ):
	msg = MIMEText("Hi,\n your build on branch %s has %s" % ( branch, time ) )

	# me == the sender's email address
	# you == the recipient's email address
	msg['Subject'] = 'Build report : the build on %s has %s' % ( branch, time )
	msg['From'] = "do-not-reply" + str(config.get('general', 'maildomain'))
	msg['To'] = to + str(config.get('general', 'maildomain'))

	# Send the message via our own SMTP server, but don't include the
	# envelope header.
	s = smtplib.SMTP('localhost')
	s.sendmail("", to, msg.as_string())
	s.quit()

def addToBuildQueues(branchName, branchPath, numBranches):
		# perform quick check on queuesize to see if we must throttle
		# NOTE: this is a poor mans throttling attempt, needs replacing
		if(linuxArmQ.qsize() >= numBranches):
				log.debug('Linux Arm queue contains current number of branches, skipping: ' + branchName)
		else:
			try:
				# for now just using one priority. The second argument is used for sorting within a priority level
				linuxArmQ.put_nowait((1, 1, Build(branchName, branchPath)))
			except Queue.Full:
					log.debug('Linux Arm queue full, skipping: ' + branchName)

		# perform quick check on queuesize to see if we must throttle
		# NOTE: this is a poor mans throttling attempt, needs replacing
		if(linuxX86Q.qsize() >= numBranches):
				log.debug('Linux X86 queue contains current number of branches, skipping: ' + branchName)
		else:
			try:
				# for now just using one priority. The second argument is used for sorting within a priority level
				linuxX86Q.put_nowait((1, 1, Build(branchName, branchPath)))
			except Queue.Full:
					log.debug('Linux X86 queue full, skipping: ' + branchName)

def addSubversionBuilds():
	client = pysvn.Client()
	client.callback_get_login = get_login
	svnRepository = str(config.get('subversion', 'repository'))

	# find branch names (returns a list of tuples)
	branchList = client.list(svnRepository + '/branches', depth=pysvn.depth.immediates)

	# skip the first entry in the list as it is /branches (the directory in the repo)
	for branch in branchList[1:]:
		log.debug('Found branch: ' +  os.path.basename(branch[0].repos_path) + ' created at revision ' + str(branch[0].created_rev.number))
		addToBuildQueues(os.path.basename(branch[0].repos_path), svnRepository + branch[0].repos_path, len(branchList[1:]) + 1)
		send_email("started", branch[0].repos_path, branch[0].last_author)

	addToBuildQueues('trunk', svnRepository + '/trunk', len(branchList[1:]) + 1)
	send_email("started", "trunk", branch[0].last_author)

def writeDefaultConfig():
	try:
		defaultConfig = open(os.path.expanduser('~/buildqueue.examplecfg'), 'w')
		defaultConfig.write('[general]\n')
		defaultConfig.write('# loglevel may be one of: debug, info, warning, error, critical\n')
		defaultConfig.write('loglevel   : \n')
		defaultConfig.write('# for example @example.com\n')
		defaultConfig.write('maildomain : \n')
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

def main():
	global config
	config = ConfigParser.SafeConfigParser()
	configfiles = config.read(['/etc/buildqueue', os.path.expanduser('~/.buildqueue')])
	if (len(configfiles) == 0):
		print 'No config files found'
		writeDefaultConfig()
		sys.exit()

	try:
		config.get('general', 'loglevel')
		config.get('general', 'maildomain')
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

	while True:
		addSubversionBuilds()
		time.sleep(30)

##################################################################################
if __name__ == '__main__':
	main()
