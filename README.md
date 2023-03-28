# LoRA Dataset Webui
This project aims to help with the creation and management of LoRa training datasets.
Scroll down to the bottom of the page for a feature overview.

*Pull requests are welcome. Currently everything is just cobbled together*

Roadmap:
- Fix orphaned images
- Refractor tag management
- Add single-image tag overrides

Known issues:
- No files/folders are ever deleted, leading to clutter/orphaned images
- Webui scrolls by random amount on first button click

## Getting started
(optional) create a venv first:
```
python -m venv venv
venv\Scripts\activate
```

install the requirements:
```
pip install -r requirements.txt
```

start either by running `start.bat` or manually using:
```
python webserver.py
```
(see `python webserver.py --help` for launch arguments)

Access the webui on the following URL: http://127.0.0.1:8080/

### download-dependencies.py
Running this script is recommended to get all features of the webui.

**using start.bat already downloads all dependencies by default**

It will gives you the option to download the following files:
- `danbooru-tags.json` and `gelbooru-tags.json` from github gist or catbox.moe.
	- You also have the option to scrape the tags from the site directly.
- `cropper.js` and `cropper.css` from Cloudflare/cdnjs.

## Folder structure

The folders created are meant to be used as follows:
- `0 - raw` - raw images from the internet / screenshots
- `1 - cropped` - cropped images (1:1 aspect ratio)
- `2 - sorted` - images grouped by quality / topic / etc
- `3 - tagged` - `.txt` or `.json` files containing autotagger output
- `4 - fixed` - pruned tags in `.txt` format.
- `5 - out` - scaled down images and pruned tags - point your training script here
- `datasets` - all your datasets are saved here

## Features:
### 
