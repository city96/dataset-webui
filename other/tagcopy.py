#!/usr/bin/python3
# copy tags from a source category to multiple target ones, useful if you're doing multiple frames of the same animation
# problems:
#  - ported over from other project
#  - hard-coded directory names
#  - no overwrite support

import os

if input("warning! Edit python file before running. run? [y/N] ").lower() != 'y':
	exit()

basedir = "../2 - cropped"
basecat = "1_f1"
targetcat = ["1_f2","1_f3","1_f4"]

# ow = input("overwrite all? [y/N]").lower() == 'y'
ow = False

bd = os.path.join(basedir,basecat)
bddb = {}
for i in os.listdir(bd):
	name, ext = os.path.splitext(i)
	if ext == ".txt":
		a = os.path.join(basedir,os.path.join(basecat,i))
		with open(a) as f:
			bddb[name] = f.read()

for k in targetcat:
	k = os.path.join(basedir,k)
	for i in os.listdir(k):
		name, ext = os.path.splitext(i)
		if ext == ".png":
			p = os.path.join(k,name+".txt")
			if name in bddb.keys():
				if not os.path.isfile(p):
					with open(p,"w") as f:
						f.write(bddb[name])