function lock_update(disabled=true) {
	let buttons = document.getElementsByClassName("update")
	
	for(const button of buttons) {
		button.disabled = disabled
	}
}

// Update/initialize all fields on first load
function update_all() {
	lock_update()
	setting_update()
	status_update()
	crop_init()
	sort_cat_update()
	sort_update()
	lock_update(false)
}

var locked = false
var disabled = []
// Lock all fields (pending edit)
function lock_all(whitelist=[],message=null) {
	if (locked) {
		return
	}

	const divs = ["dataset-div","dataset-current-div","status-div","crop-div","sort-cat-div","sort-div","tag-div"]
	for (const id of divs) {
		let div = document.getElementById(id)
		if (whitelist.includes(id)) {
			div.classList.remove("locked"); // shouldn't happen
			// let warn = div.getElementsByClassName("warn")[0]
			// warn.style.display = "block"
			// warn.innerHTML = "You have unsaved changes"
		} else {
			div.classList.add("locked");
		}
		if (message && !disabled.includes(id)) {
			let warn = div.getElementsByClassName("warn")[0]
			if (warn) {
				warn.style.display = "block"
				warn.innerHTML = message
			}
		}
	}
	locked = true
	lock_update()
}

// Unlock all fields (on save)
function unlock_all(){
	if (!locked) {
		return
	}
	const divs = ["dataset-div","dataset-current-div","status-div","crop-div","sort-cat-div","sort-div","tag-div"]
	for (const id of divs) {
		if (disabled.includes(id)) { continue }
		let div = document.getElementById(id)
		div.classList.remove("locked");
		let warn = div.getElementsByClassName("warn")[0]
		if (warn && warn.innerHTML == "You have unsaved changes") {
			warn.style.display = "none"
		}
	}
	locked = false
	lock_update(false)
}

function full_lock(state) {
	if (state) {
		document.body.classList.add("no-input")
	} else {
		document.body.classList.remove("no-input")
	}
}

document.addEventListener("DOMContentLoaded", function(){
	// dataset_update()
});



// #### Lock Rewrite ####

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
		if (message && !disabled.includes(div.id)) {
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
	lock_unsaved = true
}

function unlock() {
	if (!lock_unsaved) {
		return
	}
	for (const div of document.getElementsByClassName("module")) {
		if (disabled.includes(lock_disabled)) {
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

function add_modification_triggers() {
	for (const i of document.getElementsByTagName("input")) {
		let module = i.closest(".module").id
		if ((i.type == "text" || i.type == "number") && !i.getAttribute("oninput")) {
			i.setAttribute("oninput",`lock('${module}')`)
		} 
		if (i.type == "checkbox" && !i.getAttribute("onchange")) {
			i.setAttribute("onchange",`lock('${module}')`)
		}
	}
	for (const i of document.getElementsByTagName("select")) {
		let module = i.closest(".module").id
		if (!i.getAttribute("onchange")) {
			i.setAttribute("onchange",`lock('${module}')`)
		}
	}
}