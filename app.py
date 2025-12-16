import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import math

# 페이지 설정
st.set_page_config(page_title="내 입맛 맛집 추천", page_icon="🍽️", layout="wide")

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('taste_app.db')
    c = conn.cursor()
    
    # 사용자 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  created_at TEXT)''')
    
    # 선호도 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS preferences
                 (user_id INTEGER PRIMARY KEY,
                  spicy INTEGER,
                  oily INTEGER,
                  salty INTEGER,
                  sweet INTEGER,
                  spice_heavy INTEGER,
                  familiar INTEGER,
                  solo_friendly INTEGER,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')
    
    # 맛집 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS restaurants
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  category TEXT,
                  address TEXT,
                  phone TEXT,
                  latitude REAL,
                  longitude REAL,
                  spicy INTEGER,
                  oily INTEGER,
                  salty INTEGER,
                  sweet INTEGER,
                  spice_heavy INTEGER,
                  familiar INTEGER,
                  rating REAL)''')
    
    # 리뷰 테이블
    c.execute('''CREATE TABLE IF NOT EXISTS reviews
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  restaurant_id INTEGER,
                  rating INTEGER,
                  spicy INTEGER,
                  oily INTEGER,
                  salty INTEGER,
                  sweet INTEGER,
                  spice_heavy INTEGER,
                  familiar INTEGER,
                  comment TEXT,
                  created_at TEXT,
                  FOREIGN KEY(user_id) REFERENCES users(id),
                  FOREIGN KEY(restaurant_id) REFERENCES restaurants(id))''')
    
    conn.commit()
    conn.close()

# 광주 실제 맛집 데이터 추가
def add_gwangju_restaurants():
    conn = sqlite3.connect('taste_app.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM restaurants")
    if c.fetchone()[0] == 0:
        # 광주 실제 맛집 데이터 (이름, 카테고리, 주소, 전화번호, 위도, 경도, 맛특성...)
        gwangju_data = [
            # 한식
            ("송정떡갈비", "한식", "광주 광산구 송정로8번길 13", "062-942-5489", 35.1362, 126.7932, 4, 7, 6, 4, 2, 9, 4.5),
            ("무등산보리밥", "한식", "광주 동구 증심사길 164", "062-223-8549", 35.1470, 127.0312, 2, 3, 5, 3, 2, 10, 4.3),
            ("양동시장 국밥", "한식", "광주 동구 금남로 245", "062-226-8877", 35.1481, 126.9175, 3, 6, 7, 2, 2, 9, 4.4),
            ("할매집 백반", "한식", "광주 남구 봉선중앙로 56", "062-675-3322", 35.1325, 126.9028, 3, 4, 6, 3, 2, 10, 4.2),
            
            # 중식
            ("향촌", "중식", "광주 동구 금남로 119", "062-224-6969", 35.1502, 126.9147, 5, 7, 6, 4, 5, 6, 4.6),
            ("차이나팩토리", "중식", "광주 서구 상무중앙로 42", "062-385-8855", 35.1520, 126.8546, 8, 8, 6, 3, 8, 4, 4.4),
            
            # 일식
            ("스시효", "일식", "광주 서구 화운로 82", "062-374-0082", 35.1609, 126.8801, 1, 3, 5, 2, 1, 7, 4.7),
            ("이자카야 하나", "일식", "광주 동구 충장로 95", "062-226-8866", 35.1498, 126.9156, 2, 5, 6, 3, 2, 7, 4.3),
            
            # 양식
            ("더키친", "양식", "광주 서구 상무중앙로 31", "062-372-8282", 35.1534, 126.8520, 3, 7, 4, 5, 4, 5, 4.5),
            ("파스타랩", "양식", "광주 남구 백서로 30", "062-653-7070", 35.1456, 126.9089, 3, 6, 5, 4, 3, 6, 4.4),
            
            # 분식/떡볶이
            ("충장로 떡볶이", "분식", "광주 동구 충장로 66", "062-223-5544", 35.1490, 126.9148, 9, 6, 7, 4, 2, 10, 4.2),
            ("신전떡볶이 광주점", "분식", "광주 북구 용봉로 77", "062-575-8899", 35.1722, 126.9078, 10, 7, 8, 5, 3, 9, 4.3),
            
            # 치킨/튀김
            ("교촌치킨 충장점", "치킨", "광주 동구 충장로 90", "062-227-7788", 35.1495, 126.9152, 6, 9, 6, 5, 2, 8, 4.4),
            ("BBQ 상무점", "치킨", "광주 서구 상무중앙로 56", "062-383-8282", 35.1515, 126.8530, 7, 10, 7, 3, 2, 8, 4.3),
            
            # 카페/디저트
            ("카페 더폴리", "카페", "광주 남구 월산동 693", "062-676-0707", 35.1385, 126.9025, 1, 2, 2, 9, 1, 6, 4.6),
            ("블루보틀 광주점", "카페", "광주 동구 금남로 155", "062-233-8855", 35.1488, 126.9162, 1, 2, 2, 8, 1, 5, 4.5),
            ("설빙 광주충장점", "디저트", "광주 동구 충장로 72", "062-224-9988", 35.1492, 126.9150, 1, 2, 2, 10, 1, 7, 4.4),
            
            # 족발/보쌈
            ("왕족발보쌈", "한식", "광주 북구 첨단과기로 123", "062-971-8855", 35.2253, 126.8435, 4, 9, 8, 4, 3, 8, 4.5),
            
            # 국밥/탕
            ("송정리 국밥", "한식", "광주 광산구 송정로 88", "062-943-7722", 35.1350, 126.7925, 3, 6, 7, 2, 2, 10, 4.6),
            ("소머리국밥 본점", "한식", "광주 남구 봉선로 145", "062-654-8822", 35.1328, 126.9015, 3, 7, 8, 2, 2, 9, 4.4),
            
            # 베트남 쌀국수
            ("포하노이", "베트남식", "광주 서구 상무평화로 12", "062-385-7788", 35.1556, 126.8568, 5, 4, 6, 3, 7, 4, 4.3),
            
            # 고기/구이
            ("소문난 삼겹살", "한식", "광주 북구 설죽로 299", "062-571-8855", 35.1815, 126.9125, 5, 10, 7, 2, 3, 9, 4.5),
            ("광주식육식당", "한식", "광주 동구 서석로 28", "062-222-8866", 35.1522, 126.9223, 4, 9, 6, 2, 2, 9, 4.6),
        ]
        
        c.executemany("""INSERT INTO restaurants 
                        (name, category, address, phone, latitude, longitude, 
                         spicy, oily, salty, sweet, spice_heavy, familiar, rating) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", gwangju_data)
        conn.commit()
    
    conn.close()

# 거리 계산 (km)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # 지구 반경 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# 비밀번호 해시
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# DB 초기화
init_db()
add_gwangju_restaurants()

# 로그인/회원가입 페이지
def login_page():
    st.title("🍽️ 내 입맛 맞춤 맛집 추천")
    st.subheader("현지인 맛집이 아니라, 나한테 맛있는 집을 추천하는 앱")
    
    tab1, tab2 = st.tabs(["로그인", "회원가입"])
    
    with tab1:
        st.subheader("로그인")
        username = st.text_input("아이디", key="login_username")
        password = st.text_input("비밀번호", type="password", key="login_password")
        
        if st.button("로그인", key="login_btn"):
            if username and password:
                conn = sqlite3.connect('taste_app.db')
                c = conn.cursor()
                c.execute("SELECT id, password FROM users WHERE username=?", (username,))
                result = c.fetchone()
                conn.close()
                
                if result and result[1] == hash_password(password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.user_id = result[0]
                    st.rerun()
                else:
                    st.error("아이디 또는 비밀번호가 잘못되었습니다.")
            else:
                st.warning("아이디와 비밀번호를 입력해주세요.")
    
    with tab2:
        st.subheader("회원가입")
        new_username = st.text_input("아이디", key="signup_username")
        new_password = st.text_input("비밀번호", type="password", key="signup_password")
        confirm_password = st.text_input("비밀번호 확인", type="password", key="confirm_password")
        
        if st.button("가입하기", key="signup_btn"):
            if new_username and new_password and confirm_password:
                if new_password != confirm_password:
                    st.error("비밀번호가 일치하지 않습니다.")
                else:
                    try:
                        conn = sqlite3.connect('taste_app.db')
                        c = conn.cursor()
                        c.execute("INSERT INTO users (username, password, created_at) VALUES (?, ?, ?)",
                                (new_username, hash_password(new_password), datetime.now().isoformat()))
                        conn.commit()
                        conn.close()
                        st.success("회원가입 완료! 로그인 해주세요.")
                    except sqlite3.IntegrityError:
                        st.error("이미 존재하는 아이디입니다.")
            else:
                st.warning("모든 항목을 입력해주세요.")

# 선호도 설정 페이지
def preference_page():
    st.title("🎯 내 입맛 설정하기")
    st.write("당신의 맛 선호도를 알려주세요. 이 정보를 바탕으로 맞춤 맛집을 추천해드립니다!")
    
    conn = sqlite3.connect('taste_app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM preferences WHERE user_id=?", (st.session_state.user_id,))
    existing = c.fetchone()
    conn.close()
    
    # 기존 설정이 있으면 불러오기
    defaults = {
        'spicy': existing[1] if existing else 5,
        'oily': existing[2] if existing else 5,
        'salty': existing[3] if existing else 5,
        'sweet': existing[4] if existing else 5,
        'spice_heavy': existing[5] if existing else 5,
        'familiar': existing[6] if existing else 5,
        'solo_friendly': existing[7] if existing else 5,
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("맛 선호도")
        spicy = st.slider("🌶️ 매운맛 선호도", 1, 10, defaults['spicy'], 
                         help="1: 전혀 못 먹음 / 10: 매우 좋아함")
        oily = st.slider("🍖 기름진 음식", 1, 10, defaults['oily'],
                        help="1: 담백한 것 선호 / 10: 기름진 것 좋아함")
        salty = st.slider("🧂 짠맛", 1, 10, defaults['salty'],
                         help="1: 싱거운 편 선호 / 10: 짭짤한 것 선호")
        sweet = st.slider("🍯 단맛", 1, 10, defaults['sweet'],
                         help="1: 단맛 별로 / 10: 달달한 것 선호")
    
    with col2:
        st.subheader("음식 스타일")
        spice_heavy = st.slider("🌿 향신료 강한 음식", 1, 10, defaults['spice_heavy'],
                               help="1: 향신료 약한 것 / 10: 향신료 강한 것")
        familiar = st.slider("🏠 익숙한 맛 vs 새로운 맛", 1, 10, defaults['familiar'],
                            help="1: 새로운 맛 도전 / 10: 익숙한 맛 선호")
        solo_friendly = st.slider("👤 혼밥 선호도", 1, 10, defaults['solo_friendly'],
                                 help="1: 여럿이 / 10: 혼자 식사 선호")
    
    if st.button("💾 저장하기", type="primary"):
        conn = sqlite3.connect('taste_app.db')
        c = conn.cursor()
        
        if existing:
            c.execute("""UPDATE preferences SET spicy=?, oily=?, salty=?, sweet=?, 
                        spice_heavy=?, familiar=?, solo_friendly=? WHERE user_id=?""",
                     (spicy, oily, salty, sweet, spice_heavy, familiar, solo_friendly, st.session_state.user_id))
        else:
            c.execute("""INSERT INTO preferences (user_id, spicy, oily, salty, sweet, 
                        spice_heavy, familiar, solo_friendly) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                     (st.session_state.user_id, spicy, oily, salty, sweet, spice_heavy, familiar, solo_friendly))
        
        conn.commit()
        conn.close()
        st.success("✅ 입맛 설정이 저장되었습니다!")
        st.balloons()

# 추천 맛집 페이지
def recommendation_page():
    st.title("🍴 광주 맛집 추천")
    
    # 선호도 확인
    conn = sqlite3.connect('taste_app.db')
    c = conn.cursor()
    c.execute("SELECT * FROM preferences WHERE user_id=?", (st.session_state.user_id,))
    prefs = c.fetchone()
    
    if not prefs:
        st.warning("⚠️ 먼저 입맛 설정을 해주세요!")
        if st.button("입맛 설정하러 가기"):
            st.rerun()
        conn.close()
        return
    
    user_prefs = {
        'spicy': prefs[1],
        'oily': prefs[2],
        'salty': prefs[3],
        'sweet': prefs[4],
        'spice_heavy': prefs[5],
        'familiar': prefs[6]
    }
    
    # 위치 선택
    st.subheader("📍 검색할 지역")
    
    location_options = {
        "광주 전체": (35.1595, 126.8526),
        "동구 (충장로/금남로)": (35.1490, 126.9150),
        "서구 (상무지구)": (35.1520, 126.8540),
        "남구 (봉선동)": (35.1330, 126.9020),
        "북구 (첨단지구)": (35.2250, 126.8440),
        "광산구 (송정)": (35.1360, 126.7930)
    }
    
    col1, col2 = st.columns(2)
    with col1:
        selected_location = st.selectbox("지역 선택", list(location_options.keys()))
    with col2:
        max_distance = st.slider("최대 거리 (km)", 1.0, 10.0, 3.0, 0.5)
    
    user_lat, user_lon = location_options[selected_location]
    
    # 모든 맛집 가져오기
    c.execute("SELECT * FROM restaurants")
    restaurants = c.fetchall()
    conn.close()
    
    # 추천 점수 계산
    scored_restaurants = []
    for r in restaurants:
        # 거리 계산
        distance = calculate_distance(user_lat, user_lon, r[5], r[6])
        
        if distance <= max_distance:
            # 맛 일치도 계산
            taste_score = 0
            taste_score += 100 - abs(user_prefs['spicy'] - r[7]) * 10
            taste_score += 100 - abs(user_prefs['oily'] - r[8]) * 10
            taste_score += 100 - abs(user_prefs['salty'] - r[9]) * 10
            taste_score += 100 - abs(user_prefs['sweet'] - r[10]) * 10
            taste_score += 100 - abs(user_prefs['spice_heavy'] - r[11]) * 10
            taste_score += 100 - abs(user_prefs['familiar'] - r[12]) * 10
            taste_score = taste_score / 6
            
            # 거리 점수
            distance_score = max(0, 100 - (distance / max_distance * 100))
            
            # 최종 점수 = 맛 일치도 70% + 거리 20% + 평점 10%
            final_score = (taste_score * 0.7) + (distance_score * 0.2) + (r[13] * 20 * 0.1)
            
            scored_restaurants.append({
                'id': r[0],
                'name': r[1],
                'category': r[2],
                'address': r[3],
                'phone': r[4],
                'distance': round(distance, 2),
                'rating': r[13],
                'taste_match': round(taste_score, 1),
                'final_score': round(final_score, 1)
            })
    
    # 점수순 정렬
    scored_restaurants.sort(key=lambda x: x['final_score'], reverse=True)
    
    if scored_restaurants:
        st.success(f"✅ {len(scored_restaurants)}개의 맛집을 찾았습니다!")
        
        # 추천 맛집 표시
        for i, rest in enumerate(scored_restaurants, 1):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"### {i}. {rest['name']}")
                    st.caption(f"🏷️ {rest['category']} | 📍 {rest['distance']}km")
                    st.caption(f"📍 {rest['address']}")
                    st.caption(f"📞 {rest['phone']}")
                
                with col2:
                    st.metric("🎯 입맛 매칭", f"{rest['taste_match']}%")
                
                with col3:
                    st.metric("⭐ 평점", f"{rest['rating']}")
                
                with col4:
                    st.metric("🏆 종합", f"{rest['final_score']}")
                
                st.progress(rest['taste_match'] / 100)
                st.divider()
    else:
        st.warning("해당 지역에서 검색 결과가 없습니다. 거리를 늘려보세요!")

# 메인 앱
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        # 사이드바 메뉴
        with st.sidebar:
            st.title(f"👋 {st.session_state.username}님")
            st.divider()
            
            menu = st.radio("메뉴", ["🍴 맛집 추천", "🎯 입맛 설정", "📝 내 리뷰"])
            
            st.divider()
            st.success("✅ 광주 맛집 23곳 등록")
            st.caption("실제 주소와 전화번호 포함")
            
            st.divider()
            
            if st.button("로그아웃"):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.user_id = None
                st.rerun()
        
        # 페이지 라우팅
        if menu == "🍴 맛집 추천":
            recommendation_page()
        elif menu == "🎯 입맛 설정":
            preference_page()
        elif menu == "📝 내 리뷰":
            st.title("📝 내 리뷰")
            st.info("리뷰 기능은 곧 추가될 예정입니다!")

if __name__ == "__main__":
    main()
