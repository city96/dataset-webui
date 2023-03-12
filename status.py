#!/usr/bin/python3
# Return current dataset status + info from json
import os
import json
from common import Image, Tag, Category, step_list

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
			t.position = i
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

def get_image_txt(path):
	"""returns txt file path or none for image path"""
	if os.path.isfile(path+".txt"):
		return (path+".txt")
	txt = os.path.splitext(path)[0] + ".txt"
	if os.path.isfile(txt):
		return txt
	else:
		return None

def get_folder_images(root_path, category):
	"""returns list of image objects from a folder, set category"""
	if not os.path.isdir(root_path):
		return
	images = []
	for filename in os.listdir(root_path):
		path = os.path.join(root_path,filename)
		ext = os.path.splitext(filename)[1]
		if ext in [".png",".jpg",".webp"]:
			image = Image()
			image.filename = filename
			image.path = path
			image.category = category
			image.txt = get_image_txt(path)
			if image.txt:
				image.tags = get_tags_from_file(image.txt)
			images.append(image)
		elif os.path.isdir(path):
			if not category:
				continue
			warn.append(f" Warning! {path} is a category inside a category! it will be ignored")
			print(warn[-1])
			continue
		elif ext in [".txt"]:
			continue
		else:
			warn.append(f" Warning! Unknown extension '{ext}' for file {path}")
			print(warn[-1])
			continue
	return images

def get_step_images(folder):
	"""returns list of image objects for a given step (folder name)"""
	images = []
	images += get_folder_images(folder,None) # uncategorized

	for category in os.listdir(folder):
		if os.path.isdir(os.path.join(folder,category)):
			try:
				weight, name = category.split("_",1)
				weight = int(weight)
				cat = Category(name,weight)
			except:
				cat = Category(category)
			images += get_folder_images(os.path.join(folder,category),cat)
	return images

def get_step_stats(folder):
	"""return stats about images/tags from folder name"""
	data = {
		"image_count" : {},
		"tag_count" : {},
	}
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
	return data