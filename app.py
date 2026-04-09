import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Detre Granluce 관제시스템", layout="centered")

# ==========================================
# 💎 이도의 마스터피스: 프리미엄 디자인 & 완벽 정렬 CSS
# ==========================================
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * { font-family: 'Pretendard', sans-serif; }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 💡 폰 화면 좌우 여백을 아파트 도면과 똑같이 빈틈없이 맞춤 */
        .block-container { 
            padding-top: 1.5rem !important; 
            padding-bottom: 0.5rem !important; 
            padding-left: 6px !important;  
            padding-right: 6px !important; 
            max-width: 100% !important; 
        }
        
        /* 아파트 이름 대폭 확대 & 홍보 문구 조정 */
        .premium-title { font-size: clamp(2.2em, 8vw, 3.0em); font-weight: 900; text-align: center; color: #2b6cb0; text-shadow: 0 2px 10px rgba(43, 108, 176, 0.3); margin-bottom: 5px; letter-spacing: 0px; }
        .promo-title { font-size: 0.85em; text-align: center; color: #D4AF37; font-weight: 700; margin-top: 0px; margin-bottom: 3px; }
        .promo-subtitle { font-size: 0.75em; text-align: center; color: #aaa; font-weight: 400; margin-bottom: 10px; }
        
        /* 💡 카카오톡 문의하기 버튼 */
        .kakao-btn {
            display: inline-flex;
            justify-content: center;
            align-items: center;
            background-color: #FEE500;
            color: #191919 !important;
            font-weight: 800;
            font-size: 0.75em; 
            padding: 6px 16px; 
            border-radius: 8px;
            text-decoration: none !important;
            box-shadow: 0 2px 6px rgba(254, 229, 0, 0.2);
            margin-bottom: 12px; /* 간격 살짝 조절 */
            transition: all 0.2s ease;
        }
        .kakao-btn:active { transform: scale(0.95); }
        .kakao-container { text-align: center; width: 100%; }

        /* 💡 신의 한 수: 임원진 헌정(?) 및 업데이트 안내 박스 */
        .notice-text {
            text-align: center;
            font-size: 0.75em;
            color: #ff9f0a; /* 주황빛 경고/안내 색상으로 눈에 띄게 */
            font-weight: 600;
            margin-bottom: 18px;
            padding: 8px 10px;
            background-color: rgba(255, 159, 10, 0.1); /* 은은한 배경색 */
            border-radius: 8px;
            border: 1px solid rgba(255, 159, 10, 0.2);
            word-break: keep-all;
        }

        /* 동 선택 안내 문구 */
        .helper-text { text-align: center; font-size: 0.8em; color: #888; margin-bottom: 6px; font-weight: 500; }

        /* 통계 박스 */
        .stat-container { display: flex; flex-direction: column; gap: 4px; margin-bottom: 16px; width: 100%; }
        .stat-box { background: linear-gradient(145deg, #1c1c1e, #121212); padding: 8px 5px; border-radius: 6px; border: 1px solid #333; text-align: center; }
        .stat-box.dong-box { border: 1px solid #D4AF37; }
        .stat-text { font-size: 0.8em; color: #d1d1d6; font-weight: 400; line-height: 1.4; }
        .hl-gold { color: #D4AF37; font-weight: 700; font-size: 1.05em; margin: 0 1px; }
        .hl-green { color: #30D158; font-weight: 700; font-size: 1.05em; margin: 0 1px; }
        
        /* ==========================================
           💡 동 선택 버튼: 완벽한 중앙 정렬 & 마지막 줄 쏠림 해결
           ========================================== */
        div[data-testid="stRadio"] { width: 100% !important; }
        label[data-testid="stWidgetLabel"] { display: none !important; }
        
        div[role="radiogroup"] {
            display: flex !important;
            flex-wrap: wrap !important;
            width: 100% !important;
            gap: 4px !important;
            justify-content: center !important; 
            margin-bottom: 16px !important;
        }
        
        div[role="radiogroup"] > label {
            flex: 0 0 calc(20% - 4px) !important; 
            min-width: calc(20% - 4px) !important;
            background-color: transparent !important;
            border: none !important;
            border-bottom: 2px solid #333 !important; 
            border-radius: 0px !important;
            padding: 8px 0px !important;
            margin: 0 !important;
            box-sizing: border-box !important;
            cursor: pointer !important;
        }
        
        div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(to top, rgba(212, 175, 55, 0.2), transparent) !important; 
            border-bottom: 2px solid #D4AF37 !important; 
        }
        
        div[role="radiogroup"] > label > div:first-child { display: none !important; width: 0 !important; }
        
        div[role="radiogroup"] > label p { 
            font-size: 0.9em !important; 
            color: #888 !important; 
            text-align: center !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        div[role="radiogroup"] > label[data-checked="true"] p {
            color: #D4AF37 !important; 
            font-weight: 800 !important;
        }

        /* 아파트 도면 글씨 크기 조정 */
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
        
        # 중복 닉네임 완벽 차단 방어망
        df_res['닉네임'] = df_res['닉네임'].str.strip()
        df_res = df_res.drop_duplicates(subset=['동', '호', '닉네임'])
        
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
# 🚀 상단 타이틀, 카톡 배너, 그리고 임원진 헌정 멘트!
# ==========================================
st.markdown("""
<div class='premium-title'>Detre Granluce</div>
<div class='promo-title'>[Sol 운명상점] 사주 & MBTI 솔루션</div>
<div class='promo-subtitle'>당신의 운명을 낱낱이 파헤쳐드립니다 🔮 <span style='font-size:0.9em;'>(213동 102호 팡도사)</span></div>
<div class='kakao-container'>
    <a href="https://open.kakao.com/o/gEkb84oi" target="_blank" class='kakao-btn'>
        💬 카카오톡 문의하기(깨알광고)
    </a>
</div>
<div class='notice-text'>
    🚨 누락 또는 신규가입하신 분께서는 꼭 회장님 및 임원진에게 업데이트 요청해주세요!
</div>
""", unsafe_allow_html=True)

stats_container = st.container()

all_dongs_raw = df_layout['동'].unique().tolist()
all_dongs = sorted(all_dongs_raw, key=lambda x: int(re.sub(r'[^0-9]', '', x)) if re.sub(r'[^0-9]', '', x).isdigit() else 0)

if not all_dongs:
    st.stop()

# ==========================================
# 💡 동 선택 안내 문구 추가
# ==========================================
st.markdown("<div class='helper-text'>👇 상세 조회할 동을 선택하세요</div>", unsafe_allow_html=True)

selected_dong = st.radio("동 선택", all_dongs, horizontal=True, format_func=lambda x: x.replace("동", ""), label_visibility="collapsed")

total_units = len(df_layout) 
df_res_unique = df_res.drop_duplicates(subset=['동', '호']) 
total_joined = len(df_res_unique)
total_not_joined = total_units - total_joined
total_rate = (total_joined / total_units) * 100 if total_units > 0 else 0

dong_res = df_res[df_res['동'] == selected_dong]
resident_dict = dong_res.groupby('호')['닉네임'].apply(lambda x: '<br>'.join(x.unique())).to_dict()
dong_joined_units = len(resident_dict)

dong_layout = df_layout[df_layout['동'] == selected_dong]
valid_ho_list = dong_layout['호'].dropna().tolist()

dong_total_units = len(valid_ho_list)
dong_not_joined = dong_total_units - dong_joined_units
dong_rate = (dong_joined_units / dong_total_units) * 100 if dong_total_units > 0 else 0

# ==========================================
# 통계 박스
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
# 🔥 아파트 도면 모바일 가로 꽉 차게 절대 고정
# ==========================================
max_floor = max([int(ho[:2]) for ho in valid_ho_list if len(ho)==4]) if valid_ho_list else 20
lines = sorted(list(set([int(ho[-1]) for ho in valid_ho_list if ho[-1].isdigit()]))) if valid_ho_list else [1,2,3,4]

html_grid = "<div style='display: flex; flex-direction: column; gap: 4px;'>"

for floor in range(max_floor, 0, -1):
    html_grid += "<div style='display: flex; flex-wrap: nowrap !important; width: 100%; gap: 4px;'>"
    
    for line in lines:
        ho_str = f"{floor:02d}0{line}" 
        
        base_style = "flex: 1 1 0; min-width: 0; min-height: 40px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; box-sizing: border-box; overflow: hidden; padding: 2px 0px;"
        
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