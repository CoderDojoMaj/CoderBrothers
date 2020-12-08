function _open() {
	document.getElementById('menu').style.display = "flex";
	/*document.getElementById('openMenu').style.paddingBottom= "4vh";*/
	setTimeout(() => { document.getElementById("menu").style.width = "70vw"; }, 10);
}
function _close() {
	document.getElementById('menu').style.width = "0";
	/*document.getElementById('openMenu').style.paddingBottom= "none";*/
	setTimeout(() => { document.getElementById("menu").style.display = "none"; }, 500);
}