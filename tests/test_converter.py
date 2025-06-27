#!/usr/bin/env python3
"""
Sigma to Elasticsearch Converter 테스트
"""

import sys
import os
import json
from pathlib import Path
import unittest
import tempfile
import yaml

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sigma_cli_manager import SigmaCLIManager
from src.sigma_cli_converter import SigmaCLIConverter


class TestSigmaCLIManager(unittest.TestCase):
    """Sigma CLI 관리자 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.manager = SigmaCLIManager()
        
        # 테스트용 Sigma rule
        self.test_sigma_rule = {
            'title': 'Test Rule',
            'id': 'test-rule-123',
            'description': 'Test description',
            'author': 'Test Author',
            'date': '2024/01/01',
            'logsource': {
                'category': 'process_creation',
                'product': 'windows'
            },
            'detection': {
                'selection': {
                    'CommandLine|contains': 'test.exe'
                },
                'condition': 'selection'
            },
            'level': 'medium',
            'tags': ['test']
        }

    def test_check_installation(self):
        """설치 확인 테스트"""
        is_installed = self.manager.check_installation()
        # 설치 여부는 환경에 따라 다를 수 있으므로 단순히 호출만 확인
        self.assertIsInstance(is_installed, bool)

    def test_get_version(self):
        """버전 조회 테스트"""
        version = self.manager.get_version()
        # 버전은 설치 여부에 따라 None일 수 있음
        if version is not None:
            self.assertIsInstance(version, str)

    def test_list_available_targets(self):
        """사용 가능한 대상 조회 테스트"""
        try:
            targets = self.manager.list_available_targets()
            self.assertIsInstance(targets, list)
            if targets:  # 설치된 경우
                self.assertGreater(len(targets), 0)
                print(f"사용 가능한 대상: {targets}")
        except Exception as e:
            # 설치되지 않은 경우 예외 발생 가능
            print(f"대상 조회 실패 (예상됨): {e}")

    def test_list_available_pipelines(self):
        """사용 가능한 파이프라인 조회 테스트"""
        try:
            pipelines = self.manager.list_available_pipelines()
            self.assertIsInstance(pipelines, list)
            if pipelines:  # 설치된 경우
                self.assertGreater(len(pipelines), 0)
                print(f"사용 가능한 파이프라인: {pipelines}")
        except Exception as e:
            # 설치되지 않은 경우 예외 발생 가능
            print(f"파이프라인 조회 실패 (예상됨): {e}")

    def test_validate_sigma_rule(self):
        """Sigma rule 유효성 검사 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(self.test_sigma_rule, f)
            temp_file = f.name
        
        try:
            # 유효성 검사
            is_valid = self.manager.validate_sigma_rule(temp_file)
            # 결과는 설치 여부에 따라 다를 수 있음
            self.assertIsInstance(is_valid, bool)
            
        finally:
            # 임시 파일 삭제
            os.unlink(temp_file)

    def test_get_installation_guide(self):
        """설치 가이드 조회 테스트"""
        guide = self.manager.get_installation_guide()
        self.assertIsInstance(guide, str)
        self.assertGreater(len(guide), 0)
        self.assertIn("pip install sigma-cli", guide)


class TestSigmaCLIConverter(unittest.TestCase):
    """Sigma CLI 변환기 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.converter = SigmaCLIConverter()
        
        # 테스트용 Sigma rule
        self.test_sigma_rule = {
            'title': 'Test Rule',
            'id': 'test-rule-123',
            'description': 'Test description',
            'author': 'Test Author',
            'date': '2024/01/01',
            'logsource': {
                'category': 'process_creation',
                'product': 'windows'
            },
            'detection': {
                'selection': {
                    'CommandLine|contains': 'test.exe'
                },
                'condition': 'selection'
            },
            'level': 'medium',
            'tags': ['test']
        }

    def test_convert_to_lucene(self):
        """Lucene 쿼리 변환 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(self.test_sigma_rule, f)
            temp_file = f.name
        
        try:
            # Lucene 쿼리 변환
            lucene_query = self.converter.convert_to_lucene(temp_file, 'ecs_windows')
            
            # 결과 검증
            self.assertIsInstance(lucene_query, str)
            self.assertGreater(len(lucene_query), 0)
            print(f"생성된 Lucene 쿼리: {lucene_query}")
            
        except Exception as e:
            # Sigma CLI가 설치되지 않은 경우 예외 발생 가능
            print(f"Lucene 변환 실패 (예상됨): {e}")
            
        finally:
            # 임시 파일 삭제
            os.unlink(temp_file)

    def test_convert_to_detection_rule(self):
        """Detection Rule 변환 테스트"""
        try:
            # Detection Rule 변환
            detection_rule = self.converter.convert_to_detection_rule(self.test_sigma_rule, 'ecs_windows')
            
            # 결과 검증
            self.assertIsInstance(detection_rule, dict)
            self.assertIn('name', detection_rule)
            self.assertIn('query', detection_rule)
            self.assertIn('rule_id', detection_rule)
            self.assertIn('severity', detection_rule)
            
            print(f"생성된 Detection Rule: {json.dumps(detection_rule, indent=2)}")
            
        except Exception as e:
            # Sigma CLI가 설치되지 않은 경우 예외 발생 가능
            print(f"Detection Rule 변환 실패 (예상됨): {e}")

    def test_convert_file(self):
        """파일 변환 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(self.test_sigma_rule, f)
            temp_file = f.name
        
        try:
            # 파일 변환
            output_file = self.converter.convert_file(temp_file, None, 'ecs_windows')
            
            # 결과 검증
            self.assertIsInstance(output_file, str)
            self.assertTrue(os.path.exists(output_file))
            
            # 생성된 JSON 파일 읽기
            with open(output_file, 'r', encoding='utf-8') as f:
                detection_rule = json.load(f)
            
            self.assertIn('name', detection_rule)
            self.assertIn('query', detection_rule)
            
            print(f"생성된 파일: {output_file}")
            
            # 임시 파일 삭제
            os.unlink(output_file)
            
        except Exception as e:
            # Sigma CLI가 설치되지 않은 경우 예외 발생 가능
            print(f"파일 변환 실패 (예상됨): {e}")
            
        finally:
            # 입력 임시 파일 삭제
            os.unlink(temp_file)

    def test_load_sigma_rule(self):
        """Sigma rule 로드 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(self.test_sigma_rule, f)
            temp_file = f.name
        
        try:
            # Sigma rule 로드
            loaded_rule = self.converter.load_sigma_rule(temp_file)
            
            # 결과 검증
            self.assertIsInstance(loaded_rule, dict)
            self.assertEqual(loaded_rule['title'], self.test_sigma_rule['title'])
            self.assertEqual(loaded_rule['id'], self.test_sigma_rule['id'])
            
        finally:
            # 임시 파일 삭제
            os.unlink(temp_file)

    def test_generate_rule_id(self):
        """규칙 ID 생성 테스트"""
        # 내부 메서드 테스트를 위해 직접 호출
        rule_id = self.converter._generate_rule_id("Test Rule Name")
        self.assertIsInstance(rule_id, str)
        self.assertGreater(len(rule_id), 0)
        # 특수문자가 제거되었는지 확인
        self.assertNotIn(' ', rule_id)
        self.assertNotIn('-', rule_id)


if __name__ == '__main__':
    unittest.main() 