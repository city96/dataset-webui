#!/usr/bin/python3
# web based UI
import asyncio
from aiohttp import web
import aiohttp
import json
import os
from status import get_status
from dataset_manager import create_dataset, save_dataset, load_dataset, get_folder_dataset, dataset_status
from common import step_list
# from fix_tags import run

app = web.Application()

async def index(request):
	return web.FileResponse('web/index.html')

async def favicon(request):
	return web.FileResponse('web/favicon.ico')

async def handle(request):
	path = os.path.join("web", str(request.url.relative())[1:])
	
	if os.path.isfile(path) and os.path.splitext(path)[1] in [".html",".css",".js"]:
		return web.FileResponse(path)
	else:
		return web.Response(status=404,text="404")

async def handle_image(request):
	path = str(request.path)[5:]
	print(path)
	if os.path.isfile(path) and any(path.startswith(x) for x in step_list):
		return web.FileResponse(path)
	else:
		return web.Response(status=404,text="404")

# Get json + folder status
async def api_get_status(request):
	data = get_status()
	return web.json_response(data)

async def api_json_save(request):
	if request.body_exists:
		data = await request.read()
		data = json.loads(data)
		strdata = json.dumps(data, indent=2)
		print(strdata)
		# sanity check
		if len(data["meta"]["name"]) > 0 and len(data["tags"]) > 0:
			with open("dataset.json", "w") as f:
				f.write(strdata)
	else:
		print("no data")
	return web.json_response({})

# 
async def api_dataset(request):
	print(request)
	path = None
	data = {}
	if "path" in request.rel_url.query.keys():
		path = request.rel_url.query['path']

	if request.match_info['command'] == "save" and path == "./":
		print("saving",path)
		dataset = get_folder_dataset(path)
		save_dataset(dataset)
	elif request.match_info['command'] == "load" and os.path.isdir(path):
		print("loading",path)
		dataset = get_folder_dataset(path)
		load_dataset(dataset)

	data = dataset_status() # always re-fetch status after save.
	return web.json_response(data)

async def api_fix_tags(request):
	# run(True,True)
	return web.json_response({})

async def api_dataset_create(request):
	if os.path.isfile("dataset.json"): return web.json_response({"no"}) # fuck javascript triggering twice
	if request.body_exists:
		data = await request.read()
		print(data)
		data = json.loads(data)
		create_dataset(data)
	else:
		print("no data")
	return web.json_response({})

app.add_routes([web.get('/', index),
				web.get('/favicon.ico', favicon),
				web.get('/api/status', api_get_status),
				web.post('/api/dataset/create', api_dataset_create),
				web.get('/api/dataset/{command}', api_dataset),
				web.post('/api/json/save', api_json_save),
				web.get('/api/tags/run', api_fix_tags),
				web.get('/img/{name:.*}', handle_image),
				web.get('/{name}', handle)])

if __name__ == '__main__':
	web.run_app(app)
