export { showAlert };   // Export the showAlert function

// navigation sidebar
const sidebar = document.querySelector("#toggle-btn");

sidebar.addEventListener("click", function () {
    document.querySelector("#sidebar").classList.toggle("expand");
});


// copy data from modal textarea to textbox -- used in input_form.html
function passData() {
    let primaryTextArea = document.getElementById("primary-textbox");
    let secondaryTextArea = document.getElementById("secondary-textbox");
    let secondaryValue = secondaryTextArea.value.split("\n");
    primaryTextArea.value = secondaryValue.join(" ");
    
    let serialNumberInput = document.getElementById("serial-number-input");
    let multiSerialNumberInput = document.getElementById("multi-serial-number-input");
    let multiSerialNumberInputValue = multiSerialNumberInput.value.split("\n");
    serialNumberInput.value = multiSerialNumberInputValue.join(" ");
}


// table search method
const search = document.querySelector(".input-group input");
search.addEventListener("input", searchTable);

function searchTable() {
    const tableRows = document.querySelectorAll("tbody tr");

    tableRows.forEach((row, i) => {
        let tableData = row.textContent.toLowerCase();
        let searchData = search.value.toLowerCase();
        // search by toggling the input data. input > 0 = matching and vice versa.
        row.classList.toggle("hide", tableData.indexOf(searchData) < 0);
        row.style.setProperty("--delay", i/25 + "s");
    });
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

let serialNumberInput = document.getElementById("serial-number-input");
let selectFw = document.getElementById("select-fw")
let chooseFw = document.getElementById("choose-fw")
let uploadFw = document.getElementById("upload-fw")
let uploadingFw = document.getElementById("uploading-fw")
let alertElement = document.getElementById("alert-element");
let progressUploadWrapper = document.getElementById("progress-upload-wrapper");
let progressUpload = document.querySelector(".progress-upload");
let firmwareDetails = document.getElementById("firmware-details");
let selectedFwType = selectFw.value;

let openControl = document.getElementById("open-control");
let closeControl = document.getElementById("close-control");
let btnDeleteRow = document.getElementById("btn-delete-row");
let btnUpdate = document.getElementById("btn-update");
let btnRetry = document.getElementById("btn-retry");
let uidOnOff = document.getElementById("btn-uid");
let selectAllCheckbox = document.getElementById("select-all-checkbox");


// Event listener for the firmware type dropdown
selectFw.addEventListener("change", () => {
    selectedFwType = selectFw.value;
});


/** 
 * Upload firmware file to the server, and return the firmware version and build date. 
 */
uploadFw.addEventListener("click", function() {

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
    
    uploadFw.classList.add("d-none");
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
            showAlert(`File upload failed! Error ${request.status}`, "danger", "bi-exclamation-triangle-fill");
        }
        resetUploadUI();
    });
    
    request.addEventListener("error", () => {
        showAlert(`File upload failed! Error ${request.status}`, "danger", "bi-exclamation-triangle-fill");
        resetUploadUI();
    });

    // Get the firmware data back from the server
    request.onload = function() {
        if (request.status === 200) {
            let fwData = request.response;
            firmwareVersion = fwData["version"];
            firmwareBuildDate = fwData["build_date"];
            // firmwareDetails.innerHTML = "";
            document.getElementById("info-sec").innerText = "UPLOADED FIRMWARE INFO"
            firmwareDetails.innerHTML = `
                <table class="table table-sm table-light align-middle text-start">
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
                </table>
            `;
            showAlert("File Uploaded.", "success", "bi-check-circle");
        } else {
            showAlert(`File upload failed! Error ${request.status}`, "danger", "bi-exclamation-triangle-fill");
            resetUploadUI();
        }
    };

    request.send(data);

});


// Reset the UI either after the file upload is complete or failed
function resetUploadUI() {
    chooseFw.disabled = false;
    selectFw.disabled = false;
    uploadFw.classList.remove("d-none");
    uploadingFw.classList.add("d-none");
    progressUploadWrapper.classList.add("d-none");
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
function userInput() {
    // Get the value from the input box, remove leading and trailing spaces, and convert to uppercase
    let input = serialNumberInput.value.toUpperCase().trim();
    // Split the input by spaces or commas to get individual items
    let items = input.split(/\s*,\s*|\s+/);
    // Remove empty strings that may have been created after trimming and splitting
    items = items.filter(item => item !== "");
    // Remove duplicates -- [...] turn the set back into an array
    let uniqueItems = [...new Set(items)];
    return uniqueItems;
}


/**
 * Get IPMI information from the server.
 * @param {string} sn - System serial number
 * @returns {Promise} - IPMI information
*/ 
async function getIpmiInfo(sn) {
    // let items = userInput();
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


/**
 * Asynchronously update the table with the IPMI information.
 * Return NA if the information is not available.
*/
async function updateTable() {
    // Get the value from the input box
    let items = userInput();
    if (items.length === 0) {
        showAlert("No input detected! Please enter system serial number/s.", "warning", "bi-exclamation-triangle-fill");
        return;
    }
    dismissAlert();
    let tableBody = document.getElementById("dynamicTable");
    let progressBarWrapper = document.getElementById("custom-progress-bar");
    let progressPB = document.querySelector(".custom-pb");
    let progress = 0;
    let duplicateItems = [];
    
    serialNumberInput.value = "";  // Clear the input box
    progressBarWrapper.classList.remove('d-none');
    btnDeleteRow.classList.remove('disabled');
    selectAllCheckbox.removeAttribute("disabled");

    for (let idx = 0; idx < items.length; idx++) {
        let systemSn = items[idx];
        // Check if the item is already in the table
        let existingRow = Array.from(tableBody.rows).find(row => row.cells[2].textContent === systemSn);
        if (existingRow) {
            duplicateItems.push(systemSn);
            items.splice(idx, 1); // Remove the existing item from the array
            idx--; // Adjust the index after removal
            continue; // Skip the item if it is already in the table
        }
        let item = await getIpmiInfo(systemSn);
        let ipAddress = item[0].ip_address;
        let motherboard = item[0].mbd;
        progress += 100 / items.length;
        progressPB.style.width = `${progress}%`;
        progressPB.setAttribute("aria-valuenow", progress);

        idx = tableBody.rows.length; // Set the index to the total number of rows
        let newRow = tableBody.insertRow();
        newRow.innerHTML = `
            <td>${idx + 1}</td>
            <td>${ipAddress}</td>
            <td>${systemSn}</td>
            <td>${motherboard}</td>
            <td>
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                    role="progressbar" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
            </td>
            <td>NA</td>
            <td>In Queue</td>
            <td><input class="form-check-input" type="checkbox" value="" id="checkbox-${idx}"></td>
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
        let checkboxes = document.querySelectorAll('input[type="checkbox"]:not(#select-all-checkbox)');
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAllCheckbox.checked;
            let row = checkbox.closest('tr');
            checkbox.checked ? row.classList.add('table-secondary') : row.classList.remove('table-secondary');
        });
    });
});


// Delete selected rows from the table
// btnDeleteRow.addEventListener("click", function() {
//     let tableBody = document.getElementById("dynamicTable");
//     let rows = Array.from(tableBody.rows);
//     rows.forEach(row => {
//         if (row.querySelector('input').checked) {
//             row.remove();
//         }
//     });
//     // Rearrange the index after deletion
//     rows = Array.from(tableBody.rows);
//     rows.forEach((row, index) => {
//         row.cells[0].textContent = index + 1;
//     });

//     if (tableBody.rows.length === 0) {
//         btnDeleteRow.disabled = true;
//         selectAllCheckbox.checked = false;
//         selectAllCheckbox.setAttribute("disabled", "true");
//     }
// });


// Dummy function to simulate firmware update
async function runFirmwareUpdate(row) {
    let progressBar = row.querySelector('.progress-bar');
    let progress = 0;
    
    // Simulate progress update with setInterval
    let interval = setInterval(() => {
        if (progress < 100) {
            progress += 5;
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
            progressBar.innerText = `${progress}%`;
        } else {
            clearInterval(interval);
        }
    }, 500);  // Update progress every 0.5 seconds
}

// Reset progress bar if the checkbox is unchecked
function resetProgressBar(row) {
    let progressBar = row.querySelector('.progress-bar');
    progressBar.style.width = `0%`;
    progressBar.setAttribute('aria-valuenow', 0);
    progressBar.innerText = `0%`;
}

openControl.addEventListener("click", function() {
    openControl.classList.add("d-none");
    closeControl.classList.remove("d-none");
});


closeControl.addEventListener("click", function() {
    closeControl.classList.add("d-none");
    openControl.classList.remove("d-none");
});