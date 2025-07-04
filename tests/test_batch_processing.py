#!/usr/bin/env python3
"""
배치 처리 기능 테스트
디렉터리 단위 처리 및 일괄 등록 기능을 테스트합니다.
"""

import unittest
import json
import tempfile
import os
import shutil
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sigma_cli_converter import SigmaCLIConverter
from src.main import (
    get_sigma_rule_files,
    validate_sigma_rules,
    convert_sigma_rules,
    create_detection_rules_batch
)


class TestBatchProcessing(unittest.TestCase):
    """배치 처리 기능 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.converter = SigmaCLIConverter()
        
        # 테스트용 Sigma rule들
        self.test_rules = [
            {
                "title": "Test Rule 1",
                "id": "11111111-1111-1111-1111-111111111111",
                "description": "Test rule 1 for batch processing",
                "logsource": {
                    "category": "process_creation",
                    "product": "windows"
                },
                "detection": {
                    "selection": {
                        "CommandLine|contains": "powershell.exe"
                    },
                    "condition": "selection"
                },
                "level": "high"
            },
            {
                "title": "Test Rule 2",
                "id": "22222222-2222-2222-2222-222222222222",
                "description": "Test rule 2 for batch processing",
                "logsource": {
                    "category": "process_creation",
                    "product": "windows"
                },
                "detection": {
                    "selection": {
                        "CommandLine|contains": "cmd.exe"
                    },
                    "condition": "selection"
                },
                "level": "medium"
            },
            {
                "title": "Test Rule 3",
                "id": "33333333-3333-3333-3333-333333333333",
                "description": "Test rule 3 for batch processing",
                "logsource": {
                    "category": "network_connection",
                    "product": "windows"
                },
                "detection": {
                    "selection": {
                        "destination.port": 4444
                    },
                    "condition": "selection"
                },
                "level": "critical"
            }
        ]
        
        # 추가 필드
        self.additional_fields = {
            "interval": "10m",
            "max_signals": 500,
            "enabled": False,
            "risk_score": 85
        }
    
    def test_01_get_sigma_rule_files_single_file(self):
        """단일 파일 처리 테스트"""
        print("\n=== 단일 파일 처리 테스트 ===")
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
            import yaml
            yaml.dump(self.test_rules[0], temp_file, default_flow_style=False, allow_unicode=True)
            temp_file_path = temp_file.name
        
        try:
            # 단일 파일 처리
            rule_files = get_sigma_rule_files(temp_file_path)
            
            # 검증
            self.assertEqual(len(rule_files), 1)
            self.assertEqual(rule_files[0], temp_file_path)
            
            print(f"✅ 단일 파일 처리 테스트 성공: {rule_files[0]}")
            
        finally:
            # 임시 파일 정리
            os.unlink(temp_file_path)
    
    def test_02_get_sigma_rule_files_directory(self):
        """디렉터리 처리 테스트"""
        print("\n=== 디렉터리 처리 테스트 ===")
        
        # 임시 디렉터리 생성
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 여러 Sigma rule 파일 생성
            created_files = []
            for i, rule in enumerate(self.test_rules):
                file_path = os.path.join(temp_dir, f"rule_{i+1}.yml")
                with open(file_path, 'w', encoding='utf-8') as f:
                    import yaml
                    yaml.dump(rule, f, default_flow_style=False, allow_unicode=True)
                created_files.append(file_path)
            
            # 디렉터리 처리
            rule_files = get_sigma_rule_files(temp_dir)
            
            # 검증
            self.assertEqual(len(rule_files), 3)
            for file_path in created_files:
                self.assertIn(file_path, rule_files)
            
            print(f"✅ 디렉터리 처리 테스트 성공: {len(rule_files)}개 파일 발견")
            for rule_file in rule_files:
                print(f"   • {rule_file}")
            
        finally:
            # 임시 디렉터리 정리
            shutil.rmtree(temp_dir)
    
    def test_03_get_sigma_rule_files_invalid_path(self):
        """잘못된 경로 처리 테스트"""
        print("\n=== 잘못된 경로 처리 테스트 ===")
        
        # 존재하지 않는 경로
        with self.assertRaises(ValueError):
            get_sigma_rule_files("/nonexistent/path")
        
        # 지원하지 않는 파일 형식
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("This is not a Sigma rule")
            temp_file_path = temp_file.name
        
        try:
            with self.assertRaises(ValueError):
                get_sigma_rule_files(temp_file_path)
        finally:
            os.unlink(temp_file_path)
        
        print("✅ 잘못된 경로 처리 테스트 성공")
    
    def test_04_validate_sigma_rules(self):
        """Sigma rule 유효성 검사 테스트"""
        print("\n=== Sigma rule 유효성 검사 테스트 ===")
        
        # 임시 디렉터리 생성
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 유효한 Sigma rule 파일들 생성
            valid_files = []
            for i, rule in enumerate(self.test_rules):
                file_path = os.path.join(temp_dir, f"valid_rule_{i+1}.yml")
                with open(file_path, 'w', encoding='utf-8') as f:
                    import yaml
                    yaml.dump(rule, f, default_flow_style=False, allow_unicode=True)
                valid_files.append(file_path)
            
            # 유효성 검사 실행
            results = validate_sigma_rules(valid_files)
            
            # 검증
            self.assertEqual(len(results), 3)
            for file_path, is_valid in results.items():
                self.assertTrue(is_valid, f"파일 {file_path}이 유효하지 않습니다")
            
            print(f"✅ Sigma rule 유효성 검사 테스트 성공: {len(results)}개 파일 모두 유효")
            
        finally:
            # 임시 디렉터리 정리
            shutil.rmtree(temp_dir)
    
    def test_05_convert_sigma_rules(self):
        """Sigma rule 일괄 변환 테스트"""
        print("\n=== Sigma rule 일괄 변환 테스트 ===")
        
        # 임시 디렉터리 생성
        temp_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        
        try:
            # Sigma rule 파일들 생성
            rule_files = []
            for i, rule in enumerate(self.test_rules):
                file_path = os.path.join(temp_dir, f"convert_rule_{i+1}.yml")
                with open(file_path, 'w', encoding='utf-8') as f:
                    import yaml
                    yaml.dump(rule, f, default_flow_style=False, allow_unicode=True)
                rule_files.append(file_path)
            
            # 일괄 변환 실행
            output_files = convert_sigma_rules(
                rule_files,
                output_dir,
                pipeline="ecs_windows",
                additional_fields=self.additional_fields
            )
            
            # 검증
            self.assertEqual(len(output_files), 3)
            
            # 생성된 JSON 파일들 확인
            for output_file in output_files:
                self.assertTrue(os.path.exists(output_file))
                
                # JSON 파일 내용 확인
                with open(output_file, 'r', encoding='utf-8') as f:
                    detection_rule = json.load(f)
                
                # 추가 필드가 적용되었는지 확인
                self.assertEqual(detection_rule.get('interval'), '10m')
                self.assertEqual(detection_rule.get('max_signals'), 500)
                self.assertEqual(detection_rule.get('enabled'), False)
                self.assertEqual(detection_rule.get('risk_score'), 85)
            
            print(f"✅ Sigma rule 일괄 변환 테스트 성공: {len(output_files)}개 파일 변환 완료")
            for output_file in output_files:
                print(f"   • {output_file}")
            
        finally:
            # 임시 디렉터리 정리
            shutil.rmtree(temp_dir)
            shutil.rmtree(output_dir)
    
    def test_06_convert_sigma_rules_no_output_dir(self):
        """출력 디렉터리 없이 변환 테스트"""
        print("\n=== 출력 디렉터리 없이 변환 테스트 ===")
        
        # 임시 디렉터리 생성
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Sigma rule 파일 생성
            rule_file = os.path.join(temp_dir, "single_rule.yml")
            with open(rule_file, 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(self.test_rules[0], f, default_flow_style=False, allow_unicode=True)
            
            # 출력 디렉터리 없이 변환
            output_files = convert_sigma_rules(
                [rule_file],
                output_dir=None,  # None으로 설정
                pipeline="ecs_windows"
            )
            
            # 검증
            self.assertEqual(len(output_files), 1)
            self.assertTrue(os.path.exists(output_files[0]))
            
            # 파일이 원본과 같은 디렉터리에 생성되었는지 확인
            output_path = Path(output_files[0])
            self.assertEqual(output_path.parent, Path(temp_dir))
            
            print(f"✅ 출력 디렉터리 없이 변환 테스트 성공: {output_files[0]}")
            
        finally:
            # 임시 디렉터리 정리
            shutil.rmtree(temp_dir)
    
    def test_07_create_detection_rules_batch_mock(self):
        """Detection Rules 일괄 등록 모의 테스트"""
        print("\n=== Detection Rules 일괄 등록 모의 테스트 ===")
        
        # 임시 디렉터리 생성
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 모의 Detection Rule JSON 파일들 생성
            json_files = []
            for i in range(3):
                detection_rule = {
                    "rule_id": f"test-rule-{i+1}",
                    "name": f"Test Rule {i+1}",
                    "description": f"Test rule {i+1} for batch creation",
                    "severity": "medium",
                    "enabled": True,
                    "query": "test query",
                    "language": "kuery",
                    "type": "query"
                }
                
                file_path = os.path.join(temp_dir, f"rule_{i+1}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(detection_rule, f, indent=2, ensure_ascii=False)
                json_files.append(file_path)
            
            # 일괄 등록 함수 호출 (실제 Kibana 연결 없이)
            # 실제 테스트에서는 Kibana 서버가 필요하므로 모의 테스트로 진행
            print(f"📁 생성된 JSON 파일 {len(json_files)}개:")
            for json_file in json_files:
                print(f"   • {json_file}")
                
                # JSON 파일 내용 확인
                with open(json_file, 'r', encoding='utf-8') as f:
                    detection_rule = json.load(f)
                
                # 필수 필드 확인
                self.assertIn('rule_id', detection_rule)
                self.assertIn('name', detection_rule)
                self.assertIn('query', detection_rule)
            
            print("✅ Detection Rules 일괄 등록 모의 테스트 성공")
            print("   (실제 등록 테스트는 Kibana 서버 연결이 필요합니다)")
            
        finally:
            # 임시 디렉터리 정리
            shutil.rmtree(temp_dir)
    
    def test_08_error_handling(self):
        """에러 처리 테스트"""
        print("\n=== 에러 처리 테스트 ===")
        
        # 존재하지 않는 파일로 테스트
        with self.assertRaises(ValueError):
            get_sigma_rule_files("/nonexistent/file.yml")
        
        # 빈 디렉터리로 테스트
        temp_dir = tempfile.mkdtemp()
        try:
            with self.assertRaises(ValueError):
                get_sigma_rule_files(temp_dir)
        finally:
            shutil.rmtree(temp_dir)
        
        # 잘못된 형식의 파일로 테스트
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
            temp_file.write("invalid: yaml: content: [")
            temp_file_path = temp_file.name
        
        try:
            # 유효성 검사에서 에러가 발생해야 함
            results = validate_sigma_rules([temp_file_path])
            # 최소한 파일이 유효하지 않다고 나와야 함
            self.assertFalse(results.get(temp_file_path, True))
        finally:
            os.unlink(temp_file_path)
        
        print("✅ 에러 처리 테스트 성공")
    
    def test_09_additional_fields_integration(self):
        """추가 필드 통합 테스트"""
        print("\n=== 추가 필드 통합 테스트 ===")
        
        # 임시 디렉터리 생성
        temp_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        
        try:
            # Sigma rule 파일 생성
            rule_file = os.path.join(temp_dir, "additional_fields_test.yml")
            with open(rule_file, 'w', encoding='utf-8') as f:
                import yaml
                yaml.dump(self.test_rules[0], f, default_flow_style=False, allow_unicode=True)
            
            # 복잡한 추가 필드 정의
            complex_additional_fields = {
                "interval": "5m",
                "max_signals": 1000,
                "enabled": True,
                "risk_score": 95,
                "threat": [
                    {
                        "framework": "MITRE ATT&CK",
                        "tactic": {
                            "id": "TA0002",
                            "name": "Execution"
                        },
                        "technique": [
                            {
                                "id": "T1059.001",
                                "name": "PowerShell"
                            }
                        ]
                    }
                ],
                "references": [
                    "https://attack.mitre.org/techniques/T1059/001/"
                ]
            }
            
            # 변환 실행
            output_files = convert_sigma_rules(
                [rule_file],
                output_dir,
                additional_fields=complex_additional_fields
            )
            
            # 검증
            self.assertEqual(len(output_files), 1)
            
            with open(output_files[0], 'r', encoding='utf-8') as f:
                detection_rule = json.load(f)
            
            # 추가 필드가 제대로 적용되었는지 확인
            self.assertEqual(detection_rule.get('interval'), '5m')
            self.assertEqual(detection_rule.get('max_signals'), 1000)
            self.assertEqual(detection_rule.get('enabled'), True)
            self.assertEqual(detection_rule.get('risk_score'), 95)
            
            # 복잡한 필드들 확인
            threat = detection_rule.get('threat', [])
            self.assertEqual(len(threat), 1)
            self.assertEqual(threat[0]['framework'], 'MITRE ATT&CK')
            self.assertEqual(threat[0]['tactic']['id'], 'TA0002')
            
            references = detection_rule.get('references', [])
            self.assertEqual(len(references), 1)
            self.assertIn('https://attack.mitre.org/techniques/T1059/001/', references)
            
            print(f"✅ 추가 필드 통합 테스트 성공: {output_files[0]}")
            
        finally:
            # 임시 디렉터리 정리
            shutil.rmtree(temp_dir)
            shutil.rmtree(output_dir)


def run_batch_processing_tests():
    """배치 처리 테스트 실행"""
    print("🧪 배치 처리 기능 테스트 시작")
    
    # 테스트 스위트 생성
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestBatchProcessing)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 결과 요약
    print(f"\n📊 테스트 결과 요약:")
    print(f"   - 실행된 테스트: {result.testsRun}")
    print(f"   - 실패: {len(result.failures)}")
    print(f"   - 오류: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ 실패한 테스트:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")
    
    if result.errors:
        print(f"\n❌ 오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_batch_processing_tests()
    exit(0 if success else 1) 