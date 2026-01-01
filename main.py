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
# 1. REKLAM VE GÜVENLİK AYARLARI (REKLAM ID'LERİ VE GÜVENLİK)
# ==============================================================================
PUBLISHER_ID = "ca-pub-8501135338572495"
BANNER_ID = "2140519460"
INTERSTITIAL_ID = "2153973664"

# Streamlit Secrets üzerinden API anahtarı kontrolü
if "GEMINI_API_KEY" in st.secrets:
    MY_SECRET_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    MY_SECRET_API_KEY = ""

# Reklam Gösterim Fonksiyonları
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
        <script> (adsbygoogle = window.adsbygoogle || []).push({{}}); </script>
    </div>
    """
    components.html(ad_html, height=100)

def show_interstitial_ad():
    # Bu kısım gerçek reklamı tetikler ve sayfada yer kaplar
    interstitial_html = f"""
    <div style="text-align: center; background: #000; padding: 10px; border-radius: 10px;">
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={PUBLISHER_ID}"
             crossorigin="anonymous"></script>
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="{PUBLISHER_ID}"
             data-ad-slot="{INTERSTITIAL_ID}"
             data-ad-format="auto"
             data-full-width-responsive="true"></ins>
        <script> (adsbygoogle = window.adsbygoogle || []).push({{}}); </script>
    </div>
    """
    components.html(interstitial_html, height=320)

# ==============================================================================
# 2. BAŞLATICI MOTORU (ORİJİNAL - HİÇBİR ŞEY KESİLMEDİ)
# ==============================================================================
warnings.filterwarnings("ignore")
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"

if __name__ == "__main__":
    if os.environ.get("STREAMLIT_IS_RUNNING") != "true":
        def run_streamlit():
            os.environ["STREAMLIT_IS_RUNNING"] = "true"
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", __file__,
                "--server.headless=true",
                "--global.developmentMode=false",
                "--server.port=8501",
                "--theme.base=dark"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        try:
            import webview
            t = threading.Thread(target=run_streamlit)
            t.daemon = True
            t.start()
            time.sleep(2)
            webview.create_window("Mystic Oracle", "http://localhost:8501", width=1300, height=950, confirm_close=True)
            webview.start()
            sys.exit()
        except ImportError:
            pass

# ==============================================================================
# 3. UYGULAMA İÇERİĞİ
# ==============================================================================

if MY_SECRET_API_KEY:
    try:
        genai.configure(api_key=MY_SECRET_API_KEY)
    except:
        pass

st.set_page_config(page_title="Mystic Oracle", page_icon="🔮", layout="wide")

# CSS TASARIMI (Yenileme Engeli ve Orijinal Tasarım)
st.markdown("""
<style>
    /* Sayfayı aşağı çekince yenilenmeyi engelleyen kod */
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
    div.stButton > button:hover { transform: scale(1.02); }

    .ad-overlay {
        border: 2px solid #ffd700;
        background-color: #000;
        color: #fff;
        padding: 40px;
        text-align: center;
        border-radius: 15px;
        margin: 20px 0;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { border-color: #ffd700; }
        50% { border-color: #ff9e00; }
        100% { border-color: #ffd700; }
    }

    .stTextInput > div > div > input { background-color: rgba(255,255,255,0.1); color: #ffd700; font-weight: bold;}
    .stDateInput > div > div > input { background-color: rgba(255,255,255,0.1); color: white; }

    .validation-warning {
        background-color: #ff3333;
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
        border: 2px solid #ff0000;
    }
</style>
""", unsafe_allow_html=True)

def get_working_model():
    try:
        models = genai.list_models()
        valid = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        return valid[0] if valid else "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

def reklam_izlet(lang):
    title = "🔮 BAĞLANTI KURULUYOR" if lang == "tr" else "🔮 ESTABLISHING CONNECTION"
    desc = "Ücretsiz analiz için reklam yükleniyor..." if lang == "tr" else "Loading ad for free analysis..."
    
    placeholder = st.empty()
    with placeholder.container():
        # Reklamı BURADA zorunlu olarak gösteriyoruz
        show_interstitial_ad()
        st.markdown(f"""
        <div class="ad-overlay">
            <h2>{title}</h2>
            <p style="font-size:18px;">{desc}</p>
            <br>
            <div style="background:#333; height:5px; width:100%;"><div style="background:#ffd700; height:100%; width:75%;"></div></div>
            <br><small>Analiz reklamdan sonra başlayacaktır...</small>
        </div>
        """, unsafe_allow_html=True)
        # Reklamın yüklenmesi ve izlenmesi için 6 saniye zorunlu bekleme
        time.sleep(6) 
    placeholder.empty()

# --- BURÇ HESAPLAMA MOTORU ---
def get_zodiac_sign(day, month, lang="tr"):
    zodiac_dates = [
        (1, 20, "Oğlak", "Capricorn"), (2, 19, "Kova", "Aquarius"), (3, 20, "Balık", "Pisces"),
        (4, 20, "Koç", "Aries"), (5, 21, "Boğa", "Taurus"), (6, 21, "İkizler", "Gemini"),
        (7, 22, "Yengeç", "Cancer"), (8, 23, "Aslan", "Leo"), (9, 23, "Başak", "Virgo"),
        (10, 23, "Terazi", "Libra"), (11, 22, "Akrep", "Scorpio"), (12, 21, "Yay", "Sagittarius"),
        (12, 31, "Oğlak", "Capricorn")
    ]
    for m, d, z_tr, z_en in zodiac_dates:
        if month == m and day <= d: return z_tr if lang == "tr" else z_en
        elif month == m:
            next_idx = zodiac_dates.index((m, d, z_tr, z_en)) + 1
            if next_idx < len(zodiac_dates): return zodiac_dates[next_idx][2] if lang == "tr" else zodiac_dates[next_idx][3]
    return "Oğlak"

# --- DİL SÖZLÜĞÜ ---
TEXTS = {
    "tr": {
        "tabs": ["☕ Kahve & El", "⭐ Yıldızname", "🌙 Rüya", "🃏 Tarot", "🔢 İsim Analizi"],
        "upload": "Fotoğraf Yükle", "coffee": "Kahve Falı", "palm": "El Falı", "btn_fal": "👁️ REKLAM İZLE VE YORUMLA", "btn_burc": "⭐ REKLAM İZLE VE OKU", "btn_ruya": "🌙 REKLAM İZLE VE TABİR ET", "btn_tarot": "🃏 REKLAM İZLE VE KART ÇEK", "btn_isim": "🔢 REKLAM İZLE VE ANALİZ ET", "lbl_name": "Adınız", "lbl_birth": "Doğum Tarihi", "lbl_burc": "Burcunuz", "lbl_cins": "Cinsiyet", "lbl_drm": "Durum", "lbl_konu": "Niyet", "ph_name": "İsminizi buraya yazın...", "ph_soru": "Sorunuzu buraya yazın...", "ph_ruya": "Rüyanızı anlatın...", "warn_key": "Hata: API Anahtarı eksik!", "warn_pic": "Fotoğraf yüklemediniz.", "warn_name": "Lütfen adınızı giriniz.", "warn_wrong_img": "UYARI: Yanlış fotoğraf türü!", "deck": ["Joker", "Büyücü", "Azize", "İmparatoriçe", "İmparator", "Aziz", "Aşıklar", "Savaş Arabası", "Güç", "Ermiş", "Kader Çarkı", "Adalet", "Asılan Adam", "Ölüm", "Denge", "Şeytan", "Kule", "Yıldız", "Ay", "Güneş", "Mahkeme", "Dünya"], "zodiacs": ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"], "statuses": ["Bekar", "Evli", "İlişkisi Var"], "genders": ["Kadın", "Erkek"], "topics": ["Genel", "Aşk", "Para", "Kariyer"]
    },
    "en": {
        "tabs": ["☕ Visual Reading", "⭐ Horoscope", "🌙 Dream", "🃏 Tarot", "🔢 Name Analysis"],
        "upload": "Upload Photo", "coffee": "Coffee Cup", "palm": "Palmistry", "btn_fal": "👁️ WATCH AD & REVEAL", "btn_burc": "⭐ WATCH AD & READ", "btn_ruya": "🌙 WATCH AD & INTERPRET", "btn_tarot": "🃏 WATCH AD & DRAW CARDS", "btn_isim": "🔢 WATCH AD & ANALYZE", "lbl_name": "Name", "lbl_birth": "Date of Birth", "lbl_burc": "Zodiac Sign", "lbl_cins": "Gender", "lbl_drm": "Status", "lbl_konu": "Intention", "ph_name": "Enter name...", "ph_soru": "Type question...", "ph_ruya": "Describe dream...", "warn_key": "Error: API Key missing!", "warn_pic": "No photo.", "warn_name": "Please enter name.", "warn_wrong_img": "WARNING: Wrong photo!", "deck": ["The Fool", "Magician", "High Priestess", "Empress", "Emperor", "Hierophant", "Lovers", "Chariot", "Strength", "Hermit", "Wheel", "Justice", "Hanged Man", "Death", "Temperance", "Devil", "Tower", "Star", "Moon", "Sun", "Judgement", "World"], "zodiacs": ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"], "statuses": ["Single", "Married", "In Relationship"], "genders": ["Female", "Male"], "topics": ["General", "Love", "Money", "Career"]
    }
}

# --- UYGULAMA BAŞLANGICI ---
show_banner_ad() # En Üst Banner

with st.sidebar:
    st.title("🌐 Language")
    lang_choice = st.radio("Seçiniz", ["🇹🇷 Türkçe", "🇺🇸 English"], label_visibility="collapsed")
    lang = "tr" if "Türkçe" in lang_choice else "en"
    T = TEXTS[lang]
    st.markdown("---")
    st.markdown(f"### 👤 {T['lbl_name']}")
    user_name_sidebar = st.text_input("Name", placeholder=T["ph_name"], label_visibility="collapsed", key="u_side")
    st.markdown("---")
    st.caption("Mystic Oracle v1.0 Final")

st.markdown(f"<h1 style='text-align: center;'>✨ MYSTIC ORACLE ✨</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(T["tabs"])

# SEKME 1: GÖRSEL FAL
with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        fal_tur = st.radio(T["lbl_konu"], [T["coffee"], T["palm"]], horizontal=True, label_visibility="collapsed")
        img = st.file_uploader(T["upload"], type=["jpg", "png"], label_visibility="collapsed", key="img1")
        if img: st.image(img, width=200)
    with c2:
        z = st.selectbox(T["lbl_burc"], T["zodiacs"], key="s1_zodiac")
        g = st.selectbox(T["lbl_cins"], T["genders"], key="s1_g")
        s = st.selectbox(T["lbl_drm"], T["statuses"], key="s1_s")
        t = st.selectbox(T["lbl_konu"], T["topics"], key="s1_t")
        if st.button(T["btn_fal"], key="b1"):
            if not img: st.warning(T["warn_pic"])
            elif not MY_SECRET_API_KEY: st.error(T["warn_key"])
            else:
                reklam_izlet(lang) # ÖNCE REKLAM!
                with st.spinner("Kehanet hazırlanıyor..."):
                    try:
                        p_lang = "ENGLISH" if lang == "en" else "TURKISH"
                        isim_kismi = f"Name: {user_name_sidebar}." if user_name_sidebar else ""
                        beklenen = "Türk kahvesi" if T["coffee"] in fal_tur else "İnsan eli"
                        prompt = f"Interpret {fal_tur} for {isim_kismi} Zodiac: {z}. Lang: {p_lang}. Must look like {beklenen}."
                        model = genai.GenerativeModel(get_working_model())
                        res = model.generate_content([prompt, Image.open(img)])
                        st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)
                    except Exception as e: st.error(f"Error: {e}")

# SEKME 2: YILDIZNAME
with tab2:
    bd_burc = st.date_input("Doğum Tarihi", datetime.date(2000, 1, 1), key="d2")
    z_sign = get_zodiac_sign(bd_burc.day, bd_burc.month, lang)
    st.info(f"✨ Burç: {z_sign}")
    if st.button(T["btn_burc"], key="b2"):
        reklam_izlet(lang) # ÖNCE REKLAM!
        with st.spinner("Yıldızlar fısıldıyor..."):
            model = genai.GenerativeModel(get_working_model())
            res = model.generate_content(f"Daily horoscope for {z_sign} in {lang}.")
            st.markdown(f'<div class="fortune-card"><h3>{z_sign}</h3>{res.text}</div>', unsafe_allow_html=True)

# SEKME 3: RÜYA
with tab3:
    r_txt = st.text_area(T["ph_ruya"], height=100, key="r3")
    if st.button(T["btn_ruya"], key="b3"):
        reklam_izlet(lang) # ÖNCE REKLAM!
        with st.spinner("Rüya tabir ediliyor..."):
            model = genai.GenerativeModel(get_working_model())
            res = model.generate_content(f"Interpret dream: {r_txt} in {lang}.")
            st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)

# SEKME 4: TAROT
with tab4:
    tq = st.text_input(T["ph_soru"], key="q4")
    if st.button(T["btn_tarot"], key="b4"):
        reklam_izlet(lang) # ÖNCE REKLAM!
        with st.spinner("Kartlar çekiliyor..."):
            cards = random.sample(T["deck"], 3)
            st.write(f"Kartlarınız: {', '.join(cards)}")
            model = genai.GenerativeModel(get_working_model())
            res = model.generate_content(f"Tarot for {cards} in {lang}. Question: {tq}")
            st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)

# SEKME 5: İSİM ANALİZİ
with tab5:
    st.markdown(f"### 🔢 {T['tabs'][4]}")
    u_name_main = st.text_input(T["lbl_name"], placeholder=T["ph_name"], key="u_main")
    if st.button(T["btn_isim"], key="b5"):
        final_name = u_name_main if u_name_main else user_name_sidebar
        if not final_name: st.warning(T["warn_name"])
        else:
            reklam_izlet(lang) # ÖNCE REKLAM!
            with st.spinner("Sayılar analiz ediliyor..."):
                model = genai.GenerativeModel(get_working_model())
                res = model.generate_content(f"Numerology for {final_name} in {lang}.")
                st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)

st.markdown("---")
show_banner_ad() # Alt Banner
