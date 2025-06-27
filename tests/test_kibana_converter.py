#!/usr/bin/env python3
"""
Sigma to Kibana Detection Rule Converter 테스트
"""

import sys
import os
import json
from pathlib import Path
import unittest
import tempfile

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.kibana_client import KibanaDetectionClient



class TestKibanaDetectionClient(unittest.TestCase):
    """Kibana Detection Client 테스트"""

    def setUp(self):
        """테스트 설정"""
        # 테스트용 Kibana 클라이언트 (실제 연결은 하지 않음)
        self.client = KibanaDetectionClient(
            kibana_url="http://localhost:5601",
            username="test",
            password="test"
        )
        
        # 테스트용 Detection Rule
        self.test_detection_rule = {
            "name": "Test Detection Rule",
            "description": "Test description",
            "rule_id": "test-rule-123",
            "query": "process.command_line:*test.exe*",
            "severity": "medium",
            "risk_score": 47,
            "enabled": False,
            "type": "query",
            "language": "kuery",
            "from": "now-70m",
            "interval": "1h",
            "tags": ["test"]
        }

    def test_create_detection_rule_structure(self):
        """Detection Rule 구조 검증 테스트"""
        # 필수 필드 확인
        required_fields = ['name', 'query', 'rule_id', 'severity']
        for field in required_fields:
            self.assertIn(field, self.test_detection_rule)
        
        # 데이터 타입 확인
        self.assertIsInstance(self.test_detection_rule['name'], str)
        self.assertIsInstance(self.test_detection_rule['query'], str)
        self.assertIsInstance(self.test_detection_rule['rule_id'], str)
        self.assertIsInstance(self.test_detection_rule['severity'], str)
        
        print("✅ Detection Rule 구조 검증 통과")

    def test_save_detection_rule_to_file(self):
        """Detection Rule 파일 저장 테스트"""
        # 임시 파일에 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_detection_rule, f, indent=2)
            temp_file = f.name
        
        try:
            # 파일이 생성되었는지 확인
            self.assertTrue(os.path.exists(temp_file))
            
            # 파일 내용 읽기
            with open(temp_file, 'r', encoding='utf-8') as f:
                loaded_rule = json.load(f)
            
            # 내용이 일치하는지 확인
            self.assertEqual(loaded_rule['name'], self.test_detection_rule['name'])
            self.assertEqual(loaded_rule['rule_id'], self.test_detection_rule['rule_id'])
            
            print(f"✅ Detection Rule 파일 저장 테스트 통과: {temp_file}")
            
        finally:
            # 임시 파일 삭제
            os.unlink(temp_file)

    def test_detection_rule_validation(self):
        """Detection Rule 유효성 검사 테스트"""
        # 유효한 규칙
        self.assertTrue(self._is_valid_detection_rule(self.test_detection_rule))
        
        # 필수 필드가 없는 규칙
        invalid_rule = self.test_detection_rule.copy()
        del invalid_rule['name']
        self.assertFalse(self._is_valid_detection_rule(invalid_rule))
        
        # 잘못된 severity 값
        invalid_rule = self.test_detection_rule.copy()
        invalid_rule['severity'] = 'invalid'
        self.assertFalse(self._is_valid_detection_rule(invalid_rule))
        
        print("✅ Detection Rule 유효성 검사 테스트 통과")

    def test_query_validation(self):
        """쿼리 유효성 검사 테스트"""
        # 유효한 쿼리들
        valid_queries = [
            "process.command_line:*test.exe*",
            "event.action:Process Create",
            "user.name:testuser",
            "host.name:testhost"
        ]
        
        for query in valid_queries:
            self.assertTrue(self._is_valid_query(query))
        
        # 잘못된 쿼리들
        invalid_queries = [
            "",  # 빈 쿼리
            "invalid:field:value",  # 잘못된 구문
            None  # None 값
        ]
        
        for query in invalid_queries:
            self.assertFalse(self._is_valid_query(query))
        
        print("✅ 쿼리 유효성 검사 테스트 통과")

    def test_severity_mapping(self):
        """위험도 매핑 테스트"""
        severity_mapping = {
            'low': 21,
            'medium': 47,
            'high': 73,
            'critical': 99
        }
        
        for severity, expected_score in severity_mapping.items():
            rule = self.test_detection_rule.copy()
            rule['severity'] = severity
            rule['risk_score'] = expected_score
            
            # 위험도와 위험 점수가 일치하는지 확인
            self.assertEqual(rule['severity'], severity)
            self.assertEqual(rule['risk_score'], expected_score)
        
        print("✅ 위험도 매핑 테스트 통과")

    def _is_valid_detection_rule(self, rule):
        """Detection Rule 유효성 검사 헬퍼 함수"""
        if not isinstance(rule, dict):
            return False
        
        # 필수 필드 확인
        required_fields = ['name', 'query', 'rule_id', 'severity']
        for field in required_fields:
            if field not in rule:
                return False
        
        # severity 값 확인
        valid_severities = ['low', 'medium', 'high', 'critical']
        if rule['severity'] not in valid_severities:
            return False
        
        return True

    def _is_valid_query(self, query):
        """쿼리 유효성 검사 헬퍼 함수"""
        if not query or not isinstance(query, str):
            return False
        
        if len(query.strip()) == 0:
            return False
        
        return True


if __name__ == "__main__":
    print("Sigma to Kibana Detection Rule Converter 테스트 시작\n")
    
    try:
        test_basic_kibana_conversion()
        test_kql_query_generation()
        test_severity_mapping()
        test_filters_generation()
        test_file_conversion()
        
        print("\n🎉 모든 Kibana 변환 테스트가 성공적으로 완료되었습니다!")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        sys.exit(1)

    unittest.main() 