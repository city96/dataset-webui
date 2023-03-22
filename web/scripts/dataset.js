function dataset_updateTable(datasets){
	var table = document.getElementById("dataset-table")
	table.innerHTML = "";

	var active = false
	var current_count = 0
	for(const dataset of datasets) {
		if (dataset["active"]) {
			active = dataset
			break
		}
	}
	dataset_hasActive(active)

	for(const dataset of datasets) {
		// Name
		r = table.insertRow();
		var c = r.insertCell(0)
		c.innerHTML = dataset["name"]
		
		// Folder
		var cs = r.insertCell(1)
		cs.innerHTML = dataset["save_path"]
		
		// Images
		var c = r.insertCell(2)
		if (dataset["image_count"] > 0) {
			c.innerHTML = dataset["image_count"]
		} else {
			c.innerHTML = "-"
		}
		
		// Button
		var c = r.insertCell(3)
		b = document.createElement('button');
		c.appendChild(b)
		if (dataset["active"]) {
			b.innerHTML = "Save"
			b.setAttribute('onclick','dataset_store("'+encodeURIComponent(dataset["save_path"])+'")')
		} else {
			b.innerHTML = "Load"
			b.setAttribute('onclick','dataset_load("'+encodeURIComponent(dataset["save_path"])+'")')
			if (active) {
				b.disabled = true;
			}
		}
	}

	return current_count
}

function dataset_hasActive(active) {
	if (active) {
		document.getElementById("d_new").disabled = true;
		document.getElementById("d_update").disabled = false;
		document.getElementById("d_name").value = active.name
		document.getElementById("d_description").value = active.description
	} else {
		console.log("No active dataset")
		document.getElementById("d_name").disabled = false;
		document.getElementById("d_name").value = ""
		document.getElementById("d_description").disabled = false;
		document.getElementById("d_description").value = ""
		document.getElementById("d_new").disabled = false;
		document.getElementById("d_update").disabled = true;
	}
	update_all() // other scripts
}

function dataset_json_parse() { // Parse dataset metadata from page
	let data = {};
	data["name"] = document.getElementById("d_name").value;
	data["description"] = document.getElementById("d_description").value;
	return data;
}

async function dataset_update() { // Get active+current dataset metadata
	console.log("Update datasets")
	save_lock()
	let data = await fetch("/api/dataset/info");
	data = await data.json()
	dataset_updateTable(data["datasets"])
	save_lock(false)
}

async function dataset_store(path) { // Move current dataset to datasets folder
	if (!path) {return}
	console.log("Store dataset")
	let data = await fetch(`/api/dataset/store?path=${path}`);
	data = await data.json()
	dataset_update()
}

async function dataset_load(path) { // Load dataset into active folder
	if (!path) {return}
	console.log("Load dataset")
	let data = await fetch(`/api/dataset/load?path=${path}`);
	data = await data.json()
	dataset_update()
}

async function dataset_new() { // create new dataset from user input
	document.getElementById("d_new").disabled = true;
	let data = {}
	data["meta"] = dataset_json_parse()

	await fetch('/api/dataset/create', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify(data)
	})
	dataset_update()
}

async function dataset_save() { // Update dataset.json ["meta"] section
	console.log("Save dataset/json")
	document.getElementById("d_update").disabled = true;
	let data = {}
	data["meta"] = dataset_json_parse()

	await fetch('/api/json/save', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify(data)
	})
	dataset_update()
}

// dataset_update() // init