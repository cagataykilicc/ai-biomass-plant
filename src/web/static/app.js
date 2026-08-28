/**
 * AI-Integrated Biomass Conversion Plant - Real-Time Digital Twin Frontend Controller
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initSliders();
  initSimulationHandlers();
  initOptimizationHandlers();
  initDiagnosticsHandlers();
  initMaintenanceHandlers();

  // Run initial simulation on load
  runSimulation();
});

/* Navigation Tab Switching */
function initNavigation() {
  const navBtns = document.querySelectorAll('.nav-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      navBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetTab = btn.getAttribute('data-tab');
      const targetPane = document.getElementById(targetTab);
      if (targetPane) targetPane.classList.add('active');

      // Auto-refresh data when clicking specific tabs
      if (targetTab === 'soft-sensors-tab') runSoftSensors();
      if (targetTab === 'diagnostics-tab') runDiagnostics();
      if (targetTab === 'maintenance-tab') runMaintenance();
    });
  });
}

/* Sliders live display */
function initSliders() {
  const sliderTemp = document.getElementById('slider-temp');
  const dispTemp = document.getElementById('disp-temp');
  if (sliderTemp && dispTemp) {
    sliderTemp.addEventListener('input', (e) => {
      dispTemp.textContent = `${e.target.value} °C`;
    });
  }

  const sliderFeed = document.getElementById('slider-feed');
  const dispFeed = document.getElementById('disp-feed');
  if (sliderFeed && dispFeed) {
    sliderFeed.addEventListener('input', (e) => {
      dispFeed.textContent = `${e.target.value} kg/h`;
    });
  }

  const sliderMoisture = document.getElementById('slider-moisture');
  const dispMoisture = document.getElementById('disp-moisture');
  if (sliderMoisture && dispMoisture) {
    sliderMoisture.addEventListener('input', (e) => {
      dispMoisture.textContent = `${e.target.value} %`;
    });
  }

  const sliderSev = document.getElementById('slider-severity');
  const dispSev = document.getElementById('disp-severity');
  if (sliderSev && dispSev) {
    sliderSev.addEventListener('input', (e) => {
      dispSev.textContent = `${e.target.value} %`;
    });
  }

  const sliderHours = document.getElementById('slider-hours');
  const dispHours = document.getElementById('disp-hours');
  if (sliderHours && dispHours) {
    sliderHours.addEventListener('input', (e) => {
      dispHours.textContent = `${Number(e.target.value).toLocaleString()} Hours`;
    });
  }
}

/* Tab 1: Simulation Logic */
function initSimulationHandlers() {
  const btnRun = document.getElementById('btn-run-sim');
  if (btnRun) {
    btnRun.addEventListener('click', runSimulation);
  }
}

async function runSimulation() {
  const feedstock = document.getElementById('feedstock-select').value;
  const temp = parseFloat(document.getElementById('slider-temp').value);
  const feed = parseFloat(document.getElementById('slider-feed').value);
  const moisture = parseFloat(document.getElementById('slider-moisture').value);
  const yieldMode = document.getElementById('yield-engine-select').value;

  try {
    const res = await fetch('/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        feedstock,
        reactor_temp_c: temp,
        feed_rate_kg_h: feed,
        moisture_pct: moisture,
        yield_mode: yieldMode,
      }),
    });
    const data = await res.json();
    updateFlowsheetUI(data);
  } catch (err) {
    console.error('Simulation request failed:', err);
  }
}

function updateFlowsheetUI(data) {
  // Update Top Bar
  document.getElementById('top-temp').textContent = `${data.operating_conditions.reactor_temp_c.toFixed(1)} °C`;
  document.getElementById('top-feed').textContent = `${data.operating_conditions.feed_rate_kg_h.toFixed(1)} kg/h`;
  document.getElementById('top-tsi').textContent = `${data.energy_and_heat.tsi_pct.toFixed(1)} %`;
  
  const statusBadge = document.getElementById('top-energy-status');
  if (data.energy_and_heat.is_self_sufficient) {
    statusBadge.textContent = 'AUTONOMOUS';
    statusBadge.className = 'badge badge-success';
  } else {
    statusBadge.textContent = 'DEFICIT';
    statusBadge.className = 'badge badge-danger';
  }

  // Update SVG nodes
  document.getElementById('fs-reactor-temp').textContent = `${data.operating_conditions.reactor_temp_c.toFixed(0)} °C`;
  document.getElementById('fs-biooil-rate').textContent = `${data.product_rates_kg_h.bio_oil.toFixed(1)} kg/h`;
  document.getElementById('fs-char-rate').textContent = `${data.product_rates_kg_h.biochar.toFixed(1)} kg/h`;
  document.getElementById('fs-burner-tsi').textContent = `TSI ${data.energy_and_heat.tsi_pct.toFixed(0)}%`;

  // Update Metrics Row
  document.getElementById('card-biooil-rate').textContent = `${data.product_rates_kg_h.bio_oil.toFixed(1)} kg/h`;
  document.getElementById('card-biooil-pct').textContent = `${data.yields_dry.bio_oil_yield_pct.toFixed(1)} wt% dry`;
  document.getElementById('card-biochar-rate').textContent = `${data.product_rates_kg_h.biochar.toFixed(1)} kg/h`;
  document.getElementById('card-biochar-pct').textContent = `${data.yields_dry.biochar_yield_pct.toFixed(1)} wt% dry`;
  document.getElementById('card-syngas-rate').textContent = `${data.product_rates_kg_h.syngas.toFixed(1)} kg/h`;
  document.getElementById('card-syngas-pct').textContent = `${data.yields_dry.syngas_yield_pct.toFixed(1)} wt% dry`;

  const surplusEl = document.getElementById('card-surplus-heat');
  if (data.energy_and_heat.net_surplus_kw >= 0) {
    surplusEl.textContent = `+${data.energy_and_heat.net_surplus_kw.toFixed(1)} kW`;
    surplusEl.className = 'm-val text-green';
  } else {
    surplusEl.textContent = `${data.energy_and_heat.net_surplus_kw.toFixed(1)} kW`;
    surplusEl.className = 'm-val text-danger';
  }
}

/* Tab 2: Soft Sensors */
async function runSoftSensors() {
  const feedstock = document.getElementById('feedstock-select').value;
  const temp = parseFloat(document.getElementById('slider-temp').value);
  const feed = parseFloat(document.getElementById('slider-feed').value);

  const container = document.getElementById('soft-sensors-container');
  container.innerHTML = '<div class="glass-card">Loading real-time soft sensor telemetry...</div>';

  try {
    const res = await fetch('/api/soft-sensors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedstock, reactor_temp_c: temp, feed_rate_kg_h: feed }),
    });
    const data = await res.json();
    renderSoftSensors(data.soft_sensors);
  } catch (err) {
    container.innerHTML = `<div class="glass-card text-danger">Error: ${err.message}</div>`;
  }
}

function renderSoftSensors(sensors) {
  const container = document.getElementById('soft-sensors-container');
  container.innerHTML = '';

  for (const [tag, s] of Object.entries(sensors)) {
    const card = document.createElement('div');
    card.className = 'sensor-card';
    card.innerHTML = `
      <div class="sensor-header">
        <span class="sensor-tag">${tag}</span>
        <span class="badge ${s.status === 'NORMAL' ? 'badge-success' : 'badge-warning'}">${s.status}</span>
      </div>
      <h4>${s.name}</h4>
      <div class="sensor-val">${s.point_estimate.toFixed(2)} <span style="font-size:0.9rem; font-weight:400; color:var(--text-muted);">${s.unit}</span></div>
      <div class="sensor-ci">95% CI: [${s.lower_95_ci.toFixed(2)} - ${s.upper_95_ci.toFixed(2)}]</div>
    `;
    container.appendChild(card);
  }
}

/* Tab 3: Optimization & Pareto */
let paretoData = [];
function initOptimizationHandlers() {
  const btnOpt = document.getElementById('btn-run-opt');
  if (btnOpt) {
    btnOpt.addEventListener('click', runOptimization);
  }

  const pBtns = document.querySelectorAll('.profile-buttons button');
  pBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      pBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      drawParetoChart();
    });
  });
}

async function runOptimization() {
  const feedstock = document.getElementById('feedstock-select').value;
  try {
    const res = await fetch('/api/optimize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedstock, mode: 'pareto' }),
    });
    const data = await res.json();
    paretoData = data.frontier || [];
    drawParetoChart();
    renderBestSolution(data.top_solution, data.topsis_score);
  } catch (err) {
    console.error('Optimization failed:', err);
  }
}

function drawParetoChart() {
  const canvas = document.getElementById('paretoCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Background grid
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  ctx.lineWidth = 1;
  for (let x = 40; x < canvas.width; x += 50) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height - 30); ctx.stroke();
  }
  for (let y = 20; y < canvas.height - 30; y += 40) {
    ctx.beginPath(); ctx.moveTo(40, y); ctx.lineTo(canvas.width, y); ctx.stroke();
  }

  // Draw Axes
  ctx.strokeStyle = '#64748b';
  ctx.beginPath();
  ctx.moveTo(40, 20);
  ctx.lineTo(40, canvas.height - 30);
  ctx.lineTo(canvas.width - 20, canvas.height - 30);
  ctx.stroke();

  // Axis Labels
  ctx.fillStyle = '#94a3b8';
  ctx.font = '11px Inter';
  ctx.fillText('Biochar Yield (wt%)', canvas.width / 2 - 40, canvas.height - 10);
  ctx.save();
  ctx.translate(15, canvas.height / 2 + 30);
  ctx.rotate(-Math.PI / 2);
  ctx.fillText('Bio-Oil Yield (wt%)', 0, 0);
  ctx.restore();

  if (paretoData.length === 0) return;

  // Plot Points
  paretoData.forEach((pt, idx) => {
    const x = 40 + (pt.char_yield_dry_pct - 15) * (canvas.width - 70) / 30;
    const y = (canvas.height - 30) - (pt.liquid_yield_dry_pct - 30) * (canvas.height - 60) / 35;

    ctx.fillStyle = idx === 0 ? '#00ff88' : '#00f0ff';
    ctx.shadowColor = idx === 0 ? '#00ff88' : '#00f0ff';
    ctx.shadowBlur = idx === 0 ? 12 : 6;

    ctx.beginPath();
    ctx.arc(x, y, idx === 0 ? 7 : 4.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
  });
}

function renderBestSolution(sol, topsis) {
  const container = document.getElementById('opt-best-solution');
  if (!sol || !container) return;

  container.innerHTML = `
    <div style="margin-top:16px; padding:12px; background:rgba(0,255,136,0.05); border:1px solid rgba(0,255,136,0.2); border-radius:8px;">
      <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
        <span style="font-weight:700; color:var(--accent-green);">TOPSIS Champion Setpoint</span>
        <span class="badge badge-success">Score: ${(topsis * 100).toFixed(1)}%</span>
      </div>
      <div style="font-family:var(--font-mono); font-size:0.85rem; display:grid; grid-template-columns:1fr 1fr; gap:6px;">
        <div>Temp: <strong>${sol.reactor_temp_c.toFixed(1)} °C</strong></div>
        <div>Feed: <strong>${sol.feed_rate_kg_h.toFixed(1)} kg/h</strong></div>
        <div>Bio-Oil: <strong>${sol.liquid_yield_dry_pct.toFixed(1)} wt%</strong></div>
        <div>Biochar: <strong>${sol.char_yield_dry_pct.toFixed(1)} wt%</strong></div>
        <div>Profit: <strong>$${sol.profit_margin_usd_h.toFixed(2)}/h</strong></div>
        <div>TSI: <strong>${sol.tsi_pct.toFixed(1)} %</strong></div>
      </div>
    </div>
  `;
}

/* Tab 4: Diagnostics */
function initDiagnosticsHandlers() {
  const btnDiag = document.getElementById('btn-run-diag');
  if (btnDiag) {
    btnDiag.addEventListener('click', runDiagnostics);
  }
}

async function runDiagnostics() {
  const faultType = document.getElementById('fault-select').value;
  const severity = parseFloat(document.getElementById('slider-severity').value) / 100.0;
  const container = document.getElementById('diag-results-container');
  container.innerHTML = '<div>Evaluating tri-layer anomaly detection models...</div>';

  try {
    const res = await fetch('/api/diagnostics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fault_type: faultType, severity }),
    });
    const data = await res.json();
    renderDiagnostics(data);
  } catch (err) {
    container.innerHTML = `<div class="text-danger">Diagnostics error: ${err.message}</div>`;
  }
}

function renderDiagnostics(data) {
  const container = document.getElementById('diag-results-container');
  const anom = data.anomaly_detection;
  const diag = data.fault_diagnosis;
  const alarm = data.alarm;

  const isAlarm = alarm.priority !== 'NORMAL';

  container.innerHTML = `
    <div class="card-header">
      <h3>Diagnostic Assessment: ${diag.predicted_fault}</h3>
      <span class="badge ${isAlarm ? (alarm.priority === 'CRITICAL_EMERGENCY' ? 'badge-danger' : 'badge-warning') : 'badge-success'}">${alarm.priority}</span>
    </div>
    
    <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; margin-top:8px;">
      <div class="metric-item">
        <span class="m-title">Anomaly Score</span>
        <span class="m-val ${anom.is_anomaly ? 'text-danger' : 'text-green'}">${(anom.overall_anomaly_score * 100).toFixed(1)}%</span>
        <span class="m-sub">${anom.is_anomaly ? 'ALERT TRIGGERED' : 'NORMAL'}</span>
      </div>
      <div class="metric-item">
        <span class="m-title">PCA Q-Statistic (SPE)</span>
        <span class="m-val">${anom.pca_q_statistic.toFixed(2)}</span>
        <span class="m-sub">Limit: ${anom.pca_q_limit_99.toFixed(2)}</span>
      </div>
      <div class="metric-item">
        <span class="m-title">Hotelling's T²</span>
        <span class="m-val">${anom.pca_t2_statistic.toFixed(2)}</span>
        <span class="m-sub">Limit: ${anom.pca_t2_limit_99.toFixed(2)}</span>
      </div>
    </div>

    <div class="work-order-card ${alarm.priority === 'CRITICAL_EMERGENCY' ? 'critical' : ''}" style="margin-top:12px;">
      <div style="font-weight:700; color:var(--text-main);">${alarm.headline_message}</div>
      <div style="font-size:0.85rem; color:var(--text-muted);">Affected Equipment: <strong>${alarm.affected_equipment}</strong> | Standard: <em>${alarm.safety_standard_reference}</em></div>
      <div style="font-size:0.85rem; margin-top:4px;"><strong>Operator Action:</strong> ${alarm.recommended_operator_action}</div>
      <div style="font-size:0.85rem; color:var(--accent-crimson); margin-top:4px;"><strong>Automated Interlock:</strong> ${alarm.automated_interlock_action}</div>
    </div>
  `;
}

/* Tab 5: Predictive Maintenance */
function initMaintenanceHandlers() {
  const btnMaint = document.getElementById('btn-run-maint');
  if (btnMaint) {
    btnMaint.addEventListener('click', runMaintenance);
  }
}

async function runMaintenance() {
  const hours = parseFloat(document.getElementById('slider-hours').value);
  const container = document.getElementById('maint-results-container');
  container.innerHTML = '<div>Evaluating fleet degradation trajectories...</div>';

  try {
    const res = await fetch('/api/maintenance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ operating_hours: hours }),
    });
    const data = await res.json();
    renderMaintenance(data);
  } catch (err) {
    container.innerHTML = `<div class="text-danger">Maintenance evaluation error: ${err.message}</div>`;
  }
}

function renderMaintenance(data) {
  const container = document.getElementById('maint-results-container');
  const fleet = data.fleet_summary;
  const orders = data.work_orders;

  let html = `
    <div class="card-header">
      <h3>Plant Reliability Status (${fleet.current_operating_hours.toLocaleString()} Hours)</h3>
      <span class="badge badge-cyan">Bottleneck: ${fleet.most_critical_asset_id}</span>
    </div>
    
    <div style="display:grid; grid-template-columns:repeat(2, 1fr); gap:12px; margin-top:8px;">
  `;

  for (const [aId, a] of Object.entries(fleet.assets)) {
    const deg = a.degradation_state;
    html += `
      <div class="metric-item">
        <div style="display:flex; justify-content:space-between;">
          <span class="m-title">${a.asset_name}</span>
          <span class="badge ${a.maintenance_urgency === 'HEALTHY' ? 'badge-success' : 'badge-warning'}">${a.maintenance_urgency}</span>
        </div>
        <span class="m-val">${a.current_health_index_pct.toFixed(1)}% Health</span>
        <span class="m-sub">RUL: <strong>${a.estimated_rul_hours.toLocaleString()} h</strong> [${a.rul_95_ci_lower_hours.toLocaleString()} - ${a.rul_95_ci_upper_hours.toLocaleString()}]</span>
      </div>
    `;
  }

  html += `</div><h4 style="margin-top:16px; margin-bottom:8px;">Prescriptive Work Orders (${orders.length})</h4>`;

  if (orders.length === 0) {
    html += '<p style="color:var(--text-muted); font-size:0.85rem;">All plant assets operating in HEALTHY nominal window.</p>';
  } else {
    orders.forEach(wo => {
      html += `
        <div class="work-order-card ${wo.urgency === 'CRITICAL_REPLACEMENT' ? 'critical' : ''}">
          <div style="display:flex; justify-content:space-between;">
            <strong>${wo.work_order_id}: ${wo.asset_name}</strong>
            <span class="badge badge-warning">${wo.urgency}</span>
          </div>
          <div style="font-size:0.85rem;">Scope: ${wo.scope_of_work}</div>
          <div style="font-size:0.8rem; color:var(--primary-cyan);">Labor: ${wo.estimated_labor_hours}h | Parts BOM: $${wo.total_parts_cost_usd.toLocaleString()}</div>
          <div style="font-size:0.8rem; color:var(--accent-amber);">LOTO: ${wo.safety_loto_protocol}</div>
        </div>
      `;
    });
  }

  container.innerHTML = html;
}
