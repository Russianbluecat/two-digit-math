import streamlit as st
import random
import time

# 페이지 설정
st.set_page_config(
    page_title="두 자리 수 암산 게임",
    page_icon="🧮",
    layout="centered"
)

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
    st.session_state.question_start_time = time.time()  # 첫 문제 시작 시간
    
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
            if elapsed_time > 5:  # 5초 초과
                return False, "⏰ 5초가 지났습니다! 다음 문제로 넘어갑니다."
        
        user_input = int(st.session_state.user_answer)
        current_q_idx = st.session_state.current_question - 1
        correct_answer = st.session_state.questions[current_q_idx][3]
        
        if user_input == correct_answer:
            st.session_state.correct_count += 1
            return True, "정답!"
        else:
            return False, f"틀림! 정답은 {correct_answer}입니다."
    except ValueError:
        return False, "숫자를 입력해주세요!"

def next_question():
    """다음 문제로"""
    st.session_state.current_question += 1
    st.session_state.user_answer = ""
    st.session_state.question_start_time = time.time()  # 새 문제 시작 시간 기록
    
    if st.session_state.current_question > len(st.session_state.questions):
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
st.markdown("<h1 style='text-align: center;'>🧮 두 자리 수 암산 게임</h1>", unsafe_allow_html=True)

# 게임 설정 단계
if st.session_state.game_state == 'setup':
    st.markdown("### 🎯 게임 설정")
    
    # 사이드바에서 설정
    with st.sidebar:
        st.markdown("### ⚙️ 설정")
        operation_type = st.selectbox(
            "연산 타입 선택",
            ["덧셈", "뺄셈", "랜덤 (덧셈+뺄셈)"]
        )
        
        question_count = st.slider(
            "문제 개수",
            min_value=5,
            max_value=20,
            value=10,
            step=1
        )
        
        time_limit = st.slider(
            "제한시간 (초)",
            min_value=3,
            max_value=10,
            value=5,
            step=1
        )
    
    # 메인 화면
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        **선택된 설정:**
        - 연산 타입: **{operation_type}**
        - 문제 개수: **{question_count}개**
        - 제한시간: **{time_limit}초**
        """)
        
        if st.button("🚀 게임 시작!", use_container_width=True, type="primary"):
            start_game(operation_type, question_count)
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
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("문제", f"{st.session_state.current_question}/{len(st.session_state.questions)}")
    with col2:
        st.metric("정답", f"{st.session_state.correct_count}")
    with col3:
        accuracy = (st.session_state.correct_count / (st.session_state.current_question - 1) * 100) if st.session_state.current_question > 1 else 0
        st.metric("정답률", f"{accuracy:.1f}%")
    
    st.markdown("---")
    
    # 문제 출제
    st.markdown(f"### 문제 {st.session_state.current_question}")
    st.markdown(f"## {num1} {operator} {num2} = ?")
    
    # 답 입력
    # 경과 시간 표시
    if 'question_start_time' in st.session_state:
        elapsed = time.time() - st.session_state.question_start_time
        remaining = max(0, 5 - elapsed)
        if remaining > 0:
            st.markdown(f"### ⏰ 남은 시간: {remaining:.1f}초")
        else:
            st.markdown("### ⏰ 시간 초과!")
    
    with st.form(key=f"question_{st.session_state.current_question}"):
        user_input = st.text_input("답을 입력하세요:", key="answer_input")
        submitted = st.form_submit_button("제출", use_container_width=True, type="primary")
        
        if submitted:
            st.session_state.user_answer = user_input
            is_correct, message = check_answer()
            
            if "5초가 지났습니다" in message:
                st.warning(f"⏰ {message}")
            elif is_correct:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
            
            time.sleep(1.5)  # 1.5초 대기 (메시지 읽을 시간)
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
    
    st.markdown("## 🎉 게임 완료!")
    
    # 결과 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="총 문제 수",
            value=f"{total_questions}개"
        )
    with col2:
        st.metric(
            label="정답 수",
            value=f"{st.session_state.correct_count}개"
        )
    with col3:
        st.metric(
            label="정답률",
            value=f"{accuracy:.1f}%"
        )
    
    # 성적에 따른 메시지
    if accuracy == 100:
        st.markdown("<div style='text-align: center;'><h3 style='color: green;'>🏆 완벽합니다! 천재군요!</h3></div>", unsafe_allow_html=True)
    elif accuracy >= 80:
        st.markdown("<div style='text-align: center;'><h3 style='color: green;'>🌟 훌륭해요!</h3></div>", unsafe_allow_html=True)
    elif accuracy >= 60:
        st.markdown("<div style='text-align: center;'><h3 style='color: blue;'>👍 잘했어요!</h3></div>", unsafe_allow_html=True)
    elif accuracy >= 40:
        st.markdown("<div style='text-align: center;'><h3 style='color: orange;'>💪 조금만 더 연습하면 완벽해질 거예요!</h3></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center;'><h3 style='color: red;'>📚 더 연습해보세요!</h3></div>", unsafe_allow_html=True)
    
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
