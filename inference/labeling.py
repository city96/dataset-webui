import os
from PIL import Image
from .check import onnx_enabled, onnx_providers

if onnx_enabled:
	import numpy as np
	from huggingface_hub import hf_hub_download
	from onnxruntime import InferenceSession

interrogator_session = None
interrogator_name = None
interrogator_tags = None

interrogator_repo_names = {
	"wd-v1-4-vit-tagger-v2" : "SmilingWolf/wd-v1-4-vit-tagger-v2",
	"wd-v1-4-moat-tagger-v2" : "SmilingWolf/wd-v1-4-moat-tagger-v2",
	"wd-v1-4-swinv2-tagger-v2" : "SmilingWolf/wd-v1-4-swinv2-tagger-v2",
	"wd-v1-4-convnext-tagger-v2" : "SmilingWolf/wd-v1-4-convnext-tagger-v2",
	"wd-v1-4-convnextv2-tagger-v2" : "SmilingWolf/wd-v1-4-convnextv2-tagger-v2",
}

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

def init_interrogator(providers, repo):
	model_path = str(hf_hub_download(repo_id=repo, filename="model.onnx"))
	session = InferenceSession(str(model_path), providers=providers)
	tags_path = str(hf_hub_download(repo_id=repo, filename="selected_tags.csv"))
	tags = column_from_csv(tags_path,"name")
	tags = [x.replace('_', ' ') for x in tags] # underscore fix]
	return (session, tags)

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

def label_image(image_path, interrogator=None):
	if not onnx_enabled: return
	global onnx_providers

	global interrogator_session
	global interrogator_name
	global interrogator_tags
	global interrogator_repo_names

	if not interrogator: interrogator = interrogator_repo_names[0]
	if interrogator_name != interrogator:
		if interrogator_session: interrogator_session = None
		if interrogator_tags: interrogator_tags = None
	if not interrogator_session:
		repo = interrogator_repo_names.get(interrogator)
		if not repo: return
		interrogator_name = interrogator
		interrogator_session, interrogator_tags = init_interrogator(onnx_providers, repo)

	img = Image.open(image_path)
	labels = interrogate(interrogator_session, interrogator_tags, img)
	return labels
