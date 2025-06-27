#!/usr/bin/env python3
"""
Sigma CLI Wrapper
Sigma CLI를 래핑하여 우리 프로젝트에서 사용할 수 있는 인터페이스 제공
"""

import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml


class SigmaCLIWrapper:
    """Sigma CLI를 래핑하는 클래스"""
    
    def __init__(self, sigma_cli_path: str = "sigma"):
        """
        Sigma CLI 래퍼 초기화
        
        Args:
            sigma_cli_path: sigma CLI 명령어 경로 (기본값: "sigma")
        """
        self.sigma_cli_path = sigma_cli_path
        self._check_sigma_cli()
    
    def _check_sigma_cli(self):
        """Sigma CLI가 설치되어 있는지 확인"""
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Sigma CLI 확인됨: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                f"Sigma CLI를 찾을 수 없습니다. 설치 방법:\n"
                f"pip install sigma-cli\n"
                f"또는\n"
                f"pipx install sigma-cli"
            )
    
    def convert_to_lucene(self, sigma_rule_path: str, pipeline: str = "ecs_windows") -> str:
        """
        Sigma rule을 Lucene 쿼리로 변환
        
        Args:
            sigma_rule_path: Sigma rule 파일 경로
            pipeline: 사용할 처리 파이프라인 (기본값: "ecs_windows")
            
        Returns:
            변환된 Lucene 쿼리 문자열
        """
        try:
            cmd = [
                self.sigma_cli_path, "convert",
                "-t", "lucene",
                "-p", pipeline,
                sigma_rule_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Sigma CLI 변환 실패: {e.stderr}")
    
    def convert_to_elasticsearch(self, sigma_rule_path: str, pipeline: str = "ecs_windows") -> str:
        """
        Sigma rule을 Elasticsearch 쿼리로 변환
        
        Args:
            sigma_rule_path: Sigma rule 파일 경로
            pipeline: 사용할 처리 파이프라인 (기본값: "ecs_windows")
            
        Returns:
            변환된 Elasticsearch 쿼리 문자열
        """
        try:
            cmd = [
                self.sigma_cli_path, "convert",
                "-t", "elasticsearch",
                "-p", pipeline,
                sigma_rule_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Sigma CLI 변환 실패: {e.stderr}")
    
    def convert_sigma_rule_dict(self, sigma_rule: Dict[str, Any], 
                               target: str = "lucene", 
                               pipeline: str = "ecs_windows") -> str:
        """
        Sigma rule 딕셔너리를 임시 파일로 저장하고 변환
        
        Args:
            sigma_rule: Sigma rule 딕셔너리
            target: 변환 대상 (lucene, elasticsearch 등)
            pipeline: 사용할 처리 파이프라인
            
        Returns:
            변환된 쿼리 문자열
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
            yaml.dump(sigma_rule, temp_file, default_flow_style=False, allow_unicode=True)
            temp_file_path = temp_file.name
        
        try:
            if target == "lucene":
                return self.convert_to_lucene(temp_file_path, pipeline)
            elif target == "elasticsearch":
                return self.convert_to_elasticsearch(temp_file_path, pipeline)
            else:
                raise ValueError(f"지원하지 않는 변환 대상: {target}")
        finally:
            # 임시 파일 삭제
            os.unlink(temp_file_path)
    
    def list_available_targets(self) -> List[str]:
        """사용 가능한 변환 대상을 조회"""
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "list", "targets"],
                capture_output=True,
                text=True,
                check=True
            )
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"대상 조회 실패: {e.stderr}")
    
    def list_available_pipelines(self) -> List[str]:
        """사용 가능한 파이프라인을 조회"""
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "list", "pipelines"],
                capture_output=True,
                text=True,
                check=True
            )
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"파이프라인 조회 실패: {e.stderr}")
    
    def validate_sigma_rule(self, sigma_rule_path: str) -> bool:
        """
        Sigma rule 유효성 검사
        
        Args:
            sigma_rule_path: Sigma rule 파일 경로
            
        Returns:
            유효성 검사 결과
        """
        try:
            cmd = [
                self.sigma_cli_path, "check",
                sigma_rule_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            return True
            
        except subprocess.CalledProcessError:
            return False


class EnhancedKibanaConverter:
    """Sigma CLI를 활용한 향상된 Kibana 변환기"""
    
    def __init__(self, sigma_cli_path: str = "sigma"):
        """
        향상된 Kibana 변환기 초기화
        
        Args:
            sigma_cli_path: sigma CLI 명령어 경로
        """
        self.sigma_cli = SigmaCLIWrapper(sigma_cli_path)
        self.field_mappings = {
            'process_creation': {
                'CommandLine': 'process.command_line',
                'Image': 'process.executable',
                'User': 'user.name',
                'ComputerName': 'host.name',
                'ProcessId': 'process.pid',
                'ParentProcessId': 'process.parent.pid'
            }
        }
    
    def convert_sigma_to_kql(self, sigma_rule: Dict[str, Any], 
                           pipeline: str = "ecs_windows") -> str:
        """
        Sigma rule을 KQL로 변환 (Sigma CLI 활용)
        
        Args:
            sigma_rule: Sigma rule 딕셔너리
            pipeline: 사용할 처리 파이프라인
            
        Returns:
            변환된 KQL 쿼리
        """
        try:
            # Sigma CLI로 Lucene 쿼리 생성
            lucene_query = self.sigma_cli.convert_sigma_rule_dict(
                sigma_rule, target="lucene", pipeline=pipeline
            )
            
            # Lucene을 KQL로 변환 (필요시)
            kql_query = self._lucene_to_kql(lucene_query)
            
            return kql_query
            
        except Exception as e:
            print(f"Sigma CLI 변환 실패, 기존 변환기 사용: {e}")
            # 실패 시 기존 변환기 사용
            return self._fallback_conversion(sigma_rule)
    
    def _lucene_to_kql(self, lucene_query: str) -> str:
        """
        Lucene 쿼리를 KQL로 변환
        
        Args:
            lucene_query: Lucene 쿼리 문자열
            
        Returns:
            KQL 쿼리 문자열
        """
        # Lucene과 KQL은 매우 유사하므로 대부분 그대로 사용 가능
        # 필요시 추가 변환 로직 구현
        return lucene_query
    
    def _fallback_conversion(self, sigma_rule: Dict[str, Any]) -> str:
        """기존 변환기로 폴백"""
        from .kibana_converter import SigmaToKibanaConverter
        converter = SigmaToKibanaConverter()
        return converter.convert_to_kql_query(sigma_rule)
    
    def convert_to_detection_rule(self, sigma_rule: Dict[str, Any], 
                                pipeline: str = "ecs_windows") -> Dict[str, Any]:
        """
        Sigma rule을 Kibana Detection Rule로 변환
        
        Args:
            sigma_rule: Sigma rule 딕셔너리
            pipeline: 사용할 처리 파이프라인
            
        Returns:
            Kibana Detection Rule 딕셔너리
        """
        # 기존 변환기 사용 (Detection Rule 구조는 동일)
        from .kibana_converter import SigmaToKibanaConverter
        converter = SigmaToKibanaConverter()
        
        # KQL 쿼리는 Sigma CLI로 생성
        kql_query = self.convert_sigma_to_kql(sigma_rule, pipeline)
        
        # Detection Rule 구조 생성
        detection_rule = converter.convert_to_detection_rule(sigma_rule)
        
        # KQL 쿼리 업데이트
        detection_rule['query'] = kql_query
        
        return detection_rule


if __name__ == "__main__":
    test_sigma_cli_integration() 