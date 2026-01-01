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

# ==============================================================================
# GÜVENLİ API BAĞLANTISI (GITHUB UYUMLU)
# ==============================================================================

# Önce Streamlit Cloud'un gizli kasasına bakar
if "GEMINI_API_KEY" in st.secrets:
    MY_SECRET_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    # Kasa boşsa (veya bilgisayarındaysan) burası boş kalır
    MY_SECRET_API_KEY = ""

# ==============================================================================
# 2. BAŞLATICI MOTORU
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

# API Konfigürasyonu
if MY_SECRET_API_KEY:
    try:
        genai.configure(api_key=MY_SECRET_API_KEY)
    except:
        pass

st.set_page_config(page_title="Mystic", page_icon="🔮", layout="wide")

# CSS TASARIMI
st.markdown("""
<style>
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
    desc = "Ücretsiz analiz için kısa bir reklam izleniyor..." if lang == "tr" else "Watching a short ad for free analysis..."
    
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(f"""
        <div class="ad-overlay">
            <h2>{title}</h2>
            <p style="font-size:18px;">{desc}</p>
            <br>
            <div style="background:#333; height:5px; width:100%;"><div style="background:#ffd700; height:100%; width:50%;"></div></div>
            <br><small>Google AdMob</small>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(3) 
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
    return "Oğlak" if lang == "tr" else "Capricorn"

# --- DİL SÖZLÜĞÜ ---
TEXTS = {
    "tr": {
        "tabs": ["☕ Kahve & El", "⭐ Yıldızname", "🌙 Rüya", "🃏 Tarot", "🔢 İsim Analizi"],
        "upload": "Fotoğraf Yükle",
        "coffee": "Kahve Falı",
        "palm": "El Falı",
        "btn_fal": "👁️ REKLAM İZLE VE YORUMLA",
        "btn_burc": "⭐ REKLAM İZLE VE OKU",
        "btn_ruya": "🌙 REKLAM İZLE VE TABİR ET",
        "btn_tarot": "🃏 REKLAM İZLE VE KART ÇEK",
        "btn_isim": "🔢 REKLAM İZLE VE ANALİZ ET",
        "lbl_name": "Adınız",
        "lbl_birth": "Doğum Tarihi",
        "lbl_burc": "Burcunuz",
        "lbl_cins": "Cinsiyet",
        "lbl_drm": "Durum",
        "lbl_konu": "Niyet",
        "ph_name": "İsminizi buraya yazın...",
        "ph_soru": "Sorunuzu buraya yazın...",
        "ph_ruya": "Rüyanızı anlatın...",
        "warn_key": "UYARI: API Anahtarı girilmemiş! Lütfen Streamlit ayarlarından 'Secrets' kısmına ekleyin.",
        "warn_pic": "Fotoğraf yüklemediniz.",
        "warn_name": "Lütfen isminizi giriniz.",
        "warn_wrong_img": "UYARI: Seçtiğiniz fal türüne uygun olmayan bir fotoğraf yüklediniz. Lütfen kontrol edin.",
        "deck": ["Joker", "Büyücü", "Azize", "İmparatoriçe", "İmparator", "Aziz", "Aşıklar", "Savaş Arabası", "Güç", "Ermiş", "Kader Çarkı", "Adalet", "Asılan Adam", "Ölüm", "Denge", "Şeytan", "Kule", "Yıldız", "Ay", "Güneş", "Mahkeme", "Dünya"],
        "zodiacs": ["Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak", "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"],
        "statuses": ["Bekar", "Evli", "İlişkisi Var"],
        "genders": ["Kadın", "Erkek"],
        "topics": ["Genel", "Aşk", "Para", "Kariyer"]
    },
    "en": {
        "tabs": ["☕ Visual Reading", "⭐ Horoscope", "🌙 Dream", "🃏 Tarot", "🔢 Name Analysis"],
        "upload": "Upload Photo",
        "coffee": "Coffee Cup",
        "palm": "Palmistry",
        "btn_fal": "👁️ WATCH AD & REVEAL",
        "btn_burc": "⭐ WATCH AD & READ",
        "btn_ruya": "🌙 WATCH AD & INTERPRET",
        "btn_tarot": "🃏 WATCH AD & DRAW CARDS",
        "btn_isim": "🔢 WATCH AD & ANALYZE",
        "lbl_name": "Your Name",
        "lbl_birth": "Date of Birth",
        "lbl_burc": "Zodiac Sign",
        "lbl_cins": "Gender",
        "lbl_drm": "Status",
        "lbl_konu": "Intention",
        "ph_name": "Enter your name...",
        "ph_soru": "Type your question...",
        "ph_ruya": "Describe your dream...",
        "warn_key": "WARNING: API Key missing! Please add it to 'Secrets' in Streamlit settings.",
        "warn_pic": "No photo uploaded.",
        "warn_name": "Please enter your name.",
        "warn_wrong_img": "WARNING: The uploaded photo does not match the selected reading type. Please check.",
        "deck": ["The Fool", "The Magician", "High Priestess", "Empress", "Emperor", "Hierophant", "Lovers", "Chariot", "Strength", "Hermit", "Wheel", "Justice", "Hanged Man", "Death", "Temperance", "Devil", "Tower", "Star", "Moon", "Sun", "Judgement", "World"],
        "zodiacs": ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
        "statuses": ["Single", "Married", "In Relationship"],
        "genders": ["Female", "Male"],
        "topics": ["General", "Love", "Money", "Career"]
    }
}

# --- UYGULAMA BAŞLANGICI ---
with st.sidebar:
    st.title("🌐 Language")
    lang_choice = st.radio("Seçiniz / Select", ["🇹🇷 Türkçe", "🇺🇸 English"], label_visibility="collapsed")
    lang = "tr" if "Türkçe" in lang_choice else "en"
    T = TEXTS[lang]
    
    st.markdown("---")
    st.markdown(f"### 👤 {T['lbl_name']}")
    user_name = st.text_input("Name", placeholder=T["ph_name"], label_visibility="collapsed")
    st.markdown("---")
    st.caption("Mystic Oracle v1.0 Final")

st.markdown(f"<h1 style='text-align: center;'>✨ MYSTIC ORACLE ✨</h1>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(T["tabs"])

# ------------------------------------------------------------------------------
# SEKME 1: GÖRSEL FAL
# ------------------------------------------------------------------------------
with tab1:
    c1, c2 = st.columns([1, 2])
    with c1:
        fal_tur = st.radio(T["lbl_konu"], [T["coffee"], T["palm"]], horizontal=True, label_visibility="collapsed")
        img = st.file_uploader(T["upload"], type=["jpg", "png"], label_visibility="collapsed")
        if img: st.image(img, width=200)
    with c2:
        z = st.selectbox(T["lbl_burc"], T["zodiacs"], key="s1_zodiac")
        g = st.selectbox(T["lbl_cins"], T["genders"], key="s1_g") 
        s = st.selectbox(T["lbl_drm"], T["statuses"], key="s2")
        t = st.selectbox(T["lbl_konu"], T["topics"], key="s3")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(T["btn_fal"], key="b1"):
            if not img: st.warning(T["warn_pic"])
            elif not MY_SECRET_API_KEY: st.error(T["warn_key"])
            else:
                reklam_izlet(lang)
                with st.spinner("..."):
                    try:
                        p_lang = "ENGLISH" if lang == "en" else "TURKISH"
                        isim_kismi = f"Name: {user_name}." if user_name else ""
                        
                        if lang == "tr":
                            beklenen = "Türk kahvesi fincanı veya tabağı (telveli)" if T["coffee"] in fal_tur else "İnsan eli ayası (avuç içi)"
                            uyari_mesaji = T["warn_wrong_img"]
                        else:
                            beklenen = "A coffee cup or saucer with grounds" if T["coffee"] in fal_tur else "A human palm/hand"
                            uyari_mesaji = T["warn_wrong_img"]

                        prompt = f"""
                        CRITICAL: You are a Real Fortune Teller. Mode: {fal_tur}.
                        STEP 1: Look strictly for **{beklenen}**. If NOT present, output "VALIDATION_FAIL".
                        STEP 2: Interpret mystically.
                        User: {isim_kismi} Zodiac: {z}. Gender: {g}, Status: {s}.
                        Topic: {t}. Language: {p_lang}.
                        """
                        model = genai.GenerativeModel(get_working_model())
                        res = model.generate_content([prompt, Image.open(img)])
                        
                        if "VALIDATION_FAIL" in res.text:
                            st.markdown(f'<div class="validation-warning">{uyari_mesaji}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)
                    except Exception as e: st.error(f"Hata/Error: {e}")

# ------------------------------------------------------------------------------
# SEKME 2: YILDIZNAME
# ------------------------------------------------------------------------------
with tab2:
    st.write(f"📅 **{T['lbl_birth']}**")
    bd_burc = st.date_input("Date", datetime.date(2000, 1, 1), label_visibility="collapsed", key="d2")
    zodiac_burc = get_zodiac_sign(bd_burc.day, bd_burc.month, lang)
    st.info(f"✨ Burç / Zodiac: **{zodiac_burc}**")
    
    if st.button(T["btn_burc"], key="b2"):
        if not MY_SECRET_API_KEY: st.error(T["warn_key"])
        else:
            reklam_izlet(lang)
            with st.spinner("..."):
                try:
                    p_lang = "ENGLISH" if lang == "en" else "TURKISH"
                    isim_kismi = f"Name: {user_name}." if user_name else ""
                    prompt = f"Daily Horoscope for {zodiac_burc}. DOB: {bd_burc}. {isim_kismi} Categories: Love, Career, Spirit. Language: {p_lang}. Mystical tone. No AI mention."
                    model = genai.GenerativeModel(get_working_model())
                    res = model.generate_content(prompt)
                    st.markdown(f'<div class="fortune-card"><h3>{zodiac_burc}</h3>{res.text}</div>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Hata/Error: {e}")

# ------------------------------------------------------------------------------
# SEKME 3: RÜYA TABİRİ
# ------------------------------------------------------------------------------
with tab3:
    r_txt = st.text_area(T["ph_ruya"], height=100)
    
    if st.button(T["btn_ruya"], key="b3"):
        if not MY_SECRET_API_KEY: st.error(T["warn_key"])
        else:
            reklam_izlet(lang)
            with st.spinner("..."):
                try:
                    p_lang = "ENGLISH" if lang == "en" else "TURKISH"
                    isim_kismi = f"Name: {user_name}." if user_name else ""
                    prompt = f"Dream: '{r_txt}'. {isim_kismi} Spiritual Meaning. Language: {p_lang}. Mystical tone. No AI mention."
                    model = genai.GenerativeModel(get_working_model())
                    res = model.generate_content(prompt)
                    st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Hata/Error: {e}")

# ------------------------------------------------------------------------------
# SEKME 4: TAROT
# ------------------------------------------------------------------------------
with tab4:
    ct1, ct2 = st.columns(2)
    with ct1:
        st.write(f"📅 **{T['lbl_birth']}**")
        bd_tarot = st.date_input("Date", datetime.date(2000, 1, 1), label_visibility="collapsed", key="d4")
        zodiac_tarot = get_zodiac_sign(bd_tarot.day, bd_tarot.month, lang)
        tg = st.selectbox(T["lbl_cins"], T["genders"], key="t_gender_final") 
        ts = st.selectbox(T["lbl_drm"], T["statuses"], key="t2")
    with ct2:
        st.write(f"🔮 **{T['lbl_konu']}**")
        tq = st.text_input("Soru", placeholder=T["ph_soru"], label_visibility="collapsed", key="t3")
        st.info(f"Burç: **{zodiac_tarot}**")
        
    if st.button(T["btn_tarot"], key="b4"):
        if not tq: st.warning(T["ph_soru"])
        elif not MY_SECRET_API_KEY: st.error(T["warn_key"])
        else:
            reklam_izlet(lang)
            with st.spinner("..."):
                try:
                    cards = random.sample(T["deck"], 3)
                    p_lang = "ENGLISH" if lang == "en" else "TURKISH"
                    isim_kismi = f"Name: {user_name}." if user_name else ""
                    
                    prompt = f"""
                    You are a Tarot Reader (Real person persona). Cards: {cards}.
                    User: {isim_kismi} DOB: {bd_tarot} (Zodiac: {zodiac_tarot}).
                    Gender: {tg}, Status: {ts}. Question: {tq}.
                    Calculate 'Birth Card' energy from DOB. Interpret deeply. Language: {p_lang}.
                    NEVER mention you are an AI. Address user by name.
                    """
                    model = genai.GenerativeModel(get_working_model())
                    res = model.generate_content(prompt)
                    
                    cc1, cc2, cc3 = st.columns(3)
                    cc1.info(cards[0]); cc2.success(cards[1]); cc3.warning(cards[2])
                    st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)
                except Exception as e: st.error(f"Hata/Error: {e}")

# ------------------------------------------------------------------------------
# SEKME 5: İSİM VE NUMEROLOJİ
# ------------------------------------------------------------------------------
with tab5:
    st.markdown(f"<h3 style='text-align:center;'>🔢 {T['tabs'][4]}</h3>", unsafe_allow_html=True)
    st.write(f"📅 **{T['lbl_birth']}**")
    bd_isim = st.date_input("Date", datetime.date(2000, 1, 1), label_visibility="collapsed", key="d5")
    
    if not user_name:
        st.info(T["warn_name"])
    else:
        if st.button(T["btn_isim"], key="b5"):
            if not MY_SECRET_API_KEY: st.error(T["warn_key"])
            else:
                reklam_izlet(lang)
                with st.spinner("..."):
                    try:
                        p_lang = "ENGLISH" if lang == "en" else "TURKISH"
                        prompt = f"""
                        Perform a mystical Numerology reading.
                        Name: "{user_name}". DOB: {bd_isim}.
                        1. Calculate Life Path Number. 2. Name Energy. 3. Future Predictions.
                        Language: {p_lang}. Tone: Mystical. No AI mention.
                        """
                        model = genai.GenerativeModel(get_working_model())
                        res = model.generate_content(prompt)
                        st.markdown(f'<div class="fortune-card">{res.text}</div>', unsafe_allow_html=True)
                    except Exception as e: st.error(f"Hata/Error: {e}")

