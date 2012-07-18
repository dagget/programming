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
from logging.handlers import RotatingFileHandler


## TODO
# -- add git repo support
# -- replace while true with decent condition
# -- let threads stop gracefully

##################################################################################
class BuildQueue(Queue.PriorityQueue):
	''' Wrapper class for Queue to filter out double entries '''
	def __init__(self, queuelength, platform):
		Queue.PriorityQueue.__init__(self, queuelength)
		self.builds = {} # maintain a hash of branches added to sift out doubles
		self.lock = threading.Lock()
		self.platform = platform
	
	def enqueue(self, item):
		# if a build is in the queue then don't add it again
		self.lock.acquire()
		try:
			if(self.builds[item[2].name]):
				print 'Branch ' + item[2].name + ' is already in the queue - skipping'
		except KeyError:
			# else put it in the buildqueue
			self.put_nowait(item)
			self.builds[item[2].name] = True
		self.lock.release()

	def dequeue(self):
		item = self.get()
		self.lock.acquire()
		del self.builds[item[2].name]
		self.lock.release()
		return item

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
		#s.sendmail("do-not-reply" + str(config.get('general', 'maildomain')), to, msg.as_string())
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
			item = self.queue.dequeue()
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

def addToBuildQueues(build):
	for queue in BuildQueues[:]:
			try:
				# for now just using one priority. The second argument is used for sorting within a priority level
				queue.enqueue((1, 1, build))
			except Queue.Full:
					log.debug(queue.name + ' queue full, skipping: ' + build.name)

def addSubversionBuilds():
	client = pysvn.Client()
	client.callback_get_login = get_login
	svnRepository = str(config.get('subversion', 'repository'))

	# find branch names (returns a list of tuples)
	branchList = client.list(svnRepository + '/branches', depth=pysvn.depth.immediates)

	# skip the first entry in the list as it is /branches (the directory in the repo)
	for branch in branchList[1:]:
		log.debug('Found branch: ' +  os.path.basename(branch[0].repos_path) + ' created at revision ' + str(branch[0].created_rev.number))
		addToBuildQueues(Build(os.path.basename(branch[0].repos_path), svnRepository + branch[0].repos_path, branch[0].last_author))

	addToBuildQueues(Build('trunk', svnRepository + '/trunk', branch[0].last_author))

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
	fh  = logging.handlers.RotatingFileHandler('buildbot.log', maxBytes=1048576, backupCount=5)
	fh_fmt = logging.Formatter("%(levelname)s\t: %(message)s")
	fh.setFormatter(fh_fmt)

	global log
	log = logging.getLogger()
	log.addHandler(fh)
	log.debug('starting main loop')

	QueueLen    = 48 # just a stab at a sane queue length
	global BuildQueues
	BuildQueues = []

	if sys.platform[:5] == 'linux':
		BuildQueues.append(BuildQueue(QueueLen, 'linux-arm'))
		BuildQueues.append(BuildQueue(QueueLen, 'linux-x86'))
	elif sys.platform[:3] == 'win':
		BuildQueues.append(BuildQueue(QueueLen, 'windows-x86'))
	else:
		log.debug("Unknown platform, don't know which buildqueue to start")
		sys.exit()

	# Start build queue threads
	for queue in BuildQueues[:]:
		thread = ThreadClass(queue, queue.platform)
		# let threads be killed when main is killed
		thread.setDaemon(True)

		try:
			thread.start()
		except (KeyboardInterrupt, SystemExit):
			thread.join()
			sys.exit()

	while True:
		addSubversionBuilds()
		time.sleep(30)

##################################################################################
if __name__ == '__main__':
	main()
