function lock_update(disabled=true) {
	let buttons = document.getElementsByClassName("update")
	
	for(const button of buttons) {
		button.disabled = disabled
	}
}

function update_all() {
	lock_update()
	status_update()
	lock_update(false)
}

function disable_all(message=null) {
	lock_update()
	status_disable(message)
}