function onLogIn() {
    document.getElementById("logIn").style.display = "block";
}

function onSignUp() {
    document.getElementById("signUp").style.display = "block";
}

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

function check() {
    let pass=document.getElementById('password');
    let confpass=document.getElementById('confirm_password');
    let message=document.getElementById('message');
    if (pass.value == confpass.value) {
        message.style.color = 'green';
        message.innerHTML = 'matching';
    } else {
        message.style.color = 'red';
        message.innerHTML = 'not matching';
    }
}