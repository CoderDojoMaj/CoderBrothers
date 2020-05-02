for(let button of document.querySelectorAll(".replybutton")){
    button.onclick = () => {
        console.log(button)
        console.log(`.replyform.${button.attributes.getNamedItem('uuid').value}`)
        document.querySelector(`.replyform.uuid-${button.attributes.getNamedItem('uuid').value}`).classList.toggle('hidden')
    }
}