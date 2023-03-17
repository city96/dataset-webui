#!/usr/bin/python3
# script to save/load dataset folders
import os
import json
from common import verify_input
from common import step_list as folder_list
from status import get_step_stats

# global list of warnings
warn = []
dataset_folder = "datasets"

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

def save_dataset(dataset): 
	"""save current active dataset to the datasets folder"""
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

def load_dataset(dataset):
	"""check if there is an active dataset and load existing one if possible"""
	#shouldn't happen, sanity check
	if not os.path.isdir(dataset.save_path):
		warn.append(f"can't load dataset with invalid path {dataset.save_path}")
		print(warn[-1])
		return
	# sanity check, don't collide
	if any([os.path.isdir(x) for x in folder_list]) or os.path.isfile("dataset.json"):
		warn.append(f"target folder not empty!")
		print(warn[-1])
		return

	for folder in folder_list:
		new_path = os.path.join(dataset.save_path,folder)
		os.rename(new_path,folder)
	os.rename(os.path.join(dataset.save_path,"dataset.json"),"dataset.json")
	
	# remove old directory
	if len(os.listdir(dataset.save_path)) == 0:
		os.rmdir(dataset.save_path)
	
	print(f"Loaded '{dataset.name}' dataset into active folder")

def create_dataset(data):
	"""initialize new dataset from json"""
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

def get_all_datasets():
	"""return list of all saved dataset objects"""
	if not os.path.isdir(dataset_folder):
		return []
	datasets = []
	for name in os.listdir(dataset_folder):
		path = os.path.join(dataset_folder,name)
		if os.path.isdir(path):
			dataset = get_folder_dataset(path)
			if dataset:
				datasets.append(dataset)
	return datasets

def get_folder_dataset(path):
	"""get dataset object from folder"""
	dataset = Dataset()
	if path.startswith(dataset_folder):
		dataset.save_path = path
	# json load
	json_path = os.path.join(path,'dataset.json')
	if not os.path.isfile(json_path):
		if path != "./" and len(os.listdir(path)) > 0:
			warn.append(f"dataset in {path} has no json")
			print(warn[-1])
		return

	with open(json_path) as f:
		config = json.load(f)
	dataset.name = config["meta"]["name"].strip()
	dataset.description = config["meta"]["description"]

	if not dataset.name:
		warn.append(f"dataset in {path} has no name/empty json")
		print(warn[-1])
		dataset.name = "Untitled"
		# return

	# progress aware folder count
	for step in reversed(folder_list):
		step = os.path.join(path,step)
		size = get_step_stats(step)["image_count"]["total"]
		if size > 0:
			dataset.size = size
			break
	return dataset

def dataset_status(command=None,path=None):
	"""return info about active and saved datasets"""
	warn = [] # reset warnings
	data = {}
	data["datasets"] = []
	active = get_folder_dataset("./")
	if active:
		data["datasets"].append({
			"name": active.name,
			"description": active.description,
			"save_path": "./",
			"image_count": active.size,
			"active": True
		})
	for dataset in get_all_datasets():
		data["datasets"].append({
			"name": dataset.name,
			"description": dataset.description,
			"save_path": dataset.save_path,
			"image_count": dataset.size,
			"active": False
		})
	data["warn"] = warn
	return data