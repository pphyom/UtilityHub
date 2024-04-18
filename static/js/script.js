
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

// Full Screen

// const wrapper = document.getElementById("full-screen");
// const fullscreenButton = document.querySelector(".fsmode");

// fullscreenButton.addEventListener("click", function () {
//     if (document.fullscreenElement) {
//       document.exitFullscreen()
//     } else {
//       if (wrapper.webkitSupportsFullscreen) {
//         wrapper.webkitEnterFullscreen()
//       } else {
//         wrapper.requestFullscreen()
//       }
//     }
//   });

//   fullscreenButton.addEventListener("click", () => {
//     if (document.fullscreenElement) {
//       document
//         .exitFullscreen()
//         .then(() => fullscreenButton.classList.remove("is-active"));
//     } else {
//       if (wrapper.webkitSupportsFullscreen) {
//         wrapper
//           .webkitEnterFullscreen()
//           .then(() => fullscreenButton.classList.add("is-active"));
//       } else {
//         wrapper
//           .requestFullscreen()
//           .then(() => fullscreenButton.classList.add("is-active"));
//       }
//     }
//   });