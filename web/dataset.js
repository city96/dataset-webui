function update_dataset_table(info){
	var table = document.getElementById("dataset-table")
	table.innerHTML = "";

	var has_active = false
	var current_count = 0
	for(const key in info) {
		if (info[key]["active"]) {
			has_active = true
		}
	}
	
	if (has_active) {
		console.log("active")
		document.getElementById("d_name").disabled = true;
		document.getElementById("d_description").disabled = true;
		document.getElementById("d_new").disabled = true;
		update_status();
		load_json();
	} else {
		document.getElementById("d_name").disabled = false;
		document.getElementById("d_name").value = ""
		document.getElementById("d_description").disabled = false;
		document.getElementById("d_description").value = ""
		document.getElementById("d_new").disabled = false;
		tag_json_clear();
	}

	for(const key in info) {
		// Name
		r = table.insertRow();
		var c = r.insertCell(0)
		c.innerHTML = info[key]["name"]
		
		// Folder
		var cs = r.insertCell(1)
		cs.innerHTML = info[key]["save_path"]
		
		// Images
		var c = r.insertCell(2)
		if (info[key]["img_count"] > 0) {
			c.innerHTML = info[key]["img_count"]["total"]
		} else {
			c.innerHTML = "-"
		}
		
		// Button
		var c = r.insertCell(3)
		b = document.createElement('button');
		c.appendChild(b)
		if (info[key]["active"]) {
			b.innerHTML = "Save"
			b.setAttribute('onclick','save_dataset("'+encodeURIComponent(info[key]["save_path"])+'")')
		} else {
			b.innerHTML = "Load"
			b.setAttribute('onclick','load_dataset("'+encodeURIComponent(info[key]["save_path"])+'")')
			if (has_active) {
				b.disabled = true;
			}
		}
	}
	
	return current_count
}

function update_dataset() {
	console.log("dataset")
	var ajax = new XMLHttpRequest();
	ajax.responseType = 'json';
	ajax.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) { 
			let info = this.response
			update_dataset_table(info)
			
			let current_count = 0
			for(const key in info) {
				if (info[key]["active"]) {
					current_count = info[key]["img_count"]
				}
			}
			if (current_count > 0){
				update_status();
			} else {
				hide_status();
			}
		};
	};
	ajax.open('GET',"/api/dataset/info",true);
	ajax.send();
}

function save_dataset(path) {
	if (!path) {return}
	console.log("dataset save")
	var ajax = new XMLHttpRequest();
	ajax.responseType = 'json';
	ajax.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) { 
			update_dataset();
		};
	};
	ajax.open('GET',`/api/dataset/save?path=${path}`,true);
	ajax.send();
}

function load_dataset(path) {
	if (!path) {return}
	console.log("dataset load")
	var ajax = new XMLHttpRequest();
	ajax.responseType = 'json';
	ajax.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) { 
			update_dataset();
		};
	};
	ajax.open('GET',`/api/dataset/load?path=${path}`,true);
	ajax.send();
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

update_dataset()