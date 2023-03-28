import os
from PIL import Image
try:
	import numpy as np
	from huggingface_hub import hf_hub_download
	from onnxruntime import InferenceSession
	tagger_enabled = True
except ImportError:
	print("tagger failed to initialize - missing packages")
	tagger_enabled = False

interrogator_session = None
interrogator_tags = None

def column_from_csv(file,column):
	"""replaces pandas read_csv to reduce number of dependencies"""
	with open(file) as f:
		rows = f.readlines()
	col = 0
	for i in rows.pop(0).split(","):
		if i.strip() == column:
			break
		col += 1
	out = []
	for line in rows:
		fields = line.split(",")
		if len(fields) <= col: continue
		field = fields[col].strip()
		if field: out.append(field)
	return out

def init_interrogator(repo="SmilingWolf/wd-v1-4-vit-tagger-v2"):
	providers = ["CPUExecutionProvider"] # https://onnxruntime.ai/docs/execution-providers/
	model_path = str(hf_hub_download(repo_id=repo, filename="model.onnx"))
	session = InferenceSession(str(model_path), providers=providers)
	return session

def init_interrogator_tags(repo="SmilingWolf/wd-v1-4-vit-tagger-v2"):
	tags_path = str(hf_hub_download(repo_id=repo, filename="selected_tags.csv"))
	tags = column_from_csv(tags_path,"name")
	tags = [x.replace('_', ' ') for x in tags] # underscore fix]
	return tags

def interrogate(session, tags, image):
	width, height = session.get_inputs()[0].shape[1:3] # [1, 448, 448, 3]
	image = image.resize((width,height), Image.LANCZOS).convert('RGB')
	image = np.asarray(image)
	image = image[:, :, ::-1] # PIL RGB to OpenCV BGR
	image = image.astype(np.float32)
	image = np.expand_dims(image, 0)

	input_name = session.get_inputs()[0].name
	label_name = session.get_outputs()[0].name
	confidents = session.run([label_name], {input_name: image})[0]

	conf = confidents.tolist()[0]
	out = {tags[i]:conf[i] for i in range(len(tags))}
	return out

def get_image_tags(image_path, threshold=0.35):
	if not tagger_enabled:
		return

	global interrogator_session
	if not interrogator_session:
		interrogator_session = init_interrogator()

	global interrogator_tags
	if not interrogator_tags:
		interrogator_tags = init_interrogator_tags()

	img = Image.open(image_path)
	tags = interrogate(interrogator_session, interrogator_tags, img)
	rating = ["general", "sensitive", "questionable", "explicit"] # remove / filter these
	out = {name.replace("_"," "):conf for name, conf in tags.items() if conf >= threshold and name not in rating}
	return out
