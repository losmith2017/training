import os
import sys
import subprocess
import glob

files = glob.glob("/export/builds/release*")
p = subprocess.Popen(["find"] + files + ["-type", "d"], stdout=subprocess.PIPE)

list = p.communicate()[0].split()

list.sort()

npd = dict()
for l in list:
	r, d, b = l.split('_')
	print r, d, b
	dkey = r + "_" + d
	npd[dkey] = b

donotremove = []
for ddd in npd:
	donotremove.append(ddd + "_" + npd[ddd])

print donotremove

for l in list:
	if not l in donotremove:
		print "rm -rf " + l
		subprocess.call(["rm", "-rf", l])


