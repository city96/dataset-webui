import os
import json
from common import step_list, Category, load_dataset_json
from status import get_step_images, str_to_tag_list
warn = []

def get_original_filename(fname, folder):
	"""try to find the original filename"""
	# note: add check for global list to prevent filename conflicts being merged
	print(f"trying to find '{fname}' in '{folder}'")
	if os.path.isfile(os.path.join(folder,fname)):
		return fname # unchanged
	
	if os.sep in fname:
		listdir = list(set([x if os.path.isdir(os.path.join(folder,x)) else None for x in os.listdir(folder)]) - set([None]))
		cat, name = os.path.split(fname)
		cat_name = cat.split('_', 1)[1] if '_' in cat else cat
		for c in listdir: # same category search
			lcn = c.split('_', 1)[1] if '_' in c else c
			if (cat_name == lcn):
				npname = os.path.join(c,name)
				if os.path.isfile(os.path.join(folder,npname)):
					return npname
		
		for c in listdir: # blind category search
			npname = os.path.join(c,name)
			if os.path.isfile(os.path.join(folder,npname)):
				return npname
	
		if os.path.isfile(os.path.join(folder, name)): # base folder regression search
			return name
	
	print(f"can't match '{fname}' to original")
	return fname

def mesh_image_list(json_data,step_data):
	"""combine two data sources"""
	images = [] # images present in both
	missing = [] # json-only images

	for i in (json_data["images"] + json_data["missing"]):
		if i["filename"] in [x.get_id() for x in step_data]:
			images.append(i)
		else:
			missing.append(i)
	
	for i in step_data:
		if i.get_id() in [x["filename"] for x in (images + missing)]:
			continue
		images.append({
			"filename" : i.get_id(),
			"category" : i.category.name if i.category else "default",
		})
	return (images, missing)

def get_sort_images(path,data):
	"""parse group info from data on disk + json"""
	if "sort" not in data.keys():
		data["sort"] = {}

	data = data["sort"]
	for i in ["images","missing","categories"]:
		if i not in data.keys():
			data[i] = []

	images, missing = mesh_image_list(data, get_step_images(path))
	return(images, missing)

def get_sort_categories(path,data):
	"""get groups from both json file and disk, prioritize json"""
	categories = []

	if "sort" in data.keys() and "categories" in data["sort"].keys():
		for i in data["sort"]["categories"]:
			name = i["name"]
			weight = i["weight"]
			cat = Category(name,weight)
			cat.color = i["color"] if "color" in i.keys() and i["color"] else "#555555"
			cat.keep = i["keep"] if "keep" in i.keys() and i["keep"] else False
			cat.tags = str_to_tag_list(i["tags"]) if "tags" in i.keys() else []
			categories.append(cat)
	
	for i in get_step_images(path):
		if i.category:
			if i.category.name not in [x.name for x in categories]:
				i.category.color = "#555555"
				i.category.keep = False
				categories.append(i.category)
	
	return categories

def category_info(disk_only=False):
	global warn
	warn = []
	folder = step_list[2] if disk_only else step_list[1]

	json_data = load_dataset_json()
	if not json_data:
		data = {
			"sort" : {
				"warn" : ["No images"]
			}
		}
		return data

	data = {}
	data["categories"] = []
	categories = get_sort_categories(folder,json_data)
	images, missing = get_sort_images(folder,json_data)
	data["images"] = images
	data["missing"] = missing

	disk_cat = [x.category.name if x.category else None for x in get_step_images(folder)]
	for c in categories:
		count = sum([x["category"] == c.name for x in images])
		disk = c.name in disk_cat
		if disk_only and not disk:
			continue
		if count == 0 and not c.keep and not disk:
			continue
		data["categories"].append({
			"name" : c.name,
			"weight" : c.weight,
			"color" : c.color,
			"tags" : [x.name for x in c.tags],
			"keep" : c.keep,
			"disk" : disk,
			"count" : count,
		})

	if "default" not in [x["name"] for x in data["categories"]]:
		data["categories"].insert(0,{
			"name" : "default",
			"weight" : "1",
			"color" : "#555555",
			"tags" : [],
			"count" : sum([x["category"] == "default" for x in images])
		})

	if disk_only:
		for i in range(len(data["images"])):
			data["images"][i]["filename"] = get_original_filename(data["images"][i]["filename"],step_list[1])

	return {"sort": data}
