function dataset(info){
	var dataset_div = document.getElementById("datasets")
	dataset_div.innerHTML = "";

	var has_active = false
	for(const key in info) {
		if (info[key]["active"]) {
			has_active = true
		}
	}

	var t = document.createElement('table');
	dataset_div.appendChild(t)

	var th = t.createTHead();
	var r = th.insertRow(0);
	
	var c = r.insertCell(0);
	c.innerHTML = "Name"
	var c = r.insertCell(1);
	c.innerHTML = "Folder"
	var c = r.insertCell(2);
	c.innerHTML = "Images"
	var c = r.insertCell(3);
	c.innerHTML = "Move"

	for(const key in info) {
		r = t.insertRow();
		var c = r.insertCell(0)
		c.innerHTML = info[key]["name"]
		
		var cs = r.insertCell(1)
		cs.innerHTML = info[key]["save_path"]
		
		var cic = r.insertCell(2)
		if (info[key]["img_count"] > 0) {
			cic.innerHTML = info[key]["img_count"]
		} else {
			cic.innerHTML = "-"
		}
		var ctu = r.insertCell(3)
		b = document.createElement('button');
		ctu.appendChild(b)
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

function dataset_update() {
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

dataset_update()