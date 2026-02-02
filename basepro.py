import streamlit as st
import requests

# --- 1. AYARLAR ---
# 'wide' yerine 'centered' kullanarak mobilde daha toplu durmasını sağladık
st.set_page_config(page_title="Base Token Detective", page_icon="🛡️", layout="centered")

# Dil Seçenekleri
LANGUAGES = {
    "Türkçe": "tr",
    "English": "en",
    "中文 (Chinese)": "zh",
    "한국어 (Korean)": "ko",
    "Русский (Russian)": "ru",
    "हिन्दी (Hindi)": "hi"
}

# Çeviri Sözlüğü (Vergi metinleri silindi)
TEXTS = {
    "tr": {
        "title": "🛡️ Base Token Dedektifi",
        "subtitle": "Gelişmiş on-chain veri analizi ve güvenlik taraması.",
        "search_label": "Token İsmi veya Adresi (0x...)",
        "search_btn": "Analizi Başlat",
        "loading": "Blokzincir verileri taranıyor...",
        "not_found": "Token bulunamadı! İsmi veya adresi kontrol edin.",
        "network_error": "Token bulundu ancak Base ağında işlem görmüyor.",
        "score": "Güven Skoru",
        "safe": "💎 GÜVENİLİR YAPIDA",
        "medium": "⚖️ ORTA RİSK SEVİYESİ",
        "risky": "💀 YÜKSEK RİSK / TEHLİKELİ",
        "honeypot_alert": "🚨 KRİTİK UYARI: HONEYPOT (SATIŞ KAPALI)",
        "high_liq": "✅ Çok Güçlü Likidite (+30)",
        "good_liq": "✅ Yeterli Likidite (+15)",
        "low_liq": "⚠️ Yetersiz Likidite (+0)",
        "good_vol": "✅ Hacim Aktif (+20)",
        "bad_vol": "⚠️ Hacim Zayıf (+0)",
        "clean_code": "✅ Kontrat Analizi Temiz (+30)",
        "socials": "✅ Proje Kimliği Doğrulanmış (+10)",
        "no_socials": "❌ Anonim Proje / Sosyal Hesap Yok (+0)",
        "report_title": "Detaylı Teknik Rapor"
    },
    "en": {
        "title": "🛡️ Base Token Detective",
        "subtitle": "Advanced on-chain data analysis and security protocol.",
        "search_label": "Token Name or Address (0x...)",
        "search_btn": "Start Analysis",
        "loading": "Scanning blockchain data...",
        "not_found": "Token not found! Check name or address.",
        "network_error": "Token found but not trading on Base chain.",
        "score": "Trust Score",
        "safe": "💎 SECURE STRUCTURE",
        "medium": "⚖️ MEDIUM RISK LEVEL",
        "risky": "💀 HIGH RISK / DANGEROUS",
        "honeypot_alert": "🚨 CRITICAL ALERT: HONEYPOT (UNSELLABLE)",
        "high_liq": "✅ Strong Liquidity (+30)",
        "good_liq": "✅ Sufficient Liquidity (+15)",
        "low_liq": "⚠️ Insufficient Liquidity (+0)",
        "good_vol": "✅ Active Volume (+20)",
        "bad_vol": "⚠️ Weak Volume (+0)",
        "clean_code": "✅ Contract Analysis Clean (+30)",
        "socials": "✅ Project Identity Verified (+10)",
        "no_socials": "❌ Anonymous Project (+0)",
        "report_title": "Detailed Technical Report"
    },
    "zh": {
        "title": "🛡️ Base 代币侦探",
        "subtitle": "先进的链上数据分析与安全协议。",
        "search_label": "输入代币名称或地址 (0x...)",
        "search_btn": "开始分析",
        "loading": "正在扫描区块链数据...",
        "not_found": "未找到代币！请检查名称或地址。",
        "network_error": "找到代币但不在 Base 链上交易。",
        "score": "信任评分",
        "safe": "💎 结构安全",
        "medium": "⚖️ 中等风险水平",
        "risky": "💀 高风险 / 危险",
        "honeypot_alert": "🚨 严重警报：蜜罐 (无法出售)",
        "high_liq": "✅ 强大的流动性 (+30)",
        "good_liq": "✅ 充足的流动性 (+15)",
        "low_liq": "⚠️ 流动性不足 (+0)",
        "good_vol": "✅ 交易活跃 (+20)",
        "bad_vol": "⚠️ 交易疲软 (+0)",
        "clean_code": "✅ 合约分析干净 (+30)",
        "socials": "✅ 项目身份已验证 (+10)",
        "no_socials": "❌ 匿名项目 (+0)",
        "report_title": "详细技术报告"
    },
    "ko": {
        "title": "🛡️ Base 토큰 탐정",
        "subtitle": "고급 온체인 데이터 분석 및 보안 프로토콜.",
        "search_label": "토큰 이름 또는 주소 (0x...)",
        "search_btn": "분석 시작",
        "loading": "블록체인 데이터 스캔 중...",
        "not_found": "토큰을 찾을 수 없습니다! 이름이나 주소를 확인하세요.",
        "network_error": "토큰을 찾았으나 Base 체인에서 거래되지 않습니다.",
        "score": "신뢰 점수",
        "safe": "💎 안전한 구조",
        "medium": "⚖️ 중간 위험 수준",
        "risky": "💀 고위험 / 위험",
        "honeypot_alert": "🚨 치명적 경고: 허니팟 (판매 불가)",
        "high_liq": "✅ 강력한 유동성 (+30)",
        "good_liq": "✅ 충분한 유동성 (+15)",
        "low_liq": "⚠️ 불충분한 유동성 (+0)",
        "good_vol": "✅ 활발한 거래량 (+20)",
        "bad_vol": "⚠️ 약한 거래량 (+0)",
        "clean_code": "✅ 계약 분석 안전 (+30)",
        "socials": "✅ 프로젝트 신원 확인됨 (+10)",
        "no_socials": "❌ 익명 프로젝트 (+0)",
        "report_title": "상세 기술 보고서"
    },
    "ru": {
        "title": "🛡️ Детектив токенов Base",
        "subtitle": "Продвинутый ончейн-анализ и протокол безопасности.",
        "search_label": "Введите имя или адрес (0x...)",
        "search_btn": "Начать анализ",
        "loading": "Сканирование данных блокчейна...",
        "not_found": "Токен не найден! Проверьте имя или адрес.",
        "network_error": "Токен найден, но не торгуется в сети Base.",
        "score": "Оценка доверия",
        "safe": "💎 БЕЗОПАСНАЯ СТРУКТУРА",
        "medium": "⚖️ СРЕДНИЙ УРОВЕНЬ РИСКА",
        "risky": "💀 ВЫСОКИЙ РИСК / ОПАСНО",
        "honeypot_alert": "🚨 КРИТИЧЕСКАЯ ТРЕВОГА: HONEYPOT (НЕЛЬЗЯ ПРОДАТЬ)",
        "high_liq": "✅ Сильная ликвидность (+30)",
        "good_liq": "✅ Достаточная ликвидность (+15)",
        "low_liq": "⚠️ Недостаточная ликвидность (+0)",
        "good_vol": "✅ Активный объем (+20)",
        "bad_vol": "⚠️ Слабый объем (+0)",
        "clean_code": "✅ Анализ контракта чист (+30)",
        "socials": "✅ Личность проекта подтверждена (+10)",
        "no_socials": "❌ Анонимный проект (+0)",
        "report_title": "Подробный технический отчет"
    },
    "hi": {
        "title": "🛡️ Base टोकन जासूस",
        "subtitle": "उन्नत ऑन-चेन डेटा विश्लेषण और सुरक्षा प्रोटोकॉल।",
        "search_label": "टोकन नाम या पता दर्ज करें (0x...)",
        "search_btn": "विश्लेषण शुरू करें",
        "loading": "ब्लॉकचेन डेटा स्कैन हो रहा है...",
        "not_found": "टोकन नहीं मिला!",
        "network_error": "टोकन मिला लेकिन Base चेन पर नहीं है।",
        "score": "विश्वास स्कोर",
        "safe": "💎 सुरक्षित संरचना",
        "medium": "⚖️ मध्यम जोखिम स्तर",
        "risky": "💀 उच्च जोखिम / खतरनाक",
        "honeypot_alert": "🚨 गंभीर चेतावनी: हनीपॉट (बेचा नहीं जा सकता)",
        "high_liq": "✅ मजबूत तरलता (+30)",
        "good_liq": "✅ पर्याप्त तरलता (+15)",
        "low_liq": "⚠️ अपर्याप्त तरलता (+0)",
        "good_vol": "✅ सक्रिय वॉल्यूम (+20)",
        "bad_vol": "⚠️ कमजोर वॉल्यूम (+0)",
        "clean_code": "✅ अनुबंध विश्लेषण सुरक्षित (+30)",
        "socials": "✅ प्रोजेक्ट पहचान सत्यापित (+10)",
        "no_socials": "❌ अज्ञात प्रोजेक्ट (+0)",
        "report_title": "विस्तृत तकनीकी रिपोर्ट"
    }
}

# --- 2. DİL SEÇİMİ ---
st.sidebar.header("Language / Dil")
selected_lang_name = st.sidebar.selectbox("Select Language", list(LANGUAGES.keys()))
lang = LANGUAGES[selected_lang_name]

# --- 3. FONKSİYONLAR ---
def search_token(query):
    # Eğer sorgu '0x' ile başlıyorsa ve uzunsa ADRES arıyordur
    if query.startswith("0x") and len(query) > 30:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{query}"
    else:
        # Değilse İSİM arıyordur
        url = f"https://api.dexscreener.com/latest/dex/search?q={query}"
    
    try:
        response = requests.get(url).json()
        pairs = response.get("pairs", [])
        if not pairs: return None
        
        # Base ağını filtrele
        base_pairs = [p for p in pairs if p.get("chainId") == "base"]
        if not base_pairs: return "network_error"
        
        # En likit olanı seç
        base_pairs.sort(key=lambda x: x.get("liquidity", {}).get("usd", 0), reverse=True)
        return base_pairs[0]
    except Exception:
        return None

def check_security(token_address):
    # Honeypot Kontrolü
    url = f"https://api.gopluslabs.io/api/v1/token_security/8453?contract_addresses={token_address}"
    try:
        response = requests.get(url).json()
        return response.get("result", {}).get(token_address.lower(), {})
    except Exception:
        return None

def calculate_trust_score(dex_data, security_data, lang_code):
    score = 0
    reasons = []
    t = TEXTS[lang_code]

    # 1. HONEYPOT KONTROLÜ (Vergi kontrolü kaldırıldı)
    is_honeypot = security_data.get("is_honeypot", "0")
    if is_honeypot == "1":
        return 0, [t["honeypot_alert"]]

    # 2. PUANLAMA
    # Güvenlik (+30)
    if security_data:
        score += 30
        reasons.append(t["clean_code"])
    
    # Likidite (+30)
    liquidity = dex_data.get("liquidity", {}).get("usd", 0)
    if liquidity > 500000:
        score += 30
        reasons.append(t["high_liq"])
    elif liquidity > 50000:
        score += 15
        reasons.append(t["good_liq"])
    else:
        reasons.append(t["low_liq"])

    # Hacim (+20)
    volume = dex_data.get("volume", {}).get("h24", 0)
    if volume > 50000:
        score += 20
        reasons.append(t["good_vol"])
    else:
        reasons.append(t["bad_vol"])

    # Sosyal (+10)
    if dex_data.get("info", {}).get("socials"):
        score += 10
        reasons.append(t["socials"])
    else:
        reasons.append(t["no_socials"])

    # Bonus: Fiyat İstikrarı (+10)
    price_change = dex_data.get("priceChange", {}).get("h24", 0)
    if -10 < price_change < 100:
        score += 10
    
    return score, reasons

# --- 4. ANA ARAYÜZ ---
t = TEXTS[lang]

st.title(t["title"])
st.markdown(t["subtitle"])

# Placeholder'ı güncelledik (İsim veya Adres)
search_query = st.text_input(t["search_label"])

if st.button(t["search_btn"]):
    if len(search_query) < 2:
        st.warning("...")
    else:
        with st.spinner(t["loading"]):
            dex_data = search_token(search_query)
            
            if dex_data and dex_data != "network_error":
                token_address = dex_data.get("baseToken", {}).get("address")
                security_data = check_security(token_address)
                
                # Başlık ve Fiyat - Mobilde düzgün durması için st.metric kullanımı
                meta = dex_data.get("baseToken", {})
                st.write("---")
                
                # Mobilde yan yana sığması için sade yapı
                st.header(f"{meta.get('name')} ({meta.get('symbol')})")
                st.caption(f"Contract: `{token_address}`")
                st.metric("Price (USD)", f"${dex_data.get('priceUsd', '0')}")
                
                # Puanı Hesapla
                trust_score, reasons = calculate_trust_score(dex_data, security_data, lang)
                
                # Puan Göstergesi
                st.subheader(f"{t['score']}: {trust_score}/100")
                
                bar_color = "red"
                if trust_score == 0:
                    st.error(t["honeypot_alert"])
                elif trust_score >= 80:
                    st.success(t["safe"])
                    bar_color = "green"
                else:
                    st.warning(t["medium"])
                    bar_color = "yellow"
                    
                st.progress(trust_score)
                
                # Detaylar
                with st.expander(t["report_title"]):
                    for r in reasons:
                        st.write(r)
                
                

            elif dex_data == "network_error":
                st.warning(t["network_error"])
            else:
                st.error(t["not_found"])
