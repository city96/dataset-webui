#!/usr/bin/python3
# script to fix and filter tags using the rules in 'dataset.ini'
import os
import configparser
import random

if os.path.isfile("dataset.ini"):
	c = configparser.ConfigParser()
	c.optionxform=str #case sensitive
	c.read("dataset.ini")
else:
	print("Missing 'dataset.ini' config")
	exit(1)

# show removed tags at each step
debug = c["Misc"]["Debug"] == "True"

# image definition. do NOT edit __str__ and __repr__!
class Image:
	filename = None
	category = None
	img_path = None
	tag_path = None
	new_tag_path = None
	new_img_path = None
	tags = []
	def __int__(self):
		return len(self.tags)
	def __str__(self):
		return ", ".join([t.name for t in sorted(self.tags)])
	def __repr__(self):
		return ", ".join([t.name for t in sorted(self.tags)])

# tag definition. do NOT edit __str__ and __repr__!
class Tag:
	name = None
	position = 10
	def __str__(self):
		return f"{self.name}"
	def __repr__(self):
		return f"{self.name}"
	def __lt__(self, other):
         return self.position < other.position

# comma separated string to tag list
def str_to_taglist(string):
	taglist = []
	tags = string.replace('\n', ',').split(",")
	tags = [a.strip() for a in tags]
	for t in tags:
		if t:
			tag = Tag()
			tag.name = t
			taglist.append(tag)
	return taglist

# read tags from file, return list
def file_to_taglist(file):
	with open(file) as f:
		c = f.read()
	if not c:
		return
	return(str_to_taglist(c))

def underscore_fix(images):
	fixed = 0
	for i in images:
		for t in i.tags:
			if "_" in t.name:
				t.name = t.name.replace("_"," ")
				fixed += 1
	if fixed > 0:
		print(f"warning: tags with underscores found. Fixed {fixed} tags.")
	return images

# filter images by tags
def image_filter(images, tag_rules):
	blacklists = {}
	filters = {}
	for k in tag_rules.keys():
		if k.startswith("ImageBlacklistTags") and tag_rules[k]:
			blacklists[k] = str_to_taglist(tag_rules[k])
		if k.startswith("ImageBlacklistFilter") and tag_rules[k]:
			filters[k] = str_to_taglist(tag_rules[k])
	if not blacklist and not filters:
		return images
	print("\nFiltering input images.")
	removed = []
	filtered = []
	for i in images:
		for b in blacklists.values():
			if any([t in [x.name for x in i.tags] for t in [x.name for x in b]]):
				removed.append(i.filename)
				images.remove(i)
				break
	for i in images:
		for f in filters.values():
			if all([t in [x.name for x in i.tags] for t in [x.name for x in f]]):
				filtered.append(i.filename)
				images.remove(i)
				break

	print(f" removed {len(removed)} images from input [by tags]")
	if debug: print("REM:",removed)
	print(f" removed {len(filtered)} images from input [by filter]")
	if debug: print("REM:",filtered)
	print(f" Images: {len(images)}")
	return images

# load all images in folder
def image_loader(folder, output):
	images = []
	for cat in os.listdir(folder):
		if os.path.isdir(os.path.join(folder,cat)):
			for k in os.listdir(os.path.join(folder,cat)):
				name, ext = os.path.splitext(k)
				if ext in [".png",".jpg"]: #img
					i = Image()
					i.filename = k
					i.category = cat
					i.img_path = os.path.join(folder,os.path.join(cat,k))
					i.tag_path = os.path.join(folder,os.path.join(cat,name+".txt"))
					i.new_img_path = os.path.join(output,os.path.join(cat,k))
					i.new_tag_path = os.path.join(output,os.path.join(cat,name+".txt"))
					if os.path.isfile(i.tag_path):
						i.tags = file_to_taglist(i.tag_path)
						images.append(i)
					else:
						print(f" warning! image {i.filename} has no input tags.")
						i.tags = str_to_taglist("")
						images.append(i)
	return images

# load a list of `limit` popular tags, remove tags that aren't in this list
def popular_only(images, limit, tag_file):
	if not limit or not os.path.isfile(tag_file):
		return images
	print("\nfiltering unpopular tags")
	tags = []
	removed = []

	with open(tag_file,"r") as f:
		for tag in f:
			tags.append(tag.strip())
			if len(tags) >= limit:
				break

	print(f" loaded {len(tags)} tags successfully from {tag_file}")
	for i in images:
		for t in i.tags:
			if t.name not in tags and not any([t.name == x.name for x in whitelist]):
				removed.append(t.name)
				i.tags.remove(t)

	print(f" removed {len(removed)} instances of obscure tags")
	if debug: print("REM:",removed)
	img_status(images)
	return images

# remove tags that only appear on `freq` images or less
def frequent_only(images,freq):
	if not freq:
		return
	print(f"\nfiltering infrequent tags (min {freq})")
	tags = {}
	removed = []

	for i in images:
		for t in i.tags:
			if t.name not in tags:
				tags[t.name] = 1
			else:
				tags[t.name] += 1
	for i in images:
		for t in i.tags:
			if tags[t.name] < freq and not any([t.name == x.name for x in whitelist]):
				removed.append(t.name)
				i.tags.remove(t)

	print(f" removed {len(removed)} instances of infrequent tags")
	if debug: print("REM:",removed)
	img_status(images)
	return(images)

# attempt to replace all wrongly-detected eye colors with the user-given one
def normalize_eye_color(images,target_color):
	if not target_color:
		return images
	removed = []

	print("\nattempting to normalize eye colors")
	valid = ["blue", "red", "brown", "green", "purple", "yellow", "pink", "black", "aqua", "orange", "grey", "gray", "silver", "glowing", "multicolored", "white"]

	for i in images:
		tagged = False
		for t in i.tags:
			if t.name.endswith("eyes"):
				color = t.name.split(" eyes")[0]
				if color in valid and not any([t.name == x.name for x in whitelist]):
					removed.append(t.name)
					i.tags.remove(t)
					tagged = True
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

	print("\nattempting to normalize hair colors")
	valid = ["blonde", "brown", "black", "blue", "cyan", "purple", "pink", "lavender", "red", "white", "multicolored", "green", "silver", "grey", "orange", "two-tone", "streaked", "aqua", "gradient", "light brown", "light blue", "dark blue", "platinum blonde"]

	for i in images:
		tagged = False
		for t in i.tags:
			if t.name.endswith("hair"):
				color = t.name.split(" hair")[0]
				if color in valid and not any([t.name == x.name for x in whitelist]):
					removed.append(t.name)
					i.tags.remove(t)
					tagged = True
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

	print("\nattempting to normalize hair style")
	valid = ["long", "short", "very long", "braided", "medium", "shoulder-length", "floating", "drill", "wavy", "antenna", "spiked", "messy", "curly", "low-tied long", "asymmetrical", "tentacle", "absurdly long", "extremely long", "tied"]
	extra = ["twin braids", "double braid", "single braid", "side braid", "french braid", "hair ornament", "hair ribbon", "hair braid", "hair bow", "hair clips", "hair flower", "hair bun", "hair intakes", "hair tubes", "hair vents", "hair rings", "hair loop", "hair tie", "hair bell", "ponytail", "side ponytail", "low ponytail", "short ponytail", "braided ponytail", "folded ponytail"]

	for i in images:
		tagged = False
		for t in i.tags:
			if t.name.endswith("hair"):
				style = t.name.split(" hair")[0]
				if style in valid and not any([t.name == x.name for x in whitelist]):
					removed.append(t.name)
					i.tags.remove(t)
					tagged = True
			elif t.name in extra and not any([t.name == x.name for x in whitelist]):
				i.tags.remove(t)
				removed.append(t.name)
				tagged = True
		if tagged:
			i.tags += target_style

	if debug: print("REM:",list(set(removed)))
	if debug: print("ADD:",target_style)
	img_status(images)
	return images

# add tags based on folder names. requires entire config file for parsing
def folder_rules(images, tag_rules):
	add_rules = {}
	remove_rules = {}
	for k in tag_rules.keys():
		if k.startswith("AddFolder") and tag_rules[k]:
			add_rules[k] = str_to_taglist(tag_rules[k])
		elif k.startswith("RemoveFolder") and tag_rules[k]:
			remove_rules[k] = str_to_taglist(tag_rules[k])
	if not add_rules and not remove_rules:
		return images
	# add rules
	for rname, r in add_rules.items():
		added = 0
		for i in images:
			if i.category == r[0].name:
				i.tags += (r[1:])
				added += 1
		if added > 0:
			print(f" {rname} [{r[0].name}] (+{added})")
	
	# remove rules
	for rname, r in remove_rules.items():
		removed = []
		for i in images:
			if i.category == r[0].name:
				for t in i.tags:
					if t.name in [str(x) for x in r[1:]]:
						removed.append(t)
						i.tags.remove(t)
		if len(removed) > 0:
			print(f" {rname} [{r[0].name}] (-{len(removed)})")
			if debug: print(" REM:",list(set(removed)))
	return images

# add tags based on existing tags.
def transitive_rules(images, tag_rules):
	rules = {}
	for k in tag_rules.keys():
		if k.startswith("AddRule") and tag_rules[k]:
			rules[k] = str_to_taglist(tag_rules[k])
	if not rules:
		return images
	for rname, r in rules.items():
		added = 0
		for i in images:
			if any([t.name == r[0].name for t in i.tags]):
				i.tags += (r[1:])
				added += 1
		if added > 0:
			print(f" {rname} [{r[0].name}] (+{added})")
	return images

# replace redundant tags
def replace_rules(images, tag_rules):
	rules = {}
	for k in tag_rules.keys():
		if k.startswith("ReplaceRule") and tag_rules[k]:
			rules[k] = str_to_taglist(tag_rules[k])
	if not rules:
		return images
	for rname, r in rules.items():
		added = 0
		removed = []
		for i in images:
			tagged = False
			for t in i.tags:
				if t.name in [str(x) for x in r[1:]]:
					tagged = True
					removed.append(t.name)
					i.tags.remove(t)
			if r[0].name not in [str(x) for x in i.tags] and tagged:
				i.tags.append(r[0])
				added += 1
		if added > 0 or len(removed) > 0:
			print(f" {rname} [{r[0].name}] (+{added} | -{len(removed)})")
			if debug: print(" REM:",list(set(removed)))
	return images

# experimental spice rules
def spice_rules(images, tag_rules):
	add_rules = {}
	remove_rules = {}
	for k in tag_rules.keys():
		if k.startswith("AddSpice") and tag_rules[k]:
			add_rules[k] = str_to_taglist(tag_rules[k])
		elif k.startswith("RemoveSpice") and tag_rules[k]:
			remove_rules[k] = str_to_taglist(tag_rules[k])
	if not add_rules and not remove_rules:
		return images
	# add rules
	for rname, r in add_rules.items():
		perc = float(r[0].name)
		total = 0
		added = 0
		added_perc = 0
		for i in images:
			for t in r[1:]:
				total += 1
				if perc > random.random():
					i.tags.append(t)
					added += 1
		added_perc = added/total
		if added > 0:
			print(f" {rname} [{r[0].name}] (+{added}|{round(added_perc*100)}%)")
	# remove rules
	for rname, r in remove_rules.items():
		perc = float(r[0].name)
		total = 0
		removed = []
		removed_perc = 0
		for i in images:
			for t in i.tags:
				if t.name in [str(x) for x in r[1:]]:
					total += 1
					if perc > random.random() and perc > removed_perc: #overshoot
						removed.append(t)
						i.tags.remove(t)
			removed_perc = len(removed)/total
		if len(removed) > 0:
			print(f" {rname} [{r[0].name}] (-{len(removed)}|{round(removed_perc*100)}%)")
			if debug: print(" REM:",list(set(removed)))
	return images

# add triggerwords
def add_triggerword(images, tws):
	if not tws:
		return images
	for t in tws:
		t.position = 0
	print("\nadding triggerwords")
	for i in images:
		for t in i.tags:
			if t.name in [str(x) for x in tws]:
				i.tags.remove(t)
		i.tags += tws
	return images

# global whitelist
whitelist = str_to_taglist(c["Tags"]["Whitelist"])
whitelist += str_to_taglist(c["Tags"]["Triggerword"])

def blacklist(images,blacklist):
	if not blacklist:
		return images
	removed = 0
	for i in images:
		for t in i.tags:
			if t.name in [str(x) for x in blacklist]:
				i.tags.remove(t)
				removed += 1
	print(f"blacklist applied {removed} times")
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
		print(f"Raised {len(to_raise)} tag(s) {raised} times")
	return images

# remove duplicates, final pass
def dedupe_tags(images):
	duplicates = []
	for i in images:
		tmp = []
		for t in i.tags:
			if t.name in tmp:
				duplicates.append(t.name)
				i.tags.remove(t)
			else:
				tmp.append(t.name)
	if duplicates:
		print(f"Removed {len(duplicates)} duplicate tags")
	return images

# write all tags to the desired output folder
def write_tags(images, folder):
	print(f"Writing tags to folder '{folder}'")
	for i in images:
		cat = os.path.join(c["Tags"]["OutputFolder"],i.category)
		if not os.path.isdir(cat):
			os.mkdir(cat)
		with open(i.new_tag_path,"w") as f:
			f.write(str(i))

# copy images to the output folder
def copy_images(images):
	print(" Copying images to output folder...")
	import shutil
	for i in images:
		if i.img_path == i.new_img_path: # don't copy to itself
			continue
		elif os.path.isfile(i.new_img_path) and os.path.getsize(i.img_path) == os.path.getsize(i.new_img_path): # probably the same
			continue
		elif os.path.isfile(i.new_img_path):
			print(f" image exists but is different from source: {i.new_img_path}")
			continue
		else:
			shutil.copyfile(i.img_path, i.new_img_path)
	print(" done!")

# read only status of tag count
def img_status(images,verbose=False):
	if verbose:
		print(f" Images: {len(images)}")
		print(f" Total tags: {sum([int(x) for x in images])}")
		print(f" Avg tag per image: {round(sum([int(x) for x in images])/len(images),2)}")
	 # I'm proud of this one, probably the worst thing I've ever written in python:
	print(f" Unique tags: {len(list(set(sum([[str(y) for y in x.tags] for x in images],[]))))}")
	# print("\nDEBUG: tags left:",images[1])

# default logic + command line UI
def cli_ui():
	print("Tag fixer")
	images = image_loader(c["Tags"]["InputFolder"],c["Tags"]["OutputFolder"])
	# stats
	img_status(images,True)

	if c["Misc"]["FixUnderscores"]:
		images = underscore_fix(images)

	# filter input images
	images = image_filter(images,c["Tags"])

	# tag source for popular-only filter
	if c["Tags"]["GeneralTagsOnly"]:
		tag_file = os.path.join("other",f'tags-{c["Tags"]["TagSource"]}-general.txt')
	else:
		tag_file = os.path.join("other",f'tags-{c["Tags"]["TagSource"]}-all.txt')
	if not os.path.isfile(tag_file):
		print(f"Missing file {tag_file}\n PopularOnly filter disabled!")

	# apply filters
	images = popular_only(images,int(c["Tags"]["PopularOnly"]),tag_file)
	images = frequent_only(images,int(c["Tags"]["FrequentOnly"]))
	images = normalize_eye_color(images,str_to_taglist(c["Tags"]["EyeColor"]))
	images = normalize_hair_color(images,str_to_taglist(c["Tags"]["HairColor"]))
	images = normalize_hair_style(images,str_to_taglist(c["Tags"]["HairStyle"]))

	# rulesets
	print("\napplying custom rulesets (if any)")
	images = folder_rules(images,c["Tags"])
	images = transitive_rules(images,c["Tags"])
	images = replace_rules(images,c["Tags"])
	images = spice_rules(images,c["Tags"])

	# post-filters
	images = add_triggerword(images,str_to_taglist(c["Tags"]["Triggerword"]))
	images = raise_tags(images,str_to_taglist(c["Tags"]["RaisedTags"]))
	images = blacklist(images,str_to_taglist(c["Tags"]["Blacklist"]))
	images = dedupe_tags(images)

	print("\nFinal:")
	img_status(images,True)
	if debug or input("\nDo you want to write the new tags to disk? [y/N]? ").lower() != "y":
		exit(0)
	write_tags(images,c["Tags"]["OutputFolder"])
	if not all([os.path.isfile(x.new_img_path) for x in images]):
		if input("\nDo you want to copy the images to the output folder [y/N]? ").lower() == "y":
			copy_images(images)

cli_ui()
input("\nPress any key to exit...")