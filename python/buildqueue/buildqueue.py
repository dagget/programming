#!/usr/bin/env python

import os
import getopt
import sys
import time
import thread
import pysvn

verbose = False

##################################################################################
class Build:
	def __init__(self, path, revision):
		self.path = path
		self.revision = revision

##################################################################################
def addSubversionBuilds(svnRepository, svnUser, svnPassword):
	if(verbose):
		print 'Using Subversion repository: ' + svnRepository
		print 'Using Subversion user      : ' + svnUser
		print 'Using Subversion password  : ' + svnPassword
	
	client = pysvn.Client()
	client.list(svnRepository + '/branches', depth=pysvn.depth.immediates)

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

	addSubversionBuilds(svnRepository, svnUser, svnPassword)

##################################################################################
if __name__ == '__main__':
	if(len(sys.argv[1:]) < 3):
		usage()
	main()
