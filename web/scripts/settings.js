var global_settings = null

async function setting_update() {
	let data = await fetch("/api/settings/load");
	data = await data.json()
	if (!data || !data.version) {
		return
	}
	global_settings = data

	document.getElementById("sts_editor").value = data.editor
	document.getElementById("sts_webui").value = data.webui_url
	document.getElementById("sts_save").disabled = false
	document.getElementById("sts_revert").disabled = false
}

async function setting_save() {
	document.getElementById("sts_save").disabled = true
	document.getElementById("sts_revert").disabled = true

	let data = global_settings
	data.editor = document.getElementById("sts_editor").value
	data.webui_url = document.getElementById("sts_webui").value

	await fetch('/api/settings/save', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify(data)
	})

	setting_update()
	document.getElementById("sts_save").disabled = false
	document.getElementById("sts_revert").disabled = false
}

async function setting_webui_check() {
	document.getElementById("sts_save").disabled = true
	document.getElementById("sts_revert").disabled = true
	document.getElementById("sts_check").disabled = true

	let url = encodeURIComponent(document.getElementById("sts_webui").value)
	let data = await fetch(`/api/sd/check/conn?url=${url}`);
	data = await data.json()
	if (data) {
		out = Date() + "\n" + JSON.stringify(data, null, 2)
		document.getElementById("sts_check_out").innerHTML = out
	} else {
		document.getElementById("sts_check_out").innerHTML = "Server error"
	}

	document.getElementById("sts_save").disabled = false
	document.getElementById("sts_revert").disabled = false
	document.getElementById("sts_check").disabled = false
}