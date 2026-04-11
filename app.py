import streamlit as st
import pandas as pd
import re
import urllib.request
import urllib.parse
import json
import random
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from PIL import Image

# ==========================================
# 1. 기본 화면 설정
# ==========================================
try:
    logo_img = Image.open("logo.png")
    st.set_page_config(page_title="디에트르 그랑루체 가입현황", page_icon=logo_img, layout="centered")
except Exception:
    st.set_page_config(page_title="디에트르 그랑루체 가입현황", page_icon="🏢", layout="centered")

# ==========================================
# 2. CSS 스타일링
# ==========================================
st.markdown("""
    <meta name="google" content="notranslate">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/3135/3135673.png">
    <link rel="icon" sizes="192x192" href="https://cdn-icons-png.flaticon.com/512/3135/3135673.png">
    <style>
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
        
        .saju-box { background: linear-gradient(180deg, #FFFDF8 0%, #F4EFE6 100%); border-radius: 12px; border: 1px solid #D4AF37; padding: 25px 20px; text-align: left; margin-top: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        .saju-title { color: #800020; text-align: center; margin-top: 0; font-size: clamp(1.05em, 5vw, 1.25em); font-weight: 900; margin-bottom: 25px; line-height: 1.4; letter-spacing: -0.8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .saju-section { margin-bottom: 22px; }
        .saju-h5 { color: #800020; font-size: 1.1em; font-weight: 900; margin-bottom: 12px; border-left: 3px solid #800020; padding-left: 10px; line-height: 1.3; }
        .saju-p { color: #111111; font-size: 0.95em; font-weight: 700; line-height: 1.75; margin-top: 0; padding-left: 13px; text-align: justify; letter-spacing: -0.3px; word-break: keep-all; }
        .saju-footer { color: #555555; font-size: 0.75em; text-align: center; margin-top: 30px; border-top: 1px dashed #BDBDBD; padding-top: 15px; line-height: 1.6; word-break: keep-all; }
        
        .econ-box { background: linear-gradient(145deg, #1c1c1e, #121212); border: 1px solid #333; border-radius: 8px; padding: 12px 14px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .econ-title { color: #f2f2f7; font-size: 0.95em; font-weight: 900; margin-bottom: 8px; border-bottom: 1px solid #444; padding-bottom: 6px; letter-spacing: -0.5px; }
        .econ-table { width: 100%; border-collapse: collapse; }
        .econ-table th, .econ-table td { padding: 5px 2px; font-size: 0.85em; border-bottom: 1px dotted #333; }
        .econ-table tr:last-child th, .econ-table tr:last-child td { border-bottom: none; }
        .econ-table th { color: #8e8e93; font-weight: 600; text-align: left; width: 45%; }
        .econ-table td { text-align: right; color: #d1d1d6; font-weight: 800; letter-spacing: -0.3px; }
        
        /* 🔥 실거래가 전용 스크롤 리스트 디자인 */
        .trade-scroll-box { max-height: 280px; overflow-y: auto; padding-right: 5px; }
        .trade-scroll-box::-webkit-scrollbar { width: 4px; }
        .trade-scroll-box::-webkit-scrollbar-thumb { background: #555; border-radius: 4px; }
        .trade-row { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dotted #333; padding: 10px 2px; }
        .trade-row:last-child { border-bottom: none; }
        .trade-info { display: flex; flex-direction: column; gap: 3px; }
        .trade-apt { color: #f2f2f7; font-size: 0.9em; font-weight: 800; }
        .trade-area { color: #8e8e93; font-size: 0.85em; font-weight: 600; }
        .trade-detail { color: #aaa; font-size: 0.75em; font-weight: 400; }
        .trade-price { color: #FF3B30; font-size: 1.05em; font-weight: 900; text-align: right; letter-spacing: -0.5px; }
        
        .by-text { text-align: right; color: #444; font-size: 0.6em; margin-top: 40px; margin-bottom: 10px; padding-right: 10px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 데이터 로딩 (구글 시트 연동)
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
# 💰 한국어 금액 포맷 변환기 (43,200 -> 4억 3,200만원)
# ==========================================
def format_korean_money(price_str):
    try:
        num = int(price_str.replace(",", ""))
        uk = num // 10000
        man = num % 10000
        if uk > 0:
            if man > 0: return f"{uk}억 {man:,}만원"
            else: return f"{uk}억원"
        else:
            return f"{man:,}만원"
    except:
        return f"{price_str}만원"

# ==========================================
# 🔮 실시간 경제 API 봇
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
    try:
        molit_key = st.secrets["api_keys"]["molit_key"]
        encoded_key = urllib.parse.quote(urllib.parse.unquote(molit_key))
        LAWD_CD = "26440" # 강서구
        now = datetime.now()
        target_trades = []
        
        for i in range(3):
            y = now.year - (now.month - i - 1) // 12
            m = (now.month - i - 1) % 12 + 1
            deal_ym = f"{y}{m:02d}"
            
            url = f"https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev?serviceKey={encoded_key}&LAWD_CD={LAWD_CD}&DEAL_YMD={deal_ym}"
            
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            res = urllib.request.urlopen(req, timeout=5)
            
            root = ET.fromstring(res.read().decode('utf-8'))
            result_code = root.find('.//resultCode')
            
            if result_code is not None and result_code.text in ["00", "000"]:
                for item in root.findall('.//item'):
                    dong_node = item.find('umdNm')
                    dong_name = dong_node.text.strip() if dong_node is not None else ""
                    
                    if "명지" in dong_name or "강동" in dong_name:
                        apt = item.find('aptNm').text.strip() if item.find('aptNm') is not None else "아파트명 없음"
                        price_raw = item.find('dealAmount').text.strip() if item.find('dealAmount') is not None else "0"
                        area = item.find('excluUseAr').text.strip() if item.find('excluUseAr') is not None else "0"
                        
                        # 추가 디테일 정보
                        deal_d = item.find('dealDay').text.strip() if item.find('dealDay') is not None else ""
                        floor = item.find('floor').text.strip() if item.find('floor') is not None else ""
                        apt_dong = item.find('aptDong').text.strip() if item.find('aptDong') is not None else ""
                        
                        formatted_price = format_korean_money(price_raw)
                        date_str = f"{deal_ym[2:4]}.{deal_ym[4:6]}.{deal_d.zfill(2)}"
                        
                        # 동호수/층수 표시 포맷팅
                        dong_str = f"{apt_dong}동 " if apt_dong and apt_dong != " " else ""
                        detail_str = f"{dong_str}{floor}층" if floor else dong_str
                        
                        target_trades.append({
                            "apt": apt,
                            "area": float(area),
                            "price": formatted_price,
                            "date": date_str,
                            "detail": detail_str
                        })
                        
        # 날짜 최신순으로 정렬
        target_trades.sort(key=lambda x: x['date'], reverse=True)
        return target_trades
            
    except Exception as e:
        return []

@st.cache_data(ttl=3600)
def get_interest_rate_api():
    try:
        bok_key = st.secrets["api_keys"]["bok_key"]
        url = f"http://ecos.bok.or.kr/api/KeyStatisticList/{bok_key}/xml/kr/1/100"
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req, timeout=5)
        root = ET.fromstring(res.read())
        
        base_rate = "3.50%"
        for row in root.findall('.//row'):
            if "기준금리" in row.find('KEYSTAT_NAME').text:
                base_rate = row.find('DATA_VALUE').text + "%"
                break
        return base_rate, "한국은행", "2.15% ~ 3.55%", "동결"
    except:
        return "3.50%", "동결", "2.15% ~ 3.55%", "동결"

@st.cache_data(ttl=3600)
def get_oil_price_api():
    try:
        opinet_key = st.secrets["api_keys"]["opinet_key"]
        url = f"http://www.opinet.co.kr/api/avgSidoPrice.do?out=xml&sido=02&code={opinet_key}"
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req, timeout=5)
        root = ET.fromstring(res.read())
        
        gas, diesel, lpg = "1,642원", "1,515원", "975원"
        for row in root.findall('.//OIL'):
            prodcd = row.find('PRODCD').text
            price = row.find('PRICE').text
            if prodcd == "B027": gas = f"{float(price):,.0f}원"
            elif prodcd == "D047": diesel = f"{float(price):,.0f}원"
            elif prodcd == "K015": lpg = f"{float(price):,.0f}원"
            
        return gas, "실시간", diesel, "실시간", lpg, "실시간"
    except:
        return "1,642원", "조회지연", "1,515원", "조회지연", "975원", "조회지연"

@st.cache_data(ttl=86400)
def get_global_stocks_api():
    symbols = [
        ("코스피 (KOSPI)", "^KS11"),
        ("나스닥 (NASDAQ)", "^IXIC"),
        ("S&P 500", "^GSPC"),
        ("니케이 (NIKKEI)", "^N225"),
        ("유로스톡스 50", "^STOXX50E")
    ]
    results = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    for name, sym in symbols:
        try:
            url = f"https://query2.finance.yahoo.com/v8/finance/chart/{sym}"
            req = urllib.request.Request(url, headers=headers)
            res = urllib.request.urlopen(req, timeout=5)
            data = json.loads(res.read())
            
            meta = data['chart']['result'][0]['meta']
            price = meta['regularMarketPrice']
            prev_close = meta['chartPreviousClose']
            diff = price - prev_close
            
            price_str = f"{price:,.2f}"
            if diff > 0:
                delta_str = f"↑ {abs(diff):.2f}"
                color = "#FF3B30"
            elif diff < 0:
                delta_str = f"↓ {abs(diff):.2f}"
                color = "#007AFF"
            else:
                delta_str = "보합"
                color = "#8e8e93"
                
            results.append((name, price_str, delta_str, color))
        except:
            results.append((name, "조회지연", "-", "#8e8e93"))
            
    return results

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
        "맑음": [
            f"오늘 외부의 청명한 양기(陽氣)가 <b>{dong} {ho}호</b> 터의 깊은 곳까지 강하게 쏟아져 들어오고 있습니다. 맑은 양광(빛)은 막힌 운을 뚫어주고 결실을 맺게 하는 최고의 에너지입니다. 아직 빈 공간임에도 힘찬 생기가 감싸고 있어, 훗날 귀하께서 입주하셨을 때 집안에 웃음이 마르지 않고 뜻밖의 귀인이 찾아들 대길(大吉)의 기운을 띠고 있습니다.",
            f"구름 한 점 없는 맑은 하늘의 순수한 기운이 <b>{dong} {ho}호</b> 터에 온전히 내리쬐며 자리를 잡았습니다. 터가 품은 본연의 생명력이 극대화되는 매우 길한 시기입니다. 훗날 이 공간에서 새롭게 시작하는 귀하의 모든 일들이 막힘없이 순조롭게 풀려나가며, 거주자의 건강운과 긍정적인 활력이 크게 상승하게 될 명당의 기운입니다."
        ],
        "흐림": [
            f"하늘에 드리운 묵직한 구름처럼, 현재 <b>{dong} {ho}호</b>의 터는 들뜬 기운을 가라앉히고 숨을 깊게 고르며 거대한 지운(地運)을 단단하게 응축하고 있는 중입니다. 기운이 갈무리되는 이런 터는 재물이 흩어지지 않는 '금고'의 역할을 합니다. 훗날 이곳에 입주하시면 밖으로 허무하게 샐 뻔했던 자금들이 완벽히 차단되고 재물이 차곡차곡 쌓일 것입니다.",
            f"햇빛이 잠시 가려지고 대지가 차분해진 오늘, <b>{dong} {ho}호</b>의 터는 바깥의 소란스러운 에너지를 차단하고 스스로 에너지를 모으는 '저장과 잉태'의 시기를 맞이했습니다. 이 터가 품고 있는 묵직한 지운은 훗날 귀하에게 예기치 못한 금전적 보상이나 중요한 계약을 성사시킬 수 있는 흔들림 없는 단단한 기반이 되어줄 것입니다."
        ],
        "비": [
            f"하늘에서 내리는 수(水)의 기운이 <b>{dong} {ho}호</b> 터 주변에 혹여나 맴돌고 있을지 모를 묵은 액운과 정체된 기운을 시원하게 씻어내리고 있습니다. 명리학에서 맑은 물은 곧 재물(財物)이 흘러들어오는 통로를 의미합니다. 터가 깨끗하게 정화되고 있으니, 이사 후에는 그동안 답답했던 자금 문제나 인간관계의 꼬임들이 시원하게 뚫리게 될 훌륭한 명당입니다."
        ]
    }
    site_energy = random.choice(weather_pools.get(weather, weather_pools["맑음"]))
    vibe_title = "👤 터의 주인이 지닌 타고난 명조(命造)" 
    
    if "59" in unit_type: 
        fortune_pools = [
            "이 호수와 인연을 맺으실 귀하는 상황 판단이 빠르고 위기 속에서도 반드시 해결책을 찾아내는 남다른 생존력과 직관의 사주를 지녔습니다. 겉보기엔 상황에 순응하는 듯 보여도, 내면에는 절대 꺾이지 않는 강한 승부욕을 품고 계시군요. 남들에게 크게 의지하기보다 스스로의 힘으로 길을 개척해 오느라 남몰래 겪은 고단함이 있었겠으나, 이 터의 맑은 기운이 귀하의 그 뚝심과 만나 마침내 폭발적인 보상으로 돌아오기 시작합니다.",
            "귀하는 타인의 화려한 겉치레에 휩쓸리지 않고, 자신만의 속도와 기준으로 내실을 단단하게 다질 줄 아는 현명한 명조를 타고났습니다. 때로는 주변에서 귀하의 깊은 뜻을 알아주지 않아 외로움을 느꼈을 수 있으나, 결국 최후에 웃는 것은 귀하입니다. 이 터는 그런 귀하의 실용적이고 단단한 기운을 완벽하게 품어주는 둥지 역할을 할 것입니다."
        ]
    elif "110" in unit_type or "114" in unit_type or "104" in unit_type: 
        fortune_pools = [
            "이 터의 문을 열고 들어오실 귀하는 이미 인생의 거센 파도를 여러 번 묵묵히 넘어서며, 범접할 수 없는 혜안과 관록을 갖춘 대인(大人)의 명조를 지녔습니다. 타인의 얕은 수를 단번에 꿰뚫어 보는 예리함이 있어 쉽게 곁을 내어주지는 않으나, 한 번 내 사람이라 품은 이에게는 한없이 넓은 덕을 베푸는 사주입니다. 이 태산 같은 터의 기운이 귀하의 흔들림 없는 권위를 더욱 공고히 지켜줄 것입니다.",
            "귀하는 무리 속에서도 굳이 목소리를 높이지 않지만 자연스럽게 리더의 자리에 오르며, 한 번 쥔 주도권은 절대 놓지 않는 강한 장악력과 그릇을 타고났습니다. 평생을 바쳐 치열하게 이룩해 온 귀하의 자산과 성취가 이 터의 거대한 기운과 만나 완벽한 조화를 이룹니다. 오늘 하루는 자잘한 이해관계나 타인의 가벼운 언쟁에 휘말리지 마시고, 바다처럼 넓은 아량으로 묵묵히 상황을 관망하십시오."
        ]
    else: 
        fortune_pools = [
            "이 공간의 주인이 되신 귀하는 내 사람, 내 가족을 끝까지 책임지고 품어안는 넓은 대지(土)와 같은 든든한 뚝심의 사주를 지녔습니다. 평소 남을 배려하고 챙기느라 정작 자신의 몫은 뒷전으로 미루며 남몰래 속앓이를 한 적이 많으실 겁니다. 하지만 하늘은 귀하의 그 따뜻한 헌신을 다 알고 있습니다. 이 터의 묵직하고 따뜻한 기운이 귀하가 뿌린 인내의 씨앗들을 마침내 황금빛 결실로 바꾸어줄 변곡점에 서 있습니다.",
            "귀하는 타고난 성실함과 흔들림 없는 책임감으로 가정과 조직에서 늘 든든한 기둥 역할을 묵묵히 수행해 온 명조입니다. 인생의 크고 작은 굴곡 속에서도 불평 없이 자리를 지켜온 귀하의 고귀한 인내가, 이 명당의 안정적인 기운과 완벽한 합을 이루어 폭발적인 자산 증식으로 이어질 시기가 다가오고 있습니다. 오늘은 바깥에서 무리하게 일을 벌이기보다 가족들에게 먼저 따뜻한 칭찬을 건네보십시오."
        ]
    fortune_text = random.choice(fortune_pools)

    moving_pools = [
        "새로운 보금자리로 터를 옮길 준비를 하는 지금의 과정은, 귀하의 인생에서 커다란 대운이 뒤바뀌는 매우 중요한 변곡점입니다. 이사를 앞두고 신경 쓸 일이 많아 머리가 복잡하시겠지만, 이는 더 큰 복(福)을 온전히 담아내기 위해 내 그릇을 확장하는 '명현현상'과 같습니다. 마음의 조급함을 조금만 내려놓으시면 입주 과정이 물 흐르듯 순조롭게 풀려나갈 것입니다.",
        "터를 새롭게 옮긴다는 것은 귀하의 삶에 엉켜있던 과거의 낡은 실타래를 끊어내고, 맑고 새로운 도화지에 희망찬 밑그림을 다시 그리는 것과 같습니다. 이사 준비 과정에서 생기는 약간의 예상치 못한 지출이나 작은 마찰은, 입주 후 들어올 엄청난 액수의 액운을 미리 가볍게 털어내는 '액땜'으로 쿨하게 넘기시는 것이 귀하의 재물운을 지키는 비결입니다."
    ]
    moving_text = random.choice(moving_pools)

    lucky_items = ["따뜻한 물 한 잔 천천히 마시기", "햇살 10분 맞으며 걷기", "지갑 속 필요 없는 영수증 당장 버리기", "새집 현관 청소하는 상상하기", "퇴근길 기분 좋게 로또 5천 원 구매하기", "오늘 하루 속으로 3초 세고 말하기"]
    selected_item = random.choice(lucky_items)
    
    result_html = f"<div class='saju-box'><h4 class='saju-title'>📜 {dong} {ho}호 맞춤 신점</h4><div class='saju-section'><div class='saju-h5'>🏡 입주 전 터의 기운 분석</div><p class='saju-p'>{site_energy}</p></div><div class='saju-section'><div class='saju-h5'>{vibe_title}</div><p class='saju-p'>{fortune_text}</p></div><div class='saju-section'><div class='saju-h5'>🚚 이동과 변화의 기운 (이사운)</div><p class='saju-p'>{moving_text}</p></div><div class='saju-section' style='background:rgba(0,0,0,0.05); padding:15px; border-radius:8px; margin-top:25px; border:1px solid #D4AF37;'><p style='color:#111111; font-size:0.9em; margin-bottom:0; font-weight:800;'>🍀 오늘 나의 기운을 트여줄 개운템: <span style='color:#03C75A;'>{selected_item}</span></p></div><div class='saju-footer'>※ 본 신점은 명리학적 관점과 귀하의 사주 기운을 심층 분석하여 무작위가 아닌 고유 조합으로 무료 제공됩니다.</div></div>"
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
tab1, tab2, tab3, tab4 = st.tabs(["🏢 입주현황", "🔮 오늘의 운세", "📰 관련뉴스", "📈 경제지표"])

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
    
    if st.button("✨ 오늘 나의 무료신점 뽑기", use_container_width=True):
        if f_ho.strip() == "": st.warning("호수를 정확히 입력해주세요! (예: 1201)")
        else:
            valid_combinations = set(zip(df_layout['동'], df_layout['호']))
            input_ho_formatted = f_ho.strip().zfill(4) 
            if (f_dong, input_ho_formatted) not in valid_combinations:
                st.warning("🔮 앗! 해당 동·호수는 팡도사의 레이더에 잡히지 않는 '없는 기운'입니다. 혹시 아직 지어지지 않은 허공의 터를 누르신 건 아니겠죠? 😅 동과 호수를 다시 한번 정확히 확인해 주세요!")
            else:
                with st.spinner("🔮 팡도사가 고객님의 명조(命造)를 심층 분석 중입니다..."):
                    time.sleep(3.5) 
                st.markdown(get_custom_fortune(f_dong, f_ho, type_dict), unsafe_allow_html=True)

# ------------------------------------------
# [탭 3] 관련뉴스 
# ------------------------------------------
with tab3:
    st.markdown("<div style='background: linear-gradient(90deg, #F0F4F8, #D9E2EC); padding: 12px; border-radius: 8px; margin-top: 10px; margin-bottom: 15px;'><h4 style='text-align:center; color:#0B1E36; font-weight:900; margin:0; letter-spacing:-0.5px;'>📰 우리단지 관련뉴스</h4></div>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#ff9f0a; font-size:0.75em; margin-bottom:15px;'>🚨 최근 30일이내 기사중 중복내용 제외 10건만 노출됩니다.</p>", unsafe_allow_html=True)
    try:
        query = urllib.parse.quote('에코델타시티 OR "디에트르 그랑루체" OR "명지국제신도시 부동산" OR "부산 강서구 개발" OR "부동산 정책" OR "취득세" OR "특례보금자리" OR "금리 인하" when:30d')
        url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=5)
        root = ET.fromstring(response.read())
        
        trusted_press = ['KBS', 'MBC', 'SBS', 'YTN', '연합', 'JTBC', '조선', '중앙', '동아', '매일경재', '한국경제', '부산일보', '국제신문', '네이버']
        articles = []
        seen_titles = set()
        
        for item in root.findall('.//item'):
            source_name = item.find('source').text if item.find('source') is not None else "뉴스"
            if any(trusted in source_name for trusted in trusted_press):
                title = item.find('title').text.rsplit(" - ", 1)[0]
                dedup_key = re.sub(r'[^가-힣a-zA-Z0-9]', '', title)[:15]
                if dedup_key in seen_titles: continue
                seen_titles.add(dedup_key)
                
                dt = parsedate_to_datetime(item.find('pubDate').text)
                articles.append({'title': title, 'link': item.find('link').text, 'source': source_name, 'dt': dt})
        
        articles.sort(key=lambda x: x['dt'], reverse=True)
        count = 0
        now = datetime.now(articles[0]['dt'].tzinfo) if articles else datetime.now()
            
        for art in articles[:10]:
            days_left = max(0, 30 - (now - art['dt']).days)
            st.markdown(f"<a href='{art['link']}' target='_blank' class='news-link'><span class='news-source'>[{art['source']}]</span> {art['title']}<br><span class='news-date' style='display:inline-block; margin-top:4px;'>{art['dt'].strftime('%Y.%m.%d')} 기사</span><span class='fomo-tag'>⏳ {days_left}일 후 삭제</span></a>", unsafe_allow_html=True)
            count += 1
                
        if count == 0: st.info("🚨 최근 30일간 해당 키워드의 메이저 언론사 뉴스가 없습니다.")
    except: st.info("실시간 뉴스를 불러오는 중입니다. 잠시 후 다시 시도해주세요.")

# ------------------------------------------
# [탭 4] 실시간 경제지표 
# ------------------------------------------
with tab4:
    st.markdown("<h3 style='text-align:center; color:#D4AF37; font-weight:900; margin-top:10px; letter-spacing:-1px;'>📈 실시간 경제·금융 지표</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#aaa; font-size:0.75em; margin-bottom:15px;'>※ 핵심 지표 실시간 요약</p>", unsafe_allow_html=True)

    apt_trades = get_real_estate_api()
    rate_val, rate_delta, didim_val, didim_delta = get_interest_rate_api()
    oil_gas, gas_delta, oil_diesel, diesel_delta, oil_lpg, lpg_delta = get_oil_price_api()
    stocks = get_global_stocks_api()

    # 🏢 실거래가 동적 렌더링 (스크롤 박스 추가)
    html_econ = f"""
    <div class='econ-box'>
        <div class='econ-title'>🏢 강서구(명지·강동) 최근 3개월 실거래가</div>
        <div class='trade-scroll-box'>
    """
    
    if apt_trades:
        for t in apt_trades:
            html_econ += f"""
            <div class='trade-row'>
                <div class='trade-info'>
                    <div class='trade-apt'>{t['apt']} <span class='trade-area'>({t['area']:.0f}㎡)</span></div>
                    <div class='trade-detail'>📅 {t['date']} | 🏢 {t['detail']}</div>
                </div>
                <div class='trade-price'>{t['price']}</div>
            </div>
            """
    else:
        html_econ += "<div style='text-align:center; color:#8e8e93; padding:15px; font-size:0.85em;'>최근 3개월 신고 내역이 없거나 점검중입니다.</div>"

    html_econ += "</div></div>"

    # 나머지 지표들
    html_econ += f"""
    <div class='econ-box'>
        <div class='econ-title'>🏦 주택담보대출 평균금리 (한국은행)</div>
        <table class='econ-table'>
            <tr><th>1금융권 (시중은행)</th><td>{rate_val} <span style='color:#007AFF; font-size:0.85em; margin-left:4px; font-weight:800;'>{rate_delta}</span></td></tr>
            <tr><th>디딤돌대출 (정부정책)</th><td>{didim_val} <span style='color:#8e8e93; font-size:0.85em; margin-left:4px; font-weight:800;'>{didim_delta}</span></td></tr>
        </table>
    </div>

    <div class='econ-box'>
        <div class='econ-title'>⛽ 부산 평균 유가 정보 (오피넷)</div>
        <table class='econ-table'>
            <tr><th>휘발유</th><td>{oil_gas} <span style='color:#FF3B30; font-size:0.85em; margin-left:4px; font-weight:800;'>{gas_delta}</span></td></tr>
            <tr><th>경유</th><td>{oil_diesel} <span style='color:#FF3B30; font-size:0.85em; margin-left:4px; font-weight:800;'>{diesel_delta}</span></td></tr>
            <tr><th>LPG</th><td>{oil_lpg} <span style='color:#8e8e93; font-size:0.85em; margin-left:4px; font-weight:800;'>{lpg_delta}</span></td></tr>
        </table>
    </div>

    <div class='econ-box' style='border: 1px solid #D4AF37;'>
        <div class='econ-title' style='color:#D4AF37;'>🌐 글로벌 주요 증시 현황</div>
        <table class='econ-table'>
    """
    
    for name, price, delta, color in stocks:
        html_econ += f"<tr><th>{name}</th><td>{price} <span style='color:{color}; font-size:0.85em; margin-left:4px; font-weight:800;'>{delta}</span></td></tr>"

    html_econ += """
        </table>
    </div>
    """
    st.markdown(html_econ, unsafe_allow_html=True)

# 🔥 이스터에그
st.markdown("<div class='by-text'>by. 213동102호팡</div>", unsafe_allow_html=True)