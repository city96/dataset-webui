#!/usr/bin/python3
import os
from PIL import Image as pImage
from common import step_list
from status import get_step_images, str_to_tag_list
from tags import write_tag_txt

def scale(src,dst,width=768, height=768):
	img = pImage.open(src)
	wpercent = (width/float(img.size[0]))
	hsize = int((float(img.size[1])*float(wpercent)))
	if hsize != height:
		print("res mismatch", dst)
		hsize = height
	img = img.resize((width,hsize), pImage.ANTIALIAS)
	img.save(dst)

def scale_folder(src_dir):
	for img in os.listdir(src_dir):
		src = os.path.join(src_dir,img)
		if os.path.isdir(src):
			for cat in os.listdir(src):
				sc = os.path.join(src,cat)
				if not os.path.isfile(sc):
					continue
				name, ext = os.path.splitext(cat)
				dst = os.path.join(os.path.join(step_list[5],img),name+".png")
				scale(sc,dst)
		else:
			name, ext = os.path.splitext(img)
			dst = os.path.join(step_list[5],name+".png")
			scale(src, dst)

def finalize_image(img, ext=".png", resolution=768, overwrite=False):
	src = img.path
	dst = img.get_step_path(5)
	cat = os.path.split(dst)[0]
	if not os.path.isdir(cat):
		os.mkdir(cat)

	if ext: dst = os.path.splitext(dst)[0] + ext

	write_tag_txt(img.tags,dst)
	if os.path.isfile(dst) and not overwrite:
		print(f"image '{img}' already copied")
		return
	else:
		print(f"processing '{img}'")
	scale(src,dst,width=resolution,height=resolution)

def finalize_output(): # for testing
	images = get_step_images(step_list[2],step_list[4])
	for i in images:
		finalize_image(i)

if __name__ == "__main__":
	finalize_output()
