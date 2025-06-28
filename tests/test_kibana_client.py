#!/usr/bin/env python3
"""
Kibana Detection Client 테스트
실제 Kibana 서버에 연결하여 모든 기능을 테스트합니다.
"""

import sys
import os
import json
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch
from dotenv import load_dotenv, find_dotenv

# .env 파일 자동 로드
def load_env():
    env_path = find_dotenv()
    if env_path:
        load_dotenv(env_path)
        print(f"[INFO] .env 파일을 로드했습니다: {env_path}")
    else:
        print("[WARN] .env 파일이 존재하지 않습니다. 환경변수 또는 기본값을 사용합니다.")

load_env()

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.kibana_client import KibanaDetectionClient


class TestKibanaClient(unittest.TestCase):
    """Kibana 클라이언트 테스트"""

    def setUp(self):
        """테스트 설정"""
        # 환경변수에서 Kibana 설정 가져오기
        self.kibana_url = os.getenv('KIBANA_URL', 'http://localhost:5601')
        self.username = os.getenv('KIBANA_USERNAME', 'elastic')
        self.password = os.getenv('KIBANA_PASSWORD', 'changeme')
        
        # 클라이언트 생성
        self.client = KibanaDetectionClient(self.kibana_url, self.username, self.password)
        
        # 테스트용 Detection Rule 데이터 (rule_id는 각 테스트에서 고유하게 생성)
        self.test_rule_data_og = {
            "from": "now-70m",
            "name": "MS Office child process",
            "tags": [
                "child process",
                "ms office"
            ],
            "type": "query",
            "query": "process.parent.name:EXCEL.EXE or process.parent.name:MSPUB.EXE or process.parent.name:OUTLOOK.EXE or process.parent.name:POWERPNT.EXE or process.parent.name:VISIO.EXE or process.parent.name:WINWORD.EXE",
            "enabled": False,
            "filters": [
                {
                "query": {
                    "match": {
                    "event.action": {
                        "type": "phrase",
                        "query": "Process Create (rule: ProcessCreate)"
                    }
                    }
                }
                }
            ],
            "rule_id": None,  # 각 테스트에서 고유하게 설정
            "interval": "1h",
            "language": "kuery",
            "severity": "low",
            "risk_score": 50,
            "description": "Process started by MS Office program - possible payload",
            "required_fields": [
                {
                "name": "process.parent.name",
                "type": "keyword"
                }
            ],
            "related_integrations": [
                {
                "package": "o365",
                "version": "^2.3.2"
                }
            ]
        }
        
        # 현재 테스트에서 생성된 규칙 ID
        self.current_rule_id = None

    def tearDown(self):
        """테스트 정리 - 생성된 규칙 삭제"""
        if hasattr(self, 'current_rule_id') and self.current_rule_id:
            try:
                print(f"🧹 테스트 정리: 규칙 {self.current_rule_id} 삭제 중...")
                self.client.delete_detection_rule(self.current_rule_id)
                print(f"✅ 규칙 {self.current_rule_id} 삭제 완료")
            except Exception as e:
                print(f"⚠️ 규칙 삭제 중 오류 발생: {e}")
            finally:
                self.current_rule_id = None

    def test_01_connection(self):
        """Kibana 연결 테스트"""
        print("\n=== Kibana 연결 테스트 ===")
        
        is_connected = self.client.test_connection()
        self.assertTrue(is_connected, "Kibana 서버에 연결할 수 없습니다.")
        print("✅ Kibana 연결 성공")

    def test_02_create_rule(self):
        """Detection Rule 생성 테스트"""
        print("\n=== Detection Rule 생성 테스트 ===")
        
        # 고유한 rule_id 생성
        test_data = self.test_rule_data_og.copy()
        test_data['rule_id'] = f"test_rule_{uuid.uuid4().hex}"
        
        # 규칙 생성
        self.current_rule_id = self.client.create_detection_rule(test_data)
        
        self.assertIsNotNone(self.current_rule_id, "규칙 생성에 실패했습니다.")
        self.assertIsInstance(self.current_rule_id, str, "생성된 규칙 ID가 문자열이 아닙니다.")
        
        print(f"✅ 규칙 생성 완료: {self.current_rule_id}")

    def test_03_get_rule(self):
        """Detection Rule 조회 테스트"""
        print("\n=== Detection Rule 조회 테스트 ===")
        
        # 고유한 rule_id로 규칙 생성
        test_data = self.test_rule_data_og.copy()
        test_data['rule_id'] = f"test_rule_{uuid.uuid4().hex}"
        self.current_rule_id = self.client.create_detection_rule(test_data)
        self.assertIsNotNone(self.current_rule_id, "규칙 생성에 실패했습니다.")
        
        # 생성된 규칙 조회
        rule_data = self.client.get_detection_rule(self.current_rule_id)
        
        self.assertIsNotNone(rule_data, "규칙 조회에 실패했습니다.")
        self.assertIsInstance(rule_data, dict, "조회된 규칙이 딕셔너리가 아닙니다.")
        
        # 필수 필드 확인
        self.assertIn('name', rule_data, "규칙에 name 필드가 없습니다.")
        self.assertIn('query', rule_data, "규칙에 query 필드가 없습니다.")
        self.assertEqual(self.current_rule_id, rule_data.get('rule_id'), "규칙 ID가 일치하지 않습니다.")
        
        print(f"✅ 규칙 조회 완료: {rule_data.get('name')}")

    def test_04_update_rule(self):
        """Detection Rule 업데이트 테스트"""
        print("\n=== Detection Rule 업데이트 테스트 ===")
        
        # 고유한 rule_id로 규칙 생성
        test_data = self.test_rule_data_og.copy()
        test_data['rule_id'] = f"test_rule_{uuid.uuid4().hex}"
        self.current_rule_id = self.client.create_detection_rule(test_data)
        self.assertIsNotNone(self.current_rule_id, "규칙 생성에 실패했습니다.")
        
        # 업데이트할 데이터
        update_data = test_data.copy()
        update_data['description'] = 'Updated test rule description'
        update_data['risk_score'] = 73
        
        # 규칙 업데이트
        success = self.client.update_detection_rule(self.current_rule_id, update_data)
        
        self.assertTrue(success, "규칙 업데이트에 실패했습니다.")
        
        # 업데이트된 규칙 조회하여 확인
        updated_rule = self.client.get_detection_rule(self.current_rule_id)
        self.assertEqual(update_data['description'], updated_rule['description'], "규칙 설명이 일치하지 않습니다.")
        self.assertEqual(update_data['risk_score'], updated_rule['risk_score'], "규칙 위험 점수가 일치하지 않습니다.")
        
        print(f"✅ 규칙 업데이트 완료: {self.current_rule_id}")

    def test_05_enable_disable_rule(self):
        """Detection Rule 활성화/비활성화 테스트"""
        print("\n=== Detection Rule 활성화/비활성화 테스트 ===")
        
        # 고유한 rule_id로 규칙 생성
        test_data = self.test_rule_data_og.copy()
        test_data['rule_id'] = f"test_rule_{uuid.uuid4().hex}"
        self.current_rule_id = self.client.create_detection_rule(test_data)
        self.assertIsNotNone(self.current_rule_id, "규칙 생성에 실패했습니다.")
        
        # 규칙 비활성화
        success = self.client.disable_detection_rule(self.current_rule_id)
        self.assertTrue(success, "규칙 비활성화에 실패했습니다.")

        updated_rule = self.client.get_detection_rule(self.current_rule_id)
        self.assertEqual(updated_rule['enabled'], False, "규칙 상태가 비활성화되지 않았습니다.")

        print(f"✅ 규칙 비활성화 완료: {self.current_rule_id}")
        
        # 규칙 활성화
        success = self.client.enable_detection_rule(self.current_rule_id)
        self.assertTrue(success, "규칙 활성화에 실패했습니다.")

        updated_rule = self.client.get_detection_rule(self.current_rule_id)
        self.assertEqual(updated_rule['enabled'], True, "규칙 상태가 활성화되지 않았습니다.")

        print(f"✅ 규칙 활성화 완료: {self.current_rule_id}")

    def test_06_list_rules(self):
        """Detection Rule 목록 조회 테스트"""
        print("\n=== Detection Rule 목록 조회 테스트 ===")
        
        # 고유한 rule_id로 규칙 생성
        test_data = self.test_rule_data_og.copy()
        test_data['rule_id'] = f"test_rule_{uuid.uuid4().hex}"
        self.current_rule_id = self.client.create_detection_rule(test_data)
        self.assertIsNotNone(self.current_rule_id, "규칙 생성에 실패했습니다.")
        
        print(f"🔍 생성된 규칙 ID: {self.current_rule_id}")
        
        # 기본 파라미터로 모든 규칙 목록 조회
        rules = self.client.list_detection_rules()
        self.assertIsInstance(rules, list, "규칙 목록이 리스트가 아닙니다.")
        
        # 디버깅: 목록에서 찾은 rule_id들 출력
        found_rule_ids = [rule.get('rule_id') for rule in rules if rule.get('rule_id')]
        print(f"📋 목록에서 찾은 rule_id들: {found_rule_ids}")
        
        # 생성한 테스트 규칙이 목록에 있는지 확인
        test_rule_found = any(rule.get('rule_id') == self.current_rule_id for rule in rules)
        self.assertTrue(test_rule_found, "생성한 테스트 규칙이 목록에 없습니다.")
        
        # 다양한 파라미터 조합 테스트
        print("\n--- 다양한 파라미터 조합 테스트 ---")
        
        # 페이지네이션 테스트
        rules_page1 = self.client.list_detection_rules(page=1, per_page=5)
        self.assertIsInstance(rules_page1, list, "페이지네이션 테스트 실패")
        print(f"📄 페이지 1 (5개씩): {len(rules_page1)}개 규칙")
        
        # 정렬 테스트
        rules_sorted = self.client.list_detection_rules(sort_field='name', sort_order='asc')
        self.assertIsInstance(rules_sorted, list, "정렬 테스트 실패")
        print(f"📊 이름순 정렬: {len(rules_sorted)}개 규칙")
        
        # 필터 테스트 (테스트 규칙 이름으로 필터링)
        filter_query = f"alert.attributes.name:\"{test_data['name']}\""
        rules_filtered = self.client.list_detection_rules(filter_query=filter_query)
        self.assertIsInstance(rules_filtered, list, "필터 테스트 실패")
        print(f"🔍 필터링 결과: {len(rules_filtered)}개 규칙")
        
        print(f"✅ 규칙 목록 조회 완료: {len(rules)}개 규칙 발견")

    def test_07_delete_rule(self):
        """Detection Rule 삭제 테스트"""
        print("\n=== Detection Rule 삭제 테스트 ===")
        
        # 고유한 rule_id로 규칙 생성
        test_data = self.test_rule_data_og.copy()
        test_data['rule_id'] = f"test_rule_{uuid.uuid4().hex}"
        self.current_rule_id = self.client.create_detection_rule(test_data)
        self.assertIsNotNone(self.current_rule_id, "규칙 생성에 실패했습니다.")
        
        # 규칙 삭제
        success = self.client.delete_detection_rule(self.current_rule_id)
        self.assertTrue(success, "규칙 삭제에 실패했습니다.")
        
        # 삭제된 규칙이 목록에서 제거되었는지 확인
        rules = self.client.list_detection_rules()
        deleted_rule_found = any(rule.get('rule_id') == self.current_rule_id for rule in rules)
        self.assertFalse(deleted_rule_found, "삭제된 규칙이 여전히 목록에 있습니다.")
        
        # 삭제 완료 후 current_rule_id를 None으로 설정 (tearDown에서 중복 삭제 방지)
        self.current_rule_id = None
        
        print(f"✅ 규칙 삭제 완료")

    def test_08_invalid_rule_id(self):
        """잘못된 규칙 ID로 조회 테스트"""
        print("\n=== 잘못된 규칙 ID 조회 테스트 ===")
        
        # 존재하지 않는 규칙 ID로 조회
        invalid_rule_id = "non-existent-rule-12345"
        rule_data = self.client.get_detection_rule(invalid_rule_id)
        
        # 존재하지 않는 규칙은 None을 반환해야 함
        self.assertIsNone(rule_data, "존재하지 않는 규칙이 조회되었습니다.")
        
        print("✅ 잘못된 규칙 ID 처리 완료")

    def test_09_connection_failure(self):
        """연결 실패 테스트"""
        print("\n=== 연결 실패 테스트 ===")
        
        # 잘못된 URL로 클라이언트 생성
        invalid_client = KibanaDetectionClient("http://invalid-url:9999")
        
        # 연결 테스트
        is_connected = invalid_client.test_connection()
        self.assertFalse(is_connected, "잘못된 URL에 연결되었습니다.")
        
        print("✅ 연결 실패 처리 완료")


def run_kibana_tests():
    """Kibana 테스트 실행"""
    print("🚀 Kibana 클라이언트 테스트 시작")
    print("=" * 50)
    
    # 환경 설정 확인
    kibana_url = os.getenv('KIBANA_URL', 'http://localhost:5601')
    username = os.getenv('KIBANA_USERNAME', 'elastic')
    password = os.getenv('KIBANA_PASSWORD', 'changeme')
    
    print(f"📋 테스트 환경:")
    print(f"   - Kibana URL: {kibana_url}")
    print(f"   - Username: {username}")
    print(f"   - Password: {'*' * len(password) if password else 'None'}")
    print()
    
    # 테스트 실행
    suite = unittest.TestLoader().loadTestsFromTestCase(TestKibanaClient)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    if result.wasSuccessful():
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        print(f"   - 실패: {len(result.failures)}")
        print(f"   - 오류: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_kibana_tests()
    sys.exit(0 if success else 1) 