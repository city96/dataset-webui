import os
import json
from .common import step_list
from .loader import get_step_images

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
	"""returns dict with status for all steps"""
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
