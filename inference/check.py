try:
	import numpy as np
	from huggingface_hub import hf_hub_download
	from onnxruntime import InferenceSession
	onnx_enabled = True
except ImportError:
	print("tagger failed to initialize - missing packages")
	onnx_enabled = False
