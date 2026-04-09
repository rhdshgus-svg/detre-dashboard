import streamlit as st
import pandas as pd
import re # 숫자 정렬을 위한 라이브러리 추가

st.set_page_config(page_title="Detre Granluce 관제시스템", layout="centered")

# ==========================================
# 💎 프리미엄 UI/UX CSS (동 버튼 4열 완벽 정렬 추가)
# ==========================================
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * { font-family: 'Pretendard', sans-serif; }
        
        /* 스트림릿 기본 UI 숨기기 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 화면 상단 여백 (제목 잘림 방지) */
        .block-container { padding-top: 3.5rem !important; padding-bottom: 1rem; max-width: 650px; }
        
        .premium-title { font-size: clamp(2.0em, 6vw, 2.8em); font-weight: 900; text-align: center; color: #2b6cb0; text-shadow: 0 4px 15px rgba(43, 108, 176, 0.3); margin-bottom: 0px; letter-spacing: 1px; }
        .promo-text { font-size: clamp(0.7em, 2.5vw, 0.8em); text-align: center; color: #888; font-weight: 300; margin-top: 8px; margin-bottom: 25px; line-height: 1.5; word-break: keep-all; }
        .promo-highlight { color: #D4AF37; font-weight: 600; }
        
        .stat-box { background: linear-gradient(145deg, #1c1c1e, #121212); padding: 15px 10px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #333; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .stat-box.dong-box { border: 1px solid #D4AF37; background: linear-gradient(145deg, #221e10, #121212); }
        .stat-text { font-size: clamp(0.85em, 3vw, 0.95em); color: #d1d1d6; font-weight: 400; line-height: 1.8; }
        .hl-gold { color: #D4AF37; font-weight: 700; font-size: 1.1em; margin: 0 2px; }
        .hl-green { color: #30D158; font-weight: 700; font-size: 1.1em; margin: 0 2px; }
        
        /* 💡 동 선택 버튼: 무조건 4칸 격자(Grid)로 자로 잰 듯이 정렬 */
        div[role="radiogroup"] {
            display: grid !important;
            grid-template-columns: repeat(4, 1fr) !important; /* 4열로 강제 분할 */
            gap: 6px !important;
            margin-bottom: 15px !important;
        }
        div[role="radiogroup"] > label {
            background-color: #1C1C1E !important;
            border: 1px solid #333 !important;
            border-radius: 8px !important;
            padding: 10px 0px !important; /* 상하 여백만 주고 좌우는 꽉 채움 */
            margin: 0 !important;
            cursor: pointer !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important; /* 칸 너비에 100% 맞춤 */
        }
        div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(135deg, #E6C27A, #D4AF37) !important;
            border: 1px solid #FFECA1 !important;
            box-shadow: 0 2px 8px rgba(212, 175, 55, 0.3) !important;
        }
        div[role="radiogroup"] > label[data-checked="true"] p {
            color: #1C1C1E !important;
            font-weight: 800 !important;
        }
        div[role="radiogroup"] > label > div:first-of-type {
            display: none !important; /* 촌스러운 기본 동그라미 숨기기 */
        }
        /* 동 버튼 글씨 크기 조정 */
        div[role="radiogroup"] > label p {
            font-size: clamp(0.75em, 2.5vw, 0.9em) !important;
            margin: 0 !important;
        }

        .unit-num { font-size: clamp(0.7em, 2.5vw, 0.9em) !important; font-weight: 800; letter-spacing: 0px; }
        .unit-nick { font-size: clamp(0.55em, 2vw, 0.65em) !important; font-weight: 600; line-height: 1.3; margin-top: 3px; word-break: keep-all; overflow: hidden; text-overflow: ellipsis; }
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
        st.error(f"🚨 데이터 로딩 오류: {e}")
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
    <span class='promo-highlight'>Sol 운명상점</span> 사주 & MBTI VIP 솔루션 제공<br>
    많은 문의 부탁드려요 <span style='font-size:0.85em; color:#666;'>(by. 213동 102호 팡)</span>
</div>
""", unsafe_allow_html=True)

stats_container = st.container()

# 💡 핵심: 201동, 202동 등 숫자 순서대로 완벽하게 오름차순 정렬!
all_dongs_raw = df_layout['동'].unique().tolist()
all_dongs = sorted(all_dongs_raw, key=lambda x: int(re.sub(r'[^0-9]', '', x)) if re.sub(r'[^0-9]', '', x).isdigit() else 0)

if not all_dongs:
    st.stop()

# 라디오 버튼으로 동 선택 (키보드 팝업 방지 및 4열 정렬 적용됨)
selected_dong = st.radio("🔍 상세 조회할 동 클릭", all_dongs, horizontal=True)

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

with stats_container:
    st.markdown(f"""
    <div class='stat-box'>
        <div class='stat-text'>
            <div style="margin-bottom: 3px;">총 <span class='hl-gold'>{total_units}</span>세대 중</div>
            <div style="margin-bottom: 3px;">입장 <span class='hl-gold'>{total_joined}</span>세대 &nbsp;|&nbsp; 미입장 <span class='hl-gold'>{total_not_joined}</span>세대</div>
            <div>단지 전체 입장률 <span class='hl-green'>{total_rate:.1f}%</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='stat-box dong-box'>
        <div class='stat-text'>
            <div style="margin-bottom: 3px;"><b>{selected_dong}</b> <span class='hl-gold'>{dong_total_units}</span>세대 중</div>
            <div style="margin-bottom: 3px;">입장 <span class='hl-gold'>{dong_joined_units}</span>세대 &nbsp;|&nbsp; 미입장 <span class='hl-gold'>{dong_not_joined}</span>세대</div>
            <div>해당 동 입장률 <span class='hl-green'>{dong_rate:.1f}%</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
st.write("") 

# ==========================================
# 🔥 아파트 도면 모바일 가로 4칸 절대 고정
# ==========================================
max_floor = max([int(ho[:2]) for ho in valid_ho_list if len(ho)==4]) if valid_ho_list else 20
lines = sorted(list(set([int(ho[-1]) for ho in valid_ho_list if ho[-1].isdigit()]))) if valid_ho_list else [1,2,3,4]

html_grid = "<div style='display: flex; flex-direction: column; gap: 4px;'>"

for floor in range(max_floor, 0, -1):
    html_grid += "<div style='display: flex; flex-wrap: nowrap !important; width: 100%; gap: 4px;'>"
    
    for line in lines:
        ho_str = f"{floor:02d}0{line}" 
        
        base_style = "flex: 1 1 0; min-width: 0; min-height: 48px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; box-sizing: border-box; overflow: hidden; padding: 4px 1px;"
        
        if ho_str not in valid_ho_list:
            html_grid += f"<div style='{base_style} background-color: transparent; border: none;'></div>"
        elif ho_str in resident_dict:
            nicknames = resident_dict[ho_str]
            html_grid += f"<div style='{base_style} background: linear-gradient(135deg, #E6C27A, #D4AF37); border-radius: 6px; box-shadow: 0 4px 10px rgba(212, 175, 55, 0.2); border: 1px solid #FFECA1;'><div class='unit-num' style='color:#1C1C1E;'>{ho_str}</div><div class='unit-nick' style='color:#3A3A3C;'>{nicknames}</div></div>"
        else:
            html_grid += f"<div style='{base_style} background-color: #1C1C1E; border-radius: 6px; border: 1px solid #333;'><div class='unit-num' style='color:#555;'>{ho_str}</div></div>"
            
    html_grid += "</div>"

html_grid += "</div>"

st.markdown(html_grid, unsafe_allow_html=True)