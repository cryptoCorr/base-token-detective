import streamlit as st
import requests
import streamlit.components.v1 as components # Grafiği gömmek için gerekli
from datetime import datetime

# --- 1. AYARLAR ---
st.set_page_config(
    page_title="Base Token Detective Pro",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Arka plan ve kart tasarımları
st.markdown("""
<style>
    .metric-card {background-color: #1E1E1E; border: 1px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 10px;}
    .score-high {color: #00FF00; font-weight: bold;}
    .score-med {color: #FFA500; font-weight: bold;}
    .score-low {color: #FF0000; font-weight: bold;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. FONKSİYONLAR ---
def search_token(query):
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
        data = requests.get(url).json()
        if not data.get("pairs"): return None
        base_pairs = [p for p in data["pairs"] if p.get("chainId") == "base"]
        if not base_pairs: return "wrong_chain"
        return sorted(base_pairs, key=lambda x: x.get("liquidity", {}).get("usd", 0), reverse=True)[0]
    except: return None

def check_security(address):
    try:
        url = f"https://api.gopluslabs.io/api/v1/token_security/8453?contract_addresses={address}"
        return requests.get(url).json().get("result", {}).get(address.lower(), {})
    except: return {}

def calculate_score(dex, sec):
    score = 50 # Başlangıç puanı
    logs = []  # Puan detaylarını buraya yazacağız

    # 1. HONEYPOT (Ölümcül Hata)
    if sec.get("is_honeypot", "0") == "1":
        return 0, ["🚨 KRİTİK: Token Honeypot! (Satılamaz)"]
    else:
        score += 10
        logs.append("✅ Honeypot Değil (+10)")

    # 2. LİKİDİTE DURUMU
    liq = dex.get("liquidity", {}).get("usd", 0)
    if liq > 100000:
        score += 20
        logs.append(f"✅ Likidite Çok İyi (${liq:,.0f}) (+20)")
    elif liq > 20000:
        score += 10
        logs.append(f"✅ Likidite Yeterli (${liq:,.0f}) (+10)")
    else:
        score -= 20
        logs.append(f"⚠️ Likidite Çok Düşük (${liq:,.0f}) (-20)")

    # 3. VERGİLER (TAX)
    buy_tax = float(sec.get("buy_tax", 0) or 0) * 100
    sell_tax = float(sec.get("sell_tax", 0) or 0) * 100
    
    if buy_tax > 10 or sell_tax > 10:
        score -= 30
        logs.append(f"⚠️ Yüksek Vergi (Al:%{buy_tax:.0f} Sat:%{sell_tax:.0f}) (-30)")
    elif buy_tax < 5 and sell_tax < 5:
        score += 10
        logs.append("✅ Düşük Vergi Oranları (+10)")

    # 4. SOSYAL MEDYA
    socials = dex.get("info", {}).get("socials", [])
    if socials:
        score += 10
        logs.append(f"✅ {len(socials)} Sosyal Medya Hesabı Var (+10)")
    else:
        score -= 10
        logs.append("⚠️ Sosyal Medya Hesabı Yok (-10)")

    # 5. YAŞ (Token Eskiliği)
    created_at = dex.get("pairCreatedAt", 0)
    if created_at:
        days_old = (datetime.now().timestamp() * 1000 - created_at) / (1000 * 60 * 60 * 24)
        if days_old > 30:
            logs.append(f"✅ Token Oturmuş ({int(days_old)} günlük)")
        else:
            logs.append(f"ℹ️ Token Yeni ({int(days_old)} günlük)")

    return min(max(score, 0), 100), logs

# --- 3. ARAYÜZ (FRONTEND) ---

# Üst Başlık
c1, c2 = st.columns([1, 10])
with c1:
    st.image("https://cryptologos.cc/logos/base-base-logo.png", width=60)
with c2:
    st.title("Base Token Dedektifi")
    st.caption("Binance Tarzı Grafik & Detaylı Güvenlik Analizi")

# Arama Çubuğu
col_s1, col_s2 = st.columns([4, 1])
with col_s1:
    query = st.text_input("Token Ara", placeholder="Örn: DEGEN, BRETT, AERO...", label_visibility="collapsed")
with col_s2:
    btn = st.button("ANALİZ ET 🚀", type="primary", use_container_width=True)

if btn and query:
    with st.spinner("Piyasalar ve Kontratlar Taranıyor..."):
        dex_data = search_token(query)
        
        if dex_data and dex_data != "wrong_chain":
            addr = dex_data["baseToken"]["address"]
            sec_data = check_security(addr)
            score, score_logs = calculate_score(dex_data, sec_data)
            
            # --- TOKEN KİMLİĞİ ---
            st.markdown("---")
            head_col1, head_col2, head_col3 = st.columns([1, 3, 2])
            
            with head_col1:
                img = dex_data.get("info", {}).get("imageUrl", "https://cryptologos.cc/logos/base-base-logo.png")
                st.image(img, width=100)
            
            with head_col2:
                st.subheader(f"{dex_data['baseToken']['name']} ({dex_data['baseToken']['symbol']})")
                st.code(addr)
                
            with head_col3:
                price = float(dex_data.get("priceUsd", 0))
                change = dex_data["priceChange"]["h24"]
                color = "green" if change > 0 else "red"
                st.markdown(f"### ${price:.6f}")
                st.markdown(f":{color}[24s Değişim: %{change}]")

            # --- ANA EKRAN (SOL: GRAFİK, SAĞ: SKOR) ---
            st.markdown("---")
            col_chart, col_score = st.columns([2, 1])

            with col_chart:
                st.subheader("📊 Canlı Borsa Grafiği")
                # BURADA DEXSCREENER'IN GERÇEK GRAFİĞİNİ GÖMÜYORUZ
                # iframe yüksekliğini artırdım, tam ekran hissi versin diye
                pair_addr = dex_data["pairAddress"]
                iframe_url = f"https://dexscreener.com/base/{pair_addr}?embed=1&theme=dark&trades=0&info=0"
                components.iframe(iframe_url, height=500)

            with col_score:
                st.subheader("🛡️ Güvenlik Raporu")
                
                # Skor Göstergesi
                score_color = "#00FF00" if score >= 80 else "#FFA500" if score >= 50 else "#FF0000"
                st.markdown(
                    f"""
                    <div style="text-align: center; border: 2px solid {score_color}; padding: 20px; border-radius: 15px; background-color: #262730;">
                        <h1 style="color: {score_color}; margin: 0;">{score}/100</h1>
                        <p style="margin: 0;">GÜVEN SKORU</p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                st.write("") # Boşluk
                st.markdown("### 📝 Analiz Detayları")
                
                # Detayları madde madde yazdır
                for log in score_logs:
                    st.write(log)

            # --- ALT BİLGİLER ---
            st.markdown("---")
            st.subheader("🌍 Proje Linkleri")
            info = dex_data.get("info", {})
            links = []
            if info.get('websites'):
                for w in info['websites']: links.append(f"[🌐 Web Sitesi]({w['url']})")
            if info.get('socials'):
                for s in info['socials']: links.append(f"[{s['type'].capitalize()}]({s['url']})")
            
            if links:
                st.markdown(" | ".join(links))
            else:
                st.info("Sosyal medya bağlantısı bulunamadı.")

        elif dex_data == "wrong_chain":
            st.error("Bu token var ama Base ağında değil.")
        else:
            st.error("Token bulunamadı. İsmi doğru yazdın mı?")
