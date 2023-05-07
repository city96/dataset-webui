import os
from PIL import Image as pImage
from tqdm import tqdm
from queue import Queue
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
	def __init__(self, extension, resolution, overwrite=False, use_weights=False, n_threads=None):
		Thread.__init__(self)
		self.extension = extension
		self.resolution = resolution
		self.use_weights = use_weights
		self.n_threads = n_threads
		self.images = self.get_images(overwrite, extension)
		self.tqdm = tqdm(total=len(self.images),unit="img")

	def get_images(self, overwrite, extension):
		images = []
		folders = []
		for img in get_step_images(step_list[2],step_list[4]):
			img.dst_path = img.get_step_path(5,self.extension)
			if os.path.isfile(img.dst_path) and not overwrite:
				continue
			cat = os.path.split(img.dst_path)[0]
			if cat and cat not in folders and not os.path.isdir(cat):
				os.mkdir(cat)
				folders.append(cat)
			images.append(img)
		return images

	def scale_image_queue(self):
		while not self.queue.empty():
			img = self.queue.get()
			scale(src=img.path, dst=img.dst_path, width=self.resolution, height=self.resolution)
			write_tag_txt(img.tags,img.dst_path,self.use_weights)
			self.queue.task_done()
			self.tqdm.update()

	def run(self):
		if len(self.images) == 0:
			self.tqdm.close()
			return
		if self.n_threads and self.n_threads > 1 and len(self.images) > 25:
			self.queue = Queue()
			[self.queue.put(i) for i in self.images]
			[Thread(target=self.scale_image_queue, daemon=True).start() for _ in range(self.n_threads)]
			self.queue.join()
		else:
			if len(self.images) > 1000: tqdm.write("Consider using '--threads 4' in your launch args!")
			for img in self.images:
				scale(src=img.path, dst=img.dst_path, width=self.resolution, height=self.resolution)
				write_tag_txt(img.tags,img.dst_path,self.use_weights)
				self.tqdm.update()
		self.tqdm.close()
		return

	def get_status(self):
		data = {
			"run": self.is_alive(),
			"max": self.tqdm.total,
			"current": self.tqdm.n,
		}
		return data
