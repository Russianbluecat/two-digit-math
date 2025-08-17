# sheets_manager.py - Google Sheets 관리 모듈

import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
import logging

from config import SheetsConfig, ErrorMessages
from validation import data_validator

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SheetsManager:
    """Google Sheets 연결 및 데이터 관리 클래스"""
    
    def __init__(self):
        self.client = None
        self.spreadsheet = None
        self.sheet = None
        self.is_enabled = False
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Google Sheets 연결 초기화"""
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                st.secrets["gcp_service_account"], 
                SheetsConfig.SCOPES
            )
            self.client = gspread.authorize(creds)
            
            sheet_id = st.secrets.get("GOOGLE_SHEET_ID", SheetsConfig.DEFAULT_SHEET_ID)
            self.spreadsheet = self.client.open_by_key(sheet_id)
            self.sheet = self.spreadsheet.worksheet("Sheet1")
            
            self.is_enabled = True
            logger.info("Google Sheets 연결 성공")
            
        except Exception as e:
            self.is_enabled = False
            logger.error(f"Google Sheets 연결 실패: {str(e)}")
            self._show_connection_warning(str(e))
    
    def _show_connection_warning(self, error_message: str):
        """연결 실패 경고 표시"""
        st.warning(f"⚠️ {ErrorMessages.SHEETS_CONNECTION_ERROR}")
        with st.expander("오류 세부사항"):
            st.error(f"설정 오류: {error_message}")
    
    def save_game_result(self, total_questions: int, correct_count: int, 
                        accuracy: float, operation_type: str, 
                        time_limit: int, elapsed_time: float) -> bool:
        """
        게임 결과를 Google Sheets에 저장
        
        Args:
            total_questions: 총 문제 수
            correct_count: 정답 수
            accuracy: 정확도 (%)
            operation_type: 연산 타입
            time_limit: 제한 시간
            elapsed_time: 소요 시간
            
        Returns:
            bool: 저장 성공 여부
        """
        if not self.is_enabled:
            st.warning("⚠️ Google Sheets가 설정되지 않아 결과를 저장할 수 없습니다.")
            return False
        
        # 데이터 검증
        is_valid, error_msg = data_validator.validate_accuracy_data(correct_count, total_questions)
        if not is_valid:
            st.error(f"데이터 검증 실패: {error_msg}")
            return False
        
        try:
            # 한국 시간 설정
            kst = timezone(timedelta(hours=9))
            now = datetime.now(kst)
            
            row_data = [
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                str(total_questions),
                str(correct_count),
                f"{accuracy:.1f}%",
                operation_type,
                f"{time_limit}초",
                f"{elapsed_time:.1f}초"
            ]
            
            self.sheet.append_row(row_data)
            st.success("✔️ 결과가 성공적으로 저장되었습니다!")
            logger.info(f"게임 결과 저장 완료: 정확도 {accuracy:.1f}%")
            return True
            
        except Exception as e:
            error_message = f"❌ {ErrorMessages.SHEETS_SAVE_ERROR}: {str(e)}"
            st.error(error_message)
            logger.error(f"데이터 저장 실패: {str(e)}")
            return False
    
    def get_global_statistics(self) -> Optional[Dict[str, Any]]:
        """
        전체 사용자 통계 조회
        
        Returns:
            Optional[Dict]: 통계 데이터 또는 None
        """
        if not self.is_enabled:
            return None
        
        try:
            rows = self.sheet.get_all_values()
            
            if len(rows) < 2:  # 헤더만 있는 경우
                st.info("아직 충분한 통계 데이터가 없습니다.")
                return None
            
            # 헤더 제외
            data_rows = rows[1:]
            
            return self._process_statistics_data(data_rows)
            
        except gspread.exceptions.APIError as e:
            st.warning(f"Google Sheets API 오류: {str(e)}")
            logger.error(f"API 오류: {str(e)}")
            return None
        except Exception as e:
            st.warning(f"{ErrorMessages.SHEETS_LOAD_ERROR}: {str(e)}")
            logger.error(f"통계 로드 실패: {str(e)}")
            return None
    
    def _process_statistics_data(self, data_rows: List[List[str]]) -> Dict[str, Any]:
        """
        통계 데이터 처리
        
        Args:
            data_rows: Google Sheets에서 가져온 데이터 행들
            
        Returns:
            Dict: 처리된 통계 데이터
        """
        total_games = len(data_rows)
        accuracy_list = []
        
        # 정확도 데이터 추출 및 검증
        for row in data_rows:
            if not data_validator.validate_sheet_row(row, len(SheetsConfig.COLUMNS)):
                continue
            
            try:
                accuracy = data_validator.clean_percentage_string(row[4])
                if 0 <= accuracy <= 100:  # 유효한 범위의 정확도만 추가
                    accuracy_list.append(accuracy)
            except (IndexError, ValueError):
                continue
        
        if not accuracy_list:
            return None
        
        # 성과별 분류
        stats = self._categorize_performance(accuracy_list, total_games)
        stats.update({
            'total_games': total_games,
            'accuracy_list': accuracy_list,
            'average_accuracy': sum(accuracy_list) / len(accuracy_list)
        })
        
        return stats
    
    def _categorize_performance(self, accuracy_list: List[float], total_games: int) -> Dict[str, Any]:
        """성과별로 데이터 분류"""
        from config import GameConfig
        
        perfect_count = len([acc for acc in accuracy_list if acc == GameConfig.SCORE_PERFECT])
        great_count = len([acc for acc in accuracy_list if GameConfig.SCORE_GREAT <= acc < GameConfig.SCORE_PERFECT])
        good_count = len([acc for acc in accuracy_list if GameConfig.SCORE_GOOD <= acc < GameConfig.SCORE_GREAT])
        okay_count = len([acc for acc in accuracy_list if GameConfig.SCORE_OKAY <= acc < GameConfig.SCORE_GOOD])
        poor_count = len([acc for acc in accuracy_list if acc < GameConfig.SCORE_OKAY])
        
        return {
            'perfect_count': perfect_count,
            'perfect_rate': (perfect_count / total_games) * 100,
            'great_count': great_count,
            'great_rate': (great_count / total_games) * 100,
            'good_count': good_count,
            'good_rate': (good_count / total_games) * 100,
            'okay_count': okay_count,
            'okay_rate': (okay_count / total_games) * 100,
            'poor_count': poor_count,
            'poor_rate': (poor_count / total_games) * 100
        }
    
    def get_user_rank(self, user_accuracy: float, accuracy_list: List[float]) -> str:
        """
        사용자 순위 계산
        
        Args:
            user_accuracy: 사용자 정확도
            accuracy_list: 전체 사용자 정확도 목록
            
        Returns:
            str: 순위 문자열
        """
        if not accuracy_list:
            return "순위 계산 불가"
        
        better_scores = len([acc for acc in accuracy_list if acc > user_accuracy])
        same_scores = len([acc for acc in accuracy_list if acc == user_accuracy])
        
        # 동점자가 있을 경우 평균 순위 계산
        rank = better_scores + (same_scores + 1) / 2
        percentile = (rank / len(accuracy_list)) * 100
        
        return f"상위 {percentile:.1f}%"

# 전역 인스턴스
sheets_manager = SheetsManager()
