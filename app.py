import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Detre Granluce 관제시스템", layout="centered")

# ==========================================
# 💎 초밀착 컴팩트 UI/UX CSS (완벽한 가운데 정렬 & 풀사이즈 적용)
# ==========================================
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * { font-family: 'Pretendard', sans-serif; }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 💡 전체 화면 위아래/좌우 여백을 최소화하여 꽉 차게 만듭니다 */
        .block-container { padding-top: 1.5rem !important; padding-bottom: 0.5rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; max-width: 650px; }
        
        .premium-title { font-size: clamp(1.6em, 5vw, 2.2em); font-weight: 900; text-align: center; color: #2b6cb0; text-shadow: 0 2px 10px rgba(43, 108, 176, 0.3); margin-bottom: 0px; letter-spacing: 0px; }
        .promo-text { font-size: 0.65em; text-align: center; color: #888; font-weight: 300; margin-top: 4px; margin-bottom: 12px; line-height: 1.3; word-break: keep-all; }
        .promo-highlight { color: #D4AF37; font-weight: 600; }
        
        .stat-container { display: flex; flex-direction: column; gap: 6px; margin-bottom: 12px; }
        .stat-box { background: linear-gradient(145deg, #1c1c1e, #121212); padding: 8px 5px; border-radius: 8px; border: 1px solid #333; text-align: center; }
        .stat-box.dong-box { border: 1px solid #D4AF37; }
        .stat-text { font-size: 0.8em; color: #d1d1d6; font-weight: 400; line-height: 1.4; }
        .hl-gold { color: #D4AF37; font-weight: 700; font-size: 1.05em; margin: 0 1px; }
        .hl-green { color: #30D158; font-weight: 700; font-size: 1.05em; margin: 0 1px; }
        
        /* ==========================================
           💡 동 선택 버튼: 우측 치우침 해결 & 100% 풀사이즈 
           ========================================== */
        /* 1. 가장 바깥쪽 컨테이너를 가로 100%로 강제 확장 */
        div[data-testid="stRadio"] { 
            width: 100% !important; 
        }
        /* 2. 5칸 그리드 적용 */
        div[role="radiogroup"] {
            display: grid !important;
            grid-template-columns: repeat(5, 1fr) !important;
            gap: 4px !important;
            width: 100% !important;
            margin-bottom: 15px !important;
        }
        /* 3. 버튼 디자인 (여백 완전 제거 및 가운데 정렬) */
        div[role="radiogroup"] > label {
            background-color: transparent !important;
            border: 1px solid #444 !important;
            border-radius: 6px !important;
            margin: 0 !important;
            padding: 12px 0px !important; /* 상하 크기를 더 키워서 터치하기 편하게 만듦, 좌우 여백은 0 */
            cursor: pointer !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
            box-sizing: border-box !important;
        }
        /* 4. 선택된 버튼 황금색 강조 */
        div[role="radiogroup"] > label[data-checked="true"] {
            background: #D4AF37 !important; 
            border: 1px solid #FFECA1 !important;
        }
        /* 5. 💡 우측 치우침의 진짜 범인! 숨겨진 동그라미의 공간 자체를 소멸시킴 */
        div[role="radiogroup"] > label > div:first-child { 
            display: none !important;
            width: 0px !important;
            margin: 0px !important;
            padding: 0px !important;
        }
        /* 6. 숫자 텍스트를 한가운데로 강력하게 고정 */
        div[role="radiogroup"] > label p { 
            font-size: 0.9em !important; 
            margin: 0 !important; 
            padding: 0 !important;
            text-align: center !important;
            width: 100% !important;
            display: block !important;
        }
        div[role="radiogroup"] > label[data-checked="true"] p {
            color: #1C1C1E !important;
            font-weight: 800 !important;
        }

        .unit-num { font-size: 0.75em !important; font-weight: 800; letter-spacing: -0.5px; }
        .unit-nick { font-size: 0.6em !important; font-weight: 600; line-height: 1.1; margin-top: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 💡 구글 시트 연동 URL
# ==========================================
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQoR29bAcAP0KUBEvS3S6gn5Qz1MTKDJOxz-lW1UEyV_vOcISPxNW2uMuYMrz9HUw/pub?gid=1967078212&single=true&output=csv"
LAYOUT_FILE = "디에트르 그랑루체 카페가입 현황.xlsx" 

@st.cache_data(ttl=60)
def load_data():
    try:
        df_res = pd.read_csv(SHEET_CSV_URL, dtype=str)
        df_res.columns = df_res.columns.str.strip()
        df_res = df_res[['동', '호', '닉네임']].dropna(subset=['동', '호'])
        df_res['동'] = df_res['동'].astype(str).str.extract(r'(\d+)')[0] + "동"
        df_res['호'] = df_res['호'].astype(str).str.extract(r'(\d+)')[0].str.zfill(4) 
        
        df_layout = pd.read_excel(LAYOUT_FILE, sheet_name='동호 코드', skiprows=2, usecols="A:B", header=None, dtype=str)
        df_layout.columns = ['동', '호'] 
        df_layout = df_layout.dropna()
        df_layout['동'] = df_layout['동'].astype(str).str.extract(r'(\d+)')[0] + "동"
        df_layout['호'] = df_layout['호'].astype(str).str.extract(r'(\d+)')[0].str.zfill(4) 
        df_layout = df_layout.dropna().drop_duplicates()
        
        return df_res, df_layout
    except Exception as e:
        st.error(f"🚨 로딩 오류: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_res, df_layout = load_data()
if df_res.empty:
    st.stop()

# ==========================================
# 상단 타이틀 및 홍보 배너
# ==========================================
st.markdown("<div class='premium-title'>Detre Granluce</div>", unsafe_allow_html=True)
st.markdown("""
<div class='promo-text'>
    <span class='promo-highlight'>Sol 운명상점</span> 사주&MBTI 솔루션 <span style='color:#555;'>(213동 102호 팡)</span>
</div>
""", unsafe_allow_html=True)

stats_container = st.container()

all_dongs_raw = df_layout['동'].unique().tolist()
all_dongs = sorted(all_dongs_raw, key=lambda x: int(re.sub(r'[^0-9]', '', x)) if re.sub(r'[^0-9]', '', x).isdigit() else 0)

if not all_dongs:
    st.stop()

# 💡 선택 위젯 
selected_dong = st.radio(
    "동 선택", 
    all_dongs, 
    horizontal=True, 
    format_func=lambda x: x.replace("동", ""),
    label_visibility="collapsed" 
)

total_units = len(df_layout) 
df_res_unique = df_res.drop_duplicates(subset=['동', '호']) 
total_joined = len(df_res_unique)
total_not_joined = total_units - total_joined
total_rate = (total_joined / total_units) * 100 if total_units > 0 else 0

dong_res = df_res[df_res['동'] == selected_dong]
resident_dict = dong_res.groupby('호')['닉네임'].apply(lambda x: '<br>'.join(x)).to_dict()
dong_joined_units = len(resident_dict)

dong_layout = df_layout[df_layout['동'] == selected_dong]
valid_ho_list = dong_layout['호'].dropna().tolist()

dong_total_units = len(valid_ho_list)
dong_not_joined = dong_total_units - dong_joined_units
dong_rate = (dong_joined_units / dong_total_units) * 100 if dong_total_units > 0 else 0

# ==========================================
# 통계 박스 압축 
# ==========================================
with stats_container:
    st.markdown(f"""
    <div class='stat-container'>
        <div class='stat-box'>
            <div class='stat-text'>
                전체 단지 <span class='hl-gold'>{total_units}</span>세대 &nbsp;|&nbsp; 입장 <span class='hl-gold'>{total_joined}</span> &nbsp;|&nbsp; 가입률 <span class='hl-green'>{total_rate:.1f}%</span>
            </div>
        </div>
        <div class='stat-box dong-box'>
            <div class='stat-text'>
                <b>{selected_dong}</b> <span class='hl-gold'>{dong_total_units}</span>세대 &nbsp;|&nbsp; 입장 <span class='hl-gold'>{dong_joined_units}</span> &nbsp;|&nbsp; 해당 동 가입률 <span class='hl-green'>{dong_rate:.1f}%</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
# ==========================================
# 🔥 아파트 도면 (여백 최소화)
# ==========================================
max_floor = max([int(ho[:2]) for ho in valid_ho_list if len(ho)==4]) if valid_ho_list else 20
lines = sorted(list(set([int(ho[-1]) for ho in valid_ho_list if ho[-1].isdigit()]))) if valid_ho_list else [1,2,3,4]

html_grid = "<div style='display: flex; flex-direction: column; gap: 3px;'>"

for floor in range(max_floor, 0, -1):
    html_grid += "<div style='display: flex; flex-wrap: nowrap !important; width: 100%; gap: 3px;'>"
    
    for line in lines:
        ho_str = f"{floor:02d}0{line}" 
        
        base_style = "flex: 1 1 0; min-width: 0; min-height: 38px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; box-sizing: border-box; overflow: hidden; padding: 2px 0px;"
        
        if ho_str not in valid_ho_list:
            html_grid += f"<div style='{base_style} background-color: transparent; border: none;'></div>"
        elif ho_str in resident_dict:
            nicknames = resident_dict[ho_str]
            html_grid += f"<div style='{base_style} background: linear-gradient(135deg, #E6C27A, #D4AF37); border-radius: 4px; box-shadow: 0 2px 5px rgba(212, 175, 55, 0.2); border: 1px solid #FFECA1;'><div class='unit-num' style='color:#1C1C1E;'>{ho_str}</div><div class='unit-nick' style='color:#3A3A3C;'>{nicknames}</div></div>"
        else:
            html_grid += f"<div style='{base_style} background-color: #1C1C1E; border-radius: 4px; border: 1px solid #333;'><div class='unit-num' style='color:#555;'>{ho_str}</div></div>"
            
    html_grid += "</div>"

html_grid += "</div>"

st.markdown(html_grid, unsafe_allow_html=True)