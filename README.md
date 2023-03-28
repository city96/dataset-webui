# LoRA Dataset Webui
This project aims to help with the creation and management of LoRa training datasets.
Scroll down to the bottom of the page for a feature overview.

***This is still in beta - please report any bugs you find***
*Pull requests are welcome. Currently everything is just cobbled together*

Roadmap:
- Fix orphaned images
- Refractor tag management
- Add single-image tag overrides

Known issues:
- No files/folders are ever deleted, leading to clutter/orphaned images
- Cropping step missing overwrite option
- Deleting an enite folder can break the step
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

## Updating
**Clear your browser cache between updates. It tends to leave the old scripts/css loaded**

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
### Dataset manager
- Save / load datasets you're working on
- Avoid having to change training folder, just point your training script at the `5 - out` folder and load the right dataset
- Write notes for yourself

![ui_dataset](https://user-images.githubusercontent.com/125218114/228365966-4e7b34f7-6781-499b-a45c-7cac883fdfec.png)

### Cropping
- Crop images in your browser
- Edit already cropped images
- Duplicate image - crop two separate parts
- Quickly set the cropped area, copy it from the previous image
- Keyboard shortcuts

https://user-images.githubusercontent.com/125218114/228365872-ec57af74-5fb1-43e8-ab0c-ebb2feb3fd00.mp4

### Sorting
- add categories
- quickly sort multiple images, captcha style
- hit detection can be janky

https://user-images.githubusercontent.com/125218114/228366245-de9b590a-0489-422b-8689-e0a262e69561.mp4

#### Auto sorting
- Don't want to do it manually? Set the tags and sort automatically.

https://user-images.githubusercontent.com/125218114/228366461-3da9085a-6ec7-40f6-b746-773b168fe546.mp4

### Tagging
#### CPU-only autotagger
- A bit slow but does not take any vram, doesn't influence training.
- The output isn't realtime, I think it can do about 1 image/sec on my 11gen i5

https://user-images.githubusercontent.com/125218114/228366774-5609c1b5-28b6-4274-89b0-8296144b7f2a.mp4

#### Tag pruning
- Prune useless tags from the autotagger
- Normalize tags
- Quickly blackist/whitelist tags
- Replace tags on all images
- Edit rules, test the effects

![ui_tag_pruning](https://user-images.githubusercontent.com/125218114/228366967-7d9f94d7-199d-483f-9f89-13677068f837.png)

### Output
- Scale images to required training resolution

![ui_output](https://user-images.githubusercontent.com/125218114/228367042-2a39649e-83dc-49e9-a736-87f784e09f4f.png)
