import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import plotly.express as px
import datetime
from agronomy import calculate_feasibility, DEFAULT_CONFIG

st.set_page_config(page_title="Nusantara Palm-Estate Sentinel", page_icon="🌿", layout="wide")

# Custom Green Agritech Theme styling
st.markdown("""
<style>
    .reportview-container { background: #f0f4f1; }
    .main .block-container { padding-top: 2rem; }
    .card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border-left: 5px solid #2e7d32;
    }
    .score-badge-green {
        background-color: #e8f5e9; color: #2e7d32; padding: 4px 8px; border-radius: 8px; font-weight: bold;
    }
    .score-badge-yellow {
        background-color: #fffde7; color: #f57f17; padding: 4px 8px; border-radius: 8px; font-weight: bold;
    }
    .score-badge-red {
        background-color: #ffebee; color: #c62828; padding: 4px 8px; border-radius: 8px; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

LOCALES = {
    "Bahasa Indonesia": {
        "title": "🌿 Nusantara Palm-Estate Operations Planner",
        "subtitle": "Optimalkan kegiatan operasional harian (Pemupukan, Panen, Penyemprotan) berdasarkan indikator cuaca satelit & kelembaban tanah.",
        "estate_controls": "🌿 Kontrol Perkebunan",
        "location_selection": "Pemilihan Lokasi",
        "preset_estates": "Preset Perkebunan",
        "custom_coordinates": "Koordinat Kustom",
        "select_estate": "Pilih Perkebunan",
        "latitude": "Lintang (Latitude)",
        "longitude": "Bujur (Longitude)",
        "agronomic_params": "⚙️ Parameter Agronomi",
        "fert_settings": "Pengaturan Pemupukan",
        "harv_settings": "Pengaturan Logistik Panen",
        "spray_settings": "Pengaturan Penyemprotan Kimia",
        "max_rain_runoff": "Curah Hujan Maksimal Runoff (mm)",
        "min_soil_moist": "Kelembaban Tanah Minimal (Vol %)",
        "max_sat_moist": "Kelembaban Saturated Maksimal",
        "impassable_mud_rain": "Curah Hujan Jalan Lumpur (mm)",
        "danger_wind_speed": "Kecepatan Angin Bahaya (km/jam)",
        "caution_wind": "Angin Peringatan (km/jam)",
        "critical_wind": "Angin Kritis (km/jam)",
        "wash_off_rain": "Curah Hujan Cuci Spray (mm)",
    },
    "English": {
        "title": "🌿 Nusantara Palm-Estate Operations Planner",
        "subtitle": "Optimize day-to-day operations (Fertilizing, Harvesting, Spraying) based on satellite weather & soil moisture indicators.",
        "estate_controls": "🌿 Estate Controls",
        "location_selection": "Location Selection",
        "preset_estates": "Preset Estates",
        "custom_coordinates": "Custom Coordinates",
        "select_estate": "Select Estate",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "agronomic_params": "⚙️ Agronomic Parameters",
        "fert_settings": "Fertilizer Application Settings",
        "harv_settings": "Harvesting Logistics Settings",
        "spray_settings": "Pest & Weed Spraying Settings",
        "max_rain_runoff": "Max Rain for Runoff (mm)",
        "min_soil_moist": "Min Soil Moisture (Vol %)",
        "max_sat_moist": "Max Saturated Moisture",
        "impassable_mud_rain": "Impassable Mud Rain (mm)",
        "danger_wind_speed": "Danger Wind Speed (km/h)",
        "caution_wind": "Caution Wind (km/h)",
        "critical_wind": "Critical Wind (km/h)",
        "wash_off_rain": "Wash-off Rain (mm)",
    }
}

# Language Selector
lang = st.sidebar.selectbox("🌐 Bahasa / Language", list(LOCALES.keys()), index=0)

# 1. Preset locations
PRESETS = {
    "Riau (Pekanbaru)": {"lat": 0.507, "lon": 101.447},
    "North Sumatra (Medan)": {"lat": 3.595, "lon": 98.672},
    "Central Kalimantan (Sampit)": {"lat": -2.535, "lon": 112.956}
}

st.sidebar.title(LOCALES[lang]["estate_controls"])
location_mode = st.sidebar.radio(LOCALES[lang]["location_selection"], [LOCALES[lang]["preset_estates"], LOCALES[lang]["custom_coordinates"]])

if location_mode == LOCALES[lang]["preset_estates"]:
    selected_preset = st.sidebar.selectbox(LOCALES[lang]["select_estate"], list(PRESETS.keys()))
    lat = PRESETS[selected_preset]["lat"]
    lon = PRESETS[selected_preset]["lon"]
else:
    lat = st.sidebar.number_input(LOCALES[lang]["latitude"], value=0.507, format="%.4f")
    lon = st.sidebar.number_input(LOCALES[lang]["longitude"], value=101.447, format="%.4f")

# 2. Configurable parameters
st.sidebar.subheader(LOCALES[lang]["agronomic_params"])
config = DEFAULT_CONFIG.copy()

with st.sidebar.expander(LOCALES[lang]["fert_settings"]):
    config["fert_runoff_rain"] = st.slider(LOCALES[lang]["max_rain_runoff"], 5.0, 30.0, DEFAULT_CONFIG["fert_runoff_rain"])
    config["fert_volatilization_moisture"] = st.slider(LOCALES[lang]["min_soil_moist"], 0.05, 0.30, DEFAULT_CONFIG["fert_volatilization_moisture"])
    config["fert_saturated_moisture"] = st.slider(LOCALES[lang]["max_sat_moist"], 0.35, 0.60, DEFAULT_CONFIG["fert_saturated_moisture"])

with st.sidebar.expander(LOCALES[lang]["harv_settings"]):
    config["harv_mud_rain"] = st.slider(LOCALES[lang]["impassable_mud_rain"], 5.0, 40.0, DEFAULT_CONFIG["harv_mud_rain"])
    config["harv_wind_speed"] = st.slider(LOCALES[lang]["danger_wind_speed"], 15.0, 45.0, DEFAULT_CONFIG["harv_wind_speed"])

with st.sidebar.expander(LOCALES[lang]["spray_settings"]):
    config["spray_drift_wind_med"] = st.slider(LOCALES[lang]["caution_wind"], 10.0, 25.0, DEFAULT_CONFIG["spray_drift_wind_med"])
    config["spray_drift_wind_high"] = st.slider(LOCALES[lang]["critical_wind"], 20.0, 40.0, DEFAULT_CONFIG["spray_drift_wind_high"])
    config["spray_wash_rain"] = st.slider(LOCALES[lang]["wash_off_rain"], 0.5, 10.0, DEFAULT_CONFIG["spray_wash_rain"])

# Title
st.title(LOCALES[lang]["title"])
st.markdown(LOCALES[lang]["subtitle"])

# CPO Live Price API
@st.cache_data(ttl=86400)
def fetch_cpo_price():
    try:
        url = "https://api.worldbank.org/v2/country/WLD/indicator/POILWSD?format=json&per_page=1&date=2025:2026"
        res = requests.get(url).json()
        price = float(res[1][0]["value"])
        if price > 0:
            return price, False
        return 850.0, True
    except Exception:
        return 850.0, True

# 3. Call APIs
@st.cache_data(ttl=3600)
def fetch_data(latitude, longitude):
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,precipitation_sum,wind_speed_10m_max,relative_humidity_2m_max,et0_fao_evapotranspiration&timezone=Asia%2FSingapore"
    soil_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=soil_moisture_0_to_7cm,soil_moisture_7_to_28cm,soil_temperature_0_to_7cm&timezone=Asia%2FSingapore"
    
    r_weather = requests.get(weather_url).json()
    r_soil = requests.get(soil_url).json()
    
    # Process daily forecast
    daily = r_weather["daily"]
    df_daily = pd.DataFrame({
        "date": pd.to_datetime(daily["time"]),
        "temp_max": daily["temperature_2m_max"],
        "rain": daily["precipitation_sum"],
        "wind_speed": daily["wind_speed_10m_max"],
        "humidity": daily["relative_humidity_2m_max"],
        "et": daily["et0_fao_evapotranspiration"]
    })
    
    # Process hourly soil data to daily averages
    hourly = r_soil["hourly"]
    df_hourly = pd.DataFrame({
        "time": pd.to_datetime(hourly["time"]),
        "soil_moisture": hourly["soil_moisture_0_to_7cm"],
        "soil_moisture_deep": hourly["soil_moisture_7_to_28cm"],
        "soil_temp": hourly["soil_temperature_0_to_7cm"]
    })
    df_soil_daily = df_hourly.groupby(df_hourly["time"].dt.date)[["soil_moisture", "soil_moisture_deep", "soil_temp"]].mean().reset_index()
    df_soil_daily["time"] = pd.to_datetime(df_soil_daily["time"])
    
    # Merge
    df = pd.merge(df_daily, df_soil_daily, left_on="date", right_on="time")
    return df

LOCALES["Bahasa Indonesia"].update({
    "tab_planner": "📅 Rencana Operasional",
    "tab_audit": "📈 Audit Akurasi Cuaca",
    "tab_calculator": "💰 Kalkulator Manfaat",
    "tab_guideline": "📖 Panduan Penggunaan",
    "live_soil_status": "🌱 Status Tanah Live",
    "location_map": "📍 Peta Lokasi Perkebunan",
    "outlook_insights": "📋 Rangkuman Rekomendasi Lapangan (7 Hari)",
    "insight_rain_fert": "Peringatan Hujan Lebat pada hari {day}: Berisiko hanyut (runoff). Tunda pemupukan.",
    "insight_wind_spray": "Peringatan Angin Kencang pada hari {day}: Berisiko drift kimia. Tunda penyemprotan.",
    "insight_optimal_all": "Kondisi cuaca 3 hari ke depan sangat baik. Lanjutkan semua operasional sesuai jadwal.",
    "date_col": "Tanggal",
    "fert_col": "Pemupukan (Fertilizing)",
    "harv_col": "Pemanenan Buah (Harvesting)",
    "spray_col": "Penyemprotan (Spraying)",
    "feasibility_trend_title": "Tren Proyeksi Kelayakan Operasional (7 Hari)",
    "ops_calendar_title": "📅 Kalender Operasional 7 Hari",
    
    # Audit keys
    "audit_select_days": "Pilih Jendela Evaluasi Historis (Hari)",
    "audit_overall_accuracy": "Akurasi Prakiraan Cuaca Keseluruhan",
    "audit_desc": "Membandingkan data prakiraan cuaca historis dengan data observasi satelit aktual dari Open-Meteo Archive untuk rentang tanggal terpilih.",
    "audit_temp_acc": "Akurasi Suhu Maksimum",
    "audit_rain_acc": "Akurasi Curah Hujan",
    "audit_wind_acc": "Akurasi Kecepatan Angin",
    "audit_chart_title": "Perbandingan Historis (Prakiraan vs Observasi Aktual)",
    "audit_actual": "Observasi Aktual",
    "audit_forecast": "Prakiraan Model",
    "audit_select_param": "Pilih Parameter Perbandingan",
    "audit_error": "Gagal memuat data audit historis. Layanan API mungkin sedang memproses atau offline.",
    
    # Calculator keys
    "calc_header": "💰 Kalkulator Estimasi Manfaat Finansial Perkebunan",
    "calc_subheader": "Hitung potensi penghematan biaya operasional tahunan dengan menggunakan panduan dashboard ini.",
    "calc_cpo_latest": "Harga CPO Dunia Saat Ini (World Bank API): ${price:.2f} USD / Ton (Setara Rp {idr_price:,.0f} / Ton)",
    "calc_cpo_fallback": "Menggunakan Harga CPO Acuan (Offline Mode): ${price:.2f} USD / Ton",
    "calc_total_benefit": "Total Estimasi Manfaat Finansial Tahunan",
    "calc_saved_fert": "Penghematan Hanyutan Pupuk (NPK/Urea)",
    "calc_saved_labor": "Penghematan Efisiensi Tenaga Kerja Panen",
    "calc_saved_spray": "Penghematan Bahan Kimia Semprot (Drift)",
    "calc_saved_crop": "Penyelamatan Nilai Buah Busuk / Rusak",
    "calc_sliders_title": "🔧 Parameter Biaya & Operasional Lapangan",
    "calc_estate_size": "Luas Kebun (Hektar)",
    "calc_ex_rate": "Nilai Tukar Rupiah per USD",
    "calc_fert_cost": "Biaya Pemupukan per Hektar per Siklus (Rp)",
    "calc_fert_freq": "Frekuensi Pemupukan per Tahun",
    "calc_harvest_wage": "Upah Harian Pemanen (Rp)",
    "calc_spray_cost": "Biaya Penyemprotan per Hektar per Siklus (Rp)",
    
    # Guidelines keys
    "guide_header": "📖 Panduan Penggunaan & Metodologi Ilmiah",
    "guide_sec1_title": "1. Logika Feasibility (Kelayakan) Kegiatan Perkebunan",
    "guide_sec2_title": "2. Formulasi Perhitungan Akurasi Audit Cuaca",
    "guide_sec3_title": "3. Metodologi Perhitungan Kalkulator Manfaat",
    "guide_sec4_title": "4. Tentang Parameter Kelembaban Tanah",
    "optimal": "Optimal",
    "caution": "Hati-hati",
    "unsuitable": "Tidak Cocok",
    
    # KPI keys
    "kpi_topsoil": "Kelembaban Lapisan Atas (0-7cm)",
    "kpi_topsoil_desc": "Zona penyerapan pupuk. Kelembaban optimal diperlukan agar pupuk larut ke tanah tanpa menguap atau mengalir hilang.",
    "kpi_subsoil": "Kelembaban Lapisan Dalam (7-28cm)",
    "kpi_subsoil_desc": "Zona perakaran jangkar pohon sawit. Memantau cadangan air tanah jangka panjang untuk menghindari stres kekeringan.",
    "kpi_temp": "Suhu Udara Maksimum",
    "kpi_temp_desc": "Suhu di atas 35°C meningkatkan risiko penguapan unsur nitrogen (volatilisasi urea).",
    "kpi_wind": "Kecepatan Angin Maksimum",
    "kpi_wind_desc": "Angin > 15 km/jam menyebabkan drift (pestisida tertiup angin keluar area target). Angin > 25 km/jam berisiko pelepah jatuh.",
    "kpi_rain": "Curah Hujan Harian",
    "kpi_rain_desc": "Curah hujan > 15mm menyebabkan jalan kebun berlumpur (panen terhambat) dan erosi pupuk.",
})

LOCALES["English"].update({
    "tab_planner": "📅 Operations Planner",
    "tab_audit": "📈 Forecast Accuracy Audit",
    "tab_calculator": "💰 Benefit Calculator",
    "tab_guideline": "📖 User Guide",
    "live_soil_status": "🌱 Live Soil Status",
    "location_map": "📍 Estate Location Map",
    "outlook_insights": "📋 Field Recommendations Summary (7-Day Outlook)",
    "insight_rain_fert": "Heavy Rain warning on {day}: Runoff risk. Postpone fertilizing.",
    "insight_wind_spray": "High Wind warning on {day}: Chemical drift risk. Postpone spraying.",
    "insight_optimal_all": "Favorable conditions for the next 3 days. Proceed with all operations.",
    "date_col": "Date",
    "fert_col": "Fertilization",
    "harv_col": "Fruit Harvesting",
    "spray_col": "Chemical Spraying",
    "feasibility_trend_title": "7-Day Operational Feasibility Projections",
    "ops_calendar_title": "📅 7-Day Operations Calendar",
    
    # Audit keys
    "audit_select_days": "Select Historical Evaluation Window (Days)",
    "audit_overall_accuracy": "Overall Forecast Accuracy Rating",
    "audit_desc": "Compares archived weather forecasts against actual observed satellite data from the Open-Meteo Archive for the selected window.",
    "audit_temp_acc": "Max Temperature Accuracy",
    "audit_rain_acc": "Precipitation Accuracy",
    "audit_wind_acc": "Wind Speed Accuracy",
    "audit_chart_title": "Historical Comparison (Forecast vs. Actual)",
    "audit_actual": "Actual Observed",
    "audit_forecast": "Forecast Model",
    "audit_select_param": "Select Parameter for Comparison",
    "audit_error": "Failed to retrieve historical audit data. API services might be processing or offline.",
    
    # Calculator keys
    "calc_header": "💰 Estate Financial Benefit Estimation Calculator",
    "calc_subheader": "Calculate the potential annual operational savings gained by using this dashboard's recommendations.",
    "calc_cpo_latest": "Latest Global CPO Price (World Bank API): ${price:.2f} USD / Ton (Equivalent to Rp {idr_price:,.0f} / Ton)",
    "calc_cpo_fallback": "Using Fallback Benchmark CPO Price (Offline Mode): ${price:.2f} USD / Ton",
    "calc_total_benefit": "Total Estimated Annual Savings",
    "calc_saved_fert": "Fertilizer Runoff Cost Savings",
    "calc_saved_labor": "Labor Downtime Efficiency Savings",
    "calc_saved_spray": "Spray Drift Chemical Savings",
    "calc_saved_crop": "Avoided Crop Loss & Rot Value",
    "calc_sliders_title": "🔧 Cost & Field Operational Parameters",
    "calc_estate_size": "Estate Size (Hectares)",
    "calc_ex_rate": "Exchange Rate (IDR per USD)",
    "calc_fert_cost": "Fertilizing Cost per Hectare per Cycle (Rp)",
    "calc_fert_freq": "Fertilizing Frequency per Year",
    "calc_harvest_wage": "Daily Harvester Wage (Rp)",
    "calc_spray_cost": "Spraying Cost per Hectare per Cycle (Rp)",
    
    # Guidelines keys
    "guide_header": "📖 Usage Guide & Scientific Methodology",
    "guide_sec1_title": "1. Operational Feasibility Logic",
    "guide_sec2_title": "2. Weather Audit Accuracy Calculations",
    "guide_sec3_title": "3. Financial Savings Methodology",
    "guide_sec4_title": "4. Understanding Soil Moisture Layers",
    "optimal": "Optimal",
    "caution": "Caution",
    "unsuitable": "Unsuitable",
    
    # KPI keys
    "kpi_topsoil": "Topsoil Moisture (0-7cm)",
    "kpi_topsoil_desc": "Fertilizer absorption zone. Optimal moisture is required so nutrients dissolve rather than washing away or evaporating.",
    "kpi_subsoil": "Subsoil Moisture (7-28cm)",
    "kpi_subsoil_desc": "Deep root anchorage zone. Monitors long-term groundwater reserves to prevent drought/water stress.",
    "kpi_temp": "Max Air Temperature",
    "kpi_temp_desc": "Temperatures above 35°C increase the risk of nitrogen volatilization (urea gas loss).",
    "kpi_wind": "Max Wind Speed",
    "kpi_wind_desc": "Wind > 15 km/h causes chemical drift (spray blowing off-target). Wind > 25 km/h poses safety hazards from falling fronds.",
    "kpi_rain": "Daily Precipitation",
    "kpi_rain_desc": "Rainfall > 15mm causes muddy plantation paths (harvesting delays) and soil runoff.",
})

try:
    df = fetch_data(lat, lon)
    
    # Calculate feasibility
    fert_scores, harv_scores, spray_scores = [], [], []
    badges_fert, badges_harv, badges_spray = [], [], []
    
    for idx, row in df.iterrows():
        weather_row = {
            "temp_max": row["temp_max"],
            "rain": row["rain"],
            "soil_moisture": row["soil_moisture"],
            "wind_speed": row["wind_speed"],
            "humidity": row["humidity"]
        }
        res = calculate_feasibility(weather_row, config)
        fert_scores.append(res["fertilizer"])
        harv_scores.append(res["harvesting"])
        spray_scores.append(res["spraying"])
        
        def get_badge(score):
            if score > 75: return f'<span class="score-badge-green">{LOCALES[lang]["optimal"]} ({int(score)}%)</span>'
            elif score > 40: return f'<span class="score-badge-yellow">{LOCALES[lang]["caution"]} ({int(score)}%)</span>'
            else: return f'<span class="score-badge-red">{LOCALES[lang]["unsuitable"]} ({int(score)}%)</span>'
            
        badges_fert.append(get_badge(res["fertilizer"]))
        badges_harv.append(get_badge(res["harvesting"]))
        badges_spray.append(get_badge(res["spraying"]))
        
    df["Fertilizing"] = fert_scores
    df["Harvesting"] = harv_scores
    df["Spraying"] = spray_scores
    
    # Tab Definition
    tab_planner, tab_audit, tab_calculator, tab_guideline = st.tabs([
        LOCALES[lang]["tab_planner"],
        LOCALES[lang]["tab_audit"],
        LOCALES[lang]["tab_calculator"],
        LOCALES[lang]["tab_guideline"]
    ])
    
    with tab_planner:
        # KPI Row on Top
        latest = df.iloc[0]
        kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
        
        with kpi_col1:
            st.metric(
                label=LOCALES[lang]["kpi_topsoil"],
                value=f"{latest['soil_moisture']*100:.1f} %",
                help=LOCALES[lang]["kpi_topsoil_desc"]
            )
        with kpi_col2:
            st.metric(
                label=LOCALES[lang]["kpi_subsoil"],
                value=f"{latest['soil_moisture_deep']*100:.1f} %",
                help=LOCALES[lang]["kpi_subsoil_desc"]
            )
        with kpi_col3:
            st.metric(
                label=LOCALES[lang]["kpi_temp"],
                value=f"{latest['temp_max']:.1f} °C",
                help=LOCALES[lang]["kpi_temp_desc"]
            )
        with kpi_col4:
            st.metric(
                label=LOCALES[lang]["kpi_wind"],
                value=f"{latest['wind_speed']:.1f} km/h",
                help=LOCALES[lang]["kpi_wind_desc"]
            )
        with kpi_col5:
            st.metric(
                label=LOCALES[lang]["kpi_rain"],
                value=f"{latest['rain']:.1f} mm",
                help=LOCALES[lang]["kpi_rain_desc"]
            )
            
        # Field Recommendations / Insights Box
        st.subheader(LOCALES[lang]["outlook_insights"])
        insights = []
        # Analyze next 3 days
        next_3_days = df.head(3)
        
        # Heavy rain check
        heavy_rain_days = next_3_days[next_3_days["rain"] > config["fert_runoff_rain"]]
        if not heavy_rain_days.empty:
            days_str = ", ".join(heavy_rain_days["date"].dt.strftime("%A").unique())
            insights.append(LOCALES[lang]["insight_rain_fert"].format(day=days_str))
            
        # Wind check
        high_wind_days = next_3_days[next_3_days["wind_speed"] > config["spray_drift_wind_med"]]
        if not high_wind_days.empty:
            days_str = ", ".join(high_wind_days["date"].dt.strftime("%A").unique())
            insights.append(LOCALES[lang]["insight_wind_spray"].format(day=days_str))
            
        if not insights:
            st.success(LOCALES[lang]["insight_optimal_all"])
        else:
            for insight in insights:
                st.warning(insight)
                
        # Main Planner Section below KPIs
        col_map, col_cal = st.columns([1, 2])
        
        with col_map:
            st.subheader(LOCALES[lang]["location_map"])
            m = folium.Map(location=[lat, lon], zoom_start=11)
            folium.Marker([lat, lon], popup="Estate").add_to(m)
            st_folium(m, height=250, use_container_width=True)
            
        with col_cal:
            st.subheader(LOCALES[lang]["ops_calendar_title"])
            df_cal = pd.DataFrame({
                LOCALES[lang]["date_col"]: df["date"].dt.strftime("%A, %b %d"),
                LOCALES[lang]["fert_col"]: badges_fert,
                LOCALES[lang]["harv_col"]: badges_harv,
                LOCALES[lang]["spray_col"]: badges_spray
            })
            st.write(df_cal.to_html(escape=False, index=False), unsafe_allow_html=True)
            
        st.subheader(LOCALES[lang]["feasibility_trend_title"])
        df_melted = df.melt(id_vars=["date"], value_vars=["Fertilizing", "Harvesting", "Spraying"], var_name="Operation", value_name="Feasibility")
        fig = px.line(df_melted, x="date", y="Feasibility", color="Operation", labels={"Feasibility": "Feasibility (%)", "date": "Date"})
        fig.update_layout(yaxis_range=[0, 105], hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        
    with tab_audit:
        st.subheader(LOCALES[lang]["tab_audit"])
        st.markdown(LOCALES[lang]["audit_desc"])
        
        # 1. Slider to choose evaluation window
        audit_days = st.slider(LOCALES[lang]["audit_select_days"], 7, 30, 7)
        
        # 2. Define date strings (Open-Meteo Archive has 3 days lag)
        end_dt = datetime.date.today() - datetime.timedelta(days=3)
        start_dt = end_dt - datetime.timedelta(days=audit_days)
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d")
        
        @st.cache_data(ttl=86400)
        def fetch_audit_data(latitude, longitude, start_s, end_s):
            archive_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={start_s}&end_date={end_s}&daily=temperature_2m_max,precipitation_sum,wind_speed_10m_max,relative_humidity_2m_max&timezone=Asia%2FSingapore"
            forecast_url = f"https://historical-forecast-api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&start_date={start_s}&end_date={end_s}&daily=temperature_2m_max,precipitation_sum,wind_speed_10m_max,relative_humidity_2m_max&timezone=Asia%2FSingapore"
            
            archive_res = requests.get(archive_url).json()
            forecast_res = requests.get(forecast_url).json()
            
            arch_daily = archive_res["daily"]
            fore_daily = forecast_res["daily"]
            
            df_arch = pd.DataFrame({
                "date": pd.to_datetime(arch_daily["time"]),
                "temp_actual": arch_daily["temperature_2m_max"],
                "rain_actual": arch_daily["precipitation_sum"],
                "wind_actual": arch_daily["wind_speed_10m_max"],
                "humidity_actual": arch_daily["relative_humidity_2m_max"]
            })
            
            df_fore = pd.DataFrame({
                "date": pd.to_datetime(fore_daily["time"]),
                "temp_fore": fore_daily["temperature_2m_max"],
                "rain_fore": fore_daily["precipitation_sum"],
                "wind_fore": fore_daily["wind_speed_10m_max"],
                "humidity_fore": fore_daily["relative_humidity_2m_max"]
            })
            
            return pd.merge(df_arch, df_fore, on="date")
            
        try:
            df_audit = fetch_audit_data(lat, lon, start_str, end_str)
            
            # Calculate accuracy parameters
            temp_err = (df_audit["temp_fore"] - df_audit["temp_actual"]).abs()
            temp_acc = 100.0 * (1.0 - (temp_err / df_audit["temp_actual"]).mean())
            temp_acc = max(0.0, min(100.0, temp_acc))
            
            rain_err = (df_audit["rain_fore"] - df_audit["rain_actual"]).abs()
            rain_acc = 100.0 * (1.0 - (rain_err / (df_audit["rain_actual"] + 5.0)).mean())
            rain_acc = max(0.0, min(100.0, rain_acc))
            
            wind_err = (df_audit["wind_fore"] - df_audit["wind_actual"]).abs()
            wind_denom = df_audit["wind_actual"].replace(0.0, 1.0)
            wind_acc = 100.0 * (1.0 - (wind_err / wind_denom).mean())
            wind_acc = max(0.0, min(100.0, wind_acc))
            
            overall_acc = 0.40 * temp_acc + 0.40 * rain_acc + 0.20 * wind_acc
            overall_acc = max(0.0, min(100.0, overall_acc))
            
            # Renders scorecards
            st.write("")
            a_col1, a_col2, a_col3, a_col4 = st.columns(4)
            with a_col1:
                st.metric(LOCALES[lang]["audit_overall_accuracy"], f"{overall_acc:.1f} %")
            with a_col2:
                st.metric(LOCALES[lang]["audit_temp_acc"], f"{temp_acc:.1f} %")
            with a_col3:
                st.metric(LOCALES[lang]["audit_rain_acc"], f"{rain_acc:.1f} %")
            with a_col4:
                st.metric(LOCALES[lang]["audit_wind_acc"], f"{wind_acc:.1f} %")
                
            # Parameter select for Plotly comparison chart
            st.write("")
            params_map = {
                LOCALES[lang]["kpi_temp"]: ("temp_fore", "temp_actual", "°C"),
                LOCALES[lang]["kpi_rain"]: ("rain_fore", "rain_actual", "mm"),
                LOCALES[lang]["kpi_wind"]: ("wind_fore", "wind_actual", "km/h")
            }
            sel_param = st.selectbox(LOCALES[lang]["audit_select_param"], list(params_map.keys()))
            fore_col, act_col, unit = params_map[sel_param]
            
            # Plot
            df_chart = pd.DataFrame({
                "Date": df_audit["date"],
                LOCALES[lang]["audit_forecast"]: df_audit[fore_col],
                LOCALES[lang]["audit_actual"]: df_audit[act_col]
            })
            df_chart_melted = df_chart.melt(id_vars=["Date"], value_vars=[LOCALES[lang]["audit_forecast"], LOCALES[lang]["audit_actual"]], var_name="Type", value_name=f"{sel_param} ({unit})")
            
            fig_audit = px.line(df_chart_melted, x="Date", y=f"{sel_param} ({unit})", color="Type", title=f"{LOCALES[lang]['audit_chart_title']} - {sel_param}")
            fig_audit.update_layout(hovermode="x unified")
            st.plotly_chart(fig_audit, use_container_width=True)
            
        except Exception as err:
            st.error(f"{LOCALES[lang]['audit_error']}: {err}")
        
    with tab_calculator:
        st.header(LOCALES[lang]["calc_header"])
        st.markdown(LOCALES[lang]["calc_subheader"])
        
        # Fetch CPO Price
        cpo_price, is_fallback = fetch_cpo_price()
        
        # 1. Inputs section inside two columns
        in_col1, in_col2 = st.columns(2)
        
        with in_col1:
            st.subheader(LOCALES[lang]["calc_sliders_title"])
            c_estate_size = st.number_input(LOCALES[lang]["calc_estate_size"], value=100, min_value=1)
            c_ex_rate = st.number_input(LOCALES[lang]["calc_ex_rate"], value=16300, min_value=1000)
            c_fert_cost = st.number_input(LOCALES[lang]["calc_fert_cost"], value=2000000, min_value=100000)
            
        with in_col2:
            st.write("")
            st.write("") # spacing
            c_fert_freq = st.slider(LOCALES[lang]["calc_fert_freq"], 1, 6, 3)
            c_harvest_wage = st.number_input(LOCALES[lang]["calc_harvest_wage"], value=150000, min_value=10000)
            c_spray_cost = st.number_input(LOCALES[lang]["calc_spray_cost"], value=400000, min_value=10000)
            
        # Display current CPO price feed
        cpo_idr = cpo_price * c_ex_rate
        if is_fallback:
            st.info(LOCALES[lang]["calc_cpo_fallback"].format(price=cpo_price))
        else:
            st.success(LOCALES[lang]["calc_cpo_latest"].format(price=cpo_price, idr_price=cpo_idr))
            
        # 2. Perform Calculations
        # 2.1 Fertilizer Savings
        saved_fert = c_estate_size * c_fert_freq * c_fert_cost * 0.15 * 0.40
        # 2.2 Labor Savings
        saved_labor = c_estate_size * 30 * (c_harvest_wage * 1.5) * 0.60
        # 2.3 Spraying Savings
        saved_spray = c_estate_size * 4 * c_spray_cost * 0.10 * 0.80
        # 2.4 Crop Loss Prevention
        saved_crop = c_estate_size * 0.02 * (4.0 * cpo_price * c_ex_rate)
        
        total_benefit = saved_fert + saved_labor + saved_spray + saved_crop
        total_benefit_usd = total_benefit / c_ex_rate
        
        # 3. Output columns
        st.write("---")
        st.markdown(f"### {LOCALES[lang]['calc_total_benefit']}:")
        st.markdown(f"<h2 style='color:#2e7d32;margin-top:0;'>Rp {total_benefit:,.0f} / tahun (~${total_benefit_usd:,.2f} USD)</h2>", unsafe_allow_html=True)
        
        out_col1, out_col2 = st.columns(2)
        with out_col1:
            st.metric(LOCALES[lang]["calc_saved_fert"], f"Rp {saved_fert:,.0f}")
            st.metric(LOCALES[lang]["calc_saved_labor"], f"Rp {saved_labor:,.0f}")
        with out_col2:
            st.metric(LOCALES[lang]["calc_saved_spray"], f"Rp {saved_spray:,.0f}")
            st.metric(LOCALES[lang]["calc_saved_crop"], f"Rp {saved_crop:,.0f}")
        
    with tab_guideline:
        st.header(LOCALES[lang]["guide_header"])
        
        # 1. Operational Feasibility Logic Expander
        with st.expander(LOCALES[lang]["guide_sec1_title"]):
            if lang == "Bahasa Indonesia":
                st.markdown("""
                **Logika Penentuan Skor Kelayakan Kegiatan Kebun:**
                *   **Pemupukan (Fertilizing):**
                    *   Pupuk NPK/Urea membutuhkan sedikit air untuk larut ke tanah. Namun, curah hujan > 15 mm dalam sehari akan membilas permukaan tanah dan mencuci pupuk (leaching/runoff), mengurangi efisiensi hingga **80%**.
                    *   Tanah kering (kelembaban < 20%) tanpa hujan menyebabkan pupuk menguap menjadi gas amonia (volatilisasi Nitrogen).
                *   **Pemanenan (Harvesting):**
                    *   Hujan lebat (> 15 mm) merusak struktur jalan tanah liat perkebunan kelapa sawit menjadi lumpur tebal. Truk angkut buah akan terjebak, dan pelepah basah berbahaya bagi keselamatan pemanen sawit.
                *   **Penyemprotan (Spraying):**
                    *   Kecepatan angin > 15 km/jam memindahkan tetesan semprotan herbisida/pestisida dari target sasaran gulma/hama (spray drift).
                    *   Hujan > 2 mm segera membilas zat aktif dari permukaan daun sebelum sempat diserap tanaman (wash-off).
                """)
            else:
                st.markdown("""
                **Operational Feasibility Scoring System:**
                *   **Fertilization:**
                    *   Nutrients require soil moisture to dissolve, but rainfall > 15 mm washes fertilizer away (runoff/leaching), causing an **80% efficiency loss**.
                    *   Dry soils (moisture < 20%) with zero rain cause nitrogen to volatilize into ammonia gas.
                *   **Harvesting:**
                    *   Heavy rain (> 15 mm) turns clay plantation tracks into mud, trapping collection vehicles. Wet trunks also present harvesting safety hazards.
                *   **Spraying:**
                    *   Wind speeds > 15 km/h blow chemical droplets away from targets (drift).
                    *   Rainfall > 2 mm washes active ingredients off leaves before absorption (wash-off).
                """)

        # 2. Weather Audit Accuracy Calculations Expander (LaTeX)
        with st.expander(LOCALES[lang]["guide_sec2_title"]):
            if lang == "Bahasa Indonesia":
                st.markdown("""
                **Bagaimana Kami Menghitung Akurasi Prakiraan Cuaca?**
                Kami membandingkan prakiraan masa lalu dari model cuaca dengan observasi aktual satelit (Open-Meteo Archive). Rumus matematika di bawah digunakan untuk menghitung kecocokan keduanya:
                
                *   **Akurasi Suhu (Temperature Accuracy):**
                """)
                st.latex(r"Acc_T = 100 \times \left(1 - \frac{\sum |T_{fore} - T_{act}|}{\sum T_{act}}\right)")
                
                st.markdown("""
                *   **Akurasi Curah Hujan (Rain Accuracy):**
                Untuk menangani hari tanpa hujan (0 mm) secara adil tanpa pembagian dengan nol, pembagi disesuaikan dengan menambahkan konstanta peredam (5.0 mm):
                """)
                st.latex(r"Acc_R = \max\left(0, 100 \times \left(1 - \frac{\sum |R_{fore} - R_{act}|}{\sum (R_{act} + 5.0)}\right)\right)")
                
                st.markdown("""
                *   **Akurasi Kecepatan Angin (Wind Accuracy):**
                """)
                st.latex(r"Acc_W = 100 \times \left(1 - \frac{\sum |W_{fore} - W_{act}|}{\sum W_{act}}\right)")
                
                st.markdown("""
                *   **Rating Akurasi Keseluruhan (Overall Score):**
                Bobot disesuaikan berdasarkan signifikansinya terhadap operasional kebun (40% Suhu, 40% Hujan, 20% Angin):
                """)
                st.latex(r"Acc_{Overall} = 0.40 \times Acc_T + 0.40 \times Acc_R + 0.20 \times Acc_W")
            else:
                st.markdown("""
                **How is Forecast Accuracy Calculated?**
                We compare past predictions against actual observed values. The error difference (Mean Absolute Error) is mapped to a percentage rating:
                
                *   **Temperature Accuracy:**
                """)
                st.latex(r"Acc_T = 100 \times \left(1 - \frac{\sum |T_{fore} - T_{act}|}{\sum T_{act}}\right)")
                
                st.markdown("""
                *   **Rain Accuracy:**
                To handle dry days (0 mm) without division-by-zero, we apply a dampening constant (5.0 mm) to the denominator:
                """)
                st.latex(r"Acc_R = \max\left(0, 100 \times \left(1 - \frac{\sum |R_{fore} - R_{act}|}{\sum (R_{act} + 5.0)}\right)\right)")
                
                st.markdown("""
                *   **Wind Speed Accuracy:**
                """)
                st.latex(r"Acc_W = 100 \times \left(1 - \frac{\sum |W_{fore} - W_{act}|}{\sum W_{act}}\right)")
                
                st.markdown("""
                *   **Overall Audit Score:**
                Weighted by operational significance (40% Temperature, 40% Rain, 20% Wind):
                """)
                st.latex(r"Acc_{Overall} = 0.40 \times Acc_T + 0.40 \times Acc_R + 0.20 \times Acc_W")

        # 3. Financial Savings Methodology Expander (LaTeX)
        with st.expander(LOCALES[lang]["guide_sec3_title"]):
            if lang == "Bahasa Indonesia":
                st.markdown("""
                **Metodologi Perhitungan Penghematan Finansial:**
                
                *   **1. Penghematan Hanyutan Pupuk (NPK/Urea):**
                Mencegah pemupukan sebelum hujan lebat (probabilitas curah hujan tinggi rata-rata 15% di Indonesia dengan kerugian pencucian zat hara 40%):
                """)
                st.latex(r"\text{Hemat Pemupukan} = \text{Luas Kebun} \times \text{Frekuensi/Tahun} \times \text{Biaya/Hektar} \times 0.15 \times 0.40")
                
                st.markdown("""
                *   **2. Penghematan Tenaga Kerja Panen:**
                Menghindari pemborosan tenaga kerja saat jalan kebun tidak bisa dilewati (diestimasi rata-rata 30 hari jalan berlumpur per tahun dengan inefisiensi 60% dan kebutuhan 1.5 pekerja/hektar):
                """)
                st.latex(r"\text{Hemat Labor} = \text{Luas Kebun} \times 30\text{ hari} \times (\text{Upah Pemanen} \times 1.5) \times 0.60")
                
                st.markdown("""
                *   **3. Penghematan Bahan Kimia Semprot:**
                Mencegah zat aktif pestisida hilang tertiup angin (drift) atau terbilas hujan (diestimasi frekuensi cuaca buruk saat jadwal penyemprotan adalah 10% dengan kehilangan efisiensi 80%):
                """)
                st.latex(r"\text{Hemat Kimia} = \text{Luas Kebun} \times 4\text{ siklus} \times \text{Biaya/Hektar} \times 0.10 \times 0.80")
                
                st.markdown("""
                *   **4. Penyelamatan Nilai Panen Buah:**
                Mencegah penurunan kualitas buah sawit (peningkatan kadar Asam Lemak Bebas / FFA) akibat keterlambatan transportasi di jalan rusak (diestimasi mencegah kerugian buah rot/rusak sebesar 2% per tahun). 
                Hasil panen rata-rata sawit dewasa di Indonesia adalah 20 ton TBS/hektar/tahun (setara 4 ton CPO pada OER 20%):
                """)
                st.latex(r"\text{Penyelamatan Buah} = \text{Luas Kebun} \times 0.02 \times \left(4\text{ ton} \times \text{Harga CPO Dunia (USD)} \times \text{Kurs}\right)")
            else:
                st.markdown("""
                **Savings Formula Reference:**
                
                *   **1. Fertilizer Savings:**
                """)
                st.latex(r"\text{Fertilizer Savings} = \text{Area} \times \text{Frequency} \times \text{Cost/Ha} \times 0.15\text{ (rain probability)} \times 0.40\text{ (runoff loss)}")
                
                st.markdown("""
                *   **2. Labor Savings:**
                """)
                st.latex(r"\text{Labor Savings} = \text{Area} \times 30\text{ days} \times (\text{Wage} \times 1.5\text{ workers/ha}) \times 0.60\text{ (inefficiency saved)}")
                
                st.markdown("""
                *   **3. Chemical Spraying Savings:**
                """)
                st.latex(r"\text{Spraying Savings} = \text{Area} \times 4\text{ cycles} \times \text{Cost/Ha} \times 0.10\text{ (bad weather risk)} \times 0.80\text{ (drift/runoff loss)}")
                
                st.markdown("""
                *   **4. Avoided Crop Loss:**
                We assume prevention of a 2% annual crop yield loss caused by transport logistics delays. High-yielding mature Indonesian palm trees produce roughly 20 tons of FFB per hectare per year (OER 20% = 4 tons of CPO/ha/year):
                """)
                st.latex(r"\text{Saved Crop} = \text{Area} \times 0.02 \times \left(4\text{ tons} \times P_{CPO}\text{ (World Bank API)} \times \text{Exchange Rate}\right)")

        # 4. Understanding Soil Moisture Layers Expander
        with st.expander(LOCALES[lang]["guide_sec4_title"]):
            if lang == "Bahasa Indonesia":
                st.markdown("""
                **Memahami Lapisan Kelembaban Tanah:**
                *   **Lapisan Atas (0-7cm):** Merupakan area permukaan tanah tempat pemupukan ditaburkan. Kelembaban di area ini sangat sensitif terhadap panas matahari harian. Jika terlalu kering, pupuk tidak dapat larut untuk diserap akar tanaman.
                *   **Lapisan Dalam (7-28cm):** Merupakan area perakaran aktif pohon kelapa sawit dewasa untuk menyerap air tanah. Kadar air di lapisan ini cenderung lebih stabil dan menggambarkan ketahanan pohon sawit terhadap stres air (drought/El Niño).
                """)
            else:
                st.markdown("""
                **Understanding Soil Moisture Depth Layers:**
                *   **Topsoil (0-7cm):** The surface layer where fertilizers are applied. This zone is highly sensitive to solar radiation and daily temperatures. If topsoil is dry, granulated fertilizer cannot dissolve to enter the root system.
                *   **Subsoil (7-28cm):** The active root zone for water absorption in mature palm trees. Moisture in this layer changes slowly and represents the plantation's resilience to water/drought stress.
                """)
        
except Exception as e:
    st.error(f"Error loading estate data: {e}")
