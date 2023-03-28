import os
import json
import hashlib
from category import get_sort_categories, get_sort_images
from common import step_list, Category
from status import get_step_images
from shutil import copyfile
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
			"tags" : [x.name for x in c.tags],
			"count" : count,
		}

	if "default" not in data["categories"].keys():
		data["categories"]["default"] = {
			"name" : "default",
			"weight" : "1",
			"color" : "#555555",
			"tags" : [],
			"count" : sum([x["category"] == "default" for x in images])
		}

	data["images"] = sorted(data["images"], key=lambda x: x["filename"])

	return {"sort": data}

hash_db = {}
def build_hashdb(files,force=False):
	global hash_db
	if not hash_db or force: hash_db = {}
	h = 0
	print("Building hash list")
	for i in files:
		if i.path not in hash_db:
			hash_db[i.path] = hashlib.md5(open(i.path,'rb').read()).hexdigest()
			h += 1

	print(f" hashed {h} images")

def orphan(file, folder):
	# fname = file.lstrip( [x for x in step_list if file.startswith(x)][0] ).lstrip(os.sep)
	fname = hashlib.md5(open(file,'rb').read()).hexdigest()+os.path.splitext(file)[1]
	of = os.path.join(folder,".orphaned")
	if not os.path.isdir(of):
		os.mkdir(of)
	new = os.path.join(of,fname)
	# np = os.path.split(new)[0]
	# if not os.path.isdir(np):
		# os.mkdir(np)
	
	if os.path.isfile(new):
		# h1 = hashlib.md5(open(file,'rb').read()).hexdigest()
		# h2 = hashlib.md5(open(new,'rb').read()).hexdigest()
		# if h1 != h2 : # is this even possible?
			# print("Error: delete files in .orphaned folder")
			# return
		os.replace(file,new)
		return
	os.rename(file,new)

def check_orphans(files,source,target):
	global hash_db
	# if not hash_db: build_hashdb(get_step_images[folder])
	valid = [h for n,h in hash_db.items() if n.startswith(source)]
	for i in files:
		if hash_db[i.path] not in valid:
			print("Found orphaned file",i.path)
			orphan(i.path, target)

def get_new_names(files, json_data):
	new = []
	names = []
	orphans = (os.listdir())
	target = [h for n,h in hash_db.items() if n.startswith(step_list[2])]
	for i in json_data["sort"]["images"]:
		k = {}
		k["old_path"] = os.path.join(step_list[1],i["filename"])
		if not os.path.isfile(k["old_path"]):
			print("missing:",k["old_path"])
			continue
	
		hs = hash_db[k["old_path"]]
		hp = os.path.join(step_list[2],os.path.join(".orphaned",hs+os.path.splitext(i["filename"])[1]))
		if os.path.isfile(hp):
			k["source"] = hp
		elif hs in target:
			k["source"] = [n for n,h in hash_db.items() if h == hs and n.startswith(step_list[2])][0]
		else:
			k["source"] = None

		fname = os.path.split(i["filename"])[1]
		cat = [x for x in json_data["sort"]["categories"] if x["name"] == i["category"]][0]
		cname = f'{cat["weight"]}_{cat["name"]}'
		k["new_path"] = os.path.join(step_list[2],os.path.join(cname,fname))
		
		if k["new_path"] in names: # duplocate fix
			k["new_path"] = os.path.join(step_list[2],os.path.join(cname,cname+"_"+fname))
		names.append(k["new_path"])

		if k["source"] != k["new_path"]:
			new.append(k)
	return new

def sort_write():
	source = get_step_images(step_list[1])
	dest = get_step_images(step_list[2])
	build_hashdb((source + dest),force=True)
	check_orphans(dest,step_list[1],step_list[2])

	with open("dataset.json") as f:
		json_data = json.load(f)
	name_db = get_new_names(dest, json_data)
	print(json.dumps(name_db,indent=2))
	for i in name_db:
		path = os.path.split(i["new_path"])[0]
		if not os.path.isdir(path):
			os.mkdir(path)
		if i["source"]:
			if os.path.isfile(i["new_path"]):
				h1 = hashlib.md5(open(i["source"],'rb').read()).hexdigest()
				h2 = hashlib.md5(open(i["new_path"],'rb').read()).hexdigest()
				if h1 != h2 : # is this even possible?
					print("duplicate filename?",i["new_path"],i["source"])
					continue
				os.replace(i["source"],i["new_path"])
			else:
				os.rename(i["source"],i["new_path"])
		else:
			copyfile(i["old_path"],i["new_path"])
		
	#cleanup empty
	for f in os.listdir(step_list[2]):
		d = os.path.join(step_list[2],f)
		if os.path.isdir(d):
			if len(os.listdir(d)) == 0:
				os.rmdir(d)
