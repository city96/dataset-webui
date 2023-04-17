#!/usr/bin/python3
import argparse
import asyncio
from aiohttp import web
from base64 import b64encode
import aiohttp
import json
import os

from scripts.dataset import create_dataset, save_dataset, load_dataset, get_folder_dataset, dataset_status
from scripts.common import step_list, Image
from scripts.loader import load_dataset_json, get_step_images
from scripts.save import save_json
from scripts.status import get_status
from scripts.crop import crop_info, crop_image
from scripts.category import category_info
from scripts.sort import sort_info, sort_write
from scripts.tags import tag_fix, imgtag_info, imgtag_all_tags
from scripts.out import finalize_image

from inference.check import onnx_enabled
from inference.connector import get_image_tags, Autotagger, Autocrop

app = web.Application()

async def index(request):
	return web.FileResponse('web/index.html')

async def favicon(request):
	return web.FileResponse('web/favicon.ico')

async def handle(request):
	path = os.path.join("web", str(request.url.relative())[1:])
	if not os.path.isfile(path):
		path = os.path.join("external", str(request.url.relative())[1:])
		if not os.path.isfile(path):
			return web.Response(status=404,text="404")

	if os.path.splitext(path)[1] in [".html",".css",".png"]:
		return web.FileResponse(path)
	elif os.path.splitext(path)[1] in [".js"]:
		headers = {
			"Content-Type" : "application/javascript"
		}
		return web.FileResponse(path,headers=headers)
	else:
		return web.Response(status=403,text="403")

async def handle_image(request):
	"""Return any file that is present in any of the step folders"""
	path = str(request.path)[5:]
	if os.path.isfile(path) and any(path.startswith(x) for x in step_list):
		return web.FileResponse(path)
	else:
		return web.Response(status=404,text="404")

async def api_json_save(request):
	"""Update part of the dataset.json file [handled by save.py]"""
	if request.body_exists:
		data = await request.read()
		data = json.loads(data)
		save_json(data)
	else:
		print("no data")
	return web.json_response({})

async def inference_check(request):
	data = {
		"onnx" : onnx_enabled
	}
	return web.json_response(data)

autotagger = None
async def api_autotag(request):
	"""Autotagger [handled by local+inference.*]"""
	if not onnx_enabled: return web.Response(status=503,text="onnx runtime missing")
	global autotagger

	confidence = float(request.rel_url.query.get('confidence', 0.35))

	if request.match_info['command'] == "run":
		overwrite = request.rel_url.query.get('overwrite').lower() == "true"
		if not autotagger or not autotagger.is_alive():
			print("Start task")
			autotagger = Autotagger(get_step_images(step_list[2]), overwrite, confidence)
			autotagger.start()
			return web.json_response(autotagger.get_status())
	elif request.match_info['command'] == "run_poll":
		status = autotagger.get_status() if autotagger and autotagger.is_alive() else {"run" : False}
		return web.json_response(status)
	elif request.match_info['command'] == "single":
		path = request.rel_url.query.get('path')
		if path and os.path.isfile(path):
			data = get_image_tags(path,confidence)
			return web.json_response(data)
	return web.json_response({})

autocrop = None
async def api_autocrop(request):
	"""Image autocropping [handled by local+inference.*]"""
	global autocrop
	if not onnx_enabled: return web.Response(status=503,text="onnx runtime missing")
	
	threshold = float(request.rel_url.query.get('threshold', 0.05))
	min_size = float(request.rel_url.query.get('min_size', 0.25))
	scale = int(request.rel_url.query.get('scale', 1))

	if request.match_info['command'] == "run":
		if not request.body_exists:
			return web.json_response({})
		if not autocrop or not autocrop.is_alive():
			print("Start task")
			data = await request.read()
			data = json.loads(data)
			autocrop = Autocrop(data.get("images"), threshold, min_size, scale)
			autocrop.start()
			return web.json_response(autocrop.get_status())
	elif request.match_info['command'] == "run_poll":
		if autocrop:
			status = autocrop.get_status() 
			if not autocrop.is_alive():
				status["images"] = autocrop.image_data
				autocrop = None # final
		else: status = {"run" : False}
		return web.json_response(status)
	return web.json_response({})

async def api_dataset(request):
	"""Dataset operations [handled by dataset_manager.py]"""
	path = None
	data = {}
	if "path" in request.rel_url.query.keys():
		path = request.rel_url.query['path']

	# Move current dataset to datasets folder
	if request.match_info['command'] == "store" and path == "./":
		print("saving",path)
		dataset = get_folder_dataset(path)
		save_dataset(dataset)
	
	# Load dataset into active folder
	elif request.match_info['command'] == "load" and os.path.isdir(path):
		print("loading",path)
		dataset = get_folder_dataset(path)
		load_dataset(dataset)

	elif request.match_info['command'] == "create" and not os.path.isfile("dataset.json"):
		print("creating new dataset")
		if request.body_exists:
			data = await request.read()
			data = json.loads(data)
			create_dataset(data)
		else:
			return web.json_response(data,status=400)

	# Return active+current dataset metadata
	elif request.match_info['command'] == "info":
		print("getting stored dataset info")
		data = dataset_status()

	# Unknown request
	else:
		return web.json_response(data,status=400)
	return web.json_response(data)

async def api_status(request):
	"""Current dataset status [handled by status.py]"""
	data = get_status()
	return web.json_response(data)

crop_status = {"run":False}
async def api_crop_run():
	"""Apply crop. run this with async!! [handled by crop.py]"""
	global crop_status

	with open("dataset.json") as f:
		data = json.load(f)
	if "crop" not in data.keys() or "images" not in data["crop"].keys():
		return

	crop_status = {"run":True,"max":len(data["crop"]["images"])}
	valid = get_step_images(step_list[0])
	crop_status["current"] = 0
	history = []
	for i in data["crop"]["images"]:
		if i["filename"] in [x.get_id() for x in valid]:
			await asyncio.sleep(0.001) # Context switch, don't remove
			filename = crop_image(i, history)
			crop_status["current"] += 1
			if filename:
				history.append(filename)
	print("Crop done!")
	crop_status = {"run":False}

async def api_crop(request):
	"""Image cropping and cropping info [handled by crop.py]"""
	c_warn = []
	if request.match_info['command'] == "run":
		global crop_status
		if not crop_status["run"]:
			print("Start task")
			crop_status = {"run":True}
			asyncio.create_task(api_crop_run())
		return web.json_response(crop_status)
	elif request.match_info['command'] == "run_poll":
		return web.json_response(crop_status)
	data = crop_info()
	data["crop"]["warn"] += c_warn
	return web.json_response(data)

async def api_category(request):
	"""Image sorting and grouping - categories [handled by category.py]"""
	data = {}
	if request.match_info['command'] == "disk":
		data = category_info(disk_only=True)
	else:
		data = category_info()
	return web.json_response(data)

async def api_sort(request):
	"""Image sorting and grouping - sorting [handled by sort.py]"""
	data = {}
	if request.match_info['command'] == "write":
		sort_write()
	else:		
		data = sort_info()
	return web.json_response(data)

async def api_tags(request):
	"""Image tag pruning - tags [handled by tag.py+imgtags.py]"""
	if request.match_info['command'] == "run":
		data = tag_fix(True)
	elif request.match_info['command'] == "img":
		data = imgtag_info()
	elif request.match_info['command'] == "all":
		data = imgtag_all_tags()
	elif request.match_info['command'] == "seq":
		tr = load_dataset_json().get("tags")
		data = tr.get("sequences") if tr else []
	else:
		data = tag_fix()
	return web.json_response(data)

out_status = {"run":False}
async def api_out_run(extension,overwrite,resolution,use_weights):
	"""Process all output images"""
	global out_status

	images = get_step_images(step_list[2],step_list[4])
	out_status = {"run":True,"max":len(images)}

	out_status["current"] = 0
	for i in images:
		finalize_image(i, extension, resolution, overwrite, use_weights)
		await asyncio.sleep(0.001)
		out_status["current"] += 1
	out_status = {"run":False}

async def api_out(request):
	"""write all output images to disk"""
	global out_status
	if request.match_info['command'] == "run":
		extension = ".png"
		if "extension" in request.rel_url.query.keys():
			ext = request.rel_url.query['extension']
			extension = ext if ext in [".png",".jpg"] else ".png"
		overwrite = False
		if "overwrite" in request.rel_url.query.keys():
			overwrite = request.rel_url.query['overwrite'].lower() == "true"
		use_weights = False
		if "weights" in request.rel_url.query.keys():
			use_weights = request.rel_url.query['weights'].lower() == "true"
		resolution = 768
		if "resolution" in request.rel_url.query.keys():
			try:
				resolution = int(request.rel_url.query['resolution'])
			except:
				resolution = 768

		if not out_status["run"]:
			out_status = {"run":True}
			asyncio.create_task(api_out_run(extension,overwrite,resolution,use_weights))
		return web.json_response(out_status)
	elif request.match_info['command'] == "run_poll":
		return web.json_response(out_status)

app.add_routes([web.get('/', index),
				web.get('/favicon.ico', favicon),
				web.get('/{name}', handle),
				web.get('/assets/{name}', handle),
				web.get('/scripts/{name}', handle),
				web.get('/img/{name:.*}', handle_image),
				web.get('/api/inference_check/', inference_check),
				web.get('/api/atag/{command}', api_autotag),
				web.get('/api/acrop/{command}', api_autocrop),
				web.post('/api/acrop/{command}', api_autocrop),
				web.get('/api/dataset/{command}', api_dataset),
				web.post('/api/dataset/{command}', api_dataset),
				web.get('/api/status', api_status),
				web.get('/api/crop/{command}', api_crop),
				web.get('/api/category/{command}', api_category),
				web.get('/api/sort/{command}', api_sort),
				web.post('/api/json/save', api_json_save),
				web.get('/api/tags/{command}', api_tags),
				web.get('/api/out/{command}', api_out),
				])

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Run webui')
	parser.add_argument('-p', '--port', type=int, dest="port", default=8080, help='Port to host webui on')
	parser.add_argument('--autolaunch', action=argparse.BooleanOptionalAction, help='Open webui in default browser')
	parser.add_argument('--listen', action=argparse.BooleanOptionalAction, help='Allow access from LAN (NOT RECOMMENDED)')

	args = parser.parse_args()
	host = "0.0.0.0" if args.listen else "127.0.0.1"

	if args.autolaunch:
		try: # this probably won't work on linux
			os.startfile(f"http://127.0.0.1:{args.port}/")
		except:
			print("Failed to launch default browser")
			pass

	web.run_app(app, host=host, port=args.port)
