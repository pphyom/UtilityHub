
const sidebar = document.querySelector("#toggle-btn");

sidebar.addEventListener("click", function(){
    document.querySelector("#sidebar").classList.toggle("expand");
});