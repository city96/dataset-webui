#!/usr/bin/python3
# Script to create sorting groups for step 3
import os

class Category:
	name = None
	repeats = 0
	images = 0
	unsorted = False

	def __str__(self):
		return f"{self.repeats}_{self.name}"
	def __repr__(self):
		return f"{self.repeats}_{self.name}"

# the folder creator help
choices = {
	"Default": {
		"text" : "A single folder with no extra sorting/importance",
		"folders" : ["1_default"],
	},
	"Quality": {
		"text" : "Sort by quality into two folders",
		"folders" : ["1_medium", "3_good"],
	},
	"Quality (fine)": {
		"text" : "Sort by quality into three folders",
		"folders" : ["1_bad", "3_medium", "5_good"],
	},
	"Style": {
		"text" : "Preset for artist styles",
		"folders" : ["1_sketch","3_commission","5_main-art"],
	},
}

def get_categories(folder, raw=False):
	categories = []
	unsorted = Category()
	unsorted.name = "unsorted"
	unsorted.unsorted = True
	for k in os.listdir(folder):
		c = Category()
		if os.path.isdir(os.path.join(folder,k)):
			if "_" not in k and not raw:
				print(f" warning: ignoring invalid category name '{k}'. (Did you use '-' instead of '_'?)")
				continue
			c.name = k.split("_",1)[1]
			try:
				c.repeats = int(k.split("_",1)[0])
			except ValueError:
				c.name = k
			for i in os.listdir(os.path.join(folder,k)):
				name, ext = os.path.splitext(i)
				if ext in [".png",".jpg",".jpeg",".gif",".webp",".bmp",".tif"]: #img
					c.images += 1
			categories.append(c)
		else:
			unsorted.images += 1
	if unsorted.images > 0:
		if not raw:
			print(f" warning: folder '{folder}' has {unsorted.count} images that don't belong to any category")
		categories.append(unsorted)
	return categories

# pretty print category list
def print_categories(cats):
	name_maxlen = max([len(str(x.name)) for x in cats])
	repeats_maxlen = max(max([len(str(x.images)) for x in cats]),len("repeats"))+2

	print(f" #\t {'name'.ljust(name_maxlen)}  {'repeats'.ljust(repeats_maxlen)}  images")
	for k in range(len(cats)):
		print(f" {k+1}\t {cats[k].name.ljust(name_maxlen)}  {str(cats[k].repeats).ljust(repeats_maxlen)}  {cats[k].images}")

# budget folder creator wizard:
def custom_categories():
	input("unimplemented")
	exit()

# command line UI
def cli_ui():
	print("Sorting Group creator")
	if not os.path.isdir('0 - raw') and not os.path.isdir('1 - cropped'):
		print (f" neither '0 - raw' nor '1 - cropped' exists. (Do you have a dataset active?)")
		return

	raw_categories = get_categories('0 - raw', True)
	categories = get_categories('1 - cropped', True)

	if len(raw_categories) == 0 and len(categories) == 0:
		print(" no images in either folder. (Do you have a dataset active?)")

	if len(raw_categories) > 0 and len(categories) == 0:
		print(" no images in folder '1 - cropped', using categories/images in '0 - raw'")
		categories = raw_categories

	print()
	if len(categories) == 1:
		if categories[0].unsorted:
			print("You currently don't have any categories set up")
	else:
		print("Your current categories:")
		print_categories(categories)

	print("\nChecking folder '2 - sorted'")
	sorted_categories = get_categories('2 - sorted')
	if len(sorted_categories) > 0:
		print("You already have the following categories in '2 - sorted':")
		print_categories(sorted_categories)
		print("Delete these folders to create different categories!")
		exit()

	print("\nHow would you like to set up categories in the '2 - sorted' folder?")

	for c,d in choices.items():
		print(f" {list(choices.keys()).index(c)+1} - {c} [{d['text']}]")
		print("  folders:")
		for f in d['folders']:
			print(f"   - {f}")
		print()
	print(f" {len(choices.keys())+1} - Something else [create groups]\n")

	choice = ""
	while True:
		i = input("Choice [number]: ")
		try:
			k = int(i) - 1
			if k == len(choices.keys()):
				choice = None
				break
			if k < 0:
				print(f"Invalid input '{i}'\n")
				continue
			choice = list(choices.keys())[k]
		except:
			print(f"Invalid input '{i}'\n")
			continue
		break

	if not choice:
		choice = custom_categories()

	print("\nThe following folders will be created:")
	for f in choices[choice]["folders"]:
		f = os.path.join("2 - sorted", f)
		print(f" {f}")

	if input("\nDo you want to continue? [y/N]? ").lower() != "y":
		print("folder creation command (for manual creation):")
		print(f"mkdir {' '.join(choices[choice]['folders'])}")
		exit()
		
	print("\ncreating folders")
	for f in choices[choice]["folders"]:
		f = os.path.join("2 - sorted", f)
		print(f" {f}")
		os.mkdir(f)

if __name__ == "__main__":
	cli_ui()
	input("\nPress any key to exit...")
