import streamlit as st
import pandas as pd
import re

# ==========================================
# 1. 기본 화면 설정
# ==========================================
st.set_page_config(page_title="디에트르 그랑루체 가입현황", page_icon="🏢", layout="centered")

# ==========================================
# 2. CSS 스타일링 (🔥 초밀도 압축 및 1줄 고정 적용!)
# ==========================================
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * { font-family: 'Pretendard', sans-serif; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        /* 전체 컨테이너 여백 축소 */
        .block-container { padding-top: 1.0rem !important; padding-bottom: 0.5rem !important; padding-left: 4px !important; padding-right: 4px !important; max-width: 100% !important; }
        
        .premium-title { font-size: clamp(2.0em, 8vw, 2.8em); font-weight: 900; text-align: center; color: #2b6cb0; text-shadow: 0 2px 10px rgba(43, 108, 176, 0.3); margin-bottom: 2px; }
        .promo-title { font-size: 0.85em; text-align: center; color: #D4AF37; font-weight: 700; margin-top: 0px; margin-bottom: 2px; }
        .promo-subtitle { font-size: 0.75em; text-align: center; color: #aaa; font-weight: 400; margin-bottom: 8px; }
        .kakao-btn { display: inline-flex; justify-content: center; align-items: center; background-color: #FEE500; color: #191919 !important; font-weight: 800; font-size: 0.75em; padding: 6px 16px; border-radius: 8px; text-decoration: none !important; box-shadow: 0 2px 6px rgba(254, 229, 0, 0.2); margin-bottom: 8px; transition: all 0.2s ease; }
        
        /* 🔥 안내 문구 1줄 강제 고정 (nowrap) 및 여백 최소화 */
        .notice-text { text-align: center; font-size: 0.7em; letter-spacing: -0.5px; color: #ff9f0a; font-weight: 600; margin-bottom: 8px; padding: 6px 4px; background-color: rgba(255, 159, 10, 0.1); border-radius: 8px; border: 1px solid rgba(255, 159, 10, 0.2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        /* 🔥 통계 박스 상하 간격 축소 */
        .stat-container { display: flex; flex-direction: column; gap: 4px; margin-bottom: 10px; width: 100%; }
        .stat-box-new { display: flex; background: linear-gradient(145deg, #1c1c1e, #121212); border-radius: 8px; border: 1px solid #333; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
        .stat-box-new.dong-box { border: 1px solid #D4AF37; }
        
        /* 왼쪽 공간 축소 (22%) 및 여백 다이어트 */
        .stat-left { flex: 0 0 22%; background-color: rgba(255, 255, 255, 0.05); display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 6px 2px; border-right: 1px solid #333; font-size: 0.7em; color: #aaa; text-align: center; }
        .stat-left b { font-size: 1.15em; color: #d1d1d6; margin-bottom: 2px; white-space: nowrap; }
        
        /* 오른쪽 공간 널널하게! */
        .stat-right { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 6px 8px; gap: 4px; overflow: hidden; }
        .stat-row { font-size: 0.75em; color: #d1d1d6; display: flex; align-items: center; justify-content: space-between; white-space: nowrap; width: 100%; }
        .stat-label { font-weight: 600; color: #888; margin-right: auto; }
        
        /* 강조 색상 */
        .hl-gold { color: #D4AF37; font-weight: 800; font-size: 1.15em; margin: 0 1px; }
        .hl-red { color: #FF3B30; font-weight: 800; font-size: 1.15em; margin: 0 1px; }
        .hl-green { color: #30D158; font-weight: 800; font-size: 1.0em; margin: 0 1px; }
        .divider { color: #555; margin: 0 2px; font-size: 0.9em; }
        
        /* 동 선택 라디오 버튼 간격 축소 */
        div[role="radiogroup"] { display: flex !important; flex-wrap: wrap !important; width: 100% !important; gap: 2px !important; justify-content: center !important; margin-bottom: 10px !important; }
        div[role="radiogroup"] > label { flex: 0 0 calc(20% - 2px) !important; min-width: calc(20% - 2px) !important; background-color: transparent !important; border: none !important; border-bottom: 2px solid #333 !important; padding: 6px 0px !important; cursor: pointer !important; }
        div[role="radiogroup"] > label[data-checked="true"] { border-bottom: 2px solid #D4AF37 !important; }
        div[role="radiogroup"] > label > div:first-child { display: none !important; }
        div[role="radiogroup"] > label p { font-size: 0.85em !important; color: #888 !important; text-align: center !important; width: 100% !important; margin: 0 !important; }
        div[role="radiogroup"] > label[data-checked="true"] p { color: #D4AF37 !important; font-weight: 800 !important; }

        /* 아파트 도면 뱃지 다이어트 */
        .unit-num { font-size: 0.7em !important; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 1px; }
        .unit-nick { font-size: 0.55em !important; font-weight: 600; line-height: 1.1; margin-top: 0px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .status-badge { font-size: 0.45em !important; font-weight: 800; padding: 2px 3px; border-radius: 3px; margin-top: 1px; display: inline-block; letter-spacing: -0.5px; box-shadow: 0 1px 2px rgba(0,0,0,0.3); }
        .red-badge { background-color: #FF3B30; color: white; border: 1px solid #c22820; }
        .yellow-badge { background-color: #4A90E2; color: white; border: 1px solid #2a6fb8; } 
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 데이터 로딩 (구글 시트 & 엑셀 도면)
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
        st.error(f"🚨 데이터 로딩 오류: {e}")
        return {}, set(), pd.DataFrame()

kakao_dict, cafe_set, df_layout = load_data()
if df_layout.empty:
    st.stop()

# ==========================================
# 4. 화면 상단 타이틀 및 배너
# ==========================================
st.markdown("<div class='premium-title'>Detre Granluce</div>", unsafe_allow_html=True)
st.markdown("""
<div class='promo-title'>[Sol 운명상점] 사주 & MBTI 솔루션</div>
<div class='promo-subtitle'>당신의 운명을 낱낱이 파헤쳐드립니다 🔮 <span style='font-size:0.9em;'>(213동 102호 팡도사)</span></div>
<div style='text-align: center; width: 100%;'><a href="https://open.kakao.com/o/gEkb84oi" target="_blank" class='kakao-btn'>💬 카카오톡 문의하기(깨알광고)</a></div>
<div class='notice-text'>🚨 현황판에 미표기된 세대는 회장님 및 임원진에게 요청부탁드립니다.</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. 동 선택 및 통계 계산 로직
# ==========================================
stats_container = st.container()

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

# ==========================================
# 6. 통계 박스 UI
# ==========================================
with stats_container:
    html_stats = f"""<div class='stat-container'><div class='stat-box-new'><div class='stat-left'><b>전체 단지</b><div><span class='hl-gold' style='font-size: 1.3em;'>{total_units}</span>세대</div></div><div class='stat-right'><div class='stat-row'><span class='stat-label'>카톡입장</span><span class='stat-value'><span class='hl-gold'>{total_kakao}</span>세대 (<span class='hl-green'>{kakao_rate:.1f}%</span>) <span class='divider'>|</span> 미입장 <span class='hl-red'>{total_kakao_remain}</span>세대</span></div><div class='stat-row'><span class='stat-label'>카페위임</span><span class='stat-value'><span class='hl-gold'>{total_cafe}</span>세대 (<span class='hl-green'>{cafe_rate:.1f}%</span>) <span class='divider'>|</span> 미위임 <span class='hl-red'>{total_cafe_remain}</span>세대</span></div></div></div><div class='stat-box-new dong-box'><div class='stat-left'><b>{selected_dong}</b><div><span class='hl-gold' style='font-size: 1.3em;'>{dong_units}</span>세대</div></div><div class='stat-right'><div class='stat-row'><span class='stat-label'>카톡입장</span><span class='stat-value'><span class='hl-gold'>{dong_kakao}</span>세대 (<span class='hl-green'>{dong_kakao_rate:.1f}%</span>) <span class='divider'>|</span> 미입장 <span class='hl-red'>{dong_kakao_remain}</span>세대</span></div><div class='stat-row'><span class='stat-label'>카페위임</span><span class='stat-value'><span class='hl-gold'>{dong_cafe}</span>세대 (<span class='hl-green'>{dong_cafe_rate:.1f}%</span>) <span class='divider'>|</span> 미위임 <span class='hl-red'>{dong_cafe_remain}</span>세대</span></div></div></div></div>"""
    clean_html_stats = html_stats.replace('\n', '')
    st.markdown(clean_html_stats, unsafe_allow_html=True)
    
# ==========================================
# 7. 아파트 도면 및 뱃지 (🔥 간격 2px 압축 & 뱃지 로직 수정)
# ==========================================
valid_ho_list = dong_layout['호'].dropna().tolist()
max_floor = max([int(ho[:2]) for ho in valid_ho_list if len(ho)==4]) if valid_ho_list else 20
lines = sorted(list(set([int(ho[-1]) for ho in valid_ho_list if ho[-1].isdigit()]))) if valid_ho_list else [1,2,3,4]

# 전체 도면 상하 간격 2px 로 축소
html_grid = "<div style='display: flex; flex-direction: column; gap: 2px;'>"

for floor in range(max_floor, 0, -1):
    # 각 층별 좌우 간격 2px 로 축소
    html_grid += "<div style='display: flex; flex-wrap: nowrap !important; width: 100%; gap: 2px;'>"
    
    for line in lines:
        ho_str = f"{floor:02d}0{line}" 
        dong_ho_key = (selected_dong, ho_str)
        
        base_style = "flex: 1 1 0; min-width: 0; min-height: 44px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; box-sizing: border-box; overflow: hidden; padding: 2px 0px;"
        
        # 1. 아예 도면에 없는 허수 호수 (투명 처리)
        if ho_str not in valid_ho_list:
            html_grid += f"<div style='{base_style} background-color: transparent; border: none;'></div>"
            
        # 2. 도면에 있는 실제 호수
        else:
            nicknames = kakao_dict.get(dong_ho_key, "") 
            
            # 🔥 하나라도 가입한 경우에만 부족한 뱃지 달기!
            if dong_ho_key in kakao_dict or dong_ho_key in cafe_set:
                badge_html = ""
                if dong_ho_key not in kakao_dict:
                    badge_html += "<div class='status-badge yellow-badge'>카톡미입장</div>"
                if dong_ho_key not in cafe_set:
                    badge_html += "<div class='status-badge red-badge'>위임미진행</div>"
                    
                html_grid += f"<div style='{base_style} background: linear-gradient(135deg, #E6C27A, #D4AF37); border-radius: 4px; box-shadow: 0 2px 4px rgba(212, 175, 55, 0.2); border: 1px solid #FFECA1;'><div class='unit-num' style='color:#1C1C1E;'>{ho_str}</div><div class='unit-nick' style='color:#3A3A3C;'>{nicknames}</div>{badge_html}</div>"
            
            # 🔥 아예 둘 다 가입 안 한 경우 (검은색 배경, 뱃지 없이 텅 비우기!)
            else:
                html_grid += f"<div style='{base_style} background-color: #1C1C1E; border-radius: 4px; border: 1px solid #333;'><div class='unit-num' style='color:#555;'>{ho_str}</div></div>"
            
    html_grid += "</div>"
html_grid += "</div>"

st.markdown(html_grid, unsafe_allow_html=True)