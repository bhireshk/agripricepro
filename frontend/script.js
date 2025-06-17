// frontend/script.js

// --- Configuration ---
// IMPORTANT: Replace this with the actual URL of your backend API
const BACKEND_API_BASE_URL = 'http://localhost:5000/api'; // Assuming Flask backend on port 5000

// --- Global Data Holders (Crucial for storing fetched metadata) ---
let globalPredictionData = null; // Stores the prediction result from the backend
let globalCropTypesByCategory = {}; // e.g., { "Cereals": ["Rice", "Wheat"] }
let globalStatesByCountry = {}; // e.g., { "India": ["Karnataka", "Maharashtra"] }


// --- DOM Elements ---
const getForecastBtn = document.getElementById('get-forecast-btn');
const predictionForm = document.getElementById('prediction-form');
const closeFormBtn = document.getElementById('close-form-btn');
const backToFormBtn = document.getElementById('back-to-form');
const predictionDashboard = document.getElementById('prediction-dashboard');
const cropCategorySelect = document.getElementById('crop-category');
const cropTypeSelect = document.getElementById('crop-type');
const countrySelect = document.getElementById('country');
const stateSelect = document.getElementById('state');
const seasonSelect = document.getElementById('season');
const predictBtn = document.getElementById('predict-btn');
const predictBtnText = document.getElementById('predict-btn-text');
const predictLoader = document.getElementById('predict-loader');

const predictionTitle = document.getElementById('prediction-title');
const predictionLocation = document.getElementById('prediction-location');
const predictionSeason = document.getElementById('prediction-season');
const lastUpdated = document.getElementById('last-updated');
const predictedPrice = document.getElementById('predicted-price');
const priceChange = document.getElementById('price-change');

// Factors and Recommendations
const weatherFactor = document.getElementById('weather-factor');
const weatherImpact = document.getElementById('weather-impact');
const supplyFactor = document.getElementById('supply-factor');
const supplyImpact = document.getElementById('supply-impact');
const demandFactor = document.getElementById('demand-factor');
const demandImpact = document.getElementById('demand-impact');
const recommendationSellTime = document.getElementById('recommendation-sell-time');
const recommendationTrend = document.getElementById('recommendation-trend');

const futureChartCanvas = document.getElementById('future-chart').getContext('2d');
const historicalChartCanvas = document.getElementById('historical-chart').getContext('2d');

const chartViewBtn = document.getElementById('chart-view-btn');
const tableViewBtn = document.getElementById('table-view-btn');
const tableView = document.getElementById('table-view');
const priceTableBody = document.getElementById('price-table-body');

let futureChart;
let historicalChart;


// --- Chart Configuration ---
const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false
        },
        tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
                label: function(context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        // Use unit from backend data if available, or default
                        const unit = globalPredictionData?.unit || '/unit';
                        label += `₹${context.parsed.y.toFixed(2)}${unit}`;
                    }
                    return label;
                }
            }
        }
    },
    scales: {
        y: {
            beginAtZero: false,
            title: {
                display: true,
                text: 'Price (₹)'
            },
        },
        x: {
            title: {
                display: true,
                text: 'Month'
            }
        }
    }
};

// --- API Fetching Functions ---

/**
 * Fetches initial dropdown data (categories, countries, seasons, crop types by category, states by country)
 * from the backend and populates the initial dropdowns.
 */
async function fetchInitialData() {
    try {
        const response = await fetch(`${BACKEND_API_BASE_URL}/metadata`);
        if (!response.ok) {
            // Throw an error with status and text for better debugging
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
        const data = await response.json();
        console.log("Fetched initial data:", data); // For debugging

        // Populate top-level dropdowns
        populateDropdown(cropCategorySelect, data.crop_categories || []);
        populateDropdown(countrySelect, data.countries || []);
        populateDropdown(seasonSelect, data.seasons || []);

        // Store the detailed data for dynamic updates of dependent dropdowns
        if (data.crop_types_by_category) {
            globalCropTypesByCategory = data.crop_types_by_category;
        }
        if (data.states_by_country) {
            globalStatesByCountry = data.states_by_country;
        }

        checkFormValidity();
    } catch (error) {
        console.error("Error fetching initial data:", error);
        alert("Failed to load initial data. Please check your backend server and network connection.");
    }
}

/**
 * Populates the Crop Type dropdown based on the selected Crop Category.
 */
function populateCropTypes() {
    const selectedCategory = cropCategorySelect.value;
    cropTypeSelect.innerHTML = '<option value="" disabled selected>Select crop type</option>';
    cropTypeSelect.disabled = true; // Disable until a valid category is chosen

    if (selectedCategory && globalCropTypesByCategory[selectedCategory]) {
        populateDropdown(cropTypeSelect, globalCropTypesByCategory[selectedCategory]);
        cropTypeSelect.disabled = false;
    }
    checkFormValidity();
}

/**
 * Populates the State/Province dropdown based on the selected Country.
 */
function populateStates() {
    const selectedCountry = countrySelect.value;
    stateSelect.innerHTML = '<option value="" disabled selected>Select state</option>';
    stateSelect.disabled = true; // Disable until a valid country is chosen

    if (selectedCountry && globalStatesByCountry[selectedCountry]) {
        populateDropdown(stateSelect, globalStatesByCountry[selectedCountry]);
        stateSelect.disabled = false;
    }
    checkFormValidity();
}

/**
 * Sends the prediction request to the backend with selected form data.
 * @param {Object} payload - The form data to send.
 * @returns {Promise<Object>} The prediction data from the backend.
 */
async function getPredictionFromBackend(payload) {
    console.log("Sending prediction request:", payload);
    try {
        const response = await fetch(`${BACKEND_API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        const data = await response.json();
        console.log("Prediction data received:", data);
        return data;
    } catch (error) {
        console.error("Error fetching prediction:", error);
        alert(`Prediction failed: ${error.message}. Please check your inputs and try again.`);
        return null;
    }
}

// --- Helper Functions ---

/**
 * Generic function to populate a select dropdown.
 * @param {HTMLSelectElement} selectElement - The select element to populate.
 * @param {Array<string>} options - An array of strings for option values/texts.
 */
function populateDropdown(selectElement, options) {
    // Clear existing options, keeping the first (disabled selected) one
    const initialOption = selectElement.options[0];
    selectElement.innerHTML = '';
    selectElement.appendChild(initialOption);

    options.forEach(optionText => {
        const option = document.createElement('option');
        option.value = optionText;
        option.textContent = optionText;
        selectElement.appendChild(option);
    });
}

/**
 * Checks if all required form fields are selected and enables/disables the predict button.
 */
function checkFormValidity() {
    const isFormValid = cropCategorySelect.value && cropTypeSelect.value &&
                        countrySelect.value && stateSelect.value && seasonSelect.value;
    predictBtn.disabled = !isFormValid;
}

/**
 * Updates the main prediction summary display on the dashboard.
 * @param {Object} data - The prediction data from the backend.
 */
function updatePredictionDisplay(data) {
    if (!data) return;

    predictionTitle.textContent = `${data.crop_type} Price Prediction`;
    predictionLocation.textContent = `${data.state}, ${data.country}`;
    predictionSeason.textContent = data.season;
    // Set last updated to current date for the demo
    lastUpdated.textContent = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    predictedPrice.textContent = `₹${data.predicted_price.toFixed(2)}${data.unit || '/unit'}`;

    // Update price change percentage and arrow
    const currentPrice = data.current_price; // Assuming backend provides a 'current_price'
    if (currentPrice !== undefined && currentPrice !== null) { // Check for valid current_price
        const change = data.predicted_price - currentPrice;
        const percentageChange = (change / currentPrice) * 100;
        priceChange.innerHTML = `
            <i class="fas ${percentageChange >= 0 ? 'fa-arrow-up text-green-600' : 'fa-arrow-down text-red-600'} mr-1"></i>
            ${Math.abs(percentageChange).toFixed(2)}%
        `;
        // Ensure only one color class is applied
        priceChange.classList.remove('text-green-600', 'text-red-600');
        priceChange.classList.add(percentageChange >= 0 ? 'text-green-600' : 'text-red-600');
    } else {
        priceChange.innerHTML = `<span class="text-gray-500">N/A (Current price not available)</span>`;
        priceChange.classList.remove('text-green-600', 'text-red-600'); // Remove any previous color
    }
}

/**
 * Updates and renders the Chart.js graphs for future and historical prices.
 * @param {Object} data - The prediction data from the backend.
 */
function updateCharts(data) {
    if (!data || !data.future_prices || !data.historical_prices) {
        console.warn("Chart data missing from backend response.");
        return;
    }

    // Destroy existing charts if they exist to prevent memory leaks and drawing issues
    if (futureChart) futureChart.destroy();
    if (historicalChart) historicalChart.destroy();

    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();

    // Generate future month labels (e.g., Jun '25, Jul '25, ...)
    const futureLabels = Array.from({ length: data.future_prices.length }, (_, i) => {
        // Start from next month (currentMonth + 1) for the first future price
        const date = new Date(currentYear, currentMonth + i + 1, 1);
        return date.toLocaleString('en-US', { month: 'short', year: '2-digit' });
    });

    // Generate historical month labels (e.g., May '23, Jun '23, ...)
    const historicalLabels = Array.from({ length: data.historical_prices.length }, (_, i) => {
        // Go back in time from the current month
        const date = new Date(currentYear, currentMonth - data.historical_prices.length + i + 1, 1);
        return date.toLocaleString('en-US', { month: 'short', year: '2-digit' });
    });

    futureChart = new Chart(futureChartCanvas, {
        type: 'line',
        data: {
            labels: futureLabels,
            datasets: [{
                label: 'Predicted Price',
                data: data.future_prices,
                borderColor: '#FF9900', // Amazon-orange
                backgroundColor: 'rgba(255, 153, 0, 0.2)', // Semi-transparent orange
                tension: 0.3, // Smoothen the line
                fill: false,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: chartOptions
    });

    historicalChart = new Chart(historicalChartCanvas, {
        type: 'line',
        data: {
            labels: historicalLabels,
            datasets: [{
                label: 'Historical Price',
                data: data.historical_prices,
                borderColor: '#232F3E', // Amazon-dark (navbar lower)
                backgroundColor: 'rgba(35, 47, 62, 0.2)', // Semi-transparent dark
                tension: 0.3,
                fill: false,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: chartOptions
    });
}

/**
 * Populates the price table with future predicted prices.
 * @param {Object} data - The prediction data from the backend.
 */
function updateTable(data) {
    if (!data || !data.future_prices) return;

    priceTableBody.innerHTML = ''; // Clear previous data

    const currentMonth = new Date().getMonth();
    const currentYear = new Date().getFullYear();

    data.future_prices.forEach((price, i) => {
        const date = new Date(currentYear, currentMonth + i + 1, 1);
        const monthYear = date.toLocaleString('en-US', { month: 'long', year: 'numeric' });

        // Compare to previous predicted price if available, else to the current price from backend
        const prevPrice = (i > 0) ? data.future_prices[i-1] : data.current_price;
        const change = price - prevPrice;
        const percentageChange = (prevPrice !== 0 && prevPrice !== undefined && prevPrice !== null) ? (change / prevPrice) * 100 : 0; // Handle division by zero

        const confidence = data.confidence_scores?.[i]?.toFixed(1) || 'N/A'; // Get confidence if available

        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50'; // Tailwind class for hover effect
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${monthYear}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">₹${price.toFixed(2)}${data.unit || '/unit'}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm ${percentageChange >= 0 ? 'text-green-600' : 'text-red-600'}">
                <i class="fas ${percentageChange >= 0 ? 'fa-arrow-up' : 'fa-arrow-down'} mr-1"></i>
                ${Math.abs(percentageChange).toFixed(2)}%
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${confidence}%</td>
        `;
        priceTableBody.appendChild(row);
    });
}

/**
 * Updates the "Key Factors" and "AI Recommendations" sections with data from the backend.
 * @param {Object} data - The prediction data from the backend.
 */
function updateFactorsAndRecommendations(data) {
    if (!data || !data.factors || !data.recommendations) {
        console.warn("Factors or recommendations data missing from backend response.");
        return;
    }

    // Update Key Factors
    weatherFactor.textContent = data.factors.weather?.condition || 'N/A';
    weatherImpact.textContent = data.factors.weather?.impact || '';
    weatherImpact.className = `mt-1 text-sm ${data.factors.weather?.impact_color || 'text-gray-600'}`;

    supplyFactor.textContent = data.factors.supply?.condition || 'N/A';
    supplyImpact.textContent = data.factors.supply?.impact || '';
    supplyImpact.className = `mt-1 text-sm ${data.factors.supply?.impact_color || 'text-gray-600'}`;

    demandFactor.textContent = data.factors.demand?.condition || 'N/A';
    demandImpact.textContent = data.factors.demand?.impact || '';
    demandImpact.className = `mt-1 text-sm ${data.factors.demand?.impact_color || 'text-gray-600'}`;

    // Update AI Recommendations
    recommendationSellTime.textContent = data.recommendations.sell_time || 'No specific recommendation available.';
    recommendationTrend.textContent = data.recommendations.trend_analysis || 'No detailed trend analysis available.';
}


// --- Event Listeners ---
getForecastBtn.addEventListener('click', () => {
    predictionForm.classList.remove('form-hidden');
    predictionForm.classList.add('form-visible');
    predictionForm.scrollIntoView({ behavior: 'smooth' });
});

closeFormBtn.addEventListener('click', () => {
    predictionForm.classList.remove('form-visible');
    predictionForm.classList.add('form-hidden');
});

backToFormBtn.addEventListener('click', () => {
    predictionDashboard.classList.remove('prediction-visible');
    predictionDashboard.classList.add('prediction-hidden');
    predictionForm.classList.remove('form-hidden');
    predictionForm.classList.add('form-visible');
});

cropCategorySelect.addEventListener('change', populateCropTypes);
cropTypeSelect.addEventListener('change', checkFormValidity); // Check validity after crop type change
countrySelect.addEventListener('change', populateStates);
stateSelect.addEventListener('change', checkFormValidity); // Check validity after state change
seasonSelect.addEventListener('change', checkFormValidity); // Check validity after season change

// Main Prediction Button Click Handler
predictBtn.addEventListener('click', async (e) => {
    e.preventDefault(); // Prevent default form submission

    // Show loading state
    predictBtnText.textContent = 'Predicting...';
    predictLoader.classList.remove('hidden');
    predictBtn.disabled = true;

    const payload = {
        crop_category: cropCategorySelect.value,
        crop_type: cropTypeSelect.value,
        country: countrySelect.value,
        state: stateSelect.value,
        season: seasonSelect.value
    };

    globalPredictionData = await getPredictionFromBackend(payload);

    // Hide loading state
    predictBtnText.textContent = 'Predict Price';
    predictLoader.classList.add('hidden');
    predictBtn.disabled = false; // Re-enable button regardless of success/failure, user can try again

    if (globalPredictionData) {
        // Hide form and show dashboard
        predictionForm.classList.remove('form-visible');
        predictionForm.classList.add('form-hidden');
        predictionDashboard.classList.remove('prediction-hidden');
        predictionDashboard.classList.add('prediction-visible');
        predictionDashboard.scrollIntoView({ behavior: 'smooth' });

        // Update all dashboard elements
        updatePredictionDisplay(globalPredictionData);
        updateCharts(globalPredictionData);
        updateTable(globalPredictionData);
        updateFactorsAndRecommendations(globalPredictionData);

        // Reset chart/table view to chart view when showing dashboard
        chartViewBtn.click();
    }
});

// --- Chart/Table View Toggle ---
chartViewBtn.addEventListener('click', () => {
    chartViewBtn.classList.add('bg-white', 'shadow');
    tableViewBtn.classList.remove('bg-white', 'shadow');
    document.getElementById('future-chart').closest('.card').parentElement.classList.remove('hidden'); // Show chart parents
    document.getElementById('historical-chart').closest('.card').parentElement.classList.remove('hidden');
    tableView.classList.add('hidden');
});

tableViewBtn.addEventListener('click', () => {
    tableViewBtn.classList.add('bg-white', 'shadow');
    chartViewBtn.classList.remove('bg-white', 'shadow');
    document.getElementById('future-chart').closest('.card').parentElement.classList.add('hidden'); // Hide chart parents
    document.getElementById('historical-chart').closest('.card').parentElement.classList.add('hidden');
    tableView.classList.remove('hidden');
});

// --- Initial Data Load on Page Load ---
document.addEventListener('DOMContentLoaded', () => {
    fetchInitialData();
    // checkFormValidity() is called inside fetchInitialData
});