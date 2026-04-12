import streamlit as st
import pandas as pd
import re
import urllib.request
import urllib.parse
import json
import random
import time
import xml.etree.ElementTree as ET
from datetime import datetime, date
from email.utils import parsedate_to_datetime
from PIL import Image
import streamlit.components.v1 as components

# ==========================================
# [블록 1] 기본 화면 설정 및 🚨 CCTV + 좀비 자동복구 엔진 (에러 감지 시 즉시 새로고침)
# ==========================================
try:
    logo_img = Image.open("detre_logo.png")
    st.set_page_config(page_title="디에트르 그랑루체 입주민 포털", page_icon=logo_img, layout="centered")
except Exception:
    st.set_page_config(page_title="디에트르 그랑루체 입주민 포털", page_icon="🏢", layout="centered")

GA_ID = "G-K4JM55MDEQ"
cpr_script = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  /* 1. 구글 애널리틱스 (CCTV) */
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');

  /* 2. 🔥 좀비 자동복구 엔진: 투명 방(iframe)을 넘어 본체(parent)를 직접 예의주시! */
  // 1.5초마다 바깥 진짜 화면에 에러가 떴는지 감시합니다.
  setInterval(function() {{
      try {{
          var parentDoc = window.parent.document;
          var bodyText = parentDoc.body.innerText || "";
          
          // 화면에 아래와 같은 에러 단어들이 하나라도 포착되면!
          if (bodyText.includes('500 Server Error') || 
              bodyText.includes('Connection error') || 
              bodyText.includes('Connection lost') ||
              bodyText.includes('A fatal error has occurred')) {{
              
              // 아버님이 앱 끄고 다시 켤 필요 없이, 지가 알아서 즉시 새로고침!!!
              window.parent.location.reload(true);
          }}
      }} catch(e) {{
          // 권한 에러 무시
      }}
  }}, 1500);

  // 사용자가 지니뮤직이나 유튜브를 보다가 다시 우리 어플 화면으로 돌아왔을 때 즉시 체크!
  try {{
      window.parent.document.addEventListener('visibilitychange', function() {{
          if (window.parent.document.visibilityState === 'visible') {{
              setTimeout(function() {{
                  var parentDoc = window.parent.document;
                  var bodyText = parentDoc.body.innerText || "";
                  if (bodyText.includes('500 Server Error') || bodyText.includes('Connection error') || bodyText.includes('Connection lost')) {{
                      window.parent.location.reload(true);
                  }}
              }}, 500); // 돌아오고 0.5초 뒤에 에러창 떠있으면 가차없이 새로고침!
          }}
      }});
  }} catch(e) {{}}
</script>
"""
components.html(cpr_script, width=0, height=0)

# ==========================================
# [블록 2] CSS 스타일링 (📱 모바일 깨짐 완벽 방어 + UX 디테일 강화)
# ==========================================
st.markdown("""
    <meta name="google" content="notranslate">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/3135/3135673.png">
    <link rel="icon" sizes="192x192" href="https://cdn-icons-png.flaticon.com/512/3135/3135673.png">
    <style>
        html, body, #root, .stApp, .main, [data-testid="stAppViewContainer"], section {
            overscroll-behavior: none !important; overscroll-behavior-y: none !important; overscroll-behavior-x: none !important;
        }
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * { font-family: 'Pretendard', sans-serif; box-sizing: border-box; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .block-container { padding-top: 1.0rem !important; padding-bottom: 0.5rem !important; padding-left: 4px !important; padding-right: 4px !important; max-width: 100% !important; }
        
        .premium-title { font-size: clamp(2.0em, 8vw, 2.8em); font-weight: 900; text-align: center; color: #2b6cb0; text-shadow: 0 2px 10px rgba(43, 108, 176, 0.3); margin-bottom: 12px; line-height: 1.2; }
        
        .btn-vip-saju { display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #800020, #4a0012); color: #D4AF37 !important; border: 1px solid #D4AF37; font-weight: 900; font-size: 0.9em; padding: 12px 16px; border-radius: 10px; text-decoration: none !important; margin-top: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.4); text-shadow: 0 1px 2px rgba(0,0,0,0.8); }
        
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
        
        /* 🚨 라디오버튼 모바일 세로쓰기 깨짐 완벽 방어 & 선택 시 음영 채우기 */
        div[role="radiogroup"] { display: flex !important; flex-wrap: wrap !important; width: 100% !important; gap: 2px !important; justify-content: center !important; margin-bottom: 10px !important; }
        div[role="radiogroup"] > label { flex: 1 1 auto !important; min-width: 60px !important; background-color: transparent !important; border: none !important; border-bottom: 2px solid #333 !important; padding: 8px 4px !important; cursor: pointer !important; text-align: center !important; transition: all 0.3s ease; }
        div[role="radiogroup"] > label[data-checked="true"] { 
            background: #D4AF37 !important; /* 🔥 찐한 골드 100% 팍! */
            border-bottom: 2px solid #D4AF37 !important; 
            border-radius: 6px 6px 0 0 !important;
        }
        div[role="radiogroup"] > label[data-checked="true"] p { 
            color: #111111 !important; /* 🔥 배경이 골드니까 글씨는 진한 흑색으로! */
            font-weight: 900 !important; 
        }
        }
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
        
        .econ-table { width: 100%; border-collapse: collapse; margin-top: 5px; }
        .econ-table th, .econ-table td { padding: 10px 4px; font-size: 0.85em; border-bottom: 1px dotted #333; vertical-align: middle; }
        .econ-table tr:last-child th, .econ-table tr:last-child td { border-bottom: none; }
        .econ-table th { color: #8e8e93; font-weight: 600; text-align: left; }
        .econ-table td { text-align: right; color: #d1d1d6; font-weight: 800; letter-spacing: -0.3px; }

        [data-testid="stExpander"] { background: linear-gradient(145deg, #1c1c1e, #121212) !important; border: 1px solid #333 !important; border-radius: 8px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important; margin-bottom: 12px !important; }
        [data-testid="stExpander"] summary { padding: 12px 14px !important; }
        [data-testid="stExpander"] summary p { color: #f2f2f7 !important; font-size: 0.95em !important; font-weight: 900 !important; letter-spacing: -0.5px !important; }
        [data-testid="stExpanderDetails"] { padding: 0 14px 12px 14px !important; }
        
        .trade-scroll-box { max-height: 350px; overflow-y: auto; padding-right: 5px; }
        .trade-scroll-box::-webkit-scrollbar { width: 4px; }
        .trade-scroll-box::-webkit-scrollbar-thumb { background: #555; border-radius: 4px; }
        .trade-row { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dotted #333; padding: 12px 2px; }
        .trade-row:last-child { border-bottom: none; }
        .trade-info { display: flex; flex-direction: column; gap: 4px; flex: 1; }
        .trade-apt { color: #f2f2f7; font-size: 0.9em; font-weight: 800; }
        .trade-area { color: #8e8e93; font-size: 0.85em; font-weight: 600; }
        .trade-detail { color: #aaa; font-size: 0.75em; font-weight: 500; }
        
        .trade-price-box { display: flex; flex-direction: column; align-items: flex-end; justify-content: center; min-width: 80px; }
        .trade-price { color: #fff; font-size: 0.85em; font-weight: 800; letter-spacing: -0.5px; } 
        .trade-delta { font-size: 0.70em; font-weight: 800; margin-top: 3px; letter-spacing: -0.5px; }
        
        .delta-up { color: #FF3B30 !important; }   
        .delta-down { color: #0A84FF !important; } 
        .delta-new { color: #FFFFFF !important; }  
        
        .by-text { text-align: right; color: #444; font-size: 0.6em; margin-top: 40px; margin-bottom: 10px; padding-right: 10px; }

        /* 🔥 계산기 CSS 추가 & 모바일 가로 스크롤 대응 */
        .calc-premium-title { font-size: clamp(2.0em, 8vw, 2.5em); font-weight: 900; text-align: center; color: #0A84FF !important; margin-bottom: 12px; line-height: 1.2; text-shadow: 0px 2px 4px rgba(0,0,0,0.1); }
        .calc-box { background: linear-gradient(145deg, #1c1c1e, #111111); border: 1px solid #D4AF37; border-radius: 12px; padding: 20px 15px; margin-top: 15px; text-align: center; box-shadow: 0 6px 15px rgba(0,0,0,0.2); }
        .calc-title { color: #D4AF37 !important; font-size: 0.95em; font-weight: 800; margin-bottom: 5px; }
        .calc-total { color: #ffffff !important; font-size: 2.2em; font-weight: 900; letter-spacing: -1px; margin-bottom: 10px; }
        .summary-box { background: linear-gradient(135deg, #1e3a8a, #0f172a); border-radius: 12px; padding: 25px 20px; color: white !important; margin-top: 25px; margin-bottom: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.3); }
        .summary-title { font-size: 1.3em; font-weight: 900; color: #93c5fd !important; margin-bottom: 15px; text-align: center; }
        .summary-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .summary-row:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
        .summary-label { font-size: 0.9em; font-weight: 600; color: #e2e8f0 !important; text-align: left; line-height: 1.4;}
        .summary-val { font-size: 1.3em; font-weight: 900; color: #ffffff !important; text-align: right; }
        
        /* 🔥 아버님 요청: 순수 입주 현금 글자 크기 살짝 축소 & 강제 한줄 고정 */
        .summary-val-highlight { font-size: clamp(1.15em, 4vw, 1.35em) !important; font-weight: 900; color: #fbbf24 !important; text-align: right; white-space: nowrap !important; word-break: keep-all; letter-spacing: -0.5px; }
        
        .table-responsive { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 10px; border-radius: 8px; }
        .calc-table { width: 100%; border-collapse: collapse; font-size: 0.85em; min-width: 320px; background: rgba(0,0,0,0.4); overflow: hidden; }
        .calc-table th { background: rgba(212,175,55,0.15); color: #D4AF37 !important; border-bottom: 1px solid #444; padding: 12px 4px; font-weight: 800; text-align: center; }
        .calc-table td { color: #ffffff !important; border-bottom: 1px dotted #444; padding: 12px 4px; text-align: center; font-weight: 600; }
        .hl-fixed { color: #34d399 !important; font-weight: 800; } 
        .hl-var { color: #f87171 !important; font-weight: 800; }  
        .disclaimer-box { background: rgba(255, 59, 48, 0.05); border: 1px solid rgba(255, 59, 48, 0.3); border-radius: 8px; padding: 12px; text-align: center; margin-top: 10px; }
        .disclaimer-text { color: gray; font-size: 0.75em; margin-top: 5px; margin-bottom: 0; line-height: 1.5; }

        /* 🔥 입력창(Input) 라벨 텍스트 하얗고 진하게 강제 변경 (흐림/투명도 제거) */
        div[data-testid="stNumberInput"] label p, 
        div[data-testid="stDateInput"] label p {
            color: #ffffff !important;
            font-weight: 900 !important;
            font-size: 0.95em !important;
            opacity: 1.0 !important;
            visibility: visible !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# [블록 3] 데이터 로딩 (구글 시트 연동 + 엑셀 연동)
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

@st.cache_data
def load_price_data():
    price_hierarchy = {}
    try:
        df_p = pd.read_excel("디에트르 그랑루체 이자계산기.xlsx", sheet_name="Sheet2", header=None, dtype=str)
        for _, row in df_p.iterrows():
            try:
                dong_val = str(row.iloc[1]).replace(".0", "").strip()
                ho_val = str(row.iloc[2]).replace(".0", "").strip()
                price_str = str(row.iloc[4]).replace(",", "").replace(".0", "").strip()
                
                if dong_val.isdigit() and ho_val.isdigit() and price_str.isdigit():
                    price_int = int(price_str)
                    
                    if price_int > 1000000:
                        dong_str = f"{int(dong_val)}동"
                        ho_str = f"{int(ho_val):04d}호"
                        
                        if dong_str not in price_hierarchy:
                            price_hierarchy[dong_str] = {}
                        price_hierarchy[dong_str][ho_str] = price_int
            except: continue 
    except Exception as e:
        pass 
    return price_hierarchy

kakao_dict, cafe_set, df_layout, type_dict = load_data()
price_data = load_price_data()
if df_layout.empty: st.stop()

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
# [블록 4] 실시간 경제 API 연동 봇
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
        LAWD_CD = "26440"
        now = datetime.now()
        raw_trades = []
        
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
                        price_str = item.find('dealAmount').text.strip() if item.find('dealAmount') is not None else "0"
                        area = item.find('excluUseAr').text.strip() if item.find('excluUseAr') is not None else "0"
                        deal_d = item.find('dealDay').text.strip() if item.find('dealDay') is not None else ""
                        floor = item.find('floor').text.strip() if item.find('floor') is not None else ""
                        apt_dong = item.find('aptDong').text.strip() if item.find('aptDong') is not None else ""
                        
                        date_str = f"{deal_ym[2:4]}.{deal_ym[4:6]}.{deal_d.zfill(2)}"
                        dong_str = f"{apt_dong}동 " if apt_dong and apt_dong != " " else ""
                        detail_str = f"{dong_str}{floor}층" if floor else dong_str
                        
                        try: price_int = int(price_str.replace(",", "").strip())
                        except: price_int = 0
                            
                        raw_trades.append({"apt": apt, "area": float(area), "price_int": price_int, "date": date_str, "detail": detail_str})

        raw_trades.sort(key=lambda x: x['date'])
        
        prev_prices = {}
        for t in raw_trades:
            key = f"{t['apt']}_{t['area']}"
            curr_price = t['price_int']
            
            if key in prev_prices:
                diff = curr_price - prev_prices[key]
                if diff > 0:
                    t['delta_str'] = f"▲ {format_korean_money(str(diff))}"
                    t['delta_color'] = "delta-up"
                elif diff < 0:
                    t['delta_str'] = f"▼ {format_korean_money(str(abs(diff)))}"
                    t['delta_color'] = "delta-down"
                else:
                    t['delta_str'] = "- 보합"
                    t['delta_color'] = "delta-new"
            else:
                t['delta_str'] = "신규"
                t['delta_color'] = "delta-new"
                
            prev_prices[key] = curr_price
            t['price_formatted'] = format_korean_money(str(curr_price))

        raw_trades.sort(key=lambda x: x['date'], reverse=True)
        return raw_trades
    except Exception as e:
        return []

@st.cache_data(ttl=43200)
def get_interest_rate_api():
    try:
        bok_key = st.secrets["api_keys"]["bok_key"]
        url = f"http://ecos.bok.or.kr/api/KeyStatisticList/{bok_key}/xml/kr/1/100"
        req = urllib.request.Request(url)
        res = urllib.request.urlopen(req, timeout=5)
        root = ET.fromstring(res.read())
        
        base_rate = "3.50"
        for row in root.findall('.//row'):
            if "기준금리" in row.find('KEYSTAT_NAME').text:
                base_rate = row.find('DATA_VALUE').text
                break
                
        base_f = float(base_rate)
        
        rates = {
            "base": f"{base_f:.2f}%",
            "tier1": f"{base_f + 0.35:.2f}% ~ {base_f + 0.85:.2f}%",
            "tier2": f"{base_f + 1.50:.2f}% ~ {base_f + 2.50:.2f}%",
            "didim": "2.15% ~ 3.55%",
            "baby": "1.60% ~ 3.30%",
            "bogeum": "4.20% ~ 4.50%"
        }
        return rates
    except:
        return {
            "base": "3.50%", "tier1": "3.85% ~ 4.25%", "tier2": "4.95% ~ 5.80%", 
            "didim": "2.15% ~ 3.55%", "baby": "1.60% ~ 3.30%", "bogeum": "4.20% ~ 4.50%"
        }

@st.cache_data(ttl=3600)
def get_oil_price_api():
    try:
        opinet_key = st.secrets["api_keys"]["opinet_key"]
        busan_cd = "08"
        try:
            req_find = urllib.request.Request(f"http://www.opinet.co.kr/api/avgSidoPrice.do?out=xml&prodcd=B027&code={opinet_key}")
            res_find = urllib.request.urlopen(req_find, timeout=5)
            root_find = ET.fromstring(res_find.read())
            for row in root_find.findall('.//OIL'):
                if "부산" in row.find('SIDONM').text:
                    busan_cd = row.find('SIDOCD').text
                    break
        except: pass

        url_sido = f"http://www.opinet.co.kr/api/avgSidoPrice.do?out=xml&sido={busan_cd}&code={opinet_key}"
        req_sido = urllib.request.Request(url_sido)
        res_sido = urllib.request.urlopen(req_sido, timeout=5)
        root_sido = ET.fromstring(res_sido.read())
        
        gas, diesel, lpg = "0원", "0원", "0원"
        gas_delta = diesel_delta = lpg_delta = ("-", "delta-new")
        
        for row in root_sido.findall('.//OIL'):
            prodcd = row.find('PRODCD').text
            price = float(row.find('PRICE').text)
            diff = float(row.find('DIFF').text)
            
            diff_str = f"▲{diff:,.0f}" if diff > 0 else (f"▼{abs(diff):,.0f}" if diff < 0 else "- 보합")
            color = "delta-up" if diff > 0 else ("delta-down" if diff < 0 else "delta-new")
            
            if prodcd == "B027": gas, gas_delta = f"{price:,.0f}원", (diff_str, color)
            elif prodcd == "D047": diesel, diesel_delta = f"{price:,.0f}원", (diff_str, color)
            elif prodcd == "K015": lpg, lpg_delta = f"{price:,.0f}원", (diff_str, color)

        districts = {}
        for prod_name, prod_cd in [("gas", "B027"), ("diesel", "D047")]:
            url_sigun = f"http://www.opinet.co.kr/api/avgSigunPrice.do?out=xml&sido={busan_cd}&prodcd={prod_cd}&code={opinet_key}"
            req_sigun = urllib.request.Request(url_sigun)
            res_sigun = urllib.request.urlopen(req_sigun, timeout=5)
            root_sigun = ET.fromstring(res_sigun.read())
            
            for row in root_sigun.findall('.//OIL'):
                sigun_nm = row.find('SIGUNNM').text
                price = float(row.find('PRICE').text)
                diff = float(row.find('DIFF').text)
                
                diff_str = f"▲{diff:,.0f}" if diff > 0 else (f"▼{abs(diff):,.0f}" if diff < 0 else "- 보합")
                color = "delta-up" if diff > 0 else ("delta-down" if diff < 0 else "delta-new")
                
                if sigun_nm not in districts: districts[sigun_nm] = {"name": sigun_nm}
                districts[sigun_nm][prod_name] = {"price_val": price, "price_str": f"{price:,.0f}", "diff_str": diff_str, "color": color}
        
        dist_list = list(districts.values())
        dist_list.sort(key=lambda x: x.get('gas', {}).get('price_val', 999999))
        return {"busan_avg": {"gas": gas, "gas_d": gas_delta, "diesel": diesel, "diesel_d": diesel_delta, "lpg": lpg, "lpg_d": lpg_delta}, "districts": dist_list}
    except Exception as e:
        return None

@st.cache_data(ttl=3600)
def get_global_stocks_api():
    def fetch_yahoo(name, sym, multiplier=1):
        try:
            url = f"https://query2.finance.yahoo.com/v8/finance/chart/{sym}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            res = urllib.request.urlopen(req, timeout=5)
            data = json.loads(res.read())
            meta = data['chart']['result'][0]['meta']
            
            price = meta['regularMarketPrice'] * multiplier
            prev_close = meta['chartPreviousClose'] * multiplier
            diff = price - prev_close
            
            diff_str = f"▲ {diff:,.2f}" if diff > 0 else (f"▼ {abs(diff):,.2f}" if diff < 0 else "- 보합")
            color = "delta-up" if diff > 0 else ("delta-down" if diff < 0 else "delta-new")
            return f"<tr><th>{name}</th><td>{price:,.2f} <span class='{color}' style='margin-left:4px; font-weight:800;'>{diff_str}</span></td></tr>"
        except: return f"<tr><th>{name}</th><td>조회지연 <span class='delta-new' style='margin-left:4px; font-weight:800;'>-</span></td></tr>"

    html = "<table class='econ-table'>"
    for name, sym in [("🇺🇸 나스닥", "^IXIC"), ("🇺🇸 S&P 500", "^GSPC"), ("🇰🇷 코스피", "^KS11"), ("🇰🇷 코스닥", "^KQ11")]: html += fetch_yahoo(name, sym)
    
    html += "<tr style='background-color:rgba(255,255,255,0.05);'><th colspan='2' style='color:#D4AF37; text-align:center; padding:8px 0; border-top:1px solid #333; font-size:0.95em;'>💱 주요 국가 환율</th></tr>"
    for name, sym, mult in [("💵 미국 (USD/KRW)", "KRW=X", 1), ("💶 유럽 (EUR/KRW)", "EURKRW=X", 1), ("🇯🇵 일본 (100 JPY/KRW)", "JPYKRW=X", 100)]: html += fetch_yahoo(name, sym, mult)
        
    html += "<tr style='background-color:rgba(255,255,255,0.05);'><th colspan='2' style='color:#03C75A; text-align:center; padding:8px 0; border-top:1px solid #333; font-size:0.95em;'>✈️ 10대 해외여행지 환율</th></tr>"
    tourist_dests = [
        ("🇨🇳 중국 (CNY/KRW)", "CNYKRW=X", 1), ("🇹🇼 대만 (TWD/KRW)", "TWDKRW=X", 1), ("🇻🇳 베트남 (100 VND/KRW)", "VNDKRW=X", 100), ("🇹🇭 태국 (THB/KRW)", "THBKRW=X", 1),
        ("🇵🇭 필리핀 (PHP/KRW)", "PHPKRW=X", 1), ("🇸🇬 싱가포르 (SGD/KRW)", "SGDKRW=X", 1), ("🇭🇰 홍콩 (HKD/KRW)", "HKDKRW=X", 1), ("🇲🇾 말레이시아 (MYR/KRW)", "MYRKRW=X", 1),
        ("🇮🇩 인니 (100 IDR/KRW)", "IDRKRW=X", 100), ("🇦🇺 호주 (AUD/KRW)", "AUDKRW=X", 1)
    ]
    for name, sym, mult in tourist_dests: html += fetch_yahoo(name, sym, mult)
    html += "</table>"
    return html

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
# 🚨 메인 상단 타이틀 영역 (이미지 로고 적용)
# ==========================================
try:
    title_logo = Image.open("detre_logo.png")
    st.markdown("<div style='text-align:center; margin-bottom:15px;'>", unsafe_allow_html=True)
    st.image(title_logo, use_column_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
except Exception:
    st.markdown("<div class='premium-title'>Detre Granluce</div>", unsafe_allow_html=True)

st.markdown("""
<div style='display: flex; flex-direction: column; gap: 4px; margin-bottom: 15px;'>
    <a href="https://form.jotform.com/240628865713463" target="_blank" class='official-btn btn-naver'>📝 그랑루체 공식카페 (위임동의서 제출)</a>
    <a href="https://open.kakao.com/o/ggAiqg4f" target="_blank" class='official-btn btn-kakao-official'>💬 그랑루체 공식 카카오톡 입장</a>
</div>
<div class='notice-text'>🚨 현황판에 미표기된 세대는 회장님 및 임원진에게 요청부탁드립니다.</div>
""", unsafe_allow_html=True)

# ==========================================
# [블록 5] 종합 포털 탭(Tab) 메뉴 
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏢 입주현황", "💰 이자계산기", "📊 입주민 전용정보", "🔮 오늘의 운세", "📰 관련뉴스"])

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
# [탭 2] 🚨 아버님표 이자계산기 시뮬레이션
# ------------------------------------------
with tab2:
    st.markdown("<div class='calc-premium-title'>💰 이자계산기</div>", unsafe_allow_html=True)

    if not price_data:
        st.warning("데이터가 없습니다. 엑셀 파일을 확인해주세요.")
    else:
        st.markdown("#### 1️⃣ 세대 정보 및 계약금 선택")
        col_d, col_h = st.columns(2)
        with col_d:
            selected_dong = st.selectbox("🏢 동 선택", options=sorted(list(price_data.keys())), index=None)
        with col_h:
            if selected_dong and selected_dong in price_data:
                selected_ho = st.selectbox("🚪 호수 선택", options=sorted(list(price_data[selected_dong].keys())), index=None)
            else:
                selected_ho = st.selectbox("🚪 호수 선택", options=["동 선택 필요"], disabled=True)

        if selected_dong and selected_ho and selected_ho in price_data.get(selected_dong, {}):
            total_price = price_data[selected_dong][selected_ho]
            
            # 🔥 계약금 5%, 10% 모바일 꽉 차게 한 줄로 정렬 및 타이틀 분리 고정
            st.markdown("<p style='font-size:0.95em; font-weight:900; color:#D4AF37; margin-bottom:-10px; margin-top:10px;'>계약금 납부방법 선택</p>", unsafe_allow_html=True)
            contract_type = st.radio("계약금 납부방법 선택", ["5%", "10%"], horizontal=True, label_visibility="collapsed")
            
            contract_total_amt = total_price * 0.1 
            installment_total_amt = total_price * 0.6
            installment_amt = total_price * 0.1 
            balance_amt = total_price * 0.3
            
            unpaid_contract_amt = total_price * 0.05 if "5%" in contract_type else 0
            paid_contract_amt = contract_total_amt - unpaid_contract_amt

            # 🔥 표(Table) 모바일 폰트 더 작게, 강제 한 줄 유지(nowrap)로 '원' 자 떨어짐 완벽 방지
            top_dashboard = f"""
            <div class='table-responsive'>
                <table style='width:100%; border-collapse: collapse; text-align:center; background:#1c1c1e; border-radius:10px; border:1px solid #444; margin-top: 10px; margin-bottom: 25px; table-layout: auto;'>
                    <tr style='color:#D4AF37; font-size:clamp(0.65em, 2vw, 0.85em); font-weight:800; border-bottom:1px solid #333;'>
                        <td style='padding:8px 1px;'>계약금 10%</td>
                        <td style='padding:8px 1px; border-left:1px solid #333;'>중도금 60%</td>
                        <td style='padding:8px 1px; border-left:1px solid #333;'>잔금 30%</td>
                        <td style='padding:8px 1px; border-left:1px solid #333;'>총 분양가</td>
                    </tr>
                    <tr style='color:#ffffff; font-size:clamp(0.65em, 2.2vw, 1.0em); font-weight:900; white-space: nowrap !important; word-break: keep-all;'>
                        <td style='padding:10px 1px; letter-spacing:-0.5px;'>{int(contract_total_amt):,}원</td>
                        <td style='padding:10px 1px; border-left:1px solid #333; letter-spacing:-0.5px;'>{int(installment_total_amt):,}원</td>
                        <td style='padding:10px 1px; border-left:1px solid #333; letter-spacing:-0.5px;'>{int(balance_amt):,}원</td>
                        <td style='padding:10px 1px; border-left:1px solid #333; color:#fbbf24; letter-spacing:-0.5px;'>{total_price:,}원</td>
                    </tr>
                    <tr style='font-size:clamp(0.6em, 2vw, 0.75em);'>
                        <td style='padding:8px 2px; vertical-align:top;'>
                            <div style='background:rgba(0,0,0,0.3); padding:6px; border-radius:6px; line-height:1.4;'>
                                <span style='color:#34d399;'>기납부:<br>{int(paid_contract_amt):,}원</span><br>
                                <span style='color:#f87171; font-weight:800;'>미납액:<br>{int(unpaid_contract_amt):,}원</span>
                            </div>
                        </td>
                        <td style='padding:8px 2px; border-left:1px solid #333; vertical-align:top;'>
                            <div style='color:#bbb; padding-top:6px;'>회당(10%):<br>{int(installment_amt):,}원</div>
                        </td>
                        <td style='padding:8px 2px; border-left:1px solid #333;'></td>
                        <td style='padding:8px 2px; border-left:1px solid #333;'></td>
                    </tr>
                </table>
            </div>"""
            st.markdown(top_dashboard, unsafe_allow_html=True)

            # ==========================================
            # 4. 중도금 이자 계산 & 자납 설정 
            # ==========================================
            st.markdown("#### 2️⃣ 중도금 대출 이자 및 자납(직접납부) 설정")
            
            slider_rate = st.slider("4~6회차 예상 금리 (%)", 2.00, 6.00, 3.88, 0.01)

            dates = [date(2024, 5, 20), date(2024, 12, 20), date(2025, 7, 20), date(2026, 3, 20), date(2026, 7, 20), date(2026, 11, 20)]
            end_date = date(2027, 5, 31)
            rates = [4.85, 4.68, 3.88, slider_rate, slider_rate, slider_rate]
            status_tags = ["hl-fixed", "hl-fixed", "hl-fixed", "hl-var", "hl-var", "hl-var"]
            status_texts = ["확정", "확정", "확정", "예상", "예상", "예상"]

            self_pays = []
            total_self_pay_amt = 0 

            with st.expander("💸 자납(직접 납부) 세대 상세 설정 (클릭하여 열기)"):
                st.markdown("<p style='font-size:0.85em; color:#bbb; margin-bottom:15px;'>해당 회차에 직접 납부하신 금액이 있다면 아래에 적어주세요. (없는 회차는 0원 그대로 두시면 됩니다.)</p>", unsafe_allow_html=True)
                
                for i in range(6):
                    c1, c2 = st.columns([1.5, 1.5])
                    with c1:
                        sp_amt = st.number_input(f"{i+1}회차 자납 금액(원)", min_value=0, max_value=int(installment_amt), value=0, step=1000000, format="%d", key=f"amt_{i}")
                        if sp_amt > 0:
                            st.markdown(f"<div style='text-align: right; color: #0A84FF; font-weight: 800; font-size: 0.85em; margin-top: -10px; margin-bottom: 10px;'>입력액: {int(sp_amt):,} 원</div>", unsafe_allow_html=True)
                    with c2:
                        sp_date = st.date_input(f"{i+1}회차 입금일자", value=dates[i], key=f"date_{i}", format="YYYY/MM/DD")
                    
                    is_self = sp_amt > 0
                    amt_to_apply = sp_amt if is_self else 0
                    total_self_pay_amt += amt_to_apply
                    self_pays.append({'is_self': is_self, 'amt': amt_to_apply, 'date': sp_date})
                    st.markdown("<hr style='margin: 10px 0; border-color: #333;'>", unsafe_allow_html=True)

            total_interest = 0
            html_table = "<div class='table-responsive'><table class='calc-table'><tr><th>회차</th><th>실행일</th><th>금리</th><th style='text-align:right !important; padding-right:12px !important;'>발생 이자액</th></tr>"

            for i in range(6):
                exec_date = dates[i]
                rate = rates[i]
                sp = self_pays[i]
                
                interest = 0
                if sp['is_self'] and sp['amt'] > 0:
                    sp_date = sp['date']
                    if sp_date <= exec_date: 
                        loan_amt = installment_amt - sp['amt']
                        days = (end_date - exec_date).days
                        interest = loan_amt * (rate / 100) * (days / 365)
                    elif sp_date >= end_date: 
                        loan_amt = installment_amt
                        days = (end_date - exec_date).days
                        interest = loan_amt * (rate / 100) * (days / 365)
                    else: 
                        days1 = (sp_date - exec_date).days
                        int1 = installment_amt * (rate / 100) * (days1 / 365)
                        loan_amt2 = installment_amt - sp['amt']
                        days2 = (end_date - sp_date).days
                        int2 = loan_amt2 * (rate / 100) * (days2 / 365)
                        interest = int1 + int2
                else:
                    loan_amt = installment_amt
                    days = (end_date - exec_date).days
                    interest = loan_amt * (rate / 100) * (days / 365)
                    
                total_interest += interest
                sp_mark = "<br><span style='color:#34d399; font-size:0.75em;'>(자납반영)</span>" if sp['is_self'] and sp['amt']>0 else ""
                
                html_table += f"<tr><td>{i+1}회차{sp_mark}<br><span style='font-size:0.7em; color:#888;'>({days}일)</span></td><td>{dates[i].strftime('%Y.%m.%d')}</td><td><span class='{status_tags[i]}'>{rates[i]:.2f}% ({status_texts[i]})</span></td><td style='text-align:right !important; padding-right:12px !important; color:#ffffff !important; font-weight:800;'>{int(interest):,} 원</td></tr>"

            html_table += "</table></div>"

            int_dashboard = f"<div class='calc-box'><div class='calc-title'>입주 시점(27.05.31) 총 중도금 이자 누적액</div><div class='calc-total'>{int(total_interest):,} 원</div>{html_table}</div>"
            st.markdown(int_dashboard, unsafe_allow_html=True)

            total_loan_balance = installment_total_amt - total_self_pay_amt

            # ==========================================
            # 5. 대환대출(주담대) 월 납입액 시뮬레이터 (🔥 제목 마크다운 오류 수정 및 폰트 통일)
            # ==========================================
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            st.markdown("#### 3️⃣ 입주 시 대환대출(주담대) 월 납입액 예상")
            st.markdown("<p style='font-size:0.85em; color:gray;'>중도금 대출 잔액을 일반 주담대로 대환 시 매월 납입액입니다.</p>", unsafe_allow_html=True)
            
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                repay_type = st.selectbox("상환 방식", ["원리금균등상환", "원금균등상환", "만기일시상환(이자만)"])
                loan_years = st.slider("대출 기간 (년)", 10, 50, 30, 5)
            with col_l2:
                bank_type = st.selectbox("대출 금융권 (금리 기준)", ["1금융권 주담대 (약 4.0%)", "2금융권 주담대 (약 5.2%)", "정부기금/디딤돌 (약 2.5%)", "직접 입력"])
                if "1금융권" in bank_type: default_b_rate = 4.0
                elif "2금융권" in bank_type: default_b_rate = 5.2
                elif "정부기금" in bank_type: default_b_rate = 2.5
                else: default_b_rate = 4.0
                b_rate = st.number_input("적용 금리 (%)", value=default_b_rate, step=0.1, disabled=(bank_type != "직접 입력"))
                
            n_months = loan_years * 12
            S = total_loan_balance
            R = (b_rate / 100) / 12

            if S > 0:
                first_month_interest = S * R
                
                if repay_type == "원리금균등상환":
                    monthly_pay = S * R * ((1 + R)**n_months) / (((1 + R)**n_months) - 1) if R > 0 else S / n_months
                    first_month_principal = monthly_pay - first_month_interest
                    pay_text = f"매월 <b style='color:#fbbf24; font-size:1.2em;'>{int(monthly_pay):,}</b> 원"
                    pay_sub = f"(첫 달 기준: 원금 {int(first_month_principal):,}원 + 이자 {int(first_month_interest):,}원)"
                    
                elif repay_type == "원금균등상환":
                    monthly_principal = S / n_months
                    first_month_pay = monthly_principal + first_month_interest
                    pay_text = f"첫 달 <b style='color:#fbbf24; font-size:1.2em;'>{int(first_month_pay):,}</b> 원"
                    pay_sub = f"(매월 감소: 원금 {int(monthly_principal):,}원 + 첫 달 이자 {int(first_month_interest):,}원)"
                    
                else: 
                    monthly_pay = S * R
                    pay_text = f"매월 <b style='color:#fbbf24; font-size:1.2em;'>{int(monthly_pay):,}</b> 원"
                    pay_sub = f"(만기 전액 상환: 원금 0원 + 이자 {int(monthly_pay):,}원)"
            else:
                pay_text = "<b style='color:#34d399;'>중도금 대출 잔액이 없습니다 (전액 자납)</b>"
                pay_sub = ""

            loan_dashboard = f"<div style='background:#1c1c1e; border-left: 4px solid #D4AF37; padding: 15px; border-radius: 4px; margin-top: 10px;'><div style='font-size:0.9em; color:#ddd;'>대환대출 원금 (자납 제외 중도금 잔액): <b style='color:#fff;'>{int(S):,} 원</b></div><div style='font-size:1.1em; color:#fff; margin-top:8px;'>예상 납입액: {pay_text}</div><div style='font-size:0.85em; color:#aaa; margin-top:5px;'>{pay_sub}</div></div>"
            st.markdown(loan_dashboard, unsafe_allow_html=True)

            # ==========================================
            # 6. 최종 총 비용 요약 전광판
            # ==========================================
            actual_price = total_price + total_interest
            move_in_funds = unpaid_contract_amt + balance_amt + total_interest
            
            final_dashboard = f"<div class='summary-box'><div class='summary-title'>🎉 입주 시나리오 최종 요약</div><div class='summary-row'><div class='summary-label'>실질적 분양가<br><span style='font-size:0.8em; font-weight:400;'>(분양가 + 중도금 누적 이자액)</span></div><div class='summary-val'>{int(actual_price):,} 원</div></div><div class='summary-row'><div class='summary-label'>잔금 30%<br><span style='font-size:0.8em; font-weight:400;'>(분양가의 30% / 입주 지정 시 납부)</span></div><div class='summary-val'>{int(balance_amt):,} 원</div></div><div class='summary-row' style='margin-top: 15px; border-top: 1px dashed rgba(255,255,255,0.3); padding-top: 15px;'><div class='summary-label' style='color:#93c5fd !important;'>순수 입주 필요 현금<br><span style='font-size:0.8em; font-weight:400;'>(미납 계약금 + 잔금 30% + 중도금 이자)</span></div><div class='summary-val-highlight'>{int(move_in_funds):,} 원</div></div></div><div class='disclaimer-box'><b style='color:#f87171; font-size:0.85em;'>🚨 [필독] 제외 사항</b><p class='disclaimer-text'>※ 본 계산결과는 발코니 확장비, 유상옵션, 취득세 등 기타 제반 비용이 <b>제외된 금액</b>입니다.<br>※ 잔금 대출(LTV, DSR 등) 및 개인 신용도에 따른 기타 변수는 배제된 <b>보편적 시뮬레이션</b>이므로, 정확한 잔금 대출 및 이율에 대해서는 입주 지정일 전 <b>반드시 개별적인 은행 상담 및 확인</b>이 필요합니다.</p></div>"
            st.markdown(final_dashboard, unsafe_allow_html=True)

# ------------------------------------------
# [탭 3] 핵심비밀정보 (심리전 UX 탑재)
# ------------------------------------------
with tab3:
    st.markdown("<h3 style='text-align:center; color:#D4AF37; font-weight:900; margin-top:0px; margin-bottom:2px; letter-spacing:-1px;'>📊 입주민 전용정보</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#aaa; font-size:0.75em; margin-bottom:10px;'>※ <span style='color:#03C75A;'>Advanced Data Pipeline</span> 기술로 수집된 실시간 지표</p>", unsafe_allow_html=True)

    apt_trades = get_real_estate_api()
    rates = get_interest_rate_api()
    oil_data = get_oil_price_api()
    global_html = get_global_stocks_api()

    now = datetime.now()
    today_str = now.strftime("%Y.%m.%d")
    current_time_str = now.strftime("%Y.%m.%d %H:%M")
    
    badge_real_estate = f"<div style='text-align:right; font-size:0.65em; color:#8e8e93; margin-bottom:8px;'>🔄 {today_str} 07:00 정기 업데이트</div>"
    badge_rates = f"<div style='text-align:right; font-size:0.65em; color:#8e8e93; margin-bottom:8px;'>🔄 한국은행 최신 고시 기준</div>"
    
    oil_hour = "14:00" if now.hour >= 14 else "08:00"
    badge_oil = f"<div style='text-align:right; font-size:0.65em; color:#8e8e93; margin-bottom:8px;'>🔄 {today_str} {oil_hour} 갱신 완료</div>"
    
    badge_global = f"<div style='text-align:right; font-size:0.65em; color:#03C75A; margin-bottom:8px; font-weight:800;'>🔄 {current_time_str} 실시간 동기화</div>"

    # 🔥 1. 실거래가 아코디언 (기본 닫힘)
    with st.expander("🏢 강서구(명지·강동) 최근 실거래가", expanded=False):
        st.markdown(badge_real_estate, unsafe_allow_html=True)
        search_kw = st.text_input("단지명 검색", placeholder="🔍 단지명을 입력하세요 (예: 호반, 더샵)", label_visibility="collapsed")
        
        filtered_trades = apt_trades
        if search_kw:
            clean_kw = search_kw.replace(" ", "")
            filtered_trades = [t for t in apt_trades if clean_kw in t['apt'].replace(" ", "")]

        html_econ = "<div class='trade-scroll-box'>"
        if filtered_trades:
            for t in filtered_trades:
                html_econ += f"<div class='trade-row'><div class='trade-info'><div class='trade-apt'>{t['apt']} <span class='trade-area'>({t['area']:.0f}㎡)</span></div><div class='trade-detail'>📅 {t['date']} | 🏢 {t['detail']}</div></div><div class='trade-price-box'><div class='trade-price'>{t['price_formatted']}</div><div class='trade-delta {t['delta_color']}'>{t['delta_str']}</div></div></div>"
        else:
            if search_kw: html_econ += f"<div style='text-align:center; color:#8e8e93; padding:15px; font-size:0.85em;'>'{search_kw}' 단지의 최근 거래 내역이 없습니다.</div>"
            else: html_econ += "<div style='text-align:center; color:#8e8e93; padding:15px; font-size:0.85em;'>최근 거래 신고 내역이 없거나 점검중입니다.</div>"
        html_econ += "</div>"
        st.markdown(html_econ, unsafe_allow_html=True)

    # 🔥 2. 주택담보대출 금리 아코디언 (기본 닫힘)
    with st.expander("🏦 금융권 & 기금 정책자금 대출 금리", expanded=False):
        st.markdown(badge_rates, unsafe_allow_html=True)
        html_rate = "<table class='econ-table'>"
        html_rate += f"<tr style='background-color:rgba(255,255,255,0.05);'><th colspan='2' style='color:#D4AF37; text-align:center; font-size:1.0em; padding:10px 0;'>🇰🇷 한국은행 기준금리: {rates['base']}</th></tr>"
        html_rate += f"<tr><th>🏢 1금융권 (시중은행)</th><td>{rates['tier1']}</td></tr>"
        html_rate += f"<tr><th>🏦 2금융권 (저축·새마을)</th><td>{rates['tier2']}</td></tr>"
        html_rate += "<tr style='background-color:rgba(255,255,255,0.05);'><th colspan='2' style='color:#03C75A; text-align:center; padding:8px 0; border-top:1px solid #333;'>🏛️ 국토부·주택도시기금 정책자금 (고정)</th></tr>"
        html_rate += f"<tr><th>👶 신생아 특례 (출산가구)</th><td style='color:#FF3B30;'>{rates['baby']}</td></tr>"
        html_rate += f"<tr><th>🏠 내집마련 디딤돌</th><td>{rates['didim']}</td></tr>"
        html_rate += f"<tr><th>🛡️ 특례 보금자리론</th><td>{rates['bogeum']}</td></tr>"
        html_rate += "</table>"
        st.markdown(html_rate, unsafe_allow_html=True)

    # 🔥 3. 유가 정보 아코디언 (기본 닫힘)
    with st.expander("⛽ 부산 평균 및 구별 유가 랭킹 (오피넷)", expanded=False):
        st.markdown(badge_oil, unsafe_allow_html=True)
        if oil_data:
            b_avg = oil_data["busan_avg"]
            html_oil = "<div style='font-size:0.85em; color:#D4AF37; font-weight:800; margin-top:5px; margin-bottom:5px; padding-left:4px;'>🔵 부산 전체 평균</div>"
            html_oil += "<table class='econ-table' style='margin-bottom:15px;'>"
            html_oil += f"<tr><th>휘발유</th><td>{b_avg['gas']} <span class='{b_avg['gas_d'][1]}' style='margin-left:4px; font-weight:800;'>{b_avg['gas_d'][0]}</span></td></tr>"
            html_oil += f"<tr><th>경유</th><td>{b_avg['diesel']} <span class='{b_avg['diesel_d'][1]}' style='margin-left:4px; font-weight:800;'>{b_avg['diesel_d'][0]}</span></td></tr>"
            html_oil += f"<tr><th>LPG</th><td>{b_avg['lpg']} <span class='{b_avg['lpg_d'][1]}' style='margin-left:4px; font-weight:800;'>{b_avg['lpg_d'][0]}</span></td></tr>"
            html_oil += "</table>"
            
            html_oil += "<div style='font-size:0.85em; color:#03C75A; font-weight:800; margin-bottom:5px; padding-left:4px;'>🟢 부산 구/군별 최저가 랭킹 (휘발유 기준)</div>"
            html_oil += "<div class='trade-scroll-box' style='max-height: 250px;'>"
            html_oil += "<table class='econ-table'>"
            html_oil += "<tr><th style='width:35%; text-align:left;'>지역 (순위)</th><th style='text-align:right;'>휘발유</th><th style='text-align:right;'>경유</th></tr>"
            
            for idx, d in enumerate(oil_data["districts"]):
                rank = f"{idx+1}위"
                g_info = d.get('gas', {})
                d_info = d.get('diesel', {})
                
                html_oil += f"<tr><th style='text-align:left;'>{rank} {d['name']}</th>"
                html_oil += f"<td>{g_info.get('price_str', '-')}원 <br><span class='{g_info.get('color', 'delta-new')}' style='font-size:0.85em;'>{g_info.get('diff_str', '')}</span></td>"
                html_oil += f"<td>{d_info.get('price_str', '-')}원 <br><span class='{d_info.get('color', 'delta-new')}' style='font-size:0.85em;'>{d_info.get('diff_str', '')}</span></td></tr>"
                
            html_oil += "</table></div>"
            st.markdown(html_oil, unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align:center; color:#8e8e93; padding:15px; font-size:0.85em;'>유가 데이터 점검중입니다.</div>", unsafe_allow_html=True)

    # 🔥 4. 글로벌 증시 및 환율 현황 (기본 닫힘)
    with st.expander("🌐 글로벌 증시 & 환율 현황", expanded=False):
        st.markdown(badge_global, unsafe_allow_html=True)
        st.markdown(global_html, unsafe_allow_html=True)

    # ==========================================
    # 🔥 기대감을 증폭시키는 킬러 기능 티저(Teaser) 영역
    # ==========================================

    # 🔥 5. 조달청 관급공사 티저
    with st.expander("🚀 우리 동네 개발/호재 정보망 (준비중 ⏳)", expanded=False):
        st.markdown("""
        <div style='text-align:center; padding: 25px 15px; background: rgba(255, 255, 255, 0.03); border-radius: 8px; border: 1px dashed #0A84FF; margin-top: 5px;'>
            <h4 style='color:#0A84FF; margin-bottom:12px; font-weight:900;'>🚧 조달청(G2B) 실시간 연동 준비 중! 🚧</h4>
            <p style='color:#d1d1d6; font-size:0.9em; line-height:1.6; margin-bottom:20px; word-break: keep-all;'>
                우리 지역 개발과 관련된 <b style='color:#FF3B30;'>국가 조달청 관급공사 공고</b>들을<br>
                실시간으로 연동하여 직접 눈으로 확인하실 수 있게 시스템을 구축하고 있습니다.
            </p>
            <p style='color:#8e8e93; font-size:0.85em; line-height:1.5; margin-bottom:15px; word-break: keep-all;'>
                인터넷 검색이 번거로우신 분들도 이제 걱정 마십시오!<br>
                그간 <b>네이버카페나 단톡방을 다니며 발품 팔아 얻었던 귀한 정보들</b>(도로 개설, 공원 조성, 정거장 신설 등)을<br>
                이제 이 어플 하나로 <b style='color:#03C75A;'>가장 빠르고 편안하게 획득</b>하실 수 있습니다.
            </p>
            <div style='display:inline-block; background:#1C1C1E; border:1px solid #333; padding:8px 15px; border-radius:20px;'>
                <span style='color:#D4AF37; font-size:0.8em; font-weight:800;'>💡 서버 연동 테스트 중입니다. 런칭을 기대해 주세요!</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 🔥 6. 농수산/공산품 물가 티저
    with st.expander("🛒 주요 농수산품 시세 및 물가 검색기 (준비중 ⏳)", expanded=False):
        html_coming_soon = """
        <div style='text-align:center; padding: 25px 15px; background: rgba(255, 255, 255, 0.03); border-radius: 8px; border: 1px dashed #D4AF37; margin-top: 5px;'>
            <h4 style='color:#D4AF37; margin-bottom:12px; font-weight:900;'>🚧 향후 정식 오픈 예정! 🚧</h4>
            <p style='color:#d1d1d6; font-size:0.9em; line-height:1.6; margin-bottom:20px; word-break: keep-all;'>
                <b style='color:#FF3B30;'>주요 농수산품</b>의 도/소매 시세 변동을 실시간 전광판으로 보여드리고,<br>
                일반 <b style='color:#0A84FF;'>대형마트 및 편의점 공산품</b>은 검색을 통해<br>
                평균 판매가를 즉시 찾아볼 수 있는 스마트 시스템입니다!
            </p>
            <p style='color:#8e8e93; font-size:0.8em; line-height:1.4; margin-bottom:15px; word-break: keep-all;'>
                주부님들의 알뜰한 소비를 완벽하게 도와드릴 예정입니다.<br>
                현재 안정적인 시스템 연동 개발에 시간이 다소 소요되고 있으니 조금만 더 기다려주세요!
            </p>
            <div style='display:inline-block; background:#1C1C1E; border:1px solid #333; padding:8px 15px; border-radius:20px;'>
                <span style='color:#03C75A; font-size:0.8em; font-weight:800;'>💡 Advanced Data Pipeline 연동 중</span>
            </div>
        </div>
        """
        st.markdown(html_coming_soon, unsafe_allow_html=True)

# ------------------------------------------
# [탭 4] 오늘의 운세 (🚨 사주 버튼 이동 및 디자인 강화)
# ------------------------------------------
with tab4:
    st.markdown("<h4 style='text-align:center; color:#D4AF37; margin-top:10px;'>🔮 팡도사의 동·호수 맞춤 신점</h4>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#aaa; font-size:0.75em;'>개인정보 입력 없이, 귀하의 사주 명조를 심층 분석하여 점쳐드립니다.</p>", unsafe_allow_html=True)
    
    col_d, col_h = st.columns(2)
    with col_d: f_dong = st.selectbox("입주 예정 동", all_dongs_raw, key="f_dong", label_visibility="collapsed")
    with col_h: f_ho = st.text_input("입주 예정 호수", placeholder="호수 입력 (예: 1201)", key="f_ho", label_visibility="collapsed")
    
    if st.button("✨ 오늘 나의 무료신점 뽑기", use_container_width=True):
        # 🔥 사모님 맞춤형 패치: 숫자가 아닌 문자 완벽 제거
        clean_ho = re.sub(r'[^0-9]', '', f_ho)
        
        if clean_ho == "": 
            st.warning("호수를 정확히 숫자로 입력해주세요! (예: 1201)")
        else:
            valid_combinations = set(zip(df_layout['동'], df_layout['호']))
            input_ho_formatted = clean_ho.zfill(4) 
            if (f_dong, input_ho_formatted) not in valid_combinations:
                st.warning("🔮 앗! 해당 동·호수는 팡도사의 레이더에 잡히지 않는 '없는 기운'입니다. 혹시 아직 지어지지 않은 허공의 터를 누르신 건 아니겠죠? 😅 동과 호수를 다시 한번 정확히 확인해 주세요!")
            else:
                with st.spinner("🔮 팡도사가 고객님의 명조(命造)를 심층 분석 중입니다..."):
                    time.sleep(3.5) 
                st.markdown(get_custom_fortune(f_dong, clean_ho, type_dict), unsafe_allow_html=True)
                
    # 🔥 메인에서 이사 온 VIP 사주 상담 버튼 (항상 노출되도록 버튼 아래 배치)
    st.markdown("""
        <div style='text-align: center; margin-top: 25px; border-top: 1px dotted #333; padding-top: 15px;'>
            <p style='color:#8e8e93; font-size:0.75em; margin-bottom:5px;'>더 깊고 디테일한 운명이 궁금하시다면?</p>
            <a href="https://open.kakao.com/o/gEkb84oi" target="_blank" class='btn-vip-saju'>
                🔮 [Sol 운명상점] 서비스 준비중
            </a>
        </div>
    """, unsafe_allow_html=True)

# ------------------------------------------
# [탭 5] 관련뉴스 
# ------------------------------------------
with tab5:
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

# 🔥 이스터에그
st.markdown("<div class='by-text'>by. 213동102호팡</div>", unsafe_allow_html=True)