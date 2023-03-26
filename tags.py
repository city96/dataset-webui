#!/usr/bin/python3
# script to fix and filter tags using the rules in 'dataset.json'
import os
import json
import random
from common import step_list, rating_list
from status import get_step_images, str_to_tag_list

debug = False

# fix underscores in tags
def underscore_fix(images):
	fixed = 0
	for i in images:
		for t in i.tags:
			if "_" in t.name:
				t.name = t.name.replace("_"," ")
				fixed += 1
	if fixed > 0:
		status.append(f"tags with underscores found. Fixed {fixed} tags.")
		print(status[-1])
	return images

# filter images by tags
def image_filter(images, img_blacklist, img_filters):
	if not img_blacklist and not img_filters:
		return images
	status.append("\nFiltering input images.")
	print(status[-1])
	removed = []
	filtered = []
	for i in images:
		if any([t in [x.name for x in i.tags] for t in [x.name for x in img_blacklist]]):
			removed.append(i)
	for k in removed: images.remove(k)
	for i in images:
		for f in img_filters:
			if all([t in [x.name for x in i.tags] for t in [x.name for x in str_to_tag_list(f["target"])]]):
				filtered.append(i)
	for k in filtered: images.remove(k)

	status.append(f" removed {len(removed)} images from input [by tags]")
	print(status[-1])
	if debug: print("REM:",[x.filename for x in removed])
	status.append(f" removed {len(filtered)} images from input [by filter]")
	print(status[-1])
	if debug: print("REM:",[x.filename for x in filtered])
	status.append(f" Images: {len(images)}")
	print(status[-1])
	return images

# load a list of `limit` popular tags, remove tags that aren't in this list
def popular_only(images, tag_file, limit, general_only):
	if not limit or not os.path.isfile(tag_file):
		return images
	status.append("\nfiltering unpopular tags")
	print(status[-1])
	tags = []
	removed = []

	with open(tag_file, 'r') as f:
		raw_tags = json.load(f)

	if "danbooru" in tag_file:
		general_filter = "category"
	else:
		general_filter = "type"

	for t in raw_tags:
		if general_only and t[general_filter] != 0:
			continue
		tags.append(t["name"].replace("_"," "))
		if len(tags) >= limit:
			break
	
	if len(tags) <= 5:
		warm.append(f" failed to load tags from {tag_file}")
		print(warn[-1])
		return images
	
	status.append(f" loaded {len(tags)} tags successfully from {tag_file}")
	print(status[-1])
	for i in images:
		new = []
		for t in i.tags:
			if t.name not in tags and not any([t.name == x.name for x in whitelist]):
				removed.append(t.name)
			else:
				new.append(t)
		i.tags = new

	status.append(f" removed {len(set(removed))} obscure tags")
	print(status[-1])
	if debug: print("REM:",list(set(removed)))
	img_status(images)
	return images

# remove tags that only appear on `freq` images or less
def frequent_only(images,freq):
	if not freq:
		return images
	status.append(f"\nfiltering infrequent tags (min {freq})")
	print(status[-1])
	tags = {}
	removed = []

	for i in images:
		for t in i.tags:
			if t.name not in tags:
				tags[t.name] = 1
			else:
				tags[t.name] += 1
	for i in images:
		new = []
		for t in i.tags:
			if tags[t.name] < freq and not any([t.name == x.name for x in whitelist]):
				removed.append(t.name)
			else:
				new.append(t)
		i.tags = new

	status.append(f" removed {len(set(removed))} infrequent tags")
	print(status[-1])
	if debug: print("REM:",list(set(removed)))
	img_status(images)
	return(images)

# attempt to replace all wrongly-detected eye colors with the user-given one
def normalize_eye_color(images,target_color):
	if not target_color:
		return images
	removed = []

	status.append("\nattempting to normalize eye colors")
	print(status[-1])
	valid = ["blue", "red", "brown", "green", "purple", "yellow", "pink", "black", "aqua", "orange", "grey", "gray", "silver", "glowing", "multicolored", "white"]

	for i in images:
		tagged = False
		new = []
		for t in i.tags:
			if t.name.endswith("eyes"):
				color = t.name.split(" eyes")[0]
				if color in valid and not any([t.name == x.name for x in whitelist]):
					removed.append(t.name)
					tagged = True
				else:
					new.append(t)
			else:
				new.append(t)
		i.tags = new
		if tagged:
			i.tags += target_color

	if debug: print("REM:",list(set(removed)))
	if debug: print("ADD:",target_color)
	img_status(images)
	return images

# attempt to replace all wrongly-detected hair colors with the user-given one
def normalize_hair_color(images,target_color):
	if not target_color:
		return images
	removed = []

	status.append("\nattempting to normalize hair colors")
	print(status[-1])
	valid = ["blonde", "brown", "black", "blue", "cyan", "purple", "pink", "lavender", "red", "white", "multicolored", "green", "silver", "grey", "orange", "two-tone", "streaked", "aqua", "gradient", "light brown", "light blue", "dark blue", "platinum blonde"]

	for i in images:
		tagged = False
		new = []
		for t in i.tags:
			if t.name.endswith("hair"):
				color = t.name.split(" hair")[0]
				if color in valid and not any([t.name == x.name for x in whitelist]):
					removed.append(t.name)
					tagged = True
				else:
					new.append(t)
			else:
				new.append(t)
		i.tags = new
		if tagged:
			i.tags += target_color

	if debug: print("REM:",list(set(removed)))
	if debug: print("ADD:",target_color)
	img_status(images)
	return images

# attempt to replace all wrongly-detected hair colors with the user-given one
def normalize_hair_style(images,target_style):
	if not target_style:
		return images
	removed = []

	status.append("\nattempting to normalize hair style")
	print(status[-1])
	valid = ["long", "short", "very long", "braided", "medium", "shoulder-length", "floating", "drill", "wavy", "antenna", "spiked", "messy", "curly", "low-tied long", "asymmetrical", "tentacle", "absurdly long", "extremely long", "tied"]
	extra = ["twin braids", "double braid", "single braid", "side braid", "french braid", "hair ornament", "hair ribbon", "hair braid", "hair bow", "hair clips", "hair flower", "hair bun", "hair intakes", "hair tubes", "hair vents", "hair rings", "hair loop", "hair tie", "hair bell", "ponytail", "side ponytail", "low ponytail", "short ponytail", "braided ponytail", "folded ponytail"]

	for i in images:
		tagged = False
		new = []
		for t in i.tags:
			if t.name.endswith("hair"):
				style = t.name.split(" hair")[0]
				if style in valid and not any([t.name == x.name for x in whitelist]):
					removed.append(t.name)
					tagged = True
				else:
					new.append(t)
			elif t.name in extra and not any([t.name == x.name for x in whitelist]):
				removed.append(t.name)
				tagged = True
			else:
				new.append(t)
		i.tags = new
		if tagged:
			i.tags += target_style

	if debug: print("REM:",list(set(removed)))
	if debug: print("ADD:",target_style)
	img_status(images)
	return images

# add tags based on folder names. requires entire config file for parsing
def folder_rules(images, tag_rules):
	if not tag_rules:
		return images
	# add rules
	for rule in tag_rules:
		tags = str_to_tag_list(rule["target"])
		folder = rule["folder"]
		if rule["action"] == "add":
			added = 0
			for i in images:
				if i.category == folder:
					i.tags += (tags)
					added += 1
			if added > 0:
				status.append(f" AddFolder [{rule['target']}] (+{added} to {folder})")
				print(status[-1])
		elif rule["action"] == "remove":
			removed = []
			for i in images:
				if i.category == folder:
					new = []
					for t in i.tags:
						if t.name in [x.name for x in tags]:
							removed.append(t.name)
						else:
							new.append(t)
					i.tags = new
			if len(removed) > 0:
				status.append(f" RemoveFolder [{rule['target']}] (-{len(removed)} from {folder})")
				print(status[-1])
				if debug: print(" REM:",list(set(removed)))
	return images

# add tags based on existing tags.
def transitive_rules(images, custom_rules):
	if not custom_rules:
		return images
	for rule in custom_rules:
		if rule["type"] != "add":
			continue
		added = 0
		source = str_to_tag_list(rule["source"])
		for i in images:
			if any([t.name in [x.name for x in source] for t in i.tags]):
				for t in str_to_tag_list(rule["target"]):
					if t.name not in [x.name for x in i.tags]:
						i.tags.append(t)
						added += 1
		if added > 0:
			status.append(f" AddRule [{rule['source']}] (+{added})")
			print(status[-1])
	return images

# replace redundant tags
def replace_rules(images, custom_rules):
	if not custom_rules:
		return images
	for rule in custom_rules:
		if rule["type"] != "replace":
			continue
		source = str_to_tag_list(rule["source"])
		added = 0
		removed = []
		for i in images:
			tagged = False
			new = []
			for t in i.tags:
				if t.name in [x.name for x in source]:
					tagged = True
					removed.append(t.name)
				else:
					new.append(t)
			i.tags = new
			for t in str_to_tag_list(rule["target"]):
				if tagged and t.name not in [x.name for x in i.tags]:
					i.tags.append(t)
					added += 1
		if added > 0 or len(removed) > 0:
			status.append(f" ReplaceRule [{rule['target']}] (+{added} | -{len(removed)})")
			print(status[-1])
			if debug: print(" REM:",list(set(removed)))
	return images

# experimental spice rules
def spice_rules(images, spice_rules):
	if not spice_rules:
		return images
	# add rules
	for rule in spice_rules:
		if rule["type"] != "add":
			continue
		perc = float(rule["percent"])/100
		total = 0
		added = 0
		added_perc = 0
		for i in images:
			for t in str_to_tag_list(rule["target"]):
				total += 1
				if perc > random.random():
					i.tags.append(t)
					added += 1
		added_perc = added/total
		if added > 0:
			status.append(f" AddSpice [{rule['target']}] (+{added}|{round(added_perc*100)}%)")
			print(status[-1])
	# remove rules
	for rule in spice_rules:
		if rule["type"] != "remove":
			continue
		perc = float(rule["percent"])/100
		target = str_to_tag_list(rule["target"])
		total = 1
		removed = []
		removed_perc = 0
		for i in images:
			new = []
			for t in i.tags:
				if t.name in [x.name for x in target]:
					total += 1
					if perc > random.random() and perc > removed_perc: #overshoot
						removed.append(t.name)
					else:
						new.append(t)
				else:
					new.append(t)
			i.tags = new
			removed_perc = len(removed)/total
		if len(removed) > 0:
			status.append(f" RemoveSpice [{rule['target']}] (-{len(removed)}|{round(removed_perc*100)}%)")
			print(status[-1])
			if debug: print(" REM:",list(set(removed)))
	return images

# add triggerwords
def add_triggerword(images, tws):
	if not tws:
		return images
	for t in tws:
		t.position = 0
	status.append("\nadding triggerwords")
	print(status[-1])
	for i in images:
		new = []
		for t in i.tags:
			if t.name not in [str(x) for x in tws]:
				new.append(t)
		i.tags = new
		i.tags += tws
	return images

def blacklist(images,blacklist):
	if not blacklist:
		return images
	removed = 0
	for i in images:
		new = []
		for t in i.tags:
			if t.name in [str(x) for x in blacklist]:
				removed += 1
			else:
				new.append(t)
		i.tags = new
	status.append(f"blacklist applied {removed} times")
	print(status[-1])
	return images

# move tags to front of list, shuffle to increase fairness.
def raise_tags(images, to_raise):
	if not to_raise:
		return images
	raised = 0
	for i in images:
		for t in i.tags:
			if t.name in [str(x) for x in to_raise]:
				t.position = random.randint(4,8)
				raised += 1
	if raised > 0:
		status.append(f"Raised {len(to_raise)} tag(s) {raised} times")
		print(status[-1])
	return images

# remove duplicates, final pass
def dedupe_tags(images):
	duplicates = []
	for i in images:
		new = []
		for t in i.tags:
			if t.name in [x.name for x in new]:
				duplicates.append(t.name)
			else:
				new.append(t)
		i.tags = new
	if duplicates:
		status.append(f"Removed {len(duplicates)} duplicate tags")
		print(status[-1])
	return images

# get popular tags
def popular_tags(images):
	tags = {}
	for i in images:
		for t in i.tags:
			if t.name not in tags.keys():
				tags[t.name] = 1
			else:
				tags[t.name] += 1
	tags = {k: v for k, v in sorted(tags.items(), key=lambda item: item[1], reverse=True)}
	return tags

# write all tags to the desired output folder
def write_tags(images, folder):
	print(f"Writing tags to folder '{folder}'")
	for i in images:
		dst = i.get_step_path(folder)
		cat = os.path.split(dst)[0]
		if not os.path.isdir(cat):
			os.mkdir(cat)
		write_tag_txt(i.tags, dst)

# write list of tags to path, replacing extension
def write_tag_txt(tags, path):
	if len(tags) == 0:
		print(f"target '{path}' has no tags!")
		return
	txt = os.path.splitext(path)[0]+".txt"
	with open(txt,"w") as f:
		f.write(", ".join([str(x) for x in sorted(tags)]))

# read only status of tag count
def img_status(images,verbose=False):
	if verbose:
		status.append(f" Images: {len(images)}")
		print(status[-1])
		status.append(f" Total tags: {sum([int(x) for x in images])}")
		print(status[-1])
		status.append(f" Avg tag per image: {round(sum([int(x) for x in images])/len(images),2)}")
		print(status[-1])
	 # I'm proud of this one, probably the worst thing I've ever written in python:
	status.append(f" Unique tags: {len(list(set(sum([[str(y) for y in x.tags] for x in images],[]))))}")
	print(status[-1])
	# print("\nDEBUG: tags left:",images[1])

# default logic
def tag_fix(save=False):
	global whitelist
	global status
	global warn
	global c
	status = []
	warn = []
	status.append("Tag fixer")
	print(status[-1])

	# reload json
	if os.path.isfile("dataset.json"):
		with open("dataset.json") as f:
			data = json.load(f)
			if "tags" not in data.keys():
				warn.append("no tags or rules")
				print(warn[-1])
				return
			c = data["tags"]
	else:
		warn.append("Missing 'dataset.json' config")
		print(warn[-1])
		return

	# load images
	images = get_step_images(step_list[2],step_list[3])
	if len(images) == 0:
		warn.append("no tags")
		print(warn[-1])
		return
		
	# stats
	img_status(images,True)

	if True: #c["FixUnderscores"]:
		images = underscore_fix(images)

	# filter input images
	print(c["image_blacklist"])
	images = image_filter(images,str_to_tag_list(c["image_blacklist"]),c["filter_rules"])

	# load whitelist
	whitelist = str_to_tag_list(c["whitelist"])
	whitelist += str_to_tag_list(c["triggerword"])
	# whitelist += str_to_tag_list(c["triggerword_extra"])

	# popular-only filter
	tag_file = os.path.join("external",f'{c["booru"]["type"]}-tags.json')
	if os.path.isfile(tag_file):
		images = popular_only(images,tag_file,int(c["booru"]["popular_only"]),c["booru"]["general_only"])
	else:
		warn.append(f"Missing file {tag_file}\n PopularOnly filter disabled!")
		print(warn[-1])

	# apply filters
	images = normalize_eye_color(images,str_to_tag_list(c["normalize"]["eye_color"]))
	images = normalize_hair_color(images,str_to_tag_list(c["normalize"]["hair_color"]))
	images = normalize_hair_style(images,str_to_tag_list(c["normalize"]["hair_style"]))
	images = frequent_only(images,int(c["frequent_only"]))

	# rulesets
	status.append("\napplying custom rulesets (if any)")
	print(status[-1])
	images = folder_rules(images,c["folder_rules"])
	images = transitive_rules(images,c["custom_rules"])
	images = replace_rules(images,c["custom_rules"])
	images = spice_rules(images,c["spice_rules"])

	# post-filters
	images = add_triggerword(images,str_to_tag_list(c["triggerword"]))
	images = raise_tags(images,str_to_tag_list(c["triggerword_extra"]))
	images = blacklist(images,str_to_tag_list(c["blacklist"]))
	images = dedupe_tags(images)

	status.append("\nFinal:")
	print(status[-1])
	img_status(images,True)
	
	if save:
		write_tags(images,step_list[4])
	
	# return data
	data["tags"]["categories"] = list(set([str(x.category) for x in images]))
	data["tags"]["popular"] = popular_tags(images)
	data["tags"]["status"] = "\n".join(status)
	data["tags"]["warn"] = "\n".join(warn)
	return data

if __name__ == "__main__":
	# debug = True
	# run()
	# print(json.dumps(tag_fix(),indent=2))
	tag_fix(True)
