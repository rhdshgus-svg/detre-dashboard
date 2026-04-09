import streamlit as st
import pandas as pd

st.set_page_config(page_title="Detre Granluce 관제시스템", layout="centered")

# ==========================================
# 💎 프리미엄 UI/UX CSS (모바일 최적화 Grid 적용)
# ==========================================
st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        * { font-family: 'Pretendard', sans-serif; }
        .block-container { padding-top: 1.5rem; padding-bottom: 1rem; max-width: 650px; }
        
        .premium-title { font-size: 2.8em; font-weight: 900; text-align: center; color: #2b6cb0; text-shadow: 0 4px 15px rgba(43, 108, 176, 0.3); margin-bottom: 0px; letter-spacing: 1px; }
        .promo-text { font-size: 0.75em; text-align: center; color: #888; font-weight: 300; margin-top: 4px; margin-bottom: 25px; line-height: 1.4; }
        .promo-highlight { color: #D4AF37; font-weight: 500; }
        
        .stat-box { background: linear-gradient(145deg, #1c1c1e, #121212); padding: 16px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #333; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .stat-box.dong-box { border: 1px solid #D4AF37; background: linear-gradient(145deg, #221e10, #121212); }
        .stat-text { font-size: 0.9em; color: #d1d1d6; font-weight: 400; line-height: 1.6; }
        .hl-gold { color: #D4AF37; font-weight: 700; font-size: 1.1em; margin: 0 2px; }
        .hl-green { color: #30D158; font-weight: 700; font-size: 1.1em; margin: 0 2px; }
        
        /* 💡 모바일 최적화를 위한 폰트 사이즈 강제 고정 */
        .unit-num { font-size: 0.8em !important; font-weight: 800; letter-spacing: 0px; }
        .unit-nick { font-size: 0.65em !important; font-weight: 600; line-height: 1.2; margin-top: 2px; word-break: keep-all; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 💡 구글 시트 연동 URL (제공해주신 링크 적용 완료!)
# ==========================================
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQoR29bAcAP0KUBEvS3S6gn5Qz1MTKDJOxz-lW1UEyV_vOcISPxNW2uMuYMrz9HUw/pub?gid=1967078212&single=true&output=csv"
LAYOUT_FILE = "디에트르 그랑루체 카페가입 현황.xlsx" 

@st.cache_data(ttl=60) # 60초마다 구글 시트 새로고침
def load_data():
    try:
        # 1. 구글 시트에서 명단 불러오기
        df_res = pd.read_csv(SHEET_CSV_URL, dtype=str)
        df_res.columns = df_res.columns.str.strip()
        df_res = df_res[['동', '호', '닉네임']].dropna(subset=['동', '호'])
        df_res['동'] = df_res['동'].astype(str).str.extract(r'(\d+)')[0] + "동"
        df_res['호'] = df_res['호'].astype(str).str.extract(r'(\d+)')[0].str.zfill(4) 
        
        # 2. 뼈대 엑셀 파일 불러오기
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
# 상단 타이틀 및 통계 대시보드
# ==========================================
st.markdown("<div class='premium-title'>Detre Granluce</div>", unsafe_allow_html=True)
st.markdown("""
<div class='promo-text'>
    <span class='promo-highlight'>Sol 운명상점</span> 사주&MBTI VIP 솔루션 제공, 많은 문의 부탁드려요<br>
    <span style='font-size:0.9em; color:#666;'>by. 213동 102호 팡</span>
</div>
""", unsafe_allow_html=True)

stats_container = st.container()

all_dongs = sorted(df_layout['동'].unique().tolist())
if not all_dongs:
    st.stop()

selected_dong = st.selectbox("🔍 상세 조회할 동 선택", all_dongs)

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
            총 <span class='hl-gold'>{total_units}</span>세대 중 &nbsp;단톡방 입장 <span class='hl-gold'>{total_joined}</span>세대 &nbsp;미입장 <span class='hl-gold'>{total_not_joined}</span>세대<br>
            단지 전체 입장률 <span class='hl-green'>{total_rate:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='stat-box dong-box'>
        <div class='stat-text'>
            <b>{selected_dong}</b> <span class='hl-gold'>{dong_total_units}</span>세대 중 &nbsp;단톡방 입장 <span class='hl-gold'>{dong_joined_units}</span>세대 &nbsp;미입장 <span class='hl-gold'>{dong_not_joined}</span>세대<br>
            해당 동 입장률 <span class='hl-green'>{dong_rate:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
st.write("") 

# ==========================================
# 🔥 스트림릿 강제 억제! CSS Grid 모바일 도면
# ==========================================
max_floor = max([int(ho[:2]) for ho in valid_ho_list if len(ho)==4]) if valid_ho_list else 20
lines = sorted(list(set([int(ho[-1]) for ho in valid_ho_list if ho[-1].isdigit()]))) if valid_ho_list else [1,2,3,4]

# 그리드 컨테이너 시작
html_grid = "<div style='display: flex; flex-direction: column; gap: 4px;'>"

for floor in range(max_floor, 0, -1):
    html_grid += f"<div style='display: grid; grid-template-columns: repeat({len(lines)}, 1fr); gap: 4px;'>"
    
    for line in lines:
        ho_str = f"{floor:02d}0{line}" 
        
        # 투명 허공 (필로티/없는 호수)
        if ho_str not in valid_ho_list:
            html_grid += f"<div style='background-color: transparent; border: none; min-height: 50px;'></div>"
            
        # 단톡방 가입 세대
        elif ho_str in resident_dict:
            nicknames = resident_dict[ho_str]
            html_grid += f"""
            <div style="
                background: linear-gradient(135deg, #E6C27A, #D4AF37); 
                padding: 6px 0px; 
                border-radius: 6px; 
                text-align: center; 
                box-shadow: 0 4px 10px rgba(212, 175, 55, 0.2);
                min-height: 50px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                border: 1px solid #FFECA1;
                box-sizing: border-box;
                overflow: hidden;
            ">
                <div class='unit-num' style='color:#1C1C1E;'>{ho_str}</div>
                <div class='unit-nick' style='color:#3A3A3C;'>{nicknames}</div>
            </div>
            """
            
        # 미가입 세대
        else:
            html_grid += f"""
            <div style="
                background-color: #1C1C1E; 
                padding: 6px 0px; 
                border-radius: 6px; 
                text-align: center; 
                border: 1px solid #333;
                min-height: 50px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                box-sizing: border-box;
            ">
                <div class='unit-num' style='color:#555;'>{ho_str}</div>
            </div>
            """
            
    html_grid += "</div>" # 한 층(Grid 행) 끝

html_grid += "</div>" # 전체 그리드 끝

# 스트림릿에 완성된 전체 도면 HTML을 한 번에 뿌려줍니다.
st.markdown(html_grid, unsafe_allow_html=True)