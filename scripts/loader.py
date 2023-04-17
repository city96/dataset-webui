import os
import json
from .common import Image, Tag, Category, step_list, rating_list, version

def load_dataset_json():
	"""load the current dataset json, apply fallback fixes [fast forward to current version]"""
	if not os.path.isfile("dataset.json"):
		return {}

	with open("dataset.json") as f:
		data = json.load(f)

	v = data["meta"]["version"] if "version" in data["meta"].keys() else 1.0

	# [1.0 => 1.1] - move tag rules under dict key
	if v == 1.0:
		if "tags" in data.keys():
			if len(data["tags"].keys()) > 0:
				rules = data["tags"]
				data["tags"] = {
					"rules" : rules,
					"images" : [],
				}
		v = 1.1

	# [dsv <=> current] - fallback failed
	if v != version:
		print("UNKNOWN DATASET VERSION // Fast Forward Failed!")
		return {}

	return data

def str_to_tag_list(string):
	"""comma separated string to tag list"""
	tags = []
	raw_tags = string.replace('\n', ',').split(",")
	raw_tags = [a.strip() for a in raw_tags]
	for i in range(len(raw_tags)):
		if raw_tags[i]:
			t = Tag()
			t.name = raw_tags[i]
			if ':' in t.name and t.name.startswith('(') and t.name.endswith(')'):
				try:
					name,weight = t.name.rsplit(':',1)
					t.weight = float(weight.rstrip(')'))
					t.name = name.lstrip('(')
				except: # reset
					t.weight = 1.0
					t.name = raw_tags[i]
					print(f"failed to parse {t.name}")
			t.position = i+5
			tags.append(t)
	return tags

def get_tags_from_file(path):
	"""reads tags from txt file, returns list of tags"""
	if not os.path.isfile(path):
		return None
	with open(path,'r') as f:
		raw = f.read()
	if not raw.strip():
		return None
	tags = str_to_tag_list(raw)
	return tags

def get_tags_from_json(path):
	"""reads tags from tagger json, returns list of tags"""
	tags = []
	with open(path) as f:
		data = json.load(f)
	if "caption" in data.keys():
		for name, confidence in data["caption"].items():
			t = Tag()
			t.name = name
			t.position = 20-(confidence*10)
			t.confidence = round(confidence,4)
			tags.append(t)
	return tags

def get_image_tags(path):
	"""returns txt file path and tags or none for image path"""
	tags = []
	# image.txt (webui tagger)
	file = os.path.splitext(path)[0] + ".txt"
	if os.path.isfile(file):
		tags = get_tags_from_file(file)
		return (file, tags)
	# image.json (builtin tagger)
	file = os.path.splitext(path)[0] + ".json"
	if os.path.isfile(file):
		tags = get_tags_from_json(file)
		return (file, tags)
	# image.png.txt (gallery-dl)
	file = path+".txt"
	if os.path.isfile(file):
		tags = get_tags_from_file(file)
		return (file, tags)
	# None
	return (None, [])

def get_image_rating(tags):
	"""split ratings from regular tags"""
	rating = {}
	new_tags = [x for x in tags if x.name not in rating_list]
	rating = {x.name : x.confidence for x in tags if x.name in rating_list}
	return (rating, new_tags)

def get_folder_images(root_path, category, tag_folder=None):
	"""returns list of image objects from a folder, set category"""
	if not os.path.isdir(root_path):	
		return
	images = []
	for filename in os.listdir(root_path):
		path = os.path.join(root_path,filename)
		if '.orphaned' in path:
			continue
		ext = os.path.splitext(filename)[1]
		if ext in [".png",".jpg",".jpeg",".webp"]:
			image = Image()
			image.filename = filename
			image.path = path
			image.category = category
			tag_path = os.path.join(tag_folder,filename) if tag_folder else path
			image.txt, image.tags = get_image_tags(tag_path)
			image.rating, image.tags = get_image_rating(image.tags)
			if tag_folder and image.tags or not tag_folder:
				images.append(image)
		elif os.path.isdir(path):
			if not category:
				continue
			warn.append(f" Warning! {path} is a category inside a category! it will be ignored")
			print(warn[-1])
			continue
		elif ext in [".txt",".json"]:
			continue
		else:
			warn.append(f" Warning! Unknown extension '{ext}' for file {path}")
			print(warn[-1])
			continue
	return images

def get_step_images(folder,tag_folder=None):
	"""returns list of image objects for a given step (folder name)"""
	images = []
	images += get_folder_images(folder,None,tag_folder) # uncategorized

	for category in os.listdir(folder):
		if os.path.isdir(os.path.join(folder,category)):
			try:
				weight, name = category.split("_",1)
				weight = int(weight)
				cat = Category(name,weight)
			except:
				cat = Category(category)
			tag_path = os.path.join(tag_folder,category) if tag_folder else None
			images += get_folder_images(os.path.join(folder,category),cat,tag_path)
	return images
