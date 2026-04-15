import os
import requests
import urllib3
import json
import re
import csv
import gspread
import threading
import time
import uuid
import hmac
import hashlib
from flask import Flask, request, redirect, session, render_template_string, jsonify
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

import make_db  # 💡 오후 7시에 실행할 수집기 파일을 불러옵니다.

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "보관소.env"))

app = Flask(__name__)
app.secret_key = "nara_banjang_pro_secret_key"
app.permanent_session_lifetime = timedelta(days=31)

KAKAO_CLIENT_ID = os.getenv("KAKAO_REST_IP", "1aae24a524eac1ef066b6e25def1056a")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "vyF63ImRBkxBj2VwN89UUpZdKDEq6gau")
REDIRECT_URI = "https://nara-banjang.onrender.com/oauth/kakao/callback"
SITE_URL = "https://nara-banjang.onrender.com"

SOLAR_API_KEY = os.getenv("SOLAR_API_KEY")
SOLAR_API_SECRET = os.getenv("SOLAR_API_SECRET")
SENDER_NUMBER = os.getenv("SENDER_NUMBER")

# 💡 [수정 완료] 지점장님이 요청하신 새로운 구글 시트 URL 적용
SHEET_URL = "https://docs.google.com/spreadsheets/d/1td24AQyl97v30C2s2wA8N2iUJYqGEM02W-pFKoNWF8I/edit?gid=0#gid=0"

@app.before_request
def force_localhost():
    if request.host.startswith('127.0.0.1'):
        url = request.url.replace('127.0.0.1', 'localhost', 1)
        return redirect(url)

def get_sheets():
    creds_path = os.path.join(BASE_DIR, 'credentials.json')
    client = gspread.service_account(filename=creds_path)
    doc = client.open_by_url(SHEET_URL)
    try: notice_sheet = doc.worksheet("공지사항")
    except: notice_sheet = None
    return doc.sheet1, doc.worksheet("개인정보활용동의서"), notice_sheet

def get_live_notice():
    try:
        _, _, notice_sheet = get_sheets()
        if notice_sheet:
            status = notice_sheet.acell('B1').value or ""
            if status.strip() == "게시":
                content = notice_sheet.acell('A2').value or ""
                return {"show": True, "title": "📢 입찰반장 공지사항", "content": content.replace('\n', '<br>')}
    except: pass
    return {"show": False}

def sync_user_from_sheet(kid, default_nickname):
    try:
        sheet, _, _ = get_sheets()
        
        raw_ids = sheet.col_values(1)
        clean_ids = [str(x).replace("'", "").replace('"', "").strip() for x in raw_ids]
        kid_str = str(kid).replace("'", "").replace('"', "").strip()
        
        if kid_str in clean_ids:
            row = clean_ids.index(kid_str) + 1
            data = sheet.row_values(row)
            
            nickname = data[1] if len(data) > 1 else default_nickname
            phone = data[2] if len(data) > 2 else ""
            agency = data[3] if len(data) > 3 else ""
            
            regions_str = data[4] if len(data) > 4 else ""
            pref_time = data[5].strip() if len(data) > 5 and data[5].strip() else "09:00" 
            membership = data[6].strip().lower() if len(data) > 6 else "무료"            
            expire_date_str = data[7].strip() if len(data) > 7 else "2026-12-31"         
            
            is_master = (membership == "마스터" or membership == "master")
            is_premium = False
            
            if is_master:
                is_premium = True
            elif membership == "유료":
                try:
                    expire_dt = datetime.strptime(expire_date_str, "%Y-%m-%d")
                    if expire_dt >= datetime.now():
                        is_premium = True
                except: pass

            display_label = "Master회원" if is_master else ("VIP회원" if membership == "유료" else "무료회원")

            combined_regions = []
            if regions_str:
                combined_regions.extend([r.strip() for r in regions_str.split(",") if r.strip()])
                
            # 💡 [수정 완료] K열을 건너뛰고 L열(11)부터 추가된 지역을 읽어오도록 수정
            if len(data) > 11:
                for col_idx in range(11, len(data)):
                    val = data[col_idx].strip()
                    if val and val not in combined_regions:
                        combined_regions.append(val)

            return {
                "id": kid_str, "nickname": nickname, "phone": phone, "agency": agency,
                "regions": combined_regions, "pref_time": pref_time, 
                "is_premium": is_premium, "is_master": is_master, "premium_label": display_label, "is_new": False
            }
        else:
            return {"id": kid_str, "nickname": default_nickname, "regions": [], "pref_time": "09:00", "is_premium": False, "is_master": False, "premium_label": "무료회원", "is_new": True}
    except Exception as e:
        print(f"구글 시트 연동 에러: {e}")
        return {"id": str(kid).replace("'", "").replace('"', "").strip(), "nickname": default_nickname, "regions": [], "pref_time": "09:00", "is_premium": False, "is_master": False, "premium_label": "무료회원", "is_new": True}

REGION_DATA = {
    "서울": ["강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"],
    "부산": ["강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구", "북구", "사상구", "사하구", "서구", "수영구", "연제구", "영도구", "중구", "해운대구"],
    "대구": ["남구", "달서구", "달성군", "동구", "북구", "서구", "수성구", "중구", "군위군"],
    "인천": ["강화군", "계양구", "남동구", "동구", "미추홀구", "부평구", "서구", "연수구", "옹진군", "중구"],
    "광주": ["광산구", "남구", "동구", "북구", "서구"],
    "대전": ["대덕구", "동구", "서구", "유성구", "중구"],
    "울산": ["남구", "동구", "북구", "중구", "울주군"],
    "세종": ["세종특별자치시"],
    "경기": ["가평군", "고양시", "과천시", "광명시", "광주시", "구리시", "군포시", "김포시", "남양주시", "동두천시", "부천시", "성남시", "수원시", "시흥시", "안산시", "안성시", "안양시", "양주시", "양평군", "여주시", "연천군", "오산시", "용인시", "의왕시", "의정부시", "이천시", "파주시", "평택시", "포천시", "하남시", "화성시"],
    "강원": ["강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군", "원주시", "인제군", "정선군", "철원군", "춘천시", "태백시", "평창군", "홍천군", "화천군", "횡성군"],
    "충북": ["괴산군", "단양군", "보은군", "영동군", "옥천군", "음성군", "제천시", "증평군", "진천군", "청주시", "충주시"],
    "충남": ["계룡시", "공주시", "금산군", "논산시", "당진시", "보령시", "부여군", "서산시", "서천군", "아산시", "예산군", "천안시", "청양군", "태안군", "홍성군"],
    "전북": ["고창군", "군산시", "김제시", "남원시", "무주군", "부안군", "순창군", "완주군", "익산시", "임실군", "장수군", "전주시", "정읍시", "진안군"],
    "전남": ["강진군", "고흥군", "곡성군", "광양시", "구례군", "나주시", "담양군", "목포시", "무안군", "보성군", "순천시", "신안군", "여수시", "영광군", "영암군", "완도군", "장성군", "장흥군", "진도군", "함평군", "해남군", "화순군"],
    "경북": ["경산시", "경주시", "고령군", "구미시", "김천시", "문경시", "봉화군", "상주시", "성주군", "안동시", "영덕군", "영양군", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군", "청송군", "칠곡군", "포항시"],
    "경남": ["거제시", "거창군", "고성군", "김해시", "남해군", "밀양시", "사천시", "산청군", "양산시", "의령군", "진주시", "창녕군", "창원시", "통영시", "하동군", "함안군", "함양군", "합천군"],
    "제주": ["서귀포시", "제주시"]
}

SIDO_MAP = {
    "서울특별시": "서울", "서울시": "서울", "부산광역시": "부산", "부산시": "부산", "대구광역시": "대구", "대구시": "대구", "인천광역시": "인천", "인천시": "인천", "광주광역시": "광주", "광주시": "광주", "대전광역시": "대전", "대전시": "대전", "울산광역시": "울산", "울산시": "울산", "세종특별자치시": "세종", "세종시": "세종", "경기도": "경기", "강원도": "강원", "강원특별자치도": "강원", "충청북도": "충북", "충청남도": "충남", "전라북도": "전북", "전라북특별자치도": "전북", "전라남도": "전남", "경상북도": "경북", "경상남도": "경남", "제주특별자치도": "제주"
}

def get_core_name(name):
    if not name: return ""
    core = name.split()[-1]
    return re.sub(r'(고등학교|중학교|초등학교|학교)', '', core)

def load_history_db():
    history_dict = {} 
    school_loc_db = {} 
    csv_path = os.path.join(BASE_DIR, "작년도 낙찰자료.csv")
    if not os.path.exists(csv_path): return [], {}
    
    for enc in ['cp949', 'utf-8-sig', 'euc-kr']:
        try:
            with open(csv_path, 'r', encoding=enc) as f:
                reader = csv.DictReader(f)
                last_key = None 
                for row in reader:
                    org_name = row.get('기관명', '').strip()
                    org_loc = row.get('기관소재지', '').strip() 
                    if org_name:
                        core_name = get_core_name(org_name)
                        parts = org_loc.split()
                        if len(parts) >= 2:
                            sido = SIDO_MAP.get(parts[0], parts[0])
                            gugun = parts[1]
                            school_loc_db[core_name] = f"{sido} {gugun}" 
                        bid_title = row.get('입찰공고명', '').strip()
                        last_key = (org_name, bid_title)
                        if last_key not in history_dict:
                            history_dict[last_key] = {'org_name': org_name, 'bid_title': bid_title, 'result': row.get('결과', '').strip(), 'bidders': []}
                    bidder_raw = row.get('참여업체목록', '').strip()
                    if bidder_raw and "총 참여업체" not in bidder_raw and last_key:
                        if "▽" in bidder_raw or "부적격" in bidder_raw:
                            name = bidder_raw.split('/')[0].split('(')[0].strip() if '/' not in bidder_raw else bidder_raw.split('/')[1].split('(')[0].strip()
                            history_dict[last_key]['bidders'].append({'name': name, 'price': '금액없음', 'rate': '', 'rank': '부적격'})
                        else:
                            name = re.sub(r'^\d+\.\s*', '', bidder_raw.split('/')[0].split('(')[0].strip())
                            price_match = re.search(r'([\d,]+원)', bidder_raw)
                            rate_match = re.search(r'\(([\d.]+%)\)', bidder_raw)
                            rank_match = re.match(r'^(\d+)\.', bidder_raw)
                            history_dict[last_key]['bidders'].append({'name': name, 'price': price_match.group(1) if price_match else "", 'rate': rate_match.group(1) if rate_match else "", 'rank': rank_match.group(1) if rank_match else "?"})
            return list(history_dict.values()), school_loc_db
        except: continue
    return [], {}

GLOBAL_HISTORY_DB, SCHOOL_LOC_DB = load_history_db()

MANUAL_SCHOOL_LOC = {
    "대곡": "경남 진주시",
    "서울디지털콘텐츠": "서울 강서구"
}

def fetch_nara_data(user_info):
    selected_regions = user_info.get('regions', [])
    is_master = user_info.get('is_master', False)
    
    json_path = os.path.join(BASE_DIR, "latest_bids.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            items = json.load(f)
    except: return {}, [], [], 0

    filtered = []
    unique_dates = set()
    unique_regions = set()
    
    for item in items:
        api_core = get_core_name(item.get('school', ''))
        api_region = item.get('region', '')
        
        exact_location = SCHOOL_LOC_DB.get(api_core)
        
        if exact_location:
            db_sido = exact_location.split()[0]
            if db_sido not in api_region and api_region not in db_sido:
                exact_location = None
                
        if MANUAL_SCHOOL_LOC.get(api_core):
            exact_location = MANUAL_SCHOOL_LOC.get(api_core)
        
        is_my_region = False
        
        if is_master:
            is_my_region = True
            matched_group_name = exact_location if exact_location else "기타 (신규/미분류 학교)"
        else:
            matched_group_name = "기타 (신규/미분류 학교)"
            if exact_location:
                sido = exact_location.split()[0]
                sido_all_keyword = f"{sido} 전체"
                
                if sido_all_keyword in selected_regions:
                    is_my_region = True
                    matched_group_name = sido_all_keyword
                elif exact_location in selected_regions:
                    is_my_region = True
                    matched_group_name = exact_location
            else:
                is_my_region = True
        
        if is_my_region:
            item['matched_sido'] = matched_group_name
            if matched_group_name != "기타 (신규/미분류 학교)":
                unique_regions.add(matched_group_name)
                
            item['fmt_date'] = item.get('reg', '')
            item['fmt_deadline'] = item.get('end', '')
            date_str = item.get('reg', '')[5:10] if "-" in item.get('reg', '') else "기타"
            item['filter_date'] = date_str
            if date_str != "기타": unique_dates.add(date_str)
            
            d_val = str(item.get('d_day', ''))
            if d_val.isdigit() or (d_val.startswith('-') and d_val[1:].isdigit()):
                val = int(d_val)
                item['d_day'] = f"[D-{val}일]" if val > 0 else ("[D-Day]" if val == 0 else "[마감]")
            else: item['d_day'] = f"[{d_val}]"
            
            if exact_location:
                for db in GLOBAL_HISTORY_DB:
                    if (api_core in db['bid_title'] or api_core in db['org_name']):
                        current_kw = item.get('matched_kw', '')
                        if current_kw == '교복' and '체육복' in db['bid_title']: continue
                        if current_kw != '교복' and current_kw not in db['bid_title']: continue
                        item['history'] = db
                        break
            filtered.append(item)
            
    grouped_data = {}
    total_count = len(filtered)
    for item in filtered:
        group = item['matched_sido']
        if group not in grouped_data: grouped_data[group] = []
        grouped_data[group].append(item)
    
    sorted_groups = sorted(grouped_data.items(), key=lambda x: (1 if "기타" in x[0] else (0 if "전체" in x[0] else 0.5), x[0]))
    
    if is_master:
        sido_counts = {}
        has_gita = False
        for grp, items_in_grp in grouped_data.items():
            if "기타" in grp:
                has_gita = True
                sido_counts["기타"] = sido_counts.get("기타", 0) + len(items_in_grp)
            else:
                sido = grp.split()[0]
                sido_counts[sido] = sido_counts.get(sido, 0) + len(items_in_grp)
        
        available_filters = []
        for r in sorted(list(sido_counts.keys())):
            if r != "기타":
                available_filters.append({"name": r, "count": sido_counts[r]})
        if has_gita:
            available_filters.append({"name": "기타", "count": sido_counts["기타"]})
    else:
        available_filters = selected_regions
    
    return dict(sorted_groups), sorted(list(unique_dates), reverse=True), available_filters, total_count

def send_sms(to_number, content):
    if not to_number or not SOLAR_API_KEY: return
    clean_to = to_number.replace("-", "").strip()
    date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    salt = str(uuid.uuid1().hex)
    data = date + salt
    signature = hmac.new(SOLAR_API_SECRET.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest()
    auth = f'HMAC-SHA256 apiKey={SOLAR_API_KEY}, date={date}, salt={salt}, signature={signature}'
    headers = { 'Authorization': auth, 'Content-Type': 'application/json' }
    payload = { "message": { "to": clean_to, "from": SENDER_NUMBER, "text": content } }
    try: requests.post("https://api.solapi.com/messages/v4/send", headers=headers, json=payload)
    except Exception as e: print(f"SMS 발송 실패: {e}")

def notification_scheduler():
    while True:
        now_str = datetime.now().strftime("%H:%M")
        
        if now_str == "19:00":
            try:
                print("🚀 [19:00] 신규 공고 수집 자동 시작...")
                make_db.fetch_and_save()  
                print("✅ 수집 완료!")
                time.sleep(61) 
            except Exception as e:
                print(f"수집 에러: {e}")

        elif now_str in ["09:00", "15:00"]:
            try:
                sheet, _, _ = get_sheets()
                records = sheet.get_all_values()[1:]
                try: 
                    with open("latest_bids.json", "r", encoding="utf-8") as f: total_count = len(json.load(f))
                except: total_count = 0
                
                msg = f"[입찰반장] 사장님! 신규 공고가 업데이트 되었습니다. (전국 총 {total_count}건)\n지금 바로 확인하세요 👉 {SITE_URL}"
                
                for row in records:
                    if len(row) > 5 and row[5].strip() == now_str: 
                        send_sms(row[2].strip(), msg)
                        time.sleep(0.2) 
                time.sleep(61) 
            except Exception as e: 
                print(f"스케줄러 오류: {e}")
                
        time.sleep(30)


# ==========================================
# 🎨 [디자인 전면 개편] 타이틀 확대 & 좌우 50:50 콤팩트 컨트롤 패널
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>우리동네 입찰반장</title>
    <style>
        * { box-sizing: border-box; } 
        body { font-family: 'Malgun Gothic', sans-serif; background: #f4f7f9; padding: 0; color: #334155; margin: 0; }
        .container { max-width: 1000px; margin: 0 auto; padding: 0 20px 20px 20px; }
        
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 2000; padding: 20px; box-sizing: border-box; }
        .modal-content { background: #ffffff; padding: 20px; border-radius: 15px; max-width: 360px; width: 100%; box-shadow: 0 10px 25px rgba(0,0,0,0.15); }
        .modal-header { font-size: 1.2em; font-weight: 900; color: #075985; margin-bottom: 12px; text-align: center; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px; }
        .modal-body { font-size: 0.95em; color: #475569; line-height: 1.5; max-height: 40vh; overflow-y: auto; margin-bottom: 15px; word-break: keep-all; }
        .modal-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }
        .close-btn { background: #0f172a; color: white; border: none; padding: 8px 16px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s; }

        .landing-wrapper { max-width: 700px; margin: 40px auto; background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); overflow: hidden; border: 1px solid #e2e8f0; }
        .landing-header { background: linear-gradient(135deg, #075985 0%, #0369a1 100%); color: white; padding: 40px 20px; text-align: center; position: relative; }
        .landing-icon { font-size: 4em; margin-bottom: 10px; }
        .landing-title { font-size: 2.8em; font-weight: 900; margin: 0; letter-spacing: -1px; word-break: keep-all; }
        .landing-subtitle { font-size: 1.2em; color: #bae6fd; margin-top: 10px; word-break: keep-all; }
        .landing-body { padding: 40px 30px; background: #ffffff; }
        .greeting { font-size: 1.5em; font-weight: bold; color: #0f172a; margin-top: 0; text-align: center; }
        .pain-point { font-size: 1.25em; color: #e11d48; font-weight: bold; text-align: center; margin-bottom: 30px; background: #fff1f2; padding: 15px; border-radius: 10px; word-break: keep-all;}
        .feature-list { display: flex; flex-direction: column; gap: 20px; }
        .feature-item { display: flex; align-items: flex-start; gap: 15px; background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
        .feature-icon { font-size: 2em; line-height: 1; }
        .feature-text h4 { margin: 0 0 5px 0; color: #075985; font-size: 1.15em; }
        .feature-text p { margin: 0; color: #475569; line-height: 1.5; word-break: keep-all; }
        .landing-footer { padding: 30px; text-align: center; background: #f1f5f9; border-top: 1px solid #e2e8f0; }
        .kakao-btn { display: inline-flex; align-items: center; justify-content: center; background: #FEE500; color: #000000; font-weight: 900; font-size: 1.3em; padding: 18px 40px; border-radius: 30px; text-decoration: none; width: 100%; max-width: 400px; box-sizing: border-box; }

        .setup-section { background: white; border: 2px solid #e2e8f0; padding: 40px; border-radius: 15px; margin-top: 40px; max-width: 600px; margin-left: auto; margin-right: auto; text-align: center; }
        .setup-greeting { background: #f0fdfa; border-left: 5px solid #0d9488; padding: 15px; margin-bottom: 25px; border-radius: 5px; color: #0f766e; font-size: 0.95em; line-height: 1.5; font-weight: bold; word-break: keep-all; }
        .form-group { margin-bottom: 20px; text-align: left; }
        .form-group label { display: block; font-weight: bold; margin-bottom: 8px; color: #0f172a;}
        .form-group input[type="text"], .form-group select { width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px; box-sizing: border-box; font-size: 1em; }
        .gugun-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 8px; margin-top: 10px; }
        .gugun-item { background: #f8fafc; border: 1px solid #cbd5e1; padding: 10px; border-radius: 10px; text-align: center; cursor: pointer; font-size: 0.9em; }
        .gugun-item.selected { background: #075985; color: white; font-weight: bold; }
        input[type="checkbox"] { display: none; }
        .radio-group { display: flex; gap: 15px; margin-top: 15px; justify-content: center; background: #e0f2fe; padding: 15px; border-radius: 8px; border: 1px solid #bae6fd; }
        #save-btn:disabled { background: #cbd5e1 !important; color: #94a3b8 !important; cursor: not-allowed; }

        /* 🔥 [핵심 수정] 새로운 메인 헤더 & 컨트롤 패널 CSS */
        .header { background: #075985; color: white; padding: 15px 20px; border-radius: 0 0 15px 15px; position: sticky; top: 0; z-index: 100; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
        .main-title { font-size: 2.0em; font-weight: 900; margin: 0 0 15px 0; letter-spacing: -1px; text-align: center; }
        .membership-badge { font-size: 0.4em; background: #10b981; color: white; padding: 4px 10px; border-radius: 20px; vertical-align: middle; margin-left: 5px; transform: translateY(-3px); display: inline-block; }
        .membership-badge.vip { background: #e11d48; }
        
        .control-panel { display: flex; gap: 10px; margin-bottom: 12px; align-items: stretch; }
        .control-left { flex: 1; background: rgba(255,255,255,0.08); padding: 15px 12px; border-radius: 12px; display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(255,255,255,0.1); }
        .control-right { flex: 1; background: rgba(255,255,255,0.08); padding: 12px; border-radius: 12px; display: flex; flex-direction: column; justify-content: center; gap: 6px; border: 1px solid rgba(255,255,255,0.1); }

        .region-select { width: 100%; height: 100%; min-height: 50px; padding: 10px 5px; border-radius: 8px; border: none; font-size: 1.05em; font-weight: bold; color: #0f172a; cursor: pointer; text-align: center; outline: none; }
        .util-btn { text-align: center; text-decoration: none; padding: 7px; border-radius: 6px; font-size: 0.8em; font-weight: bold; display: block; }
        .btn-kakao { background: #0284c7; color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        .btn-logout { background: transparent; color: #fca5a5; border: 1px solid rgba(252, 165, 165, 0.4); }
        .time-select-box { padding: 6px; border-radius: 6px; border: 1px solid #38bdf8; font-size: 0.8em; text-align: center; background: #1e293b; color: #38bdf8; outline: none; width: 100%; }
        
        .date-filter-bar { margin-top: 10px; background: #0c4a6e; padding: 8px; border-radius: 8px; display: flex; justify-content: center; flex-wrap: wrap; gap: 4px; }
        .date-btn { cursor: pointer; background: transparent; color: #bae6fd; border: 1px solid transparent; padding: 4px 10px; border-radius: 15px; font-size: 0.8em; }
        .date-btn.active { background: #bae6fd; color: #075985; font-weight: bold; }

        .card { display: flex; justify-content: space-between; background: white; border-radius: 10px; padding: 15px; margin-bottom: 15px; border: 1px solid #e2e8f0; border-left: 5px solid #0284c7; }
        .card-left { flex: 1; }
        .card-right { width: 360px; background: #fff1f2; padding: 14px; border-radius: 8px; font-size: 0.85em; flex-shrink: 0; }
        .hist-header { font-weight: bold; color: #be123c; border-bottom: 1px solid #fda4af; padding-bottom: 5px; margin-bottom: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        .empty-state { display: flex; flex-direction: column; justify-content: center; align-items: center; text-align:center; padding: 60px 20px; background: white; border-radius: 15px; border: 2px dashed #cbd5e1; margin: 30px auto; max-width: 700px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
        .empty-icon { font-size: 5em; margin-bottom: 20px; animation: float 3s ease-in-out infinite; }

        @media (max-width: 768px) {
            .container { padding: 0 8px 15px 8px; }
            .header { padding: 15px 10px; }
            .main-title { font-size: 1.6em; margin-bottom: 10px; }
            .control-panel { gap: 6px; }
            .control-left, .control-right { padding: 10px; border-radius: 10px; }
            .region-select { font-size: 0.95em; padding: 8px 4px; min-height: 40px; }
            .util-btn { padding: 6px; font-size: 0.75em; }
            .time-select-box { font-size: 0.75em; }

            .card { flex-direction: column; padding: 12px; margin-bottom: 10px; }
            .card-left > div:nth-child(1) { font-size: 1.05em !important; }
            .card-left > div:nth-child(2) { font-size: 0.9em !important; margin: 5px 0 !important; }
            .card-left > div:nth-child(3) { font-size: 0.75em !important; }
            .card-left a { padding: 4px 10px !important; font-size: 0.8em !important; margin-top: 8px !important; }
            .card-right { width: 100%; margin-top: 10px; padding: 10px; font-size: 0.75em; }
            .hist-header { white-space: normal; margin-bottom: 5px; font-size: 0.9em; }
        }
    </style>
</head>
<body>
<div class="container">
    
    {% if notice and notice.show %}
    <div id="notice-modal" class="modal-overlay" style="display:none;">
        <div class="modal-content">
            <div class="modal-header">{{ notice.title }}</div>
            <div class="modal-body">{{ notice.content|safe }}</div>
            <div class="modal-footer">
                <label style="cursor:pointer; font-size:0.9em; display:flex; align-items:center; gap:5px; color:#475569; font-weight:bold;">
                    <input type="checkbox" id="hide-month-chk" onchange="if(this.checked) closeNotice(true);"> 한 달 동안 보지 않기
                </label>
                <button class="close-btn" onclick="closeNotice(false)">닫기</button>
            </div>
        </div>
    </div>
    {% endif %}

    {% if not user_info %}
        <div class="landing-wrapper">
            <div class="landing-header">
                <div class="landing-icon">🕵️‍♂️🔍</div>
                <h1 class="landing-title">우리동네 입찰반장</h1>
                <p class="landing-subtitle">B2B 학생복 및 기타복종 입찰공고 실시간 관제소</p>
            </div>
            <div class="landing-body">
                <h3 class="greeting">안녕하세요, 사장님!</h3>
                <p class="pain-point">"매번 나라장터 입찰공고가 올라왔나<br>확인하시느라 힘드셨죠?"</p>
                <div class="feature-list">
                    <div class="feature-item"><div class="feature-icon">🚨</div><div class="feature-text"><h4>단 하나도 놓치지 않는 밀착 관제</h4><p>내가 관리하는 지역의 교복 외 기타복종 공고건들까지 하루 단위로 꼼꼼히 검색하여 전달합니다.</p></div></div>
                    <div class="feature-item"><div class="feature-icon">📈</div><div class="feature-text"><h4>비즈니스 관리 효율 극대화</h4><p>가장 빠른 카카오톡 알림은 물론, 전년도 개찰결과(낙찰가/순위)까지 한 번에 보여드립니다.</p></div></div>
                    <div class="feature-item"><div class="feature-icon">📱</div><div class="feature-text"><h4>이제 내 손안에서 편안하게</h4><p>매번 검색하는 수고로움과 남을 통해 듣던 정보의 불편함을 버리고, 빠르고 편안하게 보고받으세요!</p></div></div>
                </div>
            </div>
            <div class="landing-footer"><a href="/login" class="kakao-btn"><svg class="kakao-svg" viewBox="0 0 24 24" fill="currentColor" style="width:24px;height:24px;margin-right:10px;"><path d="M12 3c-5.52 0-10 3.58-10 8 0 2.85 1.83 5.35 4.54 6.71l-1.16 4.31c-.13.48.42.84.81.56l5.04-3.3c.57.08 1.16.12 1.77.12 5.52 0 10-3.58 10-8s-4.48-8-10-8z"/></svg>카카오톡으로 간편가입하기</a></div>
        </div>

    {% elif user_info.is_new %}
        <div class="setup-section">
            <h2 style="color:#075985;">🚀 입찰반장 신규 등록</h2>
            
            <div class="setup-greeting">
                사장님, 환영합니다! 🎉<br>
                아래 양식을 작성해 주시면, 매일 나라장터에 등록되는 신규 공고를 놓치지 않고 꼼꼼하게 배달해 드리겠습니다.
            </div>
            
            <form action="/save_region" method="POST" id="register-form">
                <div class="form-group"><label>👤 실명</label><input type="text" name="nickname" required placeholder="예) 홍길동" value="{{ user_info.nickname if user_info.nickname != '회원' else '' }}"></div>
                <div class="form-group"><label>📞 연락처 (휴대폰)</label><input type="text" name="phone" required placeholder="예: 01012345678 (하이픈 없이 숫자만 입력)"></div>
                <div class="form-group"><label>🏢 운영 대리점명</label><input type="text" name="agency" required placeholder="예) 스마트학생복 해운대점"></div>
                
                <div class="form-group">
                    <label>⏰ 알림 수신 시간 선택</label>
                    <select name="pref_time">
                        <option value="09:00">오전 9시 (출근길 전일 공고 요약)</option>
                        <option value="15:00">오후 3시 (업무 중 실시간 체크)</option>
                    </select>
                </div>

                <div class="form-group" style="border-top: 1px solid #e2e8f0; padding-top: 20px;">
                    <label>📍 관제 기본 구역 설정 (추후 카톡 문의로 무한 추가 가능)</label>
                    <p id="limit-info" style="color:#0284c7; font-size:0.9em; margin-top:0;">시/도를 선택하면 선택 가능 개수가 표시됩니다.</p>
                    <select id="sido-select" onchange="renderGugun()">
                        <option value="">-- 시/도 선택 --</option>
                        {% for sido in region_data.keys() %} <option value="{{ sido }}">{{ sido }}</option> {% endfor %}
                    </select>
                    <div id="gugun-container" class="gugun-grid"></div>
                </div>
                
                <details class="privacy-accordion">
                    <summary>📜 [필수] 개인정보 수집 및 이용 안내 <span>▼ 펼쳐보기</span></summary>
                    <div class="privacy-content">
                        <strong>1. 수집하는 개인정보 항목</strong><br>- 필수항목: 이름, 휴대전화번호, 운영 대리점명, 관할 지역, 알림시간<br><br>
                        <strong>2. 개인정보의 수집 및 이용 목적</strong><br>- B2B 입찰반장 서비스 제공 및 권한 관리<br>- 카카오톡/문자 알림 서비스 제공<br><br>
                        <strong>3. 개인정보의 보유 및 이용 기간</strong><br>- <strong>회원 탈퇴 시 또는 서비스 종료 시까지 지체 없이 파기합니다.</strong><br>
                    </div>
                </details>
                <div class="radio-group">
                    <label class="radio-label"><input type="radio" name="privacy_agree_radio" value="yes" checked onchange="toggleSubmitBtn()"> 동의합니다</label>
                    <label class="radio-label"><input type="radio" name="privacy_agree_radio" value="no" onchange="toggleSubmitBtn()"> 동의하지 않습니다</label>
                </div>
                <button type="submit" id="save-btn" style="display:none; width:100%; padding:15px; background:#075985; color:white; border:none; border-radius:8px; font-weight:bold; font-size:1.1em; margin-top:30px; cursor:pointer;">입찰반장 시작하기</button>
            </form>
        </div>

    {% else %}
        <div class="header">
            <h1 class="main-title">우리동네 입찰반장 <span class="membership-badge {{ 'vip' if user_info.is_premium else '' }}">{{ user_info.premium_label }}</span></h1>
            
            <div class="control-panel">
                
                <div class="control-left">
                    <div style="font-size: 0.75em; color: #bae6fd; margin-bottom: 5px; font-weight: bold; text-align: center;">📍 지역 필터</div>
                    <select class="region-select" onchange="filterByRegion(this.value, this, true)">
                        <option value="all">전체보기 (총 {{ total_count }}건)</option>
                        {% if user_info.is_master %}
                            {% for r in available_regions %}
                                <option value="{{ r.name }}">{{ r.name }} ({{ r.count }}건)</option>
                            {% endfor %}
                        {% else %}
                            {% for r in available_regions %}
                                {% set r_count = grouped_data[r]|length if r in grouped_data else 0 %}
                                <option value="{{ r }}">{{ r }} ({{ r_count }}건)</option>
                            {% endfor %}
                        {% endif %}
                    </select>
                </div>

                <div class="control-right">
                    <a href="https://open.kakao.com/o/gw03Nkqi" target="_blank" class="util-btn btn-kakao">👑 전국열람/지역추가</a>
                    <select class="time-select-box" onchange="updateTime(this.value)">
                        <option value="09:00" {% if user_info.pref_time == '09:00' %}selected{% endif %}>🔔 09시 알림</option>
                        <option value="15:00" {% if user_info.pref_time == '15:00' %}selected{% endif %}>🔔 15시 알림</option>
                    </select>
                    <a href="/logout" class="util-btn btn-logout">로그아웃</a>
                </div>

            </div>

            {% if sorted_dates %}
            <div class="date-filter-bar">
                <span class="date-btn active" onclick="filterByDate('all', this)">날짜전체</span>
                {% for dt in sorted_dates %} <span class="date-btn" onclick="filterByDate('{{ dt }}', this)">{{ dt }}</span> {% endfor %}
            </div>
            {% endif %}
        </div>

        {% if not grouped_data %}
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <h2 style="color: #0f172a; margin-bottom: 15px; font-size: 1.5em; word-break: keep-all;">현재 우리 동네에 진행 중인 입찰 공고가 없습니다.</h2>
                <p style="color: #475569; line-height: 1.7; font-size: 1.05em; margin-bottom: 0; word-break: keep-all;">
                    나라장터에 신규 공고가 등록되는 즉시,<br>
                    사장님께서 설정하신 <strong style="color: #0284c7; font-size: 1.1em;">[알림 시간: {{ user_info.pref_time }}]</strong>에 맞춰<br>
                    가장 먼저 문자로 보고드리겠습니다!<br><br>
                    <span style="display: inline-block; background: #f0fdfa; color: #0f766e; padding: 8px 15px; border-radius: 20px; font-weight: bold; font-size: 0.9em;">마음 편히 본업에 집중하고 계시면 입찰반장이 다 챙겨드릴게요. 🫡</span>
                </p>
            </div>
        {% endif %}

        {% for region_name, items in grouped_data.items() %}
            <div class="region-group" data-region="{{ region_name }}">
                <div style="font-size: 1.4em; color: #075985; border-left: 6px solid #075985; padding-left: 10px; margin: 35px 0 15px; font-weight: bold;">
                    {{ region_name }} (<span class="region-count">{{ items|length }}</span>건)
                </div>
                <div class="cards-container">
                    {% for item in items %}
                    {% set is_paywalled = (not user_info.is_premium) and (loop.index0 >= 2) %}
                    <div class="card-wrapper bidding-card" data-date="{{ item.filter_date }}" style="position: relative;">
                        <div class="card {{ 'premium-blur' if is_paywalled else '' }}" style="{{ 'filter: blur(6px); pointer-events: none;' if is_paywalled else '' }}">
                            <div class="card-left">
                                <div style="font-weight:bold; font-size:1.15em;">{% if item.is_new %}<span style="background: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin-right: 5px;">신규</span>{% endif %}({{ item.region }}) {{ item.school }}</div>
                                <div style="margin:8px 0; color:#475569; line-height: 1.4;">{{ item.title }}</div>
                                <div style="font-size:0.85em; color:#64748b;">등록: {{ item.fmt_date }} | 마감: {{ item.fmt_deadline }} <span style="color:#e11d48; font-weight:bold;">{{ item.d_day }}</span></div>
                                <a href="{{ item.link }}" target="_blank" style="display: inline-block; background: #075985; color: white; padding: 6px 12px; text-decoration: none; border-radius: 5px; margin-top: 10px; font-size: 0.9em;">상세보기</a>
                            </div>
                            <div class="card-right">
                                <div class="hist-header">
                                    📊 25년 입찰 이력 <span style="font-size:0.8em; color:#ef4444; font-weight:normal; margin-left:3px;">(중요 학교는 나라장터 교차검증)</span>
                                </div>
                                
                                {% if item.history %}
                                    {% for b in item.history.bidders[:3] %}
                                    <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                                        <span>{{ '🏆낙찰' if b.rank=='1' and item.history.result=='낙찰' else b.rank+'등' }} {{ b.name }}</span>
                                        <span>{{ b.price }}</span>
                                    </div>
                                    {% endfor %}
                                {% else %}<div style="color:#94a3b8; text-align:center; padding-top:10px; font-weight:bold;">정보 없음</div>{% endif %}
                            </div>
                        </div>
                        {% if is_paywalled %}
                        <div class="paywall-overlay">
                            <div style="font-size: 2.5em; margin-bottom: 5px;">🔒</div>
                            <div style="font-size: 1.1em; font-weight:bold; color:#0f172a; margin-bottom: 10px;">이 지역의 3번째 공고부터는<br>VIP회원 전용입니다.</div>
                            <button class="upgrade-btn" onclick="window.open('https://open.kakao.com/o/gw03Nkqi', '_blank')">VIP회원 구독하고 전체 보기</button>
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
        {% endfor %}
    {% endif %}
</div>

<script>
    document.addEventListener("DOMContentLoaded", function() {
        const noticeModal = document.getElementById('notice-modal');
        if(noticeModal) {
            const hideUntil = localStorage.getItem('hideNoticeUntil_v13');
            const sessionHidden = sessionStorage.getItem('sessionNoticeHidden');
            const now = new Date().getTime();
            if((!hideUntil || now > parseInt(hideUntil)) && !sessionHidden) {
                noticeModal.style.display = 'flex';
            }
        }
    });

    function closeNotice(isPermanent) {
        if(isPermanent) {
            const oneMonth = 30 * 24 * 60 * 60 * 1000; 
            localStorage.setItem('hideNoticeUntil_v13', new Date().getTime() + oneMonth);
        } else {
            sessionStorage.setItem('sessionNoticeHidden', 'true');
        }
        document.getElementById('notice-modal').style.display = 'none';
    }

    function updateTime(newTime) {
        fetch('/update_time', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ time: newTime })
        }).then(res => res.json()).then(data => {
            if(data.status === 'success') {
                alert('알람 수신 시간이 [' + newTime + ']으로 변경되었습니다!');
            } else {
                alert('시간 변경에 실패했습니다. 관리자에게 문의해주세요.');
            }
        });
    }

    const regionData = {{ region_data | tojson | safe if region_data else '{}' }};
    let count = 0; let maxLimit = 1;
    let activeDate = 'all'; let activeRegion = 'all';

    function toggleSubmitBtn() {
        const isAgreed = document.querySelector('input[name="privacy_agree_radio"]:checked').value === 'yes';
        const btn = document.getElementById("save-btn");
        btn.disabled = !isAgreed;
        btn.textContent = isAgreed ? "입찰반장 시작하기" : "약관에 동의해주세요";
    }

    function renderGugun() {
        const sido = document.getElementById("sido-select").value;
        const box = document.getElementById("gugun-container");
        if(!box) return;
        box.innerHTML = ""; count = 0;
        if(!sido) { document.getElementById("save-btn").style.display="none"; return; }
        maxLimit = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종"].includes(sido) ? 4 : 1;
        document.getElementById("limit-info").textContent = `${sido} 지역은 최대 ${maxLimit}개 구/군까지 선택 가능합니다.`;
        document.getElementById("save-btn").style.display="block";
        if(regionData[sido]){
            regionData[sido].forEach(g => {
                const label = document.createElement("label"); label.className = "gugun-item";
                const chk = document.createElement("input"); chk.type = "checkbox"; chk.name = "gugun_list"; chk.value = sido + " " + g;
                chk.onchange = function() {
                    if(this.checked) {
                        if(count >= maxLimit) { alert(`이 지역은 최대 ${maxLimit}개만 선택 가능합니다!`); this.checked = false; return; }
                        count++; label.classList.add("selected");
                    } else { count--; label.classList.remove("selected"); }
                };
                label.appendChild(chk); label.appendChild(document.createTextNode(g)); box.appendChild(label);
            });
        }
    }

    function filterByDate(date, el) {
        document.querySelectorAll('.date-btn').forEach(b => b.classList.remove('active'));
        el.classList.add('active'); activeDate = date; applyFilters();
    }
    
    function filterByRegion(region, el, isSelect=false) {
        activeRegion = region;
        applyFilters();
    }
    
    function applyFilters() {
        const isMaster = {{ 'true' if user_info and user_info.is_master else 'false' }};
        
        document.querySelectorAll('.region-group').forEach(group => {
            let groupRegion = group.getAttribute('data-region');
            let regionMatch = false;

            if (activeRegion === 'all') {
                regionMatch = true;
            } else if (isMaster) {
                if (activeRegion === '기타') {
                    regionMatch = groupRegion.includes('기타');
                } else {
                    regionMatch = groupRegion.startsWith(activeRegion);
                }
            } else {
                if (activeRegion.endsWith(' 전체')) {
                    let sido = activeRegion.split(' ')[0];
                    regionMatch = groupRegion.startsWith(sido);
                } else {
                    regionMatch = (groupRegion === activeRegion);
                }
            }

            let visibleCount = 0;
            group.querySelectorAll('.bidding-card').forEach(card => {
                let dateMatch = (activeDate === 'all' || card.getAttribute('data-date') === activeDate);
                if (regionMatch && dateMatch) { card.style.display = 'block'; visibleCount++; }
                else { card.style.display = 'none'; }
            });
            group.style.display = (visibleCount > 0) ? 'block' : 'none';
            if(visibleCount > 0) group.querySelector('.region-count').textContent = visibleCount;
        });
    }
</script>
</body>
</html>
"""

@app.route("/")
def index():
    user = session.get("user")
    
    if user and not user.get('is_new'):
        updated_user = sync_user_from_sheet(user['id'], user['nickname'])
        if not updated_user.get('is_new'):
            session["user"] = updated_user
            user = updated_user
            
    grouped_data, sorted_dates, available_regions, total_count = ({}, [], [], 0)
    
    if user and (user.get('is_master') or user.get('regions')):
        grouped_data, sorted_dates, available_regions, total_count = fetch_nara_data(user)
    
    notice_data = get_live_notice()
        
    return render_template_string(HTML_TEMPLATE, user_info=user, region_data=REGION_DATA, grouped_data=grouped_data, sorted_dates=sorted_dates, available_regions=available_regions, total_count=total_count, notice=notice_data)

@app.route("/login")
def login(): return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code")

@app.route("/oauth/kakao/callback")
def kakao_callback():
    code = request.args.get("code")
    token_res = requests.post("https://kauth.kakao.com/oauth/token", data={"grant_type":"authorization_code", "client_id":KAKAO_CLIENT_ID, "client_secret":KAKAO_CLIENT_SECRET, "redirect_uri":REDIRECT_URI, "code":code}).json()
    user_res = requests.get("https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {token_res.get('access_token')}"}).json()
    
    session.permanent = True 
    session["user"] = sync_user_from_sheet(str(user_res.get("id")), user_res.get("kakao_account", {}).get("profile", {}).get("nickname", "회원"))
    return redirect("/")

@app.route("/save_region", methods=["POST"])
def save_region():
    if "user" not in session: return redirect("/")
    
    session.permanent = True 
    u = session["user"]
    nickname, phone, agency = request.form.get("nickname"), request.form.get("phone"), request.form.get("agency")
    
    pref_time = request.form.get("pref_time", "09:00")
    selected = request.form.getlist("gugun_list")
    
    try:
        main_sheet, consent_sheet, _ = get_sheets()
        
        raw_ids = main_sheet.col_values(1)
        clean_ids = [str(x).replace("'", "").replace('"', "").strip() for x in raw_ids]
        kid_str = str(u["id"]).replace("'", "").replace('"', "").strip()
        
        if kid_str in clean_ids:
            row = clean_ids.index(kid_str) + 1
            main_sheet.update_cell(row, 2, nickname)
            main_sheet.update_cell(row, 3, phone)
            main_sheet.update_cell(row, 4, agency)
            main_sheet.update_cell(row, 5, ",".join(selected))
            main_sheet.update_cell(row, 6, pref_time)
        else:
            main_sheet.append_row([str(u["id"]), nickname, phone, agency, ",".join(selected), pref_time, "무료", "2026-12-31", "Y"])
            consent_sheet.append_row([str(u["id"]), nickname, phone, agency, "v1.0", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            
            try: 
                with open("latest_bids.json", "r", encoding="utf-8") as f: total_bids = len(json.load(f))
            except: total_bids = 0
            welcome_msg = f"[우리동네 입찰반장] 가입 완료! 오늘 전국에 등록된 공고는 총 {total_bids}건입니다. 사장님 지역 공고는 매일 [{pref_time}]에 배달됩니다! 👉 {SITE_URL}"
            send_sms(phone, welcome_msg)
            
    except Exception as e: print(f"저장 에러: {e}")
    
    session["user"] = sync_user_from_sheet(u["id"], nickname)
    return redirect("/")

@app.route("/update_time", methods=["POST"])
def update_time():
    if "user" not in session: return jsonify({"status": "error"}), 401
    u = session["user"]
    new_time = request.json.get("time")
    
    try:
        main_sheet, _, _ = get_sheets()
        raw_ids = main_sheet.col_values(1)
        clean_ids = [str(x).replace("'", "").replace('"', "").strip() for x in raw_ids]
        
        if u["id"] in clean_ids:
            row = clean_ids.index(u["id"]) + 1
            main_sheet.update_cell(row, 6, new_time) 
            u["pref_time"] = new_time
            session["user"] = u
            return jsonify({"status": "success"})
    except Exception as e:
        print(e)
    return jsonify({"status": "error"}), 500

@app.route("/logout")
def logout(): session.clear(); return redirect("/")

if __name__ == "__main__":
    threading.Thread(target=notification_scheduler, daemon=True).start()
    app.run(port=5000, debug=False)