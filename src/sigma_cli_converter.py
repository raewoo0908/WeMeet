#!/usr/bin/env python3
"""
Sigma CLI 전용 변환기
Sigma CLI를 사용하여 Sigma rule을 Lucene 쿼리로 변환하고 Detection Rule을 생성하는 클래스
"""

import subprocess
import json
import tempfile
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml


class SigmaCLIConverter:
    """Sigma CLI만을 사용하는 변환기 (순수 변환 기능만 담당)"""
    
    def __init__(self, sigma_cli_path: str = "sigma"):
        """
        Sigma CLI 변환기 초기화
        
        Args:
            sigma_cli_path: sigma CLI 명령어 경로 (기본값: "sigma")
        """
        self.sigma_cli_path = sigma_cli_path
    
    def load_sigma_rule(self, file_path: str) -> Dict[str, Any]:
        """Sigma rule 파일을 로드합니다."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
        
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
    
    def convert_to_lucene(self, sigma_rule_path: str, pipeline: str) -> str:
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
            
            lucene_query = result.stdout.strip()

            return lucene_query
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Sigma CLI 변환 실패: {e.stderr}")

    def convert_sigma_rule_to_lucene(self, sigma_rule: Dict[str, Any], 
                               pipeline: str = "ecs_windows") -> str:
        """
        Sigma rule 딕셔너리를 임시 파일로 저장하고 Lucene으로 변환
        
        Args:
            sigma_rule: Sigma rule 딕셔너리
            pipeline: 사용할 처리 파이프라인
            
        Returns:
            변환된 Lucene 쿼리 문자열
        """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as temp_file:
            yaml.dump(sigma_rule, temp_file, default_flow_style=False, allow_unicode=True)
            temp_file_path = temp_file.name
        
        try:
            return self.convert_to_lucene(temp_file_path, pipeline)
        finally:
            # 임시 파일 삭제
            os.unlink(temp_file_path)
    
    def convert_to_detection_rule(self, sigma_rule: Dict[str, Any], 
                                pipeline: str = None,
                                additional_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sigma rule을 Kibana Detection Rule로 변환합니다.
        
        Args:
            sigma_rule: Sigma rule 딕셔너리
            pipeline: 사용할 처리 파이프라인 (None이면 자동 선택)
            additional_fields: 추가로 설정할 필드들 (선택사항)
            
        Returns:
            Detection Rule 딕셔너리
        """
        # 파이프라인이 지정되지 않으면 자동 선택
        if pipeline is None:
            pipeline = self._select_appropriate_pipeline(sigma_rule)
        
        # Sigma CLI로 Lucene 쿼리 생성
        lucene_query = self.convert_sigma_rule_to_lucene(sigma_rule, pipeline)
        
        # Detection Rule 구조 생성
        detection_rule = self._create_detection_rule_structure(sigma_rule, lucene_query, additional_fields)
        
        return detection_rule
    
    def _create_detection_rule_structure(self, sigma_rule: Dict[str, Any], 
                                       lucene_query: str,
                                       additional_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Detection Rule 구조를 생성합니다.
        
        Args:
            sigma_rule: Sigma rule 딕셔너리
            lucene_query: Lucene 쿼리 문자열
            additional_fields: 추가로 설정할 필드들 (선택사항)
            
        Returns:
            Detection Rule 딕셔너리
        """
        # 기본 정보 추출
        title = sigma_rule.get('title', 'Unknown Rule')
        rule_id = sigma_rule.get('id') or self._generate_rule_id(title)
        description = sigma_rule.get('description', '')
        level = sigma_rule.get('level', 'medium')
        tags = sigma_rule.get('tags', [])
        
        # 위험도 매핑
        risk_score_map = {'low': 21, 'medium': 47, 'high': 73, 'critical': 99}
        risk_score = risk_score_map.get(level.lower(), 47)
        
        # Detection Rule 구조 생성
        detection_rule = {
            "rule_id": rule_id,
            "risk_score": risk_score,
            "description": description,
            "name": title,
            "severity": level,
            "type": "query",
            "language": "lucene",
            "query": lucene_query,  # Sigma CLI가 생성한 Lucene 쿼리 사용
            "filters": self._get_filters(sigma_rule),
            "enabled": True,
            "interval": "5m",
            "from": "now-70m",
            "max_signals": 100,
            "tags": tags,
            "to": "now",
            "references": [],
            "threat": [],
            "version": 1,
            "exceptions_list": [],
            "related_integrations": [],
            "required_fields": [],
            "setup": "",
            "author": [sigma_rule.get('author', "none")],
            "false_positives": sigma_rule.get('falsepositives', []),
            "license": sigma_rule.get('license', 'DRL'),
            "output_index": "",
            "index":["apm-*-transaction*","auditbeat-*","endgame-*","filebeat-*","logs-*","packetbeat-*","traces-apm*","winlogbeat-*","-*elastic-cloud-logs-*"],
            "meta": {
                "kibana_siem_app_url": ""
            },
            "actions":[]
        }
        
        # 추가 필드가 있으면 기존 필드를 덮어쓰거나 새 필드 추가
        if additional_fields:
            detection_rule.update(additional_fields)
        
        return detection_rule
    
    def _generate_rule_id(self, title: str) -> str:
        """제목에서 규칙 ID를 생성합니다."""
        # 특수문자 제거 및 소문자 변환
        rule_id = re.sub(r'[^a-zA-Z0-9_]', '_', title.lower())
        # 연속된 언더스코어 제거
        rule_id = re.sub(r'_+', '_', rule_id)
        # 앞뒤 언더스코어 제거
        rule_id = rule_id.strip('_')
        # 언더스코어를 하이픈으로 변환
        rule_id = rule_id.replace('_', '-')
        return rule_id
    
    def _get_filters(self, sigma_rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Sigma rule에서 필터를 생성합니다."""
        logsource = sigma_rule.get('logsource', {})
        category = logsource.get('category', '')
        
        filters = []
        
        # 카테고리별 기본 필터 추가
        if category == 'process_creation':
            filters.append({
                "query": {
                    "match": {
                        "event.action": {
                            "type": "phrase",
                            "query": "Process Create (rule: ProcessCreate)"
                        }
                    }
                }
            })
        elif category == 'file_event':
            filters.append({
                "query": {
                    "match": {
                        "event.action": {
                            "type": "phrase", 
                            "query": "File Create (rule: FileCreate)"
                        }
                    }
                }
            })
        elif category == 'network_connection':
            filters.append({
                "query": {
                    "match": {
                        "event.action": {
                            "type": "phrase",
                            "query": "Network connection detected (rule: NetworkConnect)"
                        }
                    }
                }
            })
        
        return filters
    
    def _select_appropriate_pipeline(self, sigma_rule: Dict[str, Any]) -> str:
        """
        Sigma rule의 로그소스에 따라 적절한 파이프라인을 선택합니다.
        
        Args:
            sigma_rule: Sigma rule 딕셔너리
            
        Returns:
            선택된 파이프라인 이름
        """
        logsource = sigma_rule.get('logsource', {})
        product = logsource.get('product', '').lower()
        service = logsource.get('service', '').lower()
        category = logsource.get('category', '').lower()
        
        # Windows 이벤트 관련 서비스/카테고리들은 ecs_windows 파이프라인 사용
        windows_services = [
            'sysmon',
            'windefend',
            'taskscheduler'
        ]
        
        windows_categories = [
            'pipe_created',
            'network_connection', 
            'image_load',
            'driver_load',
            'dns_query',
            'create_stream_hash',
            'create_remote_thread'
        ]
        
        # 서비스 체크
        if any(service == s for s in windows_services) or service.startswith('terminalservices'):
            return 'ecs_windows'
        
        # 카테고리 체크
        if any(category == c for c in windows_categories) or category.startswith('file_'):
            return 'ecs_windows'
        
        # PowerShell 관련 카테고리는 sysmon 파이프라인 사용
        if category.startswith('ps_'):
            return 'sysmon'
        
        # WMI 이벤트는 ecs_windows_old 파이프라인 사용
        if category == 'wmi_event':
            return 'ecs_windows_old'
        
        # Kubernetes 이벤트
        if product == 'kubernetes':
            return 'ecs_kubernetes'
        
        # Zeek 네트워크 로그
        if product == 'zeek':
            return 'ecs_zeek_beats'
        
        # 기본적으로 ecs_windows 사용
        return 'ecs_windows'
    
    def convert_file(self, input_file: str, output_file: Optional[str] = None, 
                    pipeline: str = None,
                    additional_fields: Optional[Dict[str, Any]] = None) -> str:
        """
        Sigma rule 파일을 Kibana Detection Rule JSON으로 변환
        
        Args:
            input_file: 입력 Sigma rule 파일 경로
            output_file: 출력 JSON 파일 경로 (선택사항)
            pipeline: 사용할 처리 파이프라인
            additional_fields: 추가로 설정할 필드들 (선택사항)
            
        Returns:
            출력 파일 경로
        """
        # Sigma rule 로드
        sigma_rule = self.load_sigma_rule(input_file)
        
        # Detection Rule로 변환
        detection_rule = self.convert_to_detection_rule(sigma_rule, pipeline, additional_fields)
        
        # 출력 파일명 결정
        if output_file is None:
            input_path = Path(input_file)
            output_file = str(input_path.with_suffix('.detection_rule.json'))
        
        # 출력 디렉토리가 없으면 생성
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # JSON 파일로 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(detection_rule, f, indent=2, ensure_ascii=False)
        
        return output_file


def test_sigma_cli_converter():
    """Sigma CLI 변환기 테스트"""
    print("=== Sigma CLI 전용 변환기 테스트 ===")
    
    try:
        converter = SigmaCLIConverter()
        
        # 테스트용 Sigma rule
        test_rule = {
            "title": "Test Rule",
            "id": "test-123",
            "description": "Test rule for Sigma CLI converter",
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
            "level": "medium"
        }
        
        # 변환 테스트
        detection_rule = converter.convert_to_detection_rule(test_rule)
        print(f"생성된 Detection Rule:")
        print(f"  - 규칙 ID: {detection_rule.get('rule_id')}")
        print(f"  - 규칙명: {detection_rule.get('name')}")
        print(f"  - 쿼리: {detection_rule.get('query')}")
        
        print("✅ Sigma CLI 전용 변환기 테스트 성공")
        
    except Exception as e:
        print(f"❌ Sigma CLI 전용 변환기 테스트 실패: {e}")


if __name__ == "__main__":
    test_sigma_cli_converter() 