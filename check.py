#!/usr/bin/python3
# Script to track progress
import os
import json
from fix_tags import str_to_taglist

def get_step_info(folder):
	data = {
		"img_count" : 0,
		"categories" : {},
		"tag_count" : {},
		"uncategorized" : None,
	}
	print(f"\nStep {folder}")
	if not os.path.isdir(folder):
		data["error"] = "folder for step '{folder}' doesn't exist"
		print(data["error"])
		return data

	data["uncategorized"] = sum([os.path.isfile(os.path.join(folder,x)) for x in os.listdir(folder)])
	tags = []

	for cat in os.listdir(folder):
		if os.path.isdir(os.path.join(folder,cat)):
			for k in os.listdir(os.path.join(folder,cat)):
				path = os.path.join(cat,k)
				ext = os.path.splitext(k)[1]
				if ext in [".png",".jpg"]: #img
					if cat not in data["categories"].keys():
						data["categories"][cat] = 1
					else:
						data["categories"][cat] += 1
				elif ext in [".txt"]: #tag
					if folder == "4 - fixed" or folder == "3 - tagged":
						with open(os.path.join(folder,path)) as f:
							raw = f.read()
						if raw:
							tags += str_to_taglist(raw)
							
						continue
				elif os.path.isdir(path): #dir
					data["warn"].append(f" Warning! {dirpath} is a category inside a category! it will be ignored")
					print(data["warn"][-1])
				else:
					data["warn"].append(f" Warning! Unknown extension '{ext}' for file {path}")
					print(data["warn"][-1])

	if data["categories"]:
		data["img_count"] += sum(data["categories"].values())
		print(f' Total categorized images: {data["img_count"]}')
		for cat, count in data["categories"].items():
			print(f"  {cat} ({count})")
	if data["uncategorized"]:
		data["img_count"] += data["uncategorized"]
		print(f' Total uncategorized images: {data["uncategorized"]}')
	if not data["categories"] and not data["uncategorized"]:
		data["error"] = f"folder for step '{folder}' doesn't have any images"
		print(data["error"])
		return data
	if len(tags)>0:
		data["tag_count"]["total"] = len(tags)
		print(f' Total tags: {data["tag_count"]["total"]}')
		if data["img_count"] > 0:
			data["tag_count"]["average"] = round(len(tags)/data["img_count"],2)
			print(f'  Avg tag per image: {data["tag_count"]["average"]}')
		data["tag_count"]["unique"] = len(list(set([x.name for x in tags])))
		print(f'  Unique tags: {data["tag_count"]["unique"]}')
	return data

def api_json_status():
	folder_list = [
		"0 - raw",
		"1 - cropped",
		"2 - sorted",
		"3 - tagged",
		"4 - fixed",
		"5 - out",
	]

	data = {}
	for f in folder_list:
		data[f] = get_step_info(f)
	# return json.dumps(data)
	return data

if __name__ == "__main__":
	folder_list = [
		"0 - raw",
		"1 - cropped",
		"2 - sorted",
		"3 - tagged",
		"4 - fixed",
		"5 - out",
	]

	for f in folder_list:
		get_step_info(f)
	input("\nPress any key to exit...")
