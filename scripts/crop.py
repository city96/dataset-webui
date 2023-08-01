import os
import json
from PIL import Image as pImage
from tqdm import tqdm
from queue import Queue
from threading import Thread

from .common import Image, Tag, step_list
from .loader import load_dataset_json, get_step_images
from .category import mesh_image_list

# global list of warnings
warn = []

def crop_info():
	global warn
	warn = []

	data = load_dataset_json()
	if not data:
		data = {
			"crop" : {
				"warn" : ["No active dataset"]
			}
		}
		return data

	if "crop" not in data.keys():
		data["crop"] = {}
	if "images" not in data["crop"].keys():
		data["crop"]["images"] = []
	if "missing" not in data["crop"].keys():
		data["crop"]["missing"] = []
	if "current" not in data["crop"].keys():
		data["crop"]["current"] = 0
	if "disk" not in data["crop"].keys():
		data["crop"]["disk"] = []

	data = { # filter extra data
		"crop" : data["crop"]
	}

	images = []
	missing = []

	disk = get_step_images(step_list[1])
	
	images, missing = mesh_image_list(data["crop"], get_step_images(step_list[0]))
	
	data["crop"]["disk"] = []
	for i in disk: # also list output images [on disk]
		data["crop"]["disk"].append(i.get_id())

	nrm = [] # normalize values / remove useless keys
	for i in images:
		n = {}
		n["filename"] = i["filename"]

		if "crop_data" in i.keys():
			n["status"] = "auto" if i.get("auto") else "crop"
			n["crop_data"] = i["crop_data"]
		else:
			n["status"] = "raw"

		if "ignored" in i.keys():
			n["ignored"] = i["ignored"]
			if i["ignored"]:
				n["status"] = "ignored"
		
		if i["filename"] in data["crop"]["disk"]:
			n["on_disk"] = True
		else:
			n["on_disk"] = False
		
		if "duplicate" in i.keys():
			n["duplicate"] = i["duplicate"]

		nrm.append(n)
	images = nrm

	# find missing
	disk_only = list(set(data["crop"]["disk"]) - set([x["filename"] if "crop_data" in x.keys() else None for x in images]))
	if len(disk_only) > 0:
		warn.append(f"you have {len(disk_only)} image(s) that were cropped externally.")

	if data["crop"]["current"] > len(images):
		data["crop"]["current"] = 0
	data["crop"]["images"] = sorted(images, key=lambda x: x["filename"])
	data["crop"]["missing"] = missing
	data["crop"]["warn"] = warn
	return data

def crop_image(data):
	crop = data["crop_data"]
	left = crop["x"]
	top = crop["y"]
	right = crop["x"]+crop["width"]
	bottom = crop["y"]+crop["height"]
	img = pImage.open(data["src_path"])
	img = img.crop((left, top, right, bottom))
	img.save(data["dst_path"])

class CropWriter(Thread):
	def __init__(self, n_threads=None):
		Thread.__init__(self)
		self.n_threads = n_threads
		overwrite = False # toggle?
		self.images = self.get_images(overwrite)
		self.tqdm = tqdm(total=len(self.images),unit="img")

	def get_images(self, overwrite):
		data = load_dataset_json()
		if not data.get("crop") or not data["crop"].get("images"):
			return []
		images = []
		history = []
		folders = []
		valid = [x.get_id() for x in get_step_images(step_list[0])]
		for i in data["crop"]["images"]:
			# check ignore/no data
			if i.get("ignored") or not i.get("crop_data"): 
				continue
			# check valid
			filename = i.get("filename")
			if filename not in valid:
				continue
			# check exists - old
			src_path = os.path.join(step_list[0],filename)
			if not os.path.isfile(src_path):
				print(f"missing {src_path}")
			# handle duplicates
			if filename in history:
				path, ext = os.path.splitext(filename)
				n = history.count(filename) + 1
				dst_path = os.path.join(step_list[1], f"{path}_{n}{ext}")
			else:
				dst_path = os.path.join(step_list[1], filename)
			history.append(filename)
			# check exists - new
			if os.path.isfile(dst_path) and not overwrite:
				# print(f"already exists {dst_path}")
				continue
			# handle folder
			cat = os.path.split(dst_path)[0]
			if cat and cat not in folders and not os.path.isdir(cat):
				os.mkdir(cat)
				folders.append(cat)
			i["dst_path"] = dst_path
			i["src_path"] = src_path
			images.append(i)
		return images

	def crop_image_queue(self):
		while not self.queue.empty():
			img = self.queue.get()
			crop_image(img)
			self.queue.task_done()
			self.tqdm.update()

	def run(self):
		if len(self.images) == 0:
			self.tqdm.close()
			return
		if self.n_threads and self.n_threads > 1 and len(self.images) > 25:
			self.queue = Queue()
			[self.queue.put(i) for i in self.images]
			[Thread(target=self.crop_image_queue, daemon=True).start() for _ in range(self.n_threads)]
			self.queue.join()
		else:
			if len(self.images) > 1000: tqdm.write("Consider using '--threads 4' in your launch args!")
			for img in self.images:
				crop_image(img)
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
