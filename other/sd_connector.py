#!/usr/bin/python3
# Make A1111 webui api functions available
import os
import json
import requests
from base64 import b64encode
from PIL import Image as pImage
from common import Image, step_list
from status import get_step_images

def sd_api_check(url,quick=False):
	data = {
		"webui" : None,
		"api" : None,
		"tagger" : None,
	}
	if url.endswith("/"):
		url = url.rstrip("/")

	try:
		webui_test = f"{url}/favicon.ico"
		r = requests.get(url)
		r.raise_for_status()
		print("Webui connection OK")
		data["webui"] = True
		if quick:
			return data
	except:
		data["webui"] = False
		print("Webui connection Failed")
		return data

	try:
		api_test = f"{url}/sdapi/v1/progress"
		r = requests.get(api_test)
		r.raise_for_status()
		if "state" in r.json().keys():
			data["api"] = True
			print("Webui/Api connection OK")
		else:
			print("Webui/Api connection OK, got invalid reply")
			# return data // not fatal ?
	except:
		data["api"] = False
		print("Webui/Api connection Failed")
		return data

	try:
		tagger_test = f"{url}/tagger/v1/interrogators"
		r = requests.get(tagger_test)
		r.raise_for_status()
		if "models" in r.json().keys():
			data["tagger"] = True
			print("Webui/Tagger connection OK")
		else:
			print("Webui/Tagger got invalid reply")
			return data
	except:
		data["tagger"] = False
		print("Webui/Tagger connection Failed")
		return data

	return data

def sd_tag_image(url, image, overwrite=False):
	"""Write autotagger result as json (to preserve tag confidence)"""
	print(f"autotagging '{image}'")
	if url.endswith("/"): url = url.rstrip("/")
	if "localhost" in url: url = url.replace("localhost","127.0.0.1") # faster, for some reason
	
	if not os.path.isdir(step_list[2]):
		os.mkdir(step_list[2])
	
	cat_path = os.path.split(image.path)[0]
	cat_path = cat_path.replace(step_list[2],step_list[3],1)
	if not os.path.isdir(cat_path):
		os.mkdir(cat_path)
	
	# might fail with some formats?
	with open(image.path, mode='rb') as f:
		base64 = b64encode(f.read()).decode("utf-8") 
	payload = {
		"image": base64,
		"model": "wd14-vit-v2-git",
		"threshold": 0.35
	}

	fname, ext = os.path.splitext(image.get_id())
	image = f"data:image/{ext[1:]};base64,{base64}"
	json_file = os.path.join(step_list[3],fname+".json")
	if os.path.isfile(json_file) and not overwrite:
		print(" already tagged")
		with open(json_file) as f:
			data = json.load(f)
		if "caption" not in data.keys():
			return( {"caption" : {"Empty captio",1.0}, "image": image} )
		data["caption"]["Already tagged"] = 1.0
		data["image"] = image
		data["caption"] = dict(sorted(data["caption"].items(), key=lambda item: item[1], reverse=True))
		return(data)

	try:
		data = requests.post(f"{url}/tagger/v1/interrogate", json=payload)
		data.raise_for_status()
		data_json = data.json()
	except Exception as e:
		print(e)
		return( {"warn" : ["tagging error"]} )
	
	if (not data_json or "caption" not in data_json.keys()):
		return( {"warn" : ["tagging error"]} )
	
	# data_json["caption"] = sorted(data_json["caption"].items(), key=lambda x: x[1])
	with open(json_file, "w") as f:
		strdata = json.dumps(data_json, indent=2)
		f.write(strdata)
	data_json["image"] = image
	return data_json

# for i in (get_step_images(step_list[2])):
	# print(sd_tag_image("http://localhost:7860/",i))