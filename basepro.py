import streamlit as st
import requests
import streamlit.components.v1 as components
from datetime import datetime

# --- 1. AYARLAR ---
st.set_page_config(
    page_title="Base Token Detective",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TASARIM ---
st.markdown("""
<style>
    .metric-card {background-color: #1E1E1E; border: 1px solid #333; padding: 15px; border-radius: 10px; margin-bottom: 10px;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. DİL DESTEĞİ (5 DİL) ---
LANGUAGES = {
    "Türkçe": "tr",
    "English": "en",
    "中文 (Chinese)": "zh",
    "한국어 (Korean)": "ko",
    "Русский (Russian)": "ru"
}

TEXTS = {
    "tr": {
        "title": "Base Token Dedektifi",
        "subtitle": "Canlı Piyasa Verileri & Güvenlik Analizi",
        "search_ph": "Token Ara (Örn: AERO, BRETT)",
        "btn": "ANALİZ ET",
        "chart": "Fiyat Grafiği",
        "score_title": "Güvenlik Skoru",
        "details": "Analiz Detayları",
        "links": "Bağlantılar",
        "loading": "Veriler çekiliyor...",
        "error_chain": "Bu token Base ağında bulunamadı.",
        "error_404": "Token bulunamadı.",
        "liq_high": "Likidite Yüksek",
        "liq_low": "Likidite Düşük",
        "tax_high": "Yüksek Vergi",
        "tax_low": "Düşük Vergi",
        "honeypot": "KRİTİK: Honeypot (Satılamaz)",
        "safe_hp": "Satış Açık (Honeypot Değil)",
        "social_ok": "Sosyal Medya Onaylı",
        "social_no": "Sosyal Medya Yok"
    },
    "en": {
        "title": "Base Token Detective",
        "subtitle": "Live Market Data & Security Analysis",
        "search_ph": "Search Token (e.g. AERO)",
        "btn": "ANALYZE",
        "chart": "Price Chart",
        "score_title": "Security Score",
        "details": "Analysis Details",
        "links": "Links",
        "loading": "Fetching data...",
        "error_chain": "Token not found on Base chain.",
        "error_404": "Token not found.",
        "liq_high": "High Liquidity",
        "liq_low": "Low Liquidity",
        "tax_high": "High Tax",
        "tax_low": "Low Tax",
        "honeypot": "CRITICAL: Honeypot (Cannot Sell)",
        "safe_hp": "Tradable (Not Honeypot)",
        "social_ok": "Social Media Verified",
        "social_no": "No Social Media"
    },
    "zh": {
        "title": "Base 代币侦探",
        "subtitle": "实时市场数据与安全分析",
        "search_ph": "搜索代币 (例如: AERO)",
        "btn": "分析",
        "chart": "价格图表",
        "score_title": "安全评分",
        "details": "分析详情",
        "links": "链接",
        "loading": "正在加载...",
        "error_chain": "Base链上未找到该代币。",
        "error_404": "未找到代币。",
        "liq_high": "流动性高",
        "liq_low": "流动性低",
        "tax_high": "高税率",
        "tax_low": "低税率",
        "honeypot": "严重: 蜜罐 (无法出售)",
        "safe_hp": "可交易 (非蜜罐)",
        "social_ok": "社交媒体已验证",
        "social_no": "无社交媒体"
    },
    "ko": {
        "title": "Base 토큰 탐정",
        "subtitle": "실시간 시장 데이터 및 보안 분석",
        "search_ph": "토큰 검색 (예: AERO)",
        "btn": "분석",
        "chart": "가격 차트",
        "score_title": "보안 점수",
        "details": "분석 세부 정보",
        "links": "링크",
        "loading": "데이터 로딩 중...",
        "error_chain": "Base 체인에서 토큰을 찾을 수 없습니다.",
        "error_404": "토큰을 찾을 수 없습니다.",
        "liq_high": "높은 유동성",
        "liq_low": "낮은 유동성",
        "tax_high": "높은 세금",
        "tax_low": "낮은 세금",
        "honeypot": "위험: 허니팟 (판매 불가)",
        "safe_hp": "거래 가능 (허니팟 아님)",
        "social_ok": "소셜 미디어 인증됨",
        "social_no": "소셜 미디어 없음"
    },
    "ru": {
        "title": "Base Токен Детектив",
        "subtitle": "Рыночные данные и анализ безопасности",
        "search_ph": "Поиск токена (напр. AERO)",
        "btn": "АНАЛИЗ",
        "chart": "График цены",
        "score_title": "Оценка безопасности",
        "details": "Детали анализа",
        "links": "Ссылки",
        "loading": "Загрузка данных...",
        "error_chain": "Токен не найден в сети Base.",
        "error_404": "Токен не найден.",
        "liq_high": "Высокая ликвидность",
        "liq_low": "Низкая ликвидность",
        "tax_high": "Высокий налог",
        "tax_low": "Низкий налог",
        "honeypot": "КРИТИЧНО: Ханипот (Нельзя продать)",
        "safe_hp": "Торговля доступна",
        "social_ok": "Соцсети подтверждены",
        "social_no": "Нет соцсетей"
    }
}

# --- 3. FONKSİYONLAR ---
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

def calculate_score(dex, sec, txt):
    score = 50
    logs = []

    # 1. HONEYPOT
    if sec.get("is_honeypot", "0") == "1":
        return 0, [f"🚨 {txt['honeypot']}"]
    else:
        score += 10
        logs.append(f"✅ {txt['safe_hp']} (+10)")

    # 2. LİKİDİTE
    liq = dex.get("liquidity", {}).get("usd", 0)
    if liq > 100000:
        score += 20
        logs.append(f"✅ {txt['liq_high']} (${liq:,.0f}) (+20)")
    elif liq > 20000:
        score += 10
        logs.append(f"✅ {txt['liq_high']} (${liq:,.0f}) (+10)")
    else:
        score -= 20
        logs.append(f"⚠️ {txt['liq_low']} (${liq:,.0f}) (-20)")

    # 3. VERGİLER
    buy = float(sec.get("buy_tax", 0) or 0) * 100
    sell = float(sec.get("sell_tax", 0) or 0) * 100
    
    if buy > 10 or sell > 10:
        score -= 30
        logs.append(f"⚠️ {txt['tax_high']} (Buy:{buy:.0f}% Sell:{sell:.0f}%) (-30)")
    else:
        score += 10
        logs.append(f"✅ {txt['tax_low']} (+10)")

    # 4. SOSYAL MEDYA
    if dex.get("info", {}).get("socials"):
        score += 10
        logs.append(f"✅ {txt['social_ok']} (+10)")
    else:
        score -= 10
        logs.append(f"⚠️ {txt['social_no']} (-10)")

    return min(max(score, 0), 100), logs

# --- 4. ARAYÜZ ---

# Sidebar Dil Seçimi
with st.sidebar:
    st.header("🌐 Language")
    selected_lang = st.selectbox("Select Language", list(LANGUAGES.keys()))
    lang_code = LANGUAGES[selected_lang]
    t = TEXTS[lang_code] # Seçilen dilin metinlerini al

# Başlık Alanı
c1, c2 = st.columns([1, 10])
with c1:
    st.image("https://cryptologos.cc/logos/base-base-logo.png", width=60)
with c2:
    st.title(t["title"])
    st.caption(t["subtitle"])

# Arama
col_s1, col_s2 = st.columns([4, 1])
with col_s1:
    query = st.text_input("Search", placeholder=t["search_ph"], label_visibility="collapsed")
with col_s2:
    btn = st.button(t["btn"], type="primary", use_container_width=True)

if btn and query:
    with st.spinner(t["loading"]):
        dex_data = search_token(query)
        
        if dex_data and dex_data != "wrong_chain":
            addr = dex_data["baseToken"]["address"]
            sec_data = check_security(addr)
            score, score_logs = calculate_score(dex_data, sec_data, t)
            
            # --- TOKEN HEADER ---
            st.markdown("---")
            head1, head2, head3 = st.columns([1, 3, 2])
            
            with head1:
                img = dex_data.get("info", {}).get("imageUrl", "https://cryptologos.cc/logos/base-base-logo.png")
                st.image(img, width=90)
            
            with head2:
                st.subheader(f"{dex_data['baseToken']['name']} ({dex_data['baseToken']['symbol']})")
                st.code(addr)
                
            with head3:
                price = float(dex_data.get("priceUsd", 0))
                change = dex_data["priceChange"]["h24"]
                color = "green" if change > 0 else "red"
                st.markdown(f"### ${price:.6f}")
                st.markdown(f":{color}[24H: %{change}]")

            # --- İÇERİK (GRAFİK + SKOR) ---
            st.markdown("---")
            col_chart, col_score = st.columns([2, 1])

            with col_chart:
                st.subheader(f"📊 {t['chart']}")
                # GERÇEK GRAFİK (DexScreener Embed)
                pair_addr = dex_data["pairAddress"]
                iframe_url = f"https://dexscreener.com/base/{pair_addr}?embed=1&theme=dark&trades=0&info=0"
                components.iframe(iframe_url, height=500)

            with col_score:
                st.subheader(f"🛡️ {t['score_title']}")
                
                # Skor Görseli
                score_color = "#00FF00" if score >= 80 else "#FFA500" if score >= 50 else "#FF0000"
                st.markdown(
                    f"""
                    <div style="text-align: center; border: 2px solid {score_color}; padding: 15px; border-radius: 15px; background-color: #262730; margin-bottom: 20px;">
                        <h1 style="color: {score_color}; margin: 0; font-size: 3em;">{score}</h1>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                st.markdown(f"### 📝 {t['details']}")
                for log in score_logs:
                    st.write(log)

            # --- LİNKLER ---
            st.markdown("---")
            st.subheader(f"🌍 {t['links']}")
            info = dex_data.get("info", {})
            links = []
            if info.get('websites'):
                for w in info['websites']: links.append(f"[Web]({w['url']})")
            if info.get('socials'):
                for s in info['socials']: links.append(f"[{s['type'].capitalize()}]({s['url']})")
            
            if links:
                st.markdown(" | ".join(links))
            else:
                st.info("-")

        elif dex_data == "wrong_chain":
            st.error(t["error_chain"])
        else:
            st.error(t["error_404"])
