import streamlit as st
import pandas as pd
import re

# ==========================================
# 💡 기본 설정
# ==========================================
st.set_page_config(page_title="디에트르 그랑루체 가입현황", page_icon="🏢", layout="centered")

st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * { font-family: 'Pretendard', sans-serif; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .block-container { padding-top: 1.5rem !important; padding-bottom: 0.5rem !important; padding-left: 6px !important; padding-right: 6px !important; max-width: 100% !important; }
        
        .premium-title { font-size: clamp(2.2em, 8vw, 3.0em); font-weight: 900; text-align: center; color: #2b6cb0; margin-bottom: 5px; }
        .promo-title { font-size: 0.85em; text-align: center; color: #D4AF37; font-weight: 700; margin-top: 0px; margin-bottom: 3px; }
        .promo-subtitle { font-size: 0.75em; text-align: center; color: #aaa; margin-bottom: 10px; }
        .notice-text { text-align: center; font-size: 0.75em; color: #ff9f0a; font-weight: 600; margin-bottom: 12px; padding: 8px 10px; background-color: rgba(255, 159, 10, 0.1); border-radius: 8px; border: 1px solid rgba(255, 159, 10, 0.2); }
        
        /* 🏢 아버님 전용: 엑셀 병합 스타일 통계 박스 */
        .stat-container { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; width: 100%; }
        .stat-box-new { display: flex; background: linear-gradient(145deg, #1c1c1e, #121212); border-radius: 8px; border: 1px solid #333; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .stat-box-new.dong-box { border: 1px solid #D4AF37; }
        .stat-left { flex: 0 0 35%; background-color: rgba(255, 255, 255, 0.05); display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 10px 5px; border-right: 1px solid #333; font-size: 0.85em; color: #aaa; text-align: center; }
        .stat-left b { font-size: 1.1em; color: #d1d1d6; margin-bottom: 2px; }
        .stat-right { flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 10px 15px; gap: 8px; }
        .stat-row { font-size: 0.85em; color: #d1d1d6; display: flex; align-items: center; justify-content: space-between; }
        
        .hl-gold { color: #D4AF37; font-weight: 900; }
        .hl-green { color: #30D158; font-weight: 900; }
        
        /* 도면 및 뱃지 스타일 */
        div[role="radiogroup"] { display: flex !important; flex-wrap: wrap !important; width: 100% !important; gap: 4px !important; justify-content: center !important; margin-bottom: 16px !important; }
        div[role="radiogroup"] > label { flex: 0 0 calc(20% - 4px) !important; min-width: calc(20% - 4px) !important; background-color: transparent !important; border: none !important; border-bottom: 2px solid #333 !important; padding: 8px 0px !important; cursor: pointer !important; }
        div[role="radiogroup"] > label[data-checked="true"] { border-bottom: 2px solid #D4AF37 !important; }
        div[role="radiogroup"] > label > div:first-child { display: none !important; }
        div[role="radiogroup"] > label p { font-size: 0.9em !important; color: #888 !important; text-align: center !important; width: 100% !important; margin: 0 !important; }
        div[role="radiogroup"] > label[data-checked="true"] p { color: #D4AF37 !important; font-weight: 800 !important; }

        .unit-num { font-size: 0.75em !important; font-weight: 800; margin-bottom: 1px; color: #1C1C1E; }
        .unit-nick { font-size: 0.6em !important; font-weight: 600; line-height: 1.1; color: #3A3A3C; }
        .status-badge { font-size: 0.45em !important; font-weight: 800; padding: 2px 4px; border-radius: 4px; margin-top: 2px; display: inline-block; box-shadow: 0 1px 3px rgba(0,0,0,0.3); }
        .red-badge { background-color: #FF3B30; color: white; }
        .yellow-badge { background-color: #4A90E2; color: white; }
    </style>
""", unsafe_allow_html=True)

# 💡 구글 시트 링크
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQoR29bAcAP0KUBEvS3S6gn5Qz1MTKDJOxz-lW1UEyV_vOcISPxNW2uMuYMrz9HUw/pub?gid=1967078212&single=true&output=csv"
LAYOUT_FILE = "디에트르 그랑루체 카페가입 현황.xlsx" 

@st.cache_data(ttl=0) 
def load_data():
    kakao_dict = {}
    cafe_set = set()
    try:
        # 1. 아파트 도면 로드
        df_layout = pd.read_excel(LAYOUT_FILE, sheet_name='동호 코드', skiprows=2, usecols="A:B", header=None, dtype=str)
        df_layout.columns = ['동', '호']
        df_layout['동'] = df_layout['동'].astype(str).str.extract(r'(\d+)')[0] + "동"
        df_layout['호'] = df_layout['호'].astype(str).str.extract(r'(\d+)')[0].str.zfill(4)
        df_layout = df_layout.dropna().drop_duplicates()

        # 2. 구글 시트 로드 
        df_raw = pd.read_csv(SHEET_CSV_URL, dtype=str, sep=None, engine='python')
        df_raw.columns = [str(c).replace(' ', '').strip() for c in df_raw.columns]
        
        for _, row in df_raw.iterrows():
            # 카톡 데이터 
            kd = str(row.get('동', ''))
            kh = str(row.get('호', ''))
            kn = str(row.get('닉네임', ''))
            if kd and kh and kd != 'nan':
                d_num = re.sub(r'[^0-9]', '', kd)
                h_num = re.sub(r'[^0-9]', '', kh)
                if d_num and h_num:
                    key = (d_num + "동", h_num.zfill(4))
                    if key not in kakao_dict: kakao_dict[key] = set()
                    if kn and kn != 'nan': kakao_dict[key].add(kn)

            # 카페 데이터 
            cd = str(row.get('카페동', ''))
            ch = str(row.get('카페호', ''))
            if cd and ch and cd != 'nan':
                cd_num = re.sub(r'[^0-9]', '', cd)
                ch_num = re.sub(r'[^0-9]', '', ch)
                if cd_num and ch_num:
                    cafe_set.add((cd_num + "동", ch_num.zfill(4)))
        
        kakao_final = {k: '<br>'.join(sorted(list(v))) for k, v in kakao_dict.items()}
        return kakao_final, cafe_set, df_layout
    except Exception as e:
        st.error(f"데이터 로드 중 오류: {e}")
        return {}, set(), pd.DataFrame()

kakao_dict, cafe_set, df_layout = load_data()

# ==========================================
# 🚀 상단 타이틀 & 통계
# ==========================================
st.markdown("<div class='premium-title'>Detre Granluce</div>", unsafe_allow_html=True)
st.markdown("<div class='promo-title'>[Sol 운명상점] 사주 & MBTI 솔루션</div>", unsafe_allow_html=True)

stats_container = st.container()

all_dongs = sorted(df_layout['동'].unique().tolist(), key=lambda x: int(re.sub(r'[^0-9]', '', x)))
selected_dong = st.radio("동 선택", all_dongs, horizontal=True, format_func=lambda x: x.replace("동", ""), label_visibility="collapsed")

# 💡 통계 계산
total_units = len(df_layout)
total_kakao = len(kakao_dict)
total_cafe = len(cafe_set)
kakao_rate = (total_kakao / total_units) * 100 if total_units > 0 else 0
cafe_rate = (total_cafe / total_units) * 100 if total_units > 0 else 0

dong_layout = df_layout[df_layout['동'] == selected_dong]
dong_units = len(dong_layout)
dong_kakao = len([k for k in kakao_dict.keys() if k[0] == selected_dong])
dong_cafe = len([k for k in cafe_set if k[0] == selected_dong])
dong_kakao_rate = (dong_kakao / dong_units) * 100 if dong_units > 0 else 0
dong_cafe_rate = (dong_cafe / dong_units) * 100 if dong_units > 0 else 0

with stats_container:
    # 💡 수정 포인트: <span class='hl-gold'>를 써서 '1470세대'가 한 덩어리로 붙게 만들었습니다!
    st.markdown(f"""
    <div class='stat-container'>
        <div class='stat-box-new'>
            <div class='stat-left'>
                <b>전체 단지</b>
                <div><span class='hl-gold' style='font-size: 1.4em;'>{total_units}</span>세대</div>
            </div>
            <div class='stat-right'>
                <div class='stat-row'><span>💬 카톡방입장</span> <span><span class='hl-gold'>{total_kakao}</span>명 (<span class='hl-green'>{kakao_rate:.1f}%</span>)</span></div>
                <div class='stat-row'><span>☕ 카페위임</span> <span><span class='hl-gold'>{total_cafe}</span>명 (<span class='hl-green'>{cafe_rate:.1f}%</span>)</span></div>
            </div>
        </div>
        <div class='stat-box-new dong-box'>
            <div class='stat-left'>
                <b>{selected_dong}</b>
                <div><span class='hl-gold' style='font-size: 1.4em;'>{dong_units}</span>세대</div>
            </div>
            <div class='stat-right'>
                <div class='stat-row'><span>💬 카톡방입장</span> <span><span class='hl-gold'>{dong_kakao}</span>명 (<span class='hl-green'>{dong_kakao_rate:.1f}%</span>)</span></div>
                <div class='stat-row'><span>☕ 카페위임</span> <span><span class='hl-gold'>{dong_cafe}</span>명 (<span class='hl-green'>{dong_cafe_rate:.1f}%</span>)</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 도면 그리기
valid_ho_list = dong_layout['호'].tolist()
max_floor = max([int(ho[:2]) for ho in valid_ho_list])
lines = sorted(list(set([int(ho[-2:]) for ho in valid_ho_list])))

html_grid = "<div style='display: flex; flex-direction: column; gap: 4px;'>"
for floor in range(max_floor, 0, -1):
    html_grid += "<div style='display: flex; gap: 4px;'>"
    for line in lines:
        ho_str = f"{floor:02d}{line:02d}"
        key = (selected_dong, ho_str)
        if ho_str in valid_ho_list:
            bg = "linear-gradient(135deg, #E6C27A, #D4AF37)" if (key in kakao_dict or key in cafe_set) else "#1C1C1E"
            border = "1px solid #FFECA1" if (key in kakao_dict or key in cafe_set) else "1px solid #333"
            color_num = "#1C1C1E" if (key in kakao_dict or key in cafe_set) else "#555"
            
            badges = ""
            if (key in kakao_dict or key in cafe_set):
                if key not in kakao_dict: badges += "<div class='status-badge yellow-badge'>단톡미가입</div>"
                if key not in cafe_set: badges += "<div class='status-badge red-badge'>카페미가입</div>"
            
            nick = kakao_dict.get(key, "")
            html_grid += f"""<div style='flex:1; min-height:50px; background:{bg}; border:{border}; border-radius:4px; display:flex; flex-direction:column; justify-content:center; align-items:center;'>
                <div class='unit-num' style='color:{color_num};'>{ho_str}</div>
                <div class='unit-nick'>{nick}</div>
                {badges}
            </div>"""
        else:
            html_grid += "<div style='flex:1; background:transparent;'></div>"
    html_grid += "</div>"
st.markdown(html_grid + "</div>", unsafe_allow_html=True)