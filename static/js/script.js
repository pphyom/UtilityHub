
socket.connect();

// navigation sidebar
document.querySelector("#toggle-btn").addEventListener("click", function () {
    document.querySelector("#sidebar").classList.toggle("expand");
});


// copy data from modal textarea to textbox -- used in input_form.html
function passData(textBox, textArea) {
    let primaryTextArea = document.getElementById(textBox);
    let secondaryTextArea = document.getElementById(textArea);
    let finalValue = secondaryTextArea.value.split("\n");
    primaryTextArea.value = finalValue.join(" ");
}


// Alert
let initialServerIP = document.getElementById('rackServer').value;
let initialInterval = document.getElementById('update-interval').value;
const alertPlaceholder = document.getElementById('alertPlaceholder');

function showAlertSuccess () {
    alertPlaceholder.classList.remove("alert-warning", "alert-danger");
    alertPlaceholder.classList.add("alert-success", "alert-dismissible", "fade", "show");
    alertPlaceholder.innerHTML = "Configuration updated!";

    setTimeout(() => {
        alertPlaceholder.classList.remove("show");
    }, 3000);
}

function showAlertWarning () {
    alertPlaceholder.classList.remove("alert-success", "alert-danger");
    alertPlaceholder.classList.add("alert-warning", "alert-dismissible", "fade", "show");
    alertPlaceholder.innerHTML = "Nothing to update!";
    
    setTimeout(() => {
        alertPlaceholder.classList.remove("show");
    }, 3000);
}

function showAlertError () {
    alertPlaceholder.classList.remove("alert-success", "alert-warning");
    alertPlaceholder.classList.add("alert-danger", "alert-dismissible", "fade", "show");
    alertPlaceholder.innerHTML = "Value must be greater than or equal to 30 seconds!";
    
    setTimeout(() => {
        alertPlaceholder.classList.remove("show");
    }, 3000);
}

// Update configuration
function updateData () {

    const currentServerIP = document.getElementById('rackServer').value;
    const currentInterval = document.getElementById('update-interval').value;

    if (currentInterval < 30) {
        showAlertError();
    } else if (currentInterval >= 30 && (currentServerIP !== initialServerIP || currentInterval !== initialInterval)) {
        showAlertSuccess();
        // Update initial values to the new values
        initialServerIP = currentServerIP;
        initialInterval = currentInterval;
    } else {
        showAlertWarning();  // Not Updated
    }

    const newInterval = currentInterval * 1000;  // convert to milliseconds
    const newServerIP = currentServerIP;
    intervalTime = newInterval;
    rackServer = newServerIP;
    startFetching();
}

/**
*************************************************
* Firmware update page functions under tools.html
*************************************************
**/

let tableBody = document.getElementById("dynamicTable");
let chooseFw = document.getElementById("choose-fw")
let btnUploadFw = document.getElementById("btn-upload-fw")
let uploadingFw = document.getElementById("uploading-fw")
let alertElement = document.getElementById("alert-element");
let progressUploadWrapper = document.getElementById("progress-upload-wrapper");
let progressUpload = document.querySelector(".progress-upload");
let firmwareDetails = document.getElementById("firmware-details");

let openControl = document.getElementById("open-control");
let closeControl = document.getElementById("close-control");
let btnDeleteRow = document.getElementById("btn-delete-row");
let btnUpdate = document.getElementById("btn-update");
let btnRetry = document.getElementById("btn-retry");
let uidOnOff = document.getElementById("btn-uid");
let selectAllCheckbox = document.getElementById("select-all-checkbox");

let switchFirmwareUpload = document.getElementById("switch-firmware-upload");
let selectedFirmware = document.getElementById("selected-firmware");
let btnLockFw = document.getElementById("btn-lock-fw");
let selectFw = document.getElementById("select-fw");
let selectedFwType = selectFw.value;

let selectedCommand = document.getElementById("selected-command");

// Event listener for the firmware type dropdown
selectFw.addEventListener("change", () => selectedFwType = selectFw.value);


// Function to toggle between firmware upload and firmware selection
function toggleFirmwareUpload() {
    if (switchFirmwareUpload.checked) {
        chooseFw.parentElement.classList.remove("d-none");
        btnUploadFw.parentElement.classList.remove("d-none");
        selectedFirmware.parentElement.classList.add("d-none");
        btnLockFw.parentElement.classList.add("d-none");
    } else {
        chooseFw.parentElement.classList.add("d-none");
        btnUploadFw.parentElement.classList.add("d-none");
        selectedFirmware.parentElement.classList.remove("d-none");
        btnLockFw.parentElement.classList.remove("d-none");
    }
}


// Event listener for the firmware upload switch
selectedFirmware.addEventListener("change", () => {
    if (selectedFirmware.value) {
        btnLockFw.disabled = false;
    } else {    
        btnLockFw.disabled = true;
    }
});


// Upload firmware file to the server, and return the firmware version and build date. 
btnUploadFw.addEventListener("click", function() {
    if (!chooseFw.files.length) {
        showAlert("Please select a file to upload!", "warning", "bi-exclamation-triangle-fill");
        return;
    }
    dismissAlert();
    let data = new FormData();
    let request = new XMLHttpRequest();
    request.responseType = "json";

    selectFw.disabled = true;
    chooseFw.disabled = true;
    switchFirmwareUpload.disabled = true;
    
    btnUploadFw.classList.add("d-none");
    uploadingFw.classList.remove("d-none");
    progressUploadWrapper.classList.remove("d-none");
    
    let file = chooseFw.files[0];
    let filename = file.name;
    // const filesize = file.size;
    
    // document.cookie = `filesize=${filesize}`;
    document.cookie = `fw-type=${selectedFwType}`;
    data.append("file", file);
    data.append("filename", filename);
    
    request.open("POST", "/upload_firmware");
    
    // Progress Bar -- listen to the upload event
    request.upload.addEventListener("progress", function(event) {
        // calculate the percentage of the uploaded file
        let progress = Math.round((event.loaded / event.total) * 100);
        progressUpload.style.width = `${progress}%`;
        progressUpload.setAttribute("aria-valuenow", progress);
        // progressUpload.innerText = `${progress}%`;
    });
    
    // Listen to the load event
    request.addEventListener("load", () => {
        if (request.status === 200) {
            showAlert(`${request.response.alertMessage}`, "success", "bi-check-circle");
        } else {
            showAlert(`Upload failed! Error ${request.status}. ${request.response.alertMessage}`, "danger", "bi-exclamation-triangle-fill");
        }
        resetUploadUI();
        loadFirmwareList();
    });
    
    request.addEventListener("error", () => {
        showAlert(`Upload failed! Error ${request.status}. ${request.response.alertMessage}`, "danger", "bi-exclamation-triangle-fill");
        resetUploadUI();
    });

    // Get the firmware data back from the server
    request.onload = function() {
        if (request.status === 200) {
            let fwData = request.response;
            firmwareVersion = fwData["firmware_info"].version;
            firmwareBuildDate = fwData["firmware_info"].build_date;
            firmwareImage = fwData["firmware_info"].image;
            firmwareSignedKey = fwData["firmware_info"].signed_key;
            firmwareDetails.innerHTML = "";
            document.getElementById("info-sec").innerText = "UPLOADED FIRMWARE INFO"
            firmwareDetails.innerHTML = `
                <table class="table table-sm align-middle text-start">
                    <tr>
                        <td><i class="bi bi-alphabet fs-3 pe-2"></i></td>
                        <td>${filename}</td>
                    </tr>
                    <tr>
                        <td><i class="bi bi-app-indicator fs-4 pe-2"></i></td>
                        <td>${firmwareVersion}</td>
                    </tr>
                    <tr>
                        <td><i class="bi bi-calendar-check fs-4 pe-2"></i></td>
                        <td>${firmwareBuildDate}</td>
                    </tr>
                    <tr>
                        <td><i class="bi bi-file-image fs-4 pe-2"></i></td>
                        <td>${firmwareImage} (${firmwareSignedKey})</td>
                    </tr>
                </table>
            `;
            showAlert(fwData["response_message"].alertMessage, fwData["response_message"].alertType, "bi-check-circle");
        } else {
            showAlert(`Upload failed! Error ${request.status}. ${request.response.alertMessage}`, "danger", "bi-exclamation-triangle-fill");
            resetUploadUI();
        }
    };

    request.send(data);

});


// Reset the UI either after the file upload is complete or failed
function resetUploadUI() {
    chooseFw.disabled = false;
    selectFw.disabled = false;
    switchFirmwareUpload.disabled = false;
    btnUploadFw.classList.remove("d-none");
    uploadingFw.classList.add("d-none");
    progressUploadWrapper.classList.add("d-none");
}


// Disable inputs when the firmware is locked
function disableEnableInputs(isLocked) {
    if (!isLocked) {
        chooseFw.disabled = true;
        selectFw.disabled = true;
        switchFirmwareUpload.disabled = true;
        selectedFirmware.disabled = true;
    } else {
        chooseFw.disabled = false;
        selectFw.disabled = false;
        switchFirmwareUpload.disabled = false;
        selectedFirmware.disabled = false;
    }
}


// Show alert message
function showAlert(alertMessage, alertType, icon) {
    alertElement.innerHTML = `
        <div class="alert alert-${alertType} alert-dismissible fade show" role="alert">
            <i class="bi ${icon}"></i>
            <span>${alertMessage}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`;
}


// Dismiss alert message
function dismissAlert() {
    alertElement.innerHTML = "";
}


// Get the system serial number from the input box
function userInput(x) {
    // Get the value from the input box, remove leading and trailing spaces, and convert to uppercase
    let input = x.value.toUpperCase().trim();
    // Split the input by spaces or commas to get individual items
    let items = input.split(/\s*,\s*|\s+/);
    // Remove empty strings that may have been created after trimming and splitting
    items = items.filter(item => item !== "");
    // Remove duplicates -- [...] turn the set back into an array
    let uniqueItems = [...new Set(items)];
    return uniqueItems;
}


// Get IPMI information from the server
async function getIpmiInfo(sn) {
    const response = await fetch('/get_ipmi_info', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({system_sn: sn})
    });
    const data = await response.json();
    return data;
}

// Validate the serial number/s via SPM
async function validateSerialNumber(sn_list) {
    const response = await fetch('/validate_serial_number', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({system_sn_list: sn_list})
    });

    if (response.status === 200) {
        const data = await response.json();
        if (data.invalid_serialNums.length > 0) {
            showAlert(`Invalid serial number/s: ${data.invalid_serialNums.join(", ")}`, "warning", "bi-exclamation-triangle-fill");
        }
        return data.valid_serialNums;
    } else {
        showAlert("Error validating serial number/s!", "danger", "bi-exclamation-triangle-fill");
    }
}


// Load the firmware list from the server
function loadFirmwareList() {
    fetch("/list_firmware")
        .then(response => response.json())
        .then(data => {
            data.forEach(firmware => {
                // Check if the option already exists
                if (![...selectedFirmware.options].some(option => option.value === firmware.filepath)) {
                    const option = document.createElement("option");
                    option.value = firmware.filepath; // Use the filename as the value
                    option.textContent = firmware.filename;
                    selectedFirmware.appendChild(option); // Append the option to the select element
                }
            });
        })
        .catch(error => console.error("Error fetching firmware data:", error));
}


// Load the predefined commands from the server
function listCommands(...args) {
    fetch("/list_commands")
        .then(response => response.json())
        .then(data => {
            args.forEach(selectInput => {
                if (selectInput && selectInput.options) {
                    data.forEach(command => {
                        // Check if the option already exists
                        if (!Array.from(selectInput.options).some(option => option.textContent === command.name)) {
                            const option = document.createElement("option");
                            option.value = command.cmd;
                            option.textContent = command.name;
                            selectInput.appendChild(option);
                        }
                    });
                }
            });
        })
        .catch(error => console.error("Error fetching command data:", error));
}

// Refresh the options in the select element
function refreshOptions() {
    listCommands(selectedCommand);
}


window.onload = function() {
    loadFirmwareList();
    listCommands(selectedCommand);
};

/**
 * Asynchronously update the table with the IPMI information.
 * Return NA if the information is not available.
*/
async function updateTable(serialNumberID) {
    // Get the value from the input box
    let serialNumberInput = document.getElementById(serialNumberID);
    let items = userInput(serialNumberInput);
    if (items.length === 0) {
        showAlert("No input detected! Please enter system serial number/s.", "warning", "bi-exclamation-triangle-fill");
        return;
    }

    dismissAlert();
    let validated_items = await validateSerialNumber(items);
    let progressBarWrapper = document.getElementById("custom-progress-bar");
    let progressPB = document.querySelector(".custom-pb");
    let progress = 0;
    let duplicateItems = [];
    
    progressPB.style.width = "0%";
    serialNumberInput.value = "";  // Clear the input box
    progressBarWrapper.classList.remove('d-none');
    btnDeleteRow.classList.remove('disabled');
    btnUpdate.classList.remove('disabled');
    selectAllCheckbox.removeAttribute("disabled");

    for (let idx = 0; idx < validated_items.length; idx++) {
        let systemSn = validated_items[idx];
        // Check if the item is already in the table
        let existingRow = Array.from(tableBody.rows).find(row => row.cells[2].textContent === systemSn);
        if (existingRow) {
            duplicateItems.push(systemSn);
            validated_items.splice(idx, 1); // Remove the existing item from the array
            idx--; // Adjust the index after removal
            continue; // Skip the item if it is already in the table
        }
        let item = await getIpmiInfo(systemSn);
        let ipAddress = item[0].ip_address;
        let motherboard = item[0].mbd;
        // let mo = item[0].mo;
        let passwd = item[0].password;
        progress += 100 / validated_items.length;
        progressPB.style.width = `${progress}%`;
        progressPB.setAttribute("aria-valuenow", progress);

        idx = tableBody.rows.length; // Set the index to the total number of rows
        let newRow = tableBody.insertRow();
        newRow.innerHTML = `
                            <td>${idx + 1}</td>
                            <td>${ipAddress}</td>
                            <td>${systemSn}</td>
                            <td>${passwd}</td>
                            <td>${motherboard}</td>
                            <td>
                                <div class="progress mt-1">
                                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                    role="progressbar" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                            </td>
                            <td>NA</td>
                            <td style="color: ${ipAddress === "NA" ? "red" : "inherit"};">
                                ${ipAddress === "NA" ? "Disconnected" : "Queued"}
                            </td>
                            <td><input class="form-check-input" type="checkbox" value="" id="checkbox-${idx}"></td>
                            <td class="d-none">${passwd}</td>
                        `;

        // Select individual checkboxes
        let checkbox = document.getElementById(`checkbox-${idx}`);
        checkbox.addEventListener('change', function() {
            let row = this.closest('tr');
            if (this.checked) {
                row.classList.add('table-secondary');
            } else {
                row.classList.remove('table-secondary');
            }
        });
    }

    if (duplicateItems.length > 0) {
        showAlert(`${duplicateItems.join(", ")} already existed.`, "warning", "bi-exclamation-triangle-fill");
    }
}


// Select/de-select all checkboxes
document.addEventListener("DOMContentLoaded", function() {
    selectAllCheckbox.addEventListener("click", function() {
        let checkboxes = document.querySelectorAll('input[type="checkbox"]:not(#select-all-checkbox, #switch-firmware-upload)');
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAllCheckbox.checked;
            let row = checkbox.closest('tr');
            if (row) {
                checkbox.checked ? row.classList.add('table-secondary') : row.classList.remove('table-secondary');
            }
        });
    });
});


// Function to update row indices
function updateRowIndices() {
    let rows = Array.from(tableBody.rows);
    rows.forEach((row, index) => {
        row.cells[0].textContent = index + 1;
    });
}

// Delete selected rows from the table
btnDeleteRow.addEventListener("click", function() {
    let anySelected = false;
    let rows = Array.from(tableBody.rows);
    let newIndex = 1;

    if (!anySelected) {
        showAlert("No row selected for deletion!", "warning", "bi-exclamation-triangle-fill");
    }

    rows.forEach(row => {
        if (row.querySelector('input').checked) {
            anySelected = true;
            row.remove();
            dismissAlert();
        } else {
            row.cells[0].textContent = newIndex++;
        }
    });

    updateRowIndices();

    if (tableBody.rows.length === 0) {
        btnDeleteRow.classList.add("disabled");
        btnUpdate.classList.add("disabled");
        selectAllCheckbox.checked = false;
        selectAllCheckbox.setAttribute("disabled", "disabled");
    }
});


// Lock/Unlock the selected firmware for the update
let timeoutId = null;
let firmwareFilename = "";

btnLockFw.addEventListener('mousedown', function () {
    if (btnLockFw.textContent === "Unlock") {
        btnLockFw.classList.add("press-animation");
        timeoutId = setTimeout(function () {
            firmwareFilename = getLockedFirmware();
            btnLockFw.classList.remove("press-animation");
        }, 2000);
    } else {
        firmwareFilename = getLockedFirmware();
    }
});

btnLockFw.addEventListener('mouseup', function () {
    clearTimeout(timeoutId); // reset the timeout when mouse leaves the button before 2 seconds
    btnLockFw.classList.remove("press-animation");
});

btnLockFw.addEventListener('mouseleave', function () {
    clearTimeout(timeoutId); // reset the timeout when mouse leaves the button before 2 seconds
    btnLockFw.classList.remove("press-animation");
});

function getLockedFirmware() {
    let isLocked = false;
    let firmwareNameToUpdate = "";
    if (btnLockFw.textContent === "Unlock") {
        disableEnableInputs(!isLocked); // true
        btnLockFw.textContent = "Lock";
        firmwareNameToUpdate = "";
        showAlert("Locked firmware is clear! Choose or upload a new firmware for the update.", "info", "bi-exclamation-triangle-fill");
    } else {
        disableEnableInputs(isLocked); // false
        btnLockFw.textContent = "Unlock";
        firmwareNameToUpdate = selectedFirmware.options[selectedFirmware.selectedIndex].textContent;
        showAlert(`<b>${firmwareNameToUpdate}</b> is locked! Ready for the update.`, "info", "bi-check-circle");
    }
    return firmwareNameToUpdate;
}


// Update the firmware of the selected systems
// Pass the system serial number, IP address, and password to the server
btnUpdate.addEventListener("click", function () {
    if (firmwareFilename === "") {
        showAlert("Please select and lock a firmware to update!", "warning", "bi-exclamation-triangle-fill");
        return;
    }

    let rows = Array.from(tableBody.rows);

    rows.forEach(async (row) => {
        if (row.querySelector("input").checked) {
            let sn = row.cells[2].textContent; // Get the serial number
            let system = await getIpmiInfo(sn);

            // Unique log row ID
            let logRowId = `log-row-${sn}`;
            let logContentId = `log-content-${sn}`;

            // Check if the log row already exists
            if (!document.getElementById(logRowId)) {
                let logRow = document.createElement("tr");
                logRow.id = logRowId;
                logRow.style.display = "none"; // Initially hidden
                logRow.classList.add("log-row"); /// Not required

                let logCell = document.createElement("td");
                logCell.colSpan = row.cells.length; // Span all columns
                logCell.innerHTML = `<pre id="${logContentId}" class="log-content p-2"></pre>`; /// log-content not required

                logRow.appendChild(logCell);

                // Append log row **AFTER** the current row safely
                if (row.nextSibling) {
                    tableBody.insertBefore(logRow, row.nextSibling);
                } else {
                    tableBody.appendChild(logRow);
                }
            }

            // Toggle log row when clicking the original row
            row.style.cursor = "pointer";
            row.addEventListener("click", function () {
                let logRow = document.getElementById(logRowId);
                logRow.style.display = logRow.style.display === "none" ? "table-row" : "none";
            });

            // Send update request
            fetch("/start_update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ system: system[0], firmware: firmwareFilename }),
            }).then((response) => response.json());
        }
    });
});

// Listen for real-time logs and update the correct row
socket.on("update_log", (data) => {
    let logElement = document.getElementById(`log-content-${data.sn}`); // set the var to logContentId created above (logCell.innerHTML)
    if (logElement) {
        logElement.innerHTML += `${data.log}\n`;
        logElement.style.textAlign = "left"; 
    }
});


socket.on("update_status", (data) => {
    let rows = Array.from(tableBody.rows);
    rows.forEach((row) => {
        let sn = row.cells[2].textContent; // Get serial number from row
        if (sn === data.sn) {  // Match the correct row
            let statusCell = row.cells[7];
            statusCell.textContent = data.status;
            switch (data.status) {
                case "Failed":
                    statusCell.style.color = "red";
                    statusCell.style.fontWeight = "bold";
                    break;
                case "Completed":
                    statusCell.style.color = "green";
                    statusCell.style.fontWeight = "bold";
                    break;
                default:
                    statusCell.style.color = "inherit";
                    statusCell.style.fontWeight = "normal";
                    break;
            }

            // Update progress bar in Cell 5
            let progressBar = row.cells[5].querySelector(".progress-bar");
            if (progressBar) {
                let progressMatch = data.progress.match(/\((\d+)%\)/);
                if (progressMatch) {
                    let progressValue = parseInt(progressMatch[1]);
                    progressBar.style.width = `${progressValue}%`;
                    progressBar.textContent = `${progressValue}%`;
                }
            }
        }
    });
});


// Reset progress bar if the checkbox is unchecked
function resetProgressBar(row) {
    let progressBar = row.querySelector('.progress-bar');
    progressBar.style.width = `0%`;
    progressBar.setAttribute('aria-valuenow', 0);
    progressBar.innerText = `0%`;
}


// Utility Scripts
function executeCommand() {
    // Remove commas from the command value if necessary
    let cmdValue = selectedCommand.value.replace(/,/g, "");
    let anySelected = false;
    let rows = Array.from(tableBody.rows);

    rows.forEach(async (row) => {
        if (row.querySelector("input").checked) {
            anySelected = true;
            dismissAlert();
            let sn = row.cells[2].textContent; // Get the serial number
            let system = await getIpmiInfo(sn);

            fetch("/execute_command", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ system: system, cmdValue: cmdValue }),
            })
            .then((response) => response.json())
            .then(data => {
                console.log(data);
            });

        }

        if (!anySelected) {
            showAlert("No system is selected!", "warning", "bi-exclamation-triangle-fill");
        }
    });
}