# BIOPLANT AI - Digital Twin & Autonomous Platform
# Comprehensive User Manual / Kapsamlı Kullanıcı Kılavuzu (V2.0)

> **Platform Version**: `2.0.0`  
> **Status**: Production Qualified (100/100 Tests Passing)  
> **Web GUI**: `http://127.0.0.1:8000/`  
> **Repository**: [https://github.com/cagataykilicc/ai-biomass-plant](https://github.com/cagataykilicc/ai-biomass-plant)

---

## 📑 Table of Contents / İçindekiler

1. [English Edition](#-english-edition)
   - [1. System Architecture & Overview](#1-system-architecture--overview)
   - [2. Quick Start & Installation](#2-quick-start--installation)
   - [3. Interactive Web GUI - 8 Operational Modules](#3-interactive-web-gui---8-operational-modules)
   - [4. CLI Runners & Mission Dashboard](#4-cli-runners--mission-dashboard)
   - [5. Zero-Dependency REST API Reference](#5-zero-dependency-rest-api-reference)
   - [6. Feedstock Library & Proximate/Ultimate Analyses](#6-feedstock-library--proximateultimate-analyses)
   - [7. Safety Standards, SIL-2 & LOTO Protocols](#7-safety-standards-sil-2--loto-protocols)
   - [8. Troubleshooting & FAQ](#8-troubleshooting--faq)
2. [Türkçe Bölüm](#-türkçe-bölüm)
   - [1. Sistem Mimarisi ve Genel Bakış](#1-sistem-mimarisi-ve-genel-bakış)
   - [2. Hızlı Başlangıç ve Kurulum](#2-hızlı-başlangıç-ve-kurulum)
   - [3. Etkileşimli Web Arayüzü - 8 Temel Modül](#3-etkileşimli-web-arayüzü---8-temel-modül)
   - [4. Komut Satırı (CLI) ve Görev Kontrolü](#4-komut-satırı-cli-ve-görev-kontrolü)
   - [5. REST API Referansı ve Entegrasyon](#5-rest-api-referansı-ve-entegrasyon)
   - [6. Hammadde Kütüphanesi ve Analiz Değerleri](#6-hammadde-kütüphanesi-ve-analiz-değerleri)
   - [7. Güvenlik Standartları, SIL-2 ve LOTO Protokolleri](#7-güvenlik-standartları-sil-2-ve-loto-protokolleri)
   - [8. Sorun Giderme ve SSS](#8-sorun-giderme-ve-sss)

---

# 🇬🇧 English Edition

## 1. System Architecture & Overview

**BIOPLANT AI** is an industrial-grade **Digital Twin and Autonomous Operations Platform** for thermochemical biomass pyrolysis, bio-oil recovery, biochar carbon sequestration, and energy co-generation.

```mermaid
flowchart LR
    subgraph INTAKE["1. Infeed & Drying"]
        A[Wet Biomass Hopper] --> B[Drum Dryer D-101]
        B --> C[Auger Feeder A-101]
    end

    subgraph REACTOR["2. Pyrolysis & Heat Integration"]
        C --> D[Pyrolysis Reactor R-101]
        E[Combustor B-101] -->|Flue Gas Heat Recovery| D
        E -->|Exhaust Waste Heat| B
    end

    subgraph SEPARATION["3. Multi-Stage Product Recovery"]
        D --> F[Cyclone Separator C-101]
        F -->|Biochar Fraction| G[Biochar Bin]
        F -->|Hot Vapors| H[Quench Condenser HX-102]
        H -->|Bio-Oil Condensate| I[Storage Tank T-101]
        H -->|Non-Condensable Syngas| E
    end

    subgraph AI_BRAIN["4. AI Brain & Autonomous Supervisory Loop"]
        J[Telemetry Ingestion] --> K[6 Virtual Soft Sensors (95% UQ)]
        K --> L[Tri-Layer FDD Diagnostics]
        L --> M[NSGA-II Pareto & TOPSIS Optimizer]
        M --> N[MPC Closed-Loop Controller]
        N -->|Actuator Dispatch| C
        N -->|Firing Control| E
    end
```

### Key Technical Capabilities
* **Full Mass, Elemental & Energy Balance Closure**: First-principles physical conservation (<0.01% closure residual).
* **Physics-Informed ML Surrogates**: Gradient Boosting ensemble ($R^2 = 0.9981$) constrained via Simplex Euclidean projection.
* **Autonomous Autopilot FSM**: 5-state supervisory state machine (`STARTUP_PREHEAT`, `AUTONOMOUS_CRUISE`, `DISTURBANCE_ADAPTATION`, `FAULT_MITIGATION`, `EMERGENCY_SAFE_PARK`).
* **Techno-Economic (TEA) & ISO 14040/14044 LCA**: Guthrie Capital Costing, 20-year DCF ($NPV = +\$657,833$, $IRR = 24.88\%$, $LCOB = \$0.3534/\text{kg}$), and Net Carbon Negative intensity ($-40.88\text{ g CO}_2\text{eq/MJ}$).

---

## 2. Quick Start & Installation

### Prerequisites
* Python 3.11+ (Python 3.14 recommended)
* Web Browser (Chrome, Edge, Firefox, Safari)

### Launching the Digital Twin Web Platform
```bash
# Clone the repository
git clone https://github.com/cagataykilicc/ai-biomass-plant.git
cd ai-biomass-plant

# Start the web platform on port 8000
python -m src.web.run_server --port 8000 --open-browser
```
Open **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser.

---

## 3. Interactive Web GUI - 8 Operational Modules

The Web GUI is organized into 8 tabs styled with a modern Dark Glassmorphism design system:

| Tab # | Module Name | Core Features | Key Outputs |
| :--- | :--- | :--- | :--- |
| **1** | **Flowsheet & Process Twin** | Interactive P&ID SVG, sliders for $T_{reactor}$, $\dot{m}_{feed}$, moisture, and heating rate | Product yields (wt%), syngas/bio-oil kg/h, Thermal Self-Sufficiency Index (TSI) |
| **2** | **Inferential Soft Sensors** | 6 virtual gauges with 95% Bayesian Confidence Intervals | Bio-oil TAN, moisture, HHV, syngas LHV, biochar yield, real-time TSI |
| **3** | **Multiobjective Optimization** | Interactive 2D Pareto Canvas & TOPSIS MCDM profile selector | Non-dominated trade-off points, maximum profit & thermal efficiency setpoints |
| **4** | **Tri-Layer Diagnostics** | Injects equipment faults, evaluates residuals, Isolation Forest & PCA $Q/T^2$ | Anomaly score, root-cause diagnosis, NFPA/SIL-2 automated safety interlocks |
| **5** | **Predictive Maintenance** | Archard wear, thermal spalling, filter blinding, and condenser fouling models | Asset health index, 95% Remaining Useful Life (RUL), prescriptive work orders & LOTO |
| **6** | **Dynamic Control (MPC)** | Discrete PID with anti-windup vs Model Predictive Controller | 60-min closed-loop dynamic trajectory, IAE, ITAE, settling time, overshoot |
| **7** | **TEA & LCA Carbon** | Guthrie equipment costing, 20-yr DCF valuation & ISO 14040/14044 LCA | Net Present Value (NPV), IRR, LCOB ($/kg), Scope 1-2-3 GHG balance, CORC credits |
| **8** | **Autopilot Cockpit (V2.0)** | Closed-loop 2.0s supervisory FSM, disturbance injection, flight director | Real-time FSM mode badge, blackbox event stream, 4-hour mission qualification |

---

## 4. CLI Runners & Mission Dashboard

Execute platform capabilities directly from the terminal:

```bash
# 1. Run 4-Hour Autonomous Mission Qualification
python -m src.autonomous.run_autopilot --mission

# 2. Run Techno-Economic & LCA Carbon Accounting
python -m src.economics.run_economics --feedstock olive_pomace

# 3. Run Dynamic Process Control Benchmark (Open-Loop vs PID vs MPC)
python -m src.control.run_control --benchmark

# 4. Run Predictive Maintenance & RUL Prognostics
python -m src.maintenance.run_maintenance --operating-hours 4500

# 5. Run Tri-Layer Fault Diagnostics Simulation
python -m src.diagnostics.run_diagnostics --simulate-fault cyclone_blockage

# 6. Run Complete Test Suite (100 Tests)
pytest tests/ -v
```

---

## 5. Zero-Dependency REST API Reference

The digital twin includes an asynchronous, multi-threaded JSON REST API:

### `POST /api/simulate`
* **Request**:
  ```json
  {
    "feedstock": "olive_pomace",
    "reactor_temp_c": 500.0,
    "feed_rate_kg_h": 100.0,
    "moisture_pct": 12.0,
    "yield_mode": "hybrid"
  }
  ```
* **Response**:
  ```json
  {
    "feedstock": "Olive Pomace",
    "product_rates_kg_h": { "bio_oil": 48.1, "biochar": 27.4, "syngas": 24.5 },
    "energy_and_heat": { "tsi_pct": 111.3, "is_self_sufficient": true }
  }
  ```

### `POST /api/autopilot/step`
* **Request**:
  ```json
  { "moisture": 14.0, "fault": "none", "setpoint": 500.0, "reset": false }
  ```
* **Response**:
  ```json
  {
    "plant_state": { "reactor_temp_c": 498.5, "feed_rate_kg_h": 100.0, "tsi_pct": 112.1 },
    "command": { "fsm_state": "AUTONOMOUS_CRUISE", "burner_duty_pct": 74.2, "action_summary": "MPC_TRACKING_TARGET_500C" }
  }
  ```

---

## 6. Feedstock Library & Proximate/Ultimate Analyses

| Feedstock Name | Ash (wt%) | Volatiles (wt%) | Fixed Carbon (wt%) | Carbon C (%) | Hydrogen H (%) | Oxygen O (%) | HHV (MJ/kg) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Olive Pomace** | 4.2 | 72.8 | 23.0 | 51.4 | 6.2 | 40.8 | **20.45** |
| **Pine Sawdust** | 0.8 | 82.5 | 16.7 | 50.5 | 6.1 | 42.8 | **19.82** |
| **Wheat Straw** | 6.8 | 75.1 | 18.1 | 46.2 | 5.8 | 46.4 | **17.65** |
| **Rice Husk** | 16.5 | 63.2 | 20.3 | 39.8 | 5.2 | 41.5 | **15.20** |

---

## 7. Safety Standards, SIL-2 & LOTO Protocols

> [!IMPORTANT]
> - **NFPA 86 (Standard for Ovens and Furnaces)**: Requires automated nitrogen purge before burner reignition.
> - **SIL-2 Interlocks**: Over-temperature limit ($>650^\circ\text{C}$) cuts biomass feed and closes fuel gas solenoid within $250\text{ ms}$.
> - **OSHA 1910.147 LOTO**: Work orders generated by Module 5 specify zero-energy mechanical lockouts before maintenance.

---

## 8. Troubleshooting & FAQ

### Q1: The browser shows "Connection Refused" when visiting port 8000.
**Fix**: Ensure the background server is running. Run:
```powershell
python -m src.web.run_server --port 8000
```

### Q2: How do I run the full 4-hour qualification mission without waiting 4 hours?
**Fix**: The simulation runs faster-than-real-time numerically. A 4-hour mission completes in ~2 seconds:
```powershell
python -m src.autonomous.run_autopilot --mission
```

---
---

# 🇹🇷 Türkçe Bölüm

## 1. Sistem Mimarisi ve Genel Bakış

**BIOPLANT AI**, termokimyasal biyokütle pirolizi, biyo-yağ geri kazanımı, biyokömür (biochar) karbon tutulumu ve kojenerasyon için geliştirilmiş endüstriyel standartta bir **Dijital İkiz ve Otonom Tesis Yönetim Platformudur**.

```mermaid
flowchart LR
    subgraph BESLEME["1. Hammadde Besleme ve Kurutma"]
        A[Biyokütle Besleme Bunkeri] --> B[Döner Tambur Kurutucu D-101]
        B --> C[Vidalı Besleyici A-101]
    end

    subgraph REAKTOR["2. Piroliz Reaktörü ve Isı Entegrasyonu"]
        C --> D[Piroliz Reaktörü R-101]
        E[Sentez Gazı Yakıcısı B-101] -->|Baca Gazı Isı Geri Kazanımı| D
        E -->|Atık Isı Entegrasyonu| B
    end

    subgraph AYRISTIRMA["3. Ürün Geri Kazanım Üniteleri"]
        D --> F[Gaz Siklonu C-101]
        F -->|Biyokömür Ayrışımı| G[Biyokömür Deposu]
        F -->|Sıcak Piroliz Buharı| H[Şok Kondenser HX-102]
        H -->|Sıvı Biyo-Yağ| I[Depolama Tankı T-101]
        H -->|Yoğuşmayan Sentez Gazı| E
    end

    subgraph YAPAY_ZEKA["4. Yapay Zeka ve Otonom Kontrol Döngüsü"]
        J[Sensör Telemetri Verisi] --> K[6 Sanal Yumuşak Sensör (%95 UQ)]
        K --> L[Üç Katmanlı FDD Arıza Teşhisi]
        L --> M[NSGA-II Pareto & TOPSIS Optimizasyonu]
        M --> N[MPC Dinamik Süreç Kontrolörü]
        N -->|Besleme Hızı Kontrolü| C
        N -->|Brülör Alev Kontrolü| E
    end
```

### Öne Çıkan Teknik Özellikler
* **Kütle, Elementel ve Enerji Denkliği**: Birinci prensipler termodinamik korunumu (<%0.01 kalıntı hatası).
* **Fizik Destekli Makine Öğrenmesi (PINN)**: Gradient Boosting topluluk modeli ($R^2 = 0.9981$), Simplex Öklid projeksiyonu ile kütle korunumlu.
* **5 Durumlu Otonom Otopilot (FSM)**: `STARTUP_PREHEAT` (Ön Isıtma), `AUTONOMOUS_CRUISE` (Otonom Seyir), `DISTURBANCE_ADAPTATION` (Nem Bozulması Uyarlaması), `FAULT_MITIGATION` (Arıza Giderme - Darbeli Azot Geri Üfleme), `EMERGENCY_SAFE_PARK` (Acil Güvenli Kapatma).
* **Tekno-Ekonomik (TEA) ve ISO 14040/14044 LCA**: Guthrie ekipman maliyetlendirmesi, 20 yıllık İndirgenmiş Nakit Akışı (NPV = +\$657,833, IRR = %24.88, Biyo-Yağ Maliyeti = \$0.3534/kg) ve Net Negatif Karbon Salımı (-40.88 g CO2eq/MJ).

---

## 2. Hızlı Başlangıç ve Kurulum

### Gereksinimler
* Python 3.11 veya üzeri (Python 3.14 önerilir)
* Modern Web Tarayıcısı (Chrome, Edge, Firefox, Safari)

### Dijital İkiz Web Platformunu Başlatma
```bash
# Depoyu klonlayın
git clone https://github.com/cagataykilicc/ai-biomass-plant.git
cd ai-biomass-plant

# Web sunucusunu 8000 portunda başlatın
python -m src.web.run_server --port 8000 --open-browser
```
Tarayıcınızdan **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** adresini ziyaret edin.

---

## 3. Etkileşimli Web Arayüzü - 8 Temel Modül

Koyu Cam Efektli (Dark Glassmorphism) web panelinde bulunan 8 operasyonel modül:

| Modül # | Modül Başlığı | Temel İşlevler | Çıktı ve Göstergeler |
| :--- | :--- | :--- | :--- |
| **1** | **Akış Şeması ve Proses İkizi** | Etkileşimli P&ID şeması; sıcaklık, besleme debisi, nem ayar sürgüleri | Ürün verimleri (% kütle), ürün akış hızları (kg/sa), Termal Kendi Kendine Yetebilirlik (TSI) |
| **2** | **Çıkarımsal Yumuşak Sensörler** | Laboratuvar ölçümlerini simüle eden 6 sanal sensör (%95 Güven Aralığı) | Biyo-yağ Toplam Asit Numarası (TAN), nemi, ısıl değeri (HHV), sentez gazı LHV, anlık TSI |
| **3** | **Çok Amaçlı Optimizasyon** | Etkileşimli 2D Pareto eğrisi ve TOPSIS karar verme aracı | Baskın olmayan çözüm kümesi, maksimum kâr ve maksimum termal verim çalışma noktaları |
| **4** | **Üç Katmanlı Arıza Teşhisi** | Ekipman arızası simülasyonu, Kütle artıkları, Isolation Forest, PCA $Q/T^2$ | Anomali skoru, kök neden analizi, NFPA/SIL-2 otomatik emniyet kilitleri |
| **5** | **Kestirimci Bakım ve RUL** | Archard aşınması, refrakter termal dökülmesi, filtre tıkanması, boru korozyonu | Ekipman sağlık endeksi, Kalan Faydalı Ömür (RUL saat), reçeteli iş emirleri ve LOTO |
| **6** | **Dinamik Süreç Kontrolü (MPC)** | Dijital PID (Anti-windup) ile Model Öngörülü Kontrolör (MPC) karşılaştırması | 60 dakikalık dinamik yörünge, IAE, ITAE, aşım ve yerleşme süreleri |
| **7** | **Tekno-Ekonomik ve LCA Karbon** | Guthrie CAPEX/OPEX, 20 yıllık DCF, ISO 14040/14044 LCA Karbon Analizi | Net Bugünkü Değer (NPV), İç Kârlılık Oranı (IRR), Kapsam 1-2-3 salımları, CORC gelirleri |
| **8** | **Otonom Otopilot Kokpiti (V2.0)** | 2.0s döngülü otonom FSM kontrolü, arıza self-healing, görev yöneticisi | Canlı FSM durum rozeti, kara kutu olay akışı, 4 saatlik stres testi çalıştırma |

---

## 4. Komut Satırı (CLI) ve Görev Kontrolü

Terminal üzerinden tüm modülleri doğrudan çalıştırabilirsiniz:

```bash
# 1. 4 Saatlik Otonom Görev Yeterlilik Testini Çalıştırma
python -m src.autonomous.run_autopilot --mission

# 2. Tekno-Ekonomik ve LCA Karbon Analizi Raporu Oluşturma
python -m src.economics.run_economics --feedstock olive_pomace

# 3. Dinamik Kontrolör Kıyaslama Testi (Açık Çevrim vs PID vs MPC)
python -m src.control.run_control --benchmark

# 4. Kestirimci Bakım ve Kalan Ömür Analizi
python -m src.maintenance.run_maintenance --operating-hours 4500

# 5. Üç Katmanlı Arıza Teşhis Simülasyonu
python -m src.diagnostics.run_diagnostics --simulate-fault cyclone_blockage

# 6. Tüm Birim Testleri Çalıştırma (100 Test)
pytest tests/ -v
```

---

## 5. REST API Referansı ve Entegrasyon

Platform, harici SCADA veya MES sistemleri ile haberleşebilen hafif bir JSON REST API sunar:

### `POST /api/simulate`
* **İstek Gövdesi**:
  ```json
  {
    "feedstock": "olive_pomace",
    "reactor_temp_c": 500.0,
    "feed_rate_kg_h": 100.0,
    "moisture_pct": 12.0,
    "yield_mode": "hybrid"
  }
  ```
* **Yanıt Gövdesi**:
  ```json
  {
    "feedstock": "Olive Pomace",
    "product_rates_kg_h": { "bio_oil": 48.1, "biochar": 27.4, "syngas": 24.5 },
    "energy_and_heat": { "tsi_pct": 111.3, "is_self_sufficient": true }
  }
  ```

### `POST /api/autopilot/step`
* **İstek Gövdesi**:
  ```json
  { "moisture": 14.0, "fault": "none", "setpoint": 500.0, "reset": false }
  ```
* **Yanıt Gövdesi**:
  ```json
  {
    "plant_state": { "reactor_temp_c": 498.5, "feed_rate_kg_h": 100.0, "tsi_pct": 112.1 },
    "command": { "fsm_state": "AUTONOMOUS_CRUISE", "burner_duty_pct": 74.2, "action_summary": "MPC_TRACKING_TARGET_500C" }
  }
  ```

---

## 6. Hammadde Kütüphanesi ve Analiz Değerleri

| Hammadde Türü | Kül (% kuru) | Uçucu Madde (%) | Sabit Karbon (%) | C (%) | H (%) | O (%) | Isıl Değer HHV (MJ/kg) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Zeytin Prinası (Olive Pomace)** | 4.2 | 72.8 | 23.0 | 51.4 | 6.2 | 40.8 | **20.45** |
| **Çam Talaşı (Pine Sawdust)** | 0.8 | 82.5 | 16.7 | 50.5 | 6.1 | 42.8 | **19.82** |
| **Buğday Samanı (Wheat Straw)** | 6.8 | 75.1 | 18.1 | 46.2 | 5.8 | 46.4 | **17.65** |
| **Pirinç Kavuzu (Rice Husk)** | 16.5 | 63.2 | 20.3 | 39.8 | 5.2 | 41.5 | **15.20** |

---

## 7. Güvenlik Standartları, SIL-2 ve LOTO Protokolleri

> [!IMPORTANT]
> - **NFPA 86 Standardı**: Brülörün her yeniden ateşlenmesinden önce minimum 3 dakika inert azot süpürmesi zorunludur.
> - **SIL-2 Acil Durum Kilitleri**: Reaktör sıcaklığı $650^\circ\text{C}$ üzerine çıktığında biyo-kütle beslemesi ve yakıt gazı vanası $250\text{ ms}$ içinde kesilir.
> - **OSHA 1910.147 LOTO**: Modül 5 tarafından üretilen iş emirleri, bakım öncesinde sıfır enerji kilitleme/etiketleme adımlarını içerir.

---

## 8. Sorun Giderme ve SSS

### S1: Tarayıcıda `http://127.0.0.1:8000/` adresine girerken bağlantı hatası alıyorum.
**Çözüm**: Arka plandaki Python web sunucusunun çalıştığından emin olun:
```powershell
python -m src.web.run_server --port 8000
```

### S2: 4 saatlik otonom stres testi simülasyonu gerçekte 4 saat mi sürer?
**Çözüm**: Hayır, simülasyon diferansiyel denklemleri sayısal olarak hızlandırılmış sürede çözer. 4 saatlik tam görev testi yaklaşık 2 saniyede tamamlanır:
```powershell
python -m src.autonomous.run_autopilot --mission
```

### S3: Web arayüzünde "Arıza Teşhis" simülasyonu yaptıktan sonra sistemi nasıl normale döndürebilirim?
**Çözüm**: Arıza seçim menüsünden **"Nominal / Arıza Yok"** seçeneğini işaretleyip tekrar "Teşhis Çalıştır" butonuna basmanız yeterlidir.

---
*(C) 2026 BIOPLANT AI Team. Licensed under the MIT License.*
