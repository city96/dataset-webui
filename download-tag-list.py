#!/usr/bin/python3
# get pre-made or newest taglist
# problems:
#  - api not implemented
#  - only supports danbooru and general tags
#  - can't host tags on github due to 'offensive content'
import os
import requests
import time

premade = {
	"gelbooru-general-only" : {
		"url" : "https://files.catbox.moe/ah8rgm.txt",
		"filename" : os.path.join("other","tags-gelbooru-general.txt"),
	},
}

if all([os.path.isfile(x["filename"]) for x in premade.values()]):
	print("All tags already downloaded!")
	input("\nPress any key to exit...")
	exit()

print("The follwoing files will be saved into the 'other' folder:")
for name, i in premade.items():
	url, fname = i.values()
	name_maxlen = max([len(x) for x in premade.keys()])
	print(f" - {name.ljust(name_maxlen)}: {url} -> {fname}")

if input("\nStart download? [y/N] ").lower() != 'y':
	exit()
print("asd")

for name, i in premade.items():
	url, fname = i.values()
	print(' downloading', url)
	data = requests.get(url)
	data.raise_for_status()
	data = data.content
	time.sleep(1) # rate limit
	with open(fname, 'wb') as f:
		f.write(data)

print("All files downloaded")
input("\nPress any key to exit...")