# 天候・渋滞情報
import streamlit as st
from datetime import datetime
from utils.weather import get_forecast_for_date
from utils.traffic import get_traffic_info, create_map
from streamlit_folium import st_folium

st.set_page_config(page_title="天気と渋滞情報", layout="centered")

# --- デザイン統一CSS ---
st.markdown("""
    <style>
        .title-text {
            text-align: center;
            font-size: 2em;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 1rem;
        }
        .form-section {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            max-width: 600px;
            margin: auto;
        }
        .submit-button button {
            background-color: #ff6f61;
            color: white;
            font-weight: bold;
            border: none;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-size: 16px;
            width: 100%;
            transition: background-color 0.3s ease;
        }
        .submit-button button:hover {
            background-color: #e95c50;
        }
        @media screen and (max-width: 768px) {
            .form-section {
                padding: 1rem;
                margin: 0 0.5rem;
                max-width: 100% !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-text'>天気・渋滞情報を確認</div>", unsafe_allow_html=True)

# --- セッション状態の初期化 ---
for key in ["course_name", "play_date", "home_address", "forecast", "traffic"]:
    if key not in st.session_state:
        st.session_state[key] = None

# --- 初期値セット ---
default_course = st.session_state.get("selected_course", {})
default_name = default_course.get("name", "")
default_lat = default_course.get("lat")
default_lon = default_course.get("lon")

# --- 入力フォーム ---
with st.form("forecast_form"):
    st.markdown("<div class='form-section'>", unsafe_allow_html=True)

    course_name = st.text_input("予約したゴルフ場名", value=default_name)
    play_date = st.date_input("プレー日", value=datetime.today())
    home_address = st.text_input("自宅住所（例：東京都新宿区）")

    submitted = st.form_submit_button("天気と渋滞を確認")
    st.markdown("</div>", unsafe_allow_html=True)

if submitted:
    if not all([course_name, home_address, default_lat, default_lon]):
        st.error("ゴルフ場情報または自宅住所が不足しています。")
        st.stop()

    st.session_state["course_name"] = course_name
    st.session_state["play_date"] = play_date
    st.session_state["home_address"] = home_address

    st.session_state["forecast"] = get_forecast_for_date(default_lat, default_lon, play_date)
    st.session_state["traffic"] = get_traffic_info(home_address, f"{default_lat},{default_lon}")

# --- 結果表示（天気） ---
if st.session_state["forecast"]:
    f = st.session_state["forecast"]
    st.markdown("## 天気予報（プレー日）")
    if "error" in f:
        st.error(f["error"])
    else:
        st.info(f"{f['datetime']} の予報：{f['description']}、気温 {f['temp']}℃、湿度 {f['humidity']}%、風速 {f['wind']}m/s")

# --- 結果表示（渋滞） ---
if st.session_state["traffic"]:
    t = st.session_state["traffic"]
    st.markdown("## 渋滞情報（現在時刻）")
    if "error" in t:
        st.error(t["error"])
    else:
        st.success(f"{t['origin']} → {t['destination']} の所要時間：{t['duration_in_traffic']}（通常 {t['duration']}）")

# --- 地図表示 ---
if st.session_state["forecast"] and st.session_state["traffic"]:
    map_obj = create_map(
        st.session_state["home_address"],
        {
            "name": st.session_state["course_name"],
            "lat": default_lat,
            "lon": default_lon
        }
    )
    st.markdown("## 地図でルートを確認")
    st_folium(map_obj, width=700, height=500)
