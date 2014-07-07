#!/usr/bin/env python

# This is a small script that checks for out of source builddirectories on a buildbot slave.
# If a builddirectory does not have a associated branch, then we remove it to save space.
# We also list branches that don't have builddirectories, as that is an indicator for unused
# branches.

import os
import shutil
import sys
import logging
import errno
import logging.handlers
import ConfigParser
import re
import datetime, time
from git import *

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
			self.get('git', 'repository')
		except ConfigParser.Error, e:
			print str(e)
			self.writeDefaultConfig()

	def writeDefaultConfig(self):
		try:
			defaultConfig = open(os.path.expanduser('~/buildbot-cleanup.examplecfg'), 'w')
			defaultConfig.write('[general]\n')
			defaultConfig.write('# loglevel may be one of: debug, info, warning, error, critical\n')
			defaultConfig.write('loglevel   : \n')
			defaultConfig.write('[git]\n')
			defaultConfig.write('repository : <repository url>\n')
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

class RepositoryError(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

class GitClient():
	def __init__(self, repository, path):
		if not os.path.exists(path):
			self.repo = Repo.clone_from(repository, path)
		else:
			try:
				self.repo = Repo(path)
			except GitCommandError, e:
				raise RepositoryError(str(e))

	def getBranchList(self):
		branchList = []
		g = Git(self.repo.git_dir)
		for head in g.ls_remote("--heads", "origin").split('\n'):
			headname = head.split('/')[2]
			#if head.name != 'origin/HEAD':
			#	branchList.append(head.name)
			branchList.append(headname)

		return branchList

	def removeInactiveBranches(self, branchlist):
		branchList = branchlist
		g = Git(self.repo.git_dir)
		for branch in branchList:
			commit = g.log("--since={`date --date=\"$(date +%Y-%m-15) -1 month\" \"+%Y-%m-01\"`}", "-n1", "--", "origin", branch)
			print commit

	def switch(self, release, path):
		if release == 'development':
			self.repo.git.checkout('master')
		else:
			for tagref in repo.tags:
				if tagref.name == release:
					self.repo.git.checkout(release)
				else:
					return False
		return True

	def update(self):
		try:
			self.repo.remotes.origin.pull()
		except GitCommandError, e:
			raise RepositoryError(str(e))

	def commit(self, message):
		if self.repo.is_dirty(True, True, True):
			try:
				self.repo.index.commit(message)
				self.repo.remotes.origin.push()
			except GitCommandError, e:
				raise RepositoryError(str(e))

	def forceCommit(self, message):
		if self.repo.is_dirty(True, True, True):
			try:
				self.repo.index.add("*")
				self.repo.index.commit(message)
			except GitCommandError, e:
				raise RepositoryError("Can not commit local changes in configrepo during startup" + str(e))

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

	logger.info('#############################################')

	for platform, path in config.getItems('buildpaths'):
		logger.debug('platform: ' + platform)
		global repo
		try:
			repo = GitClient(config.get('git', 'repository'), path)
		except RepositoryError, e:
			logger.error('could not connect to git remote: ' + e)
			sys.exit()

		# 1. Get a list of branches found on the server
		branchList = repo.getBranchList()

		logger.debug('#############################################')
		for branch in branchList:
			logger.debug('found branch: ' + branch)

	# 2. Remove the integrated branches from the branchList to get a list of branches which will get commits and will be build
	# The branchList now contains branches that have a builddirectory (actively committed to), and branches that don't (old
	# unused branches that are not integrated yet)

	# 3. Remove the inactive (last commit > 30 days ago) from the branchList to get a list of branches that are actively used
	# and will be build.
	# The branchList now contains branches that have a builddirectory (actively committed to)
	#repo.removeInactiveBranches(branchList)

	# 4. Retreive a list of builddirectories per platform
	for platform, path in config.getItems('buildpaths'):
		absolutePath = os.path.normpath(os.path.expandvars(str(path) + '/../'))
		logger.info('#############################################')
		logger.info('Found path: ' + platform + ' ' + absolutePath)
		builddirList = os.listdir(absolutePath)

		# 5. Remove branches from the builddirlist that have a corresponding branch on the repository
		# If a branch does not have a builddirectory it is probably not active / old; report those.
		logger.info('#############################################')
		logger.info('Branches without builddirectory: ')
		for branch in branchList:
			builddirname = branch
			try:
				builddirList.remove(builddirname)
			except:
				logger.info(platform + ': ' + builddirname)

		logger.info('#############################################')

		# 6. Remove builddirectories we definately want to keep; report if missing.
		# The checkout area
		try:
			builddirList.remove('build')
		except:
			logger.debug(platform + ': no checkoutdirectory exists')

		# 7. Remove the build directories for which no branch exists on the repository,
		# or if the branch has already been integrated (see step 2).
		# or if there hasn't been a commit in 30 days (see step 3).
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
