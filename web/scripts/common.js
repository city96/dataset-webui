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