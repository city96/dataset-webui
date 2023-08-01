async function out_write_run() {
	console.log("run")
	// global lock
	lock('out-write-div')
	save_lock()
	
	let perc = document.getElementById("ow_perc")
	let ow = document.getElementById("ow_ow").checked
	let uw = document.getElementById("ow_uw").checked
	let res = document.getElementById("ow_res").value
	let ext = document.getElementById("ow_ext").value
	let data = await fetch("/api/out/run?overwrite="+ow+"&resolution="+res+"&extension="+ext+"&weights="+uw);
	document.getElementById("ow_run").disabled = true
	data = await data.json()
	while (data["run"]) {
		data = await fetch("/api/out/run_poll");
		data = await data.json()
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
	document.getElementById("ow_run").disabled = false
	
	// global lock
	unlock()
	save_lock(false)
}

async function out_scale_check() {
	let res = document.getElementById("ow_res").value
	let data = await fetch("/api/out/scale_check?resolution="+res)
	data = await data.json()
	if (!data || !data.resolution || data.resolution != res) {
		for (const i of ["ow_upsc","ow_keep","ow_down","ow_misc"]) {
			document.getElementById(i).innerHTML = "-"
		}
		return
	}
	for (const i in data.images) {
		document.getElementById(`ow_${i}`).innerHTML = data.images[i]
	}
}
