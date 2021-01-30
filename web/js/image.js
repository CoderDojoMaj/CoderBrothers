const IMG_WIDTH = 128
const IMG_HEIGHT = 128

function loadPictureAsURL(input_el,callback) {
	let file = input_el.files[0];
	let reader = new FileReader();

	reader.onloadend = function () {
		let picURL = reader.result;
		resizeImage(picURL, IMG_WIDTH, IMG_HEIGHT, function (picURL) {
			document.getElementById('pic').src = picURL
			if (callback) callback(picURL);
		});
	}
	if (file) {
		reader.readAsDataURL(file); //reads the data as a URL
	} else {
		callback(undefined);
	}
}

function resizeImage(URL, width, height, callback) {
	let img = new Image();
	img.src = URL;
	img.onload = function () {
		let canvas = document.createElement("canvas", {
			id: "resize_canvas"
		});
		canvas.width = width;
		canvas.height = height;
		let ctx = canvas.getContext("2d");
		ctx.drawImage(img, 0, 0, width, height);
		ctx.save();
		let new_url = canvas.toDataURL("image/png");
		canvas.remove();
		callback(new_url);
	}
}

document.getElementById('image').onchange = ()=>{
	loadPictureAsURL(document.getElementById('image'), (url)=>{
		console.log(url.substr(22))
		document.getElementById('update_img_base64').value = url.substr(22)
		document.getElementById('form').classList.remove('hidden')
	})
}

const img = document.getElementById("image");

img.addEventListener('change',() =>{
	document.getElementById("updateButton").disabled = false;
})