(function () {
	"use strict";

	// Do something with the response data
	// Since the visitor will leave the page we don't need this
	onResponse = function () {
		if (httpRequest.readyState == 4) {
			if (httpRequest.status === 200) {
				// Do something with httpRequest.responseText
			} else {
				console.error('Error in sending ajax request');
			}
		}
	}

	makeRequest = function (url) {
		var httpRequest;

		// Checks if browser is IE7+
		if (window.XMLHttpRequest) {
			httpRequest = new XMLHttpRequest();
		} else if (window.ActiveXObject) {
			httpRequest = new ActiveXObject("Microsoft.XMLHTTP");
		}

		httpRequest.open("GET", url);
		httpRequest.send();

		httpRequest.onreadystatechange = onResponse;
	};

	window.onbeforeunload = makeRequest('http://localhost:8080')
})();