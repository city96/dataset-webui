#!/usr/bin/python3
# get pre-made or newest taglist

import requests
import json
import time
import os

use_cache = True

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

# api cacher, "borrowed" from unknown project.
def api_cacher(api_base, api_url):
	global use_cache
	if not os.path.exists('.cache') and use_cache:
		os.makedirs('.cache')

	filename = api_url.replace(api_base,'')
	filename = filename.replace('/','_')
	filename = filename.replace('?','_')
	filename = filename.replace('&','_')
	path = os.path.join('.cache',filename+'.json')

	if os.path.isfile(path) and use_cache:
		print('   cached', api_url)
		with open(path, 'r') as f:
			data_json = json.load(f)
	else:
		print('   request', api_url)
		# data = requests.get(api_url)
		# pretend to be chrome
		user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
		data = requests.get(api_url, headers={'User-Agent': user_agent})

		data.raise_for_status()
		data_json = data.json()
		time.sleep(1)
		with open(path, 'wb') as f:
			f.write(data.content)
	return data_json

# grap tags directly from danbooru api
def download_danbooru_tags(out_file, min_count=1000, max_page=10):
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

	print(f" writing to file {out_file}")
	with open(out_file,"w") as f:
		json.dump(tags, f)

# grap tags directly from gelbooru api
def download_gelbooru_tags(out_file, min_count=1000, max_page=100, deprecated=True):
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

	with open(out_file,"w") as f:
		json.dump(tags, f)

# grab tags from catbox
def download_premade():
	print("Downloading from catbox.moe")

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
	

# bootleg input verification
def verify_input(text,true,false,default=None):
	while true:
		i = input(text).lower()
		if i == true.lower():
			return True
		elif i == false.lower():
			return False
		elif default != None:
			return default
		else:
			print(f"Invalid input '{i}'\n")

# default logic + command line UI
def cli_ui():
	if all([os.path.isfile(x["filename"]) for x in premade.values()]):
		print("All tags already downloaded!")
		print("Delete 'danbooru-tags.json' and 'gelbooru-tags.json' to re-download.")
		return
	
	print("Do you want to download the pre-made json files or scrape the tags yourself?")
	print(" It is recommended to download the pre-made ones as scraping takes")
	print(" a long time and places extra load on the servers.\n")
	
	if verify_input(f"Download premade or Scrape? [d/s] ",'d','s'):
		print("\nStarting download...")
		download_premade()
	else:
		# scrape
		download_gelbooru_tags(premade["gelbooru"]["filename"])
		download_danbooru_tags(premade["danbooru"]["filename"])

cli_ui()
input("\nPress any key to exit...")
