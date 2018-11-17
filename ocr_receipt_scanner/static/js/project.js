$(document).ready(function () {

	/* Project specific Javascript goes here. */
	console.log("project activated");

	console.log("claims upload activated");

	var form 			= document.getElementById("upload-form");
	var fileSelect 		= document.getElementById("file-select");
	var uploadButton 	= document.getElementById("upload-button");
	var imageTag 		= document.getElementById("my-image");
	var rotateBtn 		= document.getElementById("rotate-button");
	var msg 			= document.getElementById("msg");
	var previewImage	= document.getElementById("previewimg");

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

		$(rotateBtn).removeClass("disabled");
		$(uploadButton).removeClass("disabled");

		var files = fileSelect.files;
		var file = files[0];

		var fr = new FileReader();
		var imageUrl = fr.readAsDataURL(file);

		if (croppie !== undefined) {
			croppie.destroy();
		}

		fr.addEventListener ('load', function () {

			$(rotateBtn).removeClass("hidden");
			$(uploadButton).removeClass("hidden");

			imageTag.setAttribute("src", fr.result);

			// var viewportSize = 300;
			// var boundarySize = 400;
			var viewportSize = 300 - 50;
			var boundarySize = 400 - 100;

			croppie = new Croppie(imageTag, {
			    viewport: { width: viewportSize, height: viewportSize },
			    boundary: { width: boundarySize, height: boundarySize },
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
		    
		    console.log("result blob", blob);
			
			msg.innerHTML 
				= '<i class="fa fa-circle-o-notch fa-spin" style="color: red"></i> Uploading and scanning receipt... Please wait ... ';

			$(rotateBtn).addClass("disabled");
			$(uploadButton).addClass("disabled");

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

						msg.innerHTML = '<i class="fa fa-check check" style="color: green"></i> Receipt uploaded successfully';
						uploadButton.innerHTML = 'Upload';
						
						response = JSON.parse(xhr.response);

						results = response.results;

						console.log(results)

						console.log(results.receipt_no, results.receipt_amt);
						
						// <button type="button" class="btn btn-secondary btn-sm">Small button</button>

						var receiptNoData = results.receipt_no;
						var receiptAmtData = results.receipt_amt;

						if (receiptNoData !== undefined) {
							$receiptNoContainer = $(".button-container[data-type=receiptno]");
							$receiptNoInput = $("input.receiptnoinput");

							$receiptNoInput
								.attr("value", receiptNoData[0])
								.parents(".form-group")
								.removeClass("is-empty");	


							$.each(receiptNoData, function(index, value) {
								var button = document.createElement("button");
								$(button).attr("type", "button");
								$(button).attr("data-type", "receiptno");;
								$(button).attr("data-value", value);
								$(button).addClass("btn btn-secondary btn-sm suggestbtn");
								$(button).html(value);
								$receiptNoContainer.append(button);
							})
						}

						if (receiptAmtData !== undefined) {
							$receiptAmtContainer = $(".button-container[data-type=receiptamt]");
							$receiptAmtInput = $("input.receiptamtinput");

							$receiptAmtInput
								.attr("value", receiptAmtData[0])
								.parents(".form-group")
								.removeClass("is-empty");	

							$.each(receiptAmtData, function(index, value) {
								var button = document.createElement("button");
								$(button).attr("type", "button");
								$(button).attr("data-type", "receiptamt");
								$(button).attr("data-value", value);
								$(button).addClass("btn btn-secondary btn-sm suggestbtn");
								$(button).html(value);
								$receiptAmtContainer.append(button);
							})
							
						}

						setTimeout(function () {
							$(".btn-next").trigger("click");
						}, 1000);

					} else {

						alert('An error occurred!');

					}
				};

				setTimeout(function() {

				xhr.send(formData);
				}, 2000)


			} else {
				alert("Please select a valid image file");
				uploadButton.innerHTML = "Upload";
			}
		});

	}

	$("body").on("click", ".suggestbtn", function () {
		console.log("suggestbtn");

		$self = $(this);

		var dataType = $self.attr("data-type");
		var value = $self.attr("data-value");	

		$receiptNoInput = $("input.receiptnoinput");
		$receiptAmtInput = $("input.receiptamtinput");

		switch(dataType) {
			case "receiptno":
				$container = $receiptNoInput;
				break;
			case "receiptamt":
				$container = $receiptAmtInput;
				break;
		}

		console.log($container, value);

		$container
			.attr("value", value)
			.parents(".form-group")
			.removeClass("is-empty");	
	})
	
	$('.wizard-card').bootstrapWizard({
        'tabClass': 'nav nav-pills',
        'nextSelector': '.btn-next',
        'previousSelector': '.btn-previous',

        onNext: function(tab, navigation, index) {
        	// var $valid = $('.wizard-card form').valid();
        	// if(!$valid) {
        	// 	$validator.focusInvalid();
        	// 	return false;
        	// }
        	console.log("next tab", $(tab), $(navigation), index);
        	return true;
        },

        onInit : function(tab, navigation, index){
            //check number of tabs and fill the entire row
            var $total = navigation.find('li').length;
            var $wizard = navigation.closest('.wizard-card');

            $first_li = navigation.find('li:first-child a').html();
            $moving_div = $('<div class="moving-tab">' + $first_li + '</div>');
            $('.wizard-card .wizard-navigation').append($moving_div);

            refreshAnimation($wizard, index);

            $('.moving-tab').css('transition','transform 0s');
       },

        onTabClick : function(tab, navigation, index){
            // var $valid = $('.wizard-card form').valid();

            // if(!$valid){
            //     return false;
            // } else{
            //     return true;
            // }
            console.log("click tab", $(tab), $(navigation), index);
            return false;
        },

        onTabShow: function(tab, navigation, index) {
            var $total = navigation.find('li').length;
            var $current = index+1;

            var $wizard = navigation.closest('.wizard-card');

            // If it's the last tab then hide the last button and show the finish instead
            if($current >= $total) {
                $($wizard).find('.btn-next').hide();
                $($wizard).find('.btn-finish').show();
            } else {
                $($wizard).find('.btn-next').show();
                $($wizard).find('.btn-finish').hide();
            }

            button_text = navigation.find('li:nth-child(' + $current + ') a').html();

            setTimeout(function(){
                $('.moving-tab').text(button_text);
            }, 150);

            var checkbox = $('.footer-checkbox');

            if( !index == 0 ){
                $(checkbox).css({
                    'opacity':'0',
                    'visibility':'hidden',
                    'position':'absolute'
                });
            } else {
                $(checkbox).css({
                    'opacity':'1',
                    'visibility':'visible'
                });
            }

            refreshAnimation($wizard, index);
        }
  	});

  	function refreshAnimation($wizard, index){
	    $total = $wizard.find('.nav li').length;
	    $li_width = 100/$total;

	    total_steps = $wizard.find('.nav li').length;
	    move_distance = $wizard.width() / total_steps;
	    index_temp = index;
	    vertical_level = 0;

	    mobile_device = $(document).width() < 600 && $total > 3;

	    if(mobile_device){
	        move_distance = $wizard.width() / 2;
	        index_temp = index % 2;
	        $li_width = 50;
	    }

	    $wizard.find('.nav li').css('width',$li_width + '%');

	    step_width = move_distance;
	    move_distance = move_distance * index_temp;

	    $current = index + 1;

	    if($current == 1 || (mobile_device == true && (index % 2 == 0) )){
	        move_distance -= 8;
	    } else if($current == total_steps || (mobile_device == true && (index % 2 == 1))){
	        move_distance += 8;
	    }

	    if(mobile_device){
	        vertical_level = parseInt(index / 2);
	        vertical_level = vertical_level * 38;
	    }

	    $wizard.find('.moving-tab').css('width', step_width);
	    $('.moving-tab').css({
	        'transform':'translate3d(' + move_distance + 'px, ' + vertical_level +  'px, 0)',
	        'transition': 'all 0.5s cubic-bezier(0.29, 1.42, 0.79, 1)'

	    });
	}
});
