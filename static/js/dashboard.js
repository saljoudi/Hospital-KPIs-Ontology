// Hospital KPI Dashboard JavaScript - Production Version

// =============================================================================
// CONFIGURATION
// =============================================================================
const API_BASE = window.location.origin;
let isReasoningRunning = false;

// =============================================================================
// INITIALIZATION
// =============================================================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🏥 Hospital KPI Dashboard initializing...');
    console.log('API Base URL:', API_BASE);
    
    // Check if all required DOM elements exist
    const requiredElements = ['kpi-table', 'summary-cards', 'alerts-panel', 'recommendations-panel', 'insights-panel'];
    const missingElements = requiredElements.filter(id => !document.getElementById(id));
    
    if (missingElements.length > 0) {
        console.error('❌ Missing DOM elements:', missingElements);
        showFatalError(`Missing dashboard elements: ${missingElements.join(', ')}`);
        return;
    }
    
    // Load initial data
    Promise.all([loadKPIs(), loadSummary()])
        .then(() => {
            console.log('✅ Initial data loaded successfully');
            hideLoadingMessage();
            showDashboardContent();
        })
        .catch(error => {
            console.error('❌ Failed to load initial data:', error);
            showFatalError(`Failed to load dashboard: ${error.message}`);
        });
});

// =============================================================================
// DATA LOADING FUNCTIONS
// =============================================================================
async function loadKPIs() {
    console.log('📊 Loading KPIs...');
    const startTime = performance.now();
    
    try {
        const response = await fetch(`${API_BASE}/api/kpis`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const kpis = await response.json();
        const endTime = performance.now();
        
        console.log(`✅ Loaded ${kpis.length} KPIs in ${(endTime - startTime).toFixed(2)}ms`);
        
        if (kpis.length === 0) {
            showError('kpi-table', 'No KPI data available');
            return;
        }
        
        populateKPITable(kpis);
        
    } catch (error) {
        console.error('❌ Error loading KPIs:', error);
        showError('kpi-table', `Failed to load KPIs: ${error.message}`);
        throw error; // Re-throw to catch in initialization
    }
}

async function loadSummary() {
    console.log('📈 Loading summary data...');
    
    try {
        const [kpisResponse, deptResponse] = await Promise.all([
            fetch(`${API_BASE}/api/kpis`),
            fetch(`${API_BASE}/api/departments`)
        ]);
        
        if (!kpisResponse.ok || !deptResponse.ok) {
            throw new Error('One or more summary endpoints failed');
        }
        
        const kpis = await kpisResponse.json();
        const departments = await deptResponse.json();
        
        console.log(`✅ Summary: ${kpis.length} KPIs, ${Object.keys(departments).length} departments`);
        
        populateSummaryCards(kpis, departments);
        
    } catch (error) {
        console.error('❌ Error loading summary:', error);
        showError('summary-cards', `Failed to load summary: ${error.message}`);
        throw error;
    }
}

// =============================================================================
// UI POPULATION FUNCTIONS
// =============================================================================
function populateKPITable(kpis) {
    console.log('🎨 Populating KPI table...');
    const tbody = document.getElementById('kpi-table');
    
    if (!tbody) {
        console.error('❌ KPI table tbody not found');
        return;
    }
    
    // Clear existing content
    tbody.innerHTML = '';
    
    // Sort KPIs by weight (most important first)
    kpis.sort((a, b) => (b.weight || 0) - (a.weight || 0));
    
    kpis.forEach((kpi, index) => {
        const row = document.createElement('tr');
        row.className = 'card-hover';
        row.style.cursor = 'pointer';
        
        // Status badge
        const statusClass = kpi.status || 'unknown';
        const statusBadge = `<span class="badge status-${statusClass}">${statusClass.toUpperCase()}</span>`;
        
        // Trend icon
        const trendIcon = {
            'up': '📈',
            'down': '📉',
            'stable': '➡️'
        }[kpi.trend] || '➡️';
        
        // Performance ratio
        const ratio = kpi.target > 0 ? ((kpi.actual / kpi.target) * 100).toFixed(1) : 'N/A';
        
        row.innerHTML = `
            <td>
                <strong>${kpi.name || 'Unnamed KPI'}</strong><br>
                <small class="text-muted">${kpi.department || 'Unknown Dept'}</small>
            </td>
            <td>${kpi.category || 'Unknown'}</td>
            <td>
                ${kpi.actual} ${kpi.unit || ''}<br>
                <small class="text-muted">${ratio}% of target</small>
            </td>
            <td>${kpi.target} ${kpi.unit || ''}</td>
            <td>${statusBadge}</td>
            <td>${trendIcon} ${kpi.trend || 'unknown'}</td>
        `;
        
        // Add click handler for detail view
        row.onclick = () => {
            console.log('🔍 Opening details for:', kpi.id);
            window.location.href = `/api/kpi/${kpi.id}`;
        };
        
        tbody.appendChild(row);
    });
    
    console.log(`✅ Populated ${kpis.length} rows in KPI table`);
}

function populateSummaryCards(kpis, departments) {
    console.log('📊 Populating summary cards...');
    const container = document.getElementById('summary-cards');
    
    if (!container) {
        console.error('❌ Summary cards container not found');
        return;
    }
    
    // Calculate metrics
    const totalKPIs = kpis.length;
    const criticalKPIs = kpis.filter(k => k.status === 'critical').length;
    const warningKPIs = kpis.filter(k => k.status === 'warning').length;
    const goodKPIs = kpis.filter(k => k.status === 'good').length;
    const healthScore = totalKPIs > 0 ? Math.round((goodKPIs / totalKPIs) * 100) : 0;
    
    // Determine overall health color
    const healthColor = criticalKPIs > 3 ? 'critical' : 
                       warningKPIs > 5 ? 'warning' : 'good';
    
    container.innerHTML = `
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card metric-card ${healthColor} h-100">
                <div class="card-body text-center">
                    <h2 class="mb-0">${totalKPIs}</h2>
                    <p class="mb-0 text-muted">Total KPIs</p>
                    <small class="text-success">${goodKPIs} performing well</small>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card metric-card ${criticalKPIs > 0 ? 'critical' : 'good'} h-100">
                <div class="card-body text-center">
                    <h2 class="mb-0">${criticalKPIs}</h2>
                    <p class="mb-0 text-muted">Critical KPIs</p>
                    <small class="text-danger">${criticalKPIs} need immediate attention</small>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card metric-card ${healthColor} h-100">
                <div class="card-body text-center">
                    <h2 class="mb-0">${healthScore}%</h2>
                    <p class="mb-0 text-muted">Health Score</p>
                    <div class="progress mt-2" style="height: 8px;">
                        <div class="progress-bar bg-${healthColor === 'good' ? 'success' : healthColor === 'warning' ? 'warning' : 'danger'}" 
                             style="width: ${healthScore}%"></div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-3 mb-3">
            <div class="card metric-card good h-100">
                <div class="card-body text-center">
                    <h2 class="mb-0">${Object.keys(departments).length}</h2>
                    <p class="mb-0 text-muted">Departments</p>
                    <small class="text-success">All departments monitored</small>
                </div>
            </div>
        </div>
    `;
    
    console.log('✅ Summary cards populated');
}

// =============================================================================
// REASONING ENGINE FUNCTIONS
// =============================================================================
async function runReasoning() {
    if (isReasoningRunning) {
        console.log('⚠️ Reasoning already running, ignoring click');
        return;
    }
    
    console.log('🧠 Starting reasoning engine...');
    isReasoningRunning = true;
    
    const button = document.querySelector('button[onclick="runReasoning()"]');
    const buttonOriginalHTML = button.innerHTML;
    
    // Update button state
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Analyzing...';
    
    // Clear previous results
    document.getElementById('alerts-panel').innerHTML = '<p class="text-muted">Analyzing...</p>';
    document.getElementById('recommendations-panel').innerHTML = '<p class="text-muted">Generating insights...</p>';
    document.getElementById('insights-panel').innerHTML = '<small class="text-muted">Processing...</small>';
    
    try {
        console.log('📡 Fetching reasoning results...');
        const response = await fetch(`${API_BASE}/api/reasoning`, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP ${response.status}: ${errorText}`);
        }
        
        const results = await response.json();
        console.log('✅ Received reasoning results:', results);
        
        // Populate all panels
        populateAlerts(results.alerts || []);
        populateRecommendations(results.recommendations || []);
        populateInsights(results.insights || []);
        
        // Show success banner
        showTemporaryBanner(`✅ Analysis complete! Found ${results.alerts?.length || 0} alerts.`, 'success');
        
    } catch (error) {
        console.error('❌ Reasoning failed:', error);
        showTemporaryBanner(`Analysis failed: ${error.message}`, 'danger');
        
        // Show error in panels
        document.getElementById('alerts-panel').innerHTML = 
            `<div class="alert alert-danger">Failed to analyze: ${error.message}</div>`;
        document.getElementById('recommendations-panel').innerHTML = '';
        document.getElementById('insights-panel').innerHTML = '';
        
    } finally {
        // Restore button
        button.disabled = false;
        button.innerHTML = buttonOriginalHTML;
        isReasoningRunning = false;
        console.log('🏁 Reasoning complete');
    }
}

function populateAlerts(alerts) {
    console.log('🚨 Populating alerts:', alerts.length);
    const panel = document.getElementById('alerts-panel');
    
    if (!panel) return;
    
    if (!alerts || alerts.length === 0) {
        panel.innerHTML = '<div class="alert alert-success"><i class="bi bi-check-circle"></i> No alerts detected - all systems performing within normal parameters</div>';
       
