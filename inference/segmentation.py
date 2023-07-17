import os
from PIL import Image
from .check import onnx_enabled, onnx_providers

if onnx_enabled:
	import numpy as np
	from huggingface_hub import hf_hub_download
	from onnxruntime import InferenceSession

interrogator_session = None

def init_interrogator(providers, repo="skytnt/anime-seg"):
	model_path = str(hf_hub_download(repo_id=repo, filename="isnetis.onnx"))
	session = InferenceSession(str(model_path), providers=providers)
	return session

def interrogate(session, input_image, out_size):
	input_image.thumbnail((1024,1024))
	iw = int((1024-input_image.width)/2)
	ih = int((1024-input_image.height)/2)
	image = Image.new('RGB',size=(1024,1024),color=(0,0,0))
	image.paste(input_image, (iw,ih))

	image = np.array(image)
	image = image[:, :, ::-1] # PIL RGB to OpenCV BGR
	image = image / 255
	image = image.transpose((2, 1, 0))
	image = image.astype(np.float32)
	image = np.expand_dims(image, 0)

	input_name = session.get_inputs()[0].name
	label_name = session.get_outputs()[0].name
	mask = session.run([label_name], {input_name: image})[0]
	
	mask = mask.repeat(3, 1)
	mask = np.squeeze(mask, 0)
	mask = mask.transpose((2, 1, 0))
	mask = mask * 255
	mask = mask.astype(np.uint8)
	mask = Image.fromarray(mask)
	mask = mask.crop((iw,ih,1024-iw,1024-ih))
	mask = mask.resize(out_size, Image.LANCZOS).convert('RGB')
	return mask

def segment_image(image_path):
	if not onnx_enabled: return
	global onnx_providers
	global interrogator_session
	if not interrogator_session:
		interrogator_session = init_interrogator(onnx_providers)
	img = Image.open(image_path)
	out = interrogate(interrogator_session, img, img.size)
	return out
