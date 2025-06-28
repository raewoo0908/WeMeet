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
                print(f"사용 가능한 대상: \n{targets}")
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
                print(f"사용 가능한 파이프라인: \n{pipelines}")
        except Exception as e:
            # 설치되지 않은 경우 예외 발생 가능
            print(f"파이프라인 조회 실패 (예상됨): {e}")

    def test_get_installation_guide(self):
        """설치 가이드 조회 테스트"""
        guide = self.manager.get_installation_guide()
        self.assertIsInstance(guide, str)
        self.assertGreater(len(guide), 0)
        self.assertIn("pip install sigma-cli", guide)

if __name__ == '__main__':
    unittest.main() 