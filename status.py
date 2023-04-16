#!/usr/bin/python3
# Return current dataset status + info from json
import os
import json
from common import Image, Tag, Category, step_list, rating_list

# global list of warnings
warn = []

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
					name,weight = t.rsplit(':',1)
					t.weight = float(weight.rstrip(')'))
					t.name = name.lstrip('(')
				except: # reset
					t.weight = 1.0
					t.name = raw_tags[i]
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

def get_step_stats(folder):
	"""return stats about images/tags from folder name"""
	data = {
		"image_count" : {},
		"tag_count" : {},
	}
	if folder in step_list[3:5]:
		images = get_step_images(step_list[2],folder)
	else:
		images = get_step_images(folder)
	data["image_count"]["total"] = len(images)
	data["image_count"]["uncategorized"] = sum([x.category == None for x in images])
	tags = []
	for i in images:
		tags += [x.name for x in i.tags]
	data["tag_count"]["total"] = sum([len(x.tags) for x in images])
	data["tag_count"]["unique"] = len(set(tags))
	return data

def get_status():
	"""returns dict with status merged into dataset.json"""
	warn = [] # reset warnings
	if not os.path.isfile("dataset.json"):
		data = {
			"status" : {
				"steps" : [],
				"active" : False,
				"warn": ["No active dataset"],
			}
		}
		return data

	# with open("dataset.json") as f:
		# data = json.load(f)
		# data["status"] = {}

	data = {}
	data["status"] = {}
	data["status"]["steps"] = {}
	for folder in step_list:
		if not os.path.isdir(folder):
			warn.append(f"folder for step {folder} missing!")
		data["status"]["steps"][folder] = get_step_stats(folder)

	data["status"]["warn"] = warn
	data["status"]["active"] = True
	return data

if __name__ == "__main__":
	print(json.dumps(get_status(),indent=2))
	# json.dumps(get_status(),indent=2)
