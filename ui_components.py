# ui_components.py - UI 컴포넌트 관리 모듈

import streamlit as st
from typing import Dict, Any, Optional
from config import GameConfig, UIConfig
from game_logic import performance_evaluator
import streamlit.components.v1 as components


class GameSetupUI:
    """게임 설정 UI 컴포넌트"""
    
    @staticmethod
    def render_game_rules():
        """게임 규칙 설명 렌더링"""
        with st.expander("💡 게임 규칙 살펴보기"):
            st.markdown("""
            * **연산 타입**을 선택하고 **문제 개수**와 **제한 시간**을 설정하세요.
            * 주어진 시간 안에 정답을 입력하고 **제출** 버튼을 누르세요.
            * 시간이 지나면 자동으로 다음 문제로 넘어갑니다.
            * 게임이 끝나면 당신의 점수와 전체 사용자 통계를 확인할 수 있습니다!
            """)
    
    @staticmethod
    def render_operation_selector() -> str:
        """연산 타입 선택기 렌더링"""
        return st.selectbox(
            "➕➖ 연산 타입",
            UIConfig.OPERATION_TYPES
        )
    
    @staticmethod
    def render_counter(label: str, value: int, min_val: int, max_val: int, 
                      key_prefix: str, unit: str = "개") -> int:
        """카운터 UI 렌더링 (문제 개수, 제한 시간)"""
        st.markdown(f"### {label}")
        
        col_minus, col_text, col_plus = st.columns([1, 1, 1])
        
        with col_minus:
            if st.button("➖", key=f"{key_prefix}_minus", use_container_width=True):
                if value > min_val:
                    return value - 1
        
        with col_text:
            st.markdown(
                f"<h3 style='text-align: center; vertical-align: middle; line-height: 2.2;'>{value}{unit}</h3>",
                unsafe_allow_html=True
            )
        
        with col_plus:
            if st.button("➕", key=f"{key_prefix}_plus", use_container_width=True):
                if value < max_val:
                    return value + 1
        
        return value

class GamePlayUI:
    """게임 플레이 UI 컴포넌트"""
    
    @staticmethod
    def render_game_header(current_question: int, total_questions: int, 
                          correct_count: int, accuracy: float):
        """게임 헤더 (진행률, 통계) 렌더링"""
        st.markdown('<div class="game-header-container">', unsafe_allow_html=True)
        
        # 진행률 표시
        progress = (current_question - 1) / total_questions
        st.progress(progress, text=f"문제 {current_question}/{total_questions}")
        
        # 현재 통계
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="✔️ 정답 수", value=f"{correct_count}")
        with col2:
            st.metric(label="📈 정답률", value=f"{accuracy:.1f}%")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    @staticmethod
    def render_question_display(question_text: str):
        """문제 표시 영역 렌더링"""
        st.markdown("---")
        st.markdown(f"### 문제 {st.session_state.get('current_question_num', 1)}")
        st.markdown(
            f'<div class="question-display"><h2>{question_text}</h2></div>',
            unsafe_allow_html=True
        )
    
    @staticmethod
    def render_timer(remaining_time: float, total_time: int) -> st.empty:
        """타이머 진행바 렌더링"""
        if remaining_time <= 0:
            st.warning("⏳ 시간 초과! 다음 문제로 넘어갑니다.")
            return None
        
        time_progress = 1 - (remaining_time / total_time)
        progress_bar = st.progress(0)
        progress_bar.progress(time_progress, text=f"⏱️ 남은 시간: {remaining_time:.1f}초")
        
        return progress_bar
    
    @staticmethod
    def render_answer_form(question_key: str) -> tuple:
        """답안 입력 폼 렌더링"""
        with st.form(key=f"question_{question_key}"):
            user_input = st.text_input(
                "답을 입력하세요:", 
                key=f"answer_input_{question_key}",
                placeholder="숫자를 입력하세요"
            )
            submitted = st.form_submit_button("제출", use_container_width=True, type="primary")
        
        # 정교한 포커스 스크립트 - 특정 input 타겟팅
        st.components.v1.html(f"""
            <script>
            (function() {{
                let attemptCount = 0;
                const maxAttempts = 15;
                const questionKey = "{question_key}";
                
                function focusSpecificInput() {{
                    attemptCount++;
                    console.log(`포커스 시도 ${{attemptCount}}/${{maxAttempts}} - 문제 ${{questionKey}}`);
                    
                    try {{
                        const doc = window.parent ? window.parent.document : document;
                        let targetInput = null;
                        
                        // 방법 1: 현재 문제의 특정 input 찾기 (key 기반)
                        const keySelectors = [
                            `input[data-testid*="answer_input_${{questionKey}}"]`,
                            `input[aria-label*="답을 입력하세요"]`,
                            `input[placeholder*="숫자를 입력하세요"]`
                        ];
                        
                        for (const selector of keySelectors) {{
                            targetInput = doc.querySelector(selector);
                            if (targetInput) {{
                                console.log(`선택자로 찾음: ${{selector}}`);
                                break;
                            }}
                        }}
                        
                        // 방법 2: 폼 컨테이너 내부에서 찾기
                        if (!targetInput) {{
                            const forms = doc.querySelectorAll('form[data-testid*="question_${{questionKey}}"], form[data-testid*="form"]');
                            for (const form of forms) {{
                                const formInput = form.querySelector('input[type="text"]');
                                if (formInput) {{
                                    targetInput = formInput;
                                    console.log('폼 내부에서 찾음');
                                    break;
                                }}
                            }}
                        }}
                        
                        // 방법 3: 가장 최근 활성 input (fallback)
                        if (!targetInput) {{
                            const allInputs = Array.from(doc.querySelectorAll('input[type="text"]:not([readonly]):not([disabled])'));
                            // 보이는 input만 필터링
                            const visibleInputs = allInputs.filter(input => {{
                                const rect = input.getBoundingClientRect();
                                return rect.width > 0 && rect.height > 0;
                            }});
                            
                            if (visibleInputs.length > 0) {{
                                targetInput = visibleInputs[visibleInputs.length - 1];
                                console.log('최근 활성 input 사용');
                            }}
                        }}
                        
                        // 포커스 적용
                        if (targetInput && doc.activeElement !== targetInput) {{
                            targetInput.focus();
                            
                            // 기존 값이 있으면 선택, 없으면 커서만 설정
                            setTimeout(() => {{
                                if (targetInput.value && targetInput.value.trim() !== '') {{
                                    targetInput.select();
                                }}
                            }}, 10);
                            
                            console.log(`✅ 포커스 성공: 문제 ${{questionKey}}`);
                            return true;
                        }}
                        
                        // 재시도 조건
                        if (attemptCount < maxAttempts) {{
                            setTimeout(focusSpecificInput, attemptCount < 5 ? 100 : 200);
                        }} else {{
                            console.log(`❌ 포커스 실패: 문제 ${{questionKey}} (최대 시도 도달)`);
                        }}
                        
                        return false;
                    }} catch (e) {{
                        console.log(`포커스 에러: ${{e.message}}`);
                        if (attemptCount < maxAttempts) {{
                            setTimeout(focusSpecificInput, 200);
                        }}
                        return false;
                    }}
                }}
                
                // 즉시 실행
                focusSpecificInput();
                
                // 추가 시도들 (다양한 타이밍)
                setTimeout(focusSpecificInput, 50);
                setTimeout(focusSpecificInput, 150);
                setTimeout(focusSpecificInput, 300);
                setTimeout(focusSpecificInput, 500);
                
                // DOM 변경 감지
                const observer = new MutationObserver(function(mutations) {{
                    let shouldFocus = false;
                    
                    mutations.forEach(function(mutation) {{
                        if (mutation.type === 'childList') {{
                            mutation.addedNodes.forEach(node => {{
                                if (node.nodeType === 1) {{ // Element node
                                    if (node.matches && node.matches('input[type="text"]')) {{
                                        shouldFocus = true;
                                    }} else if (node.querySelector) {{
                                        const inputs = node.querySelectorAll('input[type="text"]');
                                        if (inputs.length > 0) {{
                                            shouldFocus = true;
                                        }}
                                    }}
                                }}
                            }});
                        }}
                    }});
                    
                    if (shouldFocus) {{
                        console.log('DOM 변경 감지 - 포커스 재시도');
                        setTimeout(focusSpecificInput, 50);
                    }}
                }});
                
                observer.observe(document.body, {{
                    childList: true,
                    subtree: true
                }});
                
                // observer 정리 (메모리 누수 방지)
                setTimeout(() => {{
                    observer.disconnect();
                    console.log('Observer 정리됨');
                }}, 5000);
            }})();
            </script>
        """, height=0)
        
        return user_input, submitted

class GameResultUI:
    """게임 결과 UI 컴포넌트"""
    
    @staticmethod
    def render_result_summary(results: Dict[str, Any]):
        """결과 요약 렌더링"""
        st.balloons()
        st.markdown("## ✨ 게임 완료!")
        
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 20px;'>
          <div style='margin-bottom: 10px;'>
            총 문제 수: <b>{results['total_questions']}개</b>
          </div>
          <div style='margin-bottom: 10px;'>
            정답 수: <b>{results['correct_count']}개</b>
          </div>
          <div style='margin-bottom: 10px;'>
            정답률: <b>{results['accuracy']:.1f}%</b>
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 성과 메시지
        icon, message, style = performance_evaluator.get_performance_message(results['accuracy'])
        GameResultUI._render_performance_message(icon, message, style)
    
    @staticmethod
    def _render_performance_message(icon: str, message: str, style: str):
        """성과 메시지 렌더링"""
        color_map = {
            'success': 'green',
            'info': 'blue', 
            'warning': 'orange',
            'error': 'red'
        }
        color = color_map.get(style, 'black')
        
        st.markdown(
            f"<div style='text-align: center;'><h4 style='color: {color};'>{icon} {message}</h4></div>",
            unsafe_allow_html=True
        )
    
    @staticmethod
    def render_global_statistics(global_stats: Optional[Dict[str, Any]], user_accuracy: float):
        """전체 사용자 통계 렌더링"""
        st.markdown("---")
        st.markdown("### 📈 실시간 전체 사용자 통계")
        
        if not global_stats:
            st.warning("⚠️ Google Sheets가 연결되지 않아 전체 통계를 표시할 수 없습니다.")
            return
        
        # 전체 통계 박스
        GameResultUI._render_statistics_box(global_stats)
        
        # 사용자 순위 표시
        GameResultUI._render_user_ranking(global_stats, user_accuracy)
    
    @staticmethod
    def _render_statistics_box(stats: Dict[str, Any]):
        """통계 박스 렌더링"""
        st.markdown(f"""
        <div class='stats-container'>
          <div style='text-align: center; margin-bottom: 15px;'>
            <div style='font-size: 1.1rem; color: #333; font-weight: bold; margin-bottom: 15px;'>
              🌟 지금까지 총 <span style='color: #1f77b4; font-size: 1.3rem;'>{stats['total_games']:,}명</span>이 도전했습니다!
            </div>
            <div style='font-size: 0.9rem; color: #666; margin-bottom: 10px;'>
              📈 전체 평균 정답률: <span style='font-weight: bold; color: #333;'>{stats['average_accuracy']:.1f}%</span>
            </div>
          </div>
          
          <div style='font-size: 0.95rem; color: #666; margin-bottom: 8px;'>
            🏆 100% 달성자: <span style='font-weight: bold; color: #333;'>{stats['perfect_count']}명</span> 
            <span style='color: #28a745;'>({stats['perfect_rate']:.1f}%)</span>
          </div>
          
          <div style='font-size: 0.95rem; color: #666; margin-bottom: 8px;'>
            🌟 90% 이상 달성자: <span style='font-weight: bold; color: #333;'>{stats['great_count']}명</span> 
            <span style='color: #28a745;'>({stats['great_rate']:.1f}%)</span>
          </div>
          
          <div style='font-size: 0.95rem; color: #666; margin-bottom: 8px;'>
            👍 80% 이상 달성자: <span style='font-weight: bold; color: #333;'>{stats['good_count']}명</span> 
            <span style='color: #007bff;'>({stats['good_rate']:.1f}%)</span>
          </div>
          
          <div style='font-size: 0.95rem; color: #666; margin-bottom: 8px;'>
            💪 70% 이상 달성자: <span style='font-weight: bold; color: #333;'>{stats['okay_count']}명</span> 
            <span style='color: #ffc107;'>({stats['okay_rate']:.1f}%)</span>
          </div>
          
          <div style='font-size: 0.95rem; color: #666; margin-bottom: 15px;'>
            📚 70% 미만 달성자: <span style='font-weight: bold; color: #333;'>{stats['poor_count']}명</span> 
            <span style='color: #dc3545;'>({stats['poor_rate']:.1f}%)</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def _render_user_ranking(stats: Dict[str, Any], user_accuracy: float):
        """사용자 순위 렌더링"""
        from sheets_manager import sheets_manager
        
        rank_text = sheets_manager.get_user_rank(user_accuracy, stats['accuracy_list'])
        percentile = float(rank_text.replace('상위 ', '').replace('%', ''))
        
        st.markdown(f"""
        <div style='text-align: center; padding: 15px; background-color: #f0f2f6; border-radius: 10px; margin: 10px 0;'>
          <div style='font-size: 1.1rem; font-weight: bold; color: #dc3545;'>
            🎯 당신은 <span style='font-size: 1.2rem;'>{rank_text}</span> 입니다!
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 순위별 격려 메시지
        rank_message = performance_evaluator.get_rank_message(percentile)
        color = "gold" if percentile <= 10 else "green" if percentile <= 25 else "blue" if percentile <= 50 else "orange"
        
        st.markdown(
            f"<div style='text-align: center;'><h4 style='color: {color};'>{rank_message}</h4></div>",
            unsafe_allow_html=True
        )
    
    @staticmethod
    def render_action_buttons():
        """게임 완료 후 액션 버튼들 렌더링"""
        col1, col2 = st.columns(2)
        
        with col1:
            restart_same = st.button("🔄 다시 하기", use_container_width=True, type="primary")
        
        with col2:
            change_settings = st.button("🛠️ 설정 변경", use_container_width=True, type="secondary")
        
        return restart_same, change_settings

class CommonUI:
    """공통 UI 컴포넌트"""
    
    @staticmethod
    def render_page_header():
        """페이지 헤더 렌더링"""
        st.markdown(
            f"<h2 style='text-align: center;'>{UIConfig.PAGE_ICON} {UIConfig.PAGE_TITLE}</h2>", 
            unsafe_allow_html=True
        )
    
    @staticmethod
    def render_footer():
        """페이지 푸터 렌더링"""
        st.markdown("---")
        st.markdown("<div style='text-align: center;'>Made with ❤️ using Streamlit</div>", unsafe_allow_html=True)
    
    @staticmethod
    def show_feedback_message(is_correct: bool, message: str, is_timeout: bool = False):
        """피드백 메시지 표시"""
        if is_timeout:
            st.warning(f"⏳ {message}")
        elif is_correct:
            st.success(f"✔️ {message}")
        else:
            st.error(f"✖️ {message}")

# UI 컴포넌트 인스턴스들
game_setup_ui = GameSetupUI()
game_play_ui = GamePlayUI() 
game_result_ui = GameResultUI()
common_ui = CommonUI()
