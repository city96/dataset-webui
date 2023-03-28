var stop = false
async function sort_auto_run() {
	let c = confirm("Are you sure you want to automatically sort your images? You can click 'Revert Changes' below to undo this.");
	if (!c) { return };
	document.getElementById("sa_run").disabled = true
	document.getElementById("sa_stop").disabled = false
	
	lock('sort-auto-div')
	let req_and = document.getElementById("sa_tag_req").value == "and"
	let confidence = document.getElementById("sa_conf").value
	let ignore = document.getElementById("sa_ignore").checked

	stop = false
	for(const i in sort_data.images) {
		if (sort_data.images[i].category == "default" || !ignore) {
			let cat = await sort_get_image_category(sort_data.images[i].filename, confidence, req_and)
			sort_data.images[i].category = cat
			sort_current = Math.floor(i/(sort_grid*sort_grid)) * (sort_grid*sort_grid)
			sort_img_table()
		}
		if (stop) { break }
	}
	sort_img_table()
	document.getElementById("sa_run").disabled = false
	document.getElementById("sa_stop").disabled = true
	unlock()
	lock('sort-div')
}

function sort_auto_stop() {
	stop = true
}

async function sort_get_image_category(path, confidence=0.35, req_and=false) {
	let data = await fetch("/api/tagger/single?confidence="+confidence+"&path=1%20-%20cropped/"+path);
	data = await data.json()
	if (!data ) { return "default" }
	// console.log(data)
	let cats = {}
	for (const c in sort_data.categories) {
		cats[c] = {}
		for (const t of sort_data.categories[c].tags) {
			cats[c][t] = 0
		}
	}
	for (const t in data) {
		for (const c in cats) {
			if (cats[c][t] == 0) {
				cats[c][t] = data[t]
			}
		}
	}
	// console.log(cats)
	let out = {}
	for (const c in cats) {
		if (req_and) { out[c] = 1 }
		else { out[c] = 0 }
		for (const v in cats[c]) {
			if (req_and) { out[c] = out[c] * cats[c][v] }
			else { out[c] = out[c] + cats[c][v] }
		}
	}
	// console.log(out)
	let cat = "default"
	let conf = 0
	for (const c in out) {
		if (c != "default" && out[c] > conf) {
			cat = c
			conf = out[c]
		}
	}
	console.log(path,cat)
	return cat
}
