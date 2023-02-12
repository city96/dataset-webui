#!/usr/bin/python3
# Script to track progress
import os

folder_list = [
	"0 - raw",
	"1 - cropped",
	"2 - sorted",
	"3 - tagged",
	"4 - fixed",
	"5 - out",
]

# comma separated string to list
def str_to_taglist(string):
	taglist = []
	tags = string.replace('\n', ',').split(",")
	tags = [a.strip() for a in tags]
	for tag in tags:
		if tag:
			taglist.append(tag)
	return taglist

def get_step_info(folder):
	print(f"\nStep {folder}")
	if not os.path.isdir(folder):
		print (f" folder for step '{folder}' doesn't exist")
		return

	uncategorized = sum([os.path.isfile(os.path.join(folder,x)) for x in os.listdir(folder)])
	categories = {}
	tags = []

	for cat in os.listdir(folder):
		if os.path.isdir(os.path.join(folder,cat)):
			for k in os.listdir(os.path.join(folder,cat)):
				path = os.path.join(cat,k)
				ext = os.path.splitext(k)[1]
				if ext in [".png",".jpg"]: #img
					if cat not in categories.keys():
						categories[cat] = 1
					else:
						categories[cat] += 1
				elif ext in [".txt"]: #tag
					if folder == "4 - fixed" or folder == "3 - tagged":
						with open(os.path.join(folder,path)) as f:
							raw = f.read()
						if raw:
							tags += str_to_taglist(raw)
							
						continue
				elif os.path.isdir(path): #dir
					print(f" Warning! {dirpath} is a category inside a category! it will be ignored")
				else:
					print(f" Warning! Unknown extension '{ext}' for file {path}")

	imgcount = 0
	if categories:
		imgcount += sum(categories.values())
		print(f" Total categorized images: {imgcount}")
		for cat, count in categories.items():
			print(f"  {cat} ({count})")
	if uncategorized:
		imgcount += uncategorized
		print(f" Total uncategorized images: {imgcount}")
	if not categories and not uncategorized:
		print(" No images")
	if len(tags)>0:
		print(f" Total tags: {len(tags)}")
		if imgcount:
			print(f"  Avg tag per image: {round(len(tags)/imgcount,2)}")
		print(f"  Unique tags: {len(list(set(tags)))}")

for f in folder_list:
	get_step_info(f)
input("\nPress any key to exit...")