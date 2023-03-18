#!/usr/bin/python3
# Make A1111 webui api functions available
import os
import json
import requests
from base64 import b64encode
from PIL import Image as pImage

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
