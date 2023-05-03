import os
from PIL import Image as pImage
from tqdm import tqdm
from threading import Thread

from .common import step_list
from .loader import get_step_images, str_to_tag_list
from .tags import write_tag_txt

def scale(src,dst,width=768, height=768):
	img = pImage.open(src)
	wpercent = (width/float(img.size[0]))
	hsize = int((float(img.size[1])*float(wpercent)))
	if hsize != height:
		# print("res mismatch", dst)
		hsize = height
	img = img.resize((width,hsize), pImage.ANTIALIAS)
	img.save(dst)

class OutputWriter(Thread):
	def __init__(self, extension, resolution, overwrite=False, use_weights=False):
		Thread.__init__(self)
		self.extension = extension
		self.resolution = resolution
		self.use_weights = use_weights
		images = get_step_images(step_list[2],step_list[4])
		if not overwrite:
			images = [x for x in images if not os.path.isfile(x.get_step_path(5,extension))]
		self.tqdm = tqdm(images,unit="img")
		
	def run(self):
		for img in self.tqdm:
			dst = img.get_step_path(5,self.extension)
			cat = os.path.split(dst)[0]
			if not os.path.isdir(cat):
				os.mkdir(cat)
			scale(src=img.path, dst=dst, width=self.resolution, height=self.resolution)

	def get_status(self):
		data = {
			"run": self.is_alive(),
			"max": self.tqdm.total,
			"current": self.tqdm.n,
		}
		return data
