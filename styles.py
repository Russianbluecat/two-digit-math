# styles.py - CSS 스타일 관리

def get_custom_css():
    """커스텀 CSS 스타일을 반환"""
    return """
    <style>
        /* 기본 테마 색상 재정의 */
        :root {
            --primary-color: #007bff;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --light-bg: #f8f9fa;
            --border-color: #e0e0e0;
        }
        
        /* 버튼 스타일 */
        div.stButton > button {
            border-radius: 12px;
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.15);
            transition: all 0.3s ease;
            font-weight: 500;
        }
        
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 4px 4px 12px rgba(0, 0, 0, 0.2);
            background-color: #dc3545 !important;  /* 더 진한 빨간색 */
            color: white !important;               /* 흰 글씨 */
            border-color: #ff0000 !important;      /* 빨간 테두리 */
        }
        
        .stButton button {
            border: 1px solid var(--primary-color);
            color: var(--primary-color);
            background-color: transparent;
        }
        
        /* 입력 필드 스타일 */
        .stTextInput > div > div > input {
            border-radius: 12px;
            box-shadow: inset 2px 2px 5px rgba(0, 0, 0, 0.1);
            border: 1px solid #ccc;
            font-size: 1.1rem;
            padding: 12px;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }
        
        /* 제목 및 텍스트 중앙 정렬 */
        h1, h2, h3, h4, h5, h6 {
            text-align: center;
        }
        
        /* 메트릭 스타일 */
        div[data-testid="stMetric"] {
            text-align: center;
            background-color: var(--light-bg);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid var(--border-color);
        }
        
        div[data-testid="stMetricValue"] {
            font-size: 2.5rem !important;
            font-weight: bold;
        }
        
        div[data-testid="stMetricLabel"] {
            font-size: 1rem;
            color: #666;
        }
        
        /* 게임 헤더 고정 */
        .game-header-container {
            position: sticky;
            top: 0;
            background-color: white;
            z-index: 999;
            padding: 10px 0;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* 문제 표시 영역 */
        .question-display {
            background-color: var(--light-bg);
            padding: 30px;
            border-radius: 15px;
            margin: 20px 0;
            border: 2px solid var(--border-color);
            text-align: center;
        }
        
        .question-display h2 {
            font-size: 3rem;
            margin: 10px 0;
            color: var(--primary-color);
        }
        
        /* 시간 진행바 스타일 */
        .stProgress .st-bo {
            background-color: var(--success-color);
        }
        
        /* 통계 박스 */
        .stats-container {
            background-color: var(--light-bg);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            border: 1px solid var(--border-color);
        }
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {
            h1, h2 {
                font-size: 1.5rem;
            }
            
            h3 {
                font-size: 1.2rem;
            }
            
            .question-display h2 {
                font-size: 2rem;
            }
            
            div.stButton > button {
                font-size: 0.9rem;
                padding: 8px 12px;
            }
            
            div[data-testid="stMetricValue"] {
                font-size: 2rem !important;
            }
            
            .stTextInput > div > div > input {
                font-size: 1rem;
                padding: 10px;
            }
        }
        
        @media (max-width: 480px) {
            .question-display {
                padding: 20px;
                margin: 10px 0;
            }
            
            .question-display h2 {
                font-size: 1.8rem;
            }
            
            .stats-container {
                padding: 15px;
            }
        }
        
        /* 접근성 개선 */
        .stButton > button:focus,
        .stTextInput > div > div > input:focus {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
        }
        
        /* 애니메이션 */
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .shake {
            animation: shake 0.5s ease-in-out;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .pulse {
            animation: pulse 0.6s ease-in-out;
        }
    </style>
    """

def get_google_analytics():
    """Google Analytics 코드를 반환"""
    return """
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-4Q1S1M127P"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-4Q1S1M127P');
    </script>
    """

def get_auto_focus_script():
    """자동 포커스 JavaScript 코드를 반환"""
    return """
    <script>
    function focusInput() {
        try {
            // Streamlit iframe 환경에서 document 접근
            const doc = window.parent ? window.parent.document : document;
            
            // 활성화된 text input 찾기 (readonly가 아닌 것들만)
            const inputs = doc.querySelectorAll('input[type="text"]:not([readonly]):not([disabled])');
            
            if (inputs.length > 0) {
                const lastInput = inputs[inputs.length - 1];
                
                // 포커스가 이미 있는지 확인
                if (doc.activeElement !== lastInput) {
                    lastInput.focus();
                    
                    // 기존 값이 있으면 선택, 없으면 커서만 설정
                    if (lastInput.value && lastInput.value.trim() !== '') {
                        lastInput.select();
                    }
                }
                return true;
            }
            return false;
        } catch (e) {
            // iframe 접근 실패시 일반 document 사용
            try {
                const inputs = document.querySelectorAll('input[type="text"]:not([readonly]):not([disabled])');
                if (inputs.length > 0) {
                    const lastInput = inputs[inputs.length - 1];
                    if (document.activeElement !== lastInput) {
                        lastInput.focus();
                        if (lastInput.value && lastInput.value.trim() !== '') {
                            lastInput.select();
                        }
                    }
                    return true;
                }
            } catch (e2) {
                console.log('Focus failed:', e2);
            }
            return false;
        }
    }
    
    // 즉시 실행
    focusInput();
    
    // 여러 시점에서 재시도 (Streamlit 리렌더링 대응)
    const timeouts = [50, 100, 200, 300, 500, 800, 1000, 1500];
    timeouts.forEach(delay => {
        setTimeout(() => {
            if (!focusInput()) {
                // 실패시 한 번 더 시도
                setTimeout(focusInput, 100);
            }
        }, delay);
    });
    
    // DOM 변경 감지 및 자동 포커스
    function setupMutationObserver() {
        const doc = window.parent ? window.parent.document : document;
        
        const observer = new MutationObserver(function(mutations) {
            let shouldFocus = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    // 새로운 input이 추가되었는지 확인
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1) { // Element node
                            if (node.matches && node.matches('input[type="text"]')) {
                                shouldFocus = true;
                            } else if (node.querySelector) {
                                const inputs = node.querySelectorAll('input[type="text"]');
                                if (inputs.length > 0) {
                                    shouldFocus = true;
                                }
                            }
                        }
                    });
                }
            });
            
            if (shouldFocus) {
                setTimeout(focusInput, 50);
                setTimeout(focusInput, 150);
            }
        });
        
        observer.observe(doc.body, {
            childList: true,
            subtree: true
        });
        
        // 5초 후 observer 정리 (메모리 누수 방지)
        setTimeout(() => observer.disconnect(), 5000);
    }
    
    // DOM이 준비된 후 observer 설정
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupMutationObserver);
    } else {
        setupMutationObserver();
    }
    
    // 추가 보험: 페이지 visibility 변경시에도 포커스 시도
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden) {
            setTimeout(focusInput, 100);
        }
    });
    </script>
    """
