/**
 * Financial Fraud Detection Platform - Dashboard Client
 */

let decisionChartInstance = null;
let riskDistChartInstance = null;

// Currency Configuration (INR, USD, EUR, GBP)
const CURRENCIES = {
    INR: { symbol: '₹', code: 'INR', locale: 'en-IN' },
    USD: { symbol: '$', code: 'USD', locale: 'en-US' },
    EUR: { symbol: '€', code: 'EUR', locale: 'de-DE' },
    GBP: { symbol: '£', code: 'GBP', locale: 'en-GB' }
};

let currentCurrency = localStorage.getItem('fraud_det_currency') || 'USD';

function formatCurrencyAmount(amount) {
    const config = CURRENCIES[currentCurrency] || CURRENCIES.USD;
    try {
        const formatted = Number(amount).toLocaleString(config.locale, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        return `${config.symbol}${formatted}`;
    } catch (e) {
        return `${config.symbol}${Number(amount).toFixed(2)}`;
    }
}

function onCurrencyChange(currencyCode) {
    if (!CURRENCIES[currencyCode]) return;
    currentCurrency = currencyCode;
    localStorage.setItem('fraud_det_currency', currencyCode);
    updateCurrencyDisplay();
    fetchAuditLog();
}

function updateCurrencyDisplay() {
    const config = CURRENCIES[currentCurrency] || CURRENCIES.USD;
    const selector = document.getElementById('currencySelector');
    if (selector) selector.value = currentCurrency;

    document.querySelectorAll('.currencySymbolDisplay').forEach(el => {
        el.textContent = config.symbol.trim();
    });

    const pCoffee = document.getElementById('presetCoffeeLabel');
    const pSalary = document.getElementById('presetSalaryLabel');
    const pTransfer = document.getElementById('presetTransferLabel');
    const pDrain = document.getElementById('presetDrainLabel');

    if (pCoffee) pCoffee.textContent = `${formatCurrencyAmount(4.50)} Payment`;
    if (pSalary) pSalary.textContent = `${formatCurrencyAmount(3200.00)} Cash-In`;
    if (pTransfer) pTransfer.textContent = `${formatCurrencyAmount(18000.00)} Volume`;
    if (pDrain) pDrain.textContent = `${formatCurrencyAmount(95000.00)} (03:00 AM)`;
}

// Preset Scenarios for Testing
const PRESETS = {
    coffee: {
        type: 'PAYMENT',
        amount: 4.50,
        oldOrig: 450.00,
        newOrig: 445.50,
        oldDest: 1200.00,
        newDest: 1204.50,
        hour: 9,
        origId: 'C77123490',
        destId: 'M99182371'
    },
    salary: {
        type: 'CASH_IN',
        amount: 3200.00,
        oldOrig: 850.00,
        newOrig: 4050.00,
        oldDest: 20000.00,
        newDest: 16800.00,
        hour: 14,
        origId: 'C44102948',
        destId: 'C99023481'
    },
    transfer: {
        type: 'TRANSFER',
        amount: 18000.00,
        oldOrig: 45000.00,
        newOrig: 27000.00,
        oldDest: 500.00,
        newDest: 18500.00,
        hour: 16,
        origId: 'C55198273',
        destId: 'C66291834'
    },
    drain: {
        type: 'TRANSFER',
        amount: 95000.00,
        oldOrig: 95000.00,
        newOrig: 0.00,
        oldDest: 0.00,
        newDest: 0.00,
        hour: 3,
        origId: 'C88219472',
        destId: 'C19028471'
    }
};

function loadPreset(key) {
    const p = PRESETS[key];
    if (!p) return;
    document.getElementById('formType').value = p.type;
    document.getElementById('formAmount').value = p.amount;
    document.getElementById('formOldOrig').value = p.oldOrig;
    document.getElementById('formNewOrig').value = p.newOrig;
    document.getElementById('formOldDest').value = p.oldDest;
    document.getElementById('formNewDest').value = p.newDest;
    document.getElementById('formHour').value = p.hour;
    document.getElementById('formOrigId').value = p.origId;
    document.getElementById('formDestId').value = p.destId;
}

// Form Submission & Live Prediction
document.getElementById('txnForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = document.getElementById('submitBtn');
    btn.disabled = true;
    btn.innerHTML = `<span>Evaluating Risk...</span>`;

    const payload = {
        type: document.getElementById('formType').value,
        amount: parseFloat(document.getElementById('formAmount').value),
        oldbalance_orig: parseFloat(document.getElementById('formOldOrig').value),
        newbalance_orig: parseFloat(document.getElementById('formNewOrig').value),
        oldbalance_dest: parseFloat(document.getElementById('formOldDest').value),
        newbalance_dest: parseFloat(document.getElementById('formNewDest').value),
        step: parseInt(document.getElementById('formHour').value) || 12,
        name_orig: document.getElementById('formOrigId').value || 'C_USER_01',
        name_dest: document.getElementById('formDestId').value || 'C_USER_02'
    };

    try {
        const response = await fetch('/api/v1/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }

        const data = await response.json();
        displayPredictionResult(data);
        
        fetchAnalytics();
        fetchAuditLog();
    } catch (err) {
        alert(`Evaluation error: ${err.message}`);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<i data-lucide="shield" class="w-4 h-4"></i><span>Evaluate Transaction</span>`;
        lucide.createIcons();
    }
});

function displayPredictionResult(res) {
    const box = document.getElementById('resultBox');
    const txnId = document.getElementById('resultTxnId');
    const badge = document.getElementById('decisionBadge');
    const riskText = document.getElementById('riskPercentageText');
    const bar = document.getElementById('riskBarFill');
    const reasonsList = document.getElementById('reasonsList');

    box.classList.remove('hidden', 'result-glow-approve', 'result-glow-flag', 'result-glow-block');
    badge.className = 'px-4 py-1.5 rounded-full text-xs font-bold tracking-wider border';

    txnId.textContent = res.transaction_id;
    riskText.textContent = res.risk_percentage;
    
    const riskVal = res.risk_score * 100;
    bar.style.width = `${riskVal}%`;

    if (res.decision === 'APPROVE') {
        box.classList.add('result-glow-approve', 'bg-emerald-950/20', 'border-emerald-800/40');
        badge.classList.add('badge-approve');
        badge.textContent = 'APPROVED';
        bar.className = 'h-full rounded-full transition-all duration-500 bg-emerald-500';
    } else if (res.decision === 'FLAG') {
        box.classList.add('result-glow-flag', 'bg-amber-950/20', 'border-amber-800/40');
        badge.classList.add('badge-flag');
        badge.textContent = 'FLAGGED (MFA REQUIRED)';
        bar.className = 'h-full rounded-full transition-all duration-500 bg-amber-500';
    } else {
        box.classList.add('result-glow-block', 'bg-rose-950/20', 'border-rose-800/40');
        badge.classList.add('badge-block');
        badge.textContent = 'BLOCKED';
        bar.className = 'h-full rounded-full transition-all duration-500 bg-rose-500';
    }

    reasonsList.innerHTML = '';
    if (res.flag_reasons && res.flag_reasons.length > 0) {
        res.flag_reasons.forEach(reason => {
            const tag = document.createElement('span');
            tag.className = 'text-[11px] px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700 text-slate-300 flex items-center gap-1.5';
            tag.innerHTML = `<i data-lucide="info" class="w-3 h-3 text-indigo-400"></i> ${reason}`;
            reasonsList.appendChild(tag);
        });
    }
    lucide.createIcons();
}

// Fetch Analytics & Update Charts
async function fetchAnalytics() {
    try {
        const res = await fetch('/api/v1/analytics');
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('kpiTotal').textContent = data.total_transactions.toLocaleString();
        document.getElementById('kpiApproved').textContent = data.total_approved.toLocaleString();
        document.getElementById('kpiFlagged').textContent = data.total_flagged.toLocaleString();
        document.getElementById('kpiBlocked').textContent = data.total_blocked.toLocaleString();
        document.getElementById('kpiFraudRate').textContent = `Fraud Rate: ${data.fraud_rate_percentage}%`;

        if (data.model_metadata) {
            const meta = data.model_metadata;
            document.getElementById('activeModelName').textContent = `Model: ${meta.selected_model}`;
            if (meta.metrics) {
                document.getElementById('metricF1').textContent = meta.metrics.f1_score;
                document.getElementById('metricRecall').textContent = `${(meta.metrics.recall * 100).toFixed(1)}%`;
                document.getElementById('metricPrecision').textContent = `${(meta.metrics.precision * 100).toFixed(1)}%`;
            }
        }

        renderDecisionChart(data.total_approved, data.total_flagged, data.total_blocked);
        renderRiskDistChart(data.risk_distribution);

    } catch (err) {
        console.error('Failed to fetch analytics:', err);
    }
}

function renderDecisionChart(approved, flagged, blocked) {
    const ctx = document.getElementById('decisionChart').getContext('2d');
    const chartData = [approved, flagged, blocked];
    const displayData = (approved + flagged + blocked === 0) ? [1, 0, 0] : chartData;

    if (decisionChartInstance) {
        decisionChartInstance.data.datasets[0].data = displayData;
        decisionChartInstance.update();
        return;
    }

    decisionChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Approve', 'Flag', 'Block'],
            datasets: [{
                data: displayData,
                backgroundColor: ['#10b981', '#f59e0b', '#f43f5e'],
                borderColor: '#111827',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94a3b8', font: { size: 11 } }
                }
            },
            cutout: '70%'
        }
    });
}

function renderRiskDistChart(dist) {
    const ctx = document.getElementById('riskDistributionChart').getContext('2d');
    const counts = Object.values(dist);

    if (riskDistChartInstance) {
        riskDistChartInstance.data.datasets[0].data = counts;
        riskDistChartInstance.update();
        return;
    }

    riskDistChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%'],
            datasets: [{
                label: 'Transactions',
                data: counts,
                backgroundColor: ['#10b981', '#34d399', '#f59e0b', '#fb923c', '#f43f5e'],
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } },
                y: { ticks: { color: '#94a3b8', precision: 0, font: { size: 10 } }, grid: { color: '#1e293b' } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// Transaction Audit Log Table
async function fetchAuditLog() {
    const filter = document.getElementById('filterDecision').value;
    const search = document.getElementById('searchInput').value;
    
    let url = `/api/v1/transactions?limit=25`;
    if (filter && filter !== 'ALL') url += `&decision=${filter}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    try {
        const res = await fetch(url);
        if (!res.ok) return;
        const data = await res.json();
        
        const tbody = document.getElementById('txnTableBody');
        tbody.innerHTML = '';

        if (data.transactions.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-slate-500">No transactions match your criteria.</td></tr>`;
            return;
        }

        data.transactions.forEach(t => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-slate-800/40 transition';

            let badgeClass = 'badge-approve';
            let badgeText = 'APPROVE';
            if (t.decision === 'FLAG') {
                badgeClass = 'badge-flag';
                badgeText = 'FLAG';
            } else if (t.decision === 'BLOCK') {
                badgeClass = 'badge-block';
                badgeText = 'BLOCK';
            }

            const timeStr = t.timestamp ? new Date(t.timestamp).toLocaleTimeString() : 'Just now';

            tr.innerHTML = `
                <td class="py-3 px-4 text-slate-400 font-mono">${timeStr}</td>
                <td class="py-3 px-4 font-mono font-medium text-slate-200">${t.transaction_id}</td>
                <td class="py-3 px-4 font-semibold text-slate-300">${t.type}</td>
                <td class="py-3 px-4 font-mono font-bold text-white">${formatCurrencyAmount(t.amount)}</td>
                <td class="py-3 px-4 text-slate-400 font-mono">${t.name_orig} &rarr; ${t.name_dest}</td>
                <td class="py-3 px-4">
                    <div class="flex items-center space-x-2">
                        <div class="w-16 bg-slate-800 rounded-full h-2 overflow-hidden">
                            <div class="h-full ${t.risk_score > 0.75 ? 'bg-rose-500' : (t.risk_score >= 0.3 ? 'bg-amber-500' : 'bg-emerald-500')}" style="width: ${t.risk_score * 100}%"></div>
                        </div>
                        <span class="font-mono text-slate-300 font-bold">${(t.risk_score * 100).toFixed(1)}%</span>
                    </div>
                </td>
                <td class="py-3 px-4">
                    <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${badgeClass}">${badgeText}</span>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error('Failed to fetch audit log:', err);
    }
}

document.getElementById('filterDecision').addEventListener('change', fetchAuditLog);
document.getElementById('searchInput').addEventListener('input', () => {
    clearTimeout(window.searchTimeout);
    window.searchTimeout = setTimeout(fetchAuditLog, 300);
});

window.addEventListener('DOMContentLoaded', () => {
    updateCurrencyDisplay();
    fetchAnalytics();
    fetchAuditLog();
    lucide.createIcons();
});
