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
# 1. REKLAM VE API AYARLARI (SENİN ID'LERİN)
# ==============================================================================
PUBLISHER_ID = "ca-pub-8501135338572495"
BANNER_ID = "2140519460"
INTERSTITIAL_ID = "2153973664"

# Reklam Fonksiyonları
def show_banner_ad():
    ad_html = f"""
    <div style="text-align: center; margin: 10px 0;">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={PUBLISHER_ID}" crossorigin="anonymous"></script>
        <ins class="adsbygoogle" style="display:block" data-ad-client="{PUBLISHER_ID}" data-ad-slot="{BANNER_ID}" data-ad-format="auto" data-full-width-responsive="true"></ins>
        <script> (adsbygoogle = window.adsbygoogle || []).push({{}}); </script>
    </div>
    """
    components.html(ad_html, height=100)

def show_interstitial_ad():
    interstitial_html = f"""
    <div style="text-align: center;">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={PUBLISHER_ID}" crossorigin="anonymous"></script>
        <ins class="adsbygoogle" style="display:block" data-ad-client="{PUBLISHER_ID}" data-ad-slot="{INTERSTITIAL_ID}" data-ad-format="auto"></ins>
        <script> (adsbygoogle = window.adsbygoogle || []).push({{}}); </script>
    </div>
    """
    components.html(interstitial_html, height=300)

# API Bağlantısı (Senin v15 kodundaki yapı)
if "GEMINI_API_KEY" in st.secrets:
    MY_SECRET_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    MY_SECRET_API_KEY = ""

# ==============================================================================
# 2. BAŞLATICI MOTORU (DOKUNULMADI)
# ==============================================================================
warnings.filterwarnings("ignore")
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

if MY_SECRET_API_KEY:
    try:
        genai.configure(api_key=MY_SECRET_API_KEY)
    except: pass

st.set_page_config(page_title="Mystic Oracle", page_icon="🔮", layout="wide")

# CSS TASARIMI (Yenileme Engeli Eklendi)
st.markdown("""
<style>
    /* Sayfayı aşağı çekince yenilenmesini engelleyen kod */
    html, body, [data-testid="stAppViewContainer"] { overscroll-behavior-y: contain; overflow-y: auto; }
    header, #MainMenu, footer {visibility: hidden;}
    .stApp { background-color: #0e001c; color: #e0c3fc; }
    .fortune-card { background: rgba(15, 15, 20, 0.9); border: 1px solid #7b1fa2; padding: 30px; border-radius: 15px; margin-top: 15px; box-shadow: 0 0 30px rgba(123, 31, 162, 0.3); font-family: 'Segoe UI', sans-serif; }
    div.stButton > button { background: linear-gradient(135deg, #4a0072, #7b1fa2); color: white; border: none; padding: 12px; border-radius: 8px; width: 100%; font-weight: bold; transition: 0.3s; }
    div.stButton > button:hover { transform: scale(1.02); }
    .ad-overlay { border: 2px solid #ffd700; background-color: #000; color: #fff; padding: 40px; text-align: center; border-radius: 15px; margin: 20px 0; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { border-color: #ffd700; } 50% { border-color: #ff9e00; } 100% { border-color: #ffd700; } }
    .stTextInput > div > div > input { background-color: rgba(255,255,255,0.1); color: #ffd700; font-weight: bold;}
    .stDateInput > div > div > input { background-color: rgba(255,255,255,0.1); color: white; }
    .validation-warning { background-color: #ff3333; color: white; padding: 15px; border-radius: 10px; font-weight: bold; text-align: center; border: 2px solid #ff0000; }
</style>
""", unsafe_allow_html=True)

def get_working_model():
    try:
        models = genai.list_models()
        valid = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        return valid[0] if valid else "models/gemini-1.5-flash"
    except: return "models/gemini-1.5-flash"

def reklam_izlet(lang):
    title = "🔮 BAĞLANTI KURULUYOR" if lang == "tr" else "🔮 ESTABLISHING CONNECTION"
    desc = "Ücretsiz analiz için kısa bir reklam izleniyor..." if lang == "tr" else "Watching a short ad..."
    placeholder = st.empty()
    with placeholder.container():
        show_interstitial_ad() # Gerçek reklam
        st.markdown(f'<div class="ad-overlay"><h2>{title}</h2><p style="font-size:18px;">{desc}</p></div>', unsafe_allow_html=True)
        time.sleep(4)
    placeholder.empty()

# --- BURÇ VE DİL SÖZLÜĞÜ (Senin v15 kodunla aynı) ---
def get_zodiac_sign(day, month, lang="tr"):
    zodiac_dates = [(1, 20, "Oğlak", "Capricorn"), (2, 19, "Kova", "Aquarius"), (3, 20, "Balık", "Pisces"), (4, 20, "Koç", "Aries"), (5, 21, "Boğa", "Taurus"), (6, 21, "İkizler", "Gemini"), (7, 22, "Yengeç", "Cancer"), (8, 23, "Aslan", "Leo"), (9, 23, "Başak", "Virgo"), (10, 23, "Terazi", "Libra"), (11, 22, "Akrep", "Scorpio"), (12, 21, "Yay", "Sagittarius"), (12, 31, "Oğlak", "Capricorn")]
    for m, d, z_tr, z_en in zodiac_dates:
        if month == m and day <= d: return z_tr if lang == "tr" else z_en
        elif month == m:
            next_idx = zodiac_dates.index((m, d, z_tr, z_en)) + 1
            if next_idx < len(zodiac_dates): return zodiac_dates[next_idx][2] if lang == "tr" else zodiac_dates[next_idx][3]
    return "Oğlak"

TEXTS = {
    "tr": { "tabs": ["☕ Kahve & El", "⭐ Yıldızname", "🌙 Rüya", "🃏 Tarot", "🔢 İsim Analizi"], "upload": "Fotoğraf Yükle", "coffee": "Kahve Falı", "palm": "El Falı", "btn_fal": "👁️ REKLAM İZLE VE YORUMLA", "btn_burc": "⭐ REKLAM İZLE VE OKU", "btn_ruya": "🌙 REKLAM İZLE VE TABİR ET", "btn_tarot": "🃏 REKLAM İZLE VE KART ÇEK", "btn_isim": "🔢 REKLAM İZLE VE ANALİZ ET", "lbl_name": "Adınız", "lbl_birth": "Doğum Tarihi", "lbl_burc": "Burcunuz", "lbl_cins": "Cinsiyet", "lbl_drm": "Durum", "lbl_konu": "Niyet", "ph_name": "İsminizi yazın...", "ph_soru": "Sorunuzu yazın...", "ph_ruya": "Rüyanızı anlatın...", "warn_key": "Hata: API Anahtarı eksik!", "warn_pic": "Fotoğraf yok.", "warn_name": "Lütfen isminizi giriniz.", "warn_wrong_img": "UYARI: Yanlış fotoğraf!", "deck": ["Joker", "Büyücü", "Azize", "İmparatoriçe", "İmparator", "Aziz", "Aşıklar", "Savaş Arabası", "Güç", "Ermiş", "Kader Çarkı", "Adalet", "Asılan Adam", "Ölüm", "Denge", "Şeytan", "Kule", "Yıldız", "Ay", "Güneş", "Mahkeme", "Dünya"], "zodiacs": ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"], "statuses": ["Bekar", "Evli", "İlişkisi Var"], "genders": ["Kadın", "Erkek"], "topics": ["Genel", "Aşk", "Para", "Kariyer"] },
    "en": { "tabs": ["☕ Visual Reading", "⭐ Horoscope", "🌙 Dream", "🃏 Tarot", "🔢 Name Analysis"], "upload": "Upload", "coffee": "Coffee Cup", "palm": "Palmistry", "btn_fal": "👁️ WATCH AD & REVEAL", "btn_burc": "⭐ WATCH AD & READ", "btn_ruya": "🌙 WATCH AD & INTERPRET", "btn_tarot": "🃏 WATCH AD & DRAW", "btn_isim": "🔢 WATCH AD & ANALYZE", "lbl_name": "Name", "lbl_birth": "Birth Date", "lbl_burc": "Zodiac Sign", "lbl_cins": "Gender", "lbl_drm": "Status", "lbl_konu": "Intention", "ph_name": "Enter name...", "ph_soru": "Type question...", "ph_ruya": "Describe dream...", "warn_key": "Error: API Key missing!", "warn_pic": "No photo.", "warn_name": "Enter name.", "warn_wrong_img": "WARNING: Wrong photo!", "deck": ["The Fool", "Magician", "High Priestess", "Empress", "Emperor", "Hierophant", "Lovers", "Chariot", "Strength", "Hermit", "Wheel", "Justice", "Hanged Man", "Death", "Temperance", "Devil", "Tower", "Star", "Moon", "Sun", "Judgement", "World"], "zodiacs": ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"], "statuses": ["Single", "Married", "Relationship"], "genders": ["Female", "Male"], "topics": ["General", "Love", "Money", "Career"] }
}

# --- UYGULAMA ---
show_banner_ad() # Üst Reklam

with st.sidebar:
    st.title("🌐 Language")
    lang_choice = st.radio("Seçiniz", ["🇹🇷 Türkçe", "🇺🇸 English"], label_visibility="collapsed")
    lang = "tr" if "Türkçe" in lang_choice else "en"
    T = TEXTS[lang]
    st.markdown("---")
    user_name_sidebar = st.text_input(T["lbl_name"], placeholder=T["ph_name"])
    st.caption("Mystic Oracle v1.0")

st.markdown(f"<h1 style='text-align: center;'>✨ MYSTIC ORACLE ✨</h1>", unsafe_allow_html=True)
tab1, tab2, tab3, tab4, tab5 = st.tabs(T["tabs"])

with tab1: # SEKME 1
    c1, c2 = st.columns([1, 2])
    with c1:
        fal_tur = st.radio(T["lbl_konu"], [T["coffee"], T["palm"]], horizontal=True, label_visibility="collapsed")
        img = st.file_uploader(T["upload"], type=["jpg", "png"], label_visibility="collapsed")
        if img: st.image(img, width=200)
    with c2:
        z, g, s, t = st.selectbox(T["lbl_burc"], T["zodiacs"], key="z1"), st.selectbox(T["lbl_cins"], T["genders"], key="g1"), st.selectbox(T["lbl_drm"], T["statuses"], key="s1"), st.selectbox(T["lbl_konu"], T["topics"], key="t1")
        if st.button(T["btn_fal"], key="b1"):
            if not img: st.warning(T["warn_pic"])
            elif not MY_SECRET_API_KEY: st.error(T["warn_key"])
            else:
                reklam_izlet(lang)
                with st.spinner("..."):
                    try:
                        p_lang = "ENGLISH" if lang == "en" else "TURKISH"
                        model = genai.GenerativeModel(get_working_model())
                        res = model.generate_content([f"Interpret {fal_tur} for {user_name_sidebar}. Zodiac: {z}. Lang: {p_lang}.", Image.open(img)])
                        st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)
                    except Exception as e: st.error(f"Error: {e}")

with tab2: # SEKME 2
    st.write(f"📅 **{T['lbl_birth']}**")
    bd_burc = st.date_input("D", datetime.date(2000, 1, 1), label_visibility="collapsed", key="d2")
    z_sign = get_zodiac_sign(bd_burc.day, bd_burc.month, lang)
    st.info(f"✨ {z_sign}")
    if st.button(T["btn_burc"], key="b2"):
        reklam_izlet(lang)
        with st.spinner("..."):
            model = genai.GenerativeModel(get_working_model())
            res = model.generate_content(f"Daily horoscope for {z_sign} in {lang}.")
            st.markdown(f'<div class="fortune-card"><h3>{z_sign}</h3>{res.text}</div>', unsafe_allow_html=True)

with tab3: # SEKME 3
    r_txt = st.text_area(T["ph_ruya"], height=100)
    if st.button(T["btn_ruya"], key="b3"):
        reklam_izlet(lang)
        with st.spinner("..."):
            model = genai.GenerativeModel(get_working_model())
            res = model.generate_content(f"Dream: {r_txt} in {lang}.")
            st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)

with tab4: # SEKME 4
    tq = st.text_input(T["ph_soru"], key="q4")
    if st.button(T["btn_tarot"], key="b4"):
        reklam_izlet(lang)
        with st.spinner("..."):
            c = random.sample(T["deck"], 3)
            st.write(f"Kartlar: {', '.join(c)}")
            model = genai.GenerativeModel(get_working_model())
            res = model.generate_content(f"Tarot for {c}. Question: {tq}. Lang: {lang}")
            st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)

with tab5: # SEKME 5
    st.markdown(f"### 🔢 {T['tabs'][4]}")
    u_name_main = st.text_input(T["lbl_name"], placeholder=T["ph_name"], key="u_main")
    if st.button(T["btn_isim"], key="b5"):
        final_name = u_name_main if u_name_main else user_name_sidebar
        if not final_name: st.warning(T["warn_name"])
        else:
            reklam_izlet(lang)
            with st.spinner("..."):
                model = genai.GenerativeModel(get_working_model())
                res = model.generate_content(f"Numerology for {final_name} in {lang}.")
                st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)

st.markdown("---")
show_banner_ad() # Alt Reklam
