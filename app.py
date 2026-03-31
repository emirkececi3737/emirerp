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
# BURAYA KENDİ BİLGİLERİNİ GİRMELİSİN EMİR
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
    </style>
    """, unsafe_allow_html=True)

# --- 3. YEREL SİSTEM DOSYALARI (AYARLAR VE LOGLAR İÇİN) ---
U_FILE = "users.csv"
S_FILE = "ayarlar.csv"
N_FILE = "notes.txt"
L_FILE = "logs.csv"
ATTACH_DIR = "attachments"

if not os.path.exists(ATTACH_DIR):
    os.makedirs(ATTACH_DIR)

def setup():
    if not os.path.exists(U_FILE):
        pd.DataFrame([{
            "username": "admin", 
            "password": "123", 
            "can_view_reports": True, 
            "can_manage_admin": True, 
            "can_edit_dashboard": True,
            "can_use_assistant": True,
            "can_view_ticker": True,
            "is_customer": False,
            "customer_firm": ""
        }]).to_csv(U_FILE, index=False)
    
    u_df = pd.read_csv(U_FILE)
    cols = ["is_customer", "customer_firm", "can_use_assistant", "can_edit_dashboard", "can_view_ticker"]
    updated = False
    for c in cols:
        if c not in u_df.columns:
            u_df[c] = False if "can" not in c else True
            if c == "can_view_ticker": u_df[c] = True
            updated = True
    if updated: 
        u_df.to_csv(U_FILE, index=False)
        
    if not os.path.exists(S_FILE):
        pd.DataFrame(columns=["tip", "deger"]).to_csv(S_FILE, index=False)
    
    if not os.path.exists(N_FILE):
        with open(N_FILE, "w", encoding="utf-8") as f: 
            f.write("<h2>Yönetici Notları</h2>")
            
    if not os.path.exists(L_FILE):
        pd.DataFrame(columns=["Tarih", "Saat", "Kullanıcı", "İşlem", "Cihaz"]).to_csv(L_FILE, index=False)

setup()

# --- 4. BULUT VERİ FONKSİYONLARI VE YARDIMCILAR ---
def get_supabase_data():
    try:
        res = supabase.table("satislar").select("*").execute()
        df = pd.DataFrame(res.data)
        if df.empty:
            return pd.DataFrame(columns=["id", "Tarih", "Firma", "Makine", "Operatör", "Fiyat", "Detay", "Ekleyen", "Cihaz", "Fotoğraf"])
        
        # Buluttaki küçük harfli sütunları programın eski sistemine uygun hale getiriyoruz (Hatasız geçiş için)
        rename_map = {
            "tarih": "Tarih", "firma": "Firma", "makine": "Makine",
            "operator": "Operatör", "fiyat": "Fiyat", "detay": "Detay",
            "ekleyen": "Ekleyen", "cihaz": "Cihaz", "fotograf": "Fotoğraf"
        }
        df = df.rename(columns=rename_map)
        return df
    except Exception as e:
        print(f"Supabase Hatası: {e}")
        return pd.DataFrame(columns=["id", "Tarih", "Firma", "Makine", "Operatör", "Fiyat", "Detay", "Ekleyen", "Cihaz", "Fotoğraf"])

def show_loader(mesaj="İşlem Yapılıyor..."):
    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        img_html = f'<img src="data:image/png;base64,{encoded_string}" style="width:160px; animation: pulse 1.5s infinite;">'
    else:
        img_html = '<div style="font-size: 90px; animation: pulse 1.5s infinite;">🏢</div>'
        
    loader_html = f"""
    <style>
    @keyframes pulse {{
        0% {{ transform: scale(0.9); opacity: 0.8; }}
        50% {{ transform: scale(1.1); opacity: 1; }}
        100% {{ transform: scale(0.9); opacity: 0.8; }}
    }}
    .full-screen-loader {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: rgba(255, 255, 255, 0.85); z-index: 999999;
        display: flex; flex-direction: column; justify-content: center; align-items: center;
        backdrop-filter: blur(8px);
    }}
    .loader-text {{
        color: #1e293b; margin-top: 30px; font-family: 'Inter', sans-serif; 
        font-weight: 800; font-size: 22px; letter-spacing: 0.5px;
    }}
    </style>
    <div class="full-screen-loader" id="loader">
        {img_html}
        <div class="loader-text">{mesaj}</div>
    </div>
    """
    ph = st.empty()
    ph.markdown(loader_html, unsafe_allow_html=True)
    time.sleep(1.2)
    ph.empty()

def log_islem(kullanici, islem):
    now = datetime.datetime.now()
    log_data = pd.DataFrame([{
        "Tarih": now.strftime("%Y-%m-%d"),
        "Saat": now.strftime("%H:%M:%S"),
        "Kullanıcı": kullanici,
        "İşlem": islem,
        "Cihaz": get_device_info()
    }])
    log_data.to_csv(L_FILE, mode='a', index=False, header=not os.path.exists(L_FILE))

def get_list(tip):
    df = pd.read_csv(S_FILE)
    return sorted(df[df["tip"] == tip]["deger"].unique().tolist())

def create_wa_link(firma, makine, op, fiyat, detay):
    msg = f"📋 *YENİ SERVİS KAYDI*\n\n🏢 *Firma:* {firma}\n🚜 *Makine:* {makine}\n👷 *Operatör:* {op}\n💰 *Tutar:* {fiyat:,.2f} TL\n📝 *İşlem:* {detay}"
    return f"https://wa.me/?text={urllib.parse.quote(msg)}"

def get_device_info():
    ua_string = st.context.headers.get("User-Agent", "")
    ua = parse(ua_string)
    d_type = "Mobil" if ua.is_mobile else "Masaüstü"
    return f"{d_type} ({ua.os.family})"

def send_wa_live_bot(mesaj):
    try:
        df_a = pd.read_csv(S_FILE)
        aboneler = df_a[df_a['tip'] == 'WA_BOT_SUB']['deger'].tolist()
        
        # Eski sistem uyumluluğu
        p_old_series = df_a[df_a['tip'] == 'BOT_PHONE']['deger']
        k_old_series = df_a[df_a['tip'] == 'BOT_APIKEY']['deger']
        p_old = p_old_series.iloc[0] if not p_old_series.empty else None
        k_old = k_old_series.iloc[0] if not k_old_series.empty else None
        
        if p_old and k_old:
            aboneler.append(f"Eski Sistem|{p_old}|{k_old}")
            
        for abone in aboneler:
            parcalar = abone.split('|')
            if len(parcalar) == 3:
                # Numaradaki boşlukları ve "+" işaretini zorla siliyoruz
                p = str(parcalar[1]).strip().replace(" ", "").replace("+", "")
                k = str(parcalar[2]).strip()
                
                # CallMeBot API'sine istek at
                url = f"https://api.callmebot.com/whatsapp.php?phone={p}&text={urllib.parse.quote(mesaj)}&apikey={k}"
                res = requests.get(url, timeout=10)
                
                # Eğer sunucudan olumsuz yanıt gelirse arka planda uyar
                if res.status_code != 200:
                    print(f"⚠️ CallMeBot İletim Hatası ({p}): {res.text}")
                    
    except Exception as e: 
        print(f"🚨 SİSTEM HATASI (WhatsApp Çoklu Bot): {str(e)}")

def send_excel_via_email(receiver_email, excel_bytes, filename):
    try:
        df_ayar = pd.read_csv(S_FILE)
        s_email = df_ayar[df_ayar['tip'] == 'EMAIL_ADDR']['deger'].iloc[0] if not df_ayar[df_ayar['tip'] == 'EMAIL_ADDR'].empty else None
        s_pass = df_ayar[df_ayar['tip'] == 'EMAIL_PASS']['deger'].iloc[0] if not df_ayar[df_ayar['tip'] == 'EMAIL_PASS'].empty else None
        
        if not s_email or not s_pass: 
            return False, "E-posta ayarları Yönetim Panelinden yapılmamış!"
        
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
    except Exception as e: 
        return False, f"Gönderim hatası: {str(e)}"

def akilli_asistan_cevapla(soru, df):
    soru = soru.lower()
    if df.empty: 
        return "Sistemde henüz analiz edilecek kayıtlı veri bulunmuyor ."
    
    df['Tarih_DT'] = pd.to_datetime(df['Tarih'], errors='coerce')
    bugun = datetime.date.today()
    zaman_etiketi = "Genel"
    
    if "bugün" in soru or "bugun" in soru:
        df = df[df['Tarih_DT'].dt.date == bugun]
        zaman_etiketi = "Bugün"
    elif "bu ay" in soru:
        df = df[(df['Tarih_DT'].dt.year == bugun.year) & (df['Tarih_DT'].dt.month == bugun.month)]
        zaman_etiketi = "Bu ay"
    elif "geçen ay" in soru or "gecen ay" in soru:
        gecen_ay_son = bugun.replace(day=1) - datetime.timedelta(days=1)
        df = df[(df['Tarih_DT'].dt.year == gecen_ay_son.year) & (df['Tarih_DT'].dt.month == gecen_ay_son.month)]
        zaman_etiketi = "Geçen ay"
    elif "bu yıl" in soru or "bu sene" in soru:
        df = df[df['Tarih_DT'].dt.year == bugun.year]
        zaman_etiketi = "Bu yıl"

    if df.empty: 
        return f"Belirttiğin zaman diliminde ({zaman_etiketi}) sisteme girilmiş hiçbir veri bulamadım."

    if "ciro" in soru or "ne kadar" in soru or "toplam" in soru:
        return f"💰 {zaman_etiketi} toplam ciro: **{df['Fiyat'].sum():,.2f} TL**"
    elif "kazandıran" in soru or "iyi firma" in soru or "hangi firma" in soru:
        firma = df.groupby('Firma')['Fiyat'].sum().idxmax()
        tutar = df.groupby('Firma')['Fiyat'].sum().max()
        return f"🏢 {zaman_etiketi} en çok kazandıran firma **{firma}** (Toplam {tutar:,.2f} TL)."
    elif "aktif" in soru or "operatör" in soru or "kim" in soru:
        op = df['Operatör'].value_counts().idxmax()
        is_sayisi = df['Operatör'].value_counts().max()
        return f"👷 {zaman_etiketi} en aktif operatör **{op}** (Toplam {is_sayisi} işlem)."
    elif "masraf" in soru or "arızalı" in soru or "makine" in soru:
        makine = df.groupby('Makine')['Fiyat'].sum().idxmax()
        tutar = df.groupby('Makine')['Fiyat'].sum().max()
        return f"🚜 {zaman_etiketi} en çok masraf çıkaran makine **{makine}** (Toplam {tutar:,.2f} TL)."
    elif "son kayıt" in soru or "en son" in soru:
        son = df.iloc[-1]
        return f"📅 Son işlem: **{son['Firma']}** firmasına **{son['Operatör']}** tarafından **{son['Makine']}** için yapılmış. Tutar: {son['Fiyat']} TL."
    else:
        return "🤖 Üzgünüm , anlayamadım. Zaman ekleyerek ciro, firma veya aktif operatörleri sorabilirsin."

# --- 5. GİRİŞ VE OTURUM KONTROLÜ ---
if "logged_in" not in st.session_state:
    u, p = cookies.get("saved_user"), cookies.get("saved_pass")
    if u and p:
        users = pd.read_csv(U_FILE)
        match = users[(users['username'] == u) & (users['password'].astype(str) == p)]
        if not match.empty:
            r = match.iloc[0]
            st.session_state.update({
                "logged_in": True, "user": u, 
                "can_view": bool(r["can_view_reports"]), 
                "can_admin": bool(r["can_manage_admin"]), 
                "can_edit_dash": bool(r.get("can_edit_dashboard", False)), 
                "can_use_ai": bool(r.get("can_use_assistant", False)), 
                "can_view_ticker": bool(r.get("can_view_ticker", True)),
                "is_cust": bool(r.get("is_customer", False)), 
                "cust_firm": str(r.get("customer_firm", ""))
            })
        else: st.session_state["logged_in"] = False
    else: st.session_state["logged_in"] = False

# --- 5.1 CANLI BİLGİ EKRANI (HAYALET MOD) ---
if st.session_state.get("logged_in") and st.session_state.get("can_view_ticker", False):
    components.html("""
        <script>
            var doc = window.parent.document;
            if (!doc.getElementById("live-ticker")) {
                var ticker = doc.createElement("div");
                ticker.id = "live-ticker";
                ticker.style.cssText = "position: fixed; top: 65px; right: 15px; pointer-events: none; background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(10px); color: #f8fafc; padding: 8px 15px; border-radius: 50px; font-family: 'Inter', sans-serif; font-size: 12px; font-weight: 700; z-index: 9999999; display: flex; gap: 15px; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1);";
                
                ticker.innerHTML = `
                    <div style="display: flex; align-items: center;">
                        <div style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 10px #22c55e; animation: pulse 1.5s infinite;"></div>
                    </div>
                    <div id="t-weather" style="margin-left: 5px;">🌤️ Kastamonu: Yükleniyor...</div>
                    <div id="t-usd" style="color:#4ade80;">💵 USD: --</div>
                    <div id="t-eur" style="color:#60a5fa;">💶 EUR: --</div>
                `;
                doc.body.appendChild(ticker);

                if (!doc.getElementById("ticker-styles")) {
                    var style = doc.createElement('style');
                    style.id = "ticker-styles";
                    style.innerHTML = `@keyframes pulse { 0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); } 70% { transform: scale(1.2); box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); } 100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); } }`;
                    doc.head.appendChild(style);
                }

                function updateData() {
                    fetch('https://api.open-meteo.com/v1/forecast?latitude=41.378&longitude=33.7753&current_weather=true')
                        .then(r => r.json())
                        .then(data => {
                            doc.getElementById('t-weather').innerHTML = '🌤️ Kastamonu: ' + data.current_weather.temperature + '°C';
                        }).catch(e => console.log(e));
                    
                    fetch('https://api.exchangerate-api.com/v4/latest/USD')
                        .then(r => r.json())
                        .then(data => {
                            doc.getElementById('t-usd').innerHTML = '💵 Dolar: ' + data.rates.TRY.toFixed(2) + ' ₺';
                        });
                    fetch('https://api.exchangerate-api.com/v4/latest/EUR')
                        .then(r => r.json())
                        .then(data => {
                            doc.getElementById('t-eur').innerHTML = '💶 Euro: ' + data.rates.TRY.toFixed(2) + ' ₺';
                        });
                }
                
                updateData();
                setInterval(updateData, 180000); 
            }
        </script>
    """, height=0, width=0)
else:
    components.html("""
        <script>
            var doc = window.parent.document;
            var ticker = doc.getElementById("live-ticker");
            if (ticker) { ticker.remove(); }
        </script>
    """, height=0, width=0)

if not st.session_state.get("logged_in"):
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if os.path.exists(LOGO_PATH):
        col_logo1, col_logo2, col_logo3 = st.columns([2, 1, 2])
        with col_logo2:
            st.image(LOGO_PATH, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align:center; color:#2563eb !important;'>🏢 EMİR ERP</h1>", unsafe_allow_html=True)
        
    col1, col_login, col3 = st.columns([1, 1, 1])
    with col_login:
        with st.form("login_panel"):
            u_in = st.text_input("Kullanıcı Adı")
            p_in = st.text_input("Şifre", type="password")
            rem = st.checkbox("Beni Hatırla (Girişi Sakla)")
            
            if st.form_submit_button("SİSTEME GİRİŞ YAP"):
                users = pd.read_csv(U_FILE)
                match = users[(users['username'] == u_in) & (users['password'].astype(str) == p_in)]
                if not match.empty:
                    show_loader("Sisteme Giriş Yapılıyor...")
                    log_islem(u_in, "Sisteme Giriş Yaptı")
                    r = match.iloc[0]
                    if rem: 
                        cookies["saved_user"] = u_in
                        cookies["saved_pass"] = p_in
                        cookies.save()
                    st.session_state.update({
                        "logged_in": True, "user": u_in, 
                        "can_view": bool(r["can_view_reports"]), 
                        "can_admin": bool(r["can_manage_admin"]), 
                        "can_edit_dash": bool(r.get("can_edit_dashboard", False)), 
                        "can_use_ai": bool(r.get("can_use_assistant", False)), 
                        "can_view_ticker": bool(r.get("can_view_ticker", True)),
                        "is_cust": bool(r.get("is_customer", False)), 
                        "cust_firm": str(r.get("customer_firm", "")), 
                        "choice": "🏠 Dashboard"
                    })
                    st.rerun()
                else: 
                    st.error("❌ Kullanıcı adı veya şifre hatalı!")
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
            if st.button("🏠 Müşteri Panosu", use_container_width=True):
                show_loader("Pano Yükleniyor...")
                st.session_state["choice"] = "🏠 Dashboard"
                st.session_state["kapat"] = True
                st.rerun()
            st.info(f"📍 Bağlı Firma: {st.session_state['cust_firm']}")
            
        else:
            if st.button("🏠 Dashboard", use_container_width=True):
                show_loader("Dashboard Yükleniyor...")
                st.session_state["choice"] = "🏠 Dashboard"
                st.session_state["kapat"] = True
                st.rerun()
                
            if st.session_state.get("can_use_ai", False):
                if st.button("🤖 Akıllı Asistan", use_container_width=True):
                    show_loader("Yapay Zeka Bağlanıyor...")
                    st.session_state["choice"] = "🤖 Akıllı Asistan"
                    st.session_state["kapat"] = True
                    st.rerun()
                
            if st.button("📝 Servis Kaydı", use_container_width=True):
                show_loader("Kayıt Ekranı Yükleniyor...")
                st.session_state["choice"] = "📝 Servis Kaydı"
                st.session_state["kapat"] = True
                st.rerun()
                
            if st.session_state["can_view"]:
                if st.button("📊 Finansal Analiz", use_container_width=True):
                    show_loader("Raporlar Hazırlanıyor...")
                    st.session_state["choice"] = "📊 Finansal Analiz"
                    st.session_state["kapat"] = True
                    st.rerun()
                    
            if st.session_state["can_admin"]:
                if st.button("⚙️ Yönetim Paneli", use_container_width=True):
                    show_loader("Sistem Yönetimi Yükleniyor...")
                    st.session_state["choice"] = "⚙️ Yönetim Paneli"
                    st.session_state["kapat"] = True
                    st.rerun()
        
        st.divider()
        
        if st.button("🚪 GÜVENLİ ÇIKIŞ"):
            show_loader("Sistemden Güvenle Çıkılıyor...")
            log_islem(st.session_state['user'], "Sistemden Çıkış Yaptı")
            if "saved_user" in cookies: del cookies["saved_user"]
            if "saved_pass" in cookies: del cookies["saved_pass"]
            cookies.save()
            st.session_state["logged_in"] = False
            st.rerun()

        if st.session_state.get("kapat", False):
            components.html("""
                <script>
                    var doc = window.parent.document;
                    var sidebar = doc.querySelector('[data-testid="stSidebar"]');
                    if (sidebar && sidebar.getAttribute('aria-expanded') === 'true') {
                        var closeBtn = doc.querySelector('[data-testid="baseButton-headerNoPadding"]') || sidebar.querySelector('button');
                        if (closeBtn) closeBtn.click();
                    }
                </script>
            """, width=0, height=0)
            st.session_state["kapat"] = False

    # --- 7. SAYFA İÇERİKLERİ ---
    choice = st.session_state["choice"]
    
    # ================= DASHBOARD (MÜŞTERİ VE PERSONEL GÖRÜNÜMÜ) =================
    if choice == "🏠 Dashboard":
        if st.session_state.get("is_cust", False):
            firm_name = st.session_state["cust_firm"]
            st.markdown(f"""
                <div class='customer-hero'>
                    <h1>Hoş Geldiniz, {firm_name}</h1>
                    <p>Makinelerinizin servis geçmişini ve detaylı analizlerini buradan şeffaf bir şekilde takip edebilirsiniz.</p>
                </div>
            """, unsafe_allow_html=True)
            
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
                            st.write(f"**İşlem:** {row['Detay']}")
                            if 'Fotoğraf' in row and pd.notna(row['Fotoğraf']) and row['Fotoğraf'] != "" and os.path.exists(row['Fotoğraf']):
                                st.image(row['Fotoğraf'], caption="İşlem Kanıt Fotoğrafı", use_container_width=True)
                
                with c_grafik2:
                    st.subheader("📈 Harcama Dağılımı")
                    if not cust_df.empty:
                        fig = px.pie(cust_df, names='Makine', values='Fiyat', hole=0.4)
                        st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                st.markdown("### 🛠️ Acil Bir Durum Mu Var?")
                if st.button("📲 SERVİS TALEP ET (WHATSAPP İLE BİLDİR)"):
                    show_loader("Talep İletiliyor...")
                    log_islem(st.session_state['user'], "Acil Servis Talebi Gönderdi")
                    talep_mesaji = f"🆘 *ACİL SERVİS TALEBİ*\n\n🏢 Firma: {firm_name}\n👤 Yetkili: {st.session_state['user']}\n📅 Tarih: {datetime.date.today()}\n\nLütfen en kısa sürede bizimle iletişime geçiniz."
                    send_wa_live_bot(talep_mesaji)
                    st.success("Talebiniz başarıyla merkez ofisimize iletildi. Yetkililerimiz en kısa sürede dönüş yapacaktır.")
            else:
                st.info("Sistemde firmanıza ait henüz bir kayıt bulunmuyor.")

        else:
            st.title("🏠 Dashboard")
            st.markdown("Sisteme hoş geldiniz. Sol menüyü kullanarak işlemlere başlayabilirsiniz.")
            st.divider()
            
            with open(N_FILE, "r", encoding="utf-8") as f: 
                note_content = f.read()
            
            if st.session_state["can_edit_dash"]:
                st.markdown("### 🗒️ Yönetici Panosu Notları")
                custom_toolbar = [[{'header': [1, 2, 3, 4, 5, 6, False]}], ['bold', 'italic', 'underline', 'strike'], [{'color': []}, {'background': []}], [{'list': 'ordered'}, {'list': 'bullet'}], ['clean']]
                new_notes = st_quill(value=note_content, html=True, toolbar=custom_toolbar, key="quill_editor")
                
                if st.button("💾 Notları Kaydet"):
                    if new_notes is not None:
                        show_loader("Notlar Kaydediliyor...")
                        log_islem(st.session_state['user'], "Dashboard Notlarını Güncelledi")
                        with open(N_FILE, "w", encoding="utf-8") as f: 
                            f.write(new_notes)
                        st.success("✅ Dashboard notları başarıyla güncellendi.")
                        time.sleep(0.5)
                        st.rerun()
            else:
                st.markdown(f"<div class='readonly-box'>{note_content}</div>", unsafe_allow_html=True)

    # ================= AKILLI ASİSTAN =================
    elif choice == "🤖 Akıllı Asistan":
        if not st.session_state.get("can_use_ai", False):
            st.error("Bu sayfayı görüntüleme yetkiniz yok!")
            st.stop()
            
        st.title("🤖 Yapay Zeka Asistanı")

        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "Merhaba ! Sisteme kayıtlı verilerle ilgili bana dilediğin zamanı belirterek her şeyi sorabilirsin."}]
            
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                    <div style='display: flex; justify-content: flex-end; margin-bottom: 15px;'>
                        <div style='background-color: #2563eb; color: white; padding: 12px 18px; border-radius: 18px 18px 0 18px; max-width: 75%; font-size: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            {msg['content']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div style='display: flex; justify-content: flex-start; margin-bottom: 15px;'>
                        <div style='background-color: #ffffff; color: #1e293b; border: 1px solid #e2e8f0; padding: 12px 18px; border-radius: 18px 18px 18px 0; max-width: 75%; font-size: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>
                            🤖 {msg['content']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
        if prompt := st.chat_input("Mesajınızı yazın (Örn: Bu ay ciro ne kadar?)..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            df_bot = get_supabase_data()
            cevap = akilli_asistan_cevapla(prompt, df_bot)
                
            st.session_state.messages.append({"role": "assistant", "content": cevap})
            log_islem(st.session_state['user'], "Akıllı Asistanı Kullandı")
            st.rerun()

    # ================= SERVİS KAYDI =================
    elif choice == "📝 Servis Kaydı":
        st.title("📝 Servis Kaydı")
        firma_listesi = get_list("Firma")
        operator_listesi = get_list("Operatör")
        makine_listesi = get_list("Makine")
        
        tab_manuel, tab_excel = st.tabs(["✍️ Manuel Veri Girişi", "📥 Excel Toplu Yükleme"])
        
        with tab_manuel:
            with st.form("kayit_formu", clear_on_submit=True):
                col_f1, col_f2 = st.columns(2)
                secilen_firma = col_f1.selectbox("🏢 Firma Seçimi", firma_listesi)
                secilen_makine = col_f1.selectbox("🚜 Makine/Cihaz", makine_listesi)
                secilen_operator = col_f2.selectbox("👷 Operatör", operator_listesi)
                girilen_fiyat = col_f2.number_input("💰 Servis Tutarı (TL)", min_value=0.0)
                secilen_tarih = st.date_input("📅 İşlem Tarihi")
                girilen_detay = st.text_area("🔍 Yapılan İşlem Özeti")
                secilen_foto = st.file_uploader("📸 Servis Fotoğrafı Yükle (Kanıt Görüntüsü - Opsiyonel)", type=['jpg', 'jpeg', 'png'])
                
                if st.form_submit_button("✅ KAYDI SİSTEME İŞLE"):
                    show_loader("Servis Kaydı Buluta İşleniyor...")
                    foto_yolu = ""
                    if secilen_foto is not None:
                        zaman_damgasi = int(time.time())
                        dosya_adi = f"{secilen_firma.replace(' ', '_')}_{zaman_damgasi}.jpg"
                        foto_yolu = os.path.join(ATTACH_DIR, dosya_adi)
                        with open(foto_yolu, "wb") as f:
                            f.write(secilen_foto.getbuffer())

                    cihaz_bilgisi = get_device_info()
                    payload = {
                        "tarih": str(secilen_tarih),
                        "firma": secilen_firma,
                        "makine": secilen_makine,
                        "operator": secilen_operator,
                        "fiyat": float(girilen_fiyat),
                        "detay": girilen_detay,
                        "ekleyen": st.session_state["user"],
                        "cihaz": cihaz_bilgisi,
                        "fotograf": foto_yolu
                    }
                    
                    try:
                        supabase.table("satislar").insert(payload).execute()
                        log_islem(st.session_state['user'], f"Servis Kaydı Ekledi: {secilen_firma} - {girilen_fiyat} TL")
                        
                        canli_yayin_mesaji = f"🚨 *YAPIKUR ERP - YENİ KAYIT*\n\n👨‍💻 Ekleyen: {st.session_state['user']}\n🏢 Firma: {secilen_firma}\n🚜 Makine: {secilen_makine}\n👷 Operatör: {secilen_operator}\n💰 Tutar: {girilen_fiyat:,.2f} TL\n📝 İşlem: {girilen_detay}"
                        send_wa_live_bot(canli_yayin_mesaji)

                        st.success("✅ Kayıt başarıyla Supabase bulutuna eklendi.")
                        st.markdown(f'<a href="{create_wa_link(secilen_firma, secilen_makine, secilen_operator, girilen_fiyat, girilen_detay)}" target="_blank" class="wa-button">📲 WhatsApp ile Bilgi Gönder</a>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Kayıt eklenirken hata oluştu: {e}")

        with tab_excel:
            yuklenen_dosya = st.file_uploader("Servis Kayıtları Excel Dosyası (.xlsx)", type=['xlsx'])
            if yuklenen_dosya and st.button("🚀 Excel'i İçeri Aktar"):
                show_loader("Excel Verileri Supabase'e Yükleniyor...")
                df_excel = pd.read_excel(yuklenen_dosya)
                
                records = []
                for _, r in df_excel.iterrows():
                    records.append({
                        "tarih": str(r.get("Tarih", datetime.date.today())),
                        "firma": str(r.get("Firma", "")),
                        "makine": str(r.get("Makine", "")),
                        "operator": str(r.get("Operatör", "")),
                        "fiyat": float(r.get("Fiyat", 0.0)),
                        "detay": str(r.get("Detay", "")),
                        "ekleyen": st.session_state["user"],
                        "cihaz": get_device_info(),
                        "fotograf": str(r.get("Fotoğraf", ""))
                    })
                
                if records:
                    try:
                        supabase.table("satislar").insert(records).execute()
                        log_islem(st.session_state['user'], "Excel ile Toplu Veri Aktardı")
                        st.success("✅ Toplu veri aktarımı buluta başarıyla tamamlandı.")
                    except Exception as e:
                        st.error(f"Aktarım Hatası: {e}")

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
            
            sec_firma_filtre = col_filtre1.selectbox("Firma Filtresi", firmalar)
            sec_op_filtre = col_filtre2.selectbox("Operatör Filtresi", operatorler)
            
            min_date = df_satislar['Tarih_DT'].min()
            max_date = df_satislar['Tarih_DT'].max()
            if pd.isnull(min_date) or pd.isnull(max_date):
                min_date, max_date = datetime.date(2023, 1, 1), datetime.date.today()
            else:
                min_date, max_date = min_date.date(), max_date.date()
                
            sec_tarih_araligi = col_filtre3.date_input("Tarih Aralığı", [min_date, max_date])
            
            df_filtered = df_satislar.copy()
            if sec_firma_filtre != "Tümü": 
                df_filtered = df_filtered[df_filtered['Firma'] == sec_firma_filtre]
            if sec_op_filtre != "Tümü": 
                df_filtered = df_filtered[df_filtered['Operatör'] == sec_op_filtre]
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
            
            ciro_bu_ay = df_bu_ay['Fiyat'].sum()
            ciro_gecen_ay = df_gecen_ay['Fiyat'].sum()
            
            fark_yuzde = 0.0
            if ciro_gecen_ay > 0: 
                fark_yuzde = ((ciro_bu_ay - ciro_gecen_ay) / ciro_gecen_ay) * 100
            elif ciro_bu_ay > 0: 
                fark_yuzde = 100.0

            col_k1, col_k2, col_k3, col_k4 = st.columns(4)
            col_k1.metric("FİLTRELENEN CİRO", f"{df_filtered['Fiyat'].sum():,.2f} TL")
            col_k2.metric("BU AYKİ TOPLAM CİRO", f"{ciro_bu_ay:,.2f} TL", f"{fark_yuzde:.1f}% (Geçen Aya Göre)")
            
            en_iyi_firma = df_filtered.groupby('Firma')['Fiyat'].sum().idxmax() if not df_filtered.empty else "-"
            en_iyi_op = df_filtered.groupby('Operatör')['Fiyat'].sum().idxmax() if not df_filtered.empty else "-"
            
            col_k3.metric("EN ÇOK KAZANDIRAN FİRMA", en_iyi_firma)
            col_k4.metric("EN AKTİF OPERATÖR", en_iyi_op)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            output = io.BytesIO()
            df_export = df_filtered.drop(columns=['Tarih_DT'], errors='ignore')
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Servis Kayıtları')
            excel_verisi = output.getvalue()
            dosya_adi = f"Filtreli_Servis_Raporu_{datetime.date.today()}.xlsx"
            
            st.download_button(
                label="📥 Filtrelenen Verileri Nizami Excel Olarak İndir",
                data=excel_verisi,
                file_name=dosya_adi,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                on_click=lambda: log_islem(st.session_state['user'], "Excel Raporu İndirdi")
            )
            
            with st.expander("📧 Raporu Doğrudan E-Posta Olarak Gönder"):
                alici_mail = st.text_input("Alıcı E-Posta Adresi (Örn: muhasebe@sirket.com)")
                if st.button("🚀 Excel'i E-Posta At"):
                    if alici_mail:
                        show_loader("E-Posta Gönderiliyor...")
                        success, msg = send_excel_via_email(alici_mail, excel_verisi, dosya_adi)
                        if success:
                            log_islem(st.session_state['user'], f"E-Posta Gönderdi: {alici_mail}")
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"❌ {msg}")
                    else:
                        st.warning("Lütfen geçerli bir e-posta adresi girin.")

            st.divider()
            
            if not df_filtered.empty:
                st.markdown("### 📊 Görsel Analizler")
                c_g1, c_g2 = st.columns(2)
                fig_firma = px.bar(df_filtered, x="Firma", y="Fiyat", title="Firma Bazlı Gelir Dağılımı", template="plotly_white", color_discrete_sequence=['#2563eb'])
                c_g1.plotly_chart(fig_firma, use_container_width=True)
                
                fig_makine = px.pie(df_filtered, names="Makine", values="Fiyat", title="Makine Bazlı Masraf/Gelir Dağılımı", template="plotly_white", hole=0.4)
                c_g2.plotly_chart(fig_makine, use_container_width=True)
            
            st.divider()

            st.markdown("### 📋 Servis Kayıtları Listesi")
            for index, row in df_filtered.sort_values('Tarih', ascending=False).iterrows():
                benzersiz_anahtar = f"satis_{index}_{hash(str(row['Detay']))}"
                with st.expander(f"📍 {row['Firma']} | {row['Tarih']} | {row['Fiyat']} TL"):
                    col_detay, col_sil = st.columns([5, 1])
                    cihaz_metni = row['Cihaz'] if 'Cihaz' in row and pd.notna(row['Cihaz']) else "Bilinmeyen"
                    
                    col_detay.write(f"**Cihaz:** {row['Makine']} | **Operatör:** {row['Operatör']}")
                    col_detay.write(f"**İşlem:** {row['Detay']}")
                    
                    if 'Fotoğraf' in row and pd.notna(row['Fotoğraf']) and row['Fotoğraf'] != "" and os.path.exists(row['Fotoğraf']):
                        col_detay.image(row['Fotoğraf'], caption="İşlem Kanıt Fotoğrafı", use_container_width=True)
                        
                    col_detay.markdown(f"<span class='device-tag'>📱 Giriş Cihazı: {cihaz_metni}</span>", unsafe_allow_html=True)
                    col_detay.markdown(f'<a href="{create_wa_link(row["Firma"],row["Makine"],row["Operatör"],row["Fiyat"],row["Detay"])}" target="_blank" class="wa-button" style="width:180px; font-size:12px; padding:6px;">📲 WhatsApp Paylaş</a>', unsafe_allow_html=True)
                    
                    if st.session_state["can_admin"]:
                        if col_sil.button("🗑️ Sil", key=f"del_btn_{benzersiz_anahtar}"):
                            show_loader("Kayıt Buluttan Siliniyor...")
                            log_islem(st.session_state['user'], f"Kayıt Sildi: {row['Firma']} - {row['Fiyat']} TL")
                            try:
                                supabase.table("satislar").delete().eq("id", row['id']).execute()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Silme Hatası: {e}")
        else:
            st.info("Sistemde henüz analiz edilecek kayıtlı veri bulunmuyor.")

    # ================= YÖNETİM PANELİ =================
    elif choice == "⚙️ Yönetim Paneli":
        st.title("⚙️ Sistem Yönetimi")
        tab_users, tab_operators, tab_firms, tab_machines, tab_bot, tab_email, tab_logs = st.tabs([
            "👤 Kullanıcılar/Müşteriler", "👷 Operatörler", "🏢 Firmalar", "🚜 Makineler", "🤖 Bot Ayarları", "📧 E-Posta", "🕵️ Sistem Logları"
        ])
        
        # --- KULLANICI YETKİLERİ VE MÜŞTERİ YÖNETİMİ ---
        with tab_users:
            users_db = pd.read_csv(U_FILE)
            firma_secenekleri = [""] + get_list("Firma")
            
            st.write("### 👥 Mevcut Kullanıcılar ve Müşteriler")
            
            for idx, user_row in users_db.iterrows():
                rol_etiketi = "MÜŞTERİ" if user_row.get("is_customer", False) else "PERSONEL"
                with st.expander(f"👤 {user_row['username']} ({rol_etiketi})"):
                    col_f, col_s = st.columns([4, 1])
                    with col_f:
                        with st.form(f"edit_user_form_{idx}"):
                            e_pw = st.text_input("Şifre", value=str(user_row['password']))
                            st.markdown("---")
                            
                            is_cust_val = bool(user_row.get('is_customer', False))
                            e_cust = st.checkbox("Bu Kullanıcı Bir 'Müşteri'dir", value=is_cust_val)
                            
                            mevcut_firma = str(user_row.get('customer_firm', ''))
                            if mevcut_firma not in firma_secenekleri: mevcut_firma = ""
                            e_cust_firm = st.selectbox("Müşterinin Bağlı Olduğu Firma", firma_secenekleri, index=firma_secenekleri.index(mevcut_firma))
                            
                            st.markdown("---")
                            st.markdown("**Personel Yetkileri (Müşterilerde geçersizdir):**")
                            e_rep = st.checkbox("Finansal Raporları Görebilir", value=bool(user_row['can_view_reports']))
                            e_dash = st.checkbox("Dashboard Notlarını Düzenleyebilir", value=bool(user_row.get('can_edit_dashboard', False)))
                            e_ai = st.checkbox("Akıllı Asistanı Kullanabilir", value=bool(user_row.get('can_use_assistant', False)))
                            e_ticker = st.checkbox("Canlı Bilgi Göstergesini (Sağ Üst) Görebilir", value=bool(user_row.get('can_view_ticker', True)))
                            e_adm = st.checkbox("Yönetici Yetkisi", value=bool(user_row['can_manage_admin']), disabled=(user_row['username']=='admin'))
                            
                            if st.form_submit_button("🔄 Yetkileri Güncelle"):
                                show_loader("Yetkiler Güncelleniyor...")
                                users_db.at[idx, 'password'] = e_pw
                                users_db.at[idx, 'is_customer'] = e_cust
                                users_db.at[idx, 'customer_firm'] = e_cust_firm if e_cust else ""
                                users_db.at[idx, 'can_view_reports'] = e_rep
                                users_db.at[idx, 'can_edit_dashboard'] = e_dash
                                users_db.at[idx, 'can_use_assistant'] = e_ai
                                users_db.at[idx, 'can_view_ticker'] = e_ticker
                                if user_row['username'] != 'admin': 
                                    users_db.at[idx, 'can_manage_admin'] = e_adm
                                users_db.to_csv(U_FILE, index=False)
                                log_islem(st.session_state['user'], f"Yetki Güncelledi: {user_row['username']}")
                                st.success("✅ Yetkiler başarıyla güncellendi!")
                                time.sleep(0.5)
                                st.rerun()
                    
                    with col_s:
                        if user_row['username'] != "admin":
                            if st.button("❌ Sil", key=f"del_user_{idx}"):
                                show_loader("Kullanıcı Siliniyor...")
                                log_islem(st.session_state['user'], f"Kullanıcı Sildi: {user_row['username']}")
                                users_db.drop(idx).to_csv(U_FILE, index=False)
                                st.rerun()
            
            with st.expander("➕ Yeni Personel veya Müşteri Ekle"):
                with st.form("new_u_form"):
                    nu = st.text_input("Kullanıcı Adı")
                    np = st.text_input("Şifre")
                    st.markdown("---")
                    y_cust = st.checkbox("Yeni Müşteri Hesabı Oluştur")
                    y_cust_firm = st.selectbox("Müşteri İçin Firma Seç (Opsiyonel)", firma_secenekleri)
                    st.markdown("---")
                    st.markdown("**Personel İçin Yetkiler:**")
                    yr = st.checkbox("Finansal Rapor Görüntüleme")
                    yd = st.checkbox("Dashboard Notu Düzenleme")
                    y_ai = st.checkbox("Akıllı Asistan Yetkisi")
                    y_tick = st.checkbox("Canlı Bilgi Göstergesi Yetkisi", value=True)
                    ya = st.checkbox("Admin Yetkisi")
                    
                    if st.form_submit_button("Sisteme Kaydet"):
                        show_loader("Yeni Kullanıcı Oluşturuluyor...")
                        yeni_kullanici = pd.DataFrame([{
                            "username": nu, "password": np, 
                            "can_view_reports": yr, "can_manage_admin": ya, 
                            "can_edit_dashboard": yd, "can_use_assistant": y_ai,
                            "can_view_ticker": y_tick,
                            "is_customer": y_cust, "customer_firm": y_cust_firm if y_cust else ""
                        }])
                        pd.concat([users_db, yeni_kullanici]).to_csv(U_FILE, index=False)
                        log_islem(st.session_state['user'], f"Yeni Kullanıcı Ekledi: {nu}")
                        st.success("✅ Yeni kullanıcı başarıyla eklendi!")
                        time.sleep(0.5)
                        st.rerun()

        # --- ORTAK YÖNETİM FONKSİYONU ---
        def yonetim_listesi(liste_adi, v_tipi):
            st.subheader(f"{liste_adi} Yönetimi")
            
            with st.expander(f"📥 Excel'den {liste_adi} Aktar"):
                yuklenen = st.file_uploader(f"Excel (.xlsx)", key=f"up_{v_tipi}")
                if yuklenen and st.button("Güncelle", key=f"btn_up_{v_tipi}"):
                    show_loader("Veriler İçe Aktarılıyor...")
                    okunan_excel = pd.read_excel(yuklenen)
                    yeni_liste = [{"tip": v_tipi, "deger": str(x)} for x in okunan_excel.iloc[:,0].dropna().unique()]
                    pd.concat([pd.read_csv(S_FILE), pd.DataFrame(yeni_liste)]).to_csv(S_FILE, index=False)
                    log_islem(st.session_state['user'], f"Excel ile {liste_adi} Aktardı")
                    st.rerun()
            
            c_in, c_btn = st.columns([4, 1])
            yeni = c_in.text_input(f"Yeni Ekle", key=f"in_{v_tipi}")
            if c_btn.button("EKLE", key=f"add_{v_tipi}") and yeni:
                show_loader("Listeye Ekleniyor...")
                pd.concat([pd.read_csv(S_FILE), pd.DataFrame([{"tip": v_tipi, "deger": yeni}])]).to_csv(S_FILE, index=False)
                log_islem(st.session_state['user'], f"Sisteme {liste_adi} Ekledi: {yeni}")
                st.rerun()
            
            for index, eleman in enumerate(get_list(v_tipi)):
                cl1, cl2 = st.columns([7, 1])
                cl1.write(f"🔹 {eleman}")
                if cl2.button("🗑️", key=f"rm_{v_tipi}_{index}_{hash(eleman)}"):
                    show_loader("Listeden Siliniyor...")
                    df_a = pd.read_csv(S_FILE)
                    df_a = df_a[~((df_a['tip'] == v_tipi) & (df_a['deger'] == eleman))]
                    df_a.to_csv(S_FILE, index=False)
                    log_islem(st.session_state['user'], f"Sistemden {liste_adi} Sildi: {eleman}")
                    st.rerun()

        # --- DİĞER TABLAR ---
        with tab_operators: 
            yonetim_listesi("Operatör", "Operatör")
        with tab_firms: 
            yonetim_listesi("Firma", "Firma")
        with tab_machines: 
            yonetim_listesi("Makine", "Makine")
            
        # --- WHATSAPP YAYIN AĞI TABI ---
        with tab_bot:
            st.subheader("📡 WhatsApp Canlı Yayın Ağı (Çoklu Gönderim)")
            st.info("Sisteme girilen yeni kayıtlar, buraya eklediğiniz tüm yetkililere anında WhatsApp üzerinden özel mesaj olarak gönderilir. (Sınırsız kişi ekleyebilirsiniz!)")
            
            df_ayar = pd.read_csv(S_FILE)
            
            st.markdown("### 👥 Kayıtlı Yayın Alıcıları")
            aboneler = df_ayar[df_ayar['tip'] == 'WA_BOT_SUB']['deger'].tolist()
            if not aboneler:
                st.warning("Henüz yayın ağına kimse eklenmemiş. Lütfen aşağıdan yeni bir alıcı ekleyin.")
            else:
                for idx, abone in enumerate(aboneler):
                    parcalar = abone.split('|')
                    if len(parcalar) == 3:
                        col_isim, col_no, col_sil = st.columns([4, 4, 2])
                        col_isim.write(f"👤 **{parcalar[0]}**")
                        col_no.write(f"📱 {parcalar[1]}")
                        if col_sil.button("🗑️ Ağdan Sil", key=f"del_wa_{idx}"):
                            show_loader("Kişi Ağdan Çıkarılıyor...")
                            df_ayar = df_ayar[~((df_ayar['tip'] == 'WA_BOT_SUB') & (df_ayar['deger'] == abone))]
                            df_ayar.to_csv(S_FILE, index=False)
                            log_islem(st.session_state['user'], f"WhatsApp Yayınına Çıkardı: {parcalar[0]}")
                            st.rerun()
            
            st.divider()
            st.markdown("### ➕ Yeni Alıcı Ekle")
            with st.form("yeni_wa_abone"):
                st.markdown("1. [CallMeBot WhatsApp](https://www.callmebot.com/blog/free-api-whatsapp-messages/) sayfasına gidin ve eklenecek kişi için API Key alın.")
                st.markdown("2. Aldığınız numarayı (başında + olarak) ve API şifresini aşağıya girin.")
                
                n_isim = st.text_input("Kişi Adı / Görevi (Örn: Emir Bey - Patron)")
                n_phone = st.text_input("WhatsApp Numarası (Örn: +90532...)")
                n_api = st.text_input("CallMeBot API Key", type="password")
                
                if st.form_submit_button("💾 Yayın Ağına Ekle"):
                    if n_isim and n_phone and n_api:
                        show_loader("Ağa Ekleniyor...")
                        yeni_deger = f"{n_isim}|{n_phone}|{n_api}"
                        yeni_ek = pd.DataFrame([{"tip": "WA_BOT_SUB", "deger": yeni_deger}])
                        pd.concat([df_ayar, yeni_ek]).to_csv(S_FILE, index=False)
                        log_islem(st.session_state['user'], f"WhatsApp Yayınına Ekledi: {n_isim}")
                        st.success(f"✅ {n_isim} başarıyla yayın ağına katıldı!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Lütfen tüm alanları doldurun.")
                    
        # --- E-POSTA AYARLARI TABI ---
        with tab_email:
            st.subheader("📧 Otomatik E-Posta Gönderim Ayarları")
            
            df_ayar = pd.read_csv(S_FILE)
            email_rows = df_ayar[df_ayar['tip'] == 'EMAIL_ADDR']
            pass_rows = df_ayar[df_ayar['tip'] == 'EMAIL_PASS']
            
            mevcut_email = email_rows['deger'].iloc[0] if not email_rows.empty else ""
            mevcut_pass = pass_rows['deger'].iloc[0] if not pass_rows.empty else ""
            
            with st.form("email_ayar_formu"):
                yeni_email = st.text_input("Gönderici Gmail Adresi", value=mevcut_email)
                yeni_pass = st.text_input("Gmail Uygulama Şifresi (16 Haneli)", value=mevcut_pass, type="password")
                
                if st.form_submit_button("💾 E-Posta Ayarlarını Kaydet"):
                    show_loader("E-Posta Ayarları Kaydediliyor...")
                    df_ayar = df_ayar[~df_ayar['tip'].isin(['EMAIL_ADDR', 'EMAIL_PASS'])]
                    yeni_ayarlar = pd.DataFrame([
                        {"tip": "EMAIL_ADDR", "deger": yeni_email},
                        {"tip": "EMAIL_PASS", "deger": yeni_pass}
                    ])
                    pd.concat([df_ayar, yeni_ayarlar]).to_csv(S_FILE, index=False)
                    log_islem(st.session_state['user'], "E-Posta Ayarlarını Değiştirdi")
                    st.success("✅ E-Posta Ayarları başarıyla kaydedildi!")
                    time.sleep(0.5)
                    st.rerun()

        # --- SİSTEM LOGLARI TABI ---
        with tab_logs:
            st.subheader("🕵️ Sistem Denetim ve Güvenlik Logları")
            st.info("Sisteme kimin, hangi cihazdan ve ne zaman giriş yaptığını buradan takip edebilirsiniz.")
            
            if os.path.exists(L_FILE):
                df_logs = pd.read_csv(L_FILE)
                if not df_logs.empty:
                    df_logs_sorted = df_logs.sort_values(by=['Tarih', 'Saat'], ascending=[False, False])
                    st.dataframe(df_logs_sorted, use_container_width=True, hide_index=True)
                    
                    if st.button("🗑️ Tüm Log Kayıtlarını Temizle"):
                        show_loader("Loglar Temizleniyor...")
                        pd.DataFrame(columns=["Tarih", "Saat", "Kullanıcı", "İşlem", "Cihaz"]).to_csv(L_FILE, index=False)
                        st.success("✅ Log kayıtları başarıyla sıfırlandı.")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    st.warning("Henüz kaydedilmiş bir sistem logu bulunmuyor.")
            else:
                st.warning("Log dosyası bulunamadı.")
