function tag_auto_poll_table(tags) {
	var table = document.getElementById("ta_table")
	table.innerHTML = "";
	for(const key in tags) {
		if (["general","sensitive","questionable","explicit"].includes(key)) {
			continue
		}
		r = table.insertRow();
		let c0 = r.insertCell(0)
		c0.innerHTML = key
		
		let c1 = r.insertCell(1)
		let perc = tags[key].toLocaleString(undefined,{style: 'percent', minimumFractionDigits:2});
		c1.innerHTML = perc
	}
}

async function tag_auto_run() {
	console.log("run")
	// global lock
	lock('tag-auto-div');
	save_lock()
	
	let perc = document.getElementById("ta_perc")
	let ow = document.getElementById("ta_ow").checked
	let data = await fetch("/api/sd/autotag/run?overwrite="+ow);
	document.getElementById("ta_run").disabled = true
	data = await data.json()
	while (data["run"]) {
		data = await fetch("/api/sd/autotag/run_poll");
		data = await data.json()
		if (data["url"]) {
			document.getElementById("ta_img").src = data["image"]
		} else {
			document.getElementById("ta_img").src = "/assets/placeholder.png"
		}
		if (data["caption"]) {
			tag_auto_poll_table(data["caption"])
		} else {
			document.getElementById("ta_table").innerHTML = "";
		}
		if (data["max"]) {
			console.log("poll update",data["current"],data["max"])
			perc.max = data["max"]
			perc.value = data["current"]
		} else {
			perc.max = 1
			perc.value = 1
		}
		await new Promise(r => setTimeout(r, 500));
	}
	perc.max = 1
	perc.value = 0
	document.getElementById("ta_img").src = "/assets/placeholder.png"
	document.getElementById("ta_table").innerHTML = "";
	document.getElementById("ta_run").disabled = false
	
	// global lock
	unlock()
	save_lock(false)
}
