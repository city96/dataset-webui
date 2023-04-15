from PIL import Image

def get_x_avg(img):
	"""average by row"""
	avg = [0] * img.width
	for x in range(img.width):
		for y in range(img.height):
			avg[x] += sum(img.getpixel((x,y)))/3
	avg = [int(x/img.width) for x in avg]
	return avg

def get_y_avg(img, y_range=None):
	"""average by cols"""
	avg = [0] * img.height
	for x in range(img.width):
		for y in range(img.height):
			if y_range and x not in range(*y_range): continue
			avg[y] += sum(img.getpixel((x,y)))/3
	avg = [int(y/img.height) for y in avg]
	return avg

def get_continuous(val, threshold=0.05):
	"""find index of longest line segment"""
	segs = []
	start = None
	lim = max(val) * threshold
	for i in range(len(val)):
		if val[i] > lim and not start:
			start = i
		elif val[i] < lim and start:
			segs.append((start,i))
			start = None
	if start:
		segs.append((start,len(val)))
	return segs

def expand_range(p1,p2,target_size,max_size):
	"""expand to target size, if possible"""
	size = p2 - p1
	grow_p1 = int((target_size - size) / 2)
	grow_p2 = int((target_size - size) / 2)
	if p1-grow_p1 < 0: grow_p2 += 0-(p1-grow_p1)
	if p2+grow_p2 > max_size: grow_p1 += (p2+grow_p2)-max_size
	p1 = max(p1-grow_p1, 0)
	p2 = min(p2+grow_p2, max_size)
	return (p1, p2)

def shrink_range(p1,p2,target_size,asymmetric=False):
	"""shrink to target size, if possible"""
	size = p2 - p1
	shrink = int((size - target_size) / 2)
	if asymmetric:
		p2 = p2 - shrink*2
	else:
		p1 = p1 + shrink
		p2 = p2 - shrink
	return (p1,p2)

def force_aspect_ratio(x1,x2,y1,y2,x_max,y_max):
	"""resize to square, grow first then shrink"""
	if (y2-y1) > (x2-x1): # [h>w] expand w|x
		x1, x2 = expand_range(x1, x2, (y2-y1), x_max)
	if (x2-x1) > (y2-y1): # [w>h] expand h|y
		y1, y2 = expand_range(y1, y2, (x2-x1), y_max)
	if (x2-x1) > (y2-y1): # [w>h] shrink w|x
		x1, x2 = shrink_range(x1, x2, (y2-y1))
	if (y2-y1) > (x2-x1): # [h>w] shrink h|y
		y1, y2 = shrink_range(y1, y2, (x2-x1), True) # balance top
	return ((x1,x2,y1,y2))

def get_image_regions(img,threshold,min_size,scale=1):
	"""get all crop/bounding boxes belonging to the image"""
	img = img.resize((int(img.width/scale),int(img.height/scale)), Image.LANCZOS)
	x_segs = get_continuous(get_x_avg(img),threshold)
	y_segs = [get_continuous(get_y_avg(img,xs),threshold) for xs in x_segs]
	y_segs = [ys[0] for ys in y_segs if len(ys)>0]
	boxes = [force_aspect_ratio(*x_segs[i],*y_segs[i],img.width,img.height) for i in range(min(len(x_segs),len(y_segs)))]
	boxes = [b for b in boxes if (b[1]-b[0])*(b[3]-b[2]) > img.height*img.width*min_size]
	boxes = [(b[0]*scale,b[1]*scale,b[2]*scale,b[3]*scale) for b in boxes]
	return boxes
