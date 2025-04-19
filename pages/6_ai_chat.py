# AIチャットに相談
import streamlit as st
import sys
import os

# モジュールパスを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.ai import ask_bedrock

st.set_page_config(page_title="AI幹事チャット", layout="centered")
st.title("AI幹事に質問してみよう")

# チャット履歴をセッションに保持
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# 入力フォーム
with st.form("chat_form"):
    user_input = st.text_input("質問を入力（例：近くに温泉ある？）")
    submitted = st.form_submit_button("送信")

# 送信後の処理
if submitted and user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.spinner("AIが考え中..."):
        reply = ask_bedrock(user_input)
    st.session_state.chat_history.append(("ai", reply))

# チャット履歴の表示
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"🧑‍💼 **あなた**: {msg}")
    else:
        st.markdown(f"🤖 **AI幹事**: {msg}")
