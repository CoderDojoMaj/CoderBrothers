//Opens the LogIn and SignUp forms
function onLogIn() {
	document.getElementById("logIn").style.display = "flex";
}

function onSignUp() {
	document.getElementById("signUp").style.display = "flex";
	console.log(document.getElementById("signUp"))
}

//Closes the LogIn and SignUp forms
function offLogIn(event, cliked) {
	let modal = document.getElementById("logIn")
	if (event.target === cliked) {
		modal.style.display = "none";
	}
}

function offSignUp(event, cliked) {
	let modal = document.getElementById("signUp")
	if (event.target === cliked) {
		modal.style.display = "none";
	}
}

//Opens the Dropdown menu
function showDropdown() {
document.getElementById("dropdownContent").classList.toggle("show");
}

//Closes the Dropdown menu if you click outside of it
window.onclick = function(event) {
if (!event.target.matches('.dropbtn')) {
	var dropdowns = document.getElementsByClassName("dropdown-content");
	var i;
	for (i = 0; i < dropdowns.length; i++) {
	var openDropdown = dropdowns[i];
	if (openDropdown.classList.contains('show')) {
		openDropdown.classList.remove('show');
	}
	}
}
}

//Function used in SignUp form to chek if the too paswors are correct
function check() {
	let pass=document.getElementById('p');
	let confpass=document.getElementById('rp');
	let message=document.getElementById('message');

	if (pass.value===""){
		message.style.display='none'
	}else{
		message.style.display='inline'
		if (pass.value === confpass.value) {
			message.style.color = 'green';
			message.innerText = 'Passwords match';
		} else {
			message.style.color = 'red';
			message.innerText = "Passwords don't match";
		}
	}
}
