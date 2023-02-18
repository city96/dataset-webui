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
		document.getElementById("d_name").disabled = true;
		document.getElementById("d_description").disabled = true;
		document.getElementById("d_new").disabled = true;
	} else {
		hide_status()
		document.getElementById("d_name").disabled = false;
		document.getElementById("d_name").value = ""
		document.getElementById("d_description").disabled = false;
		document.getElementById("d_description").value = ""
		document.getElementById("d_new").disabled = false;
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
function get_current_json() {
	var data = {};
	data["meta"] = {};
	data["meta"]["name"] = document.getElementById("d_name").value;
	data["meta"]["description"] = document.getElementById("d_description").value;
	
	data["tags"] = tag_json_get()
	return data;
}

function create_dataset(){
	document.getElementById("d_new").disabled = true;
	data = get_current_json()

	var ajax = new XMLHttpRequest();
	ajax.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) { 
			update_dataset()
		};
	};
	ajax.open('POST',"/api/dataset/create",false);
	ajax.setRequestHeader('Content-type', 'application/json; charset=UTF-8')

	data = JSON.stringify(data)
	ajax.send(data);
}

update_datasets()