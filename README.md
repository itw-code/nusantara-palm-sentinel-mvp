# 🌿 Nusantara Palm-Estate Operations Planner & Sentinel

An interactive, scientifically-backed Operational Agritech Dashboard for Indonesian palm oil plantations. It optimizes day-to-day estate operations (Fertilizing, Harvesting, and Spraying) using real-time and historical satellite meteorological and soil moisture metrics.

## 🚀 Getting Started

1. **Install Dependencies:**
   `ash
   pip install -r requirements.txt
   `

2. **Run the Dashboard:**
   `ash
   streamlit run app.py
   `

3. **Run Unit Tests:**
   `ash
   python -m unittest tests/test_agronomy.py
   `

## ⚙️ Features
* **Dual-Language Interface:** Seamless toggling between Bahasa Indonesia (Default) and English.
* **Operations Planner:** Exposes custom threshold controls for Fertilizing, Harvesting, and Pesticide/Herbicide Spraying.
* **Forecast Accuracy Audits:** Automatically verifies forecasts against actual satellite observations (last 7-30 days) utilizing the Open-Meteo Archive API.
* **Financial Benefits Calculator:** Pulls real-time global Crude Palm Oil (CPO) prices from the World Bank API to estimate annual cost savings per hectare.
* **Scientific Foundations:** Features LaTeX math displays for model errors, wash-off equations, and wind-drift coefficients.
