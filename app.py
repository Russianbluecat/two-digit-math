import streamlit as st
import random
import time

st.set_page_config(page_title="두 자리 연산 게임", layout="centered")

# ===== 세션 상태 초기화 =====
if "score" not in st.session_state:
    st.session_state.score = 0
if "question" not in st.session_state:
    st.session_state.question = ""
if "answer" not in st.session_state:
    st.session_state.answer = ""
if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
if "game_over" not in st.session_state:
    st.session_state.game_over = False

# ===== 문제 생성 함수 =====
def generate_question():
    a = random.randint(10, 99)
    b = random.randint(10, 99)
    op = random.choice(["+", "-"])
    return f"{a} {op} {b}"

# ===== 첫 문제 =====
if st.session_state.question == "":
    st.session_state.question = generate_question()

# ===== 자동 포커스 스크립트 =====
focus_script = """
<script>
window.onload = function() {
    const inputBox = document.getElementById("answer_input");
    if (inputBox) { inputBox.focus(); }
};
</script>
"""

# ===== 타이머 (60초 제한 예시) =====
elapsed = int(time.time() - st.session_state.start_time)
remaining_time = max(0, 60 - elapsed)
st.write(f"남은 시간: **{remaining_time}초**")

if remaining_time <= 0:
    st.session_state.game_over = True

# ===== 게임 진행 =====
if not st.session_state.game_over:
    st.write(f"**문제:** {st.session_state.question}")

    # 입력창 (HTML로 구현, id 부여)
    st.markdown(
        f"""
        <input type="text" id="answer_input" name="answer" 
               style="font-size:24px; padding:8px; width:200px;" 
               value="{st.session_state.answer}">
        """,
        unsafe_allow_html=True
    )

    # 제출 버튼
    if st.button("제출"):
        try:
            # 정답 체크
            if eval(st.session_state.question) == int(st.session_state.answer):
                st.session_state.score += 1
        except:
            pass
        # 다음 문제 생성 & 입력 초기화
        st.session_state.question = generate_question()
        st.session_state.answer = ""
        # 자동 포커스 실행
        st.markdown(focus_script, unsafe_allow_html=True)

    # 처음 로딩 시 자동 포커스
    st.markdown(focus_script, unsafe_allow_html=True)

else:
    st.write("⏰ 게임 종료!")
    st.write(f"당신의 점수: **{st.session_state.score}**")

