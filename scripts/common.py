import os

step_list = [
	"0 - raw",
	"1 - cropped",
	"2 - sorted",
	"3 - tagged",
	"4 - fixed",
	"5 - out",
]

rating_list = [
	"general",
	"sensitive",
	"questionable",
	"explicit",
]

version = 1.1 # current dataset version
dataset_folder = "datasets"

class Image:
	"""class to store image attributes"""
	category = None
	filename = None
	path = None # full path to file
	txt = None # full path to file
	tags = []
	rating = None
	def __int__(self):
		return len(self.tags)
	def __str__(self):
		return f"{self.filename}"
	def __repr__(self):
		return f"{self.filename}"
	def get_id(self):
		uid = self.path
		for i in step_list:
			if uid.startswith(i):
				uid = uid.lstrip(i)
				uid = uid.lstrip(os.path.sep) # \\
				break
		return uid
	def get_step_path(self, step):
		if step in step_list:
			folder = step
		elif type(step) == int and step < len(step_list):
			folder = step_list[step]
		else:
			print(f"external path '{step}'")
			folder = step
	
		old = self.path
		new = None
		for i in step_list:
			if old.startswith(i):
				new = old.lstrip(i)
				new = new.lstrip(os.path.sep) # \\
				break
		if not new: return None
		path = os.path.join(folder,new)
		return path

class Tag:
	"""class to store tag attributes"""
	name = None
	weight = 1.0
	position = 10
	confidence = 1.0
	def __str__(self):
		return f"{self.name}"
	def __repr__(self):
		return f"{self.name}"
	def __lt__(self, other):
         return self.position < other.position

class Category:
	"""class to store categories"""
	def __init__(self,name,weight=1):
		self.name = name
		self.weight = weight
	def __str__(self):
		return f"{self.weight}_{self.name}"
	def __repr__(self):
		return f"{self.weight}_{self.name}"
	def __lt__(self, other):
         return self.weight < other.weight
