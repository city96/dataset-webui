#!/usr/bin/python3
# script to save/load dataset folders
import os
import configparser
from common import verify_input
from check import get_step_info

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
		# load path from ini?
		exit(1)

	# check if all empty, reuse status (regex?)
	for folder in folder_list:
		old_path = os.path.join(dataset.save_path,folder)
		os.rename(folder,old_path)
	os.rename("dataset.ini",os.path.join(dataset.save_path,"dataset.ini"))
	print(f"Saved '{dataset.name}' dataset to {dataset.save_path}")

# check if there is an active dataset and load existing one if possible
def load_dataset(dataset):
	#shouldn't happen, sanity check
	if not os.path.isdir(dataset.save_path):
		exit(1)
	# sanity check, don't collide
	if any([os.path.isdir(x) for x in folder_list]) or os.path.isfile("dataset.ini"):
		print("target folder not empty!")
		exit(1)

	for folder in folder_list:
		new_path = os.path.join(dataset.save_path,folder)
		os.rename(new_path,folder)
	os.rename(os.path.join(dataset.save_path,"dataset.ini"),"dataset.ini")
	print(f"Loaded '{dataset.name}' dataset into active folder")

# initialize new dataset, copy sample ini, get name from user
def create_dataset():
	# sanity check, don't collide
	if any([os.path.isdir(x) for x in folder_list]) or os.path.isfile("dataset.ini"):
		print("target folder not empty!")
		exit(1)
	d = Dataset()
	d.name = input("Dataset name: ") # todo verify input
	d.description = input("Dataset description [optional]: ").strip()
	# folders
	for folder in folder_list:
		if os.path.isdir(folder):
			print("a")
		else:
			os.mkdir(folder)
			
	#copy from sample config properly
	with open("other/dataset-template.ini") as src:
		with open("dataset.ini","w") as dst:
			for line in src:
				if line == "Name = \n":
					line = f"Name = {d.name}\n"
				if line == "Description = \n":
					line = f"Description = {d.description}\n"
				dst.write(line)

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
	# ini load
	ini_path = os.path.join(path,'dataset.ini')
	if not os.path.isfile(ini_path):
		# print(f"no dataset ini file! {path}")
		return
	else:
		config = configparser.ConfigParser()
		config.read(ini_path)
		d.name = config["DatasetInfo"]["Name"].strip()
		d.description = config["DatasetInfo"]["Description"]
	if not d.name:
		print("Your dataset doesn't have a name! edit 'dataset.ini' before saving.")
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
def api_json_dataset(command):
	data = {}
	if command == "get_all":
		datasets = get_all_saved_datasets()
		d = get_dataset("./")
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
	return data

# default CLI ui with checks
def cli_ui():
	print("Dataset Manager")
	current = get_dataset("./")
	if current:
		if verify_input(f"\nActive dataset '{current.name}' found. Move to dataset folder? [y/N] ",'y','n',False):
			save_dataset(current)
		else:
			print("No changes were made. Exiting...")
			exit()
	
	if verify_input(f"\nCreate New or Load existing dataset? [N/L] ",'n','l'):
		create_dataset();
	else:
		datasets = get_all_saved_datasets()
		if len(datasets) == 0:
			print("You don't have any saved datasets! Exiting...")
			exit()
		print("\nDatasets:")
		name_maxlen = max([len(x.name) for x in datasets])
		size_maxlen = max([len(str(x.size)) for x in datasets])
		for k in range(len(datasets)):
			print(f"{k+1} - {datasets[k].name.ljust(name_maxlen)} ( {str(datasets[k].size).rjust(size_maxlen)} images in {datasets[k].save_path} )")
		while True:
			i = input("Dataset to load [number]: ")
			try:
				k = int(i) - 1
				if k < 0: continue
				dataset = datasets[k]
			except:
				print(f"Invalid input '{i}'\n")
				continue
			break
		load_dataset(dataset)

if __name__ == "__main__":
	cli_ui()
