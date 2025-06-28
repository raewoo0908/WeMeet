#!/usr/bin/env python3
"""
Kibana Detection Rules Client
Kibana의 Detection Rules API와 연동하는 모듈
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime


class KibanaDetectionClient:
    """Kibana Detection Rules API와 연동하는 클라이언트"""
    
    def __init__(self, kibana_url: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        Kibana 클라이언트 초기화
        
        Args:
            kibana_url: Kibana 서버 URL (예: http://localhost:5601)
            username: 사용자명 (선택사항)
            password: 비밀번호 (선택사항)
        """
        self.kibana_url = kibana_url.rstrip('/')
        self.username = username
        self.password = password
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 세션 설정
        self.session = requests.Session()
        if username and password:
            self.session.auth = (username, password)
        
        # 기본 헤더 설정
        self.session.headers.update({
            'Content-Type': 'application/json',
            'kbn-xsrf': 'true'
        })
    
    def test_connection(self) -> bool:
        """Kibana 연결을 테스트합니다."""
        try:
            response = self.session.get(f"{self.kibana_url}/api/status")
            if response.status_code == 200:
                self.logger.info("Kibana 연결 성공")
                return True
            else:
                self.logger.error(f"Kibana 연결 실패: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Kibana 연결 테스트 중 오류 발생: {e}")
            return False
    
    def create_detection_rule(self, rule_data: Dict[str, Any]) -> Optional[str]:
        """
        Detection Rule을 생성합니다.
        
        Args:
            rule_data: Detection Rule 데이터
            
        Returns:
            생성된 규칙의 rule_id 또는 None
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            
            response = self.session.post(url, json=rule_data)
            
            if response.status_code == 200:
                result = response.json()
                # 생성된 규칙의 rule_id 반환
                rule_id = result.get('rule_id')
                self.logger.info(f"Detection Rule 생성 완료: {rule_id}")
                return rule_id
            else:
                self.logger.error(f"Detection Rule 생성 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Detection Rule 생성 중 오류 발생: {e}")
            return None
    
    def update_detection_rule(self, rule_id: str, rule_data: Dict[str, Any]) -> bool:
        """
        Detection Rule을 업데이트합니다.
        
        Args:
            rule_id: 규칙 ID
            rule_data: 업데이트할 규칙 데이터
            
        Returns:
            업데이트 성공 여부
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            
            # rule_id를 데이터에 추가
            rule_data['rule_id'] = rule_id
            
            response = self.session.put(url, json=rule_data)
            
            if response.status_code == 200:
                self.logger.info(f"Detection Rule 업데이트 완료: {rule_id}")
                return True
            else:
                self.logger.error(f"Detection Rule 업데이트 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Detection Rule 업데이트 중 오류 발생: {e}")
            return False
    
    def get_detection_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Detection Rule을 조회합니다.
        
        Args:
            rule_id: 규칙 ID
            
        Returns:
            규칙 데이터 또는 None
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            params = {'rule_id': rule_id}
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                return result  # 바로 규칙 객체 반환
            else:
                self.logger.error(f"Detection Rule 조회 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Detection Rule 조회 중 오류 발생: {e}")
            return None
    
    def list_detection_rules(self, page: int = 1, per_page: int = 100, 
                           sort_field: str = 'created_at', sort_order: str = 'desc',
                           filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        모든 Detection Rule을 조회합니다.
        
        Args:
            page: 페이지 번호 (기본값: 1)
            per_page: 페이지당 규칙 수 (기본값: 100)
            sort_field: 정렬 필드 (기본값: 'created_at')
            sort_order: 정렬 순서 ('asc' 또는 'desc', 기본값: 'desc')
            filter_query: 필터 쿼리 (선택사항, 예: 'alert.attributes.name:windows')
            
        Returns:
            규칙 목록
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules/_find"
            
            # 기본 파라미터 설정
            params = {
                'page': page,
                'per_page': per_page,
                'sort_field': sort_field,
                'sort_order': sort_order
            }
            
            # 필터 쿼리가 있으면 추가
            if filter_query:
                params['filter'] = filter_query
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"목록 조회 응답: {result}")
                rules = result.get('data', [])
                self.logger.info(f"조회된 규칙 수: {len(rules)}")
                return rules
            else:
                self.logger.error(f"Detection Rule 목록 조회 실패: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.logger.error(f"Detection Rule 목록 조회 중 오류 발생: {e}")
            return []
    
    def delete_detection_rule(self, rule_id: str) -> bool:
        """
        Detection Rule을 삭제합니다.
        
        Args:
            rule_id: 규칙 ID
            
        Returns:
            삭제 성공 여부
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            params = {'rule_id': rule_id}
            
            response = self.session.delete(url, params=params)
            
            if response.status_code == 200:
                self.logger.info(f"Detection Rule 삭제 완료: {rule_id}")
                return True
            else:
                self.logger.error(f"Detection Rule 삭제 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Detection Rule 삭제 중 오류 발생: {e}")
            return False
    
    def enable_detection_rule(self, rule_id: str) -> bool:
        """
        Detection Rule을 활성화합니다.
        
        Args:
            rule_id: 규칙 ID
            
        Returns:
            활성화 성공 여부
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            
            data = {
                "rule_id": rule_id,
                "enabled": True
            }
            
            response = self.session.patch(url, json=data)
            
            if response.status_code == 200:
                self.logger.info(f"Detection Rule 활성화 완료: {rule_id}")
                return True
            else:
                self.logger.error(f"Detection Rule 활성화 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Detection Rule 활성화 중 오류 발생: {e}")
            return False
    
    def disable_detection_rule(self, rule_id: str) -> bool:
        """
        Detection Rule을 비활성화합니다.
        
        Args:
            rule_id: 규칙 ID
            
        Returns:
            비활성화 성공 여부
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            
            data = {
                "rule_id": rule_id,
                "enabled": False
            }
            
            response = self.session.patch(url, json=data)
            
            if response.status_code == 200:
                self.logger.info(f"Detection Rule 비활성화 완료: {rule_id}")
                return True
            else:
                self.logger.error(f"Detection Rule 비활성화 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Detection Rule 비활성화 중 오류 발생: {e}")
            return False 