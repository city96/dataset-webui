function lock_update(disabled=true) {
	let buttons = document.getElementsByClassName("update")
	
	for(const button of buttons) {
		button.disabled = disabled
	}
}

// Update/initialize all fields on first load
function update_all() {
	lock_update()
	status_update()
	crop_init()
	sort_cat_update()
	lock_update(false)
}

// Disable/deinitialize all fields (eg. on dataset save)
function reset_all(message=null) {
	lock_update()
	status_disable(message)
	crop_reset(message)
	sort_cat_disable(message)
}

var locked = false
// Lock all fields (pending edit)
function lock_all(whitelist=[]) {
	if (locked) {
		return
	}
	const divs = ["dataset-div","dataset-current-div","status-div","crop-div","sort-cat-div","sort-div","tag-div"]
	for (const id of divs) {
		let div = document.getElementById(id)
		if (whitelist.includes(id)) {
			div.classList.remove("locked"); // shouldn't happen
			let warn = div.getElementsByClassName("warn")[0]
			warn.style.display = "block"
			warn.innerHTML = "You have unsaved changes"
		} else {
			div.classList.add("locked");
		}
	}
	locked = true
	lock_update()
}

// Unlock all fields (on save)
function unlock_all() {
	if (!locked) {
		return
	}
	const divs = ["dataset-div","dataset-current-div","status-div","crop-div","sort-cat-div","sort-div","tag-div"]
	for (const id of divs) {
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