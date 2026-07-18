const MAX_FILE_SIZE = 500 * 1024 * 1024;

const browseButton = document.getElementById("browse-btn");
const fileInput = document.getElementById("file-input");
const dropZone = document.getElementById("drop-zone");
const modelStatus = document.getElementById("model-status");
const encoderStatus = document.getElementById("encoder-status")
const progressSection = document.getElementById("upload-progress");

const progressFill = document.getElementById("progress-fill");
const progressLabel = document.getElementById("progress-label");
const progressPercent = document.getElementById("progress-percent");

const progressMessage = document.getElementById("progress-message");
const progressBar = document.querySelector(".progress");

const modelModal = document.getElementById("model-modal");
const trainButton = document.getElementById("train-model-btn");
const trainingProgress = document.getElementById("training-progress");

const ROWS_PER_PAGE = 20;
let predictionRows = [];
let currentPage = 1;
let filteredRows = [];

const RISK_WEIGHTS = {
    "BENIGN": 0,
    "Heartbleed": 100,
    "DDoS": 90,
    "DoS Hulk": 85,
    "DoS GoldenEye": 80,
    "DoS Slowhttptest": 75,
    "DoS slowloris": 75,
    "Bot": 80,
    "FTP-Patator": 70,
    "SSH-Patator": 70,
    "PortScan": 50,
    "Web Attack - Sql Injection": 90,
    "Web Attack - XSS": 70,
    "Web Attack - Brute Force": 75,
    "Infiltration": 95
};

let modelReady = false;
let encoderReady = false;

const predictionFilter = document.getElementById("prediction-filter");
const predictionSearch = document.getElementById("prediction-search");

predictionFilter.addEventListener("change", applyFilters);

predictionSearch.addEventListener("input", applyFilters);


browseButton.addEventListener("click", () => {
    fileInput.click();
});

fileInput.addEventListener("change", () => {
    uploadFile(fileInput.files[0]);
});

dropZone.addEventListener("dragover", event => {
    event.preventDefault();
});

dropZone.addEventListener("drop", event => {
    event.preventDefault();
    uploadFile(event.dataTransfer.files[0]);
});

if (trainButton) {

    trainButton.addEventListener("click", event => {

        event.preventDefault();

        trainModel();

    });

}

async function checkModelStatus() {

    const response = await fetch("/system-status");

    const data = await response.json();


    modelReady = data.model_ready;
    encoderReady = data.encoder_ready;


    updateModelStatus();

    modelModal.hidden = data.model_ready && data.encoder_ready;

}

async function trainModel() {

    trainButton.disabled = true;

    trainButton.textContent = "Training...";

    trainingProgress.hidden = false;


    const response = await fetch(
        "/train",
        {
            method: "POST"
        }
    );

    const data = await response.json();


    await waitForModel();

}

async function waitForModel() {

    while (true) {

        const response = await fetch("/system-status");

        const data = await response.json();
        console.log(data.model_ready, data.encoder_ready);

        if (data.model_ready && data.encoder_ready) {


            console.log("Hiding modal");
            modelModal.hidden = true;
            console.log(modelModal.hidden);

            location.reload();

            return;

        }

        await new Promise(resolve => setTimeout(resolve, 2000));

    }

}

function updateModelStatus() {

    if (modelReady && encoderReady) {

        modelStatus.textContent = "Model Ready";
        encoderStatus.textContent = "Encoder Ready";

        dropZone.hidden = false;
        browseButton.hidden = false;

        trainButton.hidden = true;

    } else {

        modelStatus.textContent = "Model Not Ready OR";
        encoderStatus.textContent = "Encoder Not Ready";

        dropZone.hidden = true;
        browseButton.hidden = true;

        trainButton.hidden = false;

    }

}

window.onload = checkModelStatus


function validateFile(file) {

    if (!file) {
        return false;
    }

    if (!file.name.toLowerCase().endsWith(".csv")) {
        alert("Only CSV files are supported.");
        return false;
    }

    if (file.size > MAX_FILE_SIZE) {
        alert("Maximum file size is 500 MB.");
        return false;
    }

    return true;
}


async function uploadFile(file) {

    if (!validateFile(file)) {
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    progressSection.hidden = true;

    const xhr = new XMLHttpRequest();

    xhr.upload.onprogress = e => {

        if (!e.lengthComputable) {
            return;
        }

        const percent = Math.round((e.loaded / e.total) * 100);

        progressFill.style.width = percent + "%";
        progressPercent.textContent = percent + "%";

        if (percent === 100) {
            progressSection.hidden = false;
            startProcessing();
        }

    };

    xhr.onload = () => {

        if (xhr.status !== 200) {

            progressFill.style.width = "0%";
            progressLabel.textContent = "Prediction Failed";
            progressPercent.textContent = "";

            alert("Prediction failed.");

            return;

        }


        const data = JSON.parse(xhr.responseText);

        stopProcessing();

        progressMessage.textContent = "Rendering dashboard...";

        renderDashboard(data);

        progressSection.hidden = true;


        progressFill.style.width = "100%";
        progressLabel.textContent = "Completed";
        progressPercent.textContent = "100%";

    };

    xhr.onerror = () => {

        progressFill.style.width = "0%";
        progressLabel.textContent = "Upload Failed";
        progressPercent.textContent = "";

        alert("Upload failed.");

    };

    xhr.open("POST", "/predict");
    xhr.send(formData);

}

function calculateRisk(predictions) {

    if (predictions.length === 0) {
        return 0;
    }

    const total = predictions.reduce(
        (sum, row) => {
            return sum + (RISK_WEIGHTS[row.prediction] || 50);
        },
        0
    );

    return Math.round(total / predictions.length);

}

function applyFilters() {

    const filter = predictionFilter.value.toLowerCase();
    const search = predictionSearch.value.trim().toLowerCase();

    filteredRows = predictionRows.filter(row => {

        const prediction = row.prediction.toLowerCase();

        const flow = String(row.flow_id).toLowerCase();

        const matchesFilter = filter === "all" || prediction === filter;

        const matchesSearch =
            prediction.includes(search) ||
            flow.includes(search);

        return matchesFilter && matchesSearch;

    });

    currentPage = 1;

    populatePredictionTable();

    renderPagination();

}

function populatePredictionFilter(rows) {

    const filter = document.getElementById("prediction-filter");

    filter.innerHTML = "<option value=\"all\">All Predictions</option>";

    const predictions = [...new Set(rows.map(row => row.prediction))].sort();

    predictions.forEach(prediction => {

        const option = document.createElement("option");

        option.value = prediction;
        option.textContent = prediction;

        filter.appendChild(option);

    });

}


function renderDashboard(data) {

    document.getElementById("upload-section").hidden = true;
    document.getElementById("dashboard").hidden = false;


    document.getElementById("flow-count").textContent =
        data.summary.flows.toLocaleString();


    document.getElementById("benign-count").textContent =
        data.summary.benign.toLocaleString();


    document.getElementById("malicious-count").textContent =
        data.summary.malicious.toLocaleString();


    document.getElementById("confidence-value").textContent =
        `${(data.summary.average_confidence * 100).toFixed(2)}%`;

    const risk = calculateRisk(data.predictions);

    const riskValue = document.getElementById("risk-value");
    const riskLevel = document.getElementById("risk-level");

    if (riskValue) {
        riskValue.textContent = `${risk}/100`;
    }

    if (riskLevel) {
        riskLevel.textContent =
            risk >= 80 ? "CRITICAL" :
                risk >= 60 ? "HIGH" :
                    risk >= 30 ? "MEDIUM" :
                        "LOW";
    }


    createTrafficChart({
        BENIGN: data.summary.benign,
        MALICIOUS: data.summary.malicious
    });

    createAttackBarChart(data.distribution);

    populateSuspiciousTable(
        data.top_flows
    );


    predictionRows = data.predictions;
    filteredRows = [...predictionRows];
    populatePredictionFilter(predictionRows);
    currentPage = 1;
    populatePredictionTable();
    renderPagination();

}


function createTrafficChart(data) {

    new Chart(
        document.getElementById("attack-chart"),
        {
            type: "doughnut",
            data: {
                labels: Object.keys(data),
                datasets: [
                    {
                        data: Object.values(data)
                    }
                ]
            }
        }
    );

}


function createAttackBarChart(data) {

    new Chart(
        document.getElementById("attack-bar-chart"),
        {
            type: "bar",
            data: {
                labels: Object.keys(data),
                datasets: [
                    {
                        data: Object.values(data)
                    }
                ]
            },
            options: {
                indexAxis: "y",
                scales: {
                    x: {
                        type: "logarithmic",
                        ticks: {
                            callback: function (value) {
                                return Number(value).toLocaleString();
                            }
                        }
                    }
                }
            }
        }
    );

}


function populateSuspiciousTable(rows) {

    const table =
        document.getElementById(
            "suspicious-table"
        );

    table.innerHTML = "";

    rows.forEach(row => {

        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${row.flow_id}</td>
            <td>${row.prediction}</td>
            <td>${(row.confidence * 100).toFixed(2)}%</td>
        `;

        table.appendChild(tr);

    });

}


function populatePredictionTable() {

    const table = document.getElementById("prediction-table");

    table.innerHTML = "";

    const start = (currentPage - 1) * ROWS_PER_PAGE;
    const end = start + ROWS_PER_PAGE;

    filteredRows.slice(start, end).forEach(row => {

        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${row.flow_id}</td>
            <td>${row.prediction}</td>
            <td>${(row.confidence * 100).toFixed(2)}%</td>
        `;

        table.appendChild(tr);

    });

}

function addPageButton(container, page) {

    const button = document.createElement("button");

    button.textContent = page;

    if (page === currentPage) {
        button.classList.add("active-page");
    }

    button.onclick = () => {

        currentPage = page;

        populatePredictionTable();

        renderPagination();

    };

    container.appendChild(button);

}

function addEllipsis(container) {

    const span = document.createElement("span");

    span.textContent = "...";

    span.style.padding = "0 8px";

    container.appendChild(span);

}

function renderPagination() {

    const container = document.getElementById("pagination");

    container.innerHTML = "";

    const pages = Math.ceil(filteredRows.length / ROWS_PER_PAGE);

    if (pages <= 1) {
        return;
    }

    const previous = document.createElement("button");
    previous.textContent = "←";
    previous.disabled = currentPage === 1;
    previous.onclick = () => {
        currentPage--;
        populatePredictionTable();
        renderPagination();
    };

    container.appendChild(previous);

    if (pages <= 7) {

        for (let i = 1; i <= pages; i++) {
            addPageButton(container, i);
        }

    } else if (currentPage <= 4) {

        addPageButton(container, 1);
        addPageButton(container, 2);
        addPageButton(container, 3);
        addPageButton(container, 4);
        addEllipsis(container);
        addPageButton(container, pages - 2);
        addPageButton(container, pages - 1);
        addPageButton(container, pages);

    } else if (currentPage >= pages - 3) {

        addPageButton(container, 1);
        addPageButton(container, 2);
        addPageButton(container, 3);
        addEllipsis(container);
        addPageButton(container, pages - 3);
        addPageButton(container, pages - 2);
        addPageButton(container, pages - 1);
        addPageButton(container, pages);

    } else {

        addPageButton(container, 1);
        addPageButton(container, 2);
        addEllipsis(container);
        addPageButton(container, currentPage - 1);
        addPageButton(container, currentPage);
        addPageButton(container, currentPage + 1);
        addEllipsis(container);
        addPageButton(container, pages - 1);
        addPageButton(container, pages);

    }

    const next = document.createElement("button");
    next.textContent = "→";
    next.disabled = currentPage === pages;
    next.onclick = () => {
        currentPage++;
        populatePredictionTable();
        renderPagination();
    };

    container.appendChild(next);

}

function startProcessing() {
    progressLabel.textContent = "Analyzing Dataset";
    progressPercent.textContent = "";
    progressFill.style.width = "100%";
    progressBar.classList.add("processing");
    progressMessage.classList.add("processing");
    progressMessage.textContent = "Observing network traffic...";
}

function stopProcessing() {
    progressBar.classList.remove("processing");
    progressMessage.classList.remove("processing");
    progressMessage.textContent = "";
}