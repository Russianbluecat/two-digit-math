import streamlit as st
import random
import time

# --- 세션 상태 초기화 ---
# 앱이 재실행될 때마다 항상 실행되어 상태를 보장합니다.
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
if 'question_count' not in st.session_state:
    st.session_state.question_count = 10
if 'time_limit' not in st.session_state:
    st.session_state.time_limit = 5

# --- 페이지 설정 ---
st.set_page_config(
    page_title="두 자리 수 암산 게임",
    page_icon="🧮",
    layout="centered"
)

# --- 게임 로직 함수 ---
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
    st.session_state.questions = [generate_question(operation_type) for _ in range(question_count)]
    st.session_state.user_answer = ""
    st.session_state.question_start_time = time.time()
    st.session_state.operation_type = operation_type
    st.session_state.start_time = time.time()

def check_answer():
    try:
        if time.time() - st.session_state.question_start_time > st.session_state.time_limit:
            return False, f"⏰ {st.session_state.time_limit}초가 지났습니다! 다음 문제로 넘어갑니다."
        
        user_input = int(st.session_state.user_answer)
        correct_answer = st.session_state.questions[st.session_state.current_question - 1][3]
        
        if user_input == correct_answer:
            st.session_state.correct_count += 1
            return True, "정답!"
        else:
            return False, f"틀림! 정답은 {correct_answer}입니다."
    except ValueError:
        return False, "숫자를 입력해주세요!"

def next_question():
    st.session_state.current_question += 1
    st.session_state.user_answer = ""
    st.session_state.question_start_time = time.time()
    
    if st.session_state.current_question > len(st.session_state.questions):
        st.session_state.game_state = 'finished'

def reset_game():
    st.session_state.game_state = 'setup'
    st.session_state.current_question = 1
    st.session_state.correct_count = 0
    st.session_state.questions = []
    st.session_state.user_answer = ""
    st.session_state.start_time = None

# --- UI/UX 헬퍼 함수 ---
def update_question_count(delta):
    new_count = st.session_state.question_count + delta
    if 5 <= new_count <= 20:
        st.session_state.question_count = new_count
        st.rerun()

def update_time_limit(delta):
    new_limit = st.session_state.time_limit + delta
    if 3 <= new_limit <= 10:
        st.session_state.time_limit = new_limit
        st.rerun()
        
# --- 메인 앱 실행 ---
st.markdown("<h2 style='text-align: center; font-size: 1.8rem; margin-top: -50px;'>🧮 두 자리 수 암산 게임</h2>", unsafe_allow_html=True)

# 게임 설정 단계
if st.session_state.game_state == 'setup':
    st.markdown("### 🎯 게임 설정")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        operation_type = st.selectbox(
            "📝 연산 타입",
            ["덧셈", "뺄셈", "랜덤 (덧셈+뺄셈)"]
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**📊 문제 개수**")
        
        st.markdown("""
        <style>
        .control-container {
            display: flex !important;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
        }
        .control-button {
            width: 50px !important;
            height: 50px !important;
            background: #f0f2f6;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            cursor: pointer;
            border: 1px solid #ddd;
            transition: background-color 0.2s;
        }
        .control-button:hover {
            background: #e0e2e6;
        }
        .black-bg-text {
            min-width: 80px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            color: white;
            background-color: black;
            padding: 10px;
            border-radius: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="control-container">
            <div class="control-button" onclick="decreaseQuestions()">➖</div>
            <div class="black-bg-text">{st.session_state.question_count}개</div>
            <div class="control-button" onclick="increaseQuestions()">➕</div>
        </div>
        """, unsafe_allow_html=True)
        
        col_q_minus, col_q_plus, _ = st.columns([1, 1, 100])
        with col_q_minus:
            if st.button(" ", key="question_minus", help="decrease_q"):
                update_question_count(-1)
        with col_q_plus:
            if st.button(" ", key="question_plus", help="increase_q"):
                update_question_count(1)

        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("**⏰ 제한시간**")
        
        st.markdown(f"""
        <div class="control-container">
            <div class="control-button" onclick="decreaseTime()">➖</div>
            <div class="black-bg-text">{st.session_state.time_limit}초</div>
            <div class="control-button" onclick="increaseTime()">➕</div>
        </div>
        """, unsafe_allow_html=True)
        
        col_t_minus, col_t_plus, _ = st.columns([1, 1, 100])
        with col_t_minus:
            if st.button(" ", key="time_minus", help="decrease_t"):
                update_time_limit(-1)
        with col_t_plus:
            if st.button(" ", key="time_plus", help="increase_t"):
                update_time_limit(1)

        st.markdown("""
        <script>
        function decreaseQuestions() {
            const buttons = parent.document.querySelectorAll('button[title="decrease_q"]');
            if (buttons.length > 0) buttons[0].click();
        }
        function increaseQuestions() {
            const buttons = parent.document.querySelectorAll('button[title="increase_q"]');
            if (buttons.length > 0) buttons[0].click();
        }
        function decreaseTime() {
            const buttons = parent.document.querySelectorAll('button[title="decrease_t"]');
            if (buttons.length > 0) buttons[0].click();
        }
        function increaseTime() {
            const buttons = parent.document.querySelectorAll('button[title="increase_t"]');
            if (buttons.length > 0) buttons[0].click();
        }
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        if st.button("🚀 게임 시작!", use_container_width=True, type="primary"):
            start_game(operation_type, st.session_state.question_count)
            st.rerun()

# 게임 진행 단계
elif st.session_state.game_state == 'playing':
    progress = (st.session_state.current_question - 1) / len(st.session_state.questions)
    st.progress(progress)
    
    time_limit = st.session_state.time_limit
    elapsed = time.time() - st.session_state.question_start_time
    remaining = max(0, time_limit - elapsed)
    
    st.progress(1 - elapsed / time_limit, f"⏰ 남은 시간: {remaining:.1f}초")

    current_q_idx = st.session_state.current_question - 1
    num1, num2, operator, correct_answer = st.session_state.questions[current_q_idx]
    
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
    
    st.markdown(f"<h3 style='margin-top: 5px; margin-bottom: 5px;'>문제 {st.session_state.current_question}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='margin-top: 0px; margin-bottom: 10px;'>{num1} {operator} {num2} = ?</h2>", unsafe_allow_html=True)

    with st.form(key=f"question_{st.session_state.current_question}"):
        user_input = st.text_input("답을 입력하세요:", key="answer_input", autofocus=True)
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
    
    if st.button("🔄 게임 리셋", type="secondary"):
        reset_game()
        st.rerun()

# 게임 완료 단계
elif st.session_state.game_state == 'finished':
    st.balloons()
    
    total_questions = len(st.session_state.questions)
    accuracy = (st.session_state.correct_count / total_questions) * 100
    
    st.markdown("<h2 style='margin-top: -20px; margin-bottom: 10px;'>🎉 게임 완료!</h2>", unsafe_allow_html=True)
    
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
        
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #666;'>📊 이 기록은 현재 세션에만 저장됩니다.</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 다시 하기", use_container_width=True, type="primary"):
            reset_game()
            st.rerun()
    with col2:
        if st.button("⚙️ 설정 변경", use_container_width=True, type="secondary"):
            reset_game()
            st.rerun()

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
