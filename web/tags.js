
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

function image_filter_rule_add(rule, tags) {
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

function image_category_rule_add(rule, category, tags) {
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
	data["folder_rules"] = {};
	var t = document.getElementById("t_folder_rules");
	for (var i = 0, r; r = t.rows[i]; i++) {
		
	}
	
	return data
}

function save_json_callback() {
	var asd = tag_json_get()
	var a = document.getElementById("t_output")
	a.innerHTML = JSON.stringify(asd, null, 2);
}

function save_json(data) {
	var tag_data = tag_json_get()
	// var data = status_json_get()
	data = JSON.stringify(tag_data)

	var ajax = new XMLHttpRequest();
	ajax.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) { 
			save_json_callback(this.response);
		};
	};
	ajax.open('POST',"/api/json/save",true);
	ajax.setRequestHeader('Content-type', 'application/json; charset=UTF-8')

	console.log(data)
	ajax.send(data);
}

function load_json() {
	var asd = tag_json_get()
	var a = document.getElementById("t_output")
	a.innerHTML = JSON.stringify(asd, null, 2);
}