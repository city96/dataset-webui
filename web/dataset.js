function dataset(info){
	var table = document.getElementById("dataset-table")
	table.innerHTML = "";

	var has_active = false
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
		} else {
			b.innerHTML = "Load"
			if (has_active) {
				b.disabled = true;
			}
		}
	}
}

function update_dataset() {
	console.log("dataset")
	var ajax = new XMLHttpRequest();
	ajax.responseType = 'json';
	ajax.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) { 
			dataset(this.response);
		};
	};
	ajax.open('GET',"/api/dataset",true);
	ajax.send();
}

update_dataset()