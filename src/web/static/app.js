/**
 * AI-Integrated Biomass Conversion Plant - Real-Time Digital Twin Frontend Controller (V2.0)
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initSliders();
  initSimulationHandlers();
  initOptimizationHandlers();
  initDiagnosticsHandlers();
  initMaintenanceHandlers();
  initControlHandlers();
  initEconomicsHandlers();
  initAutopilotHandlers();
  initIoTHandlers();
  initFleetHandlers();
  initV3Handlers();
  initLanguageSwitcher();

  // Run initial simulation on load
  runSimulation();
});

function initLanguageSwitcher() {
  const langBtns = document.querySelectorAll('.btn-lang');
  langBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const lang = btn.getAttribute('data-lang');
      if (typeof setLanguage === 'function') {
        setLanguage(lang);
      }
    });
  });

  if (typeof setLanguage === 'function' && typeof getCurrentLanguage === 'function') {
    setLanguage(getCurrentLanguage());
  }
}

function getApiKey() {
  const urlParams = new URLSearchParams(window.location.search);
  return (
    urlParams.get('api_key') ||
    localStorage.getItem('bioplant_api_key') ||
    window.__BIOPLANT_API_KEY__ ||
    'bioplant-default-dev-key'
  );
}

function apiHeaders(extraHeaders = {}) {
  return {
    'Content-Type': 'application/json',
    'X-API-Key': getApiKey(),
    ...extraHeaders,
  };
}

const tabLoaded = {};

/* Navigation Tab Switching (Optimized & Instant) */
function initNavigation() {
  const navBtns = document.querySelectorAll('.nav-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetTab = btn.getAttribute('data-tab');
      if (!targetTab) return;

      // 1. Instant DOM Switching
      navBtns.forEach(b => b.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const targetPane = document.getElementById(targetTab);
      if (targetPane) targetPane.classList.add('active');

      // 2. Lazy Load Data on first visit only (Non-blocking)
      if (!tabLoaded[targetTab]) {
        tabLoaded[targetTab] = true;
        setTimeout(() => {
          if (targetTab === 'soft-sensors-tab') runSoftSensors();
          else if (targetTab === 'diagnostics-tab') runDiagnostics();
          else if (targetTab === 'maintenance-tab') runMaintenance();
          else if (targetTab === 'control-tab') runControlSimulation();
          else if (targetTab === 'economics-tab') runEconomics();
          else if (targetTab === 'autopilot-tab') stepAutopilot();
          else if (targetTab === 'iot-tab') pollModbusRegisters();
          else if (targetTab === 'fleet-tab') loadFleetStatus();
          else if (targetTab === 'spatial-tab') initThreeScene();
        }, 10);
      }
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

  const sliderCtrlSp = document.getElementById('slider-ctrl-sp');
  const dispCtrlSp = document.getElementById('disp-ctrl-sp');
  if (sliderCtrlSp && dispCtrlSp) {
    sliderCtrlSp.addEventListener('input', (e) => {
      dispCtrlSp.textContent = `${e.target.value} °C`;
    });
  }

  const sliderCtrlMoist = document.getElementById('slider-ctrl-moist');
  const dispCtrlMoist = document.getElementById('disp-ctrl-moist');
  if (sliderCtrlMoist && dispCtrlMoist) {
    sliderCtrlMoist.addEventListener('input', (e) => {
      dispCtrlMoist.textContent = `${e.target.value} wt%`;
    });
  }

  const sliderApMoist = document.getElementById('slider-ap-moist');
  const dispApMoist = document.getElementById('disp-ap-moist');
  if (sliderApMoist && dispApMoist) {
    sliderApMoist.addEventListener('input', (e) => {
      dispApMoist.textContent = `${e.target.value} %`;
    });
  }

  const sliderCorc = document.getElementById('slider-corc-spot');
  const dispCorc = document.getElementById('disp-corc-spot');
  if (sliderCorc && dispCorc) {
    sliderCorc.addEventListener('input', (e) => {
      dispCorc.textContent = `$${parseFloat(e.target.value).toFixed(1)} / t CO2`;
    });
  }

  const sliderOil = document.getElementById('slider-oil-spot');
  const dispOil = document.getElementById('disp-oil-spot');
  if (sliderOil && dispOil) {
    sliderOil.addEventListener('input', (e) => {
      dispOil.textContent = `$${parseFloat(e.target.value).toFixed(2)} / kg`;
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
      headers: apiHeaders(),
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
      headers: apiHeaders(),
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
      headers: apiHeaders(),
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

  const setpoints = sol.setpoints || {};
  const objs = sol.objectives || {};

  container.innerHTML = `
    <div style="margin-top:16px; padding:12px; background:rgba(0,255,136,0.05); border:1px solid rgba(0,255,136,0.2); border-radius:8px;">
      <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
        <span style="font-weight:700; color:var(--accent-green);">TOPSIS Champion Setpoint</span>
        <span class="badge badge-success">Score: ${((topsis || 0.85) * 100).toFixed(1)}%</span>
      </div>
      <div style="font-family:var(--font-mono); font-size:0.85rem; display:grid; grid-template-columns:1fr 1fr; gap:6px;">
        <div>Temp: <strong>${(setpoints.reactor_temp_c || 500).toFixed(1)} °C</strong></div>
        <div>Feed: <strong>${(setpoints.feed_rate_kg_h || 100).toFixed(1)} kg/h</strong></div>
        <div>Bio-Oil: <strong>${(objs.bio_oil_yield_dry_pct || 48).toFixed(1)} wt%</strong></div>
        <div>Biochar: <strong>${(objs.biochar_yield_dry_pct || 27).toFixed(1)} wt%</strong></div>
        <div>Profit: <strong>$${(objs.gross_margin_usd_h || 18).toFixed(2)}/h</strong></div>
        <div>TSI: <strong>${sol.is_self_sufficient ? '>= 100%' : '< 100%'}</strong></div>
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
      headers: apiHeaders(),
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
      headers: apiHeaders(),
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

/* Tab 6: Dynamic Process Control & MPC */
function initControlHandlers() {
  const btnCtrl = document.getElementById('btn-run-control');
  if (btnCtrl) {
    btnCtrl.addEventListener('click', runControlSimulation);
  }
}

async function runControlSimulation() {
  const ctrlType = document.getElementById('ctrl-type-select').value;
  const setpoint = parseFloat(document.getElementById('slider-ctrl-sp').value);
  const moist = parseFloat(document.getElementById('slider-ctrl-moist').value);

  try {
    const res = await fetch('/api/control', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({
        controller: ctrlType,
        setpoint: setpoint,
        moisture_disturb: moist,
      }),
    });
    const data = await res.json();
    renderControlResults(data);
  } catch (err) {
    console.error('Control simulation failed:', err);
  }
}

function renderControlResults(data) {
  const metrics = data.metrics;
  const container = document.getElementById('control-metrics-box');
  if (container) {
    container.innerHTML = `
      <div style="margin-top:16px; padding:12px; background:rgba(0,240,255,0.05); border:1px solid rgba(0,240,255,0.2); border-radius:8px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <span style="font-weight:700; color:var(--primary-cyan);">${metrics.controller_name} Performance KPIs</span>
          <span class="badge badge-cyan">Settling: ${metrics.settling_time_sec.toFixed(0)}s</span>
        </div>
        <div style="font-family:var(--font-mono); font-size:0.85rem; display:grid; grid-template-columns:1fr 1fr; gap:6px;">
          <div>IAE: <strong>${metrics.iae.toLocaleString()} °C·s</strong></div>
          <div>ITAE: <strong>${metrics.itae.toLocaleString()}</strong></div>
          <div>Overshoot: <strong>${metrics.peak_overshoot_pct.toFixed(2)} %</strong></div>
          <div>Offset Error: <strong>${metrics.steady_state_error_c.toFixed(2)} °C</strong></div>
        </div>
      </div>
    `;
  }

  drawControlChart(data.trajectory);
}

function drawControlChart(trajectory) {
  const canvas = document.getElementById('controlCanvas');
  if (!canvas || !trajectory || trajectory.length === 0) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const padding = 45;
  const w = canvas.width - padding * 2;
  const h = canvas.height - padding * 2;

  // Grid
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  ctx.lineWidth = 1;
  for (let y = padding; y <= canvas.height - padding; y += 40) {
    ctx.beginPath(); ctx.moveTo(padding, y); ctx.lineTo(canvas.width - padding, y); ctx.stroke();
  }

  // Draw Setpoint Line (500°C -> 520°C at 10 min)
  ctx.strokeStyle = 'rgba(255, 184, 0, 0.6)';
  ctx.setLineDash([4, 4]);
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  const sp1Y = canvas.height - padding - (500.0 - 450.0) * h / 150.0;
  const sp2Y = canvas.height - padding - (520.0 - 450.0) * h / 150.0;
  const stepX = padding + (10.0 / 60.0) * w;
  ctx.moveTo(padding, sp1Y);
  ctx.lineTo(stepX, sp1Y);
  ctx.lineTo(stepX, sp2Y);
  ctx.lineTo(canvas.width - padding, sp2Y);
  ctx.stroke();
  ctx.setLineDash([]);

  // Draw Actual Reactor Temp Curve
  ctx.strokeStyle = '#00f0ff';
  ctx.lineWidth = 2.5;
  ctx.shadowColor = '#00f0ff';
  ctx.shadowBlur = 8;
  ctx.beginPath();

  trajectory.forEach((pt, i) => {
    const x = padding + (pt.time_min / 60.0) * w;
    const y = canvas.height - padding - (pt.reactor_temp_c - 450.0) * h / 150.0;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.shadowBlur = 0;

  // Axes and text
  ctx.strokeStyle = '#64748b';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding, padding);
  ctx.lineTo(padding, canvas.height - padding);
  ctx.lineTo(canvas.width - padding, canvas.height - padding);
  ctx.stroke();

  ctx.fillStyle = '#94a3b8';
  ctx.font = '11px Inter';
  ctx.fillText('Time (0 - 60 Minutes)', canvas.width / 2 - 40, canvas.height - 10);
  ctx.fillText('450°C', 10, canvas.height - padding);
  ctx.fillText('600°C', 10, padding + 10);
}

/* Tab 7: Techno-Economic & LCA Carbon Accounting */
function initEconomicsHandlers() {
  const btnEcon = document.getElementById('btn-run-economics');
  if (btnEcon) {
    btnEcon.addEventListener('click', runEconomics);
  }
}

async function runEconomics() {
  const feedstock = document.getElementById('feedstock-select').value;
  const temp = parseFloat(document.getElementById('slider-temp').value);
  const feed = parseFloat(document.getElementById('slider-feed').value);
  const oilPrice = parseFloat(document.getElementById('econ-oil-price').value) || 0.65;
  const charPrice = parseFloat(document.getElementById('econ-char-price').value) || 0.45;
  const corcPrice = parseFloat(document.getElementById('econ-corc-price').value) || 65.0;

  const container = document.getElementById('econ-results-container');
  container.innerHTML = '<div>Evaluating 20-year Discounted Cash Flow and Scope 1-2-3 emissions...</div>';

  try {
    const res = await fetch('/api/economics', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({
        feedstock,
        reactor_temp_c: temp,
        feed_rate_kg_h: feed,
        oil_price: oilPrice,
        char_price: charPrice,
        corc_price: corcPrice,
      }),
    });
    const data = await res.json();
    renderEconomicsUI(data);
  } catch (err) {
    container.innerHTML = `<div class="text-danger">Economics error: ${err.message}</div>`;
  }
}

function renderEconomicsUI(data) {
  const container = document.getElementById('econ-results-container');
  if (!data || data.error || !data.life_cycle_assessment_lca) {
    container.innerHTML = `<div class="text-danger" style="padding:16px;">Economics Evaluation Error: ${data?.error || 'Invalid response received from server.'}</div>`;
    return;
  }

  const cap = data.capital_expenditure_capex;
  const op = data.operational_expenditure_opex;
  const fin = data.financial_viability_dcf;
  const lca = data.life_cycle_assessment_lca;
  const seq = lca.sequestration;

  container.innerHTML = `
    <div class="card-header">
      <h3>Financial Valuation & Carbon Removal Overview</h3>
      <span class="badge ${fin.is_financially_viable ? 'badge-success' : 'badge-warning'}">${fin.is_financially_viable ? 'COMMERCIALLY VIABLE' : 'DEFICIT'}</span>
    </div>

    <!-- Financial Key Metrics Grid -->
    <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; margin-top:8px;">
      <div class="metric-item">
        <span class="m-title">Net Present Value (NPV @ 10%)</span>
        <span class="m-val text-green">$${fin.net_present_value_usd.toLocaleString()}</span>
        <span class="m-sub">20-Year Project Life</span>
      </div>
      <div class="metric-item">
        <span class="m-title">Internal Rate of Return (IRR)</span>
        <span class="m-val text-cyan">${fin.internal_rate_of_return_pct.toFixed(1)}%</span>
        <span class="m-sub">Discounted Payback: <strong>${fin.discounted_payback_years.toFixed(1)} yrs</strong></span>
      </div>
      <div class="metric-item">
        <span class="m-title">Levelized Cost of Bio-Oil (LCOB)</span>
        <span class="m-val">$${fin.levelized_cost_bio_oil_usd_kg.toFixed(3)}/kg</span>
        <span class="m-sub">$${fin.levelized_cost_bio_oil_usd_mj.toFixed(4)}/MJ</span>
      </div>
    </div>

    <!-- Capital vs Operating Cost Summary -->
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:12px;">
      <div class="work-order-card">
        <div style="font-weight:700; color:var(--primary-cyan); margin-bottom:4px;">Capital Investment (Guthrie TCI)</div>
        <div style="font-size:0.85rem;">Total Purchased Equipment: <strong>$${cap.purchased_equipment_cost_usd.toLocaleString()}</strong></div>
        <div style="font-size:0.85rem;">Fixed Capital Investment (FCI): <strong>$${cap.fixed_capital_investment_usd.toLocaleString()}</strong></div>
        <div style="font-size:0.85rem; color:var(--text-main);"><strong>Total Capital Investment (TCI): $${cap.total_capital_investment_usd.toLocaleString()}</strong></div>
      </div>
      <div class="work-order-card">
        <div style="font-weight:700; color:var(--accent-amber); margin-bottom:4px;">Annual Operating Cost (OPEX)</div>
        <div style="font-size:0.85rem;">Feedstock Supply: <strong>$${op.feedstock_cost_usd_yr.toLocaleString()}/yr</strong></div>
        <div style="font-size:0.85rem;">Maintenance & Insurance: <strong>$${(op.maintenance_and_repairs_usd_yr + op.insurance_and_taxes_usd_yr).toLocaleString()}/yr</strong></div>
        <div style="font-size:0.85rem; color:var(--text-main);"><strong>Total OPEX: $${op.total_opex_usd_yr.toLocaleString()}/yr ($${op.unit_opex_usd_per_tonne_feed.toFixed(1)}/t)</strong></div>
      </div>
    </div>

    <!-- Carbon Intensity & Removal Profile -->
    <div class="work-order-card" style="margin-top:12px; border-color:rgba(0,255,136,0.3);">
      <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
        <span style="font-weight:700; color:var(--accent-green);">ISO 14040/14044 Carbon Balance</span>
        <span class="badge ${lca.is_carbon_negative ? 'badge-success' : 'badge-danger'}">${lca.is_carbon_negative ? 'NET CARBON NEGATIVE' : 'NET EMITTER'}</span>
      </div>
      <div style="font-size:0.85rem; display:grid; grid-template-columns:repeat(2, 1fr); gap:6px;">
        <div>Gross Scope 1+2+3 Emissions: <strong>${lca.scope_emissions.total_gross_emissions_co2e_kg_yr.toLocaleString()} kg/yr</strong></div>
        <div>Permanent Biochar Sequestration: <strong>-${seq.co2_sequestered_kg_yr.toLocaleString()} kg CO2/yr</strong></div>
        <div>Certified CORC Revenue: <strong>+$${seq.annual_carbon_credit_revenue_usd.toLocaleString()}/yr</strong></div>
        <div>Net Carbon Intensity: <strong>${lca.carbon_intensity_g_co2e_per_mj_bio_oil.toFixed(1)} g CO2eq/MJ</strong></div>
      </div>
    </div>
  `;
}

/* Tab 8: Autonomous Autopilot Cockpit */
let autopilotInterval = null;
function initAutopilotHandlers() {
  const btnToggle = document.getElementById('btn-toggle-ap');
  if (btnToggle) {
    btnToggle.addEventListener('click', toggleAutopilot);
  }

  const btnMission = document.getElementById('btn-run-full-mission');
  if (btnMission) {
    btnMission.addEventListener('click', runFullMission);
  }
}

function toggleAutopilot() {
  const btn = document.getElementById('btn-toggle-ap');
  const text = document.getElementById('ap-toggle-text');
  const statusBadge = document.getElementById('ap-loop-status');

  if (autopilotInterval) {
    clearInterval(autopilotInterval);
    autopilotInterval = null;
    btn.className = 'btn btn-primary';
    text.textContent = 'ENGAGE AUTONOMOUS AUTOPILOT';
    statusBadge.textContent = 'AUTOPILOT STANDBY';
    statusBadge.className = 'badge badge-warning';
  } else {
    btn.className = 'btn';
    btn.style.background = 'var(--accent-crimson)';
    text.textContent = 'DISENGAGE AUTOPILOT';
    statusBadge.textContent = 'AUTOPILOT ENGAGED (2.0s LOOP)';
    statusBadge.className = 'badge badge-success';

    // Step immediately and then every 2 seconds
    stepAutopilot();
    autopilotInterval = setInterval(stepAutopilot, 2000);
  }
}

async function stepAutopilot(reset = false) {
  const moist = parseFloat(document.getElementById('slider-ap-moist').value);
  const fault = document.getElementById('ap-fault-select').value;

  try {
    const res = await fetch('/api/autopilot/step', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({ moisture: moist, fault: fault, reset: reset }),
    });
    const data = await res.json();
    renderAutopilotStep(data);
  } catch (err) {
    console.error('Autopilot step failed:', err);
  }
}

function renderAutopilotStep(data) {
  const st = data.plant_state;
  const cmd = data.command;

  // Update Flight Director Badges
  const fsmBadge = document.getElementById('ap-fsm-badge');
  if (fsmBadge) {
    fsmBadge.textContent = cmd.fsm_state;
    if (cmd.fsm_state === 'STARTUP_PREHEAT') fsmBadge.className = 'badge badge-cyan';
    else if (cmd.fsm_state === 'AUTONOMOUS_CRUISE') fsmBadge.className = 'badge badge-success';
    else if (cmd.fsm_state === 'DISTURBANCE_ADAPTATION') fsmBadge.className = 'badge badge-warning';
    else if (cmd.fsm_state === 'FAULT_MITIGATION') fsmBadge.className = 'badge badge-warning';
    else fsmBadge.className = 'badge badge-danger';
  }

  // Update Gauges
  document.getElementById('ap-pv-temp').textContent = `${st.reactor_temp_c.toFixed(1)} °C`;
  document.getElementById('ap-sp-temp').textContent = `${cmd.target_temp_c.toFixed(1)} °C`;
  document.getElementById('ap-feed-rate').textContent = `${st.feed_rate_kg_h.toFixed(1)} kg/h`;
  document.getElementById('ap-burner-duty').textContent = `${cmd.burner_duty_pct.toFixed(0)}% Firing`;
  document.getElementById('ap-tsi').textContent = `${st.tsi_pct.toFixed(1)} %`;

  // Action summary & event log
  document.getElementById('ap-action-headline').textContent = cmd.action_summary;
  const events = data.active_events || [];
  if (events.length > 0) {
    const latest = events[events.length - 1];
    document.getElementById('ap-event-log').textContent = `[${latest.time_min.toFixed(1)}m] ${latest.action} | Alarm: ${latest.alarm}`;
  }
}

async function runFullMission() {
  const btn = document.getElementById('btn-run-full-mission');
  btn.disabled = true;
  btn.innerHTML = '<span>Executing 4-Hour Autonomous Stress Test...</span>';

  try {
    const res = await fetch('/api/autopilot/mission', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({ dt: 2.0 }),
    });
    const data = await res.json();
    alert(`Autonomous Mission Completed: ${data.overall_status} across ${data.phases_executed_count} flight phases! Log saved.`);
    stepAutopilot();
  } catch (err) {
    alert(`Mission failed: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span>Execute 4-Hour Stress Test Mission</span>';
  }
}

/* =========================================================================
 * Tab 9: Industrial IoT, Modbus & HIL Controller
 * ========================================================================= */
function initIoTHandlers() {
  const btnPoll = document.getElementById('btn-modbus-poll');
  if (btnPoll) btnPoll.addEventListener('click', pollModbusRegisters);

  const btnHilStep = document.getElementById('btn-hil-step');
  if (btnHilStep) btnHilStep.addEventListener('click', stepHILSimulator);

  const btnOpen = document.getElementById('btn-hil-fault-open');
  if (btnOpen) btnOpen.addEventListener('click', () => injectHILFault('AI_1', 'loop_open'));

  const btnShort = document.getElementById('btn-hil-fault-short');
  if (btnShort) btnShort.addEventListener('click', () => injectHILFault('AI_1', 'loop_short'));

  const btnClear = document.getElementById('btn-hil-fault-clear');
  if (btnClear) btnClear.addEventListener('click', () => injectHILFault('AI_1', 'clear'));
}

async function pollModbusRegisters() {
  try {
    const res = await fetch('/api/iot/modbus/read', {
      headers: apiHeaders(),
    });
    const data = await res.json();
    renderModbusTable(data);
    stepHILSimulator();
  } catch (err) {
    console.error('Failed to poll Modbus registers:', err);
  }
}

function renderModbusTable(data) {
  const tbody = document.getElementById('modbus-reg-tbody');
  if (!tbody) return;

  const irs = data.input_registers_30000 || {};
  const hrs = data.holding_registers_40000 || {};

  let rowsHtml = '';
  // Render Input Registers
  for (const [addr, info] of Object.entries(irs)) {
    rowsHtml += `
      <tr>
        <td style="padding:5px 10px; font-family:var(--font-mono); color:var(--primary-cyan);">${addr}</td>
        <td style="padding:5px 10px;">${info.name}</td>
        <td style="padding:5px 10px; font-family:var(--font-mono);">${info.raw}</td>
        <td style="padding:5px 10px; font-weight:600;">${typeof info.scaled === 'number' ? info.scaled.toFixed(1) : info.scaled} ${info.unit}</td>
        <td style="padding:5px 10px;"><span class="badge badge-cyan" style="font-size:0.7rem;">Input Reg (RO)</span></td>
      </tr>
    `;
  }

  // Render Holding Registers
  for (const [addr, info] of Object.entries(hrs)) {
    rowsHtml += `
      <tr>
        <td style="padding:5px 10px; font-family:var(--font-mono); color:var(--accent-amber);">${addr}</td>
        <td style="padding:5px 10px;">${info.name}</td>
        <td style="padding:5px 10px; font-family:var(--font-mono);">${info.raw}</td>
        <td style="padding:5px 10px; font-weight:600;">${typeof info.scaled === 'number' ? info.scaled.toFixed(1) : info.scaled} ${info.unit}</td>
        <td style="padding:5px 10px;"><span class="badge badge-warning" style="font-size:0.7rem;">Holding (RW)</span></td>
      </tr>
    `;
  }

  tbody.innerHTML = rowsHtml;
}

async function stepHILSimulator() {
  try {
    const res = await fetch('/api/iot/hil/step', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({
        telemetry: {
          reactor_temp_c: parseFloat(document.getElementById('slider-temp')?.value || 500.0),
          feed_rate_kg_h: parseFloat(document.getElementById('slider-feed')?.value || 100.0),
          dryer_temp_c: 105.0,
          cyclone_dp_mbar: 12.5,
          tsi_pct: 114.5,
        },
      }),
    });
    const data = await res.json();
    updateHILScope(data);
  } catch (err) {
    console.error('HIL step failed:', err);
  }
}

async function injectHILFault(channelKey, faultType) {
  try {
    const res = await fetch('/api/iot/hil/step', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({
        fault_channel: channelKey,
        fault_type: faultType,
        telemetry: {
          reactor_temp_c: parseFloat(document.getElementById('slider-temp')?.value || 500.0),
          feed_rate_kg_h: parseFloat(document.getElementById('slider-feed')?.value || 100.0),
        },
      }),
    });
    const data = await res.json();
    updateHILScope(data);
    alert(`HIL Circuit Fault '${faultType}' applied to ${channelKey}.`);
  } catch (err) {
    alert(`Failed to inject HIL fault: ${err.message}`);
  }
}

function updateHILScope(data) {
  const clockEl = document.getElementById('iot-hil-clock');
  if (clockEl && data.clock_ticks !== undefined) {
    clockEl.textContent = `TICKS: ${data.clock_ticks} (50 Hz)`;
  }

  const chs = data.analog_channels || {};
  if (chs.AI_1) {
    const el = document.getElementById('hil-ma-ai1');
    const elAdc = document.getElementById('hil-adc-ai1');
    if (el) {
      el.textContent = `${chs.AI_1.current_ma.toFixed(2)} mA`;
      if (chs.AI_1.namur_ne43_status !== 'NORMAL') {
        el.className = 'm-val text-coral';
        el.textContent += ` (${chs.AI_1.namur_ne43_status})`;
      } else {
        el.className = 'm-val text-cyan';
      }
    }
    if (elAdc) elAdc.textContent = `${chs.AI_1.adc_12bit} cts (${chs.AI_1.voltage_v.toFixed(2)}V)`;
  }

  if (chs.AI_3) {
    const el = document.getElementById('hil-ma-ai3');
    const elAdc = document.getElementById('hil-adc-ai3');
    if (el) el.textContent = `${chs.AI_3.current_ma.toFixed(2)} mA`;
    if (elAdc) elAdc.textContent = `${chs.AI_3.adc_12bit} cts (${chs.AI_3.voltage_v.toFixed(2)}V)`;
  }

  if (chs.AI_2) {
    const el = document.getElementById('hil-ma-ai2');
    const elAdc = document.getElementById('hil-adc-ai2');
    if (el) el.textContent = `${chs.AI_2.current_ma.toFixed(2)} mA`;
    if (elAdc) elAdc.textContent = `${chs.AI_2.adc_12bit} cts (${chs.AI_2.voltage_v.toFixed(2)}V)`;
  }

  if (chs.AI_4) {
    const el = document.getElementById('hil-ma-ai4');
    const elAdc = document.getElementById('hil-adc-ai4');
    if (el) el.textContent = `${chs.AI_4.current_ma.toFixed(2)} mA`;
    if (elAdc) elAdc.textContent = `${chs.AI_4.adc_12bit} cts (${chs.AI_4.voltage_v.toFixed(2)}V)`;
  }
}

/* =========================================================================
 * Tab 10: Multi-Plant Fleet & Carbon Trading Controller
 * ========================================================================= */
function initFleetHandlers() {
  const btnCalcCorc = document.getElementById('btn-calc-corc');
  if (btnCalcCorc) btnCalcCorc.addEventListener('click', runCORCArbitrage);

  const btnSolar = document.getElementById('btn-solar-dispatch');
  if (btnSolar) btnSolar.addEventListener('click', runSolarDispatch);

  const btnAutumn = document.getElementById('btn-season-autumn');
  if (btnAutumn) btnAutumn.addEventListener('click', () => dispatchSeason('AUTUMN'));

  const btnSummer = document.getElementById('btn-season-summer');
  if (btnSummer) btnSummer.addEventListener('click', () => dispatchSeason('SUMMER'));

  const btnSpring = document.getElementById('btn-season-spring');
  if (btnSpring) btnSpring.addEventListener('click', () => dispatchSeason('SPRING'));
}

async function loadFleetStatus() {
  try {
    const res = await fetch('/api/fleet/status', {
      headers: apiHeaders(),
    });
    const data = await res.json();
    updateFleetUI(data);
  } catch (err) {
    console.error('Failed to load fleet status:', err);
  }
}

function updateFleetUI(data) {
  const kpis = data.fleet_kpis || {};
  const feedEl = document.getElementById('fleet-total-feed');
  if (feedEl) feedEl.textContent = `${kpis.total_current_throughput_kg_h.toFixed(1)} kg/h`;

  const dailyFeedEl = document.getElementById('fleet-daily-feed');
  if (dailyFeedEl) dailyFeedEl.textContent = `${kpis.daily_aggregated_feed_tonnes.toFixed(2)} t/day`;

  const oilEl = document.getElementById('fleet-total-oil');
  if (oilEl) oilEl.textContent = `${kpis.daily_aggregated_bio_oil_m3.toFixed(2)} m³/d`;

  const co2El = document.getElementById('fleet-total-co2');
  if (co2El) co2El.textContent = `${kpis.daily_permanent_co2e_sinks_tonnes.toFixed(2)} t/d`;

  const oeeEl = document.getElementById('fleet-oee-badge');
  if (oeeEl) oeeEl.textContent = `FLEET OEE: ${kpis.fleet_average_oee_pct.toFixed(1)}%`;
}

async function dispatchSeason(seasonName) {
  try {
    const res = await fetch('/api/fleet/dispatch', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({ season: seasonName }),
    });
    const data = await res.json();
    const seasonEl = document.getElementById('fleet-active-season');
    if (seasonEl) seasonEl.textContent = `${seasonName} HARVEST SCHEDULE`;
    if (data.fleet_summary) updateFleetUI(data.fleet_summary);
    alert(`Seasonal Harvest Allocation updated for ${seasonName}. Throughput dynamically balanced.`);
  } catch (err) {
    alert(`Failed to dispatch season: ${err.message}`);
  }
}

async function runCORCArbitrage() {
  const corcPrice = parseFloat(document.getElementById('slider-corc-spot')?.value || 65.0);
  const oilPrice = parseFloat(document.getElementById('slider-oil-spot')?.value || 0.65);

  try {
    const res = await fetch('/api/fleet/corc-arbitrage', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({
        corc_price: corcPrice,
        oil_price: oilPrice,
        feed_rate_kg_h: 100.0,
      }),
    });
    const data = await res.json();
    const modeEl = document.getElementById('corc-rec-mode');
    const ratEl = document.getElementById('corc-rec-rationale');
    if (modeEl) modeEl.textContent = `${data.recommended_mode} (${data.optimal_setpoint_temp_c}°C)`;
    if (ratEl) ratEl.textContent = `${data.decision_rationale} | Projected Revenue: $${data.projected_hourly_revenue_usd.toFixed(2)}/h`;
  } catch (err) {
    alert(`Arbitrage calculation failed: ${err.message}`);
  }
}

async function runSolarDispatch() {
  try {
    const res = await fetch('/api/fleet/renewable-dispatch', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({ shift_loads: true }),
    });
    const data = await res.json();
    const m = data.daily_metrics || {};
    alert(`24h Solar Dispatch Optimized:\n- Solar Generated: ${m.total_solar_generated_kwh} kWh\n- Grid Import: ${m.total_grid_imported_kwh} kWh\n- Daily Savings: $${m.daily_cost_savings_usd}\n- Projected Annual Savings: $${m.projected_annual_power_savings_usd.toLocaleString()}/yr`);
  } catch (err) {
    alert(`Solar dispatch failed: ${err.message}`);
  }
}

/* =========================================================================
 * Tab 11: 3D Spatial Digital Twin & GenAI SCADA Copilot Controller (V3.0)
 * ========================================================================= */
let threeInitialized = false;
let scene, camera, renderer, particleSystem;
let components3D = [];
let particlesEnabled = true;

function initV3Handlers() {
  const btnDrlStep = document.getElementById('btn-drl-step');
  if (btnDrlStep) btnDrlStep.addEventListener('click', stepDRLPolicy);

  const btnDrlTrain = document.getElementById('btn-drl-train');
  if (btnDrlTrain) btnDrlTrain.addEventListener('click', trainDRLEpisode);

  const btnCopilotSend = document.getElementById('btn-copilot-send');
  if (btnCopilotSend) btnCopilotSend.addEventListener('click', sendCopilotMessage);

  const copilotInput = document.getElementById('copilot-input-text');
  if (copilotInput) {
    copilotInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendCopilotMessage();
    });
  }

  // Quick prompt buttons
  const qCyclone = document.getElementById('quick-sop-cyclone');
  if (qCyclone) qCyclone.addEventListener('click', () => sendCopilotQuickQuery('Cyclone DP is spiking to 28 mbar. What is the SOP?'));

  const qMoist = document.getElementById('quick-sop-moisture');
  if (qMoist) qMoist.addEventListener('click', () => sendCopilotQuickQuery('Feedstock moisture increased to 20%. Adjust burner setpoints.'));

  const qStartup = document.getElementById('quick-sop-startup');
  if (qStartup) qStartup.addEventListener('click', () => sendCopilotQuickQuery('Give me the thermal preheat and startup procedure.'));

  const qEmergency = document.getElementById('quick-sop-emergency');
  if (qEmergency) qEmergency.addEventListener('click', () => sendCopilotQuickQuery('Initiate SIL-2 emergency safe park trip.'));

  const btnReset3D = document.getElementById('btn-reset-3d-cam');
  if (btnReset3D) {
    btnReset3D.addEventListener('click', () => {
      if (camera) {
        camera.position.set(0, 4, 10);
        camera.lookAt(0.5, 2.0, 0);
      }
    });
  }

  const btnTogglePart = document.getElementById('btn-toggle-particles');
  if (btnTogglePart) {
    btnTogglePart.addEventListener('click', () => {
      particlesEnabled = !particlesEnabled;
      if (particleSystem) particleSystem.visible = particlesEnabled;
    });
  }
}

function initThreeScene() {
  if (threeInitialized || typeof THREE === 'undefined') return;
  const container = document.getElementById('three-canvas-container');
  if (!container) return;

  threeInitialized = true;
  const w = container.clientWidth || 600;
  const h = container.clientHeight || 320;

  scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x030712, 0.04);

  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100);
  camera.position.set(0, 4, 10);
  camera.lookAt(0.5, 2.0, 0);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(w, h);
  renderer.setPixelRatio(window.devicePixelRatio || 1);
  container.appendChild(renderer.domElement);

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  const dirLight = new THREE.DirectionalLight(0x00f0ff, 1.2);
  dirLight.position.set(5, 10, 7);
  scene.add(dirLight);

  const reactorGlow = new THREE.PointLight(0x00f0ff, 2.0, 8);
  reactorGlow.position.set(0, 2.6, 0);
  scene.add(reactorGlow);

  const burnerGlow = new THREE.PointLight(0xff0055, 2.5, 5);
  burnerGlow.position.set(0, 0.4, 0);
  scene.add(burnerGlow);

  // Grid Floor
  const grid = new THREE.GridHelper(20, 20, 0x00f0ff, 0x1e293b);
  grid.position.y = 0;
  scene.add(grid);

  // Create 3D Meshes
  buildPlant3DMeshes();

  // Create Flow Particles
  buildParticleStream();

  // Mouse Interaction (Orbit / Drag)
  let isDragging = false;
  let prevMouse = { x: 0, y: 0 };

  container.addEventListener('mousedown', (e) => {
    isDragging = true;
    prevMouse = { x: e.clientX, y: e.clientY };
  });

  window.addEventListener('mouseup', () => { isDragging = false; });

  container.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const deltaX = e.clientX - prevMouse.x;
    const deltaY = e.clientY - prevMouse.y;

    camera.position.x -= deltaX * 0.02;
    camera.position.y += deltaY * 0.02;
    camera.lookAt(0.5, 2.0, 0);

    prevMouse = { x: e.clientX, y: e.clientY };
  });

  container.addEventListener('wheel', (e) => {
    e.preventDefault();
    camera.position.z = Math.max(4.0, Math.min(18.0, camera.position.z + e.deltaY * 0.01));
  });

  // Render Loop
  function animate() {
    requestAnimationFrame(animate);

    if (particleSystem && particlesEnabled) {
      const positions = particleSystem.geometry.attributes.position.array;
      for (let i = 0; i < positions.length; i += 3) {
        positions[i] += 0.04; // Move along X
        if (positions[i] > 6.0) positions[i] = -4.0;
        positions[i + 1] += Math.sin(positions[i] * 2.0) * 0.01;
      }
      particleSystem.geometry.attributes.position.needsUpdate = true;
    }

    renderer.render(scene, camera);
  }
  animate();
}

function buildPlant3DMeshes() {
  // 1. Infeed Hopper
  const matHopper = new THREE.MeshStandardMaterial({ color: 0x8b5a2b, roughness: 0.5, metalness: 0.6 });
  const geomHopper = new THREE.CylinderGeometry(0.7, 0.3, 2.2, 16);
  const meshHopper = new THREE.Mesh(geomHopper, matHopper);
  meshHopper.position.set(-4.0, 1.8, 0);
  scene.add(meshHopper);

  // 2. Fluidized Bed Reactor (Core Vessel)
  const matReactor = new THREE.MeshStandardMaterial({ color: 0x00f0ff, roughness: 0.2, metalness: 0.8, emissive: 0x002233 });
  const geomReactor = new THREE.CylinderGeometry(0.8, 0.8, 3.6, 24);
  const meshReactor = new THREE.Mesh(geomReactor, matReactor);
  meshReactor.position.set(0, 2.6, 0);
  scene.add(meshReactor);

  // 3. Combustor / Burner Base
  const matBurner = new THREE.MeshStandardMaterial({ color: 0xff0055, roughness: 0.3, metalness: 0.7, emissive: 0x330011 });
  const geomBurner = new THREE.BoxGeometry(1.8, 0.8, 1.8);
  const meshBurner = new THREE.Mesh(geomBurner, matBurner);
  meshBurner.position.set(0, 0.4, 0);
  scene.add(meshBurner);

  // 4. Cyclone
  const matCyclone = new THREE.MeshStandardMaterial({ color: 0xffb800, roughness: 0.3, metalness: 0.7 });
  const geomCycloneTop = new THREE.CylinderGeometry(0.5, 0.5, 1.4, 16);
  const geomCycloneCone = new THREE.ConeGeometry(0.5, 1.2, 16);
  const meshCycTop = new THREE.Mesh(geomCycloneTop, matCyclone);
  const meshCycCone = new THREE.Mesh(geomCycloneCone, matCyclone);
  meshCycTop.position.set(2.8, 3.8, 0);
  meshCycCone.position.set(2.8, 2.5, 0);
  meshCycCone.rotation.x = Math.PI;
  scene.add(meshCycTop);
  scene.add(meshCycCone);

  // 5. Biochar Quench Silo
  const matChar = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.8, metalness: 0.2 });
  const geomChar = new THREE.CylinderGeometry(0.5, 0.5, 1.4, 16);
  const meshChar = new THREE.Mesh(geomChar, matChar);
  meshChar.position.set(2.8, 0.7, 0);
  scene.add(meshChar);

  // 6. Condenser HX
  const matCond = new THREE.MeshStandardMaterial({ color: 0x00ff88, roughness: 0.2, metalness: 0.8 });
  const geomCond = new THREE.CylinderGeometry(0.6, 0.6, 3.0, 16);
  const meshCond = new THREE.Mesh(geomCond, matCond);
  meshCond.position.set(5.2, 2.0, 0);
  scene.add(meshCond);

  // Piping Conduits
  const pipeMat = new THREE.MeshStandardMaterial({ color: 0x475569, metalness: 0.9, roughness: 0.1 });
  const pipe1 = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 4.0), pipeMat);
  pipe1.position.set(-2.0, 2.0, 0);
  pipe1.rotation.z = Math.PI / 2;
  scene.add(pipe1);

  const pipe2 = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 2.8), pipeMat);
  pipe2.position.set(1.4, 3.8, 0);
  pipe2.rotation.z = Math.PI / 2;
  scene.add(pipe2);

  const pipe3 = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, 2.4), pipeMat);
  pipe3.position.set(4.0, 3.2, 0);
  pipe3.rotation.z = Math.PI / 2;
  scene.add(pipe3);
}

function buildParticleStream() {
  const count = 120;
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    positions[i * 3] = -4.0 + (i / count) * 10.0;
    positions[i * 3 + 1] = 2.0 + Math.random() * 0.4;
    positions[i * 3 + 2] = (Math.random() - 0.5) * 0.4;
  }

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

  const material = new THREE.PointsMaterial({
    color: 0x00f0ff,
    size: 0.15,
    transparent: true,
    opacity: 0.8,
  });

  particleSystem = new THREE.Points(geometry, material);
  scene.add(particleSystem);
}

async function stepDRLPolicy() {
  try {
    const res = await fetch('/api/drl/step', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({}),
    });
    const data = await res.json();
    const act = data.action_executed || [0, 0, 0];
    const val = data.critic_value_estimate || 0.0;

    const bEl = document.getElementById('drl-burner-act');
    const fEl = document.getElementById('drl-feed-act');
    const vEl = document.getElementById('drl-critic-val');

    if (bEl) bEl.textContent = `${act[0] >= 0 ? '+' : ''}${act[0].toFixed(1)}%`;
    if (fEl) fEl.textContent = `${act[1] >= 0 ? '+' : ''}${act[1].toFixed(1)} kg/h`;
    if (vEl) vEl.textContent = val.toFixed(1);
  } catch (err) {
    console.error('DRL step failed:', err);
  }
}

async function trainDRLEpisode() {
  const btn = document.getElementById('btn-drl-train');
  if (btn) {
    btn.disabled = true;
    btn.textContent = 'Training PPO...';
  }

  try {
    const res = await fetch('/api/drl/train-episode', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({ max_steps: 30 }),
    });
    const data = await res.json();
    alert(`PPO Training Episode ${data.episode} Complete:\n- Reward: ${data.total_episode_reward}\n- Mean Temp Error: ${data.mean_temperature_error_c} °C\n- Status: ${data.convergence_status}`);
  } catch (err) {
    alert(`Training failed: ${err.message}`);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.textContent = 'Train PPO';
    }
  }
}

async function sendCopilotMessage() {
  const input = document.getElementById('copilot-input-text');
  if (!input || !input.value.trim()) return;
  const q = input.value.trim();
  input.value = '';
  await executeCopilotQuery(q);
}

function sendCopilotQuickQuery(q) {
  executeCopilotQuery(q);
}

async function executeCopilotQuery(queryText) {
  const chatBox = document.getElementById('copilot-chat-box');
  if (!chatBox) return;

  // Append user bubble
  const userDiv = document.createElement('div');
  userDiv.style.cssText = 'background:rgba(255,255,255,0.06); border-right:3px solid var(--accent-amber); padding:8px; border-radius:4px; align-self:flex-end; max-width:85%;';
  userDiv.innerHTML = `<strong style="color:var(--accent-amber);">Operator:</strong><p style="margin-top:2px;">${queryText}</p>`;
  chatBox.appendChild(userDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const res = await fetch('/api/copilot/chat', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({
        query: queryText,
        plant_state: {
          reactor_temp_c: parseFloat(document.getElementById('slider-temp')?.value || 500.0),
          feed_rate_kg_h: parseFloat(document.getElementById('slider-feed')?.value || 100.0),
          cyclone_dp_mbar: 12.5,
          moisture_pct: 10.0,
          fsm_state: 'AUTONOMOUS_CRUISE',
        },
      }),
    });
    const data = await res.json();

    // Append AI bubble
    const aiDiv = document.createElement('div');
    aiDiv.style.cssText = 'background:rgba(0,240,255,0.08); border-left:3px solid var(--primary-cyan); padding:8px; border-radius:4px; max-width:90%;';
    aiDiv.innerHTML = `
      <strong style="color:var(--primary-cyan);">Copilot Assistant:</strong>
      <p style="margin-top:4px; line-height:1.4;">${data.copilot_response}</p>
      <div style="font-size:0.7rem; color:var(--text-muted); margin-top:6px;">
        Action: <strong style="color:var(--primary-green);">${data.recommended_action}</strong> | Docs: <em>${(data.matched_engineering_documents || []).join(', ')}</em>
      </div>
    `;
    chatBox.appendChild(aiDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  } catch (err) {
    console.error('Copilot query failed:', err);
  }
}
