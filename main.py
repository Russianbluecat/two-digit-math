# main.py - 개선된 메인 애플리케이션

import streamlit as st
import time

# 로컬 모듈 임포트
from config import GameConfig, UIConfig
from styles import get_custom_css, get_google_analytics, get_auto_focus_script
from game_logic import game_session, QuestionGenerator
from sheets_manager import sheets_manager
from ui_components import game_setup_ui, game_play_ui, game_result_ui, common_ui
from validation import input_validator

class GameStates:
    """게임 상태 상수"""
    SETUP = 'setup'
    PLAYING = 'playing'  
    FINISHED = 'finished'

def initialize_session_state():
    """세션 상태 초기화"""
    defaults = {
        'game_state': GameStates.SETUP,
        'question_count': GameConfig.DEFAULT_QUESTIONS,
        'time_limit': GameConfig.DEFAULT_TIME_LIMIT,
        'operation_type': UIConfig.OPERATION_TYPES[0],
        'current_question_num': 1,
        'total_games': 0,
        'total_questions': 0,
        'total_correct': 0,
        'best_streak': 0,
        'current_streak': 0
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def setup_page():
    """페이지 기본 설정"""
    st.set_page_config(
        page_title=UIConfig.PAGE_TITLE,
        page_icon=UIConfig.PAGE_ICON,
        layout="centered"
    )
    
    # 스타일 및 스크립트 적용
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    st.markdown(get_google_analytics(), unsafe_allow_html=True)

def handle_game_setup():
    """게임 설정 화면 처리"""
    st.markdown("### ⚙️ 게임 설정")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        # 게임 규칙 설명
        game_setup_ui.render_game_rules()
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 연산 타입 선택
        operation_type = game_setup_ui.render_operation_selector()
        st.session_state.operation_type = operation_type
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 문제 개수 설정
        st.session_state.question_count = game_setup_ui.render_counter(
            "🔢 문제 개수",
            st.session_state.question_count,
            GameConfig.MIN_QUESTIONS,
            GameConfig.MAX_QUESTIONS,
            "question",
            "개"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 제한 시간 설정
        st.session_state.time_limit = game_setup_ui.render_counter(
            "⏱️ 제한시간",
            st.session_state.time_limit,
            GameConfig.MIN_TIME_LIMIT,
            GameConfig.MAX_TIME_LIMIT,
            "time",
            "초"
        )
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # 게임 시작 버튼
        if st.button("🚀 게임 시작!", use_container_width=True, type="primary"):
            try:
                game_session.start_game(
                    st.session_state.operation_type,
                    st.session_state.question_count,
                    st.session_state.time_limit
                )
                st.session_state.game_state = GameStates.PLAYING
                st.session_state.current_question_num = 1
                st.rerun()
            except ValueError as e:
                st.error(f"설정 오류: {str(e)}")

def handle_game_play():
    """게임 플레이 화면 처리"""
    # 자동 포커스 스크립트 적용
    st.markdown(get_auto_focus_script(), unsafe_allow_html=True)
    
    # 현재 문제 가져오기
    current_question = game_session.get_current_question()
    if not current_question:
        st.error("문제를 불러올 수 없습니다.")
        return
    
    # 게임 헤더 표시
    current_num, total_num = game_session.get_game_progress()
    current_accuracy = game_session.get_current_accuracy()
    
    game_play_ui.render_game_header(
        current_num, total_num,
        game_session.correct_count, current_accuracy
    )
    
    # 문제 표시
    st.session_state.current_question_num = current_num
    game_play_ui.render_question_display(str(current_question))
    
    # 시간 제한 확인 및 타이머 표시
    is_time_valid, remaining_time = game_session.check_time_limit()
    remaining = max(0, st.session_state.time_limit - remaining_time)
    
    timer_bar = game_play_ui.render_timer(remaining, st.session_state.time_limit)
    
    # 시간 초과 처리
    if not is_time_valid:
        if timer_bar:
            timer_bar.empty()
        st.session_state.current_streak = 0
        time.sleep(1.0)
        game_session.next_question()
        
        if game_session.is_game_finished():
            st.session_state.game_state = GameStates.FINISHED
        st.rerun()
    
    # 답안 입력 폼
    user_input, submitted = game_play_ui.render_answer_form(str(current_num))
    
    # 답안 제출 처리
    if submitted and user_input.strip():
        is_correct, message, is_timeout = game_session.submit_answer(user_input)
        
        # 연속 정답 처리
        if is_correct:
            st.session_state.current_streak += 1
            if st.session_state.current_streak > st.session_state.best_streak:
                st.session_state.best_
