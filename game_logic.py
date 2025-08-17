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
    """문제 생성 클래스"""
    
    @staticmethod
    def generate_question(operation_type: str) -> Question:
        """
        연산 타입에 따른 문제 생성
        
        Args:
            operation_type: 연산 타입 ("덧셈", "뺄셈", "랜덤 (덧셈+뺄셈)")
            
        Returns:
            Question: 생성된 문제 객체
        """
        num1 = random.randint(GameConfig.MIN_NUMBER, GameConfig.MAX_NUMBER)
        num2 = random.randint(GameConfig.MIN_NUMBER, GameConfig.MAX_NUMBER)
        
        if operation_type == "덧셈":
            operator = "+"
            answer = num1 + num2
        elif operation_type == "뺄셈":
            # 결과가 음수가 되지 않도록 보장
            if num1 < num2:
                num1, num2 = num2, num1
            operator = "-"
            answer = num1 - num2
        else:  # 랜덤
            if random.choice([True, False]):
                operator = "+"
                answer = num1 + num2
            else:
                if num1 < num2:
                    num1, num2 = num2, num1
                operator = "-"
                answer = num1 - num2
        
        return Question(num1, num2, operator, answer)
    
    @staticmethod
    def generate_question_set(operation_type: str, count: int) -> List[Question]:
        """
        문제 세트 생성
        
        Args:
            operation_type: 연산 타입
            count: 생성할 문제 수
            
        Returns:
            List[Question]: 생성된 문제들의 리스트
        """
        return [QuestionGenerator.generate_question(operation_type) for _ in range(count)]

class GameSession:
    """게임 세션을 관리하는 클래스"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """게임 세션 초기화"""
        self.questions: List[Question] = []
        self.current_question_index = 0
        self.correct_count = 0
        self.start_time = None
        self.question_start_time = None
        self.operation_type = ""
        self.time_limit = GameConfig.DEFAULT_TIME_LIMIT
        self.is_active = False
    
    def start_game(self, operation_type: str, question_count: int, time_limit: int):
        """
        게임 시작
        
        Args:
            operation_type: 연산 타입
            question_count: 문제 수
            time_limit: 제한 시간
        """
        # 설정 검증
        is_valid, error_msg = game_validator.validate_game_settings(
            question_count, time_limit, operation_type
        )
        if not is_valid:
            raise ValueError(error_msg)
        
        self.reset()
        self.questions = QuestionGenerator.generate_question_set(operation_type, question_count)
        self.operation_type = operation_type
        self.time_limit = time_limit
        self.start_time = time.time()
        self.question_start_time = time.time()
        self.is_active = True
    
    def get_current_question(self) -> Question:
        """현재 문제 반환"""
        if not self.is_active or self.current_question_index >= len(self.questions):
            return None
        return self.questions[self.current_question_index]
    
    def check_time_limit(self) -> Tuple[bool, float]:
        """제한 시간 확인"""
        if not self.question_start_time:
            return True, 0
        
        current_time = time.time()
        is_valid, elapsed = game_validator.validate_answer_timing(
            self.question_start_time, current_time, self.time_limit
        )
        return is_valid, elapsed
    
    def submit_answer(self, user_input: str) -> Tuple[bool, str, bool]:
        """
        답안 제출 및 검증
        
        Args:
            user_input: 사용자 입력
            
        Returns:
            Tuple[bool, str, bool]: (정답여부, 메시지, 시간초과여부)
        """
        # 시간 초과 확인
        is_time_valid, elapsed_time = self.check_time_limit()
        if not is_time_valid:
            return False, ErrorMessages.TIME_UP, True
        
        # 현재 문제 가져오기
        current_question = self.get_current_question()
        if not current_question:
            return False, "유효하지 않은 문제입니다.", False
        
        # 답안 검증
        is_correct, message = current_question.check_answer(user_input)
        current_question.response_time = elapsed_time
        
        if is_correct:
            self.correct_count += 1
        
        return is_correct, message, False
    
    def next_question(self):
        """다음 문제로 이동"""
        self.current_question_index += 1
        self.question_start_time = time.time()
        
        if self.current_question_index >= len(self.questions):
            self.is_active = False
    
    def is_game_finished(self) -> bool:
        """게임 종료 여부 확인"""
        return not self.is_active or self.current_question_index >= len(self.questions)
    
    def get_game_progress(self) -> Tuple[int, int]:
        """게임 진행률 반환 (현재문제, 전체문제)"""
        return self.current_question_index + 1, len(self.questions)
    
    def get_current_accuracy(self) -> float:
        """현재까지의 정확도 계산"""
        if self.current_question_index == 0:
            return 0.0
        return (self.correct_count / self.current_question_index) * 100
    
    def get_final_results(self) -> dict:
        """최종 결과 반환"""
        total_time = time.time() - self.start_time if self.start_time else 0
        accuracy = (self.correct_count / len(self.questions)) * 100
        
        return {
            'total_questions': len(self.questions),
            'correct_count': self.correct_count,
            'accuracy': accuracy,
            'total_time': total_time,
            'operation_type': self.operation_type,
            'time_limit': self.time_limit
        }

class PerformanceEvaluator:
    """성과 평가 클래스"""
    
    @staticmethod
    def get_performance_message(accuracy: float) -> Tuple[str, str, str]:
        """
        정확도에 따른 성과 메시지 반환
        
        Args:
            accuracy: 정확도 (%)
            
        Returns:
            Tuple[str, str, str]: (아이콘, 메시지, 스타일)
        """
        if accuracy == GameConfig.SCORE_PERFECT:
            return UIConfig.MESSAGES['perfect']
        elif accuracy >= GameConfig.SCORE_GREAT:
            return UIConfig.MESSAGES['great']
        elif accuracy >= GameConfig.SCORE_GOOD:
            return UIConfig.MESSAGES['good']
        elif accuracy >= GameConfig.SCORE_OKAY:
            return UIConfig.MESSAGES['okay']
        else:
            return UIConfig.MESSAGES['poor']
    
    @staticmethod
    def get_rank_message(percentile: float) -> str:
        """순위에 따른 메시지 반환"""
        if percentile <= 10:
            return "👑 상위 10% 안에 드셨네요! 정말 대단합니다!"
        elif percentile <= 25:
            return "🔥 상위 25% 안에 드셨어요! 실력자시군요!"
        elif percentile <= 50:
            return "💪 평균보다 훨씬 잘하셨어요!"
        else:
            return "📚 더 연습하면 더욱 좋아질 거예요!"

# 전역 게임 세션 인스턴스
game_session = GameSession()
performance_evaluator = PerformanceEvaluator()
