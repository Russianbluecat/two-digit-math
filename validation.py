# validation.py - 입력 검증 및 유틸리티 함수

from typing import Tuple, Union
from config import GameConfig, ErrorMessages
import re

class InputValidator:
    """사용자 입력 검증을 위한 클래스"""
    
    @staticmethod
    def validate_number_input(user_input: str, 
                            min_val: int = GameConfig.MIN_ANSWER, 
                            max_val: int = GameConfig.MAX_ANSWER) -> Tuple[bool, Union[int, str]]:
        """
        숫자 입력을 검증합니다.
        
        Args:
            user_input (str): 사용자 입력 문자열
            min_val (int): 최소값
            max_val (int): 최대값
            
        Returns:
            Tuple[bool, Union[int, str]]: (성공여부, 변환된_값_또는_에러메시지)
        """
        if not user_input or not user_input.strip():
            return False, ErrorMessages.INVALID_NUMBER
            
        # 공백 제거 및 기본 정리
        cleaned_input = user_input.strip()
        
        # 숫자와 음수 기호만 허용하는 정규표현식
        if not re.match(r'^-?\d+$', cleaned_input):
            return False, ErrorMessages.INVALID_NUMBER
        
        try:
            value = int(cleaned_input)
            
            if min_val <= value <= max_val:
                return True, value
            else:
                return False, ErrorMessages.NUMBER_OUT_OF_RANGE.format(
                    min_val=min_val, max_val=max_val
                )
                
        except ValueError:
            return False, ErrorMessages.INVALID_NUMBER
    
    @staticmethod
    def validate_question_count(count: int) -> bool:
        """문제 개수 유효성 검증"""
        return GameConfig.MIN_QUESTIONS <= count <= GameConfig.MAX_QUESTIONS
    
    @staticmethod
    def validate_time_limit(time_limit: int) -> bool:
        """제한 시간 유효성 검증"""
        return GameConfig.MIN_TIME_LIMIT <= time_limit <= GameConfig.MAX_TIME_LIMIT
    
    @staticmethod
    def sanitize_string_input(text: str, max_length: int = 100) -> str:
        """문자열 입력 정리 및 검증"""
        if not text:
            return ""
        
        # 기본 정리: 앞뒤 공백 제거, 길이 제한
        cleaned = text.strip()[:max_length]
        
        # HTML/JavaScript 태그 제거 (기본적인 XSS 방지)
        cleaned = re.sub(r'<[^>]*>', '', cleaned)
        
        return cleaned

class GameValidator:
    """게임 로직 검증을 위한 클래스"""
    
    @staticmethod
    def is_valid_operation_type(operation_type: str) -> bool:
        """연산 타입 유효성 검증"""
        from config import UIConfig
        return operation_type in UIConfig.OPERATION_TYPES
    
    @staticmethod
    def validate_game_settings(question_count: int, time_limit: int, operation_type: str) -> Tuple[bool, str]:
        """게임 설정 전체 유효성 검증"""
        if not InputValidator.validate_question_count(question_count):
            return False, f"문제 개수는 {GameConfig.MIN_QUESTIONS}개에서 {GameConfig.MAX_QUESTIONS}개 사이여야 합니다."
        
        if not InputValidator.validate_time_limit(time_limit):
            return False, f"제한 시간은 {GameConfig.MIN_TIME_LIMIT}초에서 {GameConfig.MAX_TIME_LIMIT}초 사이여야 합니다."
        
        if not GameValidator.is_valid_operation_type(operation_type):
            return False, "올바르지 않은 연산 타입입니다."
        
        return True, "설정이 유효합니다."
    
    @staticmethod
    def validate_answer_timing(start_time: float, current_time: float, time_limit: int) -> Tuple[bool, float]:
        """답변 시간 검증"""
        elapsed = current_time - start_time
        return elapsed <= time_limit, elapsed

class DataValidator:
    """데이터 검증을 위한 클래스"""
    
    @staticmethod
    def validate_accuracy_data(correct_count: int, total_questions: int) -> Tuple[bool, str]:
        """정확도 계산을 위한 데이터 검증"""
        if total_questions <= 0:
            return False, "총 문제 수는 0보다 커야 합니다."
        
        if correct_count < 0:
            return False, "정답 수는 0 이상이어야 합니다."
        
        if correct_count > total_questions:
            return False, "정답 수는 총 문제 수를 초과할 수 없습니다."
        
        return True, "데이터가 유효합니다."
    
    @staticmethod
    def clean_percentage_string(percentage_str: str) -> float:
        """퍼센트 문자열을 숫자로 변환"""
        try:
            # '%' 기호 제거 후 float로 변환
            cleaned = percentage_str.replace('%', '').strip()
            return float(cleaned)
        except (ValueError, AttributeError):
            return 0.0
    
    @staticmethod
    def validate_sheet_row(row_data: list, expected_columns: int) -> bool:
        """Google Sheets 행 데이터 유효성 검증"""
        if not row_data:
            return False
        
        if len(row_data) < expected_columns:
            return False
        
        # 필수 데이터가 있는지 확인 (정답률 컬럼)
        if len(row_data) > 4:
            try:
                DataValidator.clean_percentage_string(row_data[4])
                return True
            except:
                return False
        
        return False

# 편의를 위한 전역 인스턴스
input_validator = InputValidator()
game_validator = GameValidator()
data_validator = DataValidator()
