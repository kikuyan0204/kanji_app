# ホーム
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from supabase import create_client, Client
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# ページ設定
st.set_page_config(page_title="幹事アシストAI", layout="centered")

# 柔らかい赤色ボタン対応CSS
st.markdown("""
<style>
body, .main, .block-container {
    background-color: #f9f9f9;
    color: #333333;
    font-family: 'Hiragino Kaku Gothic ProN', 'Helvetica Neue', sans-serif;
    padding: 1.2rem;
    max-width: 100%;
    overflow-x: hidden;
}
h1, h2, h3 {
    color: #222222;
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.stForm {
    background: #ffffff;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    margin-top: 1.5rem;
}
.stButton>button {
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
.stButton>button:hover {
    background-color: #e95c50;
}
input, select, textarea {
    background-color: #ffffff !important;
    color: #333333 !important;
    border-radius: 6px !important;
    padding: 0.5rem !important;
    border: 1px solid #cccccc !important;
}
.stMarkdown, .stSelectbox, .stTextInput {
    margin-bottom: 1.5rem;
}
.sidebar .sidebar-content::before {
    content: "🛍️ 幹事アシスト";
    font-size: 1.4rem;
    font-weight: bold;
    color: #ff6f61;
    display: block;
    margin-bottom: 1.5rem;
}

/* 完全対応版: selectbox の白四角（矢印領域）を消す */
[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 1px solid #cccccc !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    color: #333333 !important;
}
[data-baseweb="select"] > div:hover,
[data-baseweb="select"] > div:focus-within {
    border: 1px solid #999999 !important;
}
[data-baseweb="select"] .css-1jqq78o-placeholder {
    color: #999999 !important;
}
[data-baseweb="select"] .css-qc6sy-singleValue {
    color: #333333 !important;
}
</style>
""", unsafe_allow_html=True)

# Supabase接続
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# utilsパス
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "utils")))

# セッション状態初期化
if "user" not in st.session_state:
    st.session_state.user = None
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"

# サイドバー
if st.session_state.user:
    with st.sidebar:
        if st.button("ログアウト"):
            st.session_state.user = None
            st.rerun()

# ログイン・新規登録画面
if st.session_state.user is None:
    mode = st.session_state.auth_mode
    st.title("幹事アシストAI")
    st.subheader("ログインまたは新規登録して始めましょう")

    with st.form("auth_form"):
        email = st.text_input("メールアドレス")
        password = st.text_input("パスワード", type="password")
        submit_btn = st.form_submit_button("ログイン" if mode == "login" else "新規登録")

    if submit_btn:
        try:
            if mode == "login":
                auth_response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                st.session_state.user = auth_response.user
                st.success("ログインに成功しました！")
                st.rerun()
            else:
                auth_response = supabase.auth.sign_up({
                    "email": email,
                    "password": password,
                    "options": {
                        "emailRedirectTo": "http://localhost:8501"
                    }
                })
                st.success("ユーザー登録が完了しました。メールの認証リンクをクリックしてからログインしてください。")
                st.session_state.auth_mode = "login"
        except Exception as e:
            st.error(f"{'ログイン' if mode == 'login' else '新規登録'}に失敗しました: {e}")

    if mode == "login":
        if st.button("新規登録はこちら"):
            st.session_state.auth_mode = "signup"
            st.rerun()
    else:
        if st.button("すでにアカウントをお持ちの方はこちら"):
            st.session_state.auth_mode = "login"
            st.rerun()

# ログイン後のメイン画面
else:
    st.title("幹事アシストAI")
    st.subheader("イベント幹事のあなたに、AIが寄り添います。")

    st.markdown("### イベントを作成")
    event_type = st.selectbox("イベントの種類を選んでください", ("飲み会", "ゴルフコンペ"))

    if st.button("AIアシスタントに相談する"):
        if event_type == "飲み会":
            switch_page("nomikai")
        else:
            switch_page("golf")

    st.markdown("---")
    st.markdown("### AI幹事に相談する")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    with st.form("chat_form"):
        user_input = st.text_input("AIに質問してみよう（例：近くに温泉ある？）")
        submitted = st.form_submit_button("送信")

    if submitted and user_input:
        from utils.ai import ask_bedrock
        st.session_state.chat_history.append(("user", user_input))

        with st.spinner("AIが考え中..."):
            reply = ask_bedrock(user_input)

        st.session_state.chat_history.append(("ai", reply))

    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"🧑‍💼 **あなた**: {msg}")
        else:
            st.markdown(f"🤖 **AI幹事**: {msg}")
