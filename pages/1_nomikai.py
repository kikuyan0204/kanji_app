# 飲み会検索
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.hotpepper import search_restaurants
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="飲み会検索", layout="centered")

# --- CSS（画像白四角除去 + カード美化） ---
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
        .search-button button {
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
        .search-button button:hover {
            background-color: #e95c50;
        }
        .result-card {
            background-color: #ffffff;
            border: 1px solid #ddd;
            border-radius: 14px;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06);
            padding: 1rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            transition: transform 0.2s ease;
        }
        .result-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
        }
        .result-image {
            display: block !important;
            width: 100% !important;
            height: 180px !important;
            object-fit: cover !important;
            border-radius: 8px !important;
            margin-bottom: 0.75rem;
        }
        .shop-name {
            font-size: 1.1rem;
            font-weight: 600;
            min-height: 3.5rem;
            margin: 0.5rem 0;
        }
        @media screen and (max-width: 768px) {
            .form-section {
                padding: 1rem;
                margin: 0 0.5rem;
                max-width: 100% !important;
            }
            .shop-name {
                font-size: 1rem !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- タイトル ---
st.markdown("<div class='title-text'>飲み会の開催条件を入力</div>", unsafe_allow_html=True)

# --- 入力フォーム ---
with st.form("search_form"):
    st.markdown("<div class='form-section'>", unsafe_allow_html=True)

    date = st.date_input("利用日", value=datetime.today())
    time = st.time_input("利用時間", value=datetime.now().time())
    location = st.text_input("利用場所（例：渋谷、梅田など）")
    num_people = st.radio("人数", ["2人", "3人", "4人", "5人", "6人以上"], horizontal=True)
    budget_label = st.selectbox("価格帯", ["指定なし", "～2000円", "2001～3000円", "3001～4000円", "4001～5000円", "5001円～"])
    keyword = st.text_area("その他条件（キーワード）", placeholder="例：個室、居酒屋、女子会 など")

    budget_map = {
        "指定なし": "",
        "～2000円": "B009",
        "2001～3000円": "B010",
        "3001～4000円": "B011",
        "4001～5000円": "B001",
        "5001円～": "B002"
    }
    budget_code = budget_map[budget_label]

    submitted = st.form_submit_button("検索する")
    st.markdown("</div>", unsafe_allow_html=True)

# --- 検索結果表示 ---
if submitted:
    st.subheader("検索結果")

    results = search_restaurants(keyword, location, budget_code)

    if not results:
        st.warning("条件に合致する飲食店が見つかりませんでした。")
    else:
        cols = st.columns(3)

        for i, shop in enumerate(results):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"""
                        <div class='result-card'>
                            <img src="{shop['photo']['pc']['l']}" class='result-image'>
                            <div class='shop-name'>{shop['name']}</div>
                            <a href="{shop['urls']['pc']}" target="_blank">店舗詳細を見る</a>
                        </div>
                    """, unsafe_allow_html=True)
