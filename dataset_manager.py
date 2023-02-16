#!/usr/bin/python3
# script to save/load dataset folders
import os
import json
from common import verify_input
from status import get_step_info

# core settings
dataset_folder = "datasets"
folder_list = [
	"0 - raw",
	"1 - cropped",
	"2 - sorted",
	"3 - tagged",
	"4 - fixed",
	"5 - out",
]

# store dataset
class Dataset:
	name = None
	description = None
	save_path = None
	size = 0

	def __str__(self):
		return f"{self.name} ({self.size})"
	def __repr__(self):
		return f"{self.name} ({self.size})"


# save current active dataset to the datasets folder
def save_dataset(dataset): 
	if not os.path.isdir(dataset_folder):
		os.mkdir(dataset_folder)
	if not dataset.save_path:
		# bootleg folder conflict resolver
		folder_name = dataset.name
		for i in range(2,100): 
			dataset.save_path = os.path.join(dataset_folder,folder_name)
			if not os.path.isdir(dataset.save_path):
				os.mkdir(dataset.save_path)
				break
			elif len(os.listdir(dataset.save_path)) == 0:
				break
			else:
				folder_name = f"{dataset.name}_{i}"
	else:
		# load path from json?
		exit(1)

	# check if all empty, reuse status (regex?)
	for folder in folder_list:
		old_path = os.path.join(dataset.save_path,folder)
		os.rename(folder,old_path)
	os.rename("dataset.json",os.path.join(dataset.save_path,"dataset.json"))
	print(f"Saved '{dataset.name}' dataset to {dataset.save_path}")

# check if there is an active dataset and load existing one if possible
def load_dataset(dataset):
	#shouldn't happen, sanity check
	if not os.path.isdir(dataset.save_path):
		exit(1)
	# sanity check, don't collide
	if any([os.path.isdir(x) for x in folder_list]) or os.path.isfile("dataset.json"):
		print("target folder not empty!")
		exit(1)

	for folder in folder_list:
		new_path = os.path.join(dataset.save_path,folder)
		os.rename(new_path,folder)
	os.rename(os.path.join(dataset.save_path,"dataset.json"),"dataset.json")
	print(f"Loaded '{dataset.name}' dataset into active folder")

# jsontialize new dataset, get name from user
def create_dataset(data):
	# sanity check, don't collide
	if any([os.path.isdir(x) for x in folder_list]) or os.path.isfile("dataset.json"):
		print("target folder not empty!")
		return
	d = Dataset()
	d.name = data["meta"]["name"].strip()
	d.description = data["meta"]["description"].strip()
	# folders
	for folder in folder_list:
		if os.path.isdir(folder):
			print("a")
		else:
			os.mkdir(folder)
	
	# dump whatever we received as json
	with open("dataset.json","w") as f:
		f.write(json.dumps(data, indent=2))
	print(f"created new dataset '{d.name}'!")

# return a list of saved datasets in dataset_folder
def get_all_saved_datasets():
	if not os.path.isdir(dataset_folder):
		return []
	datasets = []
	for k in os.listdir(dataset_folder):
		path = os.path.join(dataset_folder,k)
		if os.path.isdir(path):
			d = get_dataset(path)
			if d:
				datasets.append(d)
	return datasets

# get dataset info from folder
def get_dataset(path):
	d = Dataset()
	if path.startswith(dataset_folder):
		d.save_path = path
	# json load
	json_path = os.path.join(path,'dataset.json')
	if not os.path.isfile(json_path):
		# print(f"no dataset json file! {path}")
		return
	else:
		with open(json_path) as f:
			config = json.load(f)
		d.name = config["meta"]["name"].strip()
		d.description = config["meta"]["description"]
	if not d.name:
		print("Your dataset doesn't have a name! edit 'dataset.json' before saving.")
		exit(1)
	# progress aware folder count
	for k in reversed(folder_list):
		k = os.path.join(path,k)
		l = len(os.listdir(k))
		if l > 0:
			d.size = get_step_info(k)["img_count"]
			break

	# if d.size == 0:
		# print(f"Warning! '{d.name}' dataset is empty.")
		# return
	return d

# callable version
def api_json_dataset(command,path=None):
	data = {}
	if command == "info":
		datasets = get_all_saved_datasets()
		d = get_dataset("./")
		if d:
			data["active"] = {
				"name": d.name,
				"description": d.description,
				"save_path": "./",
				"img_count": d.size,
				"active": True
			}
		for d in datasets:
			data[d.save_path] = {
				"name": d.name,
				"description": d.description,
				"save_path": d.save_path,
				"img_count": d.size,
				"active": False
			}
	elif path and command == "save" and path == "./":
		print("save",path)
		dataset = get_dataset(path)
		save_dataset(dataset)
		data["status"] = "ok"
	elif path and command == "load" and os.path.isdir(path):
		print("load",path)
		dataset = get_dataset(path)
		load_dataset(dataset)
		data["status"] = "ok"
	else:
		print("invalid command:",command,path)
	return data