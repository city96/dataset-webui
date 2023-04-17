
var tag_seq_start = 0
var tag_seq_end = 0
var tag_seq_data
async function tag_seq_update() {
	let data = await fetch("/api/tags/seq")
	data = await data.json()
	if (!data || data.length == 0) {
		tag_seq_data = []
	} else {
		tag_seq_data = data
	}
	console.log(tag_seq_data)
	document.getElementById("ts_img_start_id").max = tag_img_data.length-1
	document.getElementById("ts_img_end_id").max = tag_img_data.length-1
	tag_seq_img_start_update()
	tag_seq_img_end_update()
	tag_seq_table()
	unlock()
}

function tag_seq_table() {
	let table = document.getElementById("ts_seq_table")
	table.innerHTML = ""
	for (const seq of tag_seq_data) {
		r = table.insertRow();
		let c0 = r.insertCell(0)
		c0.innerHTML = seq.tags
		let c1 = r.insertCell(1)
		c1.innerHTML = seq.start
		let c2 = r.insertCell(2)
		c2.innerHTML = seq.end
		let c3 = r.insertCell(3)
		c3.innerHTML = seq.from
		let c4 = r.insertCell(4)
		c4.innerHTML = seq.to
		let c5 = r.insertCell(5)
		let b = document.createElement("button")
		c5.appendChild(b)
		b.innerHTML = "x"
		b.setAttribute('onclick','lock("tag-seq-div"); tag_seq_del_seq("'+seq.tags+'")')
	}
}

function tag_seq_del_seq(tags) {
	tag_seq_data = tag_seq_data.filter(function(i){return (i.tags!==tags)})
	tag_seq_table()
}

function tag_seq_add_seq() {
	let tags = document.getElementById("ts_tag").value
	if (!tags) return
	let nd = {
		"tags" : tags,
		"start" : tag_img_data[tag_seq_start].filename,
		"end" : tag_img_data[tag_seq_end].filename,
		"from" : parseFloat(document.getElementById("ts_from").value),
		"to" : parseFloat(document.getElementById("ts_to").value),
	}		
	lock("tag-seq-div")
	tag_seq_data.push(nd)
	document.getElementById("ts_tag").value = ""
	tag_seq_table()
}

async function tag_seq_save() {
	console.log("Save tag/seq/json")
	save_lock()
	
	await fetch('/api/json/save', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify({"tags" : {"sequences" : tag_seq_data}})
	})
	save_lock(false)
	tag_seq_update()
}

function tag_seq_img_start_update() {
	tag_seq_start = parseInt(document.getElementById("ts_img_start_id").value)
	document.getElementById("ts_img_start").src = tag_img_data[tag_seq_start].img_url
	document.getElementById("ts_img_end_id").style.accentColor = (tag_seq_end < tag_seq_start) ? "red" : ""
}

function tag_seq_img_end_update() {
	tag_seq_end = parseInt(document.getElementById("ts_img_end_id").value)
	document.getElementById("ts_img_end").src = tag_img_data[tag_seq_end].img_url
	document.getElementById("ts_img_end_id").style.accentColor = (tag_seq_end < tag_seq_start) ? "red" : ""
}
