#!/usr/bin/python3
# random functions that are used in multiple scripts

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