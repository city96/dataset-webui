function crop_disabled(state) {
	console.log("crop")
	console.log(state)
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

function crop_shortcuts(e) {
	// console.log(e)
	if (e.key === 'z') { crop_prev_image() //next
	} else if (e.key === 'x') { crop_next_image(false,true) // ignore+next
	} else if (e.key === 'c') { crop_next_image(true) // crop+next
	} else if (e.key === 'v') { crop_next_image() //next
	} else {
		console.log(e)
	}
}

var crop_data
async function crop_json_load() {
	let data = await fetch("/api/crop/info");
	data = await data.json()
	crop_data = data["crop"]
	if (crop_data["current"] === undefined) {
		crop_data["current"] = 0
	}
	crop_status(true)
}

async function crop_json_save() {
	console.log("Save crop/json")
	document.getElementById("c_save").disabled = true;
	let data = {}
	data["crop"] = crop_data

	await fetch('/api/json/save', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify(data)
	})
	await crop_json_load() // verify
	document.getElementById("c_save").disabled = false;
}

function crop_update_status_text(target,data) {
	if (data["crop_data"] === undefined && data["ignored"] != true) {
		target.innerHTML = "Unknown/Not cropped"
		target.style.color = "gray"
	} else if (!(data["crop_data"] === undefined) && data["ignored"] != true) {
		target.innerHTML = "Cropped"
		target.style.color = "green"
	} else if (data["ignored"] == true) {
		target.innerHTML = "Ignored"
		target.style.color = "red"
	} else {
		target.innerHTML = "???"
		target.style.color = "orange"
	}
}

async function crop_update_current() {
	let current = crop_data["images"][crop_data["current"]]
	crop_update_status_text(document.getElementById("c_status"),current)

	if (crop.image == undefined) {
		return
	}
	
	let old_url = new URL(crop.image.src)
	let url = "/img/0 - raw/" + current["filename"]
	if (old_url.pathname != url) {
		crop.replace(url,true)
	}
	
	if (current["crop_data"] === undefined) {
		return
	}
	crop.setData(current["crop_data"])
}

function crop_status_current(row=document.getElementById("crop_table_current"),name="Current") {
	let c_name = row.insertCell(0)
	c_name.innerHTML = name
	
	let total = 0
	let cropped = 0
	let ignored = 0
	let unknown = 0
	for (const image of crop_data["images"]) {
		total++
		if (!(image["crop_data"] === undefined)) {
			if (image["ignored"]) {
				ignored++
			} else {
				cropped++
			}
		} else {
			unknown++
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
}

function crop_next_image(set_crop=false, set_ignore=false) {
	if (set_crop) {
		crop_data["images"][crop_data["current"]]["crop_data"] = crop.getData()
		crop_data["images"][crop_data["current"]]["ignored"] = false
	}
	if (set_ignore) {
		crop_data["images"][crop_data["current"]]["ignored"] = true
	}
	
	if ((crop_data["current"]+1) >= crop_data["images"].length) {
		return
	}
	crop_update_status_text(document.getElementById("c_status_prev"),crop_data["images"][crop_data["current"]])
	crop_data["current"]++
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

	let link = document.createElement( "link" )
	link.href = "cropper.css"
	link.type = "text/css"
	link.rel = "stylesheet"
	document.head.appendChild(link);

	await import('./cropper.js');

	const image = document.getElementById('crop-img');
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
crop_init()