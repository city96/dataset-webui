function tag_auto_poll_table(tags) {
	var table = document.getElementById("ta_table")
	table.innerHTML = "";
	if (!tags) return
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
	let conf = document.getElementById("ta_conf").value
	let data = await fetch("/api/atag/run?overwrite="+ow+"&confidence="+conf);
	document.getElementById("ta_run").disabled = true
	data = await data.json()
	let current = -1
	while (data["run"]) {
		data = await fetch("/api/atag/run_poll");
		data = await data.json()

		if (current == data["current"]) continue
		current = data["current"]
		
		document.getElementById("ta_img").src = (data.preview) ? data.preview : "/assets/placeholder.png"
		tag_auto_poll_table(data["caption"])

		if (data["max"]) {
			console.log("poll update",data["current"],data["max"])
			perc.max = data["max"]
			perc.value = data["current"]
		} else {
			perc.max = 1
			perc.value = 1
		}
		await new Promise(r => setTimeout(r, 200));
	}
	perc.max = 1
	perc.value = 0
	document.getElementById("ta_img").src = "/assets/placeholder.png"
	document.getElementById("ta_table").innerHTML = "";
	document.getElementById("ta_run").disabled = false
	
	// global lock
	unlock()
	save_lock(false)
	
	// update stats
	tag_update()
	tag_img_update()
	page_update(false)
}

async function tag_auto_check() {
	let data = await fetch("/api/inference_check/");
	data = await data.json()
	if (!data || !data.onnx || data.onnx == false) {
		disable_module("tag-auto-div", "ONNX Runtime missing")
	} else {
		enable_module("tag-auto-div")
	}
}
