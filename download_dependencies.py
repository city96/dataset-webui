#!/usr/bin/python3
# get pre-made or newest taglist

import requests
import json
import time
import os
from common import api_cacher, verify_input

use_cache = True

# grap tags directly from danbooru api
def download_danbooru_tags(min_count=1000, max_page=10):
	api_base = "https://danbooru.donmai.us/"
	page = 0
	tags = []
	while True:
		url = f"{api_base}tags.json?limit=1000&search[order]=count&page={page}"
		data = api_cacher(api_base, url)
		tags += data
		if page >= max_page:
			print(f" page {max_page} reached")
			break
		for tag in data:
			print(tag["post_count"])
			if tag["post_count"] < min_count:
				print(f" min images/tag {min_count} reached")
				break
		else:
			page += 1
			continue
		break

	out_file = os.path.join("other","danbooru-tags.json")
	print(f" writing to file {out_file}")
	with open(out_file,"w") as f:
		json.dump(tags, f)

# grap tags directly from gelbooru api
def download_gelbooru_tags(min_count=1000, max_page=100, deprecated=True):
	api_base = "https://gelbooru.com/index.php"
	api_key = "&api_key=anonymous"
	page = 0
	tags = []
	while True:
		url = f"{api_base}?page=dapi&s=tag&q=index&limit=100&orderby=count&order=DESC&json=1&pid={page}{api_key}"
		data = api_cacher(api_base, url)
		tags += data["tag"]
		if page+1 >= max_page:
			print(f" page {max_page} reached")
			break
		for tag in data["tag"]:
			if tag["count"] < min_count:
				print(f" min images/tag {min_count} reached")
				break
			if not deprecated and tag["type"] == 6:
				tags.remove(tag);
		else:
			page += 1
			continue
		break

	out_file = os.path.join("other","gelbooru-tags.json")
	with open(out_file,"w") as f:
		json.dump(tags, f)

# grab tags from catbox
def download_premade_tags():
	# taglist from web
	premade = {
		"danbooru" : {
			"url" : "https://files.catbox.moe/w5duuj.json",
			"url_alt" : "https://anonfiles.com/n6H1c3Ydy1/danbooru-tags_json",
			"filename" : os.path.join("other","danbooru-tags.json"),
		},
		"gelbooru" : {
			"url" : "https://files.catbox.moe/ipp6k7.json",
			"url_alt" : "https://anonfiles.com/ydHdcbY0y3/gelbooru-tags_json",
			"filename" : os.path.join("other","gelbooru-tags.json"),
		},
	}
	print("Downloading tags from catbox.moe")

	try:
		for name, i in premade.items():
			print(' downloading', i["url"])
			data = requests.get(i["url"])
			data.raise_for_status()
			data = data.content
			with open(i["filename"], 'wb') as f:
				f.write(data)
			time.sleep(1) # rate limit
	except:
		print(" couldn't download files!")
	print("\nif any files are missing, download them manually!")
	[print(f" {i['url']} => {i['filename']}") for i in premade.values()]
	print("alternative links:")
	[print(f" {i['url_alt']} => {i['filename']}") for i in premade.values()]

# tag download
def download_tags(auto=False):
	print("\n\nDownloading Tags")
	if os.path.isfile(os.path.join("other","gelbooru-tags.json")) and os.path.isfile(os.path.join("other","danbooru-tags.json")):
		print("All tags already downloaded!")
		print("Delete 'danbooru-tags.json' and 'gelbooru-tags.json' to re-download.")
		return

	print("Do you want to download the pre-made json files or scrape the tags yourself?")
	print(" It is recommended to download the pre-made ones as scraping takes")
	print(" a long time and places extra load on the servers.\n")

	if verify_input(f"Download premade or Scrape? [d/s] ",'d','s'):
		print("\nStarting download...")
		download_premade_tags()
	else:
		# scrape
		download_danbooru_tags()
		download_gelbooru_tags()

# from https://cdnjs.com/libraries/cropperjs
def download_cropperjs():
	print("\n\nDownloading cropperjs from cloudflare")
	files = {
		os.path.join("web","cropper.js") : "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.js",
		os.path.join("web","cropper.css") : "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.css",
	}
	if all([os.path.isfile(x) for x in files.keys()]):
		print("All cropperjs files already downloaded!")
		return
	
	try:
		for path, url in files.items():
			print(' downloading', path)
			data = requests.get(url)
			data.raise_for_status()
			data = data.content
			with open(path, 'wb') as f:
				f.write(data)
			time.sleep(1) # rate limit
	except:
		print(" couldn't download files!")
	print("\nif any files are missing, download them manually!")
	[print(f" {url} => other/{path}") for url,path in files.items()]

# default logic + command line UI
def cli_ui():
	download_cropperjs()
	download_tags()

if __name__ == "__main__":
	cli_ui()
	input("\nPress any key to exit...")
