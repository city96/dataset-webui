#!/usr/bin/python3
# scale images - helper script, needs fixing
# problems: 
#  - no readout on what images will be copied
#  - aspect ratio is ignored, only works on pre-scaled images
#  - modified StackOverflow answer
import os
from PIL import Image

if input("warning! Edit python file before running. run? [y/N] ").lower() != 'y':
	exit()

src_dir = "../1 - cropped"
dst_dir = "../2 - sorted"
width = 512
height = 512

for img in os.listdir(src_dir):
	name, ext = os.path.splitext(img)
	new = os.path.join(dst_dir,name+".png")
	if not os.path.isfile(new):
		# print(new)
		img = Image.open(os.path.join(src_dir,img))

		wpercent = (width/float(img.size[0]))
		hsize = int((float(img.size[1])*float(wpercent)))
		if hsize != height:
			print("mismatch", new)
		img = img.resize((width,hsize), Image.ANTIALIAS)
		img.save(new)