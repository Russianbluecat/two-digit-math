import streamlit as st
import random
import time
import json
import pandas as pd
from datetime import datetime
import requests
from urllib.parse import quote

# Google Analytics 추가
def add_google_analytics():
    ga_code = """
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-4Q1S1M127P"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-4Q1S1M127P');
    </script>
    """
    st.markdown(ga_code, unsafe_allow_html=True)

# 페이지 설정
st.set_page_config(
    page_title="두 자리 수 암산 게임",
    page_icon="🧮",
    layout="centered"
)

# Google Analytics 활성화
add_google_analytics()

# Google Sheets 설정 (환경변수 또는 secrets에서 가져오기)
# Streamlit Cloud에서는 st.secrets를 사용
try:
    GOOGLE_SHEET_ID = st.secrets["GOOGLE_SHEET_ID"]
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    # 로컬 개발용 기본값 (실제 배포시에는 secrets에 설정)
    GOOGLE_SHEET_ID = "your_sheet_id_here"
    GOOGLE_API_KEY = "your_api_key_here"

# Google Sheets 관련 함수들
def save_game_result(total_questions, correct_count, accuracy, operation_type, time_limit, elapsed_time):
    """게임 결과를 Google Sheets에 저장"""
    try:
        # 현재 시간 (한국 시간으로 조정)
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        # 저장할 데이터
        row_data = [
            date_str,
            time_str,
            total_questions,
            correct_count,
            f"{accuracy:.1f}%",
            operation_type,
            f"{time_limit}초",
            f"{elapsed_time:.1f}초"
        ]
        
        # Google Sheets API를 통해 데이터 추가
        sheet_url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/Sheet1:append"
        params = {
            "valueInputOption": "RAW",
            "key": GOOGLE_API_KEY
        }
        
        data = {
            "values": [row_data]
        }
        
        # POST 요청 보내기
        response = requests.post(sheet_url, params=params, json=data)
        
        if response.status_code == 200:
            st.success("✅ 결과가 성공적으로 저장되었습니다!")
            return True
        else:
            st.error(f"❌ 저장 실패: HTTP {response.status_code}")
            # 에러 세부사항 출력 (디버깅용)
            try:
                error_detail = response.json()
                st.error(f"상세 오류: {error_detail}")
            except:
                st.error(f"응답 내용: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        st.error(f"❌ 네트워크 오류: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ 데이터 저장 중 오류가 발생했습니다: {str(e)}")
        return False

def get_global_statistics():
    """Google Sheets에서 전체 통계 조회"""
    try:
        # Google Sheets에서 데이터 읽기
        sheet_url = f"https://sheets.googleapis.com/v4/spreadsheets/{GOOGLE_SHEET_ID}/values/Sheet1"
        params = {"key": GOOGLE_API_KEY}
        
        response = requests.get(sheet_url, params=params)
        if response.status_code != 200:
            st.warning(f"통계 데이터를 불러올 수 없습니다: HTTP {response.status_code}")
            return None
            
        data = response.json()
        if 'values' not in data or len(data['values']) < 2:
            st.info("아직 충분한 통계 데이터가 없습니다.")
            return None
            
        # 첫 번째 행은 헤더, 나머지는 데이터
        rows = data['values'][1:]  # 헤더 제외
        
        # 데이터 분석
        total_games = len(rows)
        accuracy_list = []
        
        for row in rows:
            if len(row) >= 5:  # 최소한의 데이터가 있는지 확인
                accuracy_str = row[4]  # 정답률 컬럼
                try:
                    accuracy = float(accuracy_str.replace('%', ''))
                    accuracy_list.append(accuracy)
                except:
                    continue
        
        if not accuracy_list:
            return None
            
        # 통계 계산
        perfect_count = len([acc for acc in accuracy_list if acc == 100])
        great_count = len([acc for acc in accuracy_list if acc >= 90])
        good_count = len([acc for acc in accuracy_list if acc >= 80])
        okay_count = len([acc for acc in accuracy_list if acc >= 70])
        
        return {
            'total_games': total_games,
            'perfect_count': perfect_count,
            'perfect_rate': (perfect_count / total_games) * 100,
            'great_count': great_count,
            'great_rate': (great_count / total_games) * 100,
            'good_count': good_count,
            'good_rate': (good_count / total_games) * 100,
            'okay_count': okay_count,
            'okay_rate': (okay_count / total_games) * 100,
            'accuracy_list': accuracy_list,
            'average_accuracy': sum(accuracy_list) / len(accuracy_list)
        }
        
    except requests.exceptions.RequestException as e:
        st.warning(f"네트워크 오류로 통계를 불러올 수 없습니다: {str(e)}")
        return None
    except Exception as e:
        st.warning(f"통계 조회 중 오류가 발생했습니다: {str(e)}")
        return None

def get_user_rank(user_accuracy, accuracy_list):
    """사용자의 순위 계산"""
    if not accuracy_list:
        return "순위 계산 불가"
        
    better_scores = len([acc for acc in accuracy_list if acc > user_accuracy])
    same_scores = len([acc for acc in accuracy_list if acc == user_accuracy])
    
    # 동점자의 중간 순위 계산
    rank = better_scores + (same_scores + 1) / 2
    percentile = (rank / len(accuracy_list)) * 100
    
    return f"상위 {percentile:.1f}%"

# 세션 상태 초기화
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'setup'  # setup, playing, finished
if 'current_question' not in st.session_state:
    st.session_state.current_question = 1
if 'correct_count' not in st.session_state:
    st.session_state.correct_count = 0
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'user_answer' not in st.session_state:
    st.session_state.user_answer = ""

# 통계 관련 세션 상태 초기화 (로컬용 - 백업)
if 'total_games' not in st.session_state:
    st.session_state.total_games = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0
if 'total_correct' not in st.session_state:
    st.session_state.total_correct = 0
if 'total_wrong' not in st.session_state:
    st.session_state.total_wrong = 0
if 'best_streak' not in st.session_state:
    st.session_state.best_streak = 0
if 'current_streak' not in st.session_state:
    st.session_state.current_streak = 0

def generate_question(operation_type):
    """문제 생성 함수"""
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    
    if operation_type == "덧셈":
        operator = "+"
        answer = num1 + num2
    elif operation_type == "뺄셈":
        # 결과가 음수가 되지 않도록 큰 수에서 작은 수를 빼기
        if num1 < num2:
            num1, num2 = num2, num1
        operator = "-"
        answer = num1 - num2
    else:  # "랜덤"
        if random.choice([True, False]):
            operator = "+"
            answer = num1 + num2
        else:
            if num1 < num2:
                num1, num2 = num2, num1
            operator = "-"
            answer = num1 - num2
    
    return num1, num2, operator, answer

def start_game(operation_type, question_count):
    """게임 시작"""
    st.session_state.game_state = 'playing'
    st.session_state.current_question = 1
    st.session_state.correct_count = 0
    st.session_state.questions = []
    st.session_state.user_answer = ""
    st.session_state.question_start_time = time.time()
    st.session_state.operation_type = operation_type  # 게임 완료시 저장용
    
    # 모든 문제 미리 생성
    for _ in range(question_count):
        question = generate_question(operation_type)
        st.session_state.questions.append(question)
    
    st.session_state.start_time = time.time()

def check_answer():
    """답안 체크 (시간 제한 포함)"""
    try:
        # 시간 체크
        current_time = time.time()
        if 'question_start_time' in st.session_state:
            elapsed_time = current_time - st.session_state.question_start_time
            time_limit = st.session_state.get('time_limit', 5)
            if elapsed_time > time_limit:
                st.session_state.current_streak = 0
                return False, f"⏰ {time_limit}초가 지났습니다! 다음 문제로 넘어갑니다."
        
        user_input = int(st.session_state.user_answer)
        current_q_idx = st.session_state.current_question - 1
        correct_answer = st.session_state.questions[current_q_idx][3]
        
        if user_input == correct_answer:
            st.session_state.correct_count += 1
            st.session_state.current_streak += 1
            if st.session_state.current_streak > st.session_state.best_streak:
                st.session_state.best_streak = st.session_state.current_streak
            return True, "정답!"
        else:
            st.session_state.current_streak = 0
            return False, f"틀림! 정답은 {correct_answer}입니다."
    except ValueError:
        st.session_state.current_streak = 0
        return False, "숫자를 입력해주세요!"

def next_question():
    """다음 문제로"""
    st.session_state.current_question += 1
    st.session_state.user_answer = ""
    st.session_state.question_start_time = time.time()
    
    if st.session_state.current_question > len(st.session_state.questions):
        # 게임 완료 시 Google Sheets에 저장
        total_questions = len(st.session_state.questions)
        accuracy = (st.session_state.correct_count / total_questions) * 100
        elapsed_time = time.time() - st.session_state.start_time
        
        # Google Sheets에 저장 (비동기적으로 처리)
        with st.spinner("결과를 저장하는 중..."):
            save_success = save_game_result(
                total_questions,
                st.session_state.correct_count,
                accuracy,
                st.session_state.get('operation_type', '랜덤'),
                st.session_state.get('time_limit', 5),
                elapsed_time
            )
        
        # 로컬 통계도 업데이트 (백업용)
        st.session_state.total_games += 1
        st.session_state.total_questions += len(st.session_state.questions)
        st.session_state.total_correct += st.session_state.correct_count
        st.session_state.total_wrong += len(st.session_state.questions) - st.session_state.correct_count
        
        st.session_state.game_state = 'finished'

def reset_game():
    """게임 리셋"""
    st.session_state.game_state = 'setup'
    st.session_state.current_question = 1
    st.session_state.correct_count = 0
    st.session_state.questions = []
    st.session_state.user_answer = ""
    st.session_state.start_time = None

# 메인 UI
st.markdown("<h2 style='text-align: center; font-size: 1.8rem;'>🧮 두 자리 수 암산 게임</h2>", unsafe_allow_html=True)

# 게임 설정 단계
if st.session_state.game_state == 'setup':
    st.markdown("### 🎯 게임 설정")
    
    # 세션 상태 초기화
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 10
    if 'time_limit' not in st.session_state:
        st.session_state.time_limit = 5
    
    # 메인 화면에서 설정
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # 연산 타입 선택
        operation_type = st.selectbox(
            "📝 연산 타입",
            ["덧셈", "뺄셈", "랜덤 (덧셈+뺄셈)"]
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 문제 개수 설정
        st.markdown("**📊 문제 개수**")
        
         # CSS로 강제 가로 배치
        st.markdown("""
        <style>
        .question-controls {
            display: flex !important;
            align-items: center;
            justify-content: center;
            gap: 15px;
            margin: 15px 0;
        }
        .question-controls > div {
            flex: none !important;
        }
        .question-controls button {
            width: 50px !important;
            height: 50px !important;
            min-width: 50px !important;
            border-radius: 10px !important;
            font-size: 20px !important;
        }
        .question-display {
            min-width: 56px;
            width: 70%;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            padding: 14px;
            background: black; /* 배경색을 검정색으로 변경 */
            color: white; /* 글자색을 흰색으로 변경 */
            border-radius: 10px;
            margin: 0 auto;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 문제 개수 설정 UI
        col_minus, col_text, col_plus = st.columns([1, 1, 1])
        
        with col_minus:
            if st.button("➖", key="question_minus", use_container_width=True):
                if st.session_state.question_count > 5:
                    st.session_state.question_count -= 1
                    st.rerun()
                    
        with col_text:
            st.markdown(
             f"<h3 style='text-align: center; vertical-align: middle; line-height: 2.2;'>{st.session_state.question_count}개</h3>",
             unsafe_allow_html=True
            )
            
        with col_plus:
            if st.button("➕", key="question_plus", use_container_width=True):
                if st.session_state.question_count < 20:
                    st.session_state.question_count += 1
                    st.rerun()
                    
        
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 제한시간 설정
        st.markdown("**⏰ 제한시간**")
        
        # 제한시간 설정 UI
        col_minus, col_text, col_plus = st.columns([1, 1, 1])

        with col_minus:
            if st.button("➖", key="time_minus", use_container_width=True):
                if st.session_state.time_limit > 3:
                    st.session_state.time_limit -= 1
                    st.rerun()
                    
        with col_text:
            st.markdown(
            f"<h3 style='text-align: center; vertical-align: middle; line-height: 2.2;'>{st.session_state.time_limit}초</h3>",
            unsafe_allow_html=True
            )
            
        with col_plus:
            if st.button("➕", key="time_plus", use_container_width=True):
                if st.session_state.time_limit < 10:
                    st.session_state.time_limit += 1
                    st.rerun()
        
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # 게임 시작 버튼
        if st.button("🚀 게임 시작!", use_container_width=True, type="primary"):
            start_game(operation_type, st.session_state.question_count)
            st.rerun()

# 게임 진행 단계
elif st.session_state.game_state == 'playing':
    # 진행률 표시
    progress = (st.session_state.current_question - 1) / len(st.session_state.questions)
    st.progress(progress)
    
    # 현재 문제 정보
    current_q_idx = st.session_state.current_question - 1
    num1, num2, operator, correct_answer = st.session_state.questions[current_q_idx]
    
    # 점수 표시
    accuracy = (st.session_state.correct_count / (st.session_state.current_question - 1) * 100) if st.session_state.current_question > 1 else 0
    
    st.markdown(f"""
    <div style='text-align: right; margin-bottom: 5px; margin-top: -20px;'>
        <div style='font-size: 0.75rem; color: #666; margin-bottom: 0px;'>
            문제: <span style='font-weight: bold; color: #333;'>{st.session_state.current_question}/{len(st.session_state.questions)}</span> | 
            정답: <span style='font-weight: bold; color: #333;'>{st.session_state.correct_count}</span> | 
            정답률: <span style='font-weight: bold; color: #333;'>{accuracy:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 문제 출제
    st.markdown(f"<h3 style='margin-top: 5px; margin-bottom: 5px;'>문제 {st.session_state.current_question}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='margin-top: 0px; margin-bottom: 10px;'>{num1} {operator} {num2} = ?</h2>", unsafe_allow_html=True)
    
    # 경과 시간 표시
    if 'question_start_time' in st.session_state:
        elapsed = time.time() - st.session_state.question_start_time
        time_limit = st.session_state.get('time_limit', 5)
        remaining = max(0, time_limit - elapsed)
        if remaining > 0:
            st.markdown(f"<h3 style='margin-top: 0px; margin-bottom: 10px;'>⏰ 남은 시간: {remaining:.1f}초</h3>", unsafe_allow_html=True)
        else:
            st.markdown("<h3 style='margin-top: 0px; margin-bottom: 10px;'>⏰ 시간 초과!</h3>", unsafe_allow_html=True)
    
    with st.form(key=f"question_{st.session_state.current_question}"):
        user_input = st.text_input("답을 입력하세요:", key="answer_input")
        submitted = st.form_submit_button("제출", use_container_width=True, type="primary")
        
        if submitted:
            st.session_state.user_answer = user_input
            is_correct, message = check_answer()
            
            if "초가 지났습니다" in message:
                st.warning(f"⏰ {message}")
            elif is_correct:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
            
            time.sleep(1.0)
            next_question()
            st.rerun()
    
    # 게임 중단 버튼
    if st.button("🔄 게임 리셋", type="secondary"):
        reset_game()
        st.rerun()

# 게임 완료 단계
elif st.session_state.game_state == 'finished':
    st.balloons()  # 축하 애니메이션
    
    # 최종 결과
    total_questions = len(st.session_state.questions)
    accuracy = (st.session_state.correct_count / total_questions) * 100
    
    st.markdown("<h2 style='margin-top: -20px; margin-bottom: 10px;'>🎉 게임 완료!</h2>", unsafe_allow_html=True)
    
    # 개인 결과 표시
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 10px;'>
        <div style='font-size: 0.9rem; color: #666; margin-bottom: 8px;'>
            총 문제 수: <span style='font-weight: bold; color: #333; font-size: 1.1rem;'>{total_questions}개</span>
        </div>
        <div style='font-size: 0.9rem; color: #666; margin-bottom: 8px;'>
            정답 수: <span style='font-weight: bold; color: #333; font-size: 1.1rem;'>{st.session_state.correct_count}개</span>
        </div>
        <div style='font-size: 0.9rem; color: #666; margin-bottom: 8px;'>
            정답률: <span style='font-weight: bold; color: #333; font-size: 1.1rem;'>{accuracy:.1f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 성적에 따른 메시지
    if accuracy == 100:
        st.markdown("<div style='text-align: center; margin-bottom: 15px;'><h4 style='color: green; margin: 0;'>🏆 완벽합니다! 천재군요!</h4></div>", unsafe_allow_html=True)
    elif accuracy >= 90:
        st.markdown("<div style='text-align: center; margin-bottom: 15px;'><h4 style='color: green; margin: 0;'>🌟 훌륭해요!</h4></div>", unsafe_allow_html=True)
    elif accuracy >= 80:
        st.markdown("<div style='text-align: center; margin-bottom: 15px;'><h4 style='color: blue; margin: 0;'>👍 잘했어요!</h4></div>", unsafe_allow_html=True)
    elif accuracy >= 70:
        st.markdown("<div style='text-align: center; margin-bottom: 15px;'><h4 style='color: orange; margin: 0;'>💪 조금만 더 연습하면 완벽해질 거예요!</h4></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center; margin-bottom: 15px;'><h4 style='color: red; margin: 0;'>📚 더 연습해보세요!</h4></div>", unsafe_allow_html=True)
    
    # 전체 사용자 통계 표시
    st.markdown("---")
    st.markdown("### 📊 실시간 전체 사용자 통계")
    
    with st.spinner("전체 통계를 불러오는 중..."):
        global_stats = get_global_statistics()
    
    if global_stats:
        # 전체 통계 표시
        st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
            <div style='text-align: center; margin-bottom: 15px;'>
                <div style='font-size: 1.1rem; color: #333; font-weight: bold; margin-bottom: 15px;'>
                    🌟 지금까지 총 <span style='color: #1f77b4; font-size: 1.3rem;'>{global_stats['total_games']:,}명</span>이 도전했습니다!
                </div>
                <div style='font-size: 0.9rem; color: #666; margin-bottom: 10px;'>
                    📈 전체 평균 정답률: <span style='font-weight: bold; color: #333;'>{global_stats['average_accuracy']:.1f}%</span>
                </div>
            </div>
            
            <div style='font-size: 0.95rem; color: #666; margin-bottom: 8px;'>
                🏆 100% 달성자: <span style='font-weight: bold; color: #333;'>{global_stats['perfect_count']}명</span> 
                <span style='color: #28a745;'>({global_stats['perfect_rate']:.1f}%)</span>
            </div>
            
            <div style='font-size: 0.95rem; color: #666; margin-bottom: 8px;'>
                🌟 90% 이상 달성자: <span style='font-weight: bold; color: #333;'>{global_stats['great_count']}명</span> 
                <span style='color: #28a745;'>({global_stats['great_rate']:.1f}%)</span>
            </div>
            
            <div style='font-size: 0.95rem; color: #666; margin-bottom: 8px;'>
                👍 80% 이상 달성자: <span style='font-weight: bold; color: #333;'>{global_stats['good_count']}명</span> 
                <span style='color: #007bff;'>({global_stats['good_rate']:.1f}%)</span>
            </div>
            
            <div style='font-size: 0.95rem; color: #666; margin-bottom: 15px;'>
                💪 70% 이상 달성자: <span style='font-weight: bold; color: #333;'>{global_stats['okay_count']}명</span> 
                <span style='color: #6c757d;'>({global_stats['okay_rate']:.1f}%)</span>
            </div>
            
            <div style='text-align: center; padding-top: 10px; border-top: 2px solid #ddd;'>
                <div style='font-size: 1.1rem; font-weight: bold; color: #dc3545;'>
                    🎯 당신은 <span style='font-size: 1.2rem;'>{get_user_rank(accuracy, global_stats['accuracy_list'])}</span> 입니다!
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 격려 메시지
        user_percentile = float(get_user_rank(accuracy, global_stats['accuracy_list']).replace('상위 ', '').replace('%', ''))
        
        if user_percentile <= 10:
            st.markdown("<div style='text-align: center;'><h4 style='color: gold;'>👑 상위 10% 안에 드셨네요! 정말 대단합니다!</h4></div>", unsafe_allow_html=True)
        elif user_percentile <= 25:
            st.markdown("<div style='text-align: center;'><h4 style='color: green;'>🔥 상위 25% 안에 드셨어요! 실력자시군요!</h4></div>", unsafe_allow_html=True)
        elif user_percentile <= 50:
            st.markdown("<div style='text-align: center;'><h4 style='color: blue;'>💪 평균보다 훨씬 잘하셨어요!</h4></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: center;'><h4 style='color: orange;'>📚 더 연습하면 더욱 좋아질 거예요!</h4></div>", unsafe_allow_html=True)
    
    else:
        # 통계 로딩 실패시 로컬 통계 표시 (백업)
        if st.session_state.total_games > 0:
            overall_accuracy = (st.session_state.total_correct / st.session_state.total_questions) * 100
            st.markdown(f"""
            <div style='background-color: #fff3cd; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
                <div style='text-align: center; color: #856404; margin-bottom: 10px;'>
                    ⚠️ 전체 통계를 불러올 수 없어 세션 통계를 표시합니다
                </div>
                <div style='font-size: 0.9rem; color: #666; margin-bottom: 8px;'>
                    • 이번 세션 게임 수: <span style='font-weight: bold; color: #333;'>{st.session_state.total_games}게임</span>
                </div>
                <div style='font-size: 0.9rem; color: #666; margin-bottom: 8px;'>
                    • 평균 정답률: <span style='font-weight: bold; color: #333;'>{overall_accuracy:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div style='text-align: center; color: #666;'>📊 전체 통계 준비 중...</div>", unsafe_allow_html=True)
    
    # 다시하기 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 다시 하기", use_container_width=True, type="primary"):
            reset_game()
            st.rerun()
    with col2:
        if st.button("⚙️ 설정 변경", use_container_width=True, type="secondary"):
            reset_game()
            st.rerun()

# 푸터
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")

# Google Sheets 설정 안내
st.markdown("---")
st.markdown("### 📋 Google Sheets 설정 방법")

with st.expander("🔧 개발자를 위한 설정 안내"):
    st.markdown("""
    **1. Google Sheets 생성**
    - 새 Google Sheets 문서 생성
    - 첫 번째 행에 헤더 추가: `날짜, 시간, 총문제수, 정답수, 정답률, 연산타입, 제한시간, 소요시간`
    
    **2. Google Sheets API 활성화**
    - Google Cloud Console에서 Sheets API 활성화
    - API 키 생성 (제한: Sheets API만 허용)
    
    **3. Streamlit Secrets 설정**
    ```toml
    # .streamlit/secrets.toml
    GOOGLE_SHEET_ID = "your_google_sheet_id"
    GOOGLE_API_KEY = "your_google_api_key"
    ```
    
    **4. Google Sheets 공개 설정**
    - 시트를 "링크가 있는 모든 사용자" 편집 가능으로 설정
    - 또는 서비스 계정 사용 권장 (보안성 향상)
    
    **주의사항:**
    - API 키는 절대 코드에 직접 입력하지 마세요
    - 실제 배포시에는 서비스 계정 JSON 파일 사용 권장
    - API 사용량 제한을 고려하여 캐싱 구현 권장
    """)

st.markdown("### 🎯 기대 효과")
st.markdown("""
- 🌍 **글로벌 경쟁**: 전 세계 사용자들과 실력 비교
- 📈 **동기 부여**: 실시간 순위로 재도전 의욕 상승  
- 📊 **데이터 분석**: 사용자 패턴 및 난이도 분석 가능
- 🏆 **성취감 증대**: 상위 몇% 달성시 특별한 만족감
""")
