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
if 'question_count' not in st.session_state:
    st.session_state.question_count = 10
if 'time_limit' not in st.session_state:
    st.session_state.time_limit = 5

def generate_question(operation_type):
    """문제 생성 함수"""
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
    st.session_state.operation_type = operation_type
    
    # 모든 문제 미리 생성
    for _ in range(question_count):
        question = generate_question(operation_type)
        st.session_state.questions.append(question)
    
    st.session_state.start_time = time.time()

def check_answer():
    """답안 체크 (시간 제한 포함)"""
    try:
        current_time = time.time()
        elapsed_time = current_time - st.session_state.question_start_time
        time_limit = st.session_state.time_limit
        
        if elapsed_time > time_limit:
            return False, f"⏰ {time_limit}초가 지났습니다! 다음 문제로 넘어갑니다."
            
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
    st.session_state.question_start_time = time.time()
    
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

# 메인 UI (상단 여백 제거)
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
        
        # 문제 개수 컨트롤 UI
        st.markdown(f"""
        <div class="control-container">
            <div class="control-button" onclick="decreaseQuestions()">➖</div>
            <div class="black-bg-text">{st.session_state.question_count}개</div>
            <div class="control-button" onclick="increaseQuestions()">➕</div>
        </div>
        """, unsafe_
