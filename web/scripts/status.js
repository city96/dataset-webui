function status_updateTable(steps) {
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
			// tags_disabled(false)
			tags = true
		}
	}
	// if (!tags) {
		// tags_disabled(true)
	// }
	
	// enable cropping
	// crop_disabled(!(steps["0 - raw"]["image_count"]["total"] > 0))
}

async function status_update(){
	console.log("Update page/json")
	lock_update()
	let data = await fetch("/api/status");
	data = await data.json()
	
	if (data == undefined || data.status == undefined || data.status.steps.length == 0) {
		if (data.status.warn.length > 0) {
			status_disable(data.status.warn)
		} else {
			status_disable("Nothing to load from disk")
		}
		lock_update(false)
		return
	} else {
		document.getElementById("status-div").classList.remove("locked");
		document.getElementById("status-float-warn").style.display = "none"; 
		disabled = disabled.filter(function(i){return (i!=="status-div")})
	}
	
	status_updateTable(data["status"]["steps"])
	lock_update(false)
}

function status_disable(message=null) {
	let table = document.getElementById("status-table")
	table.innerHTML = "";
	document.getElementById("status-div").classList.add("locked");
	if (!disabled.includes("status-div")) { disabled.push("status-div") }

	if (message) {
		document.getElementById("status-float-warn").style.display = "block"; 
		document.getElementById("status-float-warn").innerHTML = message
	} else {
		document.getElementById("status-float-warn").style.display = "none"; 
	}
	
}