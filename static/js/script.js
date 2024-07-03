
// navigation sidebar
const sidebar = document.querySelector("#toggle-btn");

sidebar.addEventListener("click", function () {
    document.querySelector("#sidebar").classList.toggle("expand");
});


// copy data from modal textarea to textbox -- used in input_form.html
function passData() {
    let primaryTextbox = document.querySelector("#primary-textbox")
    let secondaryTextbox = document.querySelector("#secondary-textbox")
    secondaryTextbox = secondaryTextbox.value.split("\n")
    primaryTextbox.value = secondaryTextbox.join(" ");
}


// Full Screen
const fullscreenWrapper = document.getElementById("fullscreen-wrapper");
const fullscreenButton = document.querySelector(".full-screen");

fullscreenButton.addEventListener("click", () => {
    if (document.fullscreenElement) {
        document
            .exitFullscreen()
            .then(() => fullscreenButton.classList.remove("is-active"));
    } else {
        if (fullscreenWrapper.webkitSupportsFullscreen) {
            fullscreenWrapper
                .webkitEnterFullscreen()
                .then(() => fullscreenButton.classList.add("is-active"));
        } else {
            fullscreenWrapper
                .requestFullscreen()
                .then(() => fullscreenButton.classList.add("is-active"));
        }
    }
});


