import os
import sys
import threading
import time
import subprocess
import warnings
import datetime
import random
import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

# ==============================================================================
# 1. REKLAM AYARLARI (FATİH'İN REKLAM ID'LERİ)
# ==============================================================================
PUBLISHER_ID = "ca-pub-8501135338572495"
BANNER_ID = "2140519460"
INTERSTITIAL_ID = "2153973664"

# Banner Reklam Fonksiyonu
def show_banner_ad():
    ad_html = f"""
    <div style="text-align: center; margin: 10px 0;">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={PUBLISHER_ID}"
             crossorigin="anonymous"></script>
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="{PUBLISHER_ID}"
             data-ad-slot="{BANNER_ID}"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
    </div>
    """
    components.html(ad_html, height=100)

# Geçiş Reklamı Fonksiyonu (Interstitial)
def show_interstitial_ad():
    interstitial_html = f"""
    <div style="text-align: center;">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={PUBLISHER_ID}"
             crossorigin="anonymous"></script>
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="{PUBLISHER_ID}"
             data-ad-slot="{INTERSTITIAL_ID}"
             data-ad-format="intrastat"
             data-adsbygoogle-status="done"></ins>
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>
    </div>
    """
    components.html(interstitial_html, height=300)

# ==============================================================================
# 2. BAĞLANTI VE MOTOR AYARLARI
# ==============================================================================
if "GEMINI_API_KEY" in st.secrets:
    MY_SECRET_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    MY_SECRET_API_KEY = ""

warnings.filterwarnings("ignore")
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

# ==============================================================================
# 3. UYGULAMA İÇERİĞİ
# ==============================================================================
if MY_SECRET_API_KEY:
    try:
        genai.configure(api_key=MY_SECRET_API_KEY)
    except:
        pass

st.set_page_config(page_title="Mystic Oracle", page_icon="🔮", layout="wide")

# CSS TASARIMI (Yenileme Engelleme Dahil)
st.markdown("""
<style>
    /* Sayfanın yukarıdan aşağı çekilip yenilenmesini engelleme */
    html, body, [data-testid="stAppViewContainer"] {
        overscroll-behavior-y: contain;
        overflow-y: auto;
    }

    header, #MainMenu, footer {visibility: hidden;}
    .stApp { background-color: #0e001c; color: #e0c3fc; }
    
    .fortune-card { 
        background: rgba(15, 15, 20, 0.9); 
        border: 1px solid #7b1fa2; 
        padding: 30px; 
        border-radius: 15px; 
        margin-top: 15px; 
        box-shadow: 0 0 30px rgba(123, 31, 162, 0.3);
        font-family: 'Segoe UI', sans-serif;
    }
    
    div.stButton > button { 
        background: linear-gradient(135deg, #4a0072, #7b1fa2); 
        color: white; 
        border: none; 
        padding: 12px; 
        border-radius: 8px; 
        width: 100%; 
        font-weight: bold; 
        transition: 0.3s;
    }
    
    .ad-overlay {
        border: 2px solid #ffd700;
        background-color: #000;
        color: #fff;
        padding: 40px;
        text-align: center;
        border-radius: 15px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

def get_working_model():
    try:
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

def reklam_izlet(lang):
    title = "🔮 BAĞLANTI KURULUYOR" if lang == "tr" else "🔮 ESTABLISHING CONNECTION"
    desc = "Ücretsiz analiz için kısa bir reklam izleniyor..." if lang == "tr" else "Watching a short ad for free analysis..."
    placeholder = st.empty()
    with placeholder.container():
        show_interstitial_ad() 
        st.markdown(f"""<div class="ad-overlay"><h2>{title}</h2><p style="font-size:18px;">{desc}</p></div>""", unsafe_allow_html=True)
        time.sleep(4)
    placeholder.empty()

# --- DİL SÖZLÜĞÜ ---
T_DICT = {
    "tr": {
        "tabs": ["☕ Kahve & El", "⭐ Yıldızname", "🌙 Rüya", "🃏 Tarot", "🔢 İsim Analizi"],
        "upload": "Fotoğraf Yükle", "coffee": "Kahve Falı", "palm": "El Falı",
        "btn_fal": "👁️ REKLAM İZLE VE YORUMLA", "lbl_name": "Adınız", "lbl_burc": "Burcunuz",
        "lbl_cins": "Cinsiyet", "lbl_drm": "Durum", "lbl_konu": "Niyet",
        "ph_name": "İsminizi yazın...", "warn_pic": "Fotoğraf yüklemediniz.",
        "warn_wrong_img": "UYARI: Yanlış fotoğraf türü!", "zodiacs": ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"],
        "statuses": ["Bekar", "Evli", "İlişkisi Var"], "genders": ["Kadın", "Erkek"], "topics": ["Genel", "Aşk", "Para", "Kariyer"]
    },
    "en": {
        "tabs": ["☕ Visual Reading", "⭐ Horoscope", "🌙 Dream", "🃏 Tarot", "🔢 Name Analysis"],
        "upload": "Upload Photo", "coffee": "Coffee Cup", "palm": "Palmistry",
        "btn_fal": "👁️ WATCH AD & REVEAL", "lbl_name": "Name", "lbl_burc": "Zodiac",
        "lbl_cins": "Gender", "lbl_drm": "Status", "lbl_konu": "Intention",
        "ph_name": "Enter name...", "warn_pic": "No photo.",
        "warn_wrong_img": "WARNING: Wrong photo type!", "zodiacs": ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
        "statuses": ["Single", "Married", "In Relationship"], "genders": ["Female", "Male"], "topics": ["General", "Love", "Money", "Career"]
    }
}

# --- UYGULAMA BAŞLANGICI ---
show_banner_ad()

with st.sidebar:
    st.title("🌐 Language")
    lang_choice = st.radio("Seçiniz / Select", ["🇹🇷 Türkçe", "🇺🇸 English"], label_visibility="collapsed")
    lang = "tr" if "Türkçe" in lang_choice else "en"
    T = T_DICT[lang]
    st.markdown("---")
    user_name = st.text_input(T["lbl_name"], placeholder=T["ph_name"])
    st.caption("Mystic Oracle v1.0")

st.markdown(f"<h1 style='text-align: center;'>✨ MYSTIC ORACLE ✨</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(T["tabs"])

with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        fal_tur = st.radio(T["lbl_konu"], [T["coffee"], T["palm"]], horizontal=True)
        img = st.file_uploader(T["upload"], type=["jpg", "png"])
        if img: st.image(img, width=150)
    with c2:
        z = st.selectbox(T["lbl_burc"], T["zodiacs"])
        g = st.selectbox(T["lbl_cins"], T["genders"])
        s = st.selectbox(T["lbl_drm"], T["statuses"])
        t = st.selectbox(T["lbl_konu"], T["topics"])
        
        if st.button(T["btn_fal"]):
            if not img: st.warning(T["warn_pic"])
            else:
                reklam_izlet(lang)
                with st.spinner("Kehanet hazırlanıyor..."):
                    try:
                        model = genai.GenerativeModel(get_working_model())
                        prompt = f"Role: Mystic Fortune Teller. Mode: {fal_tur}. User: {user_name}, Zodiac: {z}, Topic: {t}. Language: {lang}. Give a deep mystical reading."
                        res = model.generate_content([prompt, Image.open(img)])
                        st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)
                    except Exception as e: st.error(f"Error: {e}")

# Sayfa sonuna reklam
st.markdown("---")
show_banner_ad()
