#!/usr/bin/python3
# web based UI
import asyncio
from aiohttp import web
import aiohttp
from check import api_json_check


app = web.Application()

async def handle(request):
    return web.Response(text="api")

async def api_check(request):
	data = api_json_check()
	return web.json_response(data)

app.add_routes([web.get('/', handle),
                web.get('/api/check', api_check),
                web.get('/{name}', handle)])

if __name__ == '__main__':
	web.run_app(app)
