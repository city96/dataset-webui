function status(info){
	var table = document.getElementById("status-table")
	table.innerHTML = "";

	for(const key in info) {
		// Name
		r = table.insertRow();
		var c = r.insertCell(0)
		c.innerHTML = key

		// Images
		var c = r.insertCell(1)
		if (info[key]["img_count"] > 0) {
			c.innerHTML = info[key]["img_count"]
		} else {
			c.innerHTML = "-"
		}

		// Tags
		var c2 = r.insertCell(2)
		var c3 = r.insertCell(3)
		if(info[key]["tag_count"]["total"]) {
			c2.innerHTML = info[key]["tag_count"]["total"]
			c3.innerHTML = info[key]["tag_count"]["unique"]
		} else {
			c2.innerHTML = "-"
			c3.innerHTML = "-"
		}
	}
}

function update_status() {
	console.log("status")
	var ajax = new XMLHttpRequest();
	ajax.responseType = 'json';
	ajax.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) { 
			status(this.response);
		};
	};
	ajax.open('GET',"/api/status",true);
	ajax.send();
}

update_status()