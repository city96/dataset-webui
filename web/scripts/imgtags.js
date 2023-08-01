var tag_img_presets = {
	"composition": ["profile", "portrait", "upper body", "full body", "solo", "1girl", "facing viewer", "from side", "facing away", "from behind"],
	"position": ["looking at viewer", "looking away", "standing", "sitting", "lying"],
	"emotion": ["smile", ":D", ":3", "happy", "blush", "sad", "angry"],
}

var tag_img_data
var tag_img_missing
var tag_img_current = 0
var tag_img_all_tags = []
async function tag_img_update() {
	let data = await fetch("/api/tags/img")
	data = await data.json()
	
	if (!data || !data.images || data.images.length == 0) {
		document.getElementById("ti-table").innerHTML = ""
		document.getElementById("ti_img").src = "/assets/placeholder.png"
		disable_module("tag-image-div", "Nothing to load from disk")
		disable_module("tag-seq-div", "Nothing to load from disk")
		return
	} else {
		enable_module("tag-image-div")
		enable_module("tag-seq-div")
	}
	
	if (!tag_img_all_tags || tag_img_all_tags.length == 0) {
		let tags = await fetch("/api/tags/all")
		tag_img_all_tags = await tags.json()
	}
	
	tag_img_data = data["images"]
	tag_img_missing = data["missing"]
	// console.log(tag_img_data[tag_img_current])
	tag_img_table_update()
	unlock()
	// sideload this here, who cares
	tag_seq_update()
}

function tag_img_update_display() {
	let tr = document.getElementById("ti-tagrow")
	let buttons = tr.getElementsByTagName("button")
	for (const b of buttons) {
		if (tag_img_data[tag_img_current]["tags"].includes(b.value)) {
			b.classList.remove("inactive")
		} else {
			b.classList.add("inactive")	
		}
		if (tag_img_data[tag_img_current]["add"].includes(b.value)) {
			b.classList.remove("inactive")
		}
		if (tag_img_data[tag_img_current]["rem"].includes(b.value)) {
			b.classList.add("inactive")			
		}
	}
}

function tag_img_toggle_tag(button, tag) {
	if (button.classList.contains("inactive")) {
		if (tag_img_data[tag_img_current]["rem"].includes(tag)) { // rem from rem
			tag_img_data[tag_img_current]["rem"] = tag_img_data[tag_img_current]["rem"].filter(function(i){return (i!==tag)})
		}
		if (!tag_img_data[tag_img_current]["tags"].includes(tag)) { // add to add if not img
			if (!tag_img_data[tag_img_current]["add"].includes(tag)) {
				tag_img_data[tag_img_current]["add"].push(tag)
			}
		}
	} else {
		if (tag_img_data[tag_img_current]["add"].includes(tag)) { // rem from add
			tag_img_data[tag_img_current]["add"] = tag_img_data[tag_img_current]["add"].filter(function(i){return (i!==tag)})
		}
		if (tag_img_data[tag_img_current]["tags"].includes(tag)) { // add to rem if img
			if (!tag_img_data[tag_img_current]["rem"].includes(tag)) { // add to rem
				tag_img_data[tag_img_current]["rem"].push(tag)
			}
		}
	}
	tag_img_current_update()
	lock('tag-image-div')
}

function tag_img_create_preset_dropdown(id, active) {
	let s = document.createElement("select")
	s.setAttribute('onchange', `tag_img_preset_update(${id});tag_img_update_display()`)
	for(const preset in tag_img_presets) {
		let o = document.createElement("option")
		o.value = preset
		o.text = preset
		if (preset == active) {
			o.selected = true
		}
		s.appendChild(o);
	}
	return s
}

function tag_img_current_update() {
	let list = document.getElementById("tir_image")
	list.innerHTML = ""
	
	let target = [].concat(tag_img_data[tag_img_current]["tags"],tag_img_data[tag_img_current]["add"])
	
	for (const tag of target) {
		let b = document.createElement('button')
		b.innerHTML = tag
		b.value = tag
		if (tag_img_data[tag_img_current]["add"].includes(tag)) {
			b.classList.add("add")
		}
		if (tag_img_data[tag_img_current]["rem"].includes(tag)) {
			b.classList.add("rem")
		}
		b.setAttribute('onclick', `tag_img_toggle_tag(this,"${tag}")`)
		list.appendChild(b)
	}
	tag_img_update_display()
}

function tag_img_search_update(limit=32) {
	let list = document.getElementById(`tir_search`)
	let input = document.getElementById('ti-search').value
	list.innerHTML = ""
	let out = []
	for (const t of tag_img_all_tags) {
		if (t.match(input)) {
			out.push(t)
		}
		if (out.length >= limit) {
			break
		}
	}
	// console.log(out)
	for (const tag of out) {
		let b = document.createElement('button')
		b.innerHTML = tag
		b.value = tag
		b.setAttribute('onclick', `tag_img_toggle_tag(this,"${tag}")`)
		list.appendChild(b)
	}
	tag_img_update_display()
}

function tag_img_preset_update(list_id) {
	let list = document.getElementById(`tir_preset_${list_id}`)
	let preset = document.getElementById(`tir_preset_dd_${list_id}`)
	preset = preset.getElementsByTagName("select")[0].value

	if (!list || !preset) { return }
	list.innerHTML = ""
	
	for (const tag of tag_img_presets[preset]) {
		let b = document.createElement('button')
		b.innerHTML = tag
		b.value = tag
		b.setAttribute('onclick', `tag_img_toggle_tag(this,"${tag}")`)
		list.appendChild(b)
	}
	tag_img_update_display()
}

const max_presets = 3
function tag_img_table_update() {
	let table = document.getElementById("ti-table")
	table.innerHTML = ""
	
	// header
	let header = table.insertRow()
	header.insertCell(0).innerHTML = "Image Tags"
	header.insertCell(1).innerHTML = "Search"
	
	// control
	let control = table.insertRow()
	control.insertCell(0).innerHTML = "Click tag to remove"
	
	// search
	let search = document.createElement("input")
	search.id = "ti-search"
	search.setAttribute("oninput", "tag_img_search_update()")
	control.insertCell(1).appendChild(search)

	for (let i = 0; i < max_presets; i++) {
		header.insertCell(i+2).innerHTML = "Preset"
		let c = control.insertCell(i+2)
		c.id = `tir_preset_dd_${i}`
		let pst = Object.keys(tag_img_presets)[Math.min(i, Object.keys(tag_img_presets).length-1)]
		// console.log(pst)
		c.appendChild(tag_img_create_preset_dropdown(i, pst))
	}
	
	// tags
	let tags = table.insertRow()
	tags.id = "ti-tagrow"
	for (let i = 0; i < max_presets+2; i++) {
		let ti_ul = document.createElement("div")
		tags.insertCell(i).appendChild(ti_ul)
		ti_ul.classList.add("tir")

		if (i == 0) { 
			ti_ul.id = "tir_image"
			tag_img_current_update()
		}
		else if (i == 1) {
			ti_ul.id = "tir_search"
			tag_img_search_update()
		}
		else { 
			ti_ul.id = `tir_preset_${i-2}`
			tag_img_preset_update(i-2)
		}
	}
	document.getElementById("ti_img").src = tag_img_data[tag_img_current].img_url
	// console.log(tag_img_data[tag_img_current].img_url)
}

async function tag_save_prev() {
	console.log("Save tag/imgtag/json")
	save_lock()
	
	let data = []
	for (const img of tag_img_data) {
		if (img.add.length > 0 || img.rem.length > 0) {
			data.push({
				"filename" : img.filename,
				"add" : img.add,
				"rem" : img.rem,
			})
		}
	}
	// console.log(data)
	await fetch('/api/json/save', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify({"tags" : {"images" : data, "missing" : tag_img_missing}})
	})
	save_lock(false)
	tag_img_update()
}

function tag_img_prev() {
	let prev = tag_img_current
	tag_img_current = Math.max(0, tag_img_current-1)
	if (prev != tag_img_current) {
		tag_img_current_update()
		document.getElementById("ti_img").src = tag_img_data[tag_img_current].img_url
	}
}

function tag_img_next() {
	let prev = tag_img_current
	tag_img_current = Math.min(tag_img_data.length-1, tag_img_current+1)
	if (prev != tag_img_current) {
		tag_img_current_update()
		document.getElementById("ti_img").src = tag_img_data[tag_img_current].img_url
	}
}
