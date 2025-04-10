// STDF Analysis Report JavaScript

document.addEventListener("DOMContentLoaded", function () {
  // Example data - in a real app this would come from your backend
  const reportData = {
    lotId: "LOT12345",
    waferId: "WAFER007",
    testDate: "2023-05-15",
    waferDiameter: 300, // mm
    dieSize: { width: 10, height: 10 }, // mm
    metrics: {
      yield: 87.5,
      totalDies: 200,
      passDies: 175,
      failDies: 25,
    },
    softbinDistribution: [
      { bin: 1, count: 175, label: "Pass" },
      { bin: 2, count: 12, label: "Fail - Open" },
      { bin: 3, count: 8, label: "Fail - Short" },
      { bin: 4, count: 3, label: "Fail - Leakage" },
      { bin: 5, count: 2, label: "Fail - Other" },
    ],
    testParameters: [
      {
        id: 1,
        name: "VCC Current",
        min: 0.8,
        max: 1.2,
        mean: 1.0,
        stdDev: 0.1,
        failures: 5,
      },
      {
        id: 2,
        name: "Clock Speed",
        min: 950,
        max: 1050,
        mean: 1000,
        stdDev: 20,
        failures: 3,
      },
      {
        id: 3,
        name: "Output Voltage",
        min: 4.8,
        max: 5.2,
        mean: 5.0,
        stdDev: 0.1,
        failures: 7,
      },
      {
        id: 4,
        name: "Leakage Current",
        min: 0.001,
        max: 0.009,
        mean: 0.005,
        stdDev: 0.002,
        failures: 10,
      },
      {
        id: 5,
        name: "Rise Time",
        min: 4.5,
        max: 5.5,
        mean: 5.0,
        stdDev: 0.2,
        failures: 2,
      },
    ],
    dieData: [], // Will be generated
  };

  // Populate the metadata
  document.getElementById("lot-id").textContent = reportData.lotId;
  document.getElementById("wafer-id").textContent = reportData.waferId;
  document.getElementById("test-date").textContent = reportData.testDate;

  // Populate metrics
  document.getElementById("yield-value").textContent =
    reportData.metrics.yield.toFixed(1) + "%";
  document.getElementById("total-dies-value").textContent =
    reportData.metrics.totalDies;
  document.getElementById("pass-dies-value").textContent =
    reportData.metrics.passDies;
  document.getElementById("fail-dies-value").textContent =
    reportData.metrics.failDies;

  // Generate sample die data
  generateSampleDieData(reportData);

  // Initialize wafer map
  initWaferMap(reportData);

  // Initialize softbin chart
  initSoftbinChart(reportData);

  // Populate test parameters table
  populateTestTable(reportData);

  // Setup tab switching
  setupTabs();

  // Setup filter buttons
  setupFilters();

  // Set generation date
  document.getElementById("generation-date").textContent =
    new Date().toLocaleString();

  // Initialize modal
  initModal();

  // Tab navigation
  initTabNavigation();

  // Wafer Map Drawing
  drawWaferMap();

  // Bin chart drawing
  drawBinChart();

  // Die click handler for wafer map
  document
    .getElementById("wafer-map")
    .addEventListener("click", function (event) {
      if (event.target.classList.contains("die")) {
        openDieInfoModal(event.target.dataset.x, event.target.dataset.y);
      }
    });

  // Modal close buttons
  document.querySelectorAll(".close-button").forEach((button) => {
    button.addEventListener("click", function () {
      const modal = this.closest(".modal");
      if (modal) {
        closeModal(modal);
      }
    });
  });

  // Close modals when clicking outside of content
  window.addEventListener("click", function (event) {
    document.querySelectorAll(".modal").forEach((modal) => {
      if (event.target === modal) {
        closeModal(modal);
      }
    });
  });

  // Filter buttons for wafer map
  initFilterButtons();

  // Setup wafer navigation
  initWaferNavigation();

  // Setup map display type selector
  initMapDisplayTypeSelector();

  // Initialize report actions
  initReportActions();

  // Setup wafer selection functionality
  initWaferSelection();

  // Initialize modal action buttons
  initModalActions();

  // Additional navigation handlers for home page
  const homeLinks = document.querySelectorAll('a[href="index.html"]');
  homeLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      // You can add any transition effects or state saving here if needed
      console.log("Navigating to home page");
    });
  });
});

function generateSampleDieData(reportData) {
  // This is a simplified way to generate die data in a circular pattern
  // In a real application, this data would come from the STDF file

  const radius = reportData.waferDiameter / 2;
  const rows = Math.floor(reportData.waferDiameter / reportData.dieSize.height);
  const cols = Math.floor(reportData.waferDiameter / reportData.dieSize.width);

  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      // Calculate x and y positions
      const x = (col - cols / 2) * reportData.dieSize.width;
      const y = (row - rows / 2) * reportData.dieSize.height;

      // Calculate distance from center
      const distance = Math.sqrt(x * x + y * y);

      // Only include dies that fall within the wafer circle
      if (distance <= radius) {
        // Generate status with higher probability of pass
        const status = Math.random() < 0.875 ? "pass" : "fail";

        // Generate a softbin
        let softbin = 1;
        if (status === "fail") {
          // Randomly assign to failure bins
          softbin = Math.floor(Math.random() * 4) + 2;
        }

        // Generate test results
        const testResults = [];
        reportData.testParameters.forEach((param) => {
          const result = {
            id: param.id,
            name: param.name,
            value: param.mean + (Math.random() - 0.5) * param.stdDev * 4,
            status: "pass",
          };

          // If this is a failing die, make one or more tests fail
          if (status === "fail" && Math.random() < 0.7) {
            result.status = "fail";
            // Make the value out of range
            if (Math.random() < 0.5) {
              result.value = param.max + Math.random() * param.stdDev * 3;
            } else {
              result.value = param.min - Math.random() * param.stdDev * 3;
            }
          }

          testResults.push(result);
        });

        reportData.dieData.push({
          row,
          col,
          x,
          y,
          status,
          softbin,
          hardbin: softbin,
          testResults,
        });
      }
    }
  }
}

function initWaferMap(data) {
  const waferContainer = document.getElementById("wafer-map");
  const svg = document.getElementById("wafer-svg");

  // Clear previous content
  svg.innerHTML = "";

  // Add wafer outline
  const waferOutline = document.createElementNS(
    "http://www.w3.org/2000/svg",
    "circle"
  );
  waferOutline.setAttribute("cx", "50%");
  waferOutline.setAttribute("cy", "50%");
  waferOutline.setAttribute("r", "49%");
  waferOutline.setAttribute("class", "wafer-outline");
  svg.appendChild(waferOutline);

  // Find min/max coordinates to scale properly
  let minX = Infinity,
    maxX = -Infinity,
    minY = Infinity,
    maxY = -Infinity;
  data.dieData.forEach((die) => {
    minX = Math.min(minX, die.x);
    maxX = Math.max(maxX, die.x);
    minY = Math.min(minY, die.y);
    maxY = Math.max(maxY, die.y);
  });

  const width = maxX - minX + data.dieSize.width;
  const height = maxY - minY + data.dieSize.height;
  const scale = Math.min(100 / width, 100 / height);

  // Add dies
  data.dieData.forEach((die) => {
    const dieElement = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "rect"
    );

    // Scale and center the coordinates
    const scaledX = (die.x - minX) * scale + (100 - width * scale) / 2;
    const scaledY = (die.y - minY) * scale + (100 - height * scale) / 2;
    const scaledWidth = data.dieSize.width * scale * 0.9; // Slightly smaller for spacing
    const scaledHeight = data.dieSize.height * scale * 0.9;

    dieElement.setAttribute("x", `${scaledX}%`);
    dieElement.setAttribute("y", `${scaledY}%`);
    dieElement.setAttribute("width", `${scaledWidth}%`);
    dieElement.setAttribute("height", `${scaledHeight}%`);
    dieElement.setAttribute("class", `die ${die.status}`);
    dieElement.setAttribute("data-row", die.row);
    dieElement.setAttribute("data-col", die.col);

    // Add click event to show die details
    dieElement.addEventListener("click", () => {
      showDieDetails(die);
    });

    svg.appendChild(dieElement);
  });

  // Hide loading spinner
  document.getElementById("wafer-loading").style.display = "none";
}

function initSoftbinChart(data) {
  const chartContainer = document.getElementById("softbin-chart");
  chartContainer.innerHTML = "";

  // Find the maximum bin count for scaling
  const maxCount = Math.max(
    ...data.softbinDistribution.map((bin) => bin.count)
  );

  // Create bars
  data.softbinDistribution.forEach((bin) => {
    const barHeight = ((bin.count / maxCount) * 100).toFixed(1);

    const bar = document.createElement("div");
    bar.className = "chart-bar";
    bar.style.height = `${barHeight}%`;

    const tooltip = document.createElement("div");
    tooltip.className = "bar-tooltip";
    tooltip.textContent = `Bin ${bin.bin}: ${bin.count} dies (${(
      (bin.count / data.metrics.totalDies) *
      100
    ).toFixed(1)}%)`;

    bar.appendChild(tooltip);
    chartContainer.appendChild(bar);
  });
}

function populateTestTable(data) {
  const tableBody = document.getElementById("test-table-body");
  tableBody.innerHTML = "";

  data.testParameters.forEach((param) => {
    const row = document.createElement("tr");

    row.innerHTML = `
            <td>${param.id}</td>
            <td>${param.name}</td>
            <td>${param.min.toFixed(3)}</td>
            <td>${param.max.toFixed(3)}</td>
            <td>${param.mean.toFixed(3)}</td>
            <td>${param.stdDev.toFixed(3)}</td>
            <td>${param.failures}</td>
        `;

    tableBody.appendChild(row);
  });
}

function setupTabs() {
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Remove active class from all buttons
      tabButtons.forEach((btn) => btn.classList.remove("active"));

      // Add active class to clicked button
      button.classList.add("active");

      // Hide all tab contents
      tabContents.forEach((content) => {
        content.style.display = "none";
      });

      // Show the selected tab content
      const tabId = button.getAttribute("data-tab");
      document.getElementById(tabId).style.display = "block";
    });
  });

  // Show the first tab by default
  tabButtons[0].click();
}

function setupFilters() {
  const filterButtons = document.querySelectorAll(".filter-button");

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Toggle active class
      filterButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");

      const filter = button.getAttribute("data-filter");

      // Apply filter to wafer map
      const dies = document.querySelectorAll(".die");
      dies.forEach((die) => {
        if (filter === "all") {
          die.style.opacity = "1";
        } else if (die.classList.contains(filter)) {
          die.style.opacity = "1";
        } else {
          die.style.opacity = "0.2";
        }
      });
    });
  });
}

function showDieDetails(die) {
  const modal = document.getElementById("die-detail-modal");
  const modalTitle = document.getElementById("modal-title");
  const dieCoords = document.getElementById("die-coords");
  const dieSoftbin = document.getElementById("die-softbin");
  const dieHardbin = document.getElementById("die-hardbin");
  const dieStatus = document.getElementById("die-status");
  const dieTestsBody = document.getElementById("die-tests-body");

  // Update modal content
  modalTitle.textContent = `Die (${die.row}, ${die.col}) Details`;
  dieCoords.textContent = `(${die.row}, ${die.col})`;
  dieSoftbin.textContent = die.softbin;
  dieHardbin.textContent = die.hardbin;

  dieStatus.textContent =
    die.status.charAt(0).toUpperCase() + die.status.slice(1);
  dieStatus.className = `die-status ${die.status}`;

  // Populate test results
  dieTestsBody.innerHTML = "";
  die.testResults.forEach((test) => {
    const row = document.createElement("tr");
    row.className = `test-${test.status}`;

    row.innerHTML = `
            <td>${test.id}</td>
            <td>${test.name}</td>
            <td>${test.value.toFixed(3)}</td>
            <td>${
              test.status.charAt(0).toUpperCase() + test.status.slice(1)
            }</td>
        `;

    dieTestsBody.appendChild(row);
  });

  // Show modal
  modal.style.display = "flex";
}

// Close modal when clicking the close button
document.getElementById("close-modal").addEventListener("click", () => {
  document.getElementById("die-detail-modal").style.display = "none";
});

// Close modal when clicking outside the content
document.getElementById("die-detail-modal").addEventListener("click", (e) => {
  if (e.target === document.getElementById("die-detail-modal")) {
    document.getElementById("die-detail-modal").style.display = "none";
  }
});

// Modal Functionality
function initModal() {
  const modal = document.getElementById("die-modal");
  const closeButton = document.querySelector(".close-button");

  closeButton.addEventListener("click", function () {
    modal.style.display = "none";
  });

  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
}

// Initialize DOM elements when content is loaded
document.addEventListener("DOMContentLoaded", function () {
  // Set current date in the header
  document.getElementById("report-date").textContent =
    new Date().toLocaleDateString();

  // Tab switching functionality
  setupTabs();

  // Render wafer map
  renderWaferMap();

  // Setup filter buttons
  setupFilters();

  // Setup modal functionality
  setupModal();

  // Display first tab by default
  document.querySelector(".tab-button").click();
});

// Tab switching functionality
function setupTabs() {
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Remove active class from all buttons
      tabButtons.forEach((btn) => {
        btn.classList.remove("active");
      });

      // Hide all tab contents
      tabContents.forEach((content) => {
        content.style.display = "none";
      });

      // Activate the clicked tab
      button.classList.add("active");
      const targetTab = document.getElementById(
        button.getAttribute("data-tab")
      );
      targetTab.style.display = "block";
    });
  });
}

// Wafer map rendering
function renderWaferMap() {
  const waferMapContainer = document.querySelector(".wafer-map-svg");
  if (!waferMapContainer) return;

  // Example data - in a real application, this would come from the STDF file
  const waferSize = 11; // 11x11 grid for simplicity
  const dieSize = 100 / (waferSize + 1); // Leave space for borders

  // Generate SVG content
  let svgContent = "";

  for (let y = 0; y < waferSize; y++) {
    for (let x = 0; x < waferSize; x++) {
      // Determine if the die is within the circular wafer area
      const centerX = waferSize / 2;
      const centerY = waferSize / 2;
      const distance = Math.sqrt(
        Math.pow(x - centerX, 2) + Math.pow(y - centerY, 2)
      );

      // Skip dies outside the circular wafer area
      if (distance > waferSize / 2 - 0.5) continue;

      // Randomly assign pass/fail status (for demo purposes)
      const isPassing = Math.random() > 0.3;
      const fillColor = isPassing ? "#34c759" : "#ff3b30";
      const dieClass = isPassing ? "wafer-die passing" : "wafer-die failing";
      const binNumber = isPassing ? 1 : Math.floor(Math.random() * 5) + 2; // Bins 2-6 for failures

      // Create a rectangle for each die
      svgContent += `
                <rect 
                    x="${x * dieSize + dieSize / 2}" 
                    y="${y * dieSize + dieSize / 2}" 
                    width="${dieSize - 1}" 
                    height="${dieSize - 1}" 
                    fill="${fillColor}" 
                    class="${dieClass}"
                    data-x="${x}"
                    data-y="${y}"
                    data-status="${isPassing ? "pass" : "fail"}"
                    data-softbin="${binNumber}"
                    data-hardbin="${isPassing ? 1 : 2}"
                    onclick="showDieInfo(${x}, ${y}, ${isPassing}, ${binNumber})"
                />
            `;
    }
  }

  waferMapContainer.innerHTML = svgContent;

  // Update summary metrics
  updateWaferSummary();
}

// Update wafer summary metrics
function updateWaferSummary() {
  const totalDies = document.querySelectorAll(".wafer-die").length;
  const passingDies = document.querySelectorAll(".wafer-die.passing").length;
  const failingDies = totalDies - passingDies;
  const yield = ((passingDies / totalDies) * 100).toFixed(2);

  // Update metrics in the DOM
  document.getElementById("total-dies").textContent = totalDies;
  document.getElementById("pass-dies").textContent = passingDies;
  document.getElementById("fail-dies").textContent = failingDies;
  document.getElementById("yield-percentage").textContent = yield + "%";
}

// Setup filter buttons
function setupFilters() {
  const filterButtons = document.querySelectorAll(".filter-button");

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Toggle active state
      filterButtons.forEach((btn) => {
        btn.classList.remove("active");
      });
      button.classList.add("active");

      // Apply filter
      const filterType = button.getAttribute("data-filter");
      filterWaferMap(filterType);
    });
  });
}

// Filter wafer map based on selected criteria
function filterWaferMap(filterType) {
  const allDies = document.querySelectorAll(".wafer-die");

  allDies.forEach((die) => {
    die.classList.remove("filtered");

    if (filterType === "all") {
      // Show all dies
      return;
    } else if (filterType === "pass" && !die.classList.contains("passing")) {
      die.classList.add("filtered");
    } else if (filterType === "fail" && die.classList.contains("passing")) {
      die.classList.add("filtered");
    }
  });
}

// Setup modal functionality
function setupModal() {
  const modal = document.getElementById("die-modal");
  const closeButton = document.querySelector(".close-button");

  closeButton.addEventListener("click", () => {
    modal.style.display = "none";
  });

  // Close modal when clicking outside the content
  window.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
}

// Show die information in the modal
function showDieInfo(x, y, isPassing, binNumber) {
  const modal = document.getElementById("die-modal");
  const statusElement = document.getElementById("die-status");

  // Update die coordinates
  document.getElementById("die-x").textContent = x;
  document.getElementById("die-y").textContent = y;

  // Update die status
  statusElement.textContent = isPassing ? "PASS" : "FAIL";
  statusElement.className =
    "info-value die-status " + (isPassing ? "pass" : "fail");

  // Update bin information
  document.getElementById("die-softbin").textContent = binNumber;
  document.getElementById("die-hardbin").textContent = isPassing ? 1 : 2;

  // Generate random test results for demo purposes
  generateTestResults(isPassing);

  // Show the modal
  modal.style.display = "block";
}

// Generate random test results for the modal
function generateTestResults(isPassing) {
  const testResultsTable = document.getElementById("test-results-table");
  const testCount = 8; // Number of test items to show

  // Clear existing results
  testResultsTable.innerHTML = `
        <tr>
            <th>Test Number</th>
            <th>Test Name</th>
            <th>Value</th>
            <th>Unit</th>
            <th>Low Limit</th>
            <th>High Limit</th>
            <th>Status</th>
        </tr>
    `;

  // Test data (for demo purposes)
  const testNames = [
    "Input Leakage",
    "Output Drive",
    "VDD Current",
    "Clock Frequency",
    "Setup Time",
    "Hold Time",
    "Propagation Delay",
    "Rise Time",
    "Fall Time",
    "Input Voltage",
    "Output Voltage",
  ];

  const units = ["nA", "mA", "µA", "MHz", "ns", "ps", "V", "mV"];

  // Generate random test results
  for (let i = 1; i <= testCount; i++) {
    const testName = testNames[Math.floor(Math.random() * testNames.length)];
    const unit = units[Math.floor(Math.random() * units.length)];

    // For failing die, ensure at least one test failure
    const testPassing = isPassing
      ? true
      : i !== Math.floor(Math.random() * testCount) + 1;

    const lowLimit = (Math.random() * 10).toFixed(2);
    const highLimit = (parseFloat(lowLimit) + Math.random() * 20).toFixed(2);

    // Value will be within limits if passing, outside if failing
    let value;
    if (testPassing) {
      value = (
        parseFloat(lowLimit) +
        Math.random() * (parseFloat(highLimit) - parseFloat(lowLimit))
      ).toFixed(3);
    } else {
      // 50% chance of being below low limit or above high limit
      if (Math.random() > 0.5) {
        value = (parseFloat(lowLimit) - Math.random() * 5).toFixed(3);
      } else {
        value = (parseFloat(highLimit) + Math.random() * 5).toFixed(3);
      }
    }

    // Add row to table
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>${i}</td>
            <td>${testName}</td>
            <td>${value}</td>
            <td>${unit}</td>
            <td>${lowLimit}</td>
            <td>${highLimit}</td>
            <td class="${testPassing ? "pass" : "fail"}">${
      testPassing ? "PASS" : "FAIL"
    }</td>
        `;

    testResultsTable.appendChild(row);
  }
}

// Helper function to generate random data for charts
function generateChartData(elementId, barCount = 5) {
  const chartContainer = document.getElementById(elementId);
  if (!chartContainer) return;

  let chartHTML = "";

  for (let i = 1; i <= barCount; i++) {
    const height = Math.floor(Math.random() * 70) + 10; // Random height between 10-80%
    const value = Math.floor(Math.random() * 100);

    chartHTML += `
            <div class="chart-bar" style="height: ${height}%">
                <div class="chart-bar-value">${value}</div>
                <div class="chart-bar-label">Bin ${i}</div>
            </div>
        `;
  }

  chartContainer.innerHTML = chartHTML;
}

// Generate bin chart when the tab is shown
function showBinAnalysis() {
  generateChartData("bin-chart", 8);
}

// Initialize tab navigation
function initTabNavigation() {
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Get the target tab from the data attribute
      const targetTab = button.dataset.tab;

      // Deactivate all tabs
      tabButtons.forEach((btn) => btn.classList.remove("active"));
      tabContents.forEach((content) => (content.style.display = "none"));

      // Activate the selected tab
      button.classList.add("active");
      document.getElementById(targetTab).style.display = "block";
    });
  });

  // Initialize the first tab as active
  if (tabButtons.length > 0) {
    tabButtons[0].click();
  }
}

// Draw the wafer map with sample data
function drawWaferMap() {
  const waferMap = document.getElementById("wafer-map");
  if (!waferMap) return;

  const ctx = waferMap.getContext("2d");
  const size = Math.min(waferMap.width, waferMap.height);

  // Clear canvas
  ctx.clearRect(0, 0, waferMap.width, waferMap.height);

  // Generate sample wafer data (in a real app, this would come from STDF data)
  const waferData = generateSampleWaferData();

  // Draw wafer outline
  const centerX = size / 2;
  const centerY = size / 2;
  const radius = size / 2 - 10;

  ctx.beginPath();
  ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
  ctx.fillStyle = "#f8f8f8";
  ctx.fill();
  ctx.strokeStyle = "#d2d2d7";
  ctx.lineWidth = 1;
  ctx.stroke();

  // Draw flat
  const flatHeight = radius * 0.05;
  ctx.beginPath();
  ctx.moveTo(centerX - radius, centerY);
  ctx.lineTo(centerX - radius, centerY - flatHeight);
  ctx.lineTo(centerX - radius, centerY + flatHeight);
  ctx.closePath();
  ctx.fillStyle = "#f8f8f8";
  ctx.fill();
  ctx.stroke();

  // Draw dies
  const dieSize = size / 26; // Adjust based on wafer dimensions
  const dieGap = 1;

  // Calculate the start position to center the grid
  const gridSize = waferData.length;
  const gridWidth = gridSize * (dieSize + dieGap) - dieGap;
  const startX = (size - gridWidth) / 2;
  const startY = (size - gridWidth) / 2;

  for (let row = 0; row < gridSize; row++) {
    for (let col = 0; col < gridSize; col++) {
      const die = waferData[row][col];
      if (die) {
        const x = startX + col * (dieSize + dieGap);
        const y = startY + row * (dieSize + dieGap);

        // Check if die is within wafer circle
        const distFromCenter = Math.sqrt(
          Math.pow(x + dieSize / 2 - centerX, 2) +
            Math.pow(y + dieSize / 2 - centerY, 2)
        );

        if (distFromCenter + dieSize / 2 < radius) {
          ctx.fillStyle = die.status === "pass" ? "#34c759" : "#ff3b30";
          ctx.fillRect(x, y, dieSize, dieSize);

          // Store die data for click events using HTML overlay elements
          const dieElement = document.createElement("div");
          dieElement.className = "die";
          dieElement.dataset.x = col;
          dieElement.dataset.y = row;
          dieElement.dataset.status = die.status;
          dieElement.style.position = "absolute";
          dieElement.style.left = x + "px";
          dieElement.style.top = y + "px";
          dieElement.style.width = dieSize + "px";
          dieElement.style.height = dieSize + "px";
          dieElement.style.cursor = "pointer";

          const waferContainer = document.querySelector(".wafer-container");
          waferContainer.appendChild(dieElement);
        }
      }
    }
  }
}

// Generate sample wafer data
function generateSampleWaferData() {
  const gridSize = 21; // 21x21 grid
  const waferData = new Array(gridSize)
    .fill(null)
    .map(() => new Array(gridSize).fill(null));

  // Fill with random data
  const yieldRate = 0.88; // 88% yield

  for (let row = 0; row < gridSize; row++) {
    for (let col = 0; col < gridSize; col++) {
      // Create a circular wafer shape
      const centerX = gridSize / 2;
      const centerY = gridSize / 2;
      const distFromCenter = Math.sqrt(
        Math.pow(col - centerX, 2) + Math.pow(row - centerY, 2)
      );

      if (distFromCenter <= gridSize / 2) {
        // Assign status based on yield rate with some patterns
        let status = Math.random() < yieldRate ? "pass" : "fail";

        // Create a pattern of failures in a ring
        if (
          distFromCenter > gridSize / 2 - 2 &&
          distFromCenter < gridSize / 2 - 1
        ) {
          status = Math.random() < 0.5 ? "fail" : status;
        }

        // Create a cluster of failures
        if (row > gridSize * 0.7 && col < gridSize * 0.3) {
          status = Math.random() < 0.7 ? "fail" : status;
        }

        waferData[row][col] = {
          x: col,
          y: row,
          status: status,
          bin: status === "pass" ? 1 : Math.floor(Math.random() * 5) + 2, // 1 is pass, 2-6 are fail bins
          testData: generateTestData(status),
        };
      }
    }
  }

  return waferData;
}

// Generate sample test data for a die
function generateTestData(status) {
  const testCount = 10;
  const tests = [];

  for (let i = 1; i <= testCount; i++) {
    const isPass = status === "pass" ? true : i < 8 ? true : false;

    tests.push({
      testNumber: i,
      testName: `Test_${i}`,
      result: isPass ? "pass" : "fail",
      value: isPass
        ? (Math.random() * 4.5 + 0.5).toFixed(3) // Between 0.5 and 5.0 for pass
        : (Math.random() * 2 + 6).toFixed(3), // Between 6.0 and 8.0 for fail
      lowerLimit: "0.500",
      upperLimit: "5.000",
      unit: "mV",
    });
  }

  return tests;
}

// Open die information modal
function openDieInfoModal(x, y) {
  // In a real app, this would fetch die data from the actual dataset
  // For this demo, we'll just show sample data

  // Update modal with die information
  document.getElementById("die-coordinates").textContent = `X: ${x}, Y: ${y}`;
  document.getElementById("die-wafer-id").textContent =
    document.getElementById("wafer-id-value").textContent;
  document.getElementById("die-lot-id").textContent =
    document.getElementById("lot-id-value").textContent;

  // Set status randomly for the demo
  const isPass = Math.random() < 0.85;
  const dieStatus = document.getElementById("die-status");
  dieStatus.textContent = isPass ? "Pass" : "Fail";
  dieStatus.className = "die-status " + (isPass ? "pass" : "fail");

  document.getElementById("die-bin").textContent = isPass
    ? "1"
    : Math.floor(Math.random() * 5) + 2;

  // Generate test results table
  const testResults = document.getElementById("test-results-table");
  const tbody = testResults.querySelector("tbody");
  tbody.innerHTML = "";

  const testCount = 10;
  for (let i = 1; i <= testCount; i++) {
    const tr = document.createElement("tr");
    const testPass = isPass ? true : i < 8 ? true : false;

    tr.innerHTML = `
        <td>${i}</td>
        <td>Test_${i}</td>
        <td class="${testPass ? "pass" : "fail"}">${
      testPass ? "Pass" : "Fail"
    }</td>
        <td>${
          testPass
            ? (Math.random() * 4.5 + 0.5).toFixed(3)
            : (Math.random() * 2 + 6).toFixed(3)
        }</td>
        <td>0.500</td>
        <td>5.000</td>
        <td>mV</td>
    `;

    tbody.appendChild(tr);
  }

  // Show the modal
  const modal = document.getElementById("die-info-modal");
  openModal(modal);
}

// Draw bin chart
function drawBinChart() {
  const chartContainer = document.querySelector(".bin-chart");
  if (!chartContainer) return;

  // Sample bin data
  const binData = [
    { bin: 1, count: 1240, label: "Pass" },
    { bin: 2, count: 45, label: "Open" },
    { bin: 3, count: 32, label: "Short" },
    { bin: 4, count: 18, label: "Leakage" },
    { bin: 5, count: 22, label: "Parametric" },
    { bin: 6, count: 7, label: "Other" },
  ];

  // Find the maximum bin count for scaling
  const maxCount = Math.max(...binData.map((bin) => bin.count));
  const chartHeight = 250; // Max height in pixels

  // Create bars for the chart
  chartContainer.innerHTML = "";

  binData.forEach((bin) => {
    const barHeight = (bin.count / maxCount) * chartHeight;
    const barColor = bin.bin === 1 ? "#34c759" : "#ff3b30";

    const barElement = document.createElement("div");
    barElement.className = "bar";

    const barItemElement = document.createElement("div");
    barItemElement.className = "bar-item";
    barItemElement.style.height = `${barHeight}px`;
    barItemElement.style.backgroundColor = barColor;

    const barValueElement = document.createElement("div");
    barValueElement.className = "bar-value";
    barValueElement.textContent = bin.count;

    const barLabelElement = document.createElement("div");
    barLabelElement.className = "bar-label";
    barLabelElement.textContent = `Bin ${bin.bin} (${bin.label})`;

    barElement.appendChild(barItemElement);
    barElement.appendChild(barValueElement);
    barElement.appendChild(barLabelElement);

    chartContainer.appendChild(barElement);
  });

  // Update bin summary table
  const binTable = document.getElementById("bin-summary-table");
  if (binTable) {
    const tbody = binTable.querySelector("tbody");
    tbody.innerHTML = "";

    binData.forEach((bin) => {
      const tr = document.createElement("tr");
      const total = binData.reduce((sum, b) => sum + b.count, 0);
      const percentage = ((bin.count / total) * 100).toFixed(2);

      tr.innerHTML = `
        <td>${bin.bin}</td>
        <td>${bin.label}</td>
        <td>${bin.count}</td>
        <td>${percentage}%</td>
      `;

      tbody.appendChild(tr);
    });
  }
}

// Initialize wafer navigation
function initWaferNavigation() {
  const prevWaferBtn = document.getElementById("prev-wafer");
  const nextWaferBtn = document.getElementById("next-wafer");
  const lotLink = document.getElementById("lot-link");

  if (prevWaferBtn) {
    prevWaferBtn.addEventListener("click", () => {
      // In a real app, this would load the previous wafer data
      alert("Navigate to previous wafer");
    });
  }

  if (nextWaferBtn) {
    nextWaferBtn.addEventListener("click", () => {
      // In a real app, this would load the next wafer data
      alert("Navigate to next wafer");
    });
  }

  if (lotLink) {
    lotLink.addEventListener("click", (e) => {
      e.preventDefault();
      // In a real app, this would navigate to the lot summary page
      alert("Navigate to lot summary page");
    });
  }
}

// Initialize map display type selector
function initMapDisplayTypeSelector() {
  const mapDisplayType = document.getElementById("map-display-type");

  if (mapDisplayType) {
    mapDisplayType.addEventListener("change", () => {
      const displayType = mapDisplayType.value;
      // In a real app, this would change the wafer map visualization
      alert(`Change map display to: ${displayType}`);
    });
  }
}

// Initialize report actions
function initReportActions() {
  const exportPdfBtn = document.getElementById("export-pdf");
  const exportCsvBtn = document.getElementById("export-csv");
  const shareReportBtn = document.getElementById("share-report");

  if (exportPdfBtn) {
    exportPdfBtn.addEventListener("click", () => {
      // In a real app, this would generate and download a PDF
      alert("Exporting report as PDF");
    });
  }

  if (exportCsvBtn) {
    exportCsvBtn.addEventListener("click", () => {
      // In a real app, this would generate and download CSV data
      alert("Exporting data as CSV");
    });
  }

  if (shareReportBtn) {
    shareReportBtn.addEventListener("click", () => {
      // In a real app, this would open sharing options
      alert("Opening share options");
    });
  }
}

// Initialize wafer selection functionality
function initWaferSelection() {
  const currentWafer = document.getElementById("current-wafer");
  const waferItems = document.querySelectorAll(".wafer-item");
  const waferSearch = document.getElementById("wafer-search");

  if (currentWafer) {
    currentWafer.addEventListener("click", () => {
      // Show wafer selection modal
      const modal = document.getElementById("wafer-select-modal");
      openModal(modal);
    });
  }

  if (waferItems.length > 0) {
    waferItems.forEach((waferItem) => {
      waferItem.addEventListener("click", () => {
        // In a real app, this would load the selected wafer data
        const waferId = waferItem.querySelector(".wafer-id").textContent;
        alert(`Selected wafer: ${waferId}`);

        // Update active state
        waferItems.forEach((item) => item.classList.remove("active"));
        waferItem.classList.add("active");

        // Update current wafer display
        if (currentWafer) {
          currentWafer.textContent = waferId;
        }

        // Close modal
        const modal = document.getElementById("wafer-select-modal");
        closeModal(modal);
      });
    });
  }

  if (waferSearch) {
    waferSearch.addEventListener("input", () => {
      const searchTerm = waferSearch.value.toLowerCase();

      waferItems.forEach((waferItem) => {
        const waferId = waferItem
          .querySelector(".wafer-id")
          .textContent.toLowerCase();

        if (waferId.includes(searchTerm)) {
          waferItem.style.display = "flex";
        } else {
          waferItem.style.display = "none";
        }
      });
    });
  }
}

// Initialize modal action buttons
function initModalActions() {
  const viewSimilarDiesBtn = document.getElementById("view-similar-dies");
  const flagForReviewBtn = document.getElementById("flag-for-review");

  if (viewSimilarDiesBtn) {
    viewSimilarDiesBtn.addEventListener("click", () => {
      // In a real app, this would highlight similar dies on the wafer map
      alert("Highlighting similar dies on wafer map");
      closeModal(document.getElementById("die-info-modal"));
    });
  }

  if (flagForReviewBtn) {
    flagForReviewBtn.addEventListener("click", () => {
      // In a real app, this would flag the die for review
      alert("Die flagged for review");
      closeModal(document.getElementById("die-info-modal"));
    });
  }
}

// Navigation link handlers
document.addEventListener("DOMContentLoaded", () => {
  const lotSummaryLink = document.getElementById("lot-summary-link");
  const comparisonLink = document.getElementById("comparison-link");
  const footerLinks = document.querySelectorAll(".footer-nav a");

  if (lotSummaryLink) {
    lotSummaryLink.addEventListener("click", (e) => {
      e.preventDefault();
      // In a real app, this would navigate to the lot summary page
      alert("Navigate to lot summary page");
    });
  }

  if (comparisonLink) {
    comparisonLink.addEventListener("click", (e) => {
      e.preventDefault();
      // In a real app, this would navigate to the comparison page
      alert("Navigate to comparison page");
    });
  }

  if (footerLinks.length > 0) {
    footerLinks.forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        // In a real app, this would navigate to the respective page
        alert(`Navigate to ${link.textContent} page`);
      });
    });
  }
});

// Helper functions for modals
function openModal(modal) {
  if (modal) {
    modal.style.display = "flex";
    document.body.style.overflow = "hidden"; // Prevent scrolling behind modal
  }
}

function closeModal(modal) {
  if (modal) {
    modal.style.display = "none";
    document.body.style.overflow = ""; // Restore scrolling
  }
}

// Additional interactive elements for test tab
document.addEventListener("DOMContentLoaded", () => {
  const testSelect = document.getElementById("test-select");
  const trendPeriod = document.getElementById("trend-period");
  const compareBinsBtn = document.getElementById("compare-bins");

  if (testSelect) {
    testSelect.addEventListener("change", () => {
      const selectedTest = testSelect.value;
      // In a real app, this would update the test distribution chart and statistics
      document.querySelector(
        ".chart-message"
      ).textContent = `Showing distribution for ${
        testSelect.options[testSelect.selectedIndex].text
      }`;
    });
  }

  if (trendPeriod) {
    trendPeriod.addEventListener("change", () => {
      const period = trendPeriod.value;
      // In a real app, this would update the bin trend chart
      document.querySelector(
        ".placeholder-chart"
      ).textContent = `Showing bin trend for ${period} period`;
    });
  }

  if (compareBinsBtn) {
    compareBinsBtn.addEventListener("click", () => {
      // In a real app, this would open a comparison view
      alert("Opening bin comparison view");
    });
  }
});
