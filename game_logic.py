# game_logic.py - 게임 로직 관리 모듈

import random
import time
from typing import Tuple, List
from config import GameConfig, UIConfig, ErrorMessages
from validation import input_validator, game_validator

class Question:
    """개별 문제를 나타내는 클래스"""
    
    def __init__(self, num1: int, num2: int, operator: str, answer: int):
        self.num1 = num1
        self.num2 = num2
        self.operator = operator
        self.answer = answer
        self.user_answer = None
        self.is_correct = None
        self.response_time = None
    
    def __str__(self):
        return f"{self.num1} {self.operator} {self.num2} = ?"
    
    def check_answer(self, user_input: str) -> Tuple[bool, str]:
        """사용자 답안 검증"""
        is_valid, result = input_validator.validate_number_input(user_input)
        
        if not is_valid:
            return False, result
        
        self.user_answer = result
        self.is_correct = (result == self.answer)
        
        if self.is_correct:
            return True, "정답!"
        else:
            return False, f"틀림! 정답은 {self.answer}입니다."

class QuestionGenerator:
    """문제 생성 클래
