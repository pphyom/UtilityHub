
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


// Update
async function fetchData() {
    const response = await fetch('/update');
    const data = await response.json();
    const tableBody = document.getElementById('data-table');
    tableBody.innerHTML = '';  // Clear the table

    data.forEach(row => {
        const tableRow = document.createElement('tr');
        row.forEach(cell => {
            const tableCell = document.createElement('td');
            tableCell.textContent = cell;
            tableRow.appendChild(tableCell);
        });
        tableBody.appendChild(tableRow);
    });
}

setInterval(fetchData, 10000);  // Fetch scores every 10 seconds

// Fetch scores immediately on page load
window.onload = fetchData;
