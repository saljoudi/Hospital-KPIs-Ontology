// Add at the top of dashboard.js
const API_BASE = window.location.origin; // Auto-detects the domain

// Update all fetch calls to use full URL
async function loadKPIs() {
    try {
        const response = await fetch(`${API_BASE}/api/kpis`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const kpis = await response.json();
        populateKPITable(kpis);
    } catch (error) {
        console.error('Error loading KPIs:', error);
        document.getElementById('kpi-table').innerHTML = 
            `<tr><td colspan="7" class="text-danger">Error loading data: ${error.message}</td></tr>`;
    }
}

async function loadSummary() {
    try {
        const [kpisResponse, deptResponse] = await Promise.all([
            fetch(`${API_BASE}/api/kpis`),
            fetch(`${API_BASE}/api/departments`)
        ]);
        
        if (!kpisResponse.ok || !deptResponse.ok) {
            throw new Error('API response failed');
        }
        
        const kpis = await kpisResponse.json();
        const departments = await deptResponse.json();
        populateSummaryCards(kpis, departments);
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

async function runReasoning() {
    const button = document.querySelector('button[onclick="runReasoning()"]');
    button.disabled = true;
    button.innerHTML = '<i class="bi bi-gear"></i> Analyzing...';
    
    try {
        const response = await fetch(`${API_BASE}/api/reasoning`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const results = await response.json();
        
        populateAlerts(results.alerts);
        populateRecommendations(results.recommendations);
        populateInsights(results.insights);
        
    } catch (error) {
        console.error('Error running reasoning:', error);
        alert(`Failed to run reasoning engine: ${error.message}`);
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-gear"></i> Run Reasoning';
    }
}
