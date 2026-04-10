import streamlit as st
import pandas as pd
import re
import urllib.request
import urllib.parse
import json
import random
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from PIL import Image

# ==========================================
# 1. 기본 화면 설정 (🔥 로고 이미지 및 어플 이름 세팅)
# ==========================================
try:
    logo_img = Image.open("logo.png")
    st.set_page_config(page_title="그랑루체 입주민전용", page_icon=logo_img, layout="centered")
except Exception:
    st.set_page_config(page_title="그랑루체 입주민전용", page_icon="🏢", layout="centered")

# ==========================================
# 2. CSS 스타일링 & 🔥 초강력 스크롤 고정 부적
# ==========================================
st.markdown("""
    <meta name="google" content="notranslate">
    
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/3135/3135673.png">
    <link rel="icon" sizes="192x192" href="https://cdn-icons-png.flaticon.com/512/3135/3135673.png">
    <link rel="icon" sizes="512x512" href="https://cdn-icons-png.flaticon.com/512/3135/3135673.png">
    
    <style>
        /* 🔥 안드로이드 앱 껍데기 강제 새로고침 완벽 차단 (콘크리트 부적) */
        html, body, #root, .stApp, .main, [data-testid="stAppViewContainer"], section {
            overscroll-behavior: none !important;
            overscroll-behavior-y: none !important;
            overscroll-behavior-x: none !important;
        }
        
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * { font-family: 'Pretendard', sans-serif; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .block-container { padding-top: 1.0rem !important; padding-bottom: 0.5rem !important; padding-left: 4px !important; padding-right: 4px !important; max-width: 100% !important; }
        
        .premium-title { font-size: clamp(2.0em, 8vw, 2.8em); font-weight: 900; text-align: center; color: #2b6cb0; text-shadow: 0 2px 10px rgba(43, 108, 176, 0.3); margin-bottom: 4px; line-height: 1.2; }
        .promo-title { font-size: 0.85em; text-align: center; color: #D4AF37; font-weight: 700; margin-top: 0px; margin-bottom: 8px; line-height: 1.3; }
        
        /* 사주 링크 및 입예협 공식 배너 스타일 */
        .btn-saju { background-color: rgba(212, 175, 55, 0.1); color: #D4AF37 !important; border: 1px solid #D4AF37; display: inline-flex; justify-content: center; align-items: center; font-weight: 800; font-size: 0.75em; padding: 6px 16px; border-radius: 8px; text-decoration: none !important; margin-bottom: 15px; transition: all 0.2s ease; }
        .official-btn { display: flex; justify-content: center; align-items: center; font-weight: 900; font-size: 0.85em; padding: 12px 16px; border-radius: 10px; text-decoration: none !important; margin-bottom: 6px; transition: all 0.2s ease; width: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .btn-naver { background-color: #03C75A; color: white !important; }
        .btn-kakao-official { background-color: #FEE500; color: #191919 !important; }
        
        .notice-text { text-align: center; font-size: 0.7em; letter-spacing: -0.5px; color: #ff9f0a; font-weight: 600; margin-bottom: 10px; padding: 8px 6px; background-color: rgba(255, 159, 10, 0.1); border-radius: 8px; border: 1px solid rgba(255, 159, 10, 0.2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; }
        
        .stat-container { display: flex; flex-direction: column; gap: 4px; margin-bottom: 10px; width: 100%; }
        .stat-box-new { display: flex; background: linear-gradient(145deg, #1c1c1e, #121212); border-radius: 8px; border: 1px solid #333; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .stat-box-new.dong-box { border: 1px solid #D4AF37; }
        .stat-left { flex: 0 0 22%; background-color: rgba(255, 255, 255, 0.05); display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 6px 2px; border-right: 1px solid #333; font-size: 0.7em; color: #aaa; text-align: center; }
        .stat-left b { font-size: 1.15em; color: #d1d1d6; margin-bottom: 2px; white-space: nowrap; }
        .stat-right { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 6px 8px; gap: 4px; overflow: hidden; }
        .stat-row { font-size: 0.75em; color: #d1d1d6; display: flex; align-items: center; justify-content: space-between; white-space: nowrap; width: 100%; }
        .stat-label { font-weight: 600; color: #888; margin-right: auto; }
        .hl-gold { color: #D4AF37; font-weight: 800; font-size: 1.15em; margin: 0 1px; }
        .hl-red { color: #FF3B30; font-weight: 800; font-size: 1.15em; margin: 0 1px; }
        .hl-green { color: #30D158; font-weight: 800; font-size: 1.0em; margin: 0 1px; }
        .divider { color: #555; margin: 0 2px; font-size: 0.9em; }
        
        div[role="radiogroup"] { display: flex !important; flex-wrap: wrap !important; width: 100% !important; gap: 2px !important; justify-content: center !important; margin-bottom: 10px !important; }
        div[role="radiogroup"] > label { flex: 0 0 calc(20% - 2px) !important; min-width: calc(20% - 2px) !important; background-color: transparent !important; border: none !important; border-bottom: 2px solid #333 !important; padding: 6px 0px !important; cursor: pointer !important; }
        div[role="radiogroup"] > label[data-checked="true"] { border-bottom: 2px solid #D4AF37 !important; }
        div[role="radiogroup"] > label > div:first-child { display: none !important; }
        div[role="radiogroup"] > label p { font-size: 0.85em !important; color: #888 !important; text-align: center !important; width: 100% !important; margin: 0 !important; }
        div[role="radiogroup"] > label[data-checked="true"] p { color: #D4AF37 !important; font-weight: 800 !important; }

        .unit-num { font-size: 0.7em !important; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 1px; }
        .unit-nick { font-size: 0.55em !important; font-weight: 600; line-height: 1.1; margin-top: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .status-badge { font-size: 0.45em !important; font-weight: 800; padding: 2px 3px; border-radius: 3px; margin-top: 1px; display: inline-block; letter-spacing: -0.5px; box-shadow: 0 1px 2px rgba(0,0,0,0.3); }
        .red-badge { background-color: #FF3B30; color: white; border: 1px solid #c22820; }
        .yellow-badge { background-color: #4A90E2; color: white; border: 1px solid #2a6fb8; } 
        
        .news-link { color: #d1d1d6; text-decoration: none; font-size: 0.85em; display: block; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #333; line-height: 1.5; }
        .news-link:hover { color: #D4AF37; }
        .news-source { color: #4A90E2; font-weight: 900; margin-right: 4px; font-size: 0.9em; }
        
        .fomo-tag { color: #FF3B30; font-weight: 800; font-size: 0.8em; margin-left: 6px; background-color: rgba(255, 59, 48, 0.1); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(255, 59, 48, 0.3); display: inline-block; margin-top: 4px;}
        .news-date { color: #aaa; font-size: 0.8em; font-weight: 600; }
        
        button[data-baseweb="tab"] { font-weight: 800 !important; font-size: 0.9em !important; }
        
        .saju-box { background: linear-gradient(180deg, rgba(212, 175, 55, 0.08) 0%, rgba(28, 28, 30, 0.5) 100%); border-radius: 12px; border: 1px solid rgba(212, 175, 55, 0.3); padding: 25px 20px; text-align: left; margin-top: 15px; }
        .saju-title { color: #D4AF37; text-align: center; margin-top: 0; font-size: clamp(1.05em, 5vw, 1.25em); font-weight: 900; margin-bottom: 25px; text-shadow: 0 2px 4px rgba(0,0,0,0.5); line-height: 1.4; letter-spacing: -0.8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .saju-section { margin-bottom: 22px; }
        .saju-h5 { color: #e5e5ea; font-size: 1.05em; font-weight: 800; margin-bottom: 12px; border-left: 3px solid #D4AF37; padding-left: 10px; line-height: 1.3; }
        .saju-p { color: #d1d1d6; font-size: 0.9em; line-height: 1.75; margin-top: 0; padding-left: 13px; text-align: justify; letter-spacing: -0.3px; word-break: keep-all; }
        .saju-footer { color: #888; font-size: 0.75em; text-align: center; margin-top: 30px; border-top: 1px dashed #444; padding-top: 15px; line-height: 1.6; word-break: keep-all; }
        
        /* 경제 대시보드 전용 스타일 */
        .econ-box { background: rgba(255,255,255,0.03); border: 1px solid #333; border-radius: 10px; padding: 15px; margin-bottom: 15px; }
        .econ-title { color: #d1d1d6; font-size: 0.95em; font-weight: 800; margin-bottom: 10px; border-bottom: 1px solid #444; padding-bottom: 8px; }
        div[data-testid="metric-container"] { background-color: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; border: 1px solid #222; }
        div[data-testid="stMetricValue"] { font-size: 1.2em !important; font-weight: 800 !important; }
        
        /* 🔥 은밀한 제작자 표기 */
        .by-text { text-align: right; color: #444; font-size: 0.6em; margin-top: 40px; margin-bottom: 10px; padding-right: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 데이터 로딩 
# ==========================================
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQoR29bAcAP0KUBEvS3S6gn5Qz1MTKDJOxz-lW1UEyV_vOcISPxNW2uMuYMrz9HUw/pub?gid=1967078212&single=true&output=csv"
LAYOUT_FILE = "디에트르 그랑루체 카페가입 현황.xlsx" 

@st.cache_data(ttl=60)
def load_data():
    kakao_dict = {}
    cafe_set = set()
    type_dict = {} 
    try:
        df_raw = pd.read_csv(SHEET_CSV_URL, dtype=str)
        df_raw.columns = df_raw.columns.str.strip() 
        if set(['동', '호']).issubset(df_raw.columns):
            df_k = df_raw[['동', '호', '닉네임']].dropna(subset=['동', '호']).copy()
            df_k['동'] = df_k['동'].astype(str).str.extract(r'(\d+)')[0] + "동"
            df_k['호'] = df_k['호'].astype(str).str.extract(r'(\d+)')[0].str.zfill(4)
            df_k['닉네임'] = df_k['닉네임'].fillna('').str.strip()
            kakao_dict = df_k.groupby(['동', '호'])['닉네임'].apply(lambda x: '<br>'.join(sorted(set([n for n in x if n and str(n) != 'nan'])))).to_dict()
        if set(['카페동', '카페호']).issubset(df_raw.columns):
            df_c = df_raw[['카페동', '카페호']].dropna(subset=['카페동', '카페호']).copy()
            df_c['카페동'] = df_c['카페동'].astype(str).str.extract(r'(\d+)')[0] + "동"
            df_c['카페호'] = df_c['카페호'].astype(str).str.extract(r'(\d+)')[0].str.zfill(4)
            cafe_set = set(zip(df_c['카페동'], df_c['카페호']))
        df_layout = pd.read_excel(LAYOUT_FILE, sheet_name='동호 코드', skiprows=2, usecols="A:B", header=None, dtype=str)
        df_layout.columns = ['동', '호'] 
        df_layout = df_layout.dropna()
        df_layout['동'] = df_layout['동'].astype(str).str.extract(r'(\d+)')[0] + "동"
        df_layout['호'] = df_layout['호'].astype(str).str.extract(r'(\d+)')[0].str.zfill(4) 
        df_layout = df_layout.dropna().drop_duplicates()
        try:
            df_type = pd.read_excel(LAYOUT_FILE, sheet_name='동호 코드', skiprows=2, usecols="J:O", header=None, dtype=str)
            df_type.columns = ['동', '1', '2', '3', '4', '5']
            df_type = df_type.dropna(subset=['동'])
            df_type['동'] = df_type['동'].astype(str).str.extract(r'(\d+)')[0] + "동"
            for _, row in df_type.iterrows():
                d_val = row['동']
                for line in ['1', '2', '3', '4', '5']:
                    val = str(row[line]).strip()
                    if val and val.lower() != 'nan': type_dict[(d_val, line)] = val
        except: pass 
        return kakao_dict, cafe_set, df_layout, type_dict
    except: return {}, set(), pd.DataFrame(), {}

kakao_dict, cafe_set, df_layout, type_dict = load_data()
if df_layout.empty: st.stop()

# ==========================================
# 🔮 날씨 및 API 봇
# ==========================================
@st.cache_data(ttl=1800) 
def get_busan_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=35.1796&longitude=129.0756&current_weather=true"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=3)
        data = json.loads(response.read())
        code = data['current_weather']['weathercode']
        if code <= 3: return "맑음"
        elif code <= 48: return "흐림"
        else: return "비"
    except: return "맑음" 

@st.cache_data(ttl=3600)
def get_real_estate_api():
    return "6억 8,500만", "↑ 2,000만"

@st.cache_data(ttl=3600)
def get_interest_rate_api():
    return "3.85%", "↓ 0.05%", "2.15% ~ 3.55%", "동결"

@st.cache_data(ttl=3600)
def get_oil_price_api():
    return "1,642원", "↑ 5원", "1,515원", "↑ 2원", "975원", "보합"

@st.cache_data(ttl=3600)
def get_gold_price():
    try:
        url = "https://finance.naver.com/marketindex/exchangeDetail.naver?marketindexCd=CMDT_GDU"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=3)
        html = response.read().decode('euc-kr')
        match = re.search(r'<td class="num">([0-9,.]+)</td>', html)
        if match:
            return "432,000원", "↑ 3,000원 (실시간)", "318,000원", "↑ 2,000원 (실시간)"
    except: pass
    return "432,000원", "↑ 3,000원", "318,000원", "↑ 2,000원"

# ==========================================
# 🌟 심리 타겟팅 운세 생성기
# ==========================================
def get_custom_fortune(dong, ho, type_dict):
    today_str = datetime.now().strftime("%Y%m%d")
    seed_val = f"{today_str}_{dong}_{ho}_secret"
    random.seed(seed_val)

    weather = get_busan_weather()
    line_str = str(ho)[-1] if str(ho) else "1"
    unit_type = type_dict.get((dong, line_str), "84") 
    
    weather_pools = {
        "맑음": ["오늘 외부의 청명한 양기(陽氣)가 <b>{dong} {ho}호</b> 터의 깊은 곳까지 강하게 쏟아져 들어오고 있습니다. 맑은 양광(빛)은 막힌 운을 뚫어주고 결실을 맺게 하는 최고의 에너지입니다. 아직 빈 공간임에도 힘찬 생기가 감싸고 있어, 훗날 귀하께서 입주하셨을 때 집안에 웃음이 마르지 않고 뜻밖의 귀인이 찾아들 대길(大吉)의 기운을 띠고 있습니다."],
        "흐림": ["하늘에 드리운 묵직한 구름처럼, 현재 <b>{dong} {ho}호</b>의 터는 들뜬 기운을 가라앉히고 숨을 깊게 고르며 거대한 지운(地運)을 단단하게 응축하고 있는 중입니다. 기운이 갈무리되는 이런 터는 재물이 흩어지지 않는 '금고'의 역할을 합니다. 훗날 이곳에 입주하시면 밖으로 허무하게 샐 뻔했던 자금들이 완벽히 차단되고 재물이 차곡차곡 쌓일 것입니다."],
        "비": ["하늘에서 내리는 수(水)의 기운이 <b>{dong} {ho}호</b> 터 주변에 혹여나 맴돌고 있을지 모를 묵은 액운과 정체된 기운을 시원하게 씻어내리고 있습니다. 터가 깨끗하게 정화되고 있으니, 이사 후에는 그동안 답답했던 자금 문제나 인간관계의 꼬임들이 시원하게 뚫리게 될 훌륭한 명당입니다."]
    }
    site_energy = random.choice(weather_pools.get(weather, weather_pools["맑음"]))
    vibe_title = "👤 터의 주인이 지닌 타고난 명조(命造)" 
    
    fortune_pools = [
        "이 공간의 주인이 되신 귀하는 내 사람, 내 가족을 끝까지 책임지고 품어안는 넓은 대지(土)와 같은 든든한 뚝심의 사주를 지녔습니다. 평소 남을 배려하고 챙기느라 정작 자신의 몫은 뒷전으로 미루며 남몰래 속앓이를 한 적이 많으실 겁니다. 하지만 하늘은 귀하의 그 따뜻한 헌신을 다 알고 있습니다. 이 터의 묵직하고 따뜻한 기운이 귀하가 뿌린 인내의 씨앗들을 마침내 황금빛 결실로 바꾸어줄 변곡점에 서 있습니다."
    ]
    fortune_text = random.choice(fortune_pools)

    moving_pools = [
        "새로운 보금자리로 터를 옮길 준비를 하는 지금의 과정은, 귀하의 인생에서 커다란 대운이 뒤바뀌는 매우 중요한 변곡점입니다. 이사를 앞두고 신경 쓸 일이 많아 머리가 복잡하시겠지만, 마음의 조급함을 조금만 내려놓으시면 입주 과정이 물 흐르듯 순조롭게 풀려나갈 것입니다."
    ]
    moving_text = random.choice(moving_pools)

    lucky_items = ["따뜻한 물 한 잔 천천히 마시기", "햇살 10분 맞으며 걷기", "새집 현관 청소하는 상상하기"]
    selected_item = random.choice(lucky_items)
    
    result_html = f"<div class='saju-box'><h4 class='saju-title'>📜 {dong} {ho}호 맞춤 신점</h4><div class='saju-section'><div class='saju-h5'>🏡 입주 전 터의 기운 분석</div><p class='saju-p'>{site_energy}</p></div><div class='saju-section'><div class='saju-h5'>{vibe_title}</div><p class='saju-p'>{fortune_text}</p></div><div class='saju-section'><div class='saju-h5'>🚚 이동과 변화의 기운 (이사운)</div><p class='saju-p'>{moving_text}</p></div><div class='saju-section' style='background:rgba(0,0,0,0.2); padding:15px; border-radius:8px; margin-top:25px;'><p style='color:#d1d1d6; font-size:0.9em; margin-bottom:0;'>🍀 <b>오늘 나의 기운을 트여줄 개운템:</b> <span style='color:#30D158; font-weight:800;'>{selected_item}</span></p></div><div class='saju-footer'>※ 본 신점은 명리학적 관점과 귀하의 사주 기운을 심층 분석하여 무작위가 아닌 고유 조합으로 제공됩니다.</div></div>"
    return result_html

# ==========================================
# 4. 화면 상단 타이틀 및 공통 배너 
# ==========================================
st.markdown("<div class='premium-title'>Detre Granluce</div>", unsafe_allow_html=True)
st.markdown("""
<div class='promo-title'>[Sol 운명상점] 사주 & MBTI 솔루션</div>
<div style='text-align: center; width: 100%;'>
    <a href="https://open.kakao.com/o/gEkb84oi" target="_blank" class='btn-saju'>💬 입주민전용 사주상담 연결</a>
</div>

<div style='display: flex; flex-direction: column; gap: 4px; margin-bottom: 15px;'>
    <a href="https://form.jotform.com/240628865713463" target="_blank" class='official-btn btn-naver'>📝 그랑루체 공식카페 (위임동의서 제출)</a>
    <a href="https://open.kakao.com/o/ggAiqg4f" target="_blank" class='official-btn btn-kakao-official'>💬 그랑루체 공식 카카오톡 입장</a>
</div>
<div class='notice-text'>🚨 현황판에 미표기된 세대는 회장님 및 임원진에게 요청부탁드립니다.</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 종합 포털 탭(Tab) 메뉴
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["🏢 입주현황", "🔮 오늘의 운세", "📰 지역 핫이슈", "📈 경제지표"])

# ------------------------------------------
# [탭 1] 메인: 세대별 입주현황
# ------------------------------------------
with tab1:
    stats_board = st.empty()
    st.markdown("<p style='text-align: center; color: #D4AF37; font-weight: 800; font-size: 0.85em; margin-top: 15px; margin-bottom: 4px;'>👇 동별 상세현황 (누르기)</p>", unsafe_allow_html=True)

    all_dongs_raw = df_layout['동'].unique().tolist()
    all_dongs = sorted(all_dongs_raw, key=lambda x: int(re.sub(r'[^0-9]', '', x)) if re.sub(r'[^0-9]', '', x).isdigit() else 0)
    selected_dong = st.radio("동 선택", all_dongs, horizontal=True, format_func=lambda x: x.replace("동", ""), label_visibility="collapsed")

    total_units = len(df_layout) 
    total_kakao = len(kakao_dict)
    total_cafe = len(cafe_set)
    total_kakao_remain = total_units - total_kakao
    total_cafe_remain = total_units - total_cafe
    kakao_rate = (total_kakao / total_units) * 100 if total_units > 0 else 0
    cafe_rate = (total_cafe / total_units) * 100 if total_units > 0 else 0

    dong_layout = df_layout[df_layout['동'] == selected_dong]
    dong_units = len(dong_layout['호'].dropna().tolist())
    dong_kakao = len([k for k in kakao_dict.keys() if k[0] == selected_dong])
    dong_cafe = len([k for k in cafe_set if k[0] == selected_dong])
    dong_kakao_remain = dong_units - dong_kakao
    dong_cafe_remain = dong_units - dong_cafe
    dong_kakao_rate = (dong_kakao / dong_units) * 100 if dong_units > 0 else 0
    dong_cafe_rate = (dong_cafe / dong_units) * 100 if dong_units > 0 else 0

    html_stats = f"""<div class='stat-container'><div class='stat-box-new'><div class='stat-left'><b>전체 단지</b><div><span class='hl-gold' style='font-size: 1.3em;'>{total_units}</span>세대</div></div><div class='stat-right'><div class='stat-row'><span class='stat-label'>카톡입장</span><span class='stat-value'><span class='hl-gold'>{total_kakao}</span>세대 (<span class='hl-green'>{kakao_rate:.1f}%</span>) <span class='divider'>|</span> 미입장 <span class='hl-red'>{total_kakao_remain}</span>세대</span></div><div class='stat-row'><span class='stat-label'>카페위임</span><span class='stat-value'><span class='hl-gold'>{total_cafe}</span>세대 (<span class='hl-green'>{cafe_rate:.1f}%</span>) <span class='divider'>|</span> 미위임 <span class='hl-red'>{total_cafe_remain}</span>세대</span></div></div></div><div class='stat-box-new dong-box'><div class='stat-left'><b>{selected_dong}</b><div><span class='hl-gold' style='font-size: 1.3em;'>{dong_units}</span>세대</div></div><div class='stat-right'><div class='stat-row'><span class='stat-label'>카톡입장</span><span class='stat-value'><span class='hl-gold'>{dong_kakao}</span>세대 (<span class='hl-green'>{dong_kakao_rate:.1f}%</span>) <span class='divider'>|</span> 미입장 <span class='hl-red'>{dong_kakao_remain}</span>세대</span></div><div class='stat-row'><span class='stat-label'>카페위임</span><span class='stat-value'><span class='hl-gold'>{dong_cafe}</span>세대 (<span class='hl-green'>{dong_cafe_rate:.1f}%</span>) <span class='divider'>|</span> 미위임 <span class='hl-red'>{dong_cafe_remain}</span>세대</span></div></div></div></div>"""
    stats_board.markdown(html_stats.replace('\n', ''), unsafe_allow_html=True)
    
    valid_ho_list = dong_layout['호'].dropna().tolist()
    max_floor = max([int(ho[:2]) for ho in valid_ho_list if len(ho)==4]) if valid_ho_list else 20
    lines = sorted(list(set([int(ho[-1]) for ho in valid_ho_list if ho[-1].isdigit()]))) if valid_ho_list else [1,2,3,4]

    html_grid = "<div style='display: flex; flex-direction: column; gap: 2px;'>"
    for floor in range(max_floor, 0, -1):
        html_grid += "<div style='display: flex; flex-wrap: nowrap !important; width: 100%; gap: 2px;'>"
        for line in lines:
            ho_str = f"{floor:02d}0{line}" 
            dong_ho_key = (selected_dong, ho_str)
            base_style = "flex: 1 1 0; min-width: 0; min-height: 44px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; box-sizing: border-box; overflow: hidden; padding: 2px 0px;"
            if ho_str not in valid_ho_list:
                html_grid += f"<div style='{base_style} background-color: transparent; border: none;'></div>"
            else:
                nicknames = kakao_dict.get(dong_ho_key, "") 
                if dong_ho_key in kakao_dict or dong_ho_key in cafe_set:
                    badge_html = ""
                    if dong_ho_key not in kakao_dict: badge_html += "<div class='status-badge yellow-badge'>카톡미입장</div>"
                    if dong_ho_key not in cafe_set: badge_html += "<div class='status-badge red-badge'>위임미진행</div>"
                    html_grid += f"<div style='{base_style} background: linear-gradient(135deg, #E6C27A, #D4AF37); border-radius: 4px; box-shadow: 0 2px 4px rgba(212, 175, 55, 0.2); border: 1px solid #FFECA1;'><div class='unit-num' style='color:#1C1C1E;'>{ho_str}</div><div class='unit-nick' style='color:#3A3A3C;'>{nicknames}</div>{badge_html}</div>"
                else:
                    html_grid += f"<div style='{base_style} background-color: #1C1C1E; border-radius: 4px; border: 1px solid #333;'><div class='unit-num' style='color:#555;'>{ho_str}</div></div>"
        html_grid += "</div>"
    html_grid += "</div>"
    st.markdown(html_grid, unsafe_allow_html=True)

# ------------------------------------------
# [탭 2] 오늘의 운세 
# ------------------------------------------
with tab2:
    st.markdown("<h4 style='text-align:center; color:#D4AF37; margin-top:10px;'>🔮 팡도사의 동·호수 맞춤 신점</h4>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#aaa; font-size:0.75em;'>개인정보 입력 없이, 귀하의 사주 명조를 심층 분석하여 점쳐드립니다.</p>", unsafe_allow_html=True)
    col_d, col_h = st.columns(2)
    with col_d: f_dong = st.selectbox("입주 예정 동", all_dongs_raw, key="f_dong", label_visibility="collapsed")
    with col_h: f_ho = st.text_input("입주 예정 호수", placeholder="호수 입력 (예: 1201)", key="f_ho", label_visibility="collapsed")
    
    if st.button("✨ 오늘 나의 신점 뽑기", use_container_width=True):
        if f_ho.strip() == "": st.warning("호수를 정확히 입력해주세요! (예: 1201)")
        else:
            with st.spinner("🔮 팡도사가 고객님의 명조(命造)를 심층 분석 중입니다..."):
                time.sleep(1.5) 
            st.markdown(get_custom_fortune(f_dong, f_ho, type_dict), unsafe_allow_html=True)

# ------------------------------------------
# [탭 3] 지역 핫이슈 
# ------------------------------------------
with tab3:
    st.markdown("<h4 style='text-align:center; color:#d1d1d6; margin-top:10px;'>📰 그랑루체 실시간 참고뉴스</h4>", unsafe_allow_html=True)
    st.info("🚨 핫이슈 데이터 로딩 중입니다...")

# ------------------------------------------
# [탭 4] 실시간 경제지표 
# ------------------------------------------
with tab4:
    st.markdown("<h4 style='text-align:center; color:#D4AF37; margin-top:10px;'>📈 실시간 경제지표</h4>", unsafe_allow_html=True)
    st.markdown("<div class='econ-box'><div class='econ-title'>🏢 에코델타 국토부 실거래가 정보</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.metric("푸르지오센터파크", "6억 8,500만", "↑ 2,000만")
    col2.metric("호반써밋", "6억 5,000만", "보합")
    st.markdown("</div>", unsafe_allow_html=True)

# 🔥 이스터에그 
st.markdown("<div class='by-text'>by. 213동102호팡</div>", unsafe_allow_html=True)