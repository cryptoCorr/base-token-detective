import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# --- 1. AYARLAR ---
st.set_page_config(
    page_title="Base Token Detective Global",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TASARIM (Gizli Menüler & Kartlar) ---
st.markdown("""
<style>
    .metric-card {background-color: #0E1117; border: 1px solid #262730; padding: 20px; border-radius: 10px;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- DİL SEÇENEKLERİ (5 DİL) ---
LANGUAGES = {
    "Türkçe": "tr",
    "English": "en",
    "中文 (Chinese)": "zh",
    "한국어 (Korean)": "ko",
    "Русский (Russian)": "ru"
}

TEXTS = {
    "tr": {
        "title": "🛡️ Base Token Dedektifi",
        "search": "Token Sembolü (Örn: AERO, BRETT)",
        "btn": "Analiz Et",
        "score": "Güven Skoru",
        "tab1": "📊 Genel Bakış & Grafik",
        "tab2": "🛡️ Güvenlik Durumu",
        "tab3": "🌍 Proje Kimliği",
        "date": "Çıkış Tarihi",
        "risk": "RİSKLİ",
        "safe": "GÜVENLİ",
        "loading": "Blockchain taranıyor...",
        "honeypot": "🚨 HONEYPOT! (SATILAMAZ)",
        "safe_honeypot": "✅ Satış Açık (Honeypot Değil)"
    },
    "en": {
        "title": "🛡️ Base Token Detective",
        "search": "Token Symbol (e.g., AERO, BRETT)",
        "btn": "Analyze",
        "score": "Trust Score",
        "tab1": "📊 Overview & Chart",
        "tab2": "🛡️ Security Status",
        "tab3": "🌍 Project Identity",
        "date": "Launch Date",
        "risk": "RISKY",
        "safe": "SAFE",
        "loading": "Scanning blockchain...",
        "honeypot": "🚨 HONEYPOT! (CANNOT SELL)",
        "safe_honeypot": "✅ Tradable (Not Honeypot)"
    },
    "zh": {
        "title": "🛡️ Base 代币侦探",
        "search": "代币符号 (例如: AERO)",
        "btn": "分析",
        "score": "信任评分",
        "tab1": "📊 概览",
        "tab2": "🛡️ 安全状态",
        "tab3": "🌍 项目身份",
        "date": "发布日期",
        "risk": "风险",
        "safe": "安全",
        "loading": "正在扫描...",
        "honeypot": "🚨 蜜罐! (无法出售)",
        "safe_honeypot": "✅ 可交易 (非蜜罐)"
    },
    "ko": {
        "title": "🛡️ Base 토큰 탐정",
        "search": "토큰 심볼 (예: AERO)",
        "btn": "분석하기",
        "score": "신뢰 점수",
        "tab1": "📊 개요 & 차트",
        "tab2": "🛡️ 보안 상태",
        "tab3": "🌍 프로젝트 정보",
        "date": "출시일",
        "risk": "위험",
        "safe": "안전",
        "loading": "블록체인 스캔 중...",
        "honeypot": "🚨 허니팟! (판매 불가)",
        "safe_honeypot": "✅ 거래 가능 (허니팟 아님)"
    },
    "ru": {
        "title": "🛡️ Base Токен Детектив",
        "search": "Символ токена (напр. AERO)",
        "btn": "Анализировать",
        "score": "Оценка доверия",
        "tab1": "📊 Обзор и График",
        "tab2": "🛡️ Безопасность",
        "tab3": "🌍 О проекте",
        "date": "Дата запуска",
        "risk": "РИСК",
        "safe": "БЕЗОПАСНО",
        "loading": "Сканирование блокчейна...",
        "honeypot": "🚨 ХАНИПОТ! (Продать нельзя)",
        "safe_honeypot": "✅ Торговля доступна"
    }
}

# --- FONKSİYONLAR ---
def search_token(query):
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
        data = requests.get(url).json()
        if not data.get("pairs"): return None
        # Base ağındaki en likit çifti bul
        base_pairs = [p for p in data["pairs"] if p.get("chainId") == "base"]
        if not base_pairs: return "wrong_chain"
        return sorted(base_pairs, key=lambda x: x.get("liquidity", {}).get("usd", 0), reverse=True)[0]
    except: return None

def check_security(address):
    try:
        url = f"https://api.gopluslabs.io/api/v1/token_security/8453?contract_addresses={address}"
        return requests.get(url).json().get("result", {}).get(address.lower(), {})
    except: return {}

def create_chart(dex_data):
    changes = dex_data.get("priceChange", {})
    periods = ["m5", "h1", "h6", "h24"]
    values = [changes.get(p, 0) for p in periods]
    labels = ["5m", "1H", "6H", "24H"]
    colors = ['#00ff00' if v > 0 else '#ff0000' for v in values]
    
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color=colors)])
    fig.update_layout(
        title="Momentum (%)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=300,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

def calculate_score(dex, sec):
    score = 0
    reasons = []
    
    # 1. HONEYPOT
    if sec.get("is_honeypot", "0") == "1":
        return 0, ["Honeypot"]
    
    # 2. VERGİLER (Hesaplanıyor ama GÖSTERİLMİYOR)
    buy = float(sec.get("buy_tax", 0) or 0) * 100
    sell = float(sec.get("sell_tax", 0) or 0) * 100
    if buy > 10 or sell > 10: pass # Puan verme
    else: score += 20
    
    # 3. LİKİDİTE
    liq = dex.get("liquidity", {}).get("usd", 0)
    if liq > 200000: score += 30
    elif liq > 50000: score += 15
    
    # 4. TOKEN YAŞI
    created_at = dex.get("pairCreatedAt", 0)
    if created_at:
        age_days = (datetime.now().timestamp() * 1000 - created_at) / (1000 * 60 * 60 * 24)
        if age_days > 30: score += 20
    
    # 5. SOSYAL MEDYA
    if dex.get("info", {}).get("socials"): score += 30
    
    return min(score, 100), reasons

# --- ARAYÜZ ---
with st.sidebar:
    st.header("🌐 Language / Dil")
    lang_key = st.selectbox("", list(LANGUAGES.keys()))
    lang = LANGUAGES[lang_key]
    txt = TEXTS.get(lang, TEXTS["en"])

# LOGO VE BAŞLIK
c1, c2 = st.columns([1, 10])
with c1:
    st.image("https://cryptologos.cc/logos/base-base-logo.png", width=60)
with c2:
    st.title(txt["title"])

# ARAMA
col_search, col_btn = st.columns([4, 1])
with col_search:
    query = st.text_input(txt["search"], label_visibility="collapsed", placeholder="BRETT...")
with col_btn:
    scan_btn = st.button(txt["btn"], use_container_width=True, type="primary")

if scan_btn and query:
    with st.spinner(txt["loading"]):
        dex_data = search_token(query)
        
        if dex_data and dex_data != "wrong_chain":
            addr = dex_data.get("baseToken", {}).get("address")
            sec_data = check_security(addr)
            score, reasons = calculate_score(dex_data, sec_data)
            
            # --- ÜST KART ---
            info = dex_data.get("info", {})
            img_url = info.get("imageUrl", "https://cryptologos.cc/logos/base-base-logo.png")
            creation_date = "---"
            if dex_data.get("pairCreatedAt"):
                creation_date = datetime.fromtimestamp(dex_data["pairCreatedAt"] / 1000).strftime('%d.%m.%Y')

            head1, head2 = st.columns([1, 5])
            with head1:
                st.image(img_url, width=100)
            with head2:
                st.subheader(f"{dex_data['baseToken']['name']} ({dex_data['baseToken']['symbol']})")
                st.caption(f"Contract: {addr}")
                st.caption(f"📅 {txt['date']}: {creation_date}")

            # --- METRİKLER ---
            kpi1, kpi2, kpi3 = st.columns(3)
            price = float(dex_data.get("priceUsd", 0))
            kpi1.metric("Price", f"${price:.6f}", f"%{dex_data['priceChange']['h24']}")
            kpi2.metric("Liquidity", f"${dex_data['liquidity']['usd']:,.0f}")
            
            # Skor Rengi
            score_color = "normal" if score >= 80 else "inverse"
            kpi3.metric(txt["score"], f"{score}/100")

            st.markdown("---")

            # --- SEKMELER ---
            tab1, tab2, tab3 = st.tabs([txt["tab1"], txt["tab2"], txt["tab3"]])

            with tab1: # GRAFİK
                st.plotly_chart(create_chart(dex_data), use_container_width=True)
                if score < 50: st.error(f"🚨 {txt['risk']}")
                else: st.success(f"✅ {txt['safe']}")

            with tab2: # GÜVENLİK (Vergiler Gizli)
                # Sadece Honeypot ve Genel Durum Gösterilir
                if sec_data.get("is_honeypot") == "1":
                    st.error(txt["honeypot"])
                else:
                    st.success(txt["safe_honeypot"])
                
                if sec_data.get("owner_change_balance") == "0":
                    st.info("✅ Owner cannot change balance.")
                
                # Vergi oranları burada yazmıyor artık!

            with tab3: # LİNKLER
                links = []
                if info.get('websites'):
                    for w in info['websites']: links.append(f"[Web]({w['url']})")
                if info.get('socials'):
                    for s in info['socials']: links.append(f"[{s['type'].capitalize()}]({s['url']})")
                
                if links:
                    st.markdown(" | ".join(links))
                else:
                    st.warning("-")

        elif dex_data == "wrong_chain":
            st.warning("Token not on Base chain.")
        else:
            st.error("Token not found.")
