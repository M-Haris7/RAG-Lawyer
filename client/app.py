import streamlit as st
from compoments.upload import render_uploader
from compoments.history_download import render_history_download
from compoments.chatUI import render_chat


st.set_page_config(page_title="Lawgic AI",layout="wide")
st.title("⚖️ RAG AI Lawyer")


render_uploader()
render_chat()
render_history_download()