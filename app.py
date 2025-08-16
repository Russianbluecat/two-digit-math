import streamlit as st
import random
import time
import json
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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

# 자동 포커스 함수 추가
def auto_focus_input():
    """입력 필드에 자동으로 포커스를 설정하는 JavaScript 코드"""
    js_code = """
    <script>
    function focusInput() {
        // 입력 필드를 찾아서 포커스 설정
        const inputs = window.parent.document.querySelectorAll('input[type="text"]');
        if (inputs.length > 0) {
            // 가장 마지막 입력 필드에 포커스 (보통 답변 입력 필드)
            const lastInput = inputs[inputs.length - 1];
            lastInput.focus();
            lastInput.select(); // 기존 텍스트가 있다면 선택
        }
    }
    
    // 페이지 로드 후 실행
    setTimeout(focusInput, 100);
    
    // 또한 폼이 업데이트된 후에도 실행
    setTimeout(focusInput, 300);
    setTimeout(focusInput, 500);
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

# 페이지 설정
st.set_page_config(
    page_title="두 자리 수 암산 게임",
    page_icon="🧮",
    layout="centered"
)

# 커스텀 CSS 스타일 추가
st.markdown("""
<style>
    /* 기본 테마 색상 재정의 */
    :root {
        --primary-color: #007bff; /* 파란색 계열 */
        --success-color: #28a745; /* 초록색 */
        --warning-color: #ffc107; /* 노란색 */
        --danger-color: #dc3545; /* 빨간색 */
    }
    
    /* 버튼에 그림자 및 둥근 모서리 적용 */
    div.stButton > button {
        border-radius: 12px;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }
    
    /* 버튼 hover 효과 */
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    /* 기본 버튼 색상 */
    .stButton button {
        border: 1px solid var(--primary-color);
        color: var(--primary-color);
        background-color: transparent;
    }
    
    /* primary 버튼 색상 */
    .stButton button.primary {
        background-color: var(--primary-color);
        color: white;
    }

    /* secondary 버튼 색상 */
    .stButton button.secondary {
        background-color: #6c757d;
        color: white;
    }
    
    /* text_input에 그림자 및 둥근 모서리 적용 */
    .stTextInput > div > div > input {
        border-radius: 12px;
        box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.1);
        border: 1px solid #ccc;
    }
    
    /* expander 아이콘 색상 변경 */
    .streamlit-expanderHeader i {
        color: var(--primary-color);
    }
    
    /* 제목 중앙 정렬 및 폰트 크기 조정 */
    h1, h2, h3, h4, h5, h6 {
        text-align: center;
    }

    /* st.metric 중앙 정렬 */
    div[data-testid="stMetric"] {
        text-align: center;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
    }
    
    /* 반응형 디자인: 작은 화면에서 폰트 크기 및 버튼 간격 조절 */
    @media (max-width: 768px) {
        h1, h2 {
            font-size: 1.5rem;
        }
        h3 {
            font-size: 1.2rem;
        }
        div.stButton > button {
            font-size: 0.9rem;
            padding: 8px 12px;
        }
        div[data-testid="stMetricValue"] {
            font-size: 2rem !important;
        }
    }
    
    /* 게임 플레이 중 상단 고정 헤더 */
    .game-header-container {
        position: sticky;
        top: 0;
        background-color: white; /* 배경색을 명시적으로 설정 */
        z-index: 999; /* 다른 요소 위에 표시되도록 설정 */
        padding: 10px 0;
        border-bottom: 1px solid #e0e0e0; /* 헤더와 본문 분리선 */
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Google Analytics 활성화
add_google_analytics()

# Google Sheets 설정 (서비스 계정으로 변경)
try:
    scope = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    
    GOOGLE_SHEET_ID = st.secrets["GOOGLE_SHEET_ID"]
    spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
    sheet = spreadsheet.worksheet("Sheet1")
    SHEETS_ENABLED = True
except Exception as e:
    GOOGLE_SHEET_ID = "1zVQMc_cKkXNTTTRMzDsyRrQS_i45iulV63l6JARy0tc"
    SHEETS_ENABLED = False
    st.warning("⚠️ Google Sheets 설정이 필요합니다. 로컬 저장만 사용됩니다.")
    st.error(f"설정 오류: {str(e)}")

# Google Sheets 관련 함수들 (기존 코드와 동일)
def save_game_result(total_questions, correct_count, accuracy, operation_type, time_limit, elapsed_time):
    if not SHEETS_ENABLED:
        st.warning("⚠️ Google Sheets가 설정되지 않아 결과를 저장할 수 없습니다.")
        return False
    
    try:
        from datetime import timezone, timedelta
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        
        row_data = [
            date_str,
            time_str,
            str(total_questions),
            str(correct_count),
            f"{accuracy:.1f}%",
            operation_type,
            f"{time_limit}초",
            f"{elapsed_time:.1f}초"
        ]
        
        sheet.append_row(row_data) 
        st.success("✔️ 결과가 성공적으로 저장되었습니다!")
        return True
    except Exception as e:
        st.error(f"❌ 데이터 저장 중 오류가 발생했습니다: {str(e)}")
        return False

def get_global_statistics():
    if not SHEETS_ENABLED:
        return None
        
    try:
        rows = sheet.get_all_values()
        
        if len(rows) < 2:
            st.info("아직 충분한 통계 데이터가 없습니다.")
            return None
        
        rows = rows[1:]
        
        total_games = len(rows)
        accuracy_list = []
        
        for row in rows:
            if len(row) >= 5:
                accuracy_str = row[4] if len(row) > 4 else "0%"
                try:
                    accuracy = float(accuracy_str.replace('%', ''))
                    accuracy_list.append(accuracy)
                except:
                    continue
        
        if not accuracy_list:
            return None
            
        perfect_count = len([acc for acc in accuracy_list if acc == 100])
        great_count = len([acc for acc in accuracy_list if 90 <= acc < 100])
        good_count = len([acc for acc in accuracy_list if 80 <= acc < 90])
        okay_count = len([acc for acc in accuracy_list if 70 <= acc < 80])
        poor_count = len([acc for acc in accuracy_list if acc < 70])
        
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
            'poor_count': poor_count,
            'poor_rate': (poor_count / total_games) * 100,
            'accuracy_list': accuracy_list,
            'average_accuracy': sum(accuracy_list) / len(accuracy_list)
        }
            
    except gspread.exceptions.APIError as e:
        st.warning(f"Google Sheets API 오류: {e.args}")
        return None
    except Exception as e:
        st.warning(f"통계 조회 중 오류가 발생했습니다: {str(e)}")
        return None
        
def get_user_rank(user_accuracy, accuracy_list):
    if not accuracy_list:
        return "순위 계산 불가"
            
    better_scores = len([acc for acc in accuracy_list if acc > user_accuracy])
    same_scores = len([acc for acc in accuracy_list if acc == user_accuracy])
    
    rank = better_scores + (same_scores + 1) / 2
    percentile = (rank / len(accuracy_list)) * 100
    
    return f"상위 {percentile:.1f}%"

# 세션 상태 초기화
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'setup'
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
    num1 = random.randint(10, 99)
    num2 = random.randint(10, 99)
    
    if operation_type == "덧셈":
        operator = "+"
        answer = num1 + num2
    elif operation_type == "뺄셈":
        if num1 < num2:
            num1, num2 = num2, num1
        operator = "-"
        answer = num1 - num2
    else:
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
    st.session_state.game_state = 'playing'
    st.session_state.current_question = 1
    st.session_state.correct_count = 0
    st.session_state.questions = []
    st.session_state.user_answer = ""
    st.session_state.question_start_time = time.time()
    st.session_state.operation_type = operation_type
    
    for _ in range(question_count):
        question = generate_question(operation_type)
        st.session_state.questions.append(question)
    
    st.session_state.start_time = time.time()

def check_answer():
    try:
        current_time = time.time()
        if 'question_start_time' in st.session_state:
            elapsed_time = current_time - st.session_state.question_start_time
            time_limit = st.session_state.get('time_limit', 5)
            if elapsed_time > time_limit:
                st.session_state.current_streak = 0
                return False, f"⏳ {time_limit}초가 지났습니다! 다음 문제로 넘어갑니다."
        
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
    st.session_state.current_question += 1
    st.session_state.user_answer = ""
    st.session_state.question_start_time = time.time()
    
    if st.session_state.current_question > len(st.session_state.questions):
        total_questions = len(st.session_state.questions)
        accuracy = (st.session_state.correct_count / total_questions) * 100
        elapsed_time = time.time() - st.session_state.start_time
        
        if SHEETS_ENABLED:
            with st.spinner("결과를 저장하는 중..."):
                save_success = save_game_result(
                    total_questions,
                    st.session_state.correct_count,
                    accuracy,
                    st.session_state.get('operation_type', '랜덤'),
                    st.session_state.get('time_limit', 5),
                    elapsed_time
                )
        
        st.session_state.total_games += 1
        st.session_state.total_questions += len(st.session_state.questions)
        st.session_state.total_correct += st.session_state.correct_count
        st.session_state.total_wrong += len(st.session_state.questions) - st.session_state.correct_count
        
        st.session_state.game_state = 'finished'

def reset_game():
    st.session_state.game_state = 'setup'
    st.session_state.current_question = 1
    st.session_state.correct_count = 0
    st.session_state.questions = []
    st.session_state.user_answer = ""
    st.session_state.start_time = None

# 메인 UI
st.markdown("<h2 style='text-align: center;'>🧮 두 자리 수 암산 게임</h2>", unsafe_allow_html=True)

# 게임 설정 단계
if st.session_state.game_state == 'setup':
    st.markdown("### ⚙️ 게임 설정")
    
    if 'question_count' not in st.session_state:
        st.session_state.question_count = 10
    if 'time_limit' not in st.session_state:
        st.session_state.time_limit = 5
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        with st.expander("💡 게임 규칙 살펴보기"):
            st.markdown("""
            * **연산 타입**을 선택하고 **문제 개수**와 **제한 시간**을 설정하세요.
            * 주어진 시간 안에 정답을 입력하고 **제출** 버튼을 누르세요.
            * 시간이 지나면 자동으로 다음 문제로 넘어갑니다.
            * 게임이 끝나면 당신의 점수와 전체 사용자 통계를 확인할 수 있습니다!
            """)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        operation_type = st.selectbox(
            "➕➖ 연산 타입",
            ["덧셈", "뺄셈", "랜덤 (덧셈+뺄셈)"]
        )
        st.session_state.operation_type = operation_type
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 문제 개수와 제한시간 설정 부분을 컨테이너로 묶음
        with st.container():
            st.markdown("### 🔢 문제 개수")
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
            
            st.markdown("### ⏱️ 제한시간")
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
        
        if st.button("🚀 게임 시작!", use_container_width=True, type="primary"):
            start_game(operation_type, st.session_state.question_count)
            st.rerun()

# 게임 진행 단계
elif st.session_state.game_state == 'playing':
    auto_focus_input()
    
    # 상단 고정 헤더 컨테이너
    st.markdown('<div class="game-header-container">', unsafe_allow_html=True)
    
    # 문제 진행 상황 시각화
    progress = (st.session_state.current_question - 1) / len(st.session_state.questions)
    st.progress(progress, text=f"문제 {st.session_state.current_question}/{len(st.session_state.questions)}")
    
    accuracy = (st.session_state.correct_count / (st.session_state.current_question - 1) * 100) if st.session_state.current_question > 1 else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="✔️ 정답 수", value=f"{st.session_state.correct_count}")
    with col2:
        st.metric(label="📈 정답률", value=f"{accuracy:.1f}%")
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    current_q_idx = st.session_state.current_question - 1
    num1, num2, operator, correct_answer = st.session_state.questions[current_q_idx]

    # 시간 초과 시각화
    time_limit = st.session_state.get('time_limit', 5)
    elapsed = time.time() - st.session_state.question_start_time
    remaining = max(0, time_limit - elapsed)
    
    st.markdown("---")

    st.markdown(f"### 문제 {st.session_state.current_question}")
    st.markdown(f"<h2>{num1} {operator} {num2} = ?</h2>", unsafe_allow_html=True)
    
    # 카운트다운 진행 바
    time_progress_bar = st.progress(0, text=f"⏱️ 남은 시간: {remaining:.1f}초")
    time_progress = 1 - (remaining / time_limit)
    time_progress_bar.progress(time_progress)
    
    if remaining <= 0:
        time_progress_bar.empty()
        st.warning("⏳ 시간 초과! 다음 문제로 넘어갑니다.")
        time.sleep(1.0)
        st.session_state.current_streak = 0
        next_question()
        st.rerun()
    else:
        time_progress_bar.progress(1 - remaining / time_limit, text=f"⏱️ 남은 시간: {remaining:.1f}초")

    with st.form(key=f"question_{st.session_state.current_question}"):
        user_input = st.text_input(
            "답을 입력하세요:", 
            key="answer_input",
            placeholder="숫자를 입력하세요"
        )
        submitted = st.form_submit_button("제출", use_container_width=True, type="primary")

        if submitted:
            st.session_state.user_answer = user_input
            is_correct, message = check_answer()
            
            if "초가 지났습니다" in message:
                st.warning(f"⏳ {message}")
            elif is_correct:
                st.success(f"✔️ {message}")
            else:
                st.error(f"✖️ {message}")
            
            time.sleep(1.0)
            next_question()
            st.rerun()
    
    if st.button("🔄 게임 리셋", type="secondary"):
        reset_game()
        st.rerun()

# 게임 완료 단계
elif st.session_state.game_state == 'finished':
    st.balloons()
    
    total_questions = len(st.session_state.questions)
    accuracy = (st.session_state.correct_count / total_questions) * 100
    
    st.markdown("## ✨ 게임 완료!")
    
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 10px;'>
      <div>
        총 문제 수: <b>{total_questions}개</b>
      </div>
      <div>
        정답 수: <b>{st.session_state.correct_count}개</b>
      </div>
      <div>
        정답률: <b>{accuracy:.1f}%</b>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    if accuracy == 100:
        st.markdown("<div style='text-align: center;'><h4 style='color: green;'>🏆 완벽합니다! 천재군요!</h4></div>", unsafe_allow_html=True)
    elif accuracy >= 90:
        st.markdown("<div style='text-align: center;'><h4 style='color: green;'>🌟 훌륭해요!</h4></div>", unsafe_allow_html=True)
    elif accuracy >= 80:
        st.markdown("<div style='text-align: center;'><h4 style='color: blue;'>👍 잘했어요!</h4></div>", unsafe_allow_html=True)
    elif accuracy >= 70:
        st.markdown("<div style='text-align: center;'><h4 style='color: orange;'>💪 조금만 더 연습하면 완벽해질 거예요!</h4></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center;'><h4 style='color: red;'>📚 더 연습해보세요!</h4></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📈 실시간 전체 사용자 통계")
    
    if SHEETS_ENABLED:
        with st.spinner("전체 통계를 불러오는 중..."):
            global_stats = get_global_statistics()
    else:
        global_stats = None
        st.warning("⚠️ Google Sheets가 연결되지 않아 전체 통계를 표시할 수 없습니다.")
    
    if global_stats:
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
            🌟 90% 이상 100% 미만 달성자: <span style='font-weight: bold; color: #333;'>{global_stats['great_count']}명</span> 
            <span style='color: #28a745;'>({global_stats['great_rate']:.1f}%)</span>
          </div>
          
          <div style='font-size: 0.95rem; color: #666; margin-bottom: 8px;'>
            👍 80% 이상 90% 미만 달성자: <span style='font-weight: bold; color: #333;'>{global_stats['good_count']}명</span> 
            <span style='color: #007bff;'>({global_stats['good_rate']:.1f}%)</span>
          </div>
          
          <div style='font-size: 0.95rem; color: #666; margin-bottom: 8px;'>
            💪 70% 이상 80% 미만 달성자: <span style='font-weight: bold; color: #333;'>{global_stats['okay_count']}명</span> 
            <span style='color: #ffc107;'>({global_stats['okay_rate']:.1f}%)</span>
          </div>
          
          <div style='font-size: 0.95rem; color: #666; margin-bottom: 15px;'>
            📚 70% 미만 달성자: <span style='font-weight: bold; color: #333;'>{global_stats['poor_count']}명</span> 
            <span style='color: #dc3545;'>({global_stats['poor_rate']:.1f}%)</span>
          </div>
          
          <div style='text-align: center; padding-top: 10px; border-top: 2px solid #ddd;'>
            <div style='font-size: 1.1rem; font-weight: bold; color: #dc3545;'>
              🎯 당신은 <span style='font-size: 1.2rem;'>{get_user_rank(accuracy, global_stats['accuracy_list'])}</span> 입니다!
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
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
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 다시 하기", use_container_width=True, type="primary"):
            reset_game()
            st.rerun()
    with col2:
        if st.button("🛠️ 설정 변경", use_container_width=True, type="secondary"):
            reset_game()
            st.rerun()

# 푸터
st.markdown("---")
st.markdown("<div style='text-align: center;'>Made with ❤️ using Streamlit</div>", unsafe_allow_html=True)
