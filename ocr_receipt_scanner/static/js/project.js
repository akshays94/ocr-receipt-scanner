/* Project specific Javascript goes here. */
console.log("project activated");

console.log("claims upload activated");

var form 			= document.getElementById("upload-form");
var fileSelect 		= document.getElementById("file-select");
var uploadButton 	= document.getElementById("upload-button");
var imageTag 		= document.getElementById("my-image");
var rotateBtn 		= document.getElementById("rotate-button");
var msg 			= document.getElementById("msg");

var csrf = document.getElementsByName("csrfmiddlewaretoken")[0].value;

console.log(fileSelect);

var croppie;

rotateBtn.onclick = function (event) {
	console.log("rotate button clicked");
    croppie.rotate(90);
}

fileSelect.onchange = function (event) {
	
	console.log("change", event);

	msg.innerHTML = '';

	var files = fileSelect.files;
	var file = files[0];

	var fr = new FileReader();
	var imageUrl = fr.readAsDataURL(file);

	if (croppie !== undefined) {
		croppie.destroy();
	}

	fr.addEventListener ('load', function () {
		// console.log('url', fr.result);

		imageTag.setAttribute("src", fr.result);

		croppie = new Croppie(imageTag, {
		    // viewport: { width: 100, height: 100 },
		    // boundary: { width: 300, height: 300 },
		    viewport: { width: 300, height: 300 },
		    boundary: { width: 400, height: 400 },
		    showZoomer: false,
		    enableOrientation: true,
		    enableResize: true,
		    enableZoom: true,
		    mouseWheelZoom: 'ctrl'
		});
		
	})

}

form.onsubmit = function (event) {
	
	event.preventDefault();
	msg.innerHTML = '';

	croppie.result('blob').then(function(blob) {
	    
	    // do something with cropped blob
	    console.log("result blob", blob);
		
		uploadButton.innerHTML = "Uploading... Please wait ...";

		// var files = fileSelect.files;

		// var file = files[0];
		// console.log(files, file);

		// var isValidImageFile = file.type.match('image.*')

		var isValidImageFile = true;

		if (isValidImageFile) {
			
			var formData = new FormData();
			// formData.append("receipt", file, file.name);

			if (blob.content_type === 'image/png') {
				var fileName = 'akshay.png';
			} else {
				var fileName = 'akshay.png';						
			}

			formData.append("receipt", blob, fileName);
			formData.append("csrfmiddlewaretoken", csrf);

			for (var pair of formData.entries()) {
			    console.log(pair[0]+ ', ' + pair[1]); 
			}

			var xhr = new XMLHttpRequest();
			xhr.open('POST', form.action, true);
			
			xhr.onload = function () {
				if (xhr.status === 200) {

					msg.innerHTML = 'File uploaded successfully';
					uploadButton.innerHTML = 'Upload';

				} else {

					alert('An error occurred!');

				}
			};

			xhr.send(formData);


		} else {
			alert("Please select a valid image file");
			uploadButton.innerHTML = "Upload";
		}
	});




}