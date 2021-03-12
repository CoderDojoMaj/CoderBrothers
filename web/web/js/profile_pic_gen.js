
// def Export():  # RGBA
// 	body = Image.open(bodyPath + os.listdir(bodyPath)[bodyIdx])
// 	hair = Image.open(hairPath + os.listdir(hairPath)[hairIdx])

// 	result = Image.new("RGBA", (11, 11))
// 	pixels = result.load()

// 	for y in range(11):  # IMG[11y + x]
// 		for x in range(11):
// 			if hair.getpixel((x, y))[3] == 0:  # place body's pixel
// 				pixels[x, y] = body.getpixel((x, y))
// 			else:  # place hair's pixel
// 				pixels[x, y] = hair.getpixel((x, y))
// 	#result.resize((1100, 1100))
// 	result.save("results/unscaled result.png")
// 	result.resize((1100, 1100), resample=Image.BOX).save("results/upscaled result.png")

const SIZE = 11;

function exportImage(body, hair, callback) {
	let body_img = new Image();
	body_img.src = `/img/profile_pics/bodies/${body}.png`;
	body_img.onload = function () {
		let hair_img = new Image();
		hair_img.src = `/img/profile_pics/hair/${hair}.png`;
		hair_img.onload = function () {
			let canvas = document.createElement("canvas", {
				id: "profile_pic_canvas"
			});
			canvas.width = SIZE;
			canvas.height = SIZE;
			let ctx = canvas.getContext("2d");
			ctx.drawImage(body_img, 0, 0, SIZE, SIZE);
			ctx.drawImage(hair_img, 0, 0, SIZE, SIZE);
			ctx.save();
			let new_url = canvas.toDataURL("image/png");
			canvas.remove();
			callback(new_url)
		}
	}
}

const NUM_HAIRS = 4; // Change when adding styles
const NUM_BODIES = 2; // same (mood)

var hair = 0;
var body = 0;
var image_url = '/img/profile_pics/faces/Buffed_red_soldier.jpg'

function triggerReload() {
	exportImage(body, hair, function(url) {
		document.getElementById("custom_image").src = url
		image_url = url
	})
}

document.getElementById("prev_hair").onclick = function() {
	hair -= 1
	if (hair < 0) {
		hair = NUM_HAIRS - 1
	}
	triggerReload()
}

document.getElementById("prev_body").onclick = function() {
	body -= 1
	if (body < 0) {
		body = NUM_BODIES - 1
	}
	triggerReload()
}

document.getElementById("next_hair").onclick = function() {
	hair += 1
	if (hair >= NUM_HAIRS) {
		hair = 0
	}
	triggerReload()
}

document.getElementById("next_body").onclick = function() {
	body += 1
	if (body >= NUM_BODIES) {
		body = 0
	}
	triggerReload()
}

triggerReload()

document.getElementById("set_cutom_image").onclick = function() {
	document.getElementById('update_img_base64_custom').value = image_url.substr(22)
	document.getElementById('updateButtonCustom').click()

}