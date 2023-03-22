// target category for selector
var sort_tcat

function sort_set_tcat(cat) {
	sort_tcat = cat
	let r = document.querySelector(':root');
	let color = sort_data.categories[sort_tcat].color
	r.style.setProperty('--tcat', color);
	let t = document.getElementById("sort_tcat")
	t.innerHTML = sort_tcat
	t.style.backgroundColor = sort_data.categories[sort_tcat].color
	
	let tcat = document.getElementById("sort-img-grid").getElementsByClassName("tcat")
	for (const c of tcat) {
		c.innerHTML = sort_tcat
	}
	sort_buttons()
}

function sort_buttons() {
	let div = document.getElementById("sort-buttons")
	div.innerHTML = ""
	for (const cat in sort_data.categories) {
		let btn = document.createElement("button")
		btn.innerHTML = cat
		btn.style.backgroundColor = sort_data.categories[cat].color
		btn.classList.add("cat")
		if (cat == sort_tcat) {
			btn.classList.add("ccat")
		} else {
			btn.setAttribute("onclick","sort_set_tcat('"+cat+"')")
		}
		div.appendChild(btn)
	}
}

function sort_img_set_cat(index) {
	lock("sort-div")
	let image = sort_data.images[index]
	image.category = sort_tcat
	sort_img_table()
}

function sort_img_create_cel(index, div) {
	let image
	let src
	if ((index) >= sort_data.images.length) {
		image = {}
		image.category = "default"
		src = "/assets/placeholder.png"
		div.setAttribute("onclick", "")
	} else {
		image = sort_data.images[index]
		div.setAttribute("onclick", "sort_img_set_cat("+index+")")
		src =  "/img/1 - cropped/" + image.filename
	}
	
	let cat = div.getElementsByClassName("cat")
	if (cat[0]) {cat = cat[0] }
	else { 
		cat = document.createElement("a")
		div.appendChild(cat)
	}
	cat.innerHTML = image.category
	cat.style.background = sort_data.categories[image.category].color
	cat.classList.add("cat")
	

	let tcat = div.getElementsByClassName("tcat")
	if (tcat[0]) { tcat = tcat[0] }
	else { 
		tcat = document.createElement("a")
		div.appendChild(tcat)
	}
	tcat.innerHTML = sort_tcat
	tcat.style.background = "var(--tcat)"
	tcat.classList.add("tcat")

	let img = div.getElementsByTagName("img")
	if (img[0]) { img = img[0] }
	else {
		img = document.createElement("img")
		div.appendChild(img)
	}
	if (img.src != src) {
		img.src = src
	}

	div.style.borderColor = sort_data.categories[image.category].color
	return div
}

function sort_img_table() {
	let images = sort_data.images
	let table = document.getElementById("sort-img-grid")
	// table.innerHTML = "";
	
	if (sort_current >= images.length) {
		sort_current = 0
	}
	
	let i = 0
	let r
	let c
	let div
	for (let row = 0; row < sort_grid; row++) {
		if (table.rows[row]) { r = table.rows[row] }
		else { r = table.insertRow(); }
		for (let col = 0; col < sort_grid; col++) {
			if (r.cells[col]) { c = r.cells[col] } 
			else { c = r.insertCell(col) }
			
			div = c.getElementsByClassName("sort-img")
			if (div[0]) { div = div[0] }
			else {
				div = document.createElement("div")
				div.classList.add("sort-img")
				c.appendChild(div)
			}

			div = sort_img_create_cel(sort_current+i, div)

			i++
		}
	}
}

var sort_data
var sort_current = 0
var sort_grid = 3
async function sort_update() {
	let data = await fetch("/api/sort/info");
	data = await data.json()
	
	if (!data || !data.sort || !data.sort.categories || !data.sort.images || data.sort.images.length == 0) {
		document.getElementById("sort-buttons").innerHTML = ""
		document.getElementById("sort-img-grid").innerHTML = ""
		document.getElementById("sw_apply").disabled = true
		
		document.getElementById("sw_apply").disabled = true
		disable_module("sort-div", "Nothing to load from disk")
		disable_module("sort-write", "Nothing to load from disk")
		return
	} else {
		document.getElementById("sw_apply").disabled = false
		enable_module("sort-div")
		enable_module("sort-write")
	}
	sort_data = data.sort
	if (!sort_tcat) {
		sort_set_tcat("default")
	}
	sort_buttons()
	sort_img_table()
	unlock()
}

async function sort_json_save() {
	console.log("Save sort/json")
	save_lock()
	
	let data = sort_data
	data["categories"] = null; // don't update

	await fetch('/api/json/save', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify({"sort" : data})
	})
	save_lock(false)
	sort_update()
	sort_cat_update()
	disk = null
}

async function sort_apply() {
	// global lock
	document.getElementById("sw_apply").disabled = true
	lock('sort-write')
	save_lock()

	let data = await fetch("/api/sort/write");
	data = await data.json()
	console.log(data);
	if (data && data["sort"] && data["sort"]["warn"]) {
		document.getElementById("s_out").innerHTML = data["sort"]["warn"]
	} else {
		document.getElementById("s_out").innerHTML = ""
	}
	// global lock
	save_lock(false)
	unlock()
	document.getElementById("sw_apply").disabled = false

	// update
	sort_update()
	sort_cat_update()

	// propagate
	update_all()
}

function s_prev() {
	if (sort_current-(sort_grid*sort_grid) < 0) {
		return
	}
	sort_current = sort_current - (sort_grid*sort_grid)
	sort_img_table()
}

function s_next() {
	if (sort_current+(sort_grid*sort_grid) >= sort_data.images.length) {
		return
	}
	sort_current = sort_current + (sort_grid*sort_grid)
	sort_img_table()
}