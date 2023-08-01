var lock_unsaved = false
var lock_disabled = []

function lock(module, message="You have unsaved changes") { // module is source for lock
	if (lock_unsaved) {
		return
	}
	for (const div of document.getElementsByClassName("module")) {
		if (module == div.id) {
			div.classList.remove("locked");
			for (const i of div.getElementsByClassName("unlock")) {
				i.disabled = false
			}
		} else {
			div.classList.add("locked");
		}
		if (message && !lock_disabled.includes(div.id)) {
			let warn = div.getElementsByClassName("warn")[0]
			if (warn) {
				warn.style.display = "block"
				warn.innerHTML = message
			}
		}
	}
	for (const i of document.getElementsByClassName("update")) {
		i.disabled = true
	}
	for (const i of document.getElementsByClassName("req-save")) {
		i.disabled = true
	}
	lock_unsaved = true
}

function unlock() {
	if (!lock_unsaved) {
		return
	}
	for (const div of document.getElementsByClassName("module")) {
		if (lock_disabled.includes(div.id)) {
			continue
		}
		div.classList.remove("locked");

		let warn = div.getElementsByClassName("warn")[0]
		if (warn && warn.innerHTML == "You have unsaved changes") {
			warn.innerHTML = ""
			warn.style.display = "none"
		}
	}
	for (const i of document.getElementsByClassName("update")) {
		i.disabled = false
	}
	for (const i of document.getElementsByClassName("unlock")) {
		i.disabled = true
	}
	for (const i of document.getElementsByClassName("req-save")) {
		i.disabled = false
	}
	lock_unsaved = false
}

function disable_module(module, message=null) {
	let div = document.getElementById(module)
	if (!lock_disabled.includes(module)) {
		lock_disabled.push(module)
		div.classList.add("locked");
	}
	
	let warn = div.getElementsByClassName("float-warn")[0]
	if (message && warn) {
		warn.innerHTML = message
		warn.style.display = "block"
	} else if(warn) {
		warn.innerHTML = ""
		warn.style.display = "none"
	}
}

function enable_module(module, message=null) {
	let div = document.getElementById(module)
	if (lock_disabled.includes(module)) {
		lock_disabled = lock_disabled.filter(function(i){return (i!==module)})
		div.classList.remove("locked");
	}
	let warn = div.getElementsByClassName("float-warn")[0]
	if (warn) {
		warn.innerHTML = ""
		warn.style.display = "none"
	}
}

function save_lock(state=true) { // lock entire page for save/write operations
	if (state) {
		document.body.classList.add("no-input")
	} else {
		document.body.classList.remove("no-input")
	}
}

function add_modification_triggers(target) {
	if (!target) { return }
	for (const i of target.getElementsByTagName("input")) {
		let module = i.closest(".module").id
		if ((i.type == "text" || i.type == "number") && !i.getAttribute("oninput")) {
			i.setAttribute("oninput",`lock('${module}')`)
		} 
		if (i.type == "checkbox" && !i.getAttribute("onchange")) {
			i.setAttribute("onchange",`lock('${module}')`)
		}
	}
	for (const i of target.getElementsByTagName("select")) {
		let module = i.closest(".module").id
		if (!i.getAttribute("onchange")) {
			i.setAttribute("onchange",`lock('${module}')`)
		}
	}
}

function navbar_set(div_id, state, info="", color="red") {
	// let nb = document.getElementById("navbar")
	let div = document.getElementById(div_id)
	div.getElementsByTagName("button")[0].disabled = !state
	let nfo = div.getElementsByClassName("nfo")[0]
	nfo.innerHTML = info
	nfo.style.color = color
}

async function page_update(update=true) {
	save_lock(true)
	let loc = window.location.pathname
	let data = await fetch("/api/status");
	data = await data.json()
	if (!data || !data.status || !data.status.active || !data.status.steps) { // no dataset
		if (loc != "/") {
			window.location.replace('/'); // enable to redirect when no dataset is available
			return
		}
		for (const i of ["nb-status-div","nb-crop-div","nb-sort-div","nb-tag-div","nb-out-div"]) {
			navbar_set(i,false,"No active dataset")
		}
		if (update) {
			dataset_update()
		}
		return
	}
	console.log(data)
	// dataset / index check
	if (loc == "/") {
		navbar_set("nb-dataset-div",false,"Active tab","green")
		if (update) {
			dataset_update()
		}
	} else {
		navbar_set("nb-dataset-div",true)
	}
	// status check
	if (!data.status || !data.status.steps) {
		navbar_set("nb-crop-div",false,"No images","orange")
		if (loc == "/status.html") {
			window.location.replace('/');
		}
	} else if (loc == "/status.html") {
		navbar_set("nb-status-div",false,"Active tab","green")
		if (update) {
			status_update()
		}
	} else {
		navbar_set("nb-status-div",true)
	}
	// crop check
	if (!data.status.steps["0 - raw"] || data.status.steps["0 - raw"].image_count.total == 0) {
		navbar_set("nb-crop-div",false,"No images","orange")
		if (loc == "/crop.html") {
			window.location.replace('/');
		}
	} else if (loc == "/crop.html") {
		navbar_set("nb-crop-div",false,"Active tab","green")
		if (update) {
			crop_init()
			crop_auto_check()
		}
	} else {
		navbar_set("nb-crop-div",true)
	}
	// sort check
	if (!data.status.steps["1 - cropped"] || data.status.steps["1 - cropped"].image_count.total == 0) {
		navbar_set("nb-sort-div",false,"No images","orange")
		if (loc == "/sort.html") {
			window.location.replace('/');
		}
	} else if (loc == "/sort.html") {
		navbar_set("nb-sort-div",false,"Active tab","green")
		if (update) {
			sort_cat_update()
			sort_update()
		}
	} else {
		navbar_set("nb-sort-div",true)
	}
	// tag check
	if ((!data.status.steps["2 - sorted"] || data.status.steps["2 - sorted"].image_count.total == 0) && (!data.status.steps["3 - tagged"] || data.status.steps["3 - tagged"].image_count.total == 0)) {
		navbar_set("nb-tag-div",false,"No images/tags","orange")
		if (loc == "/tag.html") {
			window.location.replace('/');
		}
	} else if (loc == "/tag.html") {
		navbar_set("nb-tag-div",false,"Active tab","green")
		if (update) {
			tag_update()
			tag_img_update()
			tag_auto_check()
		}
	} else {
		navbar_set("nb-tag-div",true)
	}
	// out check
	if ((!data.status.steps["2 - sorted"] || data.status.steps["2 - sorted"].image_count.total == 0) && (!data.status.steps["4 - fixed"] || data.status.steps["4 - fixed"].image_count.total == 0)) {
		navbar_set("nb-out-div",false,"No images","orange")
		if (loc == "/out.html") {
			window.location.replace('/');
		}
	} else if (loc == "/out.html") {
		navbar_set("nb-out-div",false,"Active tab","green")
		if (update) {
			out_scale_check()
		}
	} else {
		navbar_set("nb-out-div",true)
	}
	save_lock(false)
}

// on page load
document.addEventListener("DOMContentLoaded", function() {
	page_update()
});
