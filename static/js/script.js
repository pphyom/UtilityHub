
const sidebar = document.querySelector("#toggle-btn");
let primaryTextbox = document.querySelector("#primary-textbox")
let secondaryTextbox = document.querySelector("#secondary-textbox")


// navigation sidebar
sidebar.addEventListener("click", function() {
    document.querySelector("#sidebar").classList.toggle("expand");
});


// copy data from modal textarea to textbox
function passData() {
    secondaryTextbox = secondaryTextbox.value.split("\n")
    primaryTextbox.value = secondaryTextbox.join(" ");
}
