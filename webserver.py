#!/usr/bin/python3
# web based UI
import asyncio
from aiohttp import web
import aiohttp
import json
import os
from status import api_json_status
from dataset_manager import api_json_dataset, create_dataset

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

async def api_status(request):
	data = api_json_status()
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

async def api_dataset(request):
	if "path" in request.rel_url.query.keys():
		data = api_json_dataset(request.match_info['command'],request.rel_url.query['path'])
	data = api_json_dataset(request.match_info['command'])
	return web.json_response(data)
	
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
				web.get('/api/status', api_status),
				web.post('/api/dataset/create', api_dataset_create),
				web.get('/api/dataset/{command}', api_dataset),
				web.post('/api/json/save', api_json_save),
				web.get('/{name}', handle)])

if __name__ == '__main__':
	web.run_app(app)
