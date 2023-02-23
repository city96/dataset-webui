function update_dataset_table(datasets){
	var table = document.getElementById("dataset-table")
	table.innerHTML = "";

	var has_active = false
	var current_count = 0
	for(const dataset of datasets) {
		if (dataset["active"]) {
			has_active = true
			break
		}
	}

	if (has_active) {
		update_status()
		document.getElementById("d_new").disabled = true;
		document.getElementById("d_update").disabled = false;
	} else {
		console.log("No active dataset")
		hide_status()
		crop_disabled(true)
		tags_disabled(true)
		document.getElementById("d_name").disabled = false;
		document.getElementById("d_name").value = ""
		document.getElementById("d_description").disabled = false;
		document.getElementById("d_description").value = ""
		document.getElementById("d_new").disabled = false;
		document.getElementById("d_update").disabled = true;
	}

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
			b.setAttribute('onclick','save_dataset("'+encodeURIComponent(dataset["save_path"])+'")')
		} else {
			b.innerHTML = "Load"
			b.setAttribute('onclick','load_dataset("'+encodeURIComponent(dataset["save_path"])+'")')
			if (has_active) {
				b.disabled = true;
			}
		}
	}

	return current_count
}

async function update_datasets() {
	console.log("Update datasets")
	let data = await fetch("/api/dataset/info");
	data = await data.json()
	update_dataset_table(data["datasets"])
}

async function save_dataset(path) {
	if (!path) {return}
	console.log("Save dataset")
	let data = await fetch(`/api/dataset/save?path=${path}`);
	data = await data.json()
	update_dataset_table(data["datasets"])
}

async function load_dataset(path) {
	if (!path) {return}
	console.log("Save dataset")
	let data = await fetch(`/api/dataset/load?path=${path}`);
	data = await data.json()
	update_dataset_table(data["datasets"])
}

// from page
function get_dataset_json() {
	let data = {};
	data["name"] = document.getElementById("d_name").value;
	data["description"] = document.getElementById("d_description").value;
	return data;
}

async function save_dataset_json() {
	console.log("Save dataset/json")
	document.getElementById("d_update").disabled = true;
	let data = {}
	data["meta"] = get_dataset_json()

	await fetch('/api/json/save', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify(data)
	})
	update_datasets()
}

async function create_dataset(){
	document.getElementById("d_new").disabled = true;
	let data = {}
	data["meta"] = get_dataset_json()

	await fetch('/api/dataset/create', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify(data)
	})
	update_datasets()
}

update_datasets()