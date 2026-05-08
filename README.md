# 📡 5G Signal Visualization Dashboard

> 🚀 **"Code with AI" Geek Exploration Challenge** - 5G Signal Data Visualization

An interactive web-based dashboard for visualizing 5G signal measurement data, built with **Streamlit**, **PyDeck**, and **Plotly**.

## ✨ Features

### 🟢 Basic Level (Completed)

- **Data Loading**: Reads 5G signal data from CSV using pandas
- **2D Signal Map**: Interactive scatter map with points color-coded by RSRP signal strength
  - 🟢 Green: Excellent signal (>-90dBm)
  - 🫒 Yellow-Green: Good signal (-90 to -100dBm)
  - 🟠 Orange: Fair signal (-100 to -110dBm)
  - 🔴 Red: Poor signal (<=-110dBm)
- **Data Overview Charts**:
  - Bar chart: Base station count by frequency band
  - Pie chart: Terminal type distribution (Smartphone, CPE, IoT)
  - Histogram: RSRP signal strength distribution
  - Box plot: Download rate by frequency band

### 🟡 Advanced Level (Completed)

- **Sidebar Filters** (Real-time linked):
  - Multi-select for frequency band (n28, n41, n78)
  - Range slider for RSRP values
  - Multi-select for terminal type
  - Range slider for SINR values
  - All filters instantly update the map and charts

- **3D Visualization**:
  - 3D column map where column height represents download rate
  - Color-coded by signal strength on dark map theme
  - Interactive tilt and rotation

- **Engineering Quality**:
  - Comprehensive code documentation and docstrings
  - 17 unit tests covering all core functions
  - Modular architecture with separated utilities

## 📸 Screenshots

See the `screenshots/` directory for application runtime screenshots:

- `screenshot_1_overview.png` - Dashboard overview with 2D map and statistics
- `screenshot_2_filters.png` - Sidebar filter controls demonstration
- `screenshot_3_3dmap.png` - 3D column visualization

## 🛠️ Installation & Running

### Prerequisites

- Python 3.8+
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- streamlit >= 1.30.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- pydeck >= 0.8.0
- plotly >= 5.18.0

### Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`.

### Run Tests

```bash
python tests/test_app.py
```

Or with pytest:

```bash
pytest tests/test_app.py -v
```

## 📁 Project Structure

```
5g-dashboard/
├── app.py              # Main Streamlit application
├── utils.py            # Core utility functions (data loading, color mapping)
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── AI_PROMPTS.md       # AI interaction log
├── data/
│   └── signal_samples.csv  # 5G signal measurement data
├── tests/
│   ├── __init__.py
│   └── test_app.py     # Unit tests (17 tests)
└── screenshots/
    ├── screenshot_1_overview.png
    ├── screenshot_2_filters.png
    └── screenshot_3_3dmap.png
```

## 📊 Data Description

The dataset (`data/signal_samples.csv`) contains 500 simulated 5G drive test records with:

| Column | Description |
|--------|-------------|
| Latitude | GPS latitude coordinate |
| Longitude | GPS longitude coordinate |
| CellID | Base station cell identifier |
| Band | 5G frequency band (n28, n41, n78) |
| RSRP_dBm | Reference Signal Received Power (dBm) |
| SINR_dB | Signal-to-Interference-plus-Noise Ratio (dB) |
| TerminalType | Device type (Smartphone, CPE, IoT) |
| Download_Mbps | Download speed (Mbps) |

## 🤖 AI Development

This project was developed using AI-assisted programming techniques. See `AI_PROMPTS.md` for the complete interaction log with the AI coding agent.

## 🏆 Contest Information

- **Contest**: besa-2026/code-with-ai-contest
- **Challenge**: 5G Signal Visualization Dashboard
- **Submission Tags**:
  - `basic-done` - Basic level completion
  - `advanced-done` - Advanced level completion

## 📄 License

This project is created for the "Code with AI" contest.
