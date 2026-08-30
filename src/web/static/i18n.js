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
    "top.temp_label": "REACTOR CORE (TI-103)",
    "top.feed_label": "FEED RATE (FI-101)",
    "top.tsi_label": "THERMAL SELF-SUFFICIENCY",
    "top.mode_label": "ENERGY STATUS",
    "top.docs_btn": "⚡ Swagger API (/docs)",
    "top.user_manual": "📖 User Manual / Kılavuz",

    // Tab 1: Flowsheet
    "tab1.card_title": "Process Setpoint Actuators",
    "tab1.card_badge": "Closed-Loop DCS",
    "tab1.feedstock_label": "Feedstock Profile",
    "tab1.opt_pine": "Pine Sawdust (Forestry Residue)",
    "tab1.opt_olive": "Olive Pomace (Agri Waste)",
    "tab1.opt_straw": "Wheat Straw (Herbaceous)",
    "tab1.opt_husk": "Rice Husk (Cereal Husk)",
    "tab1.temp_slider": "Reactor Temperature",
    "tab1.feed_slider": "Wet Biomass Feed Rate",
    "tab1.moist_slider": "Feed Initial Moisture",
    "tab1.engine_label": "Yield Prediction Engine",
    "tab1.engine_det": "Deterministic (First-Principles Kinetics)",
    "tab1.engine_ml": "Machine Learning (Gradient Boosting Champion)",
    "tab1.btn_run": "Execute Digital Twin Simulation",
    "tab1.flowsheet_title": "Live Flowsheet & Energy Integration",
    "tab1.mass_conserved": "MASS CONSERVED 100.0%",
    "tab1.m_biooil": "Liquid Bio-Oil",
    "tab1.m_biochar": "Solid Biochar",
    "tab1.m_syngas": "Clean Syngas",
    "tab1.m_thermal": "Net Thermal Power",
    "tab1.m_self_sufficient": "Self-Sufficient",

    // Tab 2: Soft Sensors
    "tab2.header_title": "Industrial Soft Sensor Suite & 95% Uncertainty Quantification (UQ)",
    "tab2.header_desc": "Real-time inferential estimators predicting unmeasured lab properties from online plant telemetry.",

    // Tab 3: Pareto Optimizer
    "tab3.header_title": "AI-Driven Multiobjective Optimization & Pareto Frontier",
    "tab3.header_desc": "Non-dominated NSGA-II frontiers and TOPSIS multi-criteria decision support.",
    "tab3.profile_title": "Stakeholder Profile Selection",
    "tab3.prof_balanced": "Balanced Operator",
    "tab3.prof_oil": "Max Bio-Oil Yield",
    "tab3.prof_char": "Carbon Sequestration",
    "tab3.prof_profit": "Max Economic Profit",
    "tab3.btn_opt": "Compute Pareto Frontier (30 Solutions)",
    "tab3.chart_title": "Bio-Oil vs Biochar Pareto Frontier Trade-Off",

    // Tab 4: Fault Diagnostics
    "tab4.header_title": "Process Anomaly Detection, Equipment Diagnostics & Alarm Management",
    "tab4.header_desc": "Tri-layer anomaly detection (Physical Balances, Isolation Forest & PCA Reconstruction Error).",
    "tab4.sim_title": "Simulate Industrial Failure Mode",
    "tab4.fault_label": "Injected Equipment Failure",
    "tab4.fault_none": "Normal Nominal Operations (Healthy)",
    "tab4.fault_cyclone": "Cyclone C101 Dipleg Blockage (Ash Bridge)",
    "tab4.fault_fouling": "Condenser HX102 Tar/Wax Fouling",
    "tab4.fault_runaway": "Pyrolysis Reactor R101 Thermal Runaway",
    "tab4.fault_sensor": "Thermocouple Sensor Drift (TI-103 Bias)",
    "tab4.fault_jam": "Biomass Infeed Auger Jamming (Fuel Loss)",
    "tab4.sev_label": "Fault Severity",
    "tab4.btn_run_diag": "Run Tri-Layer Anomaly Diagnostics",

    // Tab 5: Maintenance
    "tab5.header_title": "Predictive Maintenance, 95% RUL Prognostics & Work Order Dispatch",
    "tab5.header_desc": "Physics-informed asset wear degradation trajectories and automated safety LOTO work orders.",
    "tab5.timeline_title": "Plant Operating Timeline",
    "tab5.hours_label": "Cumulative Operating Hours",
    "tab5.btn_eval": "Evaluate Fleet RUL & Work Orders",

    // Tab 6: Dynamic Control
    "tab6.header_title": "Dynamic Closed-Loop Process Control & Model Predictive Control (MPC)",
    "tab6.header_desc": "Transient simulation of reactor thermal capacitance, feedback PID stabilization, and receding horizon MPC.",
    "tab6.cfg_title": "Controller Configuration",
    "tab6.ctrl_label": "Active Control Architecture",
    "tab6.ctrl_mpc": "Model Predictive Controller (MPC)",
    "tab6.ctrl_pid": "Industrial Digital PID Controller",
    "tab6.ctrl_open": "Uncontrolled Open-Loop (Constant 55% Duty)",
    "tab6.sp_label": "Target Setpoint (Step at 10 min)",
    "tab6.dist_label": "Moisture Disturbance (at 30 min)",
    "tab6.btn_run_ctrl": "Execute 60-Minute Transient Simulation",
    "tab6.chart_title": "Live 60-Minute Closed-Loop Response Trajectory",

    // Tab 7: Economics & LCA
    "tab7.header_title": "Techno-Economic Assessment (TEA) & ISO 14040/14044 LCA Carbon Accounting",
    "tab7.header_desc": "20-Year Discounted Cash Flow valuation, Guthrie Capex/Opex, Levelized Cost of Bio-Oil, and Scope 1-2-3 carbon removals.",
    "tab7.market_title": "Market & Commercial Valuation Parameters",
    "tab7.oil_price_label": "Bio-Oil Market Price ($/kg)",
    "tab7.char_price_label": "Biochar Market Price ($/kg)",
    "tab7.corc_price_label": "Carbon Removal Credit Price ($/tonne CO2)",
    "tab7.btn_calc_tea": "Evaluate 20-Year TEA & LCA Profile",

    // Tab 8: Autopilot
    "tab8.header_title": "Fully Autonomous AI Plant Autopilot & Supervisory Cockpit (V2.0)",
    "tab8.header_desc": "Closed-loop autonomous flight operations: Startup preheat, cruise tracking, moisture adaptation, and pulse-jet fault self-healing.",
    "tab8.flight_title": "Flight Director Control",
    "tab8.master_label": "Autopilot Master Switch",
    "tab8.ap_engage": "ENGAGE AUTONOMOUS AUTOPILOT",
    "tab8.ap_disengage": "DISENGAGE AUTOPILOT (MANUAL OVERRIDE)",
    "tab8.dist_moist_label": "Injected Disturbance (Moisture)",
    "tab8.inject_anomaly_label": "Inject Flight Anomaly",
    "tab8.anom_none": "Nominal (No Injected Fault)",
    "tab8.anom_cyclone": "Cyclone Dipleg Blockage",
    "tab8.anom_runaway": "Reactor Thermal Runaway (>630°C)",
    "tab8.btn_mission": "Execute 4-Hour Stress Test Mission",
    "tab8.blackbox_title": "Live Blackbox Telemetry & Event Stream",
    "tab8.status_ready": "AUTOPILOT READY",
    "tab8.m_temp_pv": "Reactor Temp (PV)",
    "tab8.m_feed_rate": "Feed Auger Rate",
    "tab8.m_tsi": "Thermal Index (TSI)",

    // Tab 9: IoT
    "tab9.gateways_title": "Edge Protocol Bridges & HIL",
    "tab9.modbus_label": "Modbus TCP Gateway",
    "tab9.mqtt_label": "MQTT Sparkplug B Edge Broker",
    "tab9.opcua_label": "OPC-UA IEC 62541 Address Space",
    "tab9.hil_sig_label": "HIL 4-20mA Signal Conditioning",
    "tab9.btn_hil_step": "Step HIL Clock",
    "tab9.btn_modbus_poll": "Poll Modbus",
    "tab9.hil_fault_label": "Inject HIL Loop Fault (NAMUR NE 43)",
    "tab9.btn_fault_open": "Open Loop (0mA)",
    "tab9.btn_fault_short": "Short Loop (24mA)",
    "tab9.btn_fault_clear": "Clear",
    "tab9.reg_table_title": "Live Modbus Register Table (16-bit) & 4-20mA Current Loops",
    "tab9.th_address": "Address",
    "tab9.th_tag": "Register Tag / Name",
    "tab9.th_raw": "Raw (16-bit)",
    "tab9.th_scaled": "Scaled Engineering Value",
    "tab9.th_type": "Type",
    "tab9.poll_hint": "Click 'Poll Modbus' to fetch registers",

    // Tab 10: Fleet
    "tab10.corc_title": "CORC Carbon Market & Fleet Dispatch",
    "tab10.corc_spot_label": "Puro.earth CORC Spot Price",
    "tab10.oil_spot_label": "Bio-Oil Market Price",
    "tab10.agri_dispatch_label": "Seasonal Agricultural Dispatch",
    "tab10.btn_autumn": "Autumn (Olive)",
    "tab10.btn_summer": "Summer (Straw)",
    "tab10.btn_spring": "Spring (Pine)",
    "tab10.exec_opt_label": "Execute Arbitrage & Grid Optimization",
    "tab10.btn_arbitrage": "Run Arbitrage",
    "tab10.btn_solar": "Solar 24h Sim",
    "tab10.hubs_title": "Decentralized Regional Plant Nodes (3 Active Hubs)",
    "tab10.m_total_feed": "Total Fleet Feed",
    "tab10.m_total_oil": "Daily Bio-Oil Volume",
    "tab10.m_total_carbon": "Daily Carbon Sinks",

    // Tab 11: 3D Spatial & Copilot
    "tab11.spatial_title": "3D WebGL Holographic Spatial Twin",
    "tab11.btn_particles": "Flow Particles",
    "tab11.btn_reset_cam": "Reset View",
    "tab11.spatial_hint": "[Drag to Rotate • Scroll to Zoom • Click Component for Telemetry]",
    "tab11.drl_title": "Deep RL PPO Non-Linear Policy (BioPlant-v1)",
    "tab11.btn_drl_step": "Step Policy",
    "tab11.btn_drl_train": "Train PPO",
    "tab11.copilot_title": "GenAI SCADA Operator Copilot",
    "tab11.copilot_badge": "SOP & P&ID ACTIVE",
    "tab11.copilot_welcome": "Welcome operator. I am indexed on all plant P&ID blueprints, SOP manuals, and SIL-2 safety interlocks. Ask any operational question or select a prompt below.",
    "tab11.quick_cyclone": "Cyclone DP Spikes",
    "tab11.quick_moisture": "Moisture Surge",
    "tab11.quick_startup": "Pre-Heat SOP",
    "tab11.quick_emergency": "SIL-2 Safe Park",
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
    "top.temp_label": "REAKTÖR YATAK SICAKLIĞI (TI-103)",
    "top.feed_label": "BESLEME HIZI (FI-101)",
    "top.tsi_label": "TERMAL KAPANMA (TSI)",
    "top.mode_label": "ENERJİ DURUMU",
    "top.docs_btn": "⚡ Swagger API (/docs)",
    "top.user_manual": "📖 Kullanıcı Kılavuzu / Manual",

    // Tab 1: Flowsheet
    "tab1.card_title": "Proses Ayar Noktası Eyleyicileri",
    "tab1.card_badge": "Kapalı Çevrim DCS",
    "tab1.feedstock_label": "Biyokütle Hammadde Profili",
    "tab1.opt_pine": "Çam Talaşı (Ormancılık Kalıntısı)",
    "tab1.opt_olive": "Zeytin Prinası (Tarımsal Atık)",
    "tab1.opt_straw": "Buğday Samanı (Otsu Biyokütle)",
    "tab1.opt_husk": "Pirinç Kavuzu (Tahıl Kabuğu)",
    "tab1.temp_slider": "Reaktör Sıcaklığı",
    "tab1.feed_slider": "Yaş Biyokütle Besleme Hızı",
    "tab1.moist_slider": "Başlangıç Nem Oranı",
    "tab1.engine_label": "Verim Tahmin Motoru",
    "tab1.engine_det": "Deterministik (Temel Kinetik İlkeler)",
    "tab1.engine_ml": "Makine Öğrenimi (Gradyan Artırma Modeli)",
    "tab1.btn_run": "Dijital İkiz Simülasyonunu Çalıştır",
    "tab1.flowsheet_title": "Canlı Akış Şeması & Enerji Entegrasyonu",
    "tab1.mass_conserved": "KÜTLE %100.0 KORUNDU",
    "tab1.m_biooil": "Sıvı Biyo-Yağ",
    "tab1.m_biochar": "Katı Biyokömür",
    "tab1.m_syngas": "Temiz Sentez Gazı",
    "tab1.m_thermal": "Net Termal Güç",
    "tab1.m_self_sufficient": "Öz-Yeterli",

    // Tab 2: Soft Sensors
    "tab2.header_title": "Endüstriyel Yumuşak Sensör Paketi & %95 Belirsizlik Analizi (UQ)",
    "tab2.header_desc": "Tesis telemetrisinden laboratuvar analizlerini tahmin eden gerçek zamanlı Bayesyen kestiriciler.",

    // Tab 3: Pareto Optimizer
    "tab3.header_title": "Yapay Zeka Destekli Çok Amaçlı Optimizasyon & Pareto Sınırı",
    "tab3.header_desc": "Baskın olmayan NSGA-II sınırları ve TOPSIS çok kriterli karar destek mekanizması.",
    "tab3.profile_title": "Paydaş Profil Seçimi",
    "tab3.prof_balanced": "Dengeli Operatör",
    "tab3.prof_oil": "Maksimum Biyo-Yağ",
    "tab3.prof_char": "Karbon Tutma Odaklı",
    "tab3.prof_profit": "Maksimum Ekonomik Kâr",
    "tab3.btn_opt": "Pareto Sınırını Hesapla (30 Çözüm)",
    "tab3.chart_title": "Biyo-Yağ / Biyokömür Pareto Ödünleşim Eğrisi",

    // Tab 4: Fault Diagnostics
    "tab4.header_title": "Proses Anomali Tespiti, Ekipman Teşhisi ve Alarm Yönetimi",
    "tab4.header_desc": "3 Katmanlı anomali tespiti (Fiziksel Dengeler, İzolasyon Ormanı ve PCA Hata Rekonstrüksiyonu).",
    "tab4.sim_title": "Endüstriyel Arıza Modu Simülasyonu",
    "tab4.fault_label": "Enjekte Edilen Ekipman Arızası",
    "tab4.fault_none": "Normal Nominal Operasyon (Sağlıklı)",
    "tab4.fault_cyclone": "Siklon C101 Dip Borusu Tıkanması (Kül Köprüsü)",
    "tab4.fault_fouling": "Yoğuşturucu HX102 Katran/Vaks Kirlenmesi",
    "tab4.fault_runaway": "Piroliz Reaktörü R101 Termal Kaçak",
    "tab4.fault_sensor": "Termokupl Sensör Kayması (TI-103 Sapması)",
    "tab4.fault_jam": "Besleme Helezonu Sıkışması (Yakıt Kaybı)",
    "tab4.sev_label": "Arıza Şiddeti",
    "tab4.btn_run_diag": "3 Katmanlı Anomali Teşhisini Başlat",

    // Tab 5: Maintenance
    "tab5.header_title": "Kestirimci Bakım, %95 RUL Ömür Tahmini & İş Emri Sevki",
    "tab5.header_desc": "Fizik temelli varlık aşınma modelleri ve otomatik emniyetli LOTO iş emirleri.",
    "tab5.timeline_title": "Tesis Çalışma Zaman Çizelgesi",
    "tab5.hours_label": "Kümülatif Çalışma Saati",
    "tab5.btn_eval": "Filo RUL ve İş Emirlerini Değerlendir",

    // Tab 6: Dynamic Control
    "tab6.header_title": "Dinamik Kapalı Çevrim Proses Kontrolü & Model Öngörülü Kontrol (MPC)",
    "tab6.header_desc": "Reaktör termal kapasitansı, geri beslemeli PID stabilizasyonu ve ufuk kaydırmalı MPC simülasyonu.",
    "tab6.cfg_title": "Kontrolör Yapılandırması",
    "tab6.ctrl_label": "Aktif Kontrol Mimarisi",
    "tab6.ctrl_mpc": "Model Öngörülü Kontrolör (MPC)",
    "tab6.ctrl_pid": "Endüstriyel Dijital PID Kontrolör",
    "tab6.ctrl_open": "Açık Çevrim (Sabit %55 Güç)",
    "tab6.sp_label": "Hedef Sıcaklık (10. dk Basamak)",
    "tab6.dist_label": "Nem Bozulması (30. dk)",
    "tab6.btn_run_ctrl": "60 Dakikalık Geçici Rejim Simülasyonu",
    "tab6.chart_title": "Canlı 60 Dakikalık Kapalı Çevrim Yanıt Eğrisi",

    // Tab 7: Economics & LCA
    "tab7.header_title": "Tekno-Ekonomik Değerlendirme (TEA) & ISO 14040/14044 LCA Karbon Analizi",
    "tab7.header_desc": "20 Yıllık İndirgenmiş Nakit Akışı (DCF), Guthrie Capex/Opex, Seviyelendirilmiş Biyo-Yağ Maliyeti ve Kapsam 1-2-3 karbon yutakları.",
    "tab7.market_title": "Piyasa ve Ticari Değerleme Parametreleri",
    "tab7.oil_price_label": "Biyo-Yağ Piyasa Fiyatı ($/kg)",
    "tab7.char_price_label": "Biyokömür Piyasa Fiyatı ($/kg)",
    "tab7.corc_price_label": "Karbon Giderme Kredisi Fiyatı ($/ton CO2)",
    "tab7.btn_calc_tea": "20 Yıllık TEA & LCA Profilini Hesapla",

    // Tab 8: Autopilot
    "tab8.header_title": "Tam Otonom Yapay Zeka Tesis Otopilotu & Denetim Kokpiti (V2.0)",
    "tab8.header_desc": "Kapalı çevrim otonom uçuş: Başlatma ön ısıtması, seyir takibi, nem adaptasyonu ve darbe-jet kendi kendini onarma.",
    "tab8.flight_title": "Uçuş Direktörü Kontrolü",
    "tab8.master_label": "Otopilot Ana Şalteri",
    "tab8.ap_engage": "OTONOM OTOPİLOTU DEVREYE AL",
    "tab8.ap_disengage": "OTOPİLOTU DEVREDEN ÇIKAR (MANUEL)",
    "tab8.dist_moist_label": "Enjekte Edilen Bozulma (Nem)",
    "tab8.inject_anomaly_label": "Uçuş Anomalisi Enjekte Et",
    "tab8.anom_none": "Nominal (Arıza Yok)",
    "tab8.anom_cyclone": "Siklon Dip Borusu Tıkanması",
    "tab8.anom_runaway": "Reaktör Termal Kaçak (>630°C)",
    "tab8.btn_mission": "4 Saatlik Stres Testi Görevini Başlat",
    "tab8.blackbox_title": "Canlı Karukutu Telemetrisi & Olay Akışı",
    "tab8.status_ready": "OTOPİLOT HAZIR",
    "tab8.m_temp_pv": "Reaktör Sıcaklığı (PV)",
    "tab8.m_feed_rate": "Besleme Helezon Hızı",
    "tab8.m_tsi": "Termal İndeks (TSI)",

    // Tab 9: IoT
    "tab9.gateways_title": "Uç Protokol Köprüleri & HIL",
    "tab9.modbus_label": "Modbus TCP Ağ Geçidi",
    "tab9.mqtt_label": "MQTT Sparkplug B Uç Aracısı",
    "tab9.opcua_label": "OPC-UA IEC 62541 Adres Alanı",
    "tab9.hil_sig_label": "HIL 4-20mA Sinyal Koşullandırma",
    "tab9.btn_hil_step": "HIL Saatini Adımla",
    "tab9.btn_modbus_poll": "Modbus Oku",
    "tab9.hil_fault_label": "HIL Döngü Hatası Ver (NAMUR NE 43)",
    "tab9.btn_fault_open": "Açık Devre (0mA)",
    "tab9.btn_fault_short": "Kısa Devre (24mA)",
    "tab9.btn_fault_clear": "Temizle",
    "tab9.reg_table_title": "Canlı Modbus Kayıt Tablosu (16-bit) & 4-20mA Akım Döngüleri",
    "tab9.th_address": "Adres",
    "tab9.th_tag": "Kayıt Etiketi / Adı",
    "tab9.th_raw": "Ham (16-bit)",
    "tab9.th_scaled": "Ölçeklenmiş Mühendislik Değeri",
    "tab9.th_type": "Tip",
    "tab9.poll_hint": "Kayıtları getirmek için 'Modbus Oku' butonuna tıklayın",

    // Tab 10: Fleet
    "tab10.corc_title": "CORC Karbon Piyasası & Filo Sevkiyatı",
    "tab10.corc_spot_label": "Puro.earth CORC Spot Fiyatı",
    "tab10.oil_spot_label": "Biyo-Yağ Piyasa Fiyatı",
    "tab10.agri_dispatch_label": "Mevsimsel Tarımsal Sevkiyat",
    "tab10.btn_autumn": "Sonbahar (Zeytin)",
    "tab10.btn_summer": "Yaz (Saman)",
    "tab10.btn_spring": "İlkbahar (Çam)",
    "tab10.exec_opt_label": "Arbitraj ve Şebeke Optimizasyonunu Çalıştır",
    "tab10.btn_arbitrage": "Arbitrajı Çalıştır",
    "tab10.btn_solar": "24s Güneş Simülasyonu",
    "tab10.hubs_title": "Merkezi Olmayan Bölgesel Tesis Düğümleri (3 Aktif Merkez)",
    "tab10.m_total_feed": "Toplam Filo Beslemesi",
    "tab10.m_total_oil": "Günlük Biyo-Yağ Hacmi",
    "tab10.m_total_carbon": "Günlük Karbon Yutakları",

    // Tab 11: 3D Spatial & Copilot
    "tab11.spatial_title": "3B WebGL Holografik Mekansal Dijital İkiz",
    "tab11.btn_particles": "Akış Parçacıkları",
    "tab11.btn_reset_cam": "Görünümü Sıfırla",
    "tab11.spatial_hint": "[Döndürmek için Sürükleyin • Yakınlaştırmak için Kaydırın • Telemetri için Tıklayın]",
    "tab11.drl_title": "Derin RL PPO Doğrusal Olmayan Politika (BioPlant-v1)",
    "tab11.btn_drl_step": "Politikayı Adımla",
    "tab11.btn_drl_train": "PPO Eğitimi Yap",
    "tab11.copilot_title": "Yapay Zeka SCADA Operatör Copilot",
    "tab11.copilot_badge": "SOP & P&ID AKTİF",
    "tab11.copilot_welcome": "Hoş geldiniz operatör. Tüm tesis P&ID şemaları, SOP kılavuzları ve SIL-2 güvenlik kilitleri üzerinde indekslendim. Operasyonel bir soru sorun veya aşağıdaki hazır komutları seçin.",
    "tab11.quick_cyclone": "Siklon Basınç Farkı",
    "tab11.quick_moisture": "Nem Dalgalanması",
    "tab11.quick_startup": "Ön Isıtma SOP",
    "tab11.quick_emergency": "SIL-2 Güvenli Park",
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

  // Apply smooth transition animation to main content
  const mainContent = document.querySelector('.main-content');
  if (mainContent) {
    mainContent.classList.remove('lang-fade-transition');
    void mainContent.offsetWidth; // Trigger reflow
    mainContent.classList.add('lang-fade-transition');
  }

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

  // Dispatch custom language change event for dynamic JS rerenders
  window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
}
