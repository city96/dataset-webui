#!/usr/bin/python3
import argparse
import requests
import json
import time
import os
from common import api_cacher, verify_input

use_cache = True

# grab tags directly from danbooru api
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

# grab tags directly from gelbooru api
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

# grab tags from gist or catbox
def download_premade_tags(args):
	# taglist from web
	premade = {
		"danbooru" : {
			"url" : "https://gist.githubusercontent.com/city96/86451816d65636103393e380400abaa3/raw/edaaa37c931240add974e006b72b63b8fc217167/danbooru-tags.json",
			"url_alt" : "https://files.catbox.moe/w5duuj.json",
			"filename" : os.path.join("external","danbooru-tags.json"),
		},
		"gelbooru" : {
			"url" : "https://gist.githubusercontent.com/city96/86451816d65636103393e380400abaa3/raw/edaaa37c931240add974e006b72b63b8fc217167/gelbooru-tags.json",
			"url_alt" : "https://files.catbox.moe/ipp6k7.json",
			"filename" : os.path.join("external","gelbooru-tags.json"),
		},
	}
	try:
		for name, i in premade.items():
			if not args.tag_catbox:
				print(' downloading', i["url"])
				data = requests.get(i["url"])
			else:
				print(' downloading', i["url_alt"])
				data = requests.get(i["url_alt"])
			data.raise_for_status()
			data = data.content
			with open(i["filename"], 'wb') as f:
				f.write(data)
			time.sleep(1) # rate limit
	except:
		print(" couldn't download files!")

def verify_tags(verify_content = True):
	for file in ["danbooru-tags.json","gelbooru-tags.json"]:
		path = os.path.join("external",file)
		if not os.path.isfile(path):
			return False

		if not verify_content:
			return True

		with open(path, 'r') as f:
			try:
				raw_tags = json.load(f)
			except:
				print(f"Error parsing '{path}'")
				return False
			if len(raw_tags) < 9000:
				print(f"Json at path '{path}' only has {len(raw_tags)} tags. expected 9000+")
				return False
	return True

# tag download
def download_tags(args):
	if verify_tags(args.verify) and not args.overwrite:
		print("Tags already downloaded")
		return

	if (args.auto or verify_input(f"Download tags? [y/n] ",'y','n')):
		print(f"Downloading tags from {'GitHub Gist' if not args.tag_catbox else 'catbox.moe'}")
		if (args.tag_scrape and args.auto or not args.auto and verify_input(f"Scrape tags (not recommended)? [y/n] ",'y','n')):
			print("Starting scrape")
			# scrape
			download_danbooru_tags()
			download_gelbooru_tags()
		else: # Download
			download_premade_tags(args)

	print("Tag download complete")
	if not verify_tags():
		input("VERIFICATION FAILED! check files on disk. Ctrl+C to abort.")

# from https://cdnjs.com/libraries/cropperjs
def download_cropperjs(args):
	files = {
		os.path.join("external","cropper.js") : "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.js",
		os.path.join("external","cropper.css") : "https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.css",
	}
	if all([os.path.isfile(x) for x in files.keys()]) and not args.overwrite:
		print("Cropper.js files already downloaded!")
		return
	
	print("Downloading cropperjs from cloudflare")
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

	if all([os.path.isfile(x) for x in files.keys()]):
		print("Cropper.js download complete")
	else:
		input("VERIFICATION FAILED! check files on disk. Ctrl+C to abort.")
		[print(f" {url} => other/{path}") for url,path in files.items()]

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Download/check project dependencies')
	parser.add_argument('--auto', action=argparse.BooleanOptionalAction, default=True, help='Auto-download all dependencies, only ask user on error')
	parser.add_argument('--verify', action=argparse.BooleanOptionalAction, default=True, help='Check if downloaded files are valid')
	parser.add_argument('--overwrite', action=argparse.BooleanOptionalAction, default=False, help='Overwrite files, even if they exist.')

	parser.add_argument('--skip-cropperjs', dest="cropper_skip", action="store_true", help='Don\'t download Cropper.js')
	parser.add_argument('--skip-tags', dest="tag_skip", action="store_true", help='Don\'t download tag json files')
	parser.add_argument('--force-tag-scrape', dest="tag_scrape", action="store_true", help='Use built-in scraper for tags instead of downloading')
	parser.add_argument('--tag-catbox', dest="tag_catbox", action="store_true", help='Download tags from catbox.moe instead of GitHub Gist')

	args = parser.parse_args()

	if not os.path.isdir("external"):
		os.mkdir("external")

	if not args.tag_skip:
		download_tags(args)
	if not args.cropper_skip:
		download_cropperjs(args)
	if not args.auto:
		input("\nPress any key to exit/continue...")
