import streamlit as st
import pandas as pd
import re
import urllib.request
import xml.etree.ElementTree as ET
import random
from datetime import datetime
import json

# ==========================================
# 1. 기본 화면 설정
# ==========================================
st.set_page_config(page_title="디에트르 그랑루체 가입현황", page_icon="🏢", layout="centered")

# ==========================================
# 2. CSS 스타일링 
# ==========================================
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * { font-family: 'Pretendard', sans-serif; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .block-container { padding-top: 1.0rem !important; padding-bottom: 0.5rem !important; padding-left: 4px !important; padding-right: 4px !important; max-width: 100% !important; }
        
        .premium-title { font-size: clamp(2.0em, 8vw, 2.8em); font-weight: 900; text-align: center; color: #2b6cb0; text-shadow: 0 2px 10px rgba(43, 108, 176, 0.3); margin-bottom: 2px; }
        .promo-title { font-size: 0.85em; text-align: center; color: #D4AF37; font-weight: 700; margin-top: 0px; margin-bottom: 2px; }
        .promo-subtitle { font-size: 0.75em; text-align: center; color: #aaa; font-weight: 400; margin-bottom: 8px; }
        .kakao-btn { display: inline-flex; justify-content: center; align-items: center; background-color: #FEE500; color: #191919 !important; font-weight: 800; font-size: 0.75em; padding: 6px 16px; border-radius: 8px; text-decoration: none !important; box-shadow: 0 2px 6px rgba(254, 229, 0, 0.2); margin-bottom: 8px; transition: all 0.2s ease; }
        
        .notice-text { text-align: center; font-size: 0.7em; letter-spacing: -0.5px; color: #ff9f0a; font-weight: 600; margin-bottom: 8px; padding: 6px 4px; background-color: rgba(255, 159, 10, 0.1); border-radius: 8px; border: 1px solid rgba(255, 159, 10, 0.2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
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
        
        .news-link { color: #d1d1d6; text-decoration: none; font-size: 0.85em; display: block; margin-bottom: 8px; padding-bottom: 8px; border-bottom: 1px solid #333; line-height: 1.4; }
        .news-link:hover { color: #D4AF37; }
        button[data-baseweb="tab"] { font-weight: 800 !important; font-size: 0.9em !important; }
        
        /* 운세 전용 스타일 */
        .saju-box { background: rgba(212, 175, 55, 0.05); border-radius: 12px; border: 1px solid rgba(212, 175, 55, 0.3); padding: 20px; text-align: left; }
        .saju-title { color: #D4AF37; text-align: center; margin-top: 0; font-size: 1.2em; font-weight: 800; margin-bottom: 15px; }
        .saju-section { margin-bottom: 15px; }
        .saju-h5 { color: #d1d1d6; font-size: 0.95em; font-weight: 800; margin-bottom: 5px; border-left: 3px solid #D4AF37; padding-left: 8px; }
        .saju-p { color: #e5e5ea; font-size: 0.85em; line-height: 1.6; margin-top: 0; padding-left: 10px; }
        .saju-footer { color: #aaa; font-size: 0.7em; text-align: center; margin-top: 20px; border-top: 1px dashed #555; padding-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 데이터 로딩 (구글 시트 & 엑셀)
# ==========================================
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQoR29bAcAP0KUBEvS3S6gn5Qz1MTKDJOxz-lW1UEyV_vOcISPxNW2uMuYMrz9HUw/pub?gid=1967078212&single=true&output=csv"
LAYOUT_FILE = "디에트르 그랑루체 카페가입 현황.xlsx" 

@st.cache_data(ttl=60)
def load_data():
    kakao_dict = {}
    cafe_set = set()
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
        return kakao_dict, cafe_set, df_layout
    except Exception as e:
        return {}, set(), pd.DataFrame()

kakao_dict, cafe_set, df_layout = load_data()
if df_layout.empty:
    st.stop()

# ==========================================
# 🔮 [신규] 실시간 부산 날씨 조회 API
# ==========================================
@st.cache_data(ttl=1800) # 30분마다 갱신
def get_busan_weather():
    try:
        # 부산 강서구 에코델타시티 인근 좌표
        url = "https://api.open-meteo.com/v1/forecast?latitude=35.1796&longitude=129.0756&current_weather=true"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        code = data['current_weather']['weathercode']
        
        if code <= 3: return "맑음"
        elif code <= 48: return "흐림"
        else: return "비/눈"
    except:
        return "맑음" # 에러 시 기본값

# ==========================================
# 🔮 [신규] 입주 전 맞춤 롱폼 운세 생성기
# ==========================================
def get_custom_fortune(dong, ho):
    # 💡 동동 중복 에러 해결: {dong}에는 이미 '213동'이 들어있으므로 바로 붙여 씀
    today_str = datetime.now().strftime("%Y%m%d")
    seed_val = f"{today_str}_{dong}_{ho}"
    random.seed(seed_val)

    weather = get_busan_weather()
    current_hour = datetime.now().hour
    time_str = "오전" if current_hour < 12 else ("오후" if current_hour < 18 else "저녁")

    # 1. 날씨 기반 터의 기운 (입주 전 컨텍스트)
    if weather == "맑음":
        site_energy = f"오늘 부산의 하늘은 티 없이 맑고 청명합니다. 이 눈부신 햇살의 양기(陽氣)가 훗날 입주하실 <b>{dong} {ho}호</b>의 터에 가득 차오르고 있습니다. 아직 빈 공간이지만 터의 생기가 돌기 시작했으니, 이곳에 입주하시면 밝은 에너지로 인해 집안에 웃음꽃이 피고 횡재수가 따를 대길(大吉)의 기운입니다."
    elif weather == "흐림":
        site_energy = f"오늘 부산 하늘에 드리운 구름처럼, <b>{dong} {ho}호</b>의 터는 잠시 숨을 고르며 거대한 에너지를 응축하고 있는 하루입니다. 입주 전 고요한 상태에서 지운(地運)이 깊어지고 있으니, 훗날 이사하시게 되면 밖으로 새는 돈이 막히고 재물이 차곡차곡 쌓이는 재물창고가 될 명당입니다."
    else:
        site_energy = f"오늘 부산에 내리는 물의 기운은 <b>{dong} {ho}호</b>의 터에 묻혀있던 묵은 액운을 깨끗하게 씻어내는 '정화의 비'입니다. 풍수에서 물(水)은 곧 재물을 뜻합니다. 입주 전 터가 깨끗하게 닦이고 있으니, 이사 후에는 막혔던 일들이 시원하게 풀려나갈 기막힌 사주입니다."

    # 2. 개인/입주 준비 운세
    fortunes = [
        "오늘은 귀가 얇아지면 남 좋은 일만 시키고 내 지갑만 가벼워지는 형국입니다. 가전제품이나 가구 견적 등 큰돈이 나가는 결정을 하려 했다면 무조건 내일로 미루십시오! 대신 야외 활동 중 뜻밖의 기분 좋은 소식(횡재수)을 들을 수 있습니다.",
        "스트레스가 머리로 몰려 사소한 일에 짜증이 치솟는 날입니다. 배우자나 가족과 입주 준비로 의견 충돌이 생긴다면 무조건 '당신 말이 맞다'고 한 발 물러서십시오. 져주는 것이 곧 이기는 것이며, 그래야 집안의 재물이 엉뚱한 곳으로 새지 않습니다.",
        "오지랖 부리다가 남의 일까지 독박 쓰기 딱 좋은 사주입니다. 오늘은 무조건 '내 코가 석 자' 마인드로 눈치껏 빠지세요. 새집에 들어갈 생각하며 긍정적인 마음을 유지하면, 오히려 막혀있던 대출이나 자금 문제가 뜻밖에 귀인을 만나 술술 풀리는 날입니다."
    ]
    today_fortune = random.choice(fortunes)

    # 3. 개운템
    lucky_items = ["아이스 아메리카노 한 잔", "햇살 10분 맞으며 걷기", "배우자에게 따뜻한 말 한마디", "부동산/인테리어 앱 지우고 하루 쉬기", "퇴근길 로또 5천 원"]
    selected_item = random.choice(lucky_items)
    
    result_html = f"""
    <div class='saju-box'>
        <h4 class='saju-title'>📜 {dong} {ho}호 오늘의 맞춤 운세</h4>
        
        <div class='saju-section'>
            <div class='saju-h5'>🏡 입주 전 터의 기운 ({weather})</div>
            <p class='saju-p'>{site_energy}</p>
        </div>
        
        <div class='saju-section'>
            <div class='saju-h5'>✨ 오늘의 행동 지침</div>
            <p class='saju-p'>{today_fortune}</p>
        </div>
        
        <div class='saju-section' style='background:rgba(0,0,0,0.2); padding:10px; border-radius:8px;'>
            <p style='color:#d1d1d6; font-size:0.85em; margin-bottom:4px;'>🍀 <b>오늘의 개운템 (운을 트는 행동):</b> <span style='color:#30D158; font-weight:800;'>{selected_item}</span></p>
        </div>
        
        <div class='saju-footer'>
            ※ 현재 거주지의 터 기운을 바탕으로 분석한 운세입니다.<br>더 뼈 때리는 나의 진짜 사주/MBTI 분석이 궁금하다면?<br><b>상단의 1:1 톡으로 팡도사에게 문의하세요!</b>
        </div>
    </div>
    """
    return result_html

# ==========================================
# 4. 화면 상단 타이틀 및 공통 배너
# ==========================================
st.markdown("<div class='premium-title'>Detre Granluce</div>", unsafe_allow_html=True)
st.markdown("""
<div class='promo-title'>[Sol 운명상점] 사주 & MBTI 솔루션</div>
<div style='text-align: center; margin-bottom:4px;'><span style='font-size:0.7em; color:#aaa;'>(213동 102호 팡도사)</span></div>
<div style='text-align: center; width: 100%;'><a href="https://open.kakao.com/o/gEkb84oi" target="_blank" class='kakao-btn'>💬 입주민 전용 1:1 톡 (깨알광고)</a></div>
<div class='notice-text'>🚨 현황판에 미표기된 세대는 회장님 및 임원진에게 요청부탁드립니다.</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 종합 포털 탭(Tab) 메뉴
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["🏢 입주현황", "🔮 오늘의 운세", "📰 지역 핫이슈", "📈 부동산/대출"])

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
    clean_html_stats = html_stats.replace('\n', '')
    stats_board.markdown(clean_html_stats, unsafe_allow_html=True)
    
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
# [탭 2] 오늘의 운세 (날씨/시간/동호수 기반 롱폼)
# ------------------------------------------
with tab2:
    st.markdown("<h4 style='text-align:center; color:#D4AF37; margin-top:10px;'>🔮 팡도사의 동·호수 맞춤 운세</h4>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#aaa; font-size:0.75em;'>개인정보 입력 없이, 거주하실 공간의 터 기운과<br>오늘 부산의 날씨를 결합하여 하루를 점쳐드립니다.</p>", unsafe_allow_html=True)
    
    col_d, col_h = st.columns(2)
    with col_d:
        f_dong = st.selectbox("입주 예정 동", all_dongs_raw, key="f_dong", label_visibility="collapsed")
    with col_h:
        f_ho = st.text_input("입주 예정 호수", placeholder="호수 입력 (예: 102)", key="f_ho", label_visibility="collapsed")
    
    if st.button("✨ 우리 집 오늘 운세 뽑기", use_container_width=True):
        if f_ho.strip() == "":
            st.warning("호수를 정확히 입력해주세요! (예: 102)")
        else:
            fortune_html = get_custom_fortune(f_dong, f_ho)
            st.markdown(fortune_html, unsafe_allow_html=True)

# ------------------------------------------
# [탭 3] 지역 핫이슈 
# ------------------------------------------
with tab3:
    st.markdown("<h4 style='text-align:center; color:#d1d1d6; margin-top:10px;'>📰 에코델타시티 실시간 뉴스</h4>", unsafe_allow_html=True)
    try:
        url = "https://news.google.com/rss/search?q=에코델타시티+OR+부동산정책+OR+강서구부동산&hl=ko&gl=KR&ceid=KR:ko"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        xml_data = response.read()
        root = ET.fromstring(xml_data)
        
        count = 0
        for item in root.findall('.//item'):
            if count >= 5: break 
            title = item.find('title').text
            link = item.find('link').text
            st.markdown(f"<a href='{link}' target='_blank' class='news-link'>🔹 {title}</a>", unsafe_allow_html=True)
            count += 1
    except Exception:
        st.info("실시간 뉴스를 불러오는 중입니다. 잠시 후 다시 시도해주세요.")

# ------------------------------------------
# [탭 4] 부동산 및 대출 정보
# ------------------------------------------
with tab4:
    st.markdown("<h4 style='text-align:center; color:#d1d1d6; margin-top:10px;'>📈 부동산 및 금리 동향</h4>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p style='font-size:0.85em; color:#aaa; margin-bottom:2px; text-align:center;'>🏢 에코델타 대장주 실거래</p>", unsafe_allow_html=True)
        st.metric(label="푸르지오센터파크 (84㎡)", value="6억 8,500만", delta="↑ 2,000만 (4/8)")
    with col2:
        st.markdown("<p style='font-size:0.85em; color:#aaa; margin-bottom:2px; text-align:center;'>🏦 주담대 평균 금리 (변동)</p>", unsafe_allow_html=True)
        st.metric(label="시중 1금융권 평균", value="3.85%", delta="↓ 0.12% (전월대비)", delta_color="inverse")
    
    st.markdown("<div style='text-align:center; margin-top:20px;'><a href='https://m.land.naver.com/' target='_blank' class='kakao-btn' style='background-color:#03C75A; color:white !important;'>네이버 부동산 바로가기</a></div>", unsafe_allow_html=True)