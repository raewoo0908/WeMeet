#!/usr/bin/env python3
"""
CLI 배치 명령어 테스트
새로 추가된 CLI 배치 명령어들을 테스트합니다.
"""

import unittest
import json
import tempfile
import os
import shutil
import subprocess
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCLIBatchCommands(unittest.TestCase):
    """CLI 배치 명령어 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 테스트용 Sigma rule들
        self.test_rules = [
            {
                "title": "CLI Test Rule 1",
                "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                "description": "CLI test rule 1 for batch processing",
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
                "title": "CLI Test Rule 2",
                "id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "description": "CLI test rule 2 for batch processing",
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
            }
        ]
        
        # 메인 스크립트 경로
        self.main_script = "src/main.py"
    
    def test_01_convert_to_detection_rule_single_file(self):
        """단일 파일 변환 명령어 테스트"""
        print("\n=== 단일 파일 변환 명령어 테스트 ===")
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
            import yaml
            yaml.dump(self.test_rules[0], temp_file, default_flow_style=False, allow_unicode=True)
            temp_file_path = temp_file.name
        
        try:
            # CLI 명령어 실행
            cmd = [
                sys.executable, self.main_script,
                "convert-to-detection-rule",
                "-i", temp_file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 결과 확인
            self.assertEqual(result.returncode, 0, f"명령어 실패: {result.stderr}")
            
            # 출력에서 성공 메시지 확인
            self.assertIn("Kibana Detection Rule 변환 완료", result.stdout)
            
            print(f"✅ 단일 파일 변환 명령어 테스트 성공")
            
        finally:
            # 임시 파일 정리
            os.unlink(temp_file_path)
    
    def test_02_convert_to_detection_rule_directory(self):
        """디렉터리 변환 명령어 테스트"""
        print("\n=== 디렉터리 변환 명령어 테스트 ===")
        
        # 임시 디렉터리 생성
        temp_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        
        try:
            # Sigma rule 파일들 생성
            for i, rule in enumerate(self.test_rules):
                file_path = os.path.join(temp_dir, f"cli_rule_{i+1}.yml")
                with open(file_path, 'w', encoding='utf-8') as f:
                    import yaml
                    yaml.dump(rule, f, default_flow_style=False, allow_unicode=True)
            
            # CLI 명령어 실행
            cmd = [
                sys.executable, self.main_script,
                "convert-to-detection-rule",
                "-i", temp_dir,
                "-o", output_dir
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # 결과 확인
            self.assertEqual(result.returncode, 0, f"명령어 실패: {result.stderr}")
            
            # 출력에서 성공 메시지 확인
            self.assertIn("처리할 Sigma rule 파일 2개 발견", result.stdout)
            self.assertIn("총 2개 파일 변환 완료", result.stdout)
            
            # 생성된 파일들 확인
            output_files = list(Path(output_dir).glob("*.json"))
            self.assertEqual(len(output_files), 2)
            
            print(f"✅ 디렉터리 변환 명령어 테스트 성공: {len(output_files)}개 파일 생성")
            
        finally:
            # 임시 디렉터리 정리
            shutil.rmtree(temp_dir)
            shutil.rmtree(output_dir)
    
    def test_03_validate_rule_single_file(self):
        """단일 파일 유효성 검사 명령어 테스트"""
        print("\n=== 단일 파일 유효성 검사 명령어 테스트 ===")
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
            import yaml
            yaml.dump(self.test_rules[0], temp_file, default_flow_style=False, allow_unicode=True)
            temp_file_path = temp_file.name
        
        try:
            # CLI 명령어 실행
            cmd = [
                sys.executable, self.main_script,
                "validate-rule",
                "-i", temp_file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 결과 확인
            self.assertEqual(result.returncode, 0, f"명령어 실패: {result.stderr}")
            
            # 출력에서 성공 메시지 확인
            self.assertIn("검사할 Sigma rule 파일 1개 발견", result.stdout)
            self.assertIn("모든 파일이 유효합니다", result.stdout)
            
            print(f"✅ 단일 파일 유효성 검사 명령어 테스트 성공")
            
        finally:
            # 임시 파일 정리
            os.unlink(temp_file_path)
    
    def test_04_validate_rule_directory(self):
        """디렉터리 유효성 검사 명령어 테스트"""
        print("\n=== 디렉터리 유효성 검사 명령어 테스트 ===")
        
        # 임시 디렉터리 생성
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Sigma rule 파일들 생성
            for i, rule in enumerate(self.test_rules):
                file_path = os.path.join(temp_dir, f"validate_rule_{i+1}.yml")
                with open(file_path, 'w', encoding='utf-8') as f:
                    import yaml
                    yaml.dump(rule, f, default_flow_style=False, allow_unicode=True)
            
            # CLI 명령어 실행
            cmd = [
                sys.executable, self.main_script,
                "validate-rule",
                "-i", temp_dir
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # 결과 확인
            self.assertEqual(result.returncode, 0, f"명령어 실패: {result.stderr}")
            
            # 출력에서 성공 메시지 확인
            self.assertIn("검사할 Sigma rule 파일 2개 발견", result.stdout)
            self.assertIn("모든 파일이 유효합니다", result.stdout)
            
            print(f"✅ 디렉터리 유효성 검사 명령어 테스트 성공")
            
        finally:
            # 임시 디렉터리 정리
            shutil.rmtree(temp_dir)
    
    def test_05_convert_to_detection_rule_with_additional_fields(self):
        """추가 필드와 함께 변환 명령어 테스트"""
        print("\n=== 추가 필드와 함께 변환 명령어 테스트 ===")
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
            import yaml
            yaml.dump(self.test_rules[0], temp_file, default_flow_style=False, allow_unicode=True)
            temp_file_path = temp_file.name
        
        try:
            # 추가 필드 JSON
            additional_fields = '{"interval": "15m", "max_signals": 300, "enabled": false}'
            
            # CLI 명령어 실행
            cmd = [
                sys.executable, self.main_script,
                "convert-to-detection-rule",
                "-i", temp_file_path,
                "--additional-fields", additional_fields
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 결과 확인
            self.assertEqual(result.returncode, 0, f"명령어 실패: {result.stderr}")
            
            # 출력에서 성공 메시지 확인
            self.assertIn("추가 필드 설정", result.stdout)
            self.assertIn("Kibana Detection Rule 변환 완료", result.stdout)
            
            print(f"✅ 추가 필드와 함께 변환 명령어 테스트 성공")
            
        finally:
            # 임시 파일 정리
            os.unlink(temp_file_path)
    
    def test_06_convert_and_create_batch_directory(self):
        """디렉터리 일괄 변환 및 생성 명령어 테스트"""
        print("\n=== 디렉터리 일괄 변환 및 생성 명령어 테스트 ===")
        
        # 임시 디렉터리 생성
        temp_dir = tempfile.mkdtemp()
        output_dir = tempfile.mkdtemp()
        
        try:
            # Sigma rule 파일들 생성
            for i, rule in enumerate(self.test_rules):
                file_path = os.path.join(temp_dir, f"batch_rule_{i+1}.yml")
                with open(file_path, 'w', encoding='utf-8') as f:
                    import yaml
                    yaml.dump(rule, f, default_flow_style=False, allow_unicode=True)
            
            # CLI 명령어 실행 (Kibana 연결 없이 변환만 테스트)
            cmd = [
                sys.executable, self.main_script,
                "convert-and-create-batch",
                "-i", temp_dir,
                "-o", output_dir,
                "--kibana-url", "http://nonexistent:5601"  # 존재하지 않는 URL로 설정
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 변환 단계는 성공해야 함
            self.assertIn("처리할 Sigma rule 파일 2개 발견", result.stdout)
            self.assertIn("1단계: Sigma rule 변환 중", result.stdout)
            
            # 생성된 파일들 확인
            output_files = list(Path(output_dir).glob("*.json"))
            self.assertEqual(len(output_files), 2)
            
            print(f"✅ 디렉터리 일괄 변환 및 생성 명령어 테스트 완료: {len(output_files)}개 파일 생성")
            print(f"   (Kibana 연결이 없어서 등록 단계는 생략됨)")
            
        finally:
            # 임시 디렉터리 정리
            shutil.rmtree(temp_dir)
            shutil.rmtree(output_dir)
    
    def test_07_create_rules_batch_directory(self):
        """JSON 파일 일괄 등록 명령어 테스트"""
        print("\n=== JSON 파일 일괄 등록 명령어 테스트 ===")
        
        # 임시 디렉터리 생성
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 모의 Detection Rule JSON 파일들 생성
            for i in range(2):
                detection_rule = {
                    "rule_id": f"cli-test-rule-{i+1}",
                    "name": f"CLI Test Rule {i+1}",
                    "description": f"CLI test rule {i+1} for batch creation",
                    "severity": "medium",
                    "enabled": True,
                    "query": "test query",
                    "language": "kuery",
                    "type": "query"
                }
                
                file_path = os.path.join(temp_dir, f"cli_rule_{i+1}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(detection_rule, f, indent=2, ensure_ascii=False)
            
            # CLI 명령어 실행 (Kibana 연결 없이)
            cmd = [
                sys.executable, self.main_script,
                "create-rules-batch",
                "-i", temp_dir,
                "--kibana-url", "http://nonexistent:5601"  # 존재하지 않는 URL로 설정
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 파일 검색은 성공해야 함
            self.assertIn("등록할 Detection Rule JSON 파일 2개 발견", result.stdout)
            
            print(f"✅ JSON 파일 일괄 등록 명령어 테스트 완료")
            print(f"   (Kibana 연결이 없어서 등록 단계는 생략됨)")
            
        finally:
            # 임시 디렉터리 정리
            shutil.rmtree(temp_dir)
    
    def test_08_error_handling_invalid_path(self):
        """잘못된 경로 에러 처리 테스트"""
        print("\n=== 잘못된 경로 에러 처리 테스트 ===")
        
        # 존재하지 않는 파일로 테스트
        cmd = [
            sys.executable, self.main_script,
            "convert-to-detection-rule",
            "-i", "/nonexistent/file.yml"
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 에러가 발생해야 함
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("존재하지 않는 경로입니다", result.stderr)
        
        print(f"✅ 잘못된 경로 에러 처리 테스트 성공")
    
    def test_09_error_handling_invalid_json(self):
        """잘못된 JSON 에러 처리 테스트"""
        print("\n=== 잘못된 JSON 에러 처리 테스트 ===")
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
            import yaml
            yaml.dump(self.test_rules[0], temp_file, default_flow_style=False, allow_unicode=True)
            temp_file_path = temp_file.name
        
        try:
            # 잘못된 JSON 형식의 추가 필드
            invalid_json = '{"interval": "10m", "max_signals": 200,}'
            
            cmd = [
                sys.executable, self.main_script,
                "convert-to-detection-rule",
                "-i", temp_file_path,
                "--additional-fields", invalid_json
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # JSON 파싱 에러가 발생해야 함
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("추가 필드 JSON 파싱 실패", result.stderr)
            
            print(f"✅ 잘못된 JSON 에러 처리 테스트 성공")
            
        finally:
            # 임시 파일 정리
            os.unlink(temp_file_path)
    
    def test_10_help_commands(self):
        """도움말 명령어 테스트"""
        print("\n=== 도움말 명령어 테스트 ===")
        
        # 메인 도움말
        cmd = [sys.executable, self.main_script, "--help"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("convert-to-detection-rule", result.stdout)
        self.assertIn("validate-rule", result.stdout)
        self.assertIn("convert-and-create-batch", result.stdout)
        self.assertIn("create-rules-batch", result.stdout)
        
        # 개별 명령어 도움말
        commands = [
            "convert-to-detection-rule",
            "validate-rule", 
            "convert-and-create-batch",
            "create-rules-batch"
        ]
        
        for command in commands:
            cmd = [sys.executable, self.main_script, command, "--help"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            self.assertEqual(result.returncode, 0, f"명령어 {command} 도움말 실패")
        
        print(f"✅ 도움말 명령어 테스트 성공")


def run_cli_batch_commands_tests():
    """CLI 배치 명령어 테스트 실행"""
    print("🧪 CLI 배치 명령어 테스트 시작")
    
    # 테스트 스위트 생성
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCLIBatchCommands)
    
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
    success = run_cli_batch_commands_tests()
    exit(0 if success else 1) 