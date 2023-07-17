def check_imports():
	try:
		import numpy as np
		from huggingface_hub import hf_hub_download
		from onnxruntime import InferenceSession
		return True
	except ImportError:
		print("ONNX failed to initialize - missing packages")
		print("pip install numpy onnxruntime huggingface-hub")
		return False

def get_onnx_providers(cuda_enabled=True):
	# https://onnxruntime.ai/docs/execution-providers/
	from onnxruntime import get_device
	if get_device() == "GPU" and cuda_enabled:
		print("ONNX is using CUDA backend.")
		return ["CUDAExecutionProvider", "CPUExecutionProvider"]
	else:
		print("ONNX is using CPU backend.")
		return ["CPUExecutionProvider"]

onnx_enabled = check_imports()
onnx_providers = get_onnx_providers() if onnx_enabled else []
