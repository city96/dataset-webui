#!/usr/bin/python3
# scale images - helper script, needs fixing
# problems: 
#  - no readout on what images will be copied
#  - aspect ratio is ignored, only works on pre-scaled images
#  - modified StackOverflow answer
import os
from PIL import Image

# if input("warning! Edit python file before running. run? [y/N] ").lower() != 'y':
	# exit()

src_dir = "../2 - sorted"
dst_dir = "../3 - tagged"
width = 768
height = 768

def scale(src,dst):
	d = os.path.split(dst)[0]
	if not os.path.isdir(d):
		os.mkdir(d)
	img = Image.open(src)
	wpercent = (width/float(img.size[0]))
	hsize = int((float(img.size[1])*float(wpercent)))
	if hsize != height:
		print("mismatch", dst)
	img = img.resize((width,hsize), Image.ANTIALIAS)
	img.save(dst)

for img in os.listdir(src_dir):
	src = os.path.join(src_dir,img)
	if os.path.isdir(src):
		for cat in os.listdir(src):
			sc = os.path.join(src,cat)
			if not os.path.isfile(sc):
				continue
			name, ext = os.path.splitext(cat)
			dst = os.path.join(os.path.join(dst_dir,img),name+".png")
			scale(sc,dst)
	else:
		name, ext = os.path.splitext(img)
		dst = os.path.join(dst_dir,name+".png")
		scale(src, dst)