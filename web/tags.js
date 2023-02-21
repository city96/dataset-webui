function tag_add_to_blacklist(tag) {
	let element = document.getElementById("t_blacklist")
	let blacklist = element.value;
	if (!blacklist.endsWith(",")) {
		blacklist = blacklist + ", "
	}
	if (blacklist.endsWith(",")) {
		blacklist = blacklist + " "
	}
	blacklist = blacklist + tag
	element.value = blacklist
}

function popular_tags(tags) {
	var table = document.getElementById("t_pop_table")
	table.innerHTML = "";

	for(const key in tags) {
		r = table.insertRow();
		let c0 = r.insertCell(0)
		c0.innerHTML = tags[key]
		
		let c1 = r.insertCell(1)
		c1.innerHTML = key
		
		let c2 = r.insertCell(2)
		b = document.createElement('button');
		c2.appendChild(b)
		b.innerHTML = "+"
		b.setAttribute('onclick','this.disabled=true; tag_add_to_blacklist("'+key+'")')
	}
}


function folder_rule_add(folder, action, target) {
	var table = document.getElementById("t_folder_rules")
	r = table.insertRow();
	var c = r.insertCell(0)
	c.innerHTML = "Folder rule"

	var c = r.insertCell(1)
	var s = document.createElement("select")
	s.id = "t_folder_rule_target"

	var categories = ["temp","test","invalid"]
	for(const key in categories) {
		var o = document.createElement("option")
		o.value = categories[key]
		o.text = categories[key]
		if (categories[key] == folder) {
			o.selected = true
		}
		s.appendChild(o);
	}
	c.appendChild(s)

	var c = r.insertCell(2)
	var s = document.createElement("select")
	c.appendChild(s)

	var o = document.createElement("option")
	o.value = "add"
	o.text = "Add"
	if (action == "add") { o.selected = true }
	s.appendChild(o);

	var o = document.createElement("option")
	o.value = "remove"
	o.text = "Remove"
	if (action == "remove") { o.selected = true }
	s.appendChild(o);

	var c = r.insertCell(3)
	var i = document.createElement("input")
	i.placeholder = "red hakama, hakama skirt, miko"
	if (target) {
		i.value = target
	}
	c.appendChild(i)
}

function folder_rule_del() {
	var table = document.getElementById("t_folder_rules")
	let lastRow = table.rows.length-1
	if (lastRow >= 0) {
		table.removeChild(table.rows[lastRow])
	}
}


function custom_rule_add(rule, source, target) {
	var table = document.getElementById("t_custom_rules")
	r = table.insertRow();

	var c = r.insertCell(0)
	var s = document.createElement("select")
	c.appendChild(s)

	var o = document.createElement("option")
	o.value = "replace"
	o.text = "Replacement rule"
	if (rule == "replace") { o.selected = true }
	s.appendChild(o);

	var o = document.createElement("option")
	o.value = "add"
	o.text = "Transitivity rule"
	if (rule == "add") { o.selected = true }
	s.appendChild(o);

	var c = r.insertCell(1)
	var i = document.createElement("input")
	i.placeholder = "miko"
	if (source) {
		i.value = source
	}
	c.appendChild(i)

	var c = r.insertCell(2)
	var i = document.createElement("input")
	i.placeholder = "red hakama, hakama skirt"
	if (target) {
		i.value = target
	}
	c.appendChild(i)
}

function custom_rule_del() {
	var table = document.getElementById("t_custom_rules")
	let lastRow = table.rows.length-1
	if (lastRow >= 0) {
		table.removeChild(table.rows[lastRow])
	}
}

function spice_rule_add(rule, perc, tags) {
	var table = document.getElementById("t_spice_rules")
	r = table.insertRow();

	var c = r.insertCell(0)
	var s = document.createElement("select")
	c.appendChild(s)

	var o = document.createElement("option")
	o.value = "add"
	o.text = "Add spice"
	if (rule == "add") { o.selected = true }
	s.appendChild(o);

	var o = document.createElement("option")
	o.value = "remove"
	o.text = "Remove Spice"
	if (rule == "remove") { o.selected = true }
	s.appendChild(o);

	var c = r.insertCell(1)
	var i = document.createElement("input")
	i.placeholder = "25"
	i.type = "number"
	i.min = 0
	i.max = 100
	if (perc) {
		i.value = perc
	}
	c.appendChild(i)

	var c = r.insertCell(2)
	var i = document.createElement("input")
	i.placeholder = "solo, 1girl"
	if (tags) {
		i.value = tags
	}
	c.appendChild(i)
}

function spice_rule_del() {
	var table = document.getElementById("t_spice_rules")
	let lastRow = table.rows.length-1
	if (lastRow >= 0) {
		table.removeChild(table.rows[lastRow])
	}
}

function image_filter_rule_add(tags) {
	var table = document.getElementById("t_image_filter_rules")
	r = table.insertRow();

	var c = r.insertCell(0)
	c.innerHTML = "Image filter rule"

	var c = r.insertCell(1)
	var i = document.createElement("input")
	i.placeholder = "1girl, 1boy"
	if (tags) {
		i.value = tags
	}
	c.appendChild(i)
}

function image_filter_rule_del() {
	var table = document.getElementById("t_image_filter_rules")
	let lastRow = table.rows.length-1
	if (lastRow >= 0) {
		table.removeChild(table.rows[lastRow])
	}
}

function image_category_rule_add(category, tags) {
	var table = document.getElementById("t_image_category_rules")
	r = table.insertRow();

	var c = r.insertCell(0)
	c.innerHTML = "Image category rule"

	var c = r.insertCell(1)
	var i = document.createElement("input")
	i.placeholder = "lum"
	if (category) {
		i.value = category
	}
	c.appendChild(i)

	var c = r.insertCell(2)
	var i = document.createElement("input")
	i.placeholder = "1girl, aqua hair, oni horns"
	if (tags) {
		i.value = tags
	}
	c.appendChild(i)
}

function image_category_rule_del() {
	var table = document.getElementById("t_image_category_rules")
	let lastRow = table.rows.length-1
	if (lastRow >= 0) {
		table.removeChild(table.rows[lastRow])
	}
}

function tags_disabled(state) {
	if (state) {
		document.getElementById("tag-div").style.color = "#888"
	} else {
		document.getElementById("tag-div").style.color = ""
	}
	
	document.getElementById("t_save").disabled = state;
	document.getElementById("t_load").disabled = state;
	document.getElementById("t_fix").disabled = state;

	document.getElementById("t_input_folder").disabled = state;
	document.getElementById("t_output_folder").disabled = state;
	document.getElementById("t_triggerword").disabled = state;
	document.getElementById("t_triggerword_extra").disabled = state;
	document.getElementById("t_whitelist").disabled = state;
	document.getElementById("t_blacklist").disabled = state;
	document.getElementById("t_booru_type").disabled = state;
	document.getElementById("t_booru_general_only").disabled = state;
	document.getElementById("t_booru_popular_only").disabled = state;
	document.getElementById("t_frequent_only").disabled = state;
	document.getElementById("t_norm_eye_color").disabled = state;
	document.getElementById("t_norm_hair_color").disabled = state;
	document.getElementById("t_norm_hair_style").disabled = state;
	document.getElementById("t_image_blacklist").disabled = state;
	document.getElementById("t_folder_rule_add").disabled = state;
	document.getElementById("t_folder_rule_del").disabled = state;
	document.getElementById("t_custom_rule_add").disabled = state;
	document.getElementById("t_custom_rule_del").disabled = state;
	document.getElementById("t_spice_rule_add").disabled = state;
	document.getElementById("t_spice_rule_del").disabled = state;
	document.getElementById("t_image_filter_rule_add").disabled = state;
	document.getElementById("t_image_filter_rule_del").disabled = state;
	document.getElementById("t_image_category_rule_add").disabled = state;
	document.getElementById("t_image_category_rule_del").disabled = state;
	
	['t_folder_rules', 't_custom_rules', 't_spice_rules', 't_image_filter_rules', 't_image_category_rules'].forEach(function(id){
		var table = document.getElementById(id)
		let lastRow = table.rows.length-1
		while (lastRow >= 0) {
			table.removeChild(table.rows[lastRow])
			lastRow = table.rows.length-1;
		}
	})
}

function tag_json_clear() {
	document.getElementById("t_input_folder").value = "3 - tagged";
	document.getElementById("t_output_folder").value = "4 - fixed";
	document.getElementById("t_triggerword").value = "";
	document.getElementById("t_triggerword_extra").value = "";
	document.getElementById("t_whitelist").value = "";
	document.getElementById("t_blacklist").value = "Blurry, motion blur, chromatic aberration";
	document.getElementById("t_booru_type").value = "danbooru";
	document.getElementById("t_booru_general_only").checked = true;
	document.getElementById("t_booru_popular_only").value = "2500";
	document.getElementById("t_frequent_only").value = "2";
	document.getElementById("t_norm_eye_color").value = "";
	document.getElementById("t_norm_hair_color").value = "";
	document.getElementById("t_norm_hair_style").value = "";
	document.getElementById("t_image_blacklist").value = "";
	
	['t_folder_rules', 't_custom_rules', 't_spice_rules', 't_image_filter_rules', 't_image_category_rules'].forEach(function(id){
		var table = document.getElementById(id)
		let lastRow = table.rows.length-1
		while (lastRow >= 0) {
			table.removeChild(table.rows[lastRow])
			lastRow = table.rows.length-1;
		}
	})
}

function tag_json_get() {
	data = {}
	data["folder_input"] = document.getElementById("t_input_folder").value;
	data["folder_output"] = document.getElementById("t_output_folder").value;
	data["triggerword"] = document.getElementById("t_triggerword").value;
	data["triggerword_extra"] = document.getElementById("t_triggerword_extra").value;
	data["whitelist"] = document.getElementById("t_whitelist").value;
	data["blacklist"] = document.getElementById("t_blacklist").value;
	data["booru"] = {};
	data["booru"]["type"] = document.getElementById("t_booru_type").value;
	data["booru"]["general_only"] = document.getElementById("t_booru_general_only").checked;
	data["booru"]["popular_only"] = document.getElementById("t_booru_popular_only").value;
	data["frequent_only"] = document.getElementById("t_frequent_only").value;
	data["normalize"] = {};
	data["normalize"]["eye_color"] = document.getElementById("t_norm_eye_color").value;
	data["normalize"]["hair_color"] = document.getElementById("t_norm_hair_color").value;
	data["normalize"]["hair_style"] = document.getElementById("t_norm_hair_style").value;
	data["image_blacklist"] = document.getElementById("t_image_blacklist").value;

	data["folder_rules"] = [];
	var t = document.getElementById("t_folder_rules");
	for (var i = 0, r; r = t.rows[i]; i++) {
		var a = {}
		a["folder"] = r.cells[1].getElementsByTagName('select')[0].value
		a["action"] = r.cells[2].getElementsByTagName('select')[0].value
		a["target"] = r.cells[3].getElementsByTagName('input')[0].value
		data["folder_rules"].push(a)
	}

	data["custom_rules"] = [];
	var t = document.getElementById("t_custom_rules");
	for (var i = 0, r; r = t.rows[i]; i++) {
		var a = {}
		a["type"] = r.cells[0].getElementsByTagName('select')[0].value
		a["source"] = r.cells[1].getElementsByTagName('input')[0].value
		a["target"] = r.cells[2].getElementsByTagName('input')[0].value
		data["custom_rules"].push(a)
	}

	data["spice_rules"] = [];
	var t = document.getElementById("t_spice_rules");
	for (var i = 0, r; r = t.rows[i]; i++) {
		var a = {}
		a["type"] = r.cells[0].getElementsByTagName('select')[0].value
		a["percent"] = r.cells[1].getElementsByTagName('input')[0].value
		a["target"] = r.cells[2].getElementsByTagName('input')[0].value
		data["spice_rules"].push(a)
	}

	data["filter_rules"] = [];
	var t = document.getElementById("t_image_filter_rules");
	for (var i = 0, r; r = t.rows[i]; i++) {
		var a = {}
		a["target"] = r.cells[1].getElementsByTagName('input')[0].value
		data["filter_rules"].push(a)
	}

	data["category_rules"] = [];
	var t = document.getElementById("t_image_category_rules");
	for (var i = 0, r; r = t.rows[i]; i++) {
		var a = {}
		a["category"] = r.cells[1].getElementsByTagName('input')[0].value
		a["target"] = r.cells[2].getElementsByTagName('input')[0].value
		data["category_rules"].push(a)
	}

	return data
}

function tag_json_load(data) {
	tag_json_clear();
	if(data["folder_input"]){ document.getElementById("t_input_folder").value = data["folder_input"]; };
	if(data["folder_output"]){ document.getElementById("t_output_folder").value = data["folder_output"]; };
	if(data["triggerword"]){ document.getElementById("t_triggerword").value = data["triggerword"]; };
	if(data["triggerword_extra"]) { document.getElementById("t_triggerword_extra").value = data["triggerword_extra"]; };
	if(data["whitelist"]){ document.getElementById("t_whitelist").value = data["whitelist"]; };
	if(data["blacklist"]){ document.getElementById("t_blacklist").value = data["blacklist"]; };
	if(data["booru"]){
		if(data["booru"]["type"]){ document.getElementById("t_booru_type").value = data["booru"]["type"]; };
		if(data["booru"]["general_only"]){ document.getElementById("t_booru_general_only").checked = data["booru"]["general_only"]; };
		if(data["booru"]["popular_only"]){ document.getElementById("t_booru_popular_only").value = data["booru"]["popular_only"]; };
	}
	if(data["frequent_only"]){ document.getElementById("t_frequent_only").value = data["frequent_only"]; };
	if(data["normalize"]){
		if(data["normalize"]["eye_color"]){ document.getElementById("t_norm_eye_color").value = data["normalize"]["eye_color"]; };
		if(data["normalize"]["hair_color"]){ document.getElementById("t_norm_hair_color").value = data["normalize"]["hair_color"]; };
		if(data["normalize"]["hair_style"]){ document.getElementById("t_norm_hair_style").value = data["normalize"]["hair_style"]; };
	}
	if(data["image_blacklist"]){ document.getElementById("t_image_blacklist").value = data["image_blacklist"] };

	if(data["folder_rules"]){data["folder_rules"].forEach(function(a) {
		folder_rule_add(a["folder"],a["action"],a["target"])
	})}

	if(data["custom_rules"]){data["custom_rules"].forEach(function(a) {
		custom_rule_add(a["type"],a["source"],a["target"])
	})}

	if(data["spice_rules"]){data["spice_rules"].forEach(function(a) {
		spice_rule_add(a["type"],a["percent"],a["target"])
	})}

	if(data["filter_rules"]){data["filter_rules"].forEach(function(a) {
		image_filter_rule_add(a["target"])
	})}

	if(data["category_rules"]){data["category_rules"].forEach(function(a) {
		image_category_rule_add(a["category"],a["target"])
	})}
	
	return
}

async function save_tag_json() {
	console.log("Save tag/json")
	document.getElementById("t_save").disabled = true;
	document.getElementById("t_load").disabled = true;
	document.getElementById("t_fix").disabled = true;
	let data = {}
	data["tags"] = tag_json_get()

	await fetch('/api/json/save', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json; charset=UTF-8'
		},
		body: JSON.stringify(data)
	})
	console.log(data)

	document.getElementById("t_save").disabled = false;
	document.getElementById("t_load").disabled = false;
	document.getElementById("t_fix").disabled = false;
	update_status(true)
}

async function fix_tags() {
	save_tag_json()
	console.log("run")
	let data = await fetch("/api/tags/run");
	data = await data.json()
	console.log(data);
	
	document.getElementById("t_output").innerHTML = data["tags"]["status"];
	document.getElementById("t_warn").innerHTML = data["tags"]["warn"];
	console.log(data["tags"]["popular"])
	popular_tags(data["tags"]["popular"])

	update_status(true)
}