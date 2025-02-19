
// Get BIOS and IPMI firmware version
const table = document.querySelector(".ip-lookup-table");

if (table) {
    table.addEventListener('click', async function(event) {
        const target = event.target;
        if (target.classList.contains("getBiosVer") || target.classList.contains("getIpmiVer")) {
            const row = target.closest("tr");
            const col = target.closest("td");
            const spinner = col.querySelector(".spinner");
            const firmwareType = target.classList.contains("getBiosVer") ? row.querySelector(".show-bios-ver") : row.querySelector(".show-ipmi-ver");
            const url = target.classList.contains("getBiosVer") ? "/get_bios_ver" : "/get_ipmi_ver";
            // const rowIndex = Array.from(row.parentElement.children).indexOf(row);

            // Get data or innerText from a specific column of the row
            const specificColumnIndex = {"ip_address": 1, "username": 2, "password": 3}; // Column index of the table
            const ip_address = row.children[specificColumnIndex.ip_address].innerText.trim();
            const username = row.children[specificColumnIndex.username].innerText.trim();
            const password = row.children[specificColumnIndex.password].innerText.trim();

            spinner.style.display = "block";
            target.style.display = "none";
            firmwareType.textContent = "";
            fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    ip_address: ip_address,
                    username: username,
                    password: password
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
            .catch(err => {
                console.error('Error fetching data: ', err);
            });
        }
    });
}
