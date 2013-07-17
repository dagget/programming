#!/usr/bin/env python

# This is a small script that checks for out of source builddirectories on a buildbot slave.
# If a builddirectory does not have a associated branch, then we remove it to save space.
# We also list branches that don't have builddirectories, as that is an indicator for unused
# branches.

import os
import shutil
import sys
import pysvn
import logging
import errno
import logging.handlers
import ConfigParser
import re

# prints stacktraces for each thread
# acquired from http://code.activestate.com/recipes/577334-how-to-debug-deadlocked-multi-threaded-programs/
#sys.path.append('/path/to/tracemodule')
#import stacktracer

##################################################################################
class Config(ConfigParser.SafeConfigParser):
	def __init__(self):
		ConfigParser.SafeConfigParser.__init__(self)
		self.configfiles = self.read(['/etc/buildbot-cleanup', os.path.expanduser('~/.buildbot-cleanup')])
		if (len(self.configfiles) == 0):
			print 'No config files found'
			self.writeDefaultConfig()
			sys.exit()

		try:
			self.get('general', 'loglevel')
			self.items('buildpaths')
			self.get('subversion', 'repository')
			self.get('subversion', 'user')
			self.get('subversion', 'password')
		except ConfigParser.Error, e:
			print str(e)
			self.writeDefaultConfig()

	def writeDefaultConfig(self):
		try:
			defaultConfig = open(os.path.expanduser('~/buildbot-cleanup.examplecfg'), 'w')
			defaultConfig.write('[general]\n')
			defaultConfig.write('# loglevel may be one of: debug, info, warning, error, critical\n')
			defaultConfig.write('loglevel   : \n')
			defaultConfig.write('[subversion]\n')
			defaultConfig.write('repository : <repository url>\n')
			defaultConfig.write('user       : <username>\n')
			defaultConfig.write('password   : <password>\n')
			defaultConfig.write('[buildpaths]\n')
			defaultConfig.write('<platform> : <directory containing build directories>')
			defaultConfig.close()
			print 'Default configuration written as: ' + defaultConfig.name
		except IOError, e:
			print 'Failed to write default configuration: ' + str(e)

		sys.exit()

	def getValue(self, category, attribute):
		return self.get(category, attribute)

	def getItems(self, category):
		return self.items(category)

class SubversionClient():
	def __init__(self):
		self.client = pysvn.Client()
		self.client.callback_get_login = self.get_login
		self.svnRepository = str(config.getValue('subversion', 'repository'))

	# callback needed for the subversion client
	def get_login( realm, username, may_save ):
		"""callback implementation for Subversion login"""
		return True, config.getValue('subversion', 'user'), config.getValue('subversion', 'password'), True

	def getBranchList(self):
		branchList = []
		strippedBranchList = []

		# find branch names (returns a list of tuples -> (url, created_revision))
		try:
			branchList = self.client.list(self.svnRepository + '/branches', depth=pysvn.depth.immediates)
			del branchList[0] # The first item is '/branches'

			for branch in branchList:
				strippedBranchList.append(os.path.basename(branch[0].repos_path))
				logger.debug('Found branch: ' +  os.path.basename(branch[0].repos_path) + ' created at revision ' + str(branch[0].created_rev.number))
		except pysvn.ClientError, e:
			log.warning('Failed to get the branchlist: ' + str(e))

		return strippedBranchList

	#svn propget svn:mergeinfo $trunk | cut -d'/' -f3 | cut -d':' -f1
	def getIntegratedBranchList(self):
		branchList = []
		integratedBranchList = []

		try:
			# retuns dict with keys of url/path and values of the property
			branchList = self.client.propget('svn:mergeinfo', self.svnRepository + '/trunk/', depth=pysvn.depth.empty)

			for url,branches in branchList.iteritems():
				# branches is a string of branchnames followed by the revisions
				lines = branches.split('\n')
				# now split each line (/branches/<branchname>:<merged revisions>) to retrieve only the branchnames
				regex = re.compile('/branches/([^:]+).*')
				for branch in (regex.split(line) for line in lines[:]):
					integratedBranchList.append(branch[1])

		except pysvn.ClientError, e:
			log.warning('Failed to get the integrated branchlist: ' + str(e))

		return integratedBranchList 

##################################################################################
def main():
	#stacktracer.trace_start("trace.html",interval=5,auto=True)
	global config
	config = Config()

	# setup logging for both console and file
	numeric_level = getattr(logging, str(config.getValue('general', 'loglevel')).upper(), None)
	if not isinstance(numeric_level, int):
		    raise ValueError('Invalid log level: %s' % config.getValue('general', 'loglevel'))

	global logger
	logger = logging.getLogger('logger')
	logger.setLevel(logging.DEBUG)

	# create console handler and set level to debug
	ch = logging.StreamHandler()
	ch.setLevel(numeric_level)
	formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')#, datefmt= '%d-%m-%Y %H:%M:%S')
	ch.setFormatter(formatter)
	logger.addHandler(ch)

	logger.debug('starting...')

	global subversionClient
	subversionClient = SubversionClient()

	logger.info('#############################################')

	# 1. Get a list of branches found on the server
	branchList = subversionClient.getBranchList()

	logger.debug('#############################################')
	# 2. Remove the integrated branches from the branchList to get a list of branches which will get commits and will be build
	# The branchList now contains branches that have a builddirectory (actively committed to), and branches that don't (old
	# unused branches that are not integrated yet)
	logger.debug('Branches already integrated: ')

	integratedBranchList = subversionClient.getIntegratedBranchList()

	if integratedBranchList:
		for branch in integratedBranchList:
			try:
				branchList.remove(branch)
				logger.debug('Branch ' + branch + ' still exists in the repository, but is integrated')
			except ValueError:
				pass

	# 3. Retreive a list of builddirectories per platform
	for platform, path in config.getItems('buildpaths'):
		absolutePath = os.path.normpath(os.path.expandvars(str(path) + '/'))
		logger.info('#############################################')
		logger.info('Found path: ' + platform + ' ' + absolutePath)
		builddirList = os.listdir(absolutePath)
		
		# 4. Remove branches from the builddirlist that have a corresponding branch on the repository
		# If a branch does not have a builddirectory it is probably not active / old; report those.
		logger.info('#############################################')
		logger.info('Branches without builddirectory: ')
		for branch in branchList:
			builddirname = branch + '-' + platform
			try:
				builddirList.remove(builddirname)
			except:
				logger.info(platform + ': ' + builddirname)

		logger.info('#############################################')
		
		# 5. Remove builddirectories we definately want to keep; report if missing.
		# Trunk
		try:
			builddirList.remove('trunk-' + platform)
		except:
			logger.debug(platform + ': no builddirectory exists for trunk-' + platform)

		# The checkout area
		try:
			builddirList.remove('build')
		except:
			logger.debug(platform + ': no checkoutdirectory exists')

		# 6. Remove the build directories for which no branch exists on the repository,
		# or if the branch has already been integrated (see step 2).
		logger.info('Builddirectories without branch: ')
		for builddir in builddirList[:]:
			try:
				logger.info(platform + ': removing build directory: ' + absolutePath + '/' + builddir)
				shutil.rmtree(absolutePath + '/' + builddir)
			except OSError, e:
				logger.warning(platform + ': failed to remove build directory: ' + absolutePath + '/' + builddir + ' :' + str(e))

	logger.info('#############################################')
	logger.debug('done.')
	#stacktracer.trace_stop()

##################################################################################
if __name__ == '__main__':
	main()
