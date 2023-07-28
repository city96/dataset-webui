import os
import json

from time import sleep
from io import BytesIO
from PIL import Image, ImageDraw
from tqdm import tqdm
from base64 import b64encode
from threading import Thread, Lock

from .labeling import label_image
from .segmentation import segment_image
from .region_detection import get_image_regions

from scripts.status import get_status
from scripts.common import step_list

def img_to_base64(img,scale=1):
	buffer = BytesIO()
	if scale > 1:
		img = img.resize((int(img.width/scale),int(img.height/scale)), Image.LANCZOS)
	img = img.convert('RGB')
	img.save(buffer, "jpeg")
	buffer.seek(0)
	encoded = b64encode(buffer.read()).decode('utf-8')
	return f"data:image/jpeg;base64,{encoded}"

def get_image_crop_preview(image_path,boxes):
	img = Image.open(image_path)
	draw = ImageDraw.Draw(img)
	for box in boxes:
		d = (box[0],box[2],box[1],box[3])
		draw.rectangle(d,outline="red",width=4)
	return img

def box_to_crop_data(box):
	size = min(box[1]-box[0],box[3]-box[2])
	data = {
		"x": box[0],
		"y": box[2],
		"width": size,
		"height": size,
		"rotate": 0,
		"scaleX": 1,
		"scaleY": 1
	}
	return data

def get_image_autocrop(image_path,threshold,min_size,scale):
	# print(f"autocrop {image_path} [{threshold},{min_size},{scale}]")
	boxes = get_image_regions(segment_image(image_path),threshold,min_size,scale)
	preview = get_image_crop_preview(image_path,boxes)
	return boxes, preview

class Autocrop(Thread):
	def __init__(self, image_data, threshold, min_size, scale):
		Thread.__init__(self)
		self.threshold = threshold
		self.min_size = min_size
		self.scale = scale
		self.lock = Lock()
		self.preview = None
		image_data = [x for x in image_data if not (x.get("auto") and x.get("duplicate"))]
		self.image_data = image_data
		target = [image_data.index(x) for x in image_data if x.get("auto") or x.get("status") == "raw"]
		self.tqdm = tqdm(target,unit="img")
	def run(self):
		new = []
		for i in self.tqdm:
			img = self.image_data[i]
			img_path = os.path.join(step_list[0],img.get("filename"))
			boxes, preview = get_image_autocrop(img_path, self.threshold, self.min_size, self.scale)
			if not boxes or len(boxes) == 0:
				continue
			self.image_data[i]["auto"] = True
			self.image_data[i]["crop_data"] = box_to_crop_data(boxes[0])
			if len(boxes) > 1:
				for b in boxes[1:]:
					n = dict(self.image_data[i])
					n["crop_data"] = box_to_crop_data(b)
					n["duplicate"] = True
					new.append(n)
			with self.lock:
				self.preview = img_to_base64(preview, 2)
		self.image_data = sorted(self.image_data+new, key=lambda x: x["filename"])
		sleep(0.5) # last img
		return
	def get_status(self):
		with self.lock:
			data = {
				"run": self.is_alive(),
				"max": self.tqdm.total,
				"current": self.tqdm.n,
				"preview": self.preview,
			}
		return data

def get_image_tags(tagger, image_path, threshold=0.35):
	rating = ["general", "sensitive", "questionable", "explicit"] # remove / filter these
	tags = label_image(image_path, tagger)
	tags = {name.replace("_"," "):conf for name, conf in tags.items() if conf >= threshold and name not in rating}
	return tags

class Autotagger(Thread):
	def __init__(self, images, overwrite, threshold, taggers=None, multi_conf=None, multi_mode=None):
		Thread.__init__(self)
		self.overwrite = overwrite
		self.threshold = threshold
		self.multi_conf = multi_conf
		self.multi_mode = multi_mode
		self.lock = Lock()
		self.caption = None
		self.preview = None
		for i in images: i.txt = os.path.splitext(i.get_step_path(3))[0]+".json"
		if not overwrite:
			images = [x for x in images if not os.path.isfile(x.txt)]

		image_runs = []
		taggers = ["wd-v1-4-vit-tagger-v2"] if not taggers else taggers # fallback
		for t in taggers:
			image_runs += [(t,i) for i in images]
		self.tqdm = tqdm(image_runs, unit="img")

	def run(self):
		if not os.path.isdir(step_list[3]):
			os.mkdir(step_list[3])

		captions = {}
		json_path_list = []
		for tagger, img in self.tqdm:
			json_file = os.path.splitext(img.get_step_path(3))[0]+".json"
			json_path = os.path.split(json_file)[0]
			if json_path not in json_path_list: # don't recheck each time
				if not os.path.isdir(json_path):
					os.mkdir(json_path)
				json_path_list.append(json_path)

			if os.path.isfile(json_file) and not self.overwrite:
				with open(json_file) as f:
					data = json.load(f)
				caption = {"Empty caption":1.0} if "caption" not in data.keys() else data["caption"]
				caption["Already tagged"] = 1.0
				caption = dict(sorted(caption.items(), key=lambda item: item[1], reverse=True))
			else:
				caption = get_image_tags(tagger, img.path, 0.15) # low threshold here, filter later
				if json_file not in captions.keys():
					captions[json_file] = []
				captions[json_file].append(caption)

			with self.lock:
				self.caption = caption
				self.preview = img_to_base64(Image.open(img.path),2)

		# write output
		for json_file, caption in captions.items():
				if len(caption) == 1: # single tagger mode
					caption = caption[0]
				else: # multi tagger mode
					# intersect or union
					allowed_tags = []
					for c in caption:
						for i in c.keys():
							if i not in allowed_tags:
								allowed_tags.append(i)
					if self.multi_mode == "intersect":
						for k in allowed_tags:
							for c in caption:
								if k not in c.keys():
									allowed_tags.remove(k)
									break
					# sum captions
					out = {}
					for c in caption:
						for tag, conf in c.items():
							if tag not in allowed_tags:
								continue
							if tag not in out.keys():
								out[tag] = 0
							out[tag] += conf
					# max 1.0 or avg
					cl = len(caption)
					caption = {}
					for tag, conf in out.items():
						caption[tag] = conf/cl if self.multi_conf == "avg" else min(conf, 1.0)

				caption = {tag:conf for tag, conf in caption.items() if conf >= self.threshold}
				caption = dict(sorted(caption.items(), key=lambda item: item[1], reverse=True))
				with open(json_file, "w") as f:
					f.write(json.dumps({"caption":caption}, indent=2))

		sleep(1) # last img/return
		return

	def get_status(self):
		with self.lock:
			data = {
				"run": self.is_alive(),
				"max": self.tqdm.total,
				"current": self.tqdm.n,
				"caption": self.caption,
				"preview": self.preview,
			}
		return data