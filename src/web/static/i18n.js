/**
 * BIOPLANT AI — Dynamic Bilingual Internationalization (i18n) Engine (EN / TR)
 */

const i18nData = {
  en: {
    // Navigation Tabs
    "nav.flowsheet": "Control Room",
    "nav.soft_sensors": "Soft Sensors (95% UQ)",
    "nav.optimization": "Pareto Optimizer",
    "nav.diagnostics": "Fault Diagnostics",
    "nav.maintenance": "Predictive Maintenance",
    "nav.control": "Dynamic Control (MPC)",
    "nav.economics": "TEA & LCA Carbon",
    "nav.autopilot": "Autopilot Cockpit",
    "nav.iot": "Industrial IoT & Edge",
    "nav.fleet": "Fleet & Carbon Trading",
    "nav.spatial": "3D Spatial & Copilot",

    // Sidebar & Brand
    "brand.title": "BIOPLANT AI",
    "brand.tag": "V3.0 NEXT-GEN AI & SPATIAL",
    "sidebar.status_label": "DIGITAL TWIN STATE",
    "sidebar.status_val": "REAL-TIME ACTIVE",

    // Top Header
    "top.temp_label": "REACTOR BED TEMP",
    "top.feed_label": "INFEED RATE",
    "top.tsi_label": "THERMAL CLOSURE (TSI)",
    "top.mode_label": "OPERATIONAL REGIME",
    "top.docs_btn": "⚡ Swagger API (/docs)",
    "top.user_manual": "📖 User Manual",

    // Tab 1: Flowsheet
    "tab1.card_title": "Biomass Conversion Parameters",
    "tab1.feedstock_label": "Biomass Feedstock Selection",
    "tab1.temp_slider": "Pyrolysis Bed Temperature",
    "tab1.feed_slider": "Biomass Feed Rate",
    "tab1.moist_slider": "Moisture Content",
    "tab1.engine_label": "Kinetic & Yield Engine",
    "tab1.engine_ml": "Physics-Constrained ML Surrogate (XGBoost)",
    "tab1.engine_first_principles": "First-Principles Stoichiometric Flowsheet",
    "tab1.btn_run": "Run First-Principles Simulation",
    "tab1.flowsheet_title": "Closed-Loop Process Flowsheet & Mass Balance",
    "tab1.hopper_title": "1. Infeed Silo & Feeder",
    "tab1.reactor_title": "2. Pyrolysis Reactor R-101",
    "tab1.cyclone_title": "3. Separation Cyclone CY-101",
    "tab1.condenser_title": "4. Bio-Oil Condenser HX-102",
    "tab1.combustor_title": "5. Syngas Combustor B-101",

    // Tab 2: Soft Sensors
    "tab2.card_title": "Virtual Process Sensing & Uncertainty Quantification",
    "tab2.desc": "Bayesian ML soft sensors estimating unmeasured states with 95% Confidence Intervals.",
    "tab2.btn_update": "Recalibrate Soft Sensors",

    // Tab 3: Pareto Optimizer
    "tab3.card_title": "Multi-Objective NSGA-II Optimizer",
    "tab3.desc": "Generates non-dominated Pareto trade-offs across Bio-Oil yield, Carbon Sequestration, and Energy Autarky.",
    "tab3.btn_optimize": "Execute Pareto Optimization",

    // Tab 4: Fault Diagnostics
    "tab4.card_title": "Equipment Health & Fault Injection",
    "tab4.desc": "Tri-layer Isolation Forest, Mahalanobis Distance, and Physics-informed anomaly detection.",
    "tab4.btn_diagnose": "Run Diagnostic Scan",

    // Tab 5: Maintenance
    "tab5.card_title": "Asset Health Degradation & CMMS",
    "tab5.desc": "Weibull Remaining Useful Life (RUL) estimation and prescriptive maintenance dispatching.",
    "tab5.btn_dispatch": "Dispatch Prescriptive Work Order",

    // Tab 6: Control
    "tab6.card_title": "Dynamic MPC & PID Setpoint Tracking",
    "tab6.desc": "Non-linear Model Predictive Control with state constraints and disturbance rejection.",
    "tab6.btn_step": "Simulate 60-Minute Closed-Loop Step",

    // Tab 7: Economics & LCA
    "tab7.card_title": "20-Year DCF Valuation & ISO 14040/14044 LCA",
    "tab7.desc": "Guthrie module capital cost estimation and cradle-to-gate carbon-negative accounting.",
    "tab7.btn_calc": "Recalculate DCF & Carbon Sinks",

    // Tab 8: Autopilot
    "tab8.card_title": "5-State Autonomous Supervisory FSM",
    "tab8.desc": "Automated self-healing flight controller with blackbox flight recorder.",
    "tab8.btn_step_ap": "Step Autonomous FSM (dt = 2.0s)",
    "tab8.btn_mission": "Execute 4-Hour Stress Test Mission",

    // Tab 9: IoT
    "tab9.card_title": "Industrial Protocol Bridges & HIL Current Loops",
    "tab9.desc": "Modbus TCP 16-bit register bank, MQTT Sparkplug B, OPC-UA, and 4-20mA HIL ADC.",
    "tab9.btn_poll_mb": "Poll Modbus Registers",
    "tab9.btn_hil_step": "Step HIL ADC (50 Hz)",
    "tab9.btn_fault_open": "Inject Open Loop (<3.6mA)",
    "tab9.btn_fault_short": "Inject Short Circuit (>21mA)",
    "tab9.btn_fault_clear": "Clear Circuit Faults",

    // Tab 10: Fleet
    "tab10.card_title": "CORC Carbon Market & Fleet Dispatch",
    "tab10.desc": "Decentralized regional plant coordination and real-time Puro.earth CORC price arbitrage.",
    "tab10.btn_arbitrage": "Run Arbitrage",
    "tab10.btn_solar": "Solar 24h Sim",

    // Tab 11: 3D Spatial & Copilot
    "tab11.card_title": "3D WebGL Holographic Spatial Twin",
    "tab11.btn_particles": "Flow Particles",
    "tab11.btn_reset_cam": "Reset View",
    "tab11.drl_title": "Deep RL PPO Non-Linear Policy (BioPlant-v1)",
    "tab11.btn_drl_step": "Step Policy",
    "tab11.btn_drl_train": "Train PPO",
    "tab11.copilot_title": "GenAI SCADA Operator Copilot",
    "tab11.copilot_badge": "SOP & P&ID ACTIVE",
    "tab11.copilot_welcome": "Welcome operator. I am indexed on all plant P&ID blueprints, SOP manuals, and SIL-2 safety interlocks. Ask any operational question or select a prompt below.",
    "tab11.copilot_placeholder": "Ask SCADA Copilot a question...",
    "tab11.btn_send": "Send",
  },
  tr: {
    // Navigation Tabs
    "nav.flowsheet": "Kontrol Odası",
    "nav.soft_sensors": "Yumuşak Sensörler (%95 Güven)",
    "nav.optimization": "Pareto Optimizatörü",
    "nav.diagnostics": "Arıza Teşhisi",
    "nav.maintenance": "Kestirimci Bakım",
    "nav.control": "Dinamik Kontrol (MPC)",
    "nav.economics": "TEA & LCA Karbon Analizi",
    "nav.autopilot": "Otopilot Kokpiti",
    "nav.iot": "Endüstriyel IoT & Uç Bilişim",
    "nav.fleet": "Filo Yönetimi & Karbon Ticareti",
    "nav.spatial": "3B Mekansal İkiz & Copilot",

    // Sidebar & Brand
    "brand.title": "BIOPLANT AI",
    "brand.tag": "V3.0 YENİ NESİL YAPAY ZEKA & 3B",
    "sidebar.status_label": "DİJİTAL İKİZ DURUMU",
    "sidebar.status_val": "GERÇEK ZAMANLI AKTİF",

    // Top Header
    "top.temp_label": "REAKTÖR YATAK SICAKLIĞI",
    "top.feed_label": "BESLEME HIZI",
    "top.tsi_label": "TERMAL KAPANMA (TSI)",
    "top.mode_label": "ÇALIŞMA REJİMİ",
    "top.docs_btn": "⚡ Swagger API (/docs)",
    "top.user_manual": "📖 Kullanıcı Kılavuzu",

    // Tab 1: Flowsheet
    "tab1.card_title": "Biyokütle Dönüşüm Parametreleri",
    "tab1.feedstock_label": "Biyokütle Hammadde Seçimi",
    "tab1.temp_slider": "Piroliz Yatak Sıcaklığı",
    "tab1.feed_slider": "Biyokütle Besleme Hızı",
    "tab1.moist_slider": "Nem Oranı",
    "tab1.engine_label": "Kinetik ve Verim Motoru",
    "tab1.engine_ml": "Fizik Kısıtlı ML Vekil Modeli (XGBoost)",
    "tab1.engine_first_principles": "Temel Prensiplere Dayalı Stokiyometrik Akış",
    "tab1.btn_run": "Temel Prensip Simülasyonunu Çalıştır",
    "tab1.flowsheet_title": "Kapalı Çevrim Proses Akış Şeması & Kütle Dengesi",
    "tab1.hopper_title": "1. Besleme Silosu & Helezon",
    "tab1.reactor_title": "2. Piroliz Reaktörü R-101",
    "tab1.cyclone_title": "3. Ayırma Siklonu CY-101",
    "tab1.condenser_title": "4. Biyo-Yağ Yoğuşturucu HX-102",
    "tab1.combustor_title": "5. Sentez Gazı Brülörü B-101",

    // Tab 2: Soft Sensors
    "tab2.card_title": "Sanal Proses Algılama & Belirsizlik Analizi",
    "tab2.desc": "Ölçülemeyen durumları %95 Güven Aralıklarıyla tahmin eden Bayesyen ML yumuşak sensörleri.",
    "tab2.btn_update": "Sensörleri Yeniden Kalibre Et",

    // Tab 3: Pareto Optimizer
    "tab3.card_title": "Çok Amaçlı NSGA-II Optimizatörü",
    "tab3.desc": "Biyo-yağ verimi, Karbon Tutma ve Enerji Öz-Yeterliliği arasında baskın olmayan Pareto ödünleşimleri üretir.",
    "tab3.btn_optimize": "Pareto Optimizasyonunu Başlat",

    // Tab 4: Fault Diagnostics
    "tab4.card_title": "Ekipman Sağlığı & Arıza Enjeksiyonu",
    "tab4.desc": "İzolasyon Ormanı, Mahalanobis Mesafesi ve Fizik tabanlı 3 katmanlı anomali tespiti.",
    "tab4.btn_diagnose": "Tanılama Taramasını Çalıştır",

    // Tab 5: Maintenance
    "tab5.card_title": "Varlık Aşınması & Bakım Yönetimi (CMMS)",
    "tab5.desc": "Weibull Kalan Faydalı Ömür (RUL) tahmini ve kuralcı bakım iş emri sevkiyatı.",
    "tab5.btn_dispatch": "Kuralcı İş Emri Oluştur",

    // Tab 6: Control
    "tab6.card_title": "Dinamik MPC & PID Ayar Noktası Takibi",
    "tab6.desc": "Durum kısıtlamalı ve bozulma bastırmalı Doğrusal Olmayan Model Öngörülü Kontrol (NMPC).",
    "tab6.btn_step": "60 Dakikalık Kapalı Çevrim Simülasyonu",

    // Tab 7: Economics & LCA
    "tab7.card_title": "20 Yıllık DCF Değerleme & ISO 14040/14044 LCA",
    "tab7.desc": "Guthrie modülü sermaye maliyeti tahmini ve beşikten-kapıya karbon negatif muhasebe.",
    "tab7.btn_calc": "DCF & Karbon Yutaklarını Yeniden Hesapla",

    // Tab 8: Autopilot
    "tab8.card_title": "5 Durumlu Otonom Denetleyici FSM",
    "tab8.desc": "Karukutu uçuş kayıt cihazına sahip otomatik kendini iyileştiren uçuş kontrolörü.",
    "tab8.btn_step_ap": "Otonom Adım İlerlet (dt = 2.0s)",
    "tab8.btn_mission": "4 Saatlik Stres Testi Görevini Başlat",

    // Tab 9: IoT
    "tab9.card_title": "Endüstriyel Protokol Köprüleri & HIL Akım Döngüleri",
    "tab9.desc": "Modbus TCP 16-bit kayıt tablosu, MQTT Sparkplug B, OPC-UA ve 4-20mA HIL ADC simülatörü.",
    "tab9.btn_poll_mb": "Modbus Kayıtlarını Oku",
    "tab9.btn_hil_step": "HIL ADC Adımı (50 Hz)",
    "tab9.btn_fault_open": "Açık Devre Hatası Ver (<3.6mA)",
    "tab9.btn_fault_short": "Kısa Devre Hatası Ver (>21mA)",
    "tab9.btn_fault_clear": "Devre Hatalarını Temizle",

    // Tab 10: Fleet
    "tab10.card_title": "CORC Karbon Piyasası & Filo Sevkiyatı",
    "tab10.desc": "Merkezi olmayan bölgesel tesis koordinasyonu ve gerçek zamanlı Puro.earth CORC arbitrajı.",
    "tab10.btn_arbitrage": "Arbitrajı Çalıştır",
    "tab10.btn_solar": "24s Güneş Simülasyonu",

    // Tab 11: 3D Spatial & Copilot
    "tab11.card_title": "3B WebGL Holografik Mekansal Dijital İkiz",
    "tab11.btn_particles": "Akış Parçacıkları",
    "tab11.btn_reset_cam": "Görünümü Sıfırla",
    "tab11.drl_title": "Derin RL PPO Doğrusal Olmayan Politika (BioPlant-v1)",
    "tab11.btn_drl_step": "Politikayı Adımla",
    "tab11.btn_drl_train": "PPO Eğitimi Yap",
    "tab11.copilot_title": "Yapay Zeka SCADA Operatör Copilot",
    "tab11.copilot_badge": "SOP & P&ID AKTİF",
    "tab11.copilot_welcome": "Hoş geldiniz operatör. Tüm tesis P&ID şemaları, SOP kılavuzları ve SIL-2 güvenlik kilitleri üzerinde indekslendim. Operasyonel bir soru sorun veya aşağıdaki hazır komutları seçin.",
    "tab11.copilot_placeholder": "SCADA Copilot'a bir soru sorun...",
    "tab11.btn_send": "Gönder",
  }
};

let currentLang = localStorage.getItem('bioplant_lang') || 'en';

function getCurrentLanguage() {
  return currentLang;
}

function setLanguage(lang) {
  if (!i18nData[lang]) lang = 'en';
  currentLang = lang;
  localStorage.setItem('bioplant_lang', lang);

  // Update active state on language switcher buttons
  document.querySelectorAll('.btn-lang').forEach(btn => {
    if (btn.getAttribute('data-lang') === lang) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Apply translations to all DOM elements with data-i18n attribute
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (i18nData[lang][key]) {
      if (el.tagName === 'INPUT' && el.getAttribute('placeholder')) {
        el.setAttribute('placeholder', i18nData[lang][key]);
      } else {
        el.textContent = i18nData[lang][key];
      }
    }
  });

  // Dispatch custom language change event
  window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
}
