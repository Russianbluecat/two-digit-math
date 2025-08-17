# config.py - 게임 설정 및 상수 관리

class GameConfig:
    """게임 설정 관련 상수"""
    # 문제 수 설정
    MIN_QUESTIONS = 5
    MAX_QUESTIONS = 20
    DEFAULT_QUESTIONS = 10
    
    # 시간 제한 설정
    MIN_TIME_LIMIT = 3
    MAX_TIME_LIMIT = 10
    DEFAULT_TIME_LIMIT = 5
    
    # 숫자 범위 설정
    MIN_NUMBER = 10
    MAX_NUMBER = 99
    
    # 점수 기준
    SCORE_PERFECT = 100
    SCORE_GREAT = 90
    SCORE_GOOD = 80
    SCORE_OKAY = 70
    
    # 입력 검증 범위
    MIN_ANSWER = -999
    MAX_ANSWER = 999

class UIConfig:
    """UI 관련 상수"""
    # 페이지 설정
    PAGE_TITLE = "두 자리 수 암산 게임"
    PAGE_ICON = "🧮"
    
    # 색상 테마
    PRIMARY_COLOR = "#007bff"
    SUCCESS_COLOR = "#28a745"
    WARNING_COLOR = "#ffc107"
    DANGER_COLOR = "#dc3545"
    
    # 메시지
    MESSAGES = {
        'perfect': ("🏆", "완벽합니다! 천재군요!", "success"),
        'great': ("🌟", "훌륭해요!", "success"),
        'good': ("👍", "잘했어요!", "info"),
        'okay': ("💪", "조금만 더 연습하면 완벽해질 거예요!", "warning"),
        'poor': ("📚", "더 연습해보세요!", "error")
    }
    
    # 연산 타입
    OPERATION_TYPES = ["덧셈", "뺄셈", "랜덤 (덧셈+뺄셈)"]

class SheetsConfig:
    """Google Sheets 관련 설정"""
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    # 기본 시트 ID (fallback)
    DEFAULT_SHEET_ID = "1zVQMc_cKkXNTTTRMzDsyRrQS_i45iulV63l6JARy0tc"
    
    # 저장할 데이터 컬럼
    COLUMNS = [
        "날짜", "시간", "총 문제수", "정답수", 
        "정답률", "연산타입", "제한시간", "소요시간"
    ]

class ErrorMessages:
    """에러 메시지 상수"""
    INVALID_NUMBER = "숫자만 입력 가능합니다"
    NUMBER_OUT_OF_RANGE = "값은 {min_val}과 {max_val} 사이여야 합니다"
    TIME_UP = "시간 초과! 다음 문제로 넘어갑니다"
    SHEETS_CONNECTION_ERROR = "Google Sheets 설정이 필요합니다. 로컬 저장만 사용됩니다"
    SHEETS_SAVE_ERROR = "데이터 저장 중 오류가 발생했습니다"
    SHEETS_LOAD_ERROR = "통계 조회 중 오류가 발생했습니다"
