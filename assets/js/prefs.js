var prefsDiv = null;

/* Firefox update on Linux turned the flicker from a quirky feature to a source
   of extreme lag. The flicker effect is now disabled by default. */
if (!localStorage.getItem("textflicker")) {
	localStorage.setItem("textflicker", 0);
}

function settings() {
	if (prefsDiv == null) {
		prefsDiv = document.createElement("div");
		
		var prefsHeader = document.createElement("h1");
		prefsHeader.innerHTML = "Settings";
		
		toggleFlickerBtn = makeButton("Toggle Flicker Effect", "toggleFlicker()");
		changeColorBtn = makeButton("Change Page Color", "cycleColor()");
		
		prefsDiv.appendChild(prefsHeader);
		prefsDiv.appendChild(toggleFlickerBtn);
		prefsDiv.appendChild(changeColorBtn);
		
		var mainDiv = document.getElementById("main");
		var body = document.body;
		
		body.insertBefore(prefsDiv, mainDiv);
	} else {
		prefsDiv.remove();
		prefsDiv = null;
	}
}

function makeButton(text, event) {
	var btnp = document.createElement("p");
	var btn = document.createElement("a");
	btn.innerHTML = text;
	btn.style = "font-size: 28px";
	btn.href = "javascript:" + event;
	btnp.appendChild(btn);
	return btnp;
}

function toggleFlicker() {
	if (!localStorage.getItem("textflicker")) {
		localStorage.setItem("textflicker", 1);
	}
	var textFlicker = parseInt(localStorage.getItem("textflicker"));
	if (textFlicker == 1)
		textFlicker = 0;
	else
		textFlicker = 1;
	localStorage.setItem("textflicker", textFlicker);
	setFlickerProperty();
}

var textColors = [
	[
		"--bg-color-primary", "#000b00",
		"--bg-color-secondary", "#002300",
		"--fg-color-primary", "#009927",
		"--fg-color-secondary", "#003b00",
		"--fg-color-bold", "#00ff41",
		"--fx-color-primary", "#4c754c"
	],
	[
		"--bg-color-primary", "#0b0800",
		"--bg-color-secondary", "#231a00",
		"--fg-color-primary", "#997300",
		"--fg-color-secondary", "#3b2c00",
		"--fg-color-bold", "#ffa800",
		"--fx-color-primary", "#75674c"
	],
	[
		"--bg-color-primary", "#00080a",
		"--bg-color-secondary", "#001e24",
		"--fg-color-primary", "#007f99",
		"--fg-color-secondary", "#00313b",
		"--fg-color-bold", "#00d4ff",
		"--fx-color-primary", "#4c6b75"
	],
	[
		"--bg-color-primary", "#0b0b0b",
		"--bg-color-secondary", "#232323",
		"--fg-color-primary", "#606060",
		"--fg-color-secondary", "#3b3b3b",
		"--fg-color-bold", "#e0e0e0",
		"--fx-color-primary", "#7a7a7a"
	]
];

function cycleColor() {
	if (!localStorage.getItem("textcolor")) {
		localStorage.setItem("textcolor", 0);
	}
	var textColor = parseInt(localStorage.getItem("textcolor")) + 1;
	if (textColor > 3)
		textColor = 0;
	localStorage.setItem("textcolor", textColor);
	setColorProperty();
}

function setFlickerProperty() {
	var textFlicker = parseInt(localStorage.getItem("textflicker"));
	var pageAnimation = "none";
	if (textFlicker == 1) {
		pageAnimation = "flicker 0.15s infinite";
	}
	document.documentElement.style.setProperty("--page-animation", pageAnimation);
}

function setColorProperty() {
	var textColor = parseInt(localStorage.getItem("textcolor"));
	var textColorGroup = textColors[textColor];
	for (var i = 0; i < textColorGroup.length; i += 2) {
		document.documentElement.style.setProperty(textColorGroup[i], textColorGroup[i+1]);
	}
}

//load prefs on page load

if (localStorage.getItem("textflicker")) {
	setFlickerProperty();
}

if (localStorage.getItem("textcolor")) {
	setColorProperty();
}
