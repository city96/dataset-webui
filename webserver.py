#!/usr/bin/python3
# web based UI
import asyncio
from aiohttp import web
import aiohttp
import os
from check import api_json_check
from dataset_manager import api_json_dataset

app = web.Application()

async def index(request):
	return web.FileResponse('web/index.html')

async def handle(request):
	path = os.path.join("web", str(request.url.relative())[1:])
	
	if os.path.isfile(path) and os.path.splitext(path)[1] in [".html",".css",".js"]:
		return web.FileResponse(path)
	else:
		return web.Response(status=404,text="404")

async def api_check(request):
	data = api_json_check()
	return web.json_response(data)

async def api_dataset(request):
	data = api_json_dataset("get_all")
	return web.json_response(data)

app.add_routes([web.get('/', index),
				web.get('/api/check', api_check),
				web.get('/api/dataset', api_dataset),
				web.get('/{name}', handle)])

if __name__ == '__main__':
	web.run_app(app)