function update_status_table(steps) {
	let table = document.getElementById("status-table")
	table.innerHTML = "";
	
	let tags = false
	for(const step in steps) {
		// Name
		r = table.insertRow();
		let c0 = r.insertCell(0)
		c0.innerHTML = step

		// Images
		let c1 = r.insertCell(1)
		if (steps[step]["image_count"]["total"] > 0) {
			c1.innerHTML = steps[step]["image_count"]["total"]
		} else {
			c1.innerHTML = "-"
		}

		// Tags
		let c2 = r.insertCell(2)
		let c3 = r.insertCell(3)
		if(steps[step]["tag_count"]["total"]) {
			c2.innerHTML = steps[step]["tag_count"]["total"]
			c3.innerHTML = steps[step]["tag_count"]["unique"]
		} else {
			c2.innerHTML = "-"
			c3.innerHTML = "-"
		}
		
		if (steps[step]["tag_count"]["total"] > 0 && !tags) {
			// run from here
			tags_disabled(false)
			tags = true
		}
	}
}

// call to update parts of page
async function update_status(tags){
	console.log("Update page/json")
	let data = await fetch("/api/status");
	data = await data.json()


	document.getElementById("d_name").value = data["meta"]["name"];
	document.getElementById("d_description").value = data["meta"]["description"];
	
	update_status_table(data["status"]["steps"])
	tag_json_load(data["tags"])
}

function hide_status() {
	let table = document.getElementById("status-table")
	table.innerHTML = "";
}