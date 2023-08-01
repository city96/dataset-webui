async function crop_auto_run() {
	console.log("run")
	if (!crop_data) return
	// global lock
	lock('crop-auto-div');
	save_lock()

	let perc = document.getElementById("ca_perc")
	let cth = document.getElementById("ca_cth").value
	let cam = document.getElementById("ca_cam").value
	let cdi = document.getElementById("ca_cdi").value
	document.getElementById("ca_img").style.display = "block"
	let data = await fetch(`/api/acrop/run?threshold=${cth}&min_size=${cam}&scale=${cdi}`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify(crop_data)
	})

	document.getElementById("ca_run").disabled = true
	data = await data.json()
	let current = -1
	while (data["run"]) {
		data = await fetch(`/api/acrop/run_poll`);
		data = await data.json()

		if (current == data["current"]) continue
		current = data["current"]

		document.getElementById("ca_img").src = (data.preview) ? data.preview : "/assets/placeholder.png"
	
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
	// global lock
	unlock()
	save_lock(false)
	page_update(false)

	if (data["images"] && data["images"].length > 0) {
		crop_data["images"] = data["images"]
		lock("crop-div")
		crop_update_current()
	}
	
	console.log("LAST:", data)
	perc.max = 1
	perc.value = 0
	document.getElementById("ca_img").src = "/assets/placeholder.png"
	document.getElementById("ca_img").style.display = "none"
	document.getElementById("ca_run").disabled = false
}

async function crop_auto_check() {
	let data = await fetch("/api/inference_check/");
	data = await data.json()
	if (!data || !data.onnx || data.onnx == false) {
		disable_module("crop-auto-div", "ONNX Runtime missing")
	} else {
		enable_module("crop-auto-div")
	}
}
