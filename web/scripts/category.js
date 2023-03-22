function sort_cat_updateTable(categories) {
	let table = document.getElementById("sort-cat-table")
	table.innerHTML = "";
	
	for(const cat of categories) {
		r = table.insertRow();
		let c0 = r.insertCell(0)
		c0.innerHTML = cat.name

		let c1 = r.insertCell(1)
		// c1.innerHTML = cat.weight
		//<input type="range" min="1" max="100" value="50" class="slider" id="myRange">
		let i = document.createElement("input")
		i.type = "range"
		i.min = 1
		i.max = 5
		i.value = cat.weight
		i.setAttribute("oninput", "this.nextElementSibling.value = this.value")
		i.setAttribute("onchange", "lock('sort-cat-div')")
		i.classList.add("cat_slider")
		c1.appendChild(i)

		let ip = document.createElement("input")
		ip.type = "number"
		ip.min = 1
		ip.value = cat.weight
		ip.setAttribute("oninput", "this.previousElementSibling.value = this.value")
		ip.setAttribute("onchange", "lock('sort-cat-div')")
		ip.classList.add("cat_slide_val")
		c1.appendChild(ip)
		
		let c2 = r.insertCell(2)
		let ic = document.createElement("input")
		ic.type = "color"
		ic.value = cat.color
		ic.setAttribute("onchange", "lock('sort-cat-div')")
		c2.appendChild(ic)

		let c3 = r.insertCell(3)
		let ik = document.createElement("input")
		ik.type = "checkbox"
		if (cat.disk) {
			ik.checked = true
			ik.disabled = true
			ik.title = "This category is based on a folder on the disk"
		} else { 
			ik.checked = cat.keep
		}
		ik.setAttribute("onchange", "lock('sort-cat-div')")
		ik.classList.add("cat_keep_check")
		c3.appendChild(ik)

		let c4 = r.insertCell(4)
		c4.innerHTML = cat.count	
		
		if (cat.name == "default") {
			i.disabled = true
			ip.disabled = true
			ic.value = "#555555"
			ic.disabled = true
			ik.checked = true
			ik.disabled = true
			ik.title = "This is the default category"
		}
	}
}

var disk = null
async function sort_cat_disk() {
	let c = confirm("Are you sure want to load the data from the output folder? Only do this if you manually sorted your images (i.e. by copying them to folders in the output directory). Clicking save after loading will REPLACE ALL SORTING DATA WITH THE VALUES FROM THE OUTPUT FOLDER.");
	if (!c) { return };

	let data = await fetch("/api/category/disk");
	data = await data.json()
	
	if (data == undefined || data.sort == undefined || data.sort.categories.length == 0) {
		sort_cat_update()
		return
	}
	if (data.sort.images.length > 0) {
		disk = data["sort"]["images"]
	}
	sort_cat_updateTable(data["sort"]["categories"])
	// no add
	document.getElementById("sc_new_name").disabled = true;
	document.getElementById("sc_new_add").disabled = true;
}

async function sort_cat_update(new_cat = null) {
	let data = await fetch("/api/category/info");
	data = await data.json()
	disk = null
	
	if (!data || !data.sort || !data.sort.images || data.sort.images.length == 0) {
		if (data.warn) { 
			disable_module("sort-cat-div", data.warn)
		} else {
			disable_module("sort-cat-div", "Nothing to load from disk")
		}
		return
	} else {
		if (!new_cat) { 
			enable_module("sort-cat-div")
			document.getElementById("sc_new_name").disabled = false;
			document.getElementById("sc_new_add").disabled = false;
			document.getElementById("sc_load").disabled = false;
		}
	}
	if (new_cat) { data["sort"]["categories"].push(new_cat) }
	sort_cat_updateTable(data["sort"]["categories"])
}

async function sort_cat_json_save() {
	console.log("Save sort/cat/json")
	save_lock()
	
	let data = {}
	data["categories"] = [];
	if (disk) { data["images"] = disk }
	var t = document.getElementById("sort-cat-table");
	for (var i = 0, r; r = t.rows[i]; i++) {
		var c = {}
		c["name"] = r.cells[0].innerHTML
		c["weight"] = r.cells[1].getElementsByClassName("cat_slide_val")[0].value
		c["color"] = r.cells[2].getElementsByTagName('input')[0].value
		c["keep"] = r.cells[3].getElementsByClassName("cat_keep_check")[0].checked
		data["categories"].push(c)
	}

	await fetch('/api/json/save', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify({"sort" : data})
	})
	save_lock(false)
	sort_cat_update()
	sort_update()
	disk = null
}

function sort_cat_add() {
	let name = document.getElementById("sc_new_name").value
	if (name && name.length == 0) {
		return
	}
	document.getElementById("sc_new_name").disabled = true;
	document.getElementById("sc_new_add").disabled = true;

	let cat = {
		"name" : name,
		"weight" : 1,
		"color" : "#555555",
		"keep" : true,
		"count" : 0,
	}
	lock('sort-cat-div')
	document.getElementById("sc_new_name").value = null
	sort_cat_update(cat)
}