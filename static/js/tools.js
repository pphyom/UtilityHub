
const socket = io();

socket.on('connect', () => {
    console.log('Connected to the server!');
});

socket.on('connected', (data) => {
    console.log('Connected user ID:', data);  // Expecting the message data
});

socket.on('error', (e) => {
    console.log(e.message);
});

// Copy selected text to clipboard
const table = document.querySelector(".ip-lookup-table");
const cells = table.querySelectorAll("td.user-select-all");
cells.forEach(cell => {
    cell.addEventListener("click", () => {
        let selectedText = cell.textContent;
        if (selectedText) {
            navigator.clipboard.writeText(selectedText)
            .then(() => {
                console.log('Text copied to clipboard');
            })
                .catch(err => {
                    console.error('Error copying text: ', err);
            });
        }
    });
}); // End of copy selected text to clipboard


document.querySelector(".ip-lookup-table").addEventListener('click', async function(event) {

    var sysList = {{ sys_list | safe }};  // Convert Python list to JS array
    const target = event.target;
    if (target.classList.contains("getBiosVer") || target.classList.contains("getIpmiVer")) {
        const row = target.closest("tr");
        const col = target.closest("td");
        const spinner = col.querySelector(".spinner");
        const firmwareType = target.classList.contains("getBiosVer") ? row.querySelector(".show-bios-ver") : row.querySelector(".show-ipmi-ver");
        const url = target.classList.contains("getBiosVer") ? "/get_bios_ver" : "/get_ipmi_ver";
        const rowIndex = Array.from(row.parentElement.children).indexOf(row);
        
        spinner.style.display = "block";
        target.style.display = "none";
        firmwareType.textContent = "";
        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                ip_address: sysList[rowIndex].ip_address,
                username: sysList[rowIndex].username,
                password: sysList[rowIndex].password
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            spinner.style.display = "none";
            firmwareType.textContent = data;
        })
    }
});