function check(info){
	var check_div = document.getElementById("check")
	check_div.innerHTML = "";
	var t = document.createElement('table');
	check_div.appendChild(t)

	var th = t.createTHead();
	var r = th.insertRow(0);
	
	var c = r.insertCell(0);
	c.innerHTML = "Step"
	var c = r.insertCell(1);
	c.innerHTML = "Images"
	var c = r.insertCell(2);
	c.innerHTML = "Total Tags"
	var c = r.insertCell(3);
	c.innerHTML = "Unique Tags"

	for(const key in info) {
		r = t.insertRow();
		var c = r.insertCell(0)
		c.innerHTML = key
		var cic = r.insertCell(1)
		if (info[key]["img_count"] > 0) {
			cic.innerHTML = info[key]["img_count"]
		} else {
			cic.innerHTML = "-"
		}
		var ctc = r.insertCell(2)
		var ctu = r.insertCell(3)
		if(info[key]["tag_count"]["total"]) {
			ctc.innerHTML = info[key]["tag_count"]["total"]
			ctu.innerHTML = info[key]["tag_count"]["unique"]
		} else {
			ctc.innerHTML = "-"
			ctu.innerHTML = "-"
		}
	}
}

function check_update() {
	console.log("check")
	var ajax = new XMLHttpRequest();
	ajax.responseType = 'json';
	ajax.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) { 
			check(this.response);
		};
	};
	ajax.open('GET',"/api/check",true);
	ajax.send();
}

check_update()