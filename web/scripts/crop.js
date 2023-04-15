function crop_reset() {
	if (crop) {
		crop.destroy()
	}
	crop = null
	crop_data = null
	crop_disable_shortcuts()
	document.getElementById("crop-img-div").innerHTML = ""

	document.getElementById("c_warn").innerHTML = ""
	document.getElementById("c_status").innerHTML = ""
	document.getElementById("c_filename").innerHTML = ""
	document.getElementById("c_status_prev").innerHTML = ""
	document.getElementById("crop-table").innerHTML = ""
}

function crop_slider() {
	let target = parseInt(document.getElementById("c_slider").value)
	if (target < 0 || target >= crop_data["images"].length) {
		return
	}
	crop_data["current"] = target
	crop_update_current()
}

function crop_update_slider() {
	document.getElementById("c_slider").max = crop_data["images"].length-1
	document.getElementById("c_slider").value = crop_data["current"]
}

function crop_duplicate() {
	lock("crop-div")
	let current = crop_data["images"][crop_data["current"]]
	let target = JSON.parse(JSON.stringify(current)) // copy
	target["duplicate"] = true
	target["on_disk"] = false
	target["ignored"] = false
	delete target["crop_data"]
	crop_data["images"].splice(crop_data["current"]+1, 0, target);
	crop_status()
	document.getElementById("c_status").innerHTML = "Duplicated as next image!"
	document.getElementById("c_status").style.color = "orange"
}

function crop_enable_shortcuts() {
	console.log("crop/shortcuts on")
	document.getElementById("c_shortcuts").style.display = "block";
	document.getElementById("c_enable_shortcuts").disabled = true;
	document.getElementById("c_disable_shortcuts").disabled = false;
	document.addEventListener('keyup', crop_shortcuts, false);
	document.activeElement.blur();
}

function crop_disable_shortcuts() {
	console.log("crop/shortcuts off")
	document.getElementById("c_shortcuts").style.display = "none";
	document.getElementById("c_enable_shortcuts").disabled = false;
	document.getElementById("c_disable_shortcuts").disabled = true;
	document.removeEventListener('keyup', crop_shortcuts, false);
}

function crop_auto_next_buttons() {
	let state = document.getElementById("c_next").checked
	let ignore = document.getElementById("c_ignore")
	let crop = document.getElementById("c_crop")
	if (state) {
		ignore.innerHTML = "Ignore+Next"
		crop.innerHTML = "Crop+Next"
		ignore.style.backgroundImage = "url('assets/c_ignore_next.png')"
		crop.style.backgroundImage = "url('assets/c_crop_next.png')"
	} else {
		ignore.innerHTML = "Ignore"
		crop.innerHTML = "Set crop"
		ignore.style.backgroundImage = "url('assets/c_ignore.png')"
		crop.style.backgroundImage = "url('assets/c_crop.png')"
	}
}

function crop_mask_prev() {
	if (crop_data["current"] == 0) {
		return
	}
	crop.setData(crop_data["images"][crop_data["current"]-1]["crop_data"])
}

function crop_mask_fill() {
	let crop_data = crop.getData()
	if (crop.image.naturalHeight  > crop.image.naturalWidth) {
		crop_data.width = crop.image.naturalWidth
		crop_data.height = crop.image.naturalWidth
		crop_data.x = 0
		if (crop_data.y > (crop.image.naturalHeight-crop.image.naturalWidth)) {
			crop_data.y = crop.image.naturalHeight-crop.image.naturalWidth
		}
	} else {
		crop_data.width = crop.image.naturalHeight
		crop_data.height = crop.image.naturalHeight
		crop_data.y = 0
		if (crop_data.x > (crop.image.naturalWidth-crop.image.naturalHeight)) {
			crop_data.x = crop.image.naturalWidth-crop.image.naturalHeight
		}
	}
	crop.setData(crop_data)
}
function crop_mask_half() {
	let crop_data = crop.getData()
	if (crop.image.naturalHeight  > crop.image.naturalWidth) {
		crop_data.width = crop.image.naturalWidth / 2
		crop_data.height = crop.image.naturalWidth /2
	} else {
		crop_data.width = crop.image.naturalHeight / 2
		crop_data.height = crop.image.naturalHeight /2
	}
	crop.setData(crop_data)
}

function crop_shortcuts(e) {
	// console.log(e)
	if (e.key === 'z') { crop_prev_image() //next
	} else if (e.key === 'x') { crop_next_image(false,true) // ignore+next
	} else if (e.key === 'c') { crop_next_image(true) // crop+next
	} else if (e.key === 'v') { crop_next_image() //next
	} else if (e.key === 's') { crop_mask_prev() // mask from prev
	} else if (e.key === 'd') { crop_mask_half() // mask half
	} else if (e.key === 'f') { crop_mask_fill() // mask fill
	} else {
		console.log(e)
	}
}

var crop_data
async function crop_json_load() {
	let data = await fetch("/api/crop/info");
	data = await data.json()
	crop_data = data["crop"]
	if (crop_data === undefined || crop_data.images === undefined || crop_data.images.length == 0) {
		disable_module("crop-div", "Nothing to load from disk")
		disable_module("crop-write", "Nothing to load from disk")
		unlock()
		return
	}
	if (crop_data["current"] === undefined) {
		crop_data["current"] = 0
	}
	document.getElementById("c_warn").innerHTML = data["crop"]["warn"]
	crop_status(true)
	unlock()
}

async function crop_json_save() {
	console.log("Save crop/json")
	save_lock()

	let data = {}
	data["crop"] = crop_data

	await fetch('/api/json/save', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify(data)
	})
	save_lock(false)
	crop_json_load() // verify
}

function crop_update_status_text(target,data) {
	if (data["crop_data"] === undefined && !data["ignored"] && !data["on_disk"]) {
		target.innerHTML = "Unknown/Not cropped"
		target.style.color = "gray"
	} else if (!(data["crop_data"] === undefined) && !data["ignored"] && !data["auto"]) {
		target.innerHTML = "Cropped"
		target.style.color = "green"
	} else if (data["ignored"] == true) {
		target.innerHTML = "Ignored"
		target.style.color = "red"
	} else if (data["auto"] == true) {
		target.innerHTML = "Auto"
		target.style.color = "aqua"
	} else if (data["on_disk"]) {
		target.innerHTML = "On-disk/Cropped externally"
		target.style.color = "blue"
	} else {
		target.innerHTML = "???"
		target.style.color = "orange"
	}
}

async function crop_update_current() {
	let current = crop_data["images"][crop_data["current"]]
	crop_update_status_text(document.getElementById("c_status"),current)
	if (current.duplicate) {
		document.getElementById("c_filename").innerHTML = "Duplicate of " + crop_data["images"][crop_data["current"]].filename
	} else {
		document.getElementById("c_filename").innerHTML = crop_data["images"][crop_data["current"]].filename
	}

	if (crop.image == undefined) {
		return
	}
	
	let old_url = new URL(crop.image.src)
	let url = "/img/0 - raw/" + current["filename"]
	if (decodeURIComponent(old_url.pathname) != url) {
		console.log("replace", crop_data["current"])
		crop.replace(url)
	}
	
	if (current["crop_data"] === undefined) {
		if (!document.getElementById("c_copy").checked) { 
			return
		}
		// find previous good
		let data = null 
		for (let i = crop_data["current"]; i >= 0; i--) {
			data = crop_data["images"][i]["crop_data"]
			if (data) {
				break
			}
		}
		if(!data) {
			return
		}
		await new Promise(r => setTimeout(r, 50));
		crop.setData(data)
		return
	}
	await new Promise(r => setTimeout(r, 50)); // why ??
	crop.setData(current["crop_data"])
}

function crop_status_current(row=document.getElementById("crop_table_current"),name="Current") {
	let c_name = row.insertCell(0)
	c_name.innerHTML = name
	
	let total = 0
	let cropped = 0
	let ignored = 0
	let unknown = 0
	let on_disk = 0
	for (const image of crop_data["images"]) {
		total++
		if (!(image["crop_data"] === undefined)) {
			if (image["ignored"]) {
				ignored++
			} else {
				cropped++
				if (image["on_disk"]) {
					on_disk++
				}
			}
		} else {
			if (image["ignored"]) {
				ignored++
			} else if (image["on_disk"]) {
				on_disk++
			} else {
				unknown++
			}
		}
	}
	
	let c_total = row.insertCell(1)
	c_total.innerHTML = total

	let c_missing = row.insertCell(2)
	c_missing.innerHTML = crop_data["missing"].length

	let c_unknown = row.insertCell(3)
	c_unknown.innerHTML = unknown

	let c_ignored = row.insertCell(4)
	c_ignored.innerHTML = ignored
	
	let c_cropped = row.insertCell(5)
	c_cropped.innerHTML = cropped

	let c_on_disk = row.insertCell(6)
	c_on_disk.innerHTML = on_disk
}

function crop_status(reload=false){
	let table = document.getElementById("crop-table")
	if (reload) {
		table.innerHTML = "";
		crop_status_current(table.insertRow(),"Saved")
		let current = table.insertRow();
		current.setAttribute('id', 'crop_table_current');
		crop_status_current(current)
	} else {
		let current = document.getElementById("crop_table_current")
		current.innerHTML = ""
		crop_status_current(current)
	}
	crop_update_slider()
}

function crop_next_image(set_crop=false, set_ignore=false) {
	if (set_crop) {
		crop_data["images"][crop_data["current"]]["crop_data"] = crop.getData(true)
		crop_data["images"][crop_data["current"]]["ignored"] = false
		crop_data["images"][crop_data["current"]]["auto"] = false
	}
	if (set_ignore) {
		crop_data["images"][crop_data["current"]]["ignored"] = true
	}

	if (set_crop || set_ignore) { // unsaved changes
		lock("crop-div")
		if (!document.getElementById("c_next").checked) { // not auto next
			crop_update_status_text(document.getElementById("c_status"),crop_data["images"][crop_data["current"]])
			return
		}
	}

	crop_update_status_text(document.getElementById("c_status_prev"),crop_data["images"][crop_data["current"]])
	
	if (document.getElementById("c_skip").checked) {
		let i = crop_data["current"]
		let loop = false
		while(true) {
			i++
			if (i >= crop_data["images"].length) {
				if (loop) {
					document.getElementById("c_status").innerHTML = "No more images left!"
					document.getElementById("c_status").style.color = "orange"
					return
				} else {
					loop = true
					i = 0
				}
			}
			if (!crop_data["images"][i]["ignored"] && !crop_data["images"][i]["on_disk"] && crop_data["images"][i]["crop_data"] === undefined) {
				crop_data["current"] = i
				console.log(i)
				break
			}
		}
	} else {
		if ((crop_data["current"]+1) >= crop_data["images"].length) {
			document.getElementById("c_status").innerHTML = "Last image reached!"
			document.getElementById("c_status").style.color = "orange"
			return
		}
		crop_data["current"]++
	}
	crop_update_current()
	crop_status()
}

function crop_first_image() {
	crop_data["current"] = 0
	crop_update_current()
	crop_status()
}

function crop_prev_image() {
	if ((crop_data["current"]-1) < 0) {
		return
	}
	crop_update_status_text(document.getElementById("c_status_prev"),crop_data["images"][crop_data["current"]])
	crop_data["current"]--
	crop_update_current()
	crop_status()
}

var crop
var crop_index
async function crop_init() {
	await crop_json_load()
	if (!crop_data || !crop_data.images || crop_data.images.length == 0) {
		document.getElementById("c_apply").disabled = true
		if(crop_data.warn) {
			disable_module("crop-div", crop_data.warn)
			disable_module("crop-write", crop_data.warn)	
		} else {
			disable_module("crop-div", "Nothing to load from disk")
			disable_module("crop-write", "Nothing to load from disk")
		}
		crop_reset()
		return
	} else {
		document.getElementById("c_apply").disabled = false
		enable_module("crop-div")
		enable_module("crop-write")
	}
	if (crop) { // already init
		return 
	}

	crop_disable_shortcuts()

	let link = document.createElement( "link" )
	link.href = "cropper.css"
	link.type = "text/css"
	link.rel = "stylesheet"
	document.head.appendChild(link);

	await import('/cropper.js');

	let div = document.getElementById("crop-img-div")
	let image = document.createElement("img")
	image.setAttribute('id', 'crop-img');
	div.appendChild(image)

	image.src = "/img/0 - raw/" + crop_data["images"][crop_data["current"]]["filename"]
	let options = {
		"viewMode" : 1,
		"aspectRatio" : 1,
		"zoomable" : false,
		"toggleDragModeOnDblclick" : false,
		"data" : crop_data["images"][crop_data["current"]]["crop_data"],
	}
	crop = new Cropper(image, options)
	crop_update_current()
}

async function crop_apply() {
	console.log("run")
	// lock
	document.getElementById("c_apply").disabled = true
	lock('crop-write')
	save_lock()
	
	let perc = document.getElementById("c_perc")
	let data = await fetch("/api/crop/run");

	data = await data.json()
	while (data["run"]) {
		data = await fetch("/api/crop/run_poll");
		data = await data.json()
		if (data["max"]) {
			console.log("poll update",data["current"],data["max"])
			perc.max = data["max"]
			perc.value = data["current"]
		} else {
			perc.max = 1
			perc.value = 1
		}
		await new Promise(r => setTimeout(r, 500));
	}
	console.log("asdasd")
	perc.max = 1
	perc.value = 0
	console.log(data);
	
	// lock
	save_lock(false)
	unlock()
	document.getElementById("c_apply").disabled = false
	
	// propagate
	page_update(false)
}

function crop_revert() {
	let c = confirm("Are you sure you want to revert all changes?");
	if (!c) { return };
	crop_reset()
	crop_init()
}

async function crop_clear() {
	let c = confirm("Are you sure you want to clear all crop data? This is irreversible and will set all images to 'uncropped'");
	if (!c) { return };
	crop_data = {
		images : [],
		missing : [],
	}
	crop_json_save()
	await new Promise(r => setTimeout(r, 500));
	crop_reset()
	crop_init()
}