#!/usr/bin/env python

from blessings import Terminal
import fileinput
import re
import time

# This script will add color to the output of Ninja doing a GCC compilation 
# It will take input on stdin or use a file if supplied.

term = Terminal()
errorline = re.compile('(: error:)');
warningline = re.compile('(: warning:)');
buildline = re.compile('^\[\d+/\d+\]');
brokeOn = ""

for line in fileinput.input():
	line = line.decode('utf-8')
	lineList = errorline.split(line)
	if len(lineList) > 1:
		print lineList[0] + term.bold + term.red + lineList[1] + term.normal + lineList[2],
		brokeOn = line
	else:
		lineList = warningline.split(line)
		if len(warningline.split(line)) > 1:
			print lineList[0] + term.bold + term.yellow + lineList[1] + term.normal + lineList[2],
		else:
			if buildline.match(line):
				print term.move_up + line,
				#time.sleep(0.1) 
			else:
				print line,

print "\nYour build broke on the following:\n" + term.bold + brokeOn + term.normal
