
// navigation sidebar
const sidebar = document.querySelector("#toggle-btn");

sidebar.addEventListener("click", function() {
    document.querySelector("#sidebar").classList.toggle("expand");
});


// copy data from modal textarea to textbox
function passData() {
    let primaryTextbox = document.querySelector("#primary-textbox")
    let secondaryTextbox = document.querySelector("#secondary-textbox")
    secondaryTextbox = secondaryTextbox.value.split("\n")
    primaryTextbox.value = secondaryTextbox.join(" ");
}


// FULL SCREEN
var isFullscreen = false
var page = document.getElementById("full-screen");

function toggleFS () {
    isFullscreen ? document.exitFullscreen?.() : 
    page.requestFullscreen?.(), 
    (isFullscreen = !isFullscreen)
}
