import os
import argparse
from PIL import Image
from .common import step_list
from .loader import load_dataset_json, str_to_tag_list, get_step_images
from .tags import popular_tags

TRAIN_EPOCHS = 15
TRAIN_BATCH = 2
WORKERS = 12
NET_DIM = 128
NET_ALPHA = NET_DIM/2
SAVE_FOLDER = r"%UserProfile%\Desktop\LoRA"

# common options
sda = [
	'--shuffle_caption',
	'--caption_extension ".txt"',
	'--seed 101010',
	f'--save_every_n_epochs {int(TRAIN_EPOCHS/3)}',
	f'--train_data_dir "{os.path.abspath(step_list[5])}"'
]
# performance
sda += [
	'--xformers',
	'--cache_latents',
	'--save_precision fp16',
	'--mixed_precision bf16',
	'--clip_skip 2',
	f'--max_data_loader_n_workers {WORKERS}',
	f'--persistent_data_loader_workers',
]
# network
sda += [
	'--network_module "networks.lora"',
	f'--network_dim {NET_DIM}',
	f'--network_alpha {NET_ALPHA}',
	'--lr_scheduler cosine_with_restarts',
	'--lr_scheduler_num_cycles 1', # same as cosine
	'--optimizer_type AdamW8bit',
	'--optimizer_args weight_decay=0.1 betas=0.9,0.99',
	'--learning_rate 0.0001',
	'--max_grad_norm 1.0',
]

def meta():
	data = load_dataset_json()
	name = data['meta'].get('name','untitled').replace(' ','_')
	trig = data['tags']['rules'].get('triggerword','')
	return [
		f'--output_name "{name}"',
		f'--log_prefix "{name}"',
		f'--training_comment "{trig}"',
		f'--keep_tokens {len(str_to_tag_list(trig))}',
	]

def sample_prompt():
	sample_prompt = os.path.join(step_list[5],"sample_prompt.txt")
	if os.path.isfile(sample_prompt):
		return [
			'--sample_every_n_epochs 1',
			'--sample_sampler euler_a',
			f'--sample_prompts "{os.path.abspath(sample_prompt)}"',
		]
	return []

def save_dir():
	global SAVE_FOLDER
	SAVE_FOLDER = os.path.expandvars(SAVE_FOLDER)
	if not os.path.isdir(SAVE_FOLDER):
		os.mkdir(SAVE_FOLDER)
	return [
		f'--output_dir "{os.path.abspath(SAVE_FOLDER)}"',
		f'--logging_dir "{os.path.abspath(SAVE_FOLDER)}"',
	]

def resolution():
	width,height = Image.open(get_step_images(step_list[5])[0].path).size
	if height not in [512,576,768,960]:
		print("res invalid")
		return []
	if width == height:
		return [f"--resolution {height}"]
	else:
		return [f"--resolution \"{width},{height}\"",]

def counts():
	global TRAIN_EPOCHS
	global TRAIN_BATCH
	# images = get_step_images(step_list[5])
	# steps = sum([i.category.weight for i in images])
	return [
		f"--train_batch_size {TRAIN_BATCH}",
		f"--max_train_epochs {TRAIN_EPOCHS}",
		f"--dataset_repeats 1",
	]

def caption_weights():
	weight = False
	for i in get_step_images(step_list[5]):
		if any([x.weight != 1.0 for x in i.tags]):
			weight = True
			break
	if weight:
		return ['--weighted_captions']
	else:
		return []

def get_sd_scripts_command(args):
	args += meta()
	args += counts()
	args += save_dir()
	args += resolution()
	args += sample_prompt()
	args += caption_weights()
	return f"accelerate launch train_network.py {' '.join(args)}"

def create_sample_prompt(max_tags=12):
	popular = popular_tags(get_step_images(step_list[5]))
	tags = list(popular.keys())[:max_tags]
	spf = os.path.join(step_list[5],"sample_prompt.txt")
	print(f"Writing {len(tags)} tags+settings to '{spf}'")
	prompt = f"masterpiece, best quality, {', '.join(tags)} "
	prompt += "--n nsfw, lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name " #NAI default
	
	width,height = Image.open(get_step_images(step_list[5])[0].path).size
	prompt += f"--w {width} --h {height} "
	prompt += f"--d 3470720151 " # seed
	prompt += f"--l 10 --s 35 "
	
	print(prompt)
	with open(spf, "w") as f:
		f.write(prompt)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Helper script for kohya-ss/sd-scripts')
	parser.add_argument('--prompt', action="store_true", help=f"Write 'sample_prompt.txt' to '{step_list[5]}'")
	parser.add_argument('--command', action="store_true", help=f"Print training command and exit")
	parser.add_argument('--model', type=str, dest="model", help=f"Model path")
	args = parser.parse_args()
	
	if args.prompt:
		create_sample_prompt()
	elif args.command:
		cmd = get_sd_scripts_command(sda)
		cmd += f" --pretrained_model_name_or_path \"{os.path.abspath(args.model) if args.model else '[MODEL PATH]'}\""
		print(f'\n{cmd}\n')
	else:
		print("See 'sd_scripts.py --help' for usage")
