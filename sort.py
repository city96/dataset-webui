import os
import json
from category import get_sort_categories, get_sort_images
from common import step_list, Category
from status import get_step_images
warn = []

def sort_info():
	global warn
	warn = []
	if not os.path.isfile("dataset.json"):
		data = {
			"sort" : {
				"warn" : ["No images"]
			}
		}
		return data
	
	with open("dataset.json") as f:
		json_data = json.load(f)

	data = {}
	data["categories"] = {}
	folder = step_list[1]
	categories = get_sort_categories(folder,json_data)
	images, missing = get_sort_images(folder,json_data)
	data["images"] = images
	data["missing"] = missing

	disk_cat = [x.category.name if x.category else None for x in get_step_images(folder)]
	for c in categories:
		count = sum([x["category"] == c.name for x in images])
		disk = c.name in disk_cat
		if count == 0 and not c.keep and not disk:
			continue
		data["categories"][c.name] = {
			"color" : c.color,
			"count" : count,
		}

	if "default" not in data["categories"].keys():
		data["categories"]["default"] = {
			"name" : "default",
			"weight" : "1",
			"color" : "#555555",
			"count" : sum([x["category"] == "default" for x in images])
		}

	data["images"] = sorted(data["images"], key=lambda x: x["filename"])

	return {"sort": data}
