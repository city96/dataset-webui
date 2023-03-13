// target category for selector
var sort_tcat

function sort_set_tcat(cat) {
	sort_tcat = cat
	let r = document.querySelector(':root');
	let color = sort_data.categories[sort_tcat].color
	r.style.setProperty('--tcat', color);
}

function sort_img_create_cel(image, div) {
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
	img.src =  "/img/1 - cropped/" + image.filename

	div.style.borderColor = sort_data.categories[image.category].color
	return div
}

function sort_img_table(images) {
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

			div = sort_img_create_cel(images[sort_current+i], div)

			i++
			if ((sort_current+i) >= images.length) {
				return
			}
		}
	}
}

var sort_data
var sort_current = 0
var sort_grid = 3
async function sort_update() {
	lock_update()
	let data = await fetch("/api/sort/info");
	data = await data.json()
	
	if (data == undefined || data.sort == undefined || data.sort.categories.length == 0) {
		document.getElementById("sort-float-warn").style.display = "block"; 
		document.getElementById("sort-float-warn").innerHTML = "Nothing to load from disk"
		lock_update(false)
		return
	} else {
		document.getElementById("sort-div").classList.remove("locked");
		document.getElementById("sort-float-warn").style.display = "none";
	}
	sort_data = data.sort
	if (!sort_tcat) {
		sort_set_tcat("default")
	}
	
	sort_img_table(sort_data.images)
	lock_update(false)
}

function s_prev() {
	if (sort_current-(sort_grid*sort_grid) < 0) {
		return
	}
	sort_current = sort_current - (sort_grid*sort_grid)
	sort_img_table(sort_data.images)
}

function s_next() {
	if (sort_current+(sort_grid*sort_grid) >= sort_data.images.length) {
		return
	}
	sort_current = sort_current + (sort_grid*sort_grid)
	sort_img_table(sort_data.images)
}

document.addEventListener("DOMContentLoaded", function() {
	sort_update()
});