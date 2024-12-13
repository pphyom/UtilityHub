
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

let selectFw = document.getElementById("select-fw")
let chooseFw = document.getElementById("choose-fw")
let uploadFw = document.getElementById("upload-fw")
let uploadingFw = document.getElementById("uploading-fw")
let alertElement = document.getElementById("alert-element");
let progressUploadWrapper = document.getElementById("progress-upload-wrapper");
let progressUpload = document.querySelector(".progress-upload");
let firmwareDetails = document.getElementById("firmware-details");
let selectedFwType = selectFw.value;

selectFw.addEventListener("change", () => {
    selectedFwType = selectFw.value;
});

uploadFw.addEventListener("click", function() {
    if (!chooseFw.files.length) {
        showAlert("Please select a file to upload!", "warning", "bi-exclamation-triangle-fill");
        return;
    }
    dismissAlert();
    let data = new FormData();
    let request = new XMLHttpRequest();
    request.responseType = "json";
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

    request.upload.addEventListener("progress", function(event) {
        // calculate the percentage of the uploaded file
        let progress = Math.round((event.loaded / event.total) * 100);
        progressUpload.style.width = `${progress}%`;
        progressUpload.setAttribute("aria-valuenow", progress);
        progressUpload.innerText = `${progress}%`;
    });

    request.addEventListener("load", () => {
        if (request.status === 200) {
            showAlert(`${request.response.alertMessage}`, "success", "bi-check-circle");
        } else {
            showAlert("File upload failed!", "danger", "bi-exclamation-triangle-fill");
        }
        resetUploadUI();
    });

    request.addEventListener("error", () => {
        showAlert("File upload failed!", "danger", "bi-exclamation-triangle-fill");
        resetUploadUI();
    });

    // Get the firmware data back from the server
    request.onload = function() {
        if (request.status === 200) {
            let fwData = request.response;
            firmware_info = fwData["firmware_info"];
            firmwareDetails.innerHTML = `${firmware_info}`;
        } else {
            console.log("Error: " + request.status);
        }
    };

    request.send(data);
});


function resetUploadUI() {
    chooseFw.disabled = false;
    uploadFw.classList.remove("d-none");
    uploadingFw.classList.add("d-none");
    progressUploadWrapper.classList.add("d-none");
}


function showAlert(alertMessage, alertType, icon) {
    alertElement.innerHTML = `
        <div class="alert alert-${alertType} alert-dismissible fade show" role="alert">
            <i class="bi ${icon}"></i>
            <span>${alertMessage}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>`;
}


function dismissAlert() {
    alertElement.innerHTML = "";
}


function userInput() {
    // Get the value from the input box, remove leading and trailing spaces, and convert to uppercase
    let input = document.getElementById("inputSerialNum").value.toUpperCase().trim();
    // Split the input by spaces or commas to get individual items
    let items = input.split(/\s*,\s*|\s+/);
    // Remove empty strings that may have been created after trimming and splitting
    items = items.filter(item => item !== "");
    // Remove duplicates -- [...] turn the set back into an array
    let uniqueItems = [...new Set(items)];
    return uniqueItems;
}


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
    // Clear current table rows
    tableBody.innerHTML = "";
    progressBarWrapper.classList.remove('d-none');

    for (let ind = 0; ind < items.length; ind++) {
        let item = await getIpmiInfo(items[ind]);
        let ipAddress = item[0].ip_address;
        let systemSn = items[ind];
        progress += 100 / items.length;
        progressPB.style.width = `${progress}%`;
        progressPB.setAttribute("aria-valuenow", progress);


        let newRow = tableBody.insertRow();
        newRow.innerHTML = `
            <td>${ind + 1}</td>
            <td>${ipAddress}</td>
            <td>${systemSn}</td>
            <td>
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated bg-warning text-dark" 
                    role="progressbar" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
            </td>
            <td>NA</td>
            <td>NA</td>
            <td><input class="form-check-input" type="checkbox" value="" id="checkbox-${ind}"></td>
        `;

        let checkbox = document.getElementById(`checkbox-${ind}`);
        checkbox.addEventListener('change', function() {
            let row = this.closest('tr');
            if (this.checked) {
                row.classList.add('table-secondary');
                runFirmwareUpdate(row);
            } else {
                row.classList.remove('table-secondary');
                resetProgressBar(row);
            }
        });
    }
}


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
