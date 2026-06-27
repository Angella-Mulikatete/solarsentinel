# ☀️ SolarSentinel — Solar Plant Performance & Intelligence Dashboard

> **Hackathon Entry** | Python Data Visualisation Sprint  
> *Built with Python 3.11+, Pandas, Plotly, Dash · Deployed on Gunicorn*

---

## 📌 Overview

**SolarSentinel** is a production-grade interactive operations dashboard built on real solar plant telemetry data from two photovoltaic (PV) generating stations in India. It transforms raw inverter-level sensor readings into actionable intelligence — the kind of display you'd find in a renewable energy operations room.

The dashboard enables plant operators and analysts to:
- Monitor real-time power generation trends across inverters
- Identify underperforming inverters before they cause yield loss
- Understand how environmental conditions (irradiance, temperature) drive output
- Track daily and cumulative energy yield against plant capacity

---

## 📊 Dataset

**Source:** [Solar Power Generation Data — Kaggle](https://www.kaggle.com/datasets/anikannal/solar-power-generation-data)  
**Origin:** Two real solar PV generating stations in India  
**Period:** 34 days of operational sensor readings  

### Files Used
| File | Description |
|------|-------------|
| `Plant_1_Generation_Data.csv` | DC/AC power output per inverter, Plant 1 |
| `Plant_1_Weather_Sensor_Data.csv` | Irradiance, ambient & module temperature, Plant 1 |
| `Plant_2_Generation_Data.csv` | DC/AC power output per inverter, Plant 2 |
| `Plant_2_Weather_Sensor_Data.csv` | Irradiance, ambient & module temperature, Plant 2 |

### Key Columns
| Column | Description |
|--------|-------------|
| `DATE_TIME` | Timestamp of observation (15-min intervals) |
| `PLANT_ID` | Unique plant identifier |
| `SOURCE_KEY` | Unique inverter identifier |
| `DC_POWER` | DC power output (kW) |
| `AC_POWER` | AC power output (kW) |
| `DAILY_YIELD` | Energy produced today (kWh) |
| `TOTAL_YIELD` | Cumulative energy produced (kWh) |
| `IRRADIATION` | Solar irradiance (W/m²) |
| `AMBIENT_TEMPERATURE` | Ambient air temperature (°C) |
| `MODULE_TEMPERATURE` | Panel surface temperature (°C) |

---

## 🖥️ Dashboard Views

### 1. 🏭 Plant Overview
Live KPIs and plant-level generation summary:
- Total AC/DC power generated
- Daily yield trend (line chart)
- Generation vs irradiance (dual-axis chart)
- Plant comparison (Plant 1 vs Plant 2)

### 2. ⚡ Inverter Performance Grid
Inverter-level health monitoring:
- Heatmap of all inverters by output (spot underperformers instantly)
- DC-to-AC conversion efficiency per inverter
- Inverter ranking chart (best to worst performers)
- Drill-down: select any inverter to see its full time series

### 3. 🌤️ Weather Impact Analysis
Environmental correlation with power output:
- Irradiance vs AC Power scatter plot
- Ambient temperature vs module temperature over time
- Cloud/shading detection (irradiance drop correlation)
- Performance ratio over the 34-day period

### 4. 📈 Yield & Efficiency Tracker
Cumulative production insights:
- Cumulative yield over time (both plants)
- DC-to-AC efficiency loss trend
- Peak production hours heatmap (hour of day × day of week)
- Daily performance summary table

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| Data Processing | Pandas, NumPy |
| Visualisation | Plotly Express, Plotly Graph Objects |
| Dashboard Framework | Dash 2.x (multi-page) |
| Styling | Dash Bootstrap Components (dark ops theme) |
| WSGI Server | Gunicorn |
| Deployment | Render.com (free tier) |

---

## 📁 Project Structure

```
solar-sentinel/
├── app.py                    # Entry point — Dash app + Gunicorn server
├── pages/
│   ├── plant_overview.py     # View 1: Plant-level KPIs & trends
│   ├── inverter_grid.py      # View 2: Inverter health heatmap
│   ├── weather_analysis.py   # View 3: Environmental correlation
│   └── yield_tracker.py      # View 4: Cumulative yield & efficiency
├── data/
│   ├── loader.py             # Data ingestion & cleaning pipeline
│   └── *.csv                 # Raw dataset files (downloaded from Kaggle)
├── components/
│   ├── navbar.py             # Top navigation bar
│   └── kpi_card.py           # Reusable KPI metric card component
├── assets/
│   └── style.css             # Global dark ops-room theme
├── requirements.txt          # Python dependencies
├── Procfile                  # Gunicorn start command for Render
├── render.yaml               # Render.com deployment config
└── README.md                 # This file
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/solar-sentinel.git
cd solar-sentinel
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the Dataset
Download the dataset from [Kaggle](https://www.kaggle.com/datasets/anikannal/solar-power-generation-data) and place all 4 CSV files into the `data/` folder.

### 5. Run Locally (Development)
```bash
python app.py
```
Open http://localhost:8050 in your browser.

### 6. Run with Gunicorn (Production)
```bash
gunicorn app:server --workers 2 --threads 4 --bind 0.0.0.0:8050
```

---

## ☁️ Deployment (Render.com)

1. Push this repository to GitHub
2. Go to [Render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render will auto-detect the `render.yaml` config
5. Your dashboard will be live at `https://solar-sentinel.onrender.com`

> **No localhost screenshots.** The dashboard is deployed at a real public URL as required by the hackathon brief.

---

## 📋 Requirements

See [`requirements.txt`](./requirements.txt) for the full list. Key packages:

```
dash>=2.14.0
plotly>=5.18.0
pandas>=2.1.0
numpy>=1.26.0
dash-bootstrap-components>=1.5.0
gunicorn>=21.2.0
```

---

## 🏆 Hackathon Criteria Met

| Criterion | Status |
|-----------|--------|
| Python 3.11+ | ✅ |
| Pandas data processing | ✅ |
| Plotly visualisations | ✅ |
| Dash interactive framework | ✅ |
| WSGI server (Gunicorn) | ✅ |
| Real public URL | ✅ Render.com |
| No localhost screenshots | ✅ |
| No full-page reloads | ✅ Dash callbacks |
| 3+ distinct interactive views | ✅ 4 views |
| Engineering operations room aesthetic | ✅ Dark ops theme |
| Real (not simulated) dataset | ✅ Kaggle India Solar Plant |

