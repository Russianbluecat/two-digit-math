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
        const inputs = window.parent.document.querySelectorAll('input[type="text"]');
        if (inputs.length > 0) {
            const lastInput = inputs[inputs.length - 1];
            lastInput.focus();
            lastInput.select();
        }
    }
    
    setTimeout(focusInput, 100);
    setTimeout(focusInput, 300);
    setTimeout(focusInput, 500);
    </script>
    """
