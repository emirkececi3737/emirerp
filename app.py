import streamlit as st
import pandas as pd
import datetime
import os
import urllib.parse
import plotly.express as px
from streamlit_cookies_manager import EncryptedCookieManager
from user_agents import parse
import streamlit.components.v1 as components
from streamlit_quill import st_quill
import io
import requests
import time
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from PIL import Image
from supabase import create_client, Client

# --- 1. SUPABASE BULUT BAĞLANTISI VE ÇEREZ YÖNETİCİSİ ---
SUPABASE_URL = "https://dzkrarizvpuehabjepiy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR6a3Jhcml6dnB1ZWhhYmplcGl5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ5NTgwODUsImV4cCI6MjA5MDUzNDA4NX0.XEAFlH7HMXWHkDOaumKkvTaKfr3LcJNuIdvS281VdhA"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"⚠️ Supabase bağlantısı başarısız: {e}")

LOGO_PATH = "logo.png"

cookies = EncryptedCookieManager(password="yapikur")
if not cookies.ready():
    st.stop()

# --- 2. MODERN LIGHT UI TASARIMI VE DİNAMİK FAVICON ---
if os.path.exists(LOGO_PATH):
    page_icon_val = Image.open(LOGO_PATH)
else:
    page_icon_val = "🏢"

st.set_page_config(page_title="EMİR ERP", page_icon=page_icon_val, layout="wide")

if "choice" not in st.session_state:
    st.session_state["choice"] = "🏠 Dashboard"

st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #1e293b !important; }
    h1, h2, h3, h4, h5, p, span, label, li { color: #1e293b !important; font-family: 'Inter', sans-serif; }
    
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
    
    [data-testid="stSidebar"] .stButton>button {
        background: transparent !important; color: #1e293b !important;
        border: 1px solid #e2e8f0 !important; text-align: left !important;
        justify-content: flex-start !important; padding-left: 20px !important;
        font-weight: 600 !important; margin-bottom: 5px !important;
    }
    [data-testid="stSidebar"] .stButton>button:hover {
        background: #f1f5f9 !important; border-color: #2563eb !important;
        color: #2563eb !important; transform: translateY(-2px);
    }
    div[data-testid="stSidebarNav"] { display: none; }

    div[data-testid="stMetric"] {
        background-color: #ffffff !important; border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        padding: 20px !important;
    }
    div[data-testid="stMetricValue"] > div { color: #2563eb !important; font-weight: 800; }

    .stButton>button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important; border-radius: 8px !important; border: none !important;
        font-weight: 600 !important; width: 100%; transition: 0.3s; height: 45px;
    }
    
    .wa-button {
        display: block; background: #22c55e !important; color: white !important;
        padding: 12px; text-align: center; text-decoration: none; border-radius: 10px;
        font-weight: 700; margin-top: 10px; transition: 0.3s;
    }
    .wa-button:hover { background: #16a34a !important; opacity: 0.9; }

    input, select, textarea, div[data-baseweb="select"] {
        background-color: #ffffff !important; color: #1e293b !important;
        border: 1px solid #cbd5e1 !important; border-radius: 8px !important;
    }
    
    .device-tag { font-size: 11px; color: #64748b; font-style: italic; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; }
    .readonly-box { background-color: #ffffff; padding: 20px; border-radius: 8px; border: 1px solid #e2e8f0; color: #1e293b; min-height: 300px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    
    .customer-hero {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 40px; border-radius: 15px; color: white !important; margin-bottom: 30px;
    }
    .customer-hero h1, .customer-hero p { color: white !important; }
    
    /* SAĞ ALT SABİT TELİF YAZISI */
    .floating-copyright {
        position: fixed;
        bottom: 15px;
        right: 15px;
        background-color: rgba(255, 255, 255, 0.85);
        color: #64748b;
        font-size: 11px;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        z-index: 999999;
        backdrop-filter: blur(5px);
        font-family: 'Inter', sans-serif;
        pointer-events: none;
    }
    
    /* CANLI İŞ KARTI TASARIMI */
    .active-job-card {
        background-color: #ffffff;
        border-left: 5px solid #22c55e;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .paused-job-card {
        background-color: #ffffff;
        border-left: 5px solid #f59e0b;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='floating-copyright'>© 2026 EMİR ERP. Tüm hakları saklıdır.</div>", unsafe_allow_html=True)

# --- 3. YEREL SİSTEM DOSYALARI (AYARLAR, LOGLAR VE CANLI İŞLER İÇİN) ---
U_FILE = "users.csv"
S_FILE = "ayarlar.csv"
N_FILE = "notes.txt"
L_FILE = "logs.csv"
D_FILE = "devam_eden.csv" # YENİ: Canlı işleri tutan dosya
ATTACH_DIR = "attachments"

if not os.path.exists(ATTACH_DIR):
    os.makedirs(ATTACH_DIR)

def setup():
    if not os.path.exists(U_FILE):
        pd.DataFrame([{
            "username": "admin", "password": "123", "can_view_reports": True, 
            "can_manage_admin": True, "can_edit_dashboard": True, "can_use_assistant": True,
            "can_view_ticker": True, "is_customer": False, "customer_firm": ""
        }]).to_csv(U_FILE, index=False)
    
    u_df = pd.read_csv(U_FILE)
    cols = ["is_customer", "customer_firm", "can_use_assistant", "can_edit_dashboard", "can_view_ticker"]
    updated = False
    for c in cols:
        if c not in u_df.columns:
            u_df[c] = False if "can" not in c else True
            if c == "can_view_ticker": u_df[c] = True
            updated = True
    if updated: u_df.to_csv(U_FILE, index=False)
        
    if not os.path.exists(S_FILE):
        pd.DataFrame(columns=["tip", "deger"]).to_csv(S_FILE, index=False)
    
    if not os.path.exists(N_FILE):
        with open(N_FILE, "w", encoding="utf-8") as f: f.write("<h2>Yönetici Notları</h2>")
            
    if not os.path.exists(L_FILE):
        pd.DataFrame(columns=["Tarih", "Saat", "Kullanıcı", "İşlem", "Cihaz"]).to_csv(L_FILE, index=False)
        
    if not os.path.exists(D_FILE):
        # YENİ: Devam eden işler şablonu
        pd.DataFrame(columns=[
            "id", "Firma", "Makine", "Operatör", "Fiyat", "Detay", "Foto_Yolu", 
            "Durum", "Ilk_Baslama", "Son_Baslama", "Birikmis_Saniye", "Ekleyen"
        ]).to_csv(D_FILE, index=False)

setup()

# --- 4. BULUT VERİ FONKSİYONLARI VE YARDIMCILAR ---
def get_supabase_data():
    try:
        res = supabase.table("satislar").select("*").execute()
        df = pd.DataFrame(res.data)
        if df.empty:
            return pd.DataFrame(columns=["id", "Tarih", "Firma", "Makine", "Operatör", "Fiyat", "Detay", "Başlama Tarihi", "Bitiş Tarihi", "Başlama Saati", "Bitiş Saati", "Toplam Saat", "Ekleyen", "Cihaz", "Fotoğraf"])
        
        rename_map = {
            "tarih": "Tarih", "firma": "Firma", "makine": "Makine",
            "operator": "Operatör", "fiyat": "Fiyat", "detay": "Detay",
            "baslama_tarihi": "Başlama Tarihi", "bitis_tarihi": "Bitiş Tarihi",
            "baslama_saati": "Başlama Saati", "bitis_saati": "Bitiş Saati", "toplam_saat": "Toplam Saat",
            "ekleyen": "Ekleyen", "cihaz": "Cihaz", "fotograf": "Fotoğraf"
        }
        df = df.rename(columns=rename_map)
        
        if "Başlama Tarihi" not in df.columns: df["Başlama Tarihi"] = ""
        if "Bitiş Tarihi" not in df.columns: df["Bitiş Tarihi"] = ""
        if "Başlama Saati" not in df.columns: df["Başlama Saati"] = ""
        if "Bitiş Saati" not in df.columns: df["Bitiş Saati"] = ""
        if "Toplam Saat" not in df.columns: df["Toplam Saat"] = 0.0
        
        return df
    except Exception as e:
        print(f"Supabase Hatası: {e}")
        return pd.DataFrame(columns=["id", "Tarih", "Firma", "Makine", "Operatör", "Fiyat", "Detay", "Başlama Tarihi", "Bitiş Tarihi", "Başlama Saati", "Bitiş Saati", "Toplam Saat", "Ekleyen", "Cihaz", "Fotoğraf"])

def show_loader(mesaj="İşlem Yapılıyor..."):
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        img_html = f'<img src="data:image/png;base64,{encoded_string}" style="width:160px; animation: pulse 1.5s infinite;">'
    else:
        img_html = '<div style="font-size: 90px; animation: pulse 1.5s infinite;">🏢</div>'
        
    loader_html = f"""
    <style>
    @keyframes pulse {{ 0% {{ transform: scale(0.9); opacity: 0.8; }} 50% {{ transform: scale(1.1); opacity: 1; }} 100% {{ transform: scale(0.9); opacity: 0.8; }} }}
    .full-screen-loader {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(255, 255, 255, 0.85); z-index: 999999; display: flex; flex-direction: column; justify-content: center; align-items: center; backdrop-filter: blur(8px); }}
    .loader-text {{ color: #1e293b; margin-top: 30px; font-family: 'Inter', sans-serif; font-weight: 800; font-size: 22px; letter-spacing: 0.5px; }}
    </style>
    <div class="full-screen-loader" id="loader">{img_html}<div class="loader-text">{mesaj}</div></div>
    """
    ph = st.empty()
    ph.markdown(loader_html, unsafe_allow_html=True)
    time.sleep(1.0)
    ph.empty()

def log_islem(kullanici, islem):
    now = datetime.datetime.now()
    pd.DataFrame([{ "Tarih": now.strftime("%Y-%m-%d"), "Saat": now.strftime("%H:%M:%S"), "Kullanıcı": kullanici, "İşlem": islem, "Cihaz": get_device_info() }]).to_csv(L_FILE, mode='a', index=False, header=not os.path.exists(L_FILE))

def get_list(tip):
    df = pd.read_csv(S_FILE)
    return sorted(df[df["tip"] == tip]["deger"].unique().tolist())

def create_wa_link(firma, makine, op, fiyat, detay, bas_tar, bit_tar, bas_saat, bit_saat, top_saat):
    msg = f"📋 *YENİ SERVİS KAYDI*\n\n🏢 *Firma:* {firma}\n🚜 *Makine:* {makine}\n👷 *Operatör:* {op}\n⏱️ *Süre:* {top_saat} Saat ({bas_tar} {bas_saat} - {bit_tar} {bit_saat})\n💰 *Tutar:* {fiyat:,.2f} TL\n📝 *İşlem:* {detay}"
    return f"https://wa.me/?text={urllib.parse.quote(msg)}"

def get_device_info():
    ua_string = st.context.headers.get("User-Agent", "")
    ua = parse(ua_string)
    return f"{'Mobil' if ua.is_mobile else 'Masaüstü'} ({ua.os.family})"

def send_wa_live_bot(mesaj):
    try:
        df_a = pd.read_csv(S_FILE)
        aboneler = df_a[df_a['tip'] == 'WA_BOT_SUB']['deger'].tolist()
        for abone in aboneler:
            parcalar = abone.split('|')
            if len(parcalar) == 3:
                p, k = parcalar[1].strip().replace(" ", "").replace("+", ""), parcalar[2].strip()
                requests.get(f"https://api.callmebot.com/whatsapp.php?phone={p}&text={urllib.parse.quote(mesaj)}&apikey={k}", timeout=10)
    except: pass

def send_excel_via_email(receiver_email, excel_bytes, filename):
    try:
        df_ayar = pd.read_csv(S_FILE)
        s_email = df_ayar[df_ayar['tip'] == 'EMAIL_ADDR']['deger'].iloc[0] if not df_ayar[df_ayar['tip'] == 'EMAIL_ADDR'].empty else None
        s_pass = df_ayar[df_ayar['tip'] == 'EMAIL_PASS']['deger'].iloc[0] if not df_ayar[df_ayar['tip'] == 'EMAIL_PASS'].empty else None
        if not s_email or not s_pass: return False, "E-posta ayarları Yönetim Panelinden yapılmamış!"
        
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = s_email, receiver_email, f"EMİR ERP - Finansal Rapor Eki ({datetime.date.today()})"
        msg.attach(MIMEText("Sistemden otomatik olarak oluşturulan güncel finansal analiz raporu ektedir.\n\nİyi çalışmalar.", 'plain'))
        
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(excel_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(s_email, s_pass)
        server.send_message(msg)
        server.quit()
        return True, "E-posta başarıyla gönderildi!"
    except Exception as e: return False, f"Gönderim hatası: {str(e)}"

def akilli_asistan_cevapla(soru, df):
    soru = soru.lower()
    if df.empty: return "Sistemde henüz analiz edilecek kayıtlı veri bulunmuyor."
    df['Tarih_DT'] = pd.to_datetime(df['Tarih'], errors='coerce')
    bugun = datetime.date.today()
    zaman_etiketi = "Genel"
    
    if "bugün" in soru or "bugun" in soru: df = df[df['Tarih_DT'].dt.date == bugun]; zaman_etiketi = "Bugün"
    elif "bu ay" in soru: df = df[(df['Tarih_DT'].dt.year == bugun.year) & (df['Tarih_DT'].dt.month == bugun.month)]; zaman_etiketi = "Bu ay"
    elif "geçen ay" in soru or "gecen ay" in soru:
        gecen_ay_son = bugun.replace(day=1) - datetime.timedelta(days=1)
        df = df[(df['Tarih_DT'].dt.year == gecen_ay_son.year) & (df['Tarih_DT'].dt.month == gecen_ay_son.month)]; zaman_etiketi = "Geçen ay"
    elif "bu yıl" in soru or "bu sene" in soru: df = df[df['Tarih_DT'].dt.year == bugun.year]; zaman_etiketi = "Bu yıl"

    if df.empty: return f"Belirttiğin zaman diliminde ({zaman_etiketi}) sisteme girilmiş hiçbir veri bulamadım."
    if "ciro" in soru or "ne kadar" in soru or "toplam" in soru: return f"💰 {zaman_etiketi} toplam ciro: **{df['Fiyat'].sum():,.2f} TL**"
    elif "saat" in soru or "mesai" in soru: return f"⏱️ {zaman_etiketi} toplam çalışma süresi: **{df['Toplam Saat'].sum() if 'Toplam Saat' in df.columns else 0:,.2f} Saat**"
    elif "kazandıran" in soru or "iyi firma" in soru or "hangi firma" in soru: return f"🏢 {zaman_etiketi} en çok kazandıran firma **{df.groupby('Firma')['Fiyat'].sum().idxmax()}** (Toplam {df.groupby('Firma')['Fiyat'].sum().max():,.2f} TL)."
    elif "aktif" in soru or "operatör" in soru or "kim" in soru: return f"👷 {zaman_etiketi} en aktif operatör **{df['Operatör'].value_counts().idxmax()}** (Toplam {df['Operatör'].value_counts().max()} işlem)."
    elif "masraf" in soru or "arızalı" in soru or "makine" in soru: return f"🚜 {zaman_etiketi} en çok masraf çıkaran makine **{df.groupby('Makine')['Fiyat'].sum().idxmax()}** (Toplam {df.groupby('Makine')['Fiyat'].sum().max():,.2f} TL)."
    elif "son kayıt" in soru or "en son" in soru: son = df.iloc[-1]; return f"📅 Son işlem: **{son['Firma']}** firmasına **{son['Operatör']}** tarafından **{son['Makine']}** için yapılmış. Tutar: {son['Fiyat']} TL."
    else: return "🤖 Üzgünüm , anlayamadım. Zaman ekleyerek ciro, saat, firma veya aktif operatörleri sorabilirsin."

# --- 5. GİRİŞ VE OTURUM KONTROLÜ ---
if "logged_in" not in st.session_state:
    u, p = cookies.get("saved_user"), cookies.get("saved_pass")
    if u and p:
        users = pd.read_csv(U_FILE)
        match = users[(users['username'] == u) & (users['password'].astype(str) == p)]
        if not match.empty:
            r = match.iloc[0]
            st.session_state.update({
                "logged_in": True, "user": u, "can_view": bool(r["can_view_reports"]), 
                "can_admin": bool(r["can_manage_admin"]), "can_edit_dash": bool(r.get("can_edit_dashboard", False)), 
                "can_use_ai": bool(r.get("can_use_assistant", False)), "can_view_ticker": bool(r.get("can_view_ticker", True)),
                "is_cust": bool(r.get("is_customer", False)), "cust_firm": str(r.get("customer_firm", ""))
            })
        else: st.session_state["logged_in"] = False
    else: st.session_state["logged_in"] = False

# --- 5.1 CANLI BİLGİ EKRANI ---
if st.session_state.get("logged_in") and st.session_state.get("can_view_ticker", False):
    components.html("""
        <script>
            var doc = window.parent.document;
            if (!doc.getElementById("live-ticker")) {
                var ticker = doc.createElement("div"); ticker.id = "live-ticker";
                ticker.style.cssText = "position: fixed; top: 65px; right: 15px; pointer-events: none; background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(10px); color: #f8fafc; padding: 8px 15px; border-radius: 50px; font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 700; z-index: 9999999; display: flex; gap: 15px; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);";
                ticker.innerHTML = `<div style="display: flex; align-items: center;"><div style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 10px #22c55e; animation: pulse 1.5s infinite;"></div></div><div id="t-weather" style="margin-left: 5px;">🌤️ Kastamonu: Yükleniyor...</div><div id="t-usd" style="color:#4ade80;">💵 USD: --</div><div id="t-eur" style="color:#60a5fa;">💶 EUR: --</div>`;
                doc.body.appendChild(ticker);
                if (!doc.getElementById("ticker-styles")) {
                    var style = doc.createElement('style'); style.id = "ticker-styles";
                    style.innerHTML = `@keyframes pulse { 0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); } 70% { transform: scale(1.2); box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); } 100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); } }`;
                    doc.head.appendChild(style);
                }
                function updateData() {
                    fetch('https://api.open-meteo.com/v1/forecast?latitude=41.378&longitude=33.7753&current_weather=true').then(r => r.json()).then(data => { doc.getElementById('t-weather').innerHTML = '🌤️ Kastamonu: ' + data.current_weather.temperature + '°C'; }).catch(e => console.log(e));
                    fetch('https://api.exchangerate-api.com/v4/latest/USD').then(r => r.json()).then(data => { doc.getElementById('t-usd').innerHTML = '💵 Dolar: ' + data.rates.TRY.toFixed(2) + ' ₺'; });
                    fetch('https://api.exchangerate-api.com/v4/latest/EUR').then(r => r.json()).then(data => { doc.getElementById('t-eur').innerHTML = '💶 Euro: ' + data.rates.TRY.toFixed(2) + ' ₺'; });
                }
                updateData(); setInterval(updateData, 180000); 
            }
        </script>
    """, height=0, width=0)
else:
    components.html("<script>var t = window.parent.document.getElementById('live-ticker'); if(t) t.remove();</script>", height=0, width=0)

if not st.session_state.get("logged_in"):
    st.markdown("<br><br>", unsafe_allow_html=True)
    if os.path.exists(LOGO_PATH):
        col_logo1, col_logo2, col_logo3 = st.columns([2, 1, 2])
        with col_logo2: st.image(LOGO_PATH, use_container_width=True)
    else: st.markdown("<h1 style='text-align:center; color:#2563eb !important;'>🏢 EMİR ERP</h1>", unsafe_allow_html=True)
        
    col1, col_login, col3 = st.columns([1, 1, 1])
    with col_login:
        with st.form("login_panel", clear_on_submit=False):
            u_in = st.text_input("Kullanıcı Adı", key="login_user")
            p_in = st.text_input("Şifre", type="password", key="login_pass")
            rem = st.checkbox("Beni Hatırla (Girişi Sakla)", key="login_rem")
            
            if st.form_submit_button("SİSTEME GİRİŞ YAP"):
                users = pd.read_csv(U_FILE)
                match = users[(users['username'] == u_in) & (users['password'].astype(str) == p_in)]
                if not match.empty:
                    show_loader("Sisteme Giriş Yapılıyor...")
                    log_islem(u_in, "Sisteme Giriş Yaptı")
                    r = match.iloc[0]
                    if rem: cookies["saved_user"] = u_in; cookies["saved_pass"] = p_in; cookies.save()
                    st.session_state.update({
                        "logged_in": True, "user": u_in, "can_view": bool(r["can_view_reports"]), 
                        "can_admin": bool(r["can_manage_admin"]), "can_edit_dash": bool(r.get("can_edit_dashboard", False)), 
                        "can_use_ai": bool(r.get("can_use_assistant", False)), "can_view_ticker": bool(r.get("can_view_ticker", True)),
                        "is_cust": bool(r.get("is_customer", False)), "cust_firm": str(r.get("customer_firm", "")), "choice": "🏠 Dashboard"
                    })
                    st.rerun()
                else: st.error("❌ Kullanıcı adı veya şifre hatalı!")
else:
    # --- 6. YAN MENÜ (SIDEBAR) --- 
    with st.sidebar:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-weight:bold; color:#64748b; margin-top:-10px;'>👋 Hoş geldin, {st.session_state['user'].upper()}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h2 style='text-align:center;'>👋 {st.session_state['user'].upper()}</h2>", unsafe_allow_html=True)
            
        st.divider()
        
        if st.session_state.get("is_cust", False):
            if st.button("🏠 Müşteri Panosu", use_container_width=True, key="btn_cust_dash"): show_loader("Pano Yükleniyor..."); st.session_state["choice"] = "🏠 Dashboard"; st.session_state["kapat"] = True; st.rerun()
            st.info(f"📍 Bağlı Firma: {st.session_state['cust_firm']}")
        else:
            if st.button("🏠 Dashboard", use_container_width=True, key="btn_dash"): show_loader("Dashboard Yükleniyor..."); st.session_state["choice"] = "🏠 Dashboard"; st.session_state["kapat"] = True; st.rerun()
            if st.session_state.get("can_use_ai", False):
                if st.button("🤖 Akıllı Asistan", use_container_width=True, key="btn_ai"): show_loader("Yapay Zeka Bağlanıyor..."); st.session_state["choice"] = "🤖 Akıllı Asistan"; st.session_state["kapat"] = True; st.rerun()
            if st.button("📝 Servis Kaydı", use_container_width=True, key="btn_servis"): show_loader("Kayıt Ekranı Yükleniyor..."); st.session_state["choice"] = "📝 Servis Kaydı"; st.session_state["kapat"] = True; st.rerun()
            if st.session_state["can_view"]:
                if st.button("📊 Finansal Analiz", use_container_width=True, key="btn_finans"): show_loader("Raporlar Hazırlanıyor..."); st.session_state["choice"] = "📊 Finansal Analiz"; st.session_state["kapat"] = True; st.rerun()
            if st.session_state["can_admin"]:
                if st.button("⚙️ Yönetim Paneli", use_container_width=True, key="btn_admin"): show_loader("Sistem Yönetimi Yükleniyor..."); st.session_state["choice"] = "⚙️ Yönetim Paneli"; st.session_state["kapat"] = True; st.rerun()
        
        st.divider()
        if st.button("🚪 GÜVENLİ ÇIKIŞ", key="btn_logout"):
            show_loader("Sistemden Güvenle Çıkılıyor...")
            log_islem(st.session_state['user'], "Sistemden Çıkış Yaptı")
            if "saved_user" in cookies: del cookies["saved_user"]
            if "saved_pass" in cookies: del cookies["saved_pass"]
            cookies.save(); st.session_state["logged_in"] = False; st.rerun()
            
        st.markdown("<br><br><br><div style='text-align: center; color: #94a3b8; font-size: 11px; padding-bottom: 20px;'>© 2026 EMİR ERP.<br>Tüm hakları saklıdır.</div>", unsafe_allow_html=True)
        if st.session_state.get("kapat", False):
            components.html("<script>var d = window.parent.document; var s = d.querySelector('[data-testid=\"stSidebar\"]'); if (s && s.getAttribute('aria-expanded') === 'true') { var b = d.querySelector('[data-testid=\"baseButton-headerNoPadding\"]') || s.querySelector('button'); if (b) b.click(); }</script>", width=0, height=0); st.session_state["kapat"] = False

    # --- 7. SAYFA İÇERİKLERİ ---
    choice = st.session_state["choice"]
    
    # ================= DASHBOARD =================
    if choice == "🏠 Dashboard":
        if st.session_state.get("is_cust", False):
            firm_name = st.session_state["cust_firm"]
            st.markdown(f"<div class='customer-hero'><h1>Hoş Geldiniz, {firm_name}</h1><p>Makinelerinizin servis geçmişini ve detaylı analizlerini buradan şeffaf bir şekilde takip edebilirsiniz.</p></div>", unsafe_allow_html=True)
            df_all = get_supabase_data()
            if not df_all.empty:
                cust_df = df_all[df_all['Firma'] == firm_name]
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Toplam Servis İşlemi", len(cust_df))
                col_m2.metric("Toplam Harcama", f"{cust_df['Fiyat'].sum():,.2f} TL")
                col_m3.metric("Kayıtlı Makine Sayısı", cust_df['Makine'].nunique())
                st.divider()
                c_grafik1, c_grafik2 = st.columns([2, 1])
                with c_grafik1:
                    st.subheader("🚜 Makine Bazlı Servis Geçmişi")
                    for idx, row in cust_df.sort_values('Tarih', ascending=False).iterrows():
                        with st.expander(f"📍 {row['Makine']} | {row['Tarih']} | {row['Fiyat']} TL"):
                            st.write(f"**Operatör:** {row['Operatör']}")
                            st.write(f"**Süre:** {row.get('Toplam Saat', 0)} Saat ({row.get('Başlama Tarihi', '-')} {row.get('Başlama Saati', '-')} - {row.get('Bitiş Tarihi', '-')} {row.get('Bitiş Saati', '-')})")
                            st.write(f"**İşlem:** {row['Detay']}")
                            if 'Fotoğraf' in row and pd.notna(row['Fotoğraf']) and row['Fotoğraf'] != "" and os.path.exists(row['Fotoğraf']): st.image(row['Fotoğraf'], use_container_width=True)
                with c_grafik2:
                    st.subheader("📈 Harcama Dağılımı")
                    if not cust_df.empty: st.plotly_chart(px.pie(cust_df, names='Makine', values='Fiyat', hole=0.4), use_container_width=True)
                st.divider()
                st.markdown("### 🛠️ Acil Bir Durum Mu Var?")
                if st.button("📲 SERVİS TALEP ET (WHATSAPP İLE BİLDİR)", key="btn_talep"):
                    show_loader("Talep İletiliyor..."); log_islem(st.session_state['user'], "Acil Servis Talebi Gönderdi")
                    send_wa_live_bot(f"🆘 *ACİL SERVİS TALEBİ*\n\n🏢 Firma: {firm_name}\n👤 Yetkili: {st.session_state['user']}\n📅 Tarih: {datetime.date.today()}\n\nLütfen en kısa sürede iletişime geçiniz.")
                    st.success("Talebiniz ofisimize iletildi.")
            else: st.info("Sistemde firmanıza ait henüz bir kayıt bulunmuyor.")

        else:
            st.title("🏠 Dashboard")
            
            # --- YENİ EKLENEN: DEVAM EDEN İŞLER (PERSONEL İÇİN) ---
            df_devam = pd.read_csv(D_FILE)
            my_jobs = df_devam[df_devam['Ekleyen'] == st.session_state['user']]
            if not my_jobs.empty:
                st.markdown("### 🚀 Devam Eden İşlerim")
                for idx, row in my_jobs.iterrows():
                    now = datetime.datetime.now()
                    ilk_bas = datetime.datetime.fromisoformat(row['Ilk_Baslama'])
                    son_bas = datetime.datetime.fromisoformat(row['Son_Baslama'])
                    birikmis = float(row['Birikmis_Saniye'])
                    
                    if row['Durum'] == "Çalışıyor":
                        guncel_birikmis = birikmis + (now - son_bas).total_seconds()
                        durum_ikon = "🟢 Çalışıyor"
                        css_class = "active-job-card"
                    else:
                        guncel_birikmis = birikmis
                        durum_ikon = "⏸️ Molada"
                        css_class = "paused-job-card"
                        
                    guncel_saat = guncel_birikmis / 3600
                    
                    st.markdown(f"<div class='{css_class}'><b>{row['Firma']} - {row['Makine']}</b><br>Durum: {durum_ikon} | Biriken Süre: {guncel_saat:.2f} Saat</div>", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    if row['Durum'] == "Çalışıyor":
                        if c1.button("⏸️ Mola Ver", key=f"mola_{row['id']}", use_container_width=True):
                            df_devam.at[idx, 'Durum'] = "Molada"
                            df_devam.at[idx, 'Birikmis_Saniye'] = guncel_birikmis
                            df_devam.to_csv(D_FILE, index=False)
                            st.rerun()
                    else:
                        if c1.button("▶️ İşe Devam Et", key=f"devam_{row['id']}", use_container_width=True):
                            df_devam.at[idx, 'Durum'] = "Çalışıyor"
                            df_devam.at[idx, 'Son_Baslama'] = now.isoformat()
                            df_devam.to_csv(D_FILE, index=False)
                            st.rerun()
                            
                    if c2.button("✅ İşi Bitir (Buluta Gönder)", key=f"bitir_{row['id']}", use_container_width=True):
                        show_loader("İş bitiriliyor ve Supabase'e aktarılıyor...")
                        # Son zaman hesaplamaları
                        if row['Durum'] == "Çalışıyor":
                            final_saniye = birikmis + (now - son_bas).total_seconds()
                        else:
                            final_saniye = birikmis
                            
                        toplam_saat = round(final_saniye / 3600, 2)
                        
                        payload = {
                            "tarih": str(now.date()),
                            "firma": row['Firma'],
                            "makine": row['Makine'],
                            "operator": row['Operatör'],
                            "fiyat": float(row['Fiyat']),
                            "detay": row['Detay'],
                            "baslama_tarihi": str(ilk_bas.date()),
                            "bitis_tarihi": str(now.date()),
                            "baslama_saati": str(ilk_bas.time())[:5],
                            "bitis_saati": str(now.time())[:5],
                            "toplam_saat": float(toplam_saat),
                            "ekleyen": st.session_state["user"],
                            "cihaz": get_device_info(),
                            "fotograf": row['Foto_Yolu']
                        }
                        
                        try:
                            supabase.table("satislar").insert(payload).execute()
                            # İş başarıyla buluta gittiyse, yerel devam edenlerden sil
                            df_devam = df_devam.drop(idx)
                            df_devam.to_csv(D_FILE, index=False)
                            
                            log_islem(st.session_state['user'], f"Canlı İş Bitirdi: {row['Firma']}")
                            send_wa_live_bot(f"🚨 *YAPIKUR ERP - CANLI İŞ TAMAMLANDI*\n\n👨‍💻 Ekleyen: {st.session_state['user']}\n🏢 Firma: {row['Firma']}\n🚜 Makine: {row['Makine']}\n👷 Operatör: {row['Operatör']}\n⏱️ Toplam Çalışma: {toplam_saat} Saat\n💰 Tutar: {row['Fiyat']:,.2f} TL\n📝 İşlem: {row['Detay']}")
                            st.success("İş başarıyla tamamlandı ve raporlara işlendi!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Buluta aktarırken hata: {e}")
                
                st.divider()

            with open(N_FILE, "r", encoding="utf-8") as f: note_content = f.read()
            if st.session_state["can_edit_dash"]:
                st.markdown("### 🗒️ Yönetici Panosu Notları")
                custom_toolbar = [[{'header': [1, 2, 3, 4, 5, 6, False]}], ['bold', 'italic', 'underline', 'strike'], [{'color': []}, {'background': []}], [{'list': 'ordered'}, {'list': 'bullet'}], ['clean']]
                new_notes = st_quill(value=note_content, html=True, toolbar=custom_toolbar, key="quill_editor")
                if st.button("💾 Notları Kaydet", key="btn_not_kaydet"):
                    if new_notes is not None:
                        show_loader("Notlar Kaydediliyor..."); log_islem(st.session_state['user'], "Dashboard Notlarını Güncelledi")
                        with open(N_FILE, "w", encoding="utf-8") as f: f.write(new_notes)
                        st.success("✅ Güncellendi."); time.sleep(0.5); st.rerun()
            else:
                st.info("💡 Notları görüntüleme yetkiniz var ancak düzenleme yetkiniz bulunmuyor.")
                st.markdown(f"<div class='readonly-box'>{note_content}</div>", unsafe_allow_html=True)

    # ================= AKILLI ASİSTAN =================
    elif choice == "🤖 Akıllı Asistan":
        if not st.session_state.get("can_use_ai", False): st.error("Bu sayfayı görüntüleme yetkiniz yok!"); st.stop()
        st.title("🤖 Yapay Zeka Asistanı")
        st.markdown("<div style='background-color: #e0f2fe; padding: 20px; border-radius: 10px; border-left: 5px solid #0284c7; margin-bottom: 20px;'><h4 style='color: #0284c7 !important; margin-top: 0;'>Zaman Bazlı Akıllı Sohbet</h4><p style='color: #0f172a !important; margin-bottom: 0;'>Sisteme zaman belirterek sorular sorabilirsiniz:<br> <i>\"Bu ay toplam ciro ne kadar?\", \"Bugün toplam mesai kaç saat?\"</i></p></div>", unsafe_allow_html=True)
        if "messages" not in st.session_state: st.session_state.messages = [{"role": "assistant", "content": "Merhaba ! Sisteme kayıtlı verilerle ilgili her şeyi sorabilirsin."}]
        for msg in st.session_state.messages:
            if msg["role"] == "user": st.markdown(f"<div style='display: flex; justify-content: flex-end; margin-bottom: 15px;'><div style='background-color: #2563eb; color: white; padding: 12px 18px; border-radius: 18px 18px 0 18px; max-width: 75%; font-size: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>{msg['content']}</div></div>", unsafe_allow_html=True)
            else: st.markdown(f"<div style='display: flex; justify-content: flex-start; margin-bottom: 15px;'><div style='background-color: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; padding: 12px 18px; border-radius: 18px 18px 18px 0; max-width: 75%; font-size: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>🤖 {msg['content']}</div></div>", unsafe_allow_html=True)
        if prompt := st.chat_input("Mesajınızı yazın (Örn: Bu ay toplam mesai kaç saat?)..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            cevap = akilli_asistan_cevapla(prompt, get_supabase_data())
            st.session_state.messages.append({"role": "assistant", "content": cevap}); log_islem(st.session_state['user'], "Akıllı Asistanı Kullandı"); st.rerun()

    # ================= SERVİS KAYDI =================
    elif choice == "📝 Servis Kaydı":
        st.title("📝 Servis Kaydı Merkezi")
        firma_listesi = get_list("Firma")
        operator_listesi = get_list("Operatör")
        makine_listesi = get_list("Makine")
        
        tab_canli, tab_manuel, tab_excel = st.tabs(["⏱️ Canlı İş Başlat", "✍️ Geçmiş İşi Manuel Gir", "📥 Excel Toplu Yükleme"])
        
        # 1. SEKME: CANLI İŞ BAŞLATMA
        with tab_canli:
            st.info("💡 Buradan başlattığınız işler, arka planda sayacı çalıştırır ve Dashboard'daki 'Devam Eden İşlerim' bölümüne düşer. Mola verdiğinizde süre durur, işi bitirdiğinizde net saat hesaplanıp buluta gönderilir.")
            with st.form("canli_baslat_form", clear_on_submit=True):
                col_c1, col_c2 = st.columns(2)
                c_firma = col_c1.selectbox("🏢 Firma Seçimi", firma_listesi, key="canli_firma")
                c_makine = col_c1.selectbox("🚜 Makine/Cihaz", makine_listesi, key="canli_makine")
                c_op = col_c2.selectbox("👷 Operatör", operator_listesi, key="canli_op")
                c_fiyat = col_c2.number_input("💰 Beklenen Tutar (TL)", min_value=0.0, key="canli_fiyat")
                c_detay = st.text_area("🔍 Yapılacak İşlem Özeti", key="canli_detay")
                c_foto = st.file_uploader("📸 Başlangıç Fotoğrafı (Opsiyonel)", type=['jpg', 'jpeg', 'png'], key="canli_foto")
                
                if st.form_submit_button("▶️ İŞİ BAŞLAT (SAYACI AÇ)"):
                    show_loader("İş Başlatılıyor...")
                    foto_yolu = ""
                    if c_foto is not None:
                        zaman_damgasi = int(time.time())
                        dosya_adi = f"{c_firma.replace(' ', '_')}_{zaman_damgasi}.jpg"
                        foto_yolu = os.path.join(ATTACH_DIR, dosya_adi)
                        with open(foto_yolu, "wb") as f: f.write(c_foto.getbuffer())
                    
                    now_str = datetime.datetime.now().isoformat()
                    yeni_is = pd.DataFrame([{
                        "id": str(int(time.time() * 1000)),
                        "Firma": c_firma, "Makine": c_makine, "Operatör": c_op, 
                        "Fiyat": float(c_fiyat), "Detay": c_detay, "Foto_Yolu": foto_yolu,
                        "Durum": "Çalışıyor", "Ilk_Baslama": now_str, "Son_Baslama": now_str,
                        "Birikmis_Saniye": 0.0, "Ekleyen": st.session_state["user"]
                    }])
                    
                    df_devam = pd.read_csv(D_FILE)
                    pd.concat([df_devam, yeni_is]).to_csv(D_FILE, index=False)
                    
                    log_islem(st.session_state['user'], f"Canlı İş Başlattı: {c_firma}")
                    st.success("✅ İş başlatıldı! Dashboard üzerinden sayacı kontrol edebilirsiniz.")
                    
        # 2. SEKME: MANUEL GEÇMİŞ İŞ GİRİŞİ
        with tab_manuel:
            st.info("💡 Önceden tamamlanmış, süresi bilinen geçmiş işleri buradan sisteme doğrudan işleyebilirsiniz.")
            with st.form("kayit_formu", clear_on_submit=True):
                col_f1, col_f2 = st.columns(2)
                secilen_firma = col_f1.selectbox("🏢 Firma Seçimi", firma_listesi, key="kayit_firma")
                secilen_makine = col_f1.selectbox("🚜 Makine/Cihaz", makine_listesi, key="kayit_makine")
                secilen_operator = col_f2.selectbox("👷 Operatör", operator_listesi, key="kayit_op")
                girilen_fiyat = col_f2.number_input("💰 Servis Tutarı (TL)", min_value=0.0, key="kayit_fiyat")
                secilen_tarih = st.date_input("📅 Kayıt Tarihi", key="kayit_tarih")
                
                st.markdown("---")
                col_d1, col_d2 = st.columns(2)
                bas_tarihi = col_d1.date_input("📅 İşe Başlama Tarihi", key="kayit_bas_tarih")
                bit_tarihi = col_d2.date_input("📅 İşin Bitiş Tarihi", key="kayit_bit_tarih")
                
                col_t1, col_t2 = st.columns(2)
                # Orijinal Saat Seçici Sistemi
                bas_saati = col_t1.time_input("⏰ İşe Başlama Saati", value=datetime.time(8, 0), key="kayit_bas_saati")
                bit_saati = col_t2.time_input("🏁 İşin Bitiş Saati", value=datetime.time(17, 0), key="kayit_bit_saati")
                st.markdown("---")
                
                girilen_detay = st.text_area("🔍 Yapılan İşlem Özeti", key="kayit_detay")
                secilen_foto = st.file_uploader("📸 Servis Fotoğrafı Yükle (Opsiyonel)", type=['jpg', 'jpeg', 'png'], key="kayit_foto")
                
                if st.form_submit_button("✅ GEÇMİŞ KAYDI SİSTEME İŞLE"):
                    show_loader("Servis Kaydı Buluta İşleniyor...")
                    start_dt = datetime.datetime.combine(bas_tarihi, bas_saati)
                    end_dt = datetime.datetime.combine(bit_tarihi, bit_saati)
                    toplam_saat = round((end_dt - start_dt).total_seconds() / 3600, 2) if end_dt >= start_dt else 0.0
                    
                    foto_yolu = ""
                    if secilen_foto is not None:
                        zaman_damgasi = int(time.time())
                        dosya_adi = f"{secilen_firma.replace(' ', '_')}_{zaman_damgasi}.jpg"
                        foto_yolu = os.path.join(ATTACH_DIR, dosya_adi)
                        with open(foto_yolu, "wb") as f: f.write(secilen_foto.getbuffer())

                    payload = {
                        "tarih": str(secilen_tarih), "firma": secilen_firma, "makine": secilen_makine,
                        "operator": secilen_operator, "fiyat": float(girilen_fiyat), "detay": girilen_detay,
                        "baslama_tarihi": str(bas_tarihi), "bitis_tarihi": str(bit_tarihi),
                        "baslama_saati": str(bas_saati)[:5], "bitis_saati": str(bit_saati)[:5],
                        "toplam_saat": float(toplam_saat), "ekleyen": st.session_state["user"],
                        "cihaz": get_device_info(), "fotograf": foto_yolu
                    }
                    
                    try:
                        supabase.table("satislar").insert(payload).execute()
                        log_islem(st.session_state['user'], f"Manuel Kayıt Ekledi: {secilen_firma}")
                        canli_yayin_mesaji = f"🚨 *YAPIKUR ERP - YENİ KAYIT*\n\n👨‍💻 Ekleyen: {st.session_state['user']}\n🏢 Firma: {secilen_firma}\n🚜 Makine: {secilen_makine}\n👷 Operatör: {secilen_operator}\n⏱️ Süre: {toplam_saat} Saat ({bas_tarihi} {str(bas_saati)[:5]} - {bit_tarihi} {str(bit_saati)[:5]})\n💰 Tutar: {girilen_fiyat:,.2f} TL\n📝 İşlem: {girilen_detay}"
                        send_wa_live_bot(canli_yayin_mesaji)
                        st.success("✅ Kayıt başarıyla Supabase bulutuna eklendi.")
                        st.markdown(f'<a href="{create_wa_link(secilen_firma, secilen_makine, secilen_operator, girilen_fiyat, girilen_detay, str(bas_tarihi), str(bit_tarihi), str(bas_saati)[:5], str(bit_saati)[:5], toplam_saat)}" target="_blank" class="wa-button">📲 WhatsApp ile Bilgi Gönder</a>', unsafe_allow_html=True)
                    except Exception as e: st.error(f"Kayıt eklenirken hata: {e}")

        # 3. SEKME: EXCEL TOPLU YÜKLEME
        with tab_excel:
            yuklenen_dosya = st.file_uploader("Servis Kayıtları Excel Dosyası (.xlsx)", type=['xlsx'], key="excel_upload")
            st.info("💡 Excel dosyasında 'Başlama Tarihi', 'Bitiş Tarihi', 'Başlama Saati', 'Bitiş Saati' ve 'Toplam Saat' sütunları varsa sisteme otomatik aktarılır.")
            if yuklenen_dosya and st.button("🚀 Excel'i İçeri Aktar", key="btn_excel"):
                show_loader("Excel Verileri Supabase'e Yükleniyor...")
                df_excel = pd.read_excel(yuklenen_dosya)
                records = []
                for _, r in df_excel.iterrows():
                    records.append({
                        "tarih": str(r.get("Tarih", datetime.date.today())), "firma": str(r.get("Firma", "")),
                        "makine": str(r.get("Makine", "")), "operator": str(r.get("Operatör", "")),
                        "fiyat": float(r.get("Fiyat", 0.0)), "detay": str(r.get("Detay", "")),
                        "baslama_tarihi": str(r.get("Başlama Tarihi", datetime.date.today())),
                        "bitis_tarihi": str(r.get("Bitiş Tarihi", datetime.date.today())),
                        "baslama_saati": str(r.get("Başlama Saati", "08:00:00")),
                        "bitis_saati": str(r.get("Bitiş Saati", "17:00:00")),
                        "toplam_saat": float(r.get("Toplam Saat", 0.0)),
                        "ekleyen": st.session_state["user"], "cihaz": get_device_info(),
                        "fotograf": str(r.get("Fotoğraf", ""))
                    })
                if records:
                    try:
                        supabase.table("satislar").insert(records).execute()
                        log_islem(st.session_state['user'], "Excel ile Toplu Veri Aktardı")
                        st.success("✅ Toplu veri aktarımı buluta başarıyla tamamlandı.")
                    except Exception as e: st.error(f"Aktarım Hatası: {e}")

    # ================= FİNANSAL ANALİZ VE E-POSTA =================
    elif choice == "📊 Finansal Analiz":
        st.title("📊 Finansal Analiz ve Performans Raporları")
        
        df_satislar = get_supabase_data()
        
        if not df_satislar.empty:
            df_satislar['Tarih_DT'] = pd.to_datetime(df_satislar['Tarih'], errors='coerce')
            
            st.markdown("### 🔍 Detaylı Filtreleme")
            col_filtre1, col_filtre2, col_filtre3 = st.columns(3)
            
            firmalar = ["Tümü"] + sorted(df_satislar['Firma'].dropna().unique().tolist())
            operatorler = ["Tümü"] + sorted(df_satislar['Operatör'].dropna().unique().tolist())
            
            sec_firma_filtre = col_filtre1.selectbox("Firma Filtresi", firmalar, key="filtre_firma")
            sec_op_filtre = col_filtre2.selectbox("Operatör Filtresi", operatorler, key="filtre_op")
            
            min_date = df_satislar['Tarih_DT'].min()
            max_date = df_satislar['Tarih_DT'].max()
            if pd.isnull(min_date) or pd.isnull(max_date):
                min_date, max_date = datetime.date(2023, 1, 1), datetime.date.today()
            else:
                min_date, max_date = min_date.date(), max_date.date()
                
            sec_tarih_araligi = col_filtre3.date_input("Tarih Aralığı", [min_date, max_date], key="filtre_tarih")
            
            df_filtered = df_satislar.copy()
            if sec_firma_filtre != "Tümü": df_filtered = df_filtered[df_filtered['Firma'] == sec_firma_filtre]
            if sec_op_filtre != "Tümü": df_filtered = df_filtered[df_filtered['Operatör'] == sec_op_filtre]
            if len(sec_tarih_araligi) == 2:
                s_date, e_date = sec_tarih_araligi
                df_filtered = df_filtered[(df_filtered['Tarih_DT'].dt.date >= s_date) & (df_filtered['Tarih_DT'].dt.date <= e_date)]
            
            st.divider()

            st.markdown("### 📈 Temel Performans Göstergeleri (KPI)")
            bugun = datetime.date.today()
            bu_ay_bas = bugun.replace(day=1)
            gecen_ay_son = bu_ay_bas - datetime.timedelta(days=1)
            gecen_ay_bas = gecen_ay_son.replace(day=1)
            
            df_bu_ay = df_satislar[(df_satislar['Tarih_DT'].dt.date >= bu_ay_bas) & (df_satislar['Tarih_DT'].dt.date <= bugun)]
            df_gecen_ay = df_satislar[(df_satislar['Tarih_DT'].dt.date >= gecen_ay_bas) & (df_satislar['Tarih_DT'].dt.date <= gecen_ay_son)]
            
            ciro_bu_ay, ciro_gecen_ay = df_bu_ay['Fiyat'].sum(), df_gecen_ay['Fiyat'].sum()
            fark_yuzde = ((ciro_bu_ay - ciro_gecen_ay) / ciro_gecen_ay) * 100 if ciro_gecen_ay > 0 else 100.0 if ciro_bu_ay > 0 else 0.0

            col_k1, col_k2, col_k3, col_k4 = st.columns(4)
            col_k1.metric("FİLTRELENEN CİRO", f"{df_filtered['Fiyat'].sum():,.2f} TL")
            col_k2.metric("TOPLAM MESAİ SÜRESİ", f"{df_filtered['Toplam Saat'].sum() if 'Toplam Saat' in df_filtered.columns else 0:,.2f} Saat")
            col_k3.metric("EN ÇOK KAZANDIRAN", df_filtered.groupby('Firma')['Fiyat'].sum().idxmax() if not df_filtered.empty else "-")
            col_k4.metric("EN AKTİF OPERATÖR", df_filtered.groupby('Operatör')['Fiyat'].sum().idxmax() if not df_filtered.empty else "-")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            output = io.BytesIO()
            df_export = df_filtered.drop(columns=['Tarih_DT', 'id', 'Fotoğraf'], errors='ignore')
            istenen_sira = ['Tarih', 'Başlama Tarihi', 'Başlama Saati', 'Bitiş Tarihi', 'Bitiş Saati', 'Toplam Saat', 'Firma', 'Makine', 'Operatör', 'Fiyat', 'Detay', 'Ekleyen', 'Cihaz']
            df_export = df_export[[col for col in istenen_sira if col in df_export.columns]]
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer: df_export.to_excel(writer, index=False, sheet_name='Servis Kayıtları')
            excel_verisi = output.getvalue()
            dosya_adi = f"Filtreli_Servis_Raporu_{datetime.date.today()}.xlsx"
            
            st.download_button("📥 Filtrelenen Verileri Nizami Excel Olarak İndir", data=excel_verisi, file_name=dosya_adi, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="btn_excel_indir", on_click=lambda: log_islem(st.session_state['user'], "Excel Raporu İndirdi"))
            
            with st.expander("📧 Raporu Doğrudan E-Posta Olarak Gönder"):
                alici_mail = st.text_input("Alıcı E-Posta Adresi", key="mail_alici")
                if st.button("🚀 Excel'i E-Posta At", key="btn_mail_gonder"):
                    if alici_mail:
                        show_loader("E-Posta Gönderiliyor...")
                        success, msg = send_excel_via_email(alici_mail, excel_verisi, dosya_adi)
                        if success: log_islem(st.session_state['user'], f"E-Posta Gönderdi: {alici_mail}"); st.success(f"✅ {msg}")
                        else: st.error(f"❌ {msg}")
                    else: st.warning("Geçerli bir adres girin.")

            st.divider()
            
            if not df_filtered.empty:
                st.markdown("### 📊 Görsel Analizler")
                c_g1, c_g2 = st.columns(2)
                c_g1.plotly_chart(px.bar(df_filtered, x="Firma", y="Fiyat", title="Firma Bazlı Gelir Dağılımı", template="plotly_white", color_discrete_sequence=['#2563eb']), use_container_width=True)
                if 'Toplam Saat' in df_filtered.columns and df_filtered['Toplam Saat'].sum() > 0:
                    c_g2.plotly_chart(px.pie(df_filtered, names="Operatör", values="Toplam Saat", title="Operatör Bazlı Mesai Dağılımı", template="plotly_white", hole=0.4), use_container_width=True)
                else: c_g2.plotly_chart(px.pie(df_filtered, names="Makine", values="Fiyat", title="Makine Bazlı Masraf Dağılımı", template="plotly_white", hole=0.4), use_container_width=True)
            
            st.divider()

            st.markdown("### 📋 Servis Kayıtları Listesi")
            for index, row in df_filtered.sort_values('Tarih', ascending=False).iterrows():
                benzersiz_anahtar = f"satis_{index}_{hash(str(row['Detay']))}"
                with st.expander(f"📍 {row['Firma']} | {row['Tarih']} | {row['Fiyat']} TL"):
                    col_detay, col_sil = st.columns([5, 1])
                    
                    col_detay.write(f"**Cihaz:** {row['Makine']} | **Operatör:** {row['Operatör']}")
                    t_saat = row.get('Toplam Saat', 0)
                    col_detay.write(f"**Çalışma Süresi:** {t_saat} Saat ({row.get('Başlama Tarihi','-')} {row.get('Başlama Saati','-')} / {row.get('Bitiş Tarihi','-')} {row.get('Bitiş Saati','-')})")
                    col_detay.write(f"**İşlem:** {row['Detay']}")
                    
                    if 'Fotoğraf' in row and pd.notna(row['Fotoğraf']) and row['Fotoğraf'] != "" and os.path.exists(row['Fotoğraf']): col_detay.image(row['Fotoğraf'], use_container_width=True)
                    col_detay.markdown(f"<span class='device-tag'>📱 Giriş Cihazı: {row.get('Cihaz', 'Bilinmeyen')}</span>", unsafe_allow_html=True)
                    
                    b_tar, bi_tar = str(row.get('Başlama Tarihi', '-')), str(row.get('Bitiş Tarihi', '-'))
                    b_saat_str = str(row.get('Başlama Saati', '-'))[:5] if row.get('Başlama Saati') != '-' else '-'
                    bi_saat_str = str(row.get('Bitiş Saati', '-'))[:5] if row.get('Bitiş Saati') != '-' else '-'
                        
                    col_detay.markdown(f'<a href="{create_wa_link(row["Firma"],row["Makine"],row["Operatör"],row["Fiyat"],row["Detay"], b_tar, bi_tar, b_saat_str, bi_saat_str, t_saat)}" target="_blank" class="wa-button" style="width:180px; font-size:12px; padding:6px;">📲 WhatsApp Paylaş</a>', unsafe_allow_html=True)
                    
                    if st.session_state["can_admin"]:
                        if col_sil.button("🗑️ Sil", key=f"del_btn_{benzersiz_anahtar}"):
                            show_loader("Siliniyor...")
                            try: supabase.table("satislar").delete().eq("id", row['id']).execute(); st.rerun()
                            except Exception as e: st.error(f"Hata: {e}")
        else: st.info("Veri bulunamadı.")

    # ================= YÖNETİM PANELİ =================
    elif choice == "⚙️ Yönetim Paneli":
        st.title("⚙️ Sistem Yönetimi")
        tab_users, tab_operators, tab_firms, tab_machines, tab_bot, tab_email, tab_logs = st.tabs([
            "👤 Kullanıcılar", "👷 Operatörler", "🏢 Firmalar", "🚜 Makineler", "🤖 Bot Ayarları", "📧 E-Posta", "🕵️ Loglar"
        ])
        
        with tab_users:
            users_db = pd.read_csv(U_FILE)
            firma_secenekleri = [""] + get_list("Firma")
            for idx, user_row in users_db.iterrows():
                rol_etiketi = "MÜŞTERİ" if user_row.get("is_customer", False) else "PERSONEL"
                with st.expander(f"👤 {user_row['username']} ({rol_etiketi})"):
                    col_f, col_s = st.columns([4, 1])
                    with col_f:
                        with st.form(f"edit_user_form_{idx}"):
                            e_pw = st.text_input("Şifre", value=str(user_row['password']))
                            e_cust = st.checkbox("Müşteri'dir", value=bool(user_row.get('is_customer', False)))
                            mevcut_firma = str(user_row.get('customer_firm', ''))
                            if mevcut_firma not in firma_secenekleri: mevcut_firma = ""
                            e_cust_firm = st.selectbox("Firma", firma_secenekleri, index=firma_secenekleri.index(mevcut_firma))
                            st.markdown("---")
                            e_rep = st.checkbox("Raporları Görebilir", value=bool(user_row['can_view_reports']))
                            e_dash = st.checkbox("Dashboard Düzenleyebilir", value=bool(user_row.get('can_edit_dashboard', False)))
                            e_ai = st.checkbox("Asistanı Kullanabilir", value=bool(user_row.get('can_use_assistant', False)))
                            e_ticker = st.checkbox("Canlı Bilgi Görebilir", value=bool(user_row.get('can_view_ticker', True)))
                            e_adm = st.checkbox("Yönetici", value=bool(user_row['can_manage_admin']), disabled=(user_row['username']=='admin'))
                            
                            if st.form_submit_button("🔄 Güncelle"):
                                users_db.at[idx, 'password'] = e_pw
                                users_db.at[idx, 'is_customer'] = e_cust; users_db.at[idx, 'customer_firm'] = e_cust_firm if e_cust else ""
                                users_db.at[idx, 'can_view_reports'] = e_rep; users_db.at[idx, 'can_edit_dashboard'] = e_dash; users_db.at[idx, 'can_use_assistant'] = e_ai; users_db.at[idx, 'can_view_ticker'] = e_ticker
                                if user_row['username'] != 'admin': users_db.at[idx, 'can_manage_admin'] = e_adm
                                users_db.to_csv(U_FILE, index=False); st.success("Güncellendi!"); time.sleep(0.5); st.rerun()
                    with col_s:
                        if user_row['username'] != "admin":
                            if st.button("❌ Sil", key=f"del_user_{idx}"): users_db.drop(idx).to_csv(U_FILE, index=False); st.rerun()
            
            with st.expander("➕ Yeni Ekle"):
                with st.form("new_u_form"):
                    nu, np = st.text_input("Kullanıcı Adı"), st.text_input("Şifre")
                    y_cust, y_cust_firm = st.checkbox("Müşteri Hesabı"), st.selectbox("Firma Seç", firma_secenekleri)
                    yr, yd, y_ai, y_tick, ya = st.checkbox("Rapor Görüntüleme"), st.checkbox("Dashboard Düzenleme"), st.checkbox("Akıllı Asistan"), st.checkbox("Canlı Bilgi Göstergesi", value=True), st.checkbox("Admin Yetkisi")
                    
                    if st.form_submit_button("Kaydet"):
                        pd.concat([users_db, pd.DataFrame([{ "username": nu, "password": np, "can_view_reports": yr, "can_manage_admin": ya, "can_edit_dashboard": yd, "can_use_assistant": y_ai, "can_view_ticker": y_tick, "is_customer": y_cust, "customer_firm": y_cust_firm if y_cust else "" }])]).to_csv(U_FILE, index=False)
                        st.success("Eklendi!"); time.sleep(0.5); st.rerun()

        def yonetim_listesi(liste_adi, v_tipi):
            with st.expander(f"📥 Excel'den Aktar"):
                yuklenen = st.file_uploader(f"Excel", key=f"up_{v_tipi}")
                if yuklenen and st.button("Güncelle", key=f"btn_up_{v_tipi}"):
                    pd.concat([pd.read_csv(S_FILE), pd.DataFrame([{"tip": v_tipi, "deger": str(x)} for x in pd.read_excel(yuklenen).iloc[:,0].dropna().unique()])]).to_csv(S_FILE, index=False); st.rerun()
            
            c_in, c_btn = st.columns([4, 1])
            yeni = c_in.text_input("Yeni Ekle", key=f"in_{v_tipi}")
            if c_btn.button("EKLE", key=f"add_{v_tipi}") and yeni:
                pd.concat([pd.read_csv(S_FILE), pd.DataFrame([{"tip": v_tipi, "deger": yeni}])]).to_csv(S_FILE, index=False); st.rerun()
            
            for index, eleman in enumerate(get_list(v_tipi)):
                cl1, cl2 = st.columns([7, 1])
                cl1.write(f"🔹 {eleman}")
                if cl2.button("🗑️", key=f"rm_{v_tipi}_{index}"):
                    df_a = pd.read_csv(S_FILE); df_a[~((df_a['tip'] == v_tipi) & (df_a['deger'] == eleman))].to_csv(S_FILE, index=False); st.rerun()

        with tab_operators: yonetim_listesi("Operatör", "Operatör")
        with tab_firms: yonetim_listesi("Firma", "Firma")
        with tab_machines: yonetim_listesi("Makine", "Makine")
            
        with tab_bot:
            df_ayar = pd.read_csv(S_FILE)
            for idx, abone in enumerate(df_ayar[df_ayar['tip'] == 'WA_BOT_SUB']['deger'].tolist()):
                parcalar = abone.split('|')
                if len(parcalar) == 3:
                    col_isim, col_no, col_sil = st.columns([4, 4, 2])
                    col_isim.write(f"👤 **{parcalar[0]}**"); col_no.write(f"📱 {parcalar[1]}")
                    if col_sil.button("🗑️ Sil", key=f"del_wa_{idx}"):
                        df_ayar[~((df_ayar['tip'] == 'WA_BOT_SUB') & (df_ayar['deger'] == abone))].to_csv(S_FILE, index=False); st.rerun()
            
            with st.form("yeni_wa_abone"):
                n_isim, n_phone, n_api = st.text_input("Adı"), st.text_input("No"), st.text_input("API Key", type="password")
                if st.form_submit_button("Ekle") and n_isim and n_phone and n_api:
                    pd.concat([df_ayar, pd.DataFrame([{"tip": "WA_BOT_SUB", "deger": f"{n_isim}|{n_phone}|{n_api}"}])]).to_csv(S_FILE, index=False); st.rerun()
                    
        with tab_email:
            df_ayar = pd.read_csv(S_FILE)
            email_rows, pass_rows = df_ayar[df_ayar['tip'] == 'EMAIL_ADDR'], df_ayar[df_ayar['tip'] == 'EMAIL_PASS']
            with st.form("email_ayar_formu"):
                yeni_email = st.text_input("Gmail", value=email_rows['deger'].iloc[0] if not email_rows.empty else "")
                yeni_pass = st.text_input("Şifre", value=pass_rows['deger'].iloc[0] if not pass_rows.empty else "", type="password")
                if st.form_submit_button("Kaydet"):
                    pd.concat([df_ayar[~df_ayar['tip'].isin(['EMAIL_ADDR', 'EMAIL_PASS'])], pd.DataFrame([{"tip": "EMAIL_ADDR", "deger": yeni_email}, {"tip": "EMAIL_PASS", "deger": yeni_pass}])]).to_csv(S_FILE, index=False); st.rerun()

        with tab_logs:
            if os.path.exists(L_FILE):
                df_logs = pd.read_csv(L_FILE)
                if not df_logs.empty:
                    st.dataframe(df_logs.sort_values(by=['Tarih', 'Saat'], ascending=[False, False]), use_container_width=True, hide_index=True)
                    if st.button("🗑️ Temizle"): pd.DataFrame(columns=["Tarih", "Saat", "Kullanıcı", "İşlem", "Cihaz"]).to_csv(L_FILE, index=False); st.rerun()
