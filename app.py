import streamlit as st
import pandas as pd
import re

# ==========================================
# 💡 기본 설정
# ==========================================
st.set_page_config(page_title="디에트르 그랑루체 가입현황", page_icon="🏢", layout="centered")

# ==========================================
# 💎 CSS 스타일링 (미입장/미위임 빨간색 강조 추가)
# ==========================================
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * { font-family: 'Pretendard', sans-serif; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .block-container { padding-top: 1.5rem !important; padding-bottom: 0.5rem !important; padding-left: 6px !important; padding-right: 6px !important; max-width: 100% !important; }
        
        .premium-title { font-size: clamp(2.2em, 8vw, 3.0em); font-weight: 900; text-align: center; color: #2b6cb0; text-shadow: 0 2px 10px rgba(43, 108, 176, 0.3); margin-bottom: 5px; }
        .promo-title { font-size: 0.85em; text-align: center; color: #D4AF37; font-weight: 700; margin-top: 0px; margin-bottom: 3px; }
        .promo-subtitle { font-size: 0.75em; text-align: center; color: #aaa; font-weight: 400; margin-bottom: 10px; }
        .kakao-btn { display: inline-flex; justify-content: center; align-items: center; background-color: #FEE500; color: #191919 !important; font-weight: 800; font-size: 0.75em; padding: 6px 16px; border-radius: 8px; text-decoration: none !important; box-shadow: 0 2px 6px rgba(254, 229, 0, 0.2); margin-bottom: 12px; transition: all 0.2s ease; }
        .kakao-btn:active { transform: scale(0.95); }
        .kakao-container { text-align: center; width: 100%; }
        .notice-text { text-align: center; font-size: 0.75em; color: #ff9f0a; font-weight: 600; margin-bottom: 12px; padding: 8px 10px; background-color: rgba(255, 159, 10, 0.1); border-radius: 8px; border: 1px solid rgba(255, 159, 10, 0.2); }
        
        /* 🔥 엑셀 병합 스타일 통계 박스 */
        .stat-container { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; width: 100%; }
        .stat-box-new { display: flex; background: linear-gradient(145deg, #1c1c1e, #121212); border-radius: 8px; border: 1px solid #333; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .stat-box-new.dong-box { border: 1px solid #D4AF37; }
        .stat-left { flex: 0 0 33%; background-color: rgba(255, 255, 255, 0.05); display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 10px 5px; border-right: 1px solid #333; font-size: 0.8em; color: #aaa; text-align: center; }
        .stat-left b { font-size: 1.1em; color: #d1d1d6; margin-bottom: 3px; }
        .stat-right { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 10px 12px; gap: 6px; }
        .stat-row { font-size: 0.85em; color: #d1d1d6; display: flex; align-items: center; justify-content: space-between; }
        .stat-label { display: inline-block; font-weight: 600; color: #888;}
        
        .hl-gold { color: #D4AF37; font-weight: 700; font-size: 1.1em; margin: 0 1px; }
        .hl-green { color: #30D158; font-weight: 700; font-size: 1.1em; margin: 0 1px; }
        .hl-red { color: #FF3B30; font-weight: 700; font-size: 1.1em; margin: 0 1px; } /* 남은 세대 강조용 빨간색! */
        
        /* 동 선택 라디오 버튼 */
        div[role="radiogroup"] { display: flex !important; flex-wrap: wrap !important; width: 100% !important; gap: 4px !important; justify-content: center !important; margin-bottom: 16px !important; }
        div[role="radiogroup"] > label { flex: 0 0 calc(20% - 4px) !important; min-width: calc(20% - 4px) !important; background-color: transparent !important; border: none !important; border-bottom: 2px solid #333 !important; padding: 8px 0px !important; cursor: pointer !important; }
        div[role="radiogroup"] > label[data-checked="true"] { border-bottom: 2px solid #D4AF37 !important; }
        div[role="radiogroup"] > label > div:first-child { display: none !important; }
        div[role="radiogroup"] > label p { font-size: 0.9em !important; color: #888 !important; text-align: center !important; width: 100% !important; margin: 0 !important; }
        div[role="radiogroup"] > label[data-checked="true"] p { color: #D4AF37 !important; font-weight: 800 !important; }

        /* 뱃지 및 유닛 */
        .unit-num { font-size: 0.75em !important; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 1px; }
        .unit-nick { font-size: 0.6em !important; font-weight: 600; line-height: 1.1; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .status-badge { font-size: 0.45em !important; font-weight: 800; padding: 2px 4px; border-radius: 4px; margin-top: 2px; display: inline-block; letter-spacing: -0.5px; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
        .red-badge { background-color: #FF3B30; color: white; border: 1px solid #c22820; }
        .yellow-badge { background-color: #4A90E2; color: white; border: 1px solid #2a6fb8; } 
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 💡 구글 시트 링크 (쉼표 구분)
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
        st.error(f"🚨 로딩 오류: {e}")
        return {}, set(), pd.DataFrame()

kakao_dict, cafe_set, df_layout = load_data()
if df_layout.empty:
    st.stop()

# ==========================================
# 🚀 상단 타이틀 & 영업 배너
# ==========================================
st.markdown("<div class='premium-title'>Detre Granluce</div>", unsafe_allow_html=True)
st.markdown("""
<div class='promo-title'>[Sol 운명상점] 사주 & MBTI 솔루션</div>
<div class='promo-subtitle'>당신의 운명을 낱낱이 파헤쳐드립니다 🔮 <span style='font-size:0.9em;'>(213동 102호 팡도사)</span></div>
<div class='kakao-container'><a href="https://open.kakao.com/o/gEkb84oi" target="_blank" class='kakao-btn'>💬 카카오톡 문의하기(깨알광고)</a></div>
<div class='notice-text'>🚨 미입력 또는 신규가입하신 분께서는 꼭 회장님 및 임원진에게 업데이트 요청해주세요!</div>
""", unsafe_allow_html=True)

stats_container = st.container()

# 동 선택
all_dongs_raw = df_layout['동'].unique().tolist()
all_dongs = sorted(all_dongs_raw, key=lambda x: int(re.sub(r'[^0-9]', '', x)) if re.sub(r'[^0-9]', '', x).isdigit() else 0)
selected_dong = st.radio("동 선택", all_dongs, horizontal=True, format_func=lambda x: x.replace("동", ""), label_visibility="collapsed")

# ==========================================
# 🎯 타겟 관리 (앞으로 받아야 할 인원수 계산!)
# ==========================================
total_units = len(df_layout) 
total_kakao = len(kakao_dict)
total_cafe = len(cafe_set)
total_kakao_remain = total_units - total_kakao # 카톡 미입장 타겟 수
total_cafe_remain = total_units - total_cafe   # 카페 미위임 타겟 수

dong_layout = df_layout[df_layout['동'] == selected_dong]
dong_units = len(dong_layout['호'].dropna().tolist())
dong_kakao = len([k for k in kakao_dict.keys() if k[0] == selected_dong])
dong_cafe = len([k for k in cafe_set if k[0] == selected_dong])
dong_kakao_remain = dong_units - dong_kakao    # 동별 카톡 타겟 수
dong_cafe_remain = dong_units - dong_cafe      # 동별 카페 타겟 수

# ==========================================
# 🔥 띄어쓰기 함정 제거! HTML 코드를 왼쪽 벽에 딱 붙였습니다!
# ==========================================
with stats_container:
    st.markdown(f"""
<div class='stat-container'>
    <div class='stat-box-new'>
        <div class='stat-left'>
            <b>전체 단지</b>
            <div><span class='hl-gold' style='font-size: 1.4em;'>{total_units}</span>세대</div>
        </div>
        <div class='stat-right'>
            <div class='stat-row'>
                <span class='stat-label'>카톡방입장</span> 
                <span><span class='hl-gold'>{total_kakao}</span>명 &nbsp;|&nbsp; 미입장 <span class='hl-red'>{total_kakao_remain}</span>세대</span>
            </div>
            <div class='stat-row'>
                <span class='stat-label'>카페위임</span> 
                <span><span class='hl-gold'>{total_cafe}</span>명 &nbsp;|&nbsp; 미위임 <span class='hl-red'>{total_cafe_remain}</span>세대</span>
            </div>
        </div>
    </div>
    
    <div class='stat-box-new dong-box'>
        <div class='stat-left'>
            <b>{selected_dong}</b>
            <div><span class='hl-gold' style='font-size: 1.4em;'>{dong_units}</span>세대</div>
        </div>
        <div class='stat-right'>
            <div class='stat-row'>
                <span class='stat-label'>카톡방입장</span> 
                <span><span class='hl-gold'>{dong_kakao}</span>명 &nbsp;|&nbsp; 미입장 <span class='hl-red'>{dong_kakao_remain}</span>세대</span>
            </div>
            <div class='stat-row'>
                <span class='stat-label'>카페위임</span> 
                <span><span class='hl-gold'>{dong_cafe}</span>명 &nbsp;|&nbsp; 미위임 <span class='hl-red'>{dong_cafe_remain}</span>세대</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
    
# ==========================================
# 🔥 아파트 도면 & 결손 뱃지 (단톡미입장 적용!)
# ==========================================
valid_ho_list = dong_layout['호'].dropna().tolist()
max_floor = max([int(ho[:2]) for ho in valid_ho_list if len(ho)==4]) if valid_ho_list else 20
lines = sorted(list(set([int(ho[-1]) for ho in valid_ho_list if ho[-1].isdigit()]))) if valid_ho_list else [1,2,3,4]

html_grid = "<div style='display: flex; flex-direction: column; gap: 4px;'>"

for floor in range(max_floor, 0, -1):
    html_grid += "<div style='display: flex; flex-wrap: nowrap !important; width: 100%; gap: 4px;'>"
    
    for line in lines:
        ho_str = f"{floor:02d}0{line}" 
        dong_ho_key = (selected_dong, ho_str)
        
        base_style = "flex: 1 1 0; min-width: 0; min-height: 48px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; box-sizing: border-box; overflow: hidden; padding: 2px 0px;"
        
        if ho_str not in valid_ho_list:
            html_grid += f"<div style='{base_style} background-color: transparent; border: none;'></div>"
        
        elif dong_ho_key in kakao_dict or dong_ho_key in cafe_set:
            nicknames = kakao_dict.get(dong_ho_key, "") 
            
            badge_html = ""
            if dong_ho_key not in kakao_dict:
                badge_html += "<div class='status-badge yellow-badge'>단톡미입장</div>"
            if dong_ho_key not in cafe_set:
                badge_html += "<div class='status-badge red-badge'>카페미가입</div>"
                
            html_grid += f"<div style='{base_style} background: linear-gradient(135deg, #E6C27A, #D4AF37); border-radius: 4px; box-shadow: 0 2px 5px rgba(212, 175, 55, 0.2); border: 1px solid #FFECA1;'><div class='unit-num' style='color:#1C1C1E;'>{ho_str}</div><div class='unit-nick' style='color:#3A3A3C;'>{nicknames}</div>{badge_html}</div>"
        else:
            html_grid += f"<div style='{base_style} background-color: #1C1C1E; border-radius: 4px; border: 1px solid #333;'><div class='unit-num' style='color:#555;'>{ho_str}</div></div>"
            
    html_grid += "</div>"
html_grid += "</div>"

st.markdown(html_grid, unsafe_allow_html=True)