#!/usr/bin/python3
# web based UI
import argparse
import asyncio
from aiohttp import web
import aiohttp
import json
import os
from status import get_status
from save import save_json
from crop import crop_info
from category import category_info
from sort import sort_info, sort_write
from dataset_manager import create_dataset, save_dataset, load_dataset, get_folder_dataset, dataset_status
from common import step_list
from fix_tags import tag_info, tag_run

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
	from crop import crop_image
	from status import get_step_images

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
	if request.match_info['command'] == "run":
		data = tag_run(True,True)
	else:
		data = tag_info()
	return web.json_response(data)

app.add_routes([web.get('/', index),
				web.get('/favicon.ico', favicon),
				web.get('/{name}', handle),
				web.get('/assets/{name}', handle),
				web.get('/scripts/{name}', handle),
				web.get('/img/{name:.*}', handle_image),
				web.get('/api/dataset/{command}', api_dataset),
				web.post('/api/dataset/{command}', api_dataset),
				web.get('/api/status', api_status),
				web.get('/api/crop/{command}', api_crop),
				web.get('/api/category/{command}', api_category),
				web.get('/api/sort/{command}', api_sort),
				web.post('/api/json/save', api_json_save),
				web.get('/api/tags/{command}', api_tags),
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
