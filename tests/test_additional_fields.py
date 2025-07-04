#!/usr/bin/env python3
"""
추가 필드 설정 테스트
Sigma rule 변환 시 추가 필드를 설정하는 기능을 테스트합니다.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sigma_cli_converter import SigmaCLIConverter


class TestAdditionalFields(unittest.TestCase):
    """추가 필드 기능 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.converter = SigmaCLIConverter()
        
        # 테스트용 Sigma rule
        self.test_rule = {
            "title": "Suspicious PowerShell Execution",
            "id": "12345678-1234-1234-1234-123456789012",
            "description": "Detects suspicious PowerShell execution patterns",
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
            "level": "high",
            "tags": ["attack.execution", "attack.t1059.001"]
        }
        
        # 기본 추가 필드
        self.basic_additional_fields = {
            "interval": "10m",
            "max_signals": 500,
            "enabled": False,
            "risk_score": 85
        }
        
        # 복잡한 추가 필드 (MITRE ATT&CK 정보 포함)
        self.complex_additional_fields = {
            "interval": "5m",
            "max_signals": 1000,
            "from": "now-2h",
            "to": "now",
            "enabled": True,
            "risk_score": 95,
            "meta": {
                "from": "5m",
                "kibana_siem_app_url": "https://kibana.example.com/app/security",
                "custom_field": "custom_value"
            },
            "threat": [
                {
                    "framework": "MITRE ATT&CK",
                    "tactic": {
                        "id": "TA0002",
                        "name": "Execution",
                        "reference": "https://attack.mitre.org/tactics/TA0002/"
                    },
                    "technique": [
                        {
                            "id": "T1059.001",
                            "name": "PowerShell",
                            "reference": "https://attack.mitre.org/techniques/T1059/001/"
                        }
                    ]
                }
            ],
            "references": [
                "https://docs.microsoft.com/en-us/powershell/scripting/overview",
                "https://attack.mitre.org/techniques/T1059/001/"
            ],
            "false_positives": [
                "Legitimate PowerShell scripts for system administration",
                "Automated deployment tools using PowerShell"
            ],
            "setup": "Enable PowerShell logging and process monitoring",
            "author": ["Security Team", "Threat Intelligence"],
            "license": "DRL"
        }
    
    def test_01_basic_additional_fields(self):
        """기본 추가 필드 테스트"""
        print("\n=== 기본 추가 필드 테스트 ===")
        
        # 추가 필드 없이 변환
        detection_rule_basic = self.converter.convert_to_detection_rule(
            self.test_rule, 
            pipeline="ecs_windows"
        )
        
        # 추가 필드와 함께 변환
        detection_rule_with_fields = self.converter.convert_to_detection_rule(
            self.test_rule, 
            pipeline="ecs_windows",
            additional_fields=self.basic_additional_fields
        )
        
        # 기본값과 추가 필드 값 비교
        self.assertEqual(detection_rule_basic.get('interval'), '5m')  # 기본값
        self.assertEqual(detection_rule_with_fields.get('interval'), '10m')  # 추가 필드 값
        
        self.assertEqual(detection_rule_basic.get('max_signals'), 100)  # 기본값
        self.assertEqual(detection_rule_with_fields.get('max_signals'), 500)  # 추가 필드 값
        
        self.assertEqual(detection_rule_basic.get('enabled'), True)  # 기본값
        self.assertEqual(detection_rule_with_fields.get('enabled'), False)  # 추가 필드 값
        
        self.assertEqual(detection_rule_basic.get('risk_score'), 73)  # high 레벨 기본값
        self.assertEqual(detection_rule_with_fields.get('risk_score'), 85)  # 추가 필드 값
        
        print(f"✅ 기본 추가 필드 테스트 성공")
        print(f"   - 기본 interval: {detection_rule_basic.get('interval')} → 추가 필드: {detection_rule_with_fields.get('interval')}")
        print(f"   - 기본 max_signals: {detection_rule_basic.get('max_signals')} → 추가 필드: {detection_rule_with_fields.get('max_signals')}")
        print(f"   - 기본 enabled: {detection_rule_basic.get('enabled')} → 추가 필드: {detection_rule_with_fields.get('enabled')}")
        print(f"   - 기본 risk_score: {detection_rule_basic.get('risk_score')} → 추가 필드: {detection_rule_with_fields.get('risk_score')}")
    
    def test_02_complex_additional_fields(self):
        """복잡한 추가 필드 테스트 (MITRE ATT&CK 정보 포함)"""
        print("\n=== 복잡한 추가 필드 테스트 ===")
        
        detection_rule = self.converter.convert_to_detection_rule(
            self.test_rule, 
            pipeline="ecs_windows",
            additional_fields=self.complex_additional_fields
        )
        
        # 복잡한 필드들이 제대로 설정되었는지 확인
        self.assertEqual(detection_rule.get('interval'), '5m')
        self.assertEqual(detection_rule.get('max_signals'), 1000)
        self.assertEqual(detection_rule.get('from'), 'now-2h')
        self.assertEqual(detection_rule.get('to'), 'now')
        self.assertEqual(detection_rule.get('enabled'), True)
        self.assertEqual(detection_rule.get('risk_score'), 95)
        
        # meta 필드 확인
        meta = detection_rule.get('meta', {})
        self.assertEqual(meta.get('kibana_siem_app_url'), 'https://kibana.example.com/app/security')
        self.assertEqual(meta.get('custom_field'), 'custom_value')
        
        # threat 필드 확인
        threat = detection_rule.get('threat', [])
        self.assertEqual(len(threat), 1)
        self.assertEqual(threat[0]['framework'], 'MITRE ATT&CK')
        self.assertEqual(threat[0]['tactic']['id'], 'TA0002')
        self.assertEqual(len(threat[0]['technique']), 1)
        self.assertEqual(threat[0]['technique'][0]['id'], 'T1059.001')
        
        # references 필드 확인
        references = detection_rule.get('references', [])
        self.assertEqual(len(references), 2)
        self.assertIn('https://attack.mitre.org/techniques/T1059/001/', references)
        
        print(f"✅ 복잡한 추가 필드 테스트 성공")
        print(f"   - MITRE ATT&CK 위협 정보: {len(threat)}개")
        print(f"   - 참조 링크: {len(references)}개")
        print(f"   - 커스텀 메타 필드: {meta.get('custom_field')}")
    
    def test_03_file_conversion_with_additional_fields(self):
        """파일 변환 시 추가 필드 테스트"""
        print("\n=== 파일 변환 시 추가 필드 테스트 ===")
        
        # 임시 Sigma rule 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
            import yaml
            yaml.dump(self.test_rule, temp_file, default_flow_style=False, allow_unicode=True)
            temp_sigma_file = temp_file.name
        
        try:
            # 추가 필드 없이 변환
            output_file_basic = self.converter.convert_file(
                temp_sigma_file, 
                output_file="basic.detection_rule.json",
                pipeline="ecs_windows"
            )
            
            # 추가 필드와 함께 변환
            output_file_with_fields = self.converter.convert_file(
                temp_sigma_file, 
                output_file="with_fields.detection_rule.json",
                pipeline="ecs_windows",
                additional_fields=self.basic_additional_fields
            )
            
            # 결과 파일 로드 및 비교
            with open(output_file_basic, 'r', encoding='utf-8') as f:
                detection_rule_basic = json.load(f)
            
            with open(output_file_with_fields, 'r', encoding='utf-8') as f:
                detection_rule_with_fields = json.load(f)
            
            # 필드 값 비교
            self.assertEqual(detection_rule_basic.get('interval'), '5m')
            self.assertEqual(detection_rule_with_fields.get('interval'), '10m')
            
            self.assertEqual(detection_rule_basic.get('max_signals'), 100)
            self.assertEqual(detection_rule_with_fields.get('max_signals'), 500)
            
            print(f"✅ 파일 변환 시 추가 필드 테스트 성공")
            print(f"   - 기본 파일: {output_file_basic}")
            print(f"   - 추가 필드 파일: {output_file_with_fields}")
            
            # 임시 파일 정리
            os.unlink(output_file_basic)
            os.unlink(output_file_with_fields)
            
        finally:
            # 임시 Sigma rule 파일 정리
            os.unlink(temp_sigma_file)
    
    def test_04_field_override_behavior(self):
        """필드 덮어쓰기 동작 테스트"""
        print("\n=== 필드 덮어쓰기 동작 테스트 ===")
        
        # 기존 필드를 덮어쓰는 추가 필드
        override_fields = {
            "name": "Overridden Rule Name",
            "description": "This description is overridden",
            "severity": "low",
            "rule_id": "overridden-rule-id"
        }
        
        detection_rule = self.converter.convert_to_detection_rule(
            self.test_rule, 
            pipeline="ecs_windows",
            additional_fields=override_fields
        )
        
        # 기존 필드가 덮어써졌는지 확인
        self.assertEqual(detection_rule.get('name'), 'Overridden Rule Name')
        self.assertEqual(detection_rule.get('description'), 'This description is overridden')
        self.assertEqual(detection_rule.get('severity'), 'low')
        self.assertEqual(detection_rule.get('rule_id'), 'overridden-rule-id')
        
        print(f"✅ 필드 덮어쓰기 동작 테스트 성공")
        print(f"   - 원본 이름: {self.test_rule.get('title')} → 덮어쓴 이름: {detection_rule.get('name')}")
        print(f"   - 원본 설명: {self.test_rule.get('description')} → 덮어쓴 설명: {detection_rule.get('description')}")
    
    def test_05_none_additional_fields(self):
        """None 추가 필드 테스트"""
        print("\n=== None 추가 필드 테스트 ===")
        
        # None 추가 필드로 변환
        detection_rule = self.converter.convert_to_detection_rule(
            self.test_rule, 
            pipeline="ecs_windows",
            additional_fields=None
        )
        
        # 기본값이 그대로 유지되는지 확인
        self.assertEqual(detection_rule.get('interval'), '5m')
        self.assertEqual(detection_rule.get('max_signals'), 100)
        self.assertEqual(detection_rule.get('enabled'), True)
        self.assertEqual(detection_rule.get('risk_score'), 73)  # high 레벨
        
        print(f"✅ None 추가 필드 테스트 성공")
        print(f"   - 기본값이 그대로 유지됨")


def run_additional_fields_tests():
    """추가 필드 테스트 실행"""
    print("🧪 추가 필드 기능 테스트 시작")
    
    # 테스트 스위트 생성
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestAdditionalFields)
    
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
    success = run_additional_fields_tests()
    exit(0 if success else 1) 