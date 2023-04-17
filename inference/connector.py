import os
import json

from time import sleep
from io import BytesIO
from PIL import Image, ImageDraw
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
	print(f"autocrop {image_path} [{threshold},{min_size},{scale}]")
	boxes = get_image_regions(segment_image(image_path),threshold,min_size,scale)
	preview = img_to_base64(get_image_crop_preview(image_path,boxes),2)
	return boxes, preview

class Autocrop(Thread):
	def __init__(self, image_data, threshold, min_size, scale):
		Thread.__init__(self)
		image_data = [x for x in image_data if not (x.get("auto") and x.get("duplicate"))]
		self.image_data = image_data
		self.threshold = threshold
		self.min_size = min_size
		self.scale = scale
		self.lock = Lock()
		self.current = 0
		self.max = len(image_data)
		self.preview = None
	def run(self):
		new = []
		for i in range(len(self.image_data)):
			img = self.image_data[i]
			preview = None
			if img.get("auto") or img.get("status") == "raw":
				img_path = os.path.join(step_list[0],img.get("filename"))
				print(img_path)
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
				self.current = i+1
				self.preview = preview
		self.image_data = sorted(self.image_data+new, key=lambda x: x["filename"])
		sleep(0.5) # last img
		return
	def get_status(self):
		with self.lock:
			data = {
				"run": self.is_alive(),
				"max": self.max,
				"current": self.current,
				"preview": self.preview,
			}
		return data

def get_image_tags(image_path, threshold=0.35):
	rating = ["general", "sensitive", "questionable", "explicit"] # remove / filter these
	tags = label_image(image_path)
	tags = {name.replace("_"," "):conf for name, conf in tags.items() if conf >= threshold and name not in rating}
	return tags

class Autotagger(Thread):
	def __init__(self, images, overwrite, threshold):
		Thread.__init__(self)
		self.images = images
		self.overwrite = overwrite
		self.threshold = threshold
		self.lock = Lock()
		self.current = 0
		self.max = len(images)
		self.caption = None
		self.preview = None
	def run(self):
		if not os.path.isdir(step_list[3]):
			os.mkdir(step_list[3])

		for i in range(len(self.images)):
			img = self.images[i]
			print(f"Autotag: {img.path}")
			json_file = os.path.splitext(img.get_step_path(3))[0]+".json"
			if not os.path.isdir(os.path.split(json_file)[0]):
				os.mkdir(os.path.split(json_file)[0])

			if os.path.isfile(json_file) and not self.overwrite:
				with open(json_file) as f:
					data = json.load(f)
				caption = {"Empty caption":1.0} if "caption" not in data.keys() else data["caption"]
				caption["Already tagged"] = 1.0
				caption = dict(sorted(caption.items(), key=lambda item: item[1], reverse=True))
			else:
				caption = get_image_tags(img.path, self.threshold)
				caption = dict(sorted(caption.items(), key=lambda item: item[1], reverse=True))
				with open(json_file, "w") as f:
					f.write(json.dumps({"caption":caption}, indent=2))
			# print(f"\t{len(caption)} tags")
			with self.lock:
				self.current = i+1
				self.caption = caption
				self.preview = img_to_base64(Image.open(img.path),2)
		sleep(0.5) # last img
		return
	def get_status(self):
		with self.lock:
			data = {
				"run": self.is_alive(),
				"max": self.max,
				"current": self.current,
				"caption": self.caption,
				"preview": self.preview,
			}
		return data