function _open() {
    document.getElementById("menu").style.display= "flex";
    setTimeout(() => {document.getElementById("menu").style.width = "70vw";}, 10);
  }
  function _close() {
    document.getElementById("menu").style.width = "0";
    setTimeout(() => {document.getElementById("menu").style.display= "none";}, 500);
  }