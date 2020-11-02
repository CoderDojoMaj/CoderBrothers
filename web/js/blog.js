function onLogIn() {
    document.getElementById("logIn").style.display = "flex";
}

function onSignUp() {
    document.getElementById("signUp").style.display = "flex";
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
    let pass=document.getElementById('p');
    let confpass=document.getElementById('rp');
    let message=document.getElementById('message');

    if (pass.value===""){
        message.style.display='none'
    }else{
        if (pass.value === confpass.value) {
            message.style.color = 'green';
            message.innerText = 'Matching';
        } else {
            message.style.color = 'red';
            message.innerText = 'Not matching';
        }
    }
}