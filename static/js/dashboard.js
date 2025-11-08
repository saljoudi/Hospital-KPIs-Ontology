// KPI Dashboard JavaScript

// Base API URL (auto-detects production vs local)
const API_BASE = window.location.origin;

// Auto-load data when page opens
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard initializing...');
    loadKPIs();
    loadSummary();
});

// Load KPI data
async function loadKPIs() {
    console.log('📊 Loading KPIs from:', `${API_BASE}/api/kpis`);
    try {
        const response = await fetch(`${API_BASE}/api/kpis`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const kpis = await response.json();
        console.log('✅ Received', kpis.length, 'KPIs');
        populateKPITable(kpis);
        
        // Hide loading, show content
        document.getElementById('loading-message').style.display = 'none';
        document.getElementById('dashboard-content').style.display = 'block';
        
    } catch (error) {
        console.error('❌ Error loading KPIs:', error);
        showError('kpi-table', `Failed to load KPIs: ${error.message}`);
    }
}

// Populate KPI table
function populateKPITable(kpis) {
    const tbody = document.querySelector('#kpi-table');
    if (!tbody) {
        console.error('❌ KPI table element not found');
        return;
    }
    
    tbody.innerHTML = ''; // Clear existing
    
    if (kpis.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No KPI data available</td></tr>';
        return;
    }
    
    kpis.forEach(kpi => {
        const row = document.createElement('tr');
        row.classList.add('card-hover');
        
        // Calculate performance ratio
        const ratio = ((kpi.actual / kpi.target) * 100).toFixed(1);
        
        // Status badge
        const statusBadge = `<span class="badge status-${kpi.status}">${kpi.status.toUpperCase()}</span>`;
        
        // Trend indicator
        const trendIcon = {
            'up': '📈',
            'down': '📉',
            'stable': '➡️'
        }[kpi.trend] || '➡️';
        
        row.innerHTML = `
            <td><strong>${kpi.name}</strong></td>
            <td>${kpi.department}</td>
            <td>${kpi.actual} ${kpi.unit || ''}</td>
            <td>${kpi.target} ${kpi.unit || ''}</td>
            <td>${statusBadge}</td>
            <td>${trendIcon} ${kpi.trend}</td>
        `;
        
        // Add click handler for detail view
        row.style.cursor = 'pointer';
        row.onclick = () => window.location.href = `/api/kpi/${kpi.id}`;
        
        tbody.appendChild(row);
    });
}

// Load summary cards
async function loadSummary() {
    console.log('📈 Loading summary data...');
    try {
        const [kpisResponse, deptResponse] = await Promise.all([
            fetch(`${API_BASE}/api/kpis`),
            fetch(`${API_BASE}/api/departments`)
        ]);
        
        if (!kpisResponse.ok || !deptResponse.ok) {
            throw new Error('Failed to load summary data');
        }
        
        const kpis = await kpisResponse.json();
        const departments = await deptResponse.json();
        
        populateSummaryCards(kpis, departments);
        
    } catch (error) {
        console.error('❌ Error loading summary:', error);
    }
}

// Populate summary cards
function populateSummaryCards(kpis, departments) {
    const container = document.getElementById('summary-cards');
    if (!container) return;
    
    const totalKPIs = kpis.length;
    const criticalKPIs = kpis.filter(k => k.status === 'critical').length;
    const goodKPIs = kpis.filter(k => k.status === 'good').length;
    const avgHealth = Math.round((goodKPIs / totalKPIs) * 100);
    
    container.innerHTML = `
        <div class="col-md-3">
            <div class="card metric-card ${criticalKPIs > 3 ? 'critical' : 'good'}">
                <div class="card-body">
                    <h3>${totalKPIs}</h3>
                    <p class="mb-0">Total KPIs</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card metric-card ${criticalKPIs > 3 ? 'critical' : 'good'}">
                <div class="card-body">
                    <h3>${criticalKPIs}</h3>
                    <p class="mb-0">Critical KPIs</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card metric-card good">
                <div class="card-body">
                    <h3>${avgHealth}%</h3>
                    <p class="mb-0">Health Score</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card metric-card good">
                <div class="card-body">
                    <h3>${Object.keys(departments).length}</h3>
                    <p class="mb-0">Departments</p>
                </div>
            </div>
        </div>
    `;
}

// Run reasoning engine
async function runReasoning() {
    console.log('🧠 Running reasoning engine...');
    const button = document.querySelector('button[onclick="runReasoning()"]');
    if (!button) {
        console.error('Reasoning button not found');
        return;
    }
    
    button.disabled = true;
    button.innerHTML = '<i class="bi bi-gear"></i> Analyzing...';
    
    try {
        const response = await fetch(`${API_BASE}/api/reasoning`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const results = await response.json();
        console.log('✅ Reasoning results:', results);
        
        populateAlerts(results.alerts);
        populateRecommendations(results.recommendations);
        populateInsights(results.insights);
        
    } catch (error) {
        console.error('❌ Error running reasoning:', error);
        alert(`Failed: ${error.message}`);
    } finally {
        button.disabled = false;
        button.innerHTML = '<i class="bi bi-gear"></i> Run Reasoning';
    }
}

// Populate alerts panel
function populateAlerts(alerts) {
    const panel = document.getElementById('alerts-panel');
    if (!panel) return;
    
    if (!alerts || alerts.length === 0) {
        panel.innerHTML = '<p class="text-success"><i class="bi bi-check-circle"></i> No alerts detected</p>';
        return;
    }
    
    panel.innerHTML = alerts.map(alert => `
        <div class="alert alert-${alert.level.toLowerCase()} mb-2">
            <strong>${alert.type}</strong><br>
            ${alert.message}
            <br><small class="text-muted">${new Date(alert.timestamp).toLocaleTimeString()}</small>
        </div>
    `).join('');
}

// Populate recommendations panel
function populateRecommendations(recommendations) {
    const panel = document.getElementById('recommendations-panel');
    if (!panel) return;
    
    if (!recommendations || recommendations.length === 0) {
        panel.innerHTML = '<p class="text-muted">No recommendations at this time</p>';
        return;
    }
    
    panel.innerHTML = recommendations.map(rec => `
        <div class="recommendation-item mb-2">
            <span class="badge bg-${rec.priority.includes('CRITICAL') ? 'danger' : 'warning'}">${rec.priority}</span><br>
            <strong>Action:</strong> ${rec.action}<br>
            <strong>Owner:</strong> ${rec.owner}<br>
            <small class="text-muted">Timeline: ${rec.timeline}</small>
        </div>
    `).join('');
}

// Populate insights panel
function populateInsights(insights) {
    const panel = document.getElementById('insights-panel');
    if (!panel) return;
    
    if (!insights || insights.length === 0) {
        panel.innerHTML = '<small class="text-muted">No analysis yet. Click "Run Reasoning".</small>';
        return;
    }
    
    panel.innerHTML = insights.map(insight => 
        `<div class="text-muted mb-1">• ${insight}</div>`
    ).join('');
}

// Error helper
function showError(elementId, message) {
    const elem = document.getElementById(elementId);
    if (elem) {
        elem.innerHTML = `<tr><td colspan="7" class="text-danger">${message}</td></tr>`;
    }
}
