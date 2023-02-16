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
			c.innerHTML = info[key]["img_count"]
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

update_dataset()