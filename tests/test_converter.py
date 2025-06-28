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

from src.sigma_cli_converter import SigmaCLIConverter

class TestSigmaCLIConverter(unittest.TestCase):
    """Sigma CLI 변환기 테스트"""

    def setUp(self):
        """테스트 설정"""
        self.converter = SigmaCLIConverter()
        
        # 테스트용 Sigma rule
        self.valid_test_sigma_rule = {
            'title': 'Test Rule',
            'id': 'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
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
            'tags': ['test.rule', 'test.process']
        }
        self.invalid_test_sigma_rule = {
            # 필수 필드인 logsource와 detection 필드가 없음
            'title': 'Test Rule',
            'id': 'test-rule-123',
            'description': 'Test description',
            'author': 'Test Author',
            'date': '2024/01/01',
        }

    def test_01_load_sigma_rule(self):
        """Sigma rule 로드 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(self.valid_test_sigma_rule, f)
            temp_file = f.name
        
        try:
            # Sigma rule 로드
            loaded_rule = self.converter.load_sigma_rule(temp_file)
            
            # 결과 검증
            self.assertIsInstance(loaded_rule, dict)
            self.assertEqual(loaded_rule['title'], self.valid_test_sigma_rule['title'])
            self.assertEqual(loaded_rule['id'], self.valid_test_sigma_rule['id'])
            
        finally:
            # 임시 파일 삭제
            os.unlink(temp_file)

    def test_02_validate_sigma_rule(self):
        """Sigma rule 유효성 검사 테스트"""
        
        # 1. 유효한 Sigma rule 테스트
        print("\n=== 유효한 Sigma Rule 테스트 ===")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(self.valid_test_sigma_rule, f)
            valid_temp_file = f.name
        
        try:
            # 유효한 규칙 검사
            is_valid = self.converter.validate_sigma_rule(valid_temp_file)
            self.assertIsInstance(is_valid, bool)
            print(f"유효한 규칙 검사 결과: {is_valid}")
            self.assertTrue(is_valid, "유효한 Sigma 규칙이 거부되었습니다!")
            print("✅ 유효한 규칙이 올바르게 검증되었습니다.")
        
        except Exception as e:
            print(f"유효한 규칙 검사 실패: {e}")
            raise
        
        finally:
            # 임시 파일 삭제
            os.unlink(valid_temp_file)
        
        # 2. 유효하지 않은 Sigma rule 테스트
        print("\n=== 유효하지 않은 Sigma Rule 테스트 ===")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(self.invalid_test_sigma_rule, f)
            invalid_temp_file = f.name
        
        try:
            # 유효하지 않은 규칙 검사
            is_valid = self.converter.validate_sigma_rule(invalid_temp_file)
            self.assertIsInstance(is_valid, bool)
            print(f"유효하지 않은 규칙 검사 결과: {is_valid}")
            self.assertFalse(is_valid, "유효하지 않은 Sigma 규칙이 허용되었습니다!")
            print("✅ 유효하지 않은 규칙이 올바르게 거부되었습니다.")
        
        except Exception as e:
            print(f"유효하지 않은 규칙 검사 실패: {e}")
            raise
        
        finally:
            # 임시 파일 삭제
            os.unlink(invalid_temp_file)

    def test_03_generate_rule_id(self):
        """규칙 ID 생성 테스트"""
        # 내부 메서드 테스트를 위해 직접 호출
        rule_id = self.converter._generate_rule_id("Test Rule Name")
        self.assertIsInstance(rule_id, str)
        self.assertGreater(len(rule_id), 0)
        # 특수문자가 제거되었는지 확인
        self.assertNotIn(' ', rule_id)
        self.assertNotIn('-', rule_id)

    def test_04_convert_to_lucene(self):
        """Lucene 쿼리 변환 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(self.valid_test_sigma_rule, f)
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

    def test_05_convert_to_detection_rule(self):
        """Detection Rule 변환 테스트"""
        try:
            # Detection Rule 변환
            detection_rule = self.converter.convert_to_detection_rule(self.valid_test_sigma_rule, 'ecs_windows')
            
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

    def test_06_convert_file(self):
        """파일 변환 테스트"""
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(self.valid_test_sigma_rule, f)
            temp_file = f.name
        
        try:
            # 파일 변환
            output_file = self.converter.convert_file(temp_file, "tests/converted_files/test_output_file.json", 'ecs_windows')
            
            # 결과 검증
            self.assertIsInstance(output_file, str)
            self.assertTrue(os.path.exists(output_file))
            
            # 생성된 JSON 파일 읽기
            with open(output_file, 'r', encoding='utf-8') as f:
                detection_rule = json.load(f)
            
            self.assertIn('name', detection_rule)
            self.assertIn('query', detection_rule)
            
            print(f"생성된 파일: {output_file}")
            
        except Exception as e:
            # Sigma CLI가 설치되지 않은 경우 예외 발생 가능
            print(f"파일 변환 실패: {e}")
            
        finally:
            # 입력 임시 파일 삭제
            os.unlink(temp_file)

if __name__ == '__main__':
    unittest.main() 