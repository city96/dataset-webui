#!/usr/bin/python3
# individual image tag override management
import os
import json
import random
from common import step_list, rating_list, load_dataset_json
from status import get_step_images, str_to_tag_list
from tags import tag_fix

def imgtag_all_tags(general_only=True):
	tags = []
	if os.path.isfile(os.path.join("external",'danbooru-tags.json')):
		with open(os.path.join("external",'danbooru-tags.json')) as f:
			raw_tags = json.load(f)
		for t in raw_tags:
			if general_only and t["category"] != 0:
				continue
			tags.append(t["name"].replace("_"," "))
	elif os.path.isfile(os.path.join("external",'gelbooru-tags.json')):
		with open(os.path.join("external",'gelbooru-tags.json')) as f:
			raw_tags = json.load(f)
		for t in raw_tags:
			if general_only and t["type"] != 0:
				continue
			tags.append(t["name"].replace("_"," "))
	else:
		tags = ["no *booru.json tag file!"]
	return tags

def imgtag_info():
	valid = tag_fix(save=False, rules_only=True)
	
	json_data = load_dataset_json()
	if "tags" in json_data.keys() and "images" in json_data["tags"].keys():
		missing = json_data["tags"]["missing"] if "missing" in json_data["tags"].keys() else []
		images = json_data["tags"]["images"] + missing
		if not valid:
			return {"images" : [], "missing" : missing+images}
	else:
		images = []

	data = []
	for i in valid:
		filename = i.get_id()
		if filename in [x["filename"] for x in images]:
			data.append({
				"filename" : filename,
				"img_url" : "/img/" + i.path.replace(os.sep,'/'),
				"tags" : [x.name for x in sorted(i.tags)],
				"add" : [x["add"] for x in images if x["filename"] == filename][0],
				"rem" : [x["rem"] for x in images if x["filename"] == filename][0],
			})
		else:
			data.append({
				"filename" : filename,
				"img_url" : "/img/" + i.path.replace(os.sep,'/'),
				"tags" : [x.name for x in sorted(i.tags)],
				"add" : [],
				"rem" : [],
			})
	
	missing = [x for x in images if x["filename"] not in [d["filename"] for d in data]]
	return {"images" : data, "missing" : missing}
