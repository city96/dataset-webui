#!/usr/bin/python3
# auto download tags from api - helper script, needs fixing
# problems:
#  - ported over from other project
#  - only supports danbooru
#  - doesn't have to be recursive (unneeded os.walk())

from urllib.request import Request, urlopen
import json
import os

if input("warning! Edit python file before running. run? [y/N] ").lower() != 'y':
	exit()

src_dir = "../3 - tagged"

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
url = "https://gelbooru.com/index.php?page=dapi&json=1&s=post&q=index&limit=1&tags=md5:{}"

hash = []
for dirpath, subdirs, files in os.walk(src_dir):
	for f in files:
		if len(f.split(".")[0]) == 32:
			h = (f.split(".")[0])
			txt = os.path.join(dirpath,(h+".txt"))
			if not os.path.isfile(txt):
				try:
					request = Request(url.format(h),headers={'User-Agent': user_agent})
					page = urlopen(request).read()
					data = json.loads(page)
					
					with open(txt,"w") as file:
						file.write(data[0]["tags"])
				except:
					print(h)
