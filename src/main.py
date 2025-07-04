#!/usr/bin/env python3
"""
Sigma CLI to Kibana Detection Rules Converter
Sigma CLI를 사용하여 Sigma rule을 Lucene 쿼리로 변환하고 Kibana Detection Rules로 관리하는 도구
"""

import os
import sys
import json
import click
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv, find_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sigma_cli_manager import SigmaCLIManager
from src.sigma_cli_converter import SigmaCLIConverter
from src.kibana_client import KibanaDetectionClient

# .env 파일 자동 로드
def load_env():
    env_path = find_dotenv()
    if env_path:
        load_dotenv(env_path)
        print(f"[INFO] .env 파일을 로드했습니다: {env_path}")
    else:
        print("[WARN] .env 파일이 존재하지 않습니다. 환경변수 또는 CLI 옵션을 사용하세요.")

load_env()


def get_kibana_client(kibana_url: str = None, username: str = None, password: str = None):
    """Kibana 클라이언트를 생성합니다."""
    kibana_url = kibana_url or os.getenv('KIBANA_URL', 'http://localhost:5601')
    username = username or os.getenv('KIBANA_USERNAME')
    password = password or os.getenv('KIBANA_PASSWORD')
    
    return KibanaDetectionClient(kibana_url, username, password)


def get_sigma_manager(sigma_cli_path: str = None):
    """Sigma CLI 관리자를 생성합니다."""
    if sigma_cli_path is None:
        sigma_cli_path = os.getenv('SIGMA_CLI_PATH', 'sigma')
    return SigmaCLIManager(sigma_cli_path)


def get_sigma_converter(sigma_cli_path: str = None):
    """Sigma CLI 변환기를 생성합니다."""
    if sigma_cli_path is None:
        sigma_cli_path = os.getenv('SIGMA_CLI_PATH', 'sigma')
    return SigmaCLIConverter(sigma_cli_path)


def __get_default_sigma_cli_path():
    """기본 Sigma CLI 경로를 반환합니다."""
    return os.getenv('SIGMA_CLI_PATH', 'sigma')

def __get_default_kibana_url():
    """기본 Kibana URL을 반환합니다."""
    return os.getenv('KIBANA_URL', 'http://localhost:5601')

def __get_default_kibana_username():
    """기본 Kibana 사용자명을 반환합니다."""
    return os.getenv('KIBANA_USERNAME', 'elastic')

def __get_default_kibana_password():
    """기본 Kibana 비밀번호를 반환합니다."""
    return os.getenv('KIBANA_PASSWORD', 'changeme')


def get_sigma_rule_files(input_path: str) -> List[str]:
    """
    입력 경로에서 Sigma rule 파일들을 찾습니다.
    
    Args:
        input_path: 파일 또는 디렉터리 경로
        
    Returns:
        Sigma rule 파일 경로 리스트
    """
    path = Path(input_path)
    
    if path.is_file():
        # 단일 파일인 경우
        if path.suffix.lower() in ['.yml', '.yaml']:
            return [str(path)]
        else:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {path.suffix}")
    
    elif path.is_dir():
        # 디렉터리인 경우 모든 .yml, .yaml 파일 찾기
        yml_files = []
        for file_path in path.rglob('*.yml'):
            yml_files.append(str(file_path))
        for file_path in path.rglob('*.yaml'):
            yml_files.append(str(file_path))
        
        if not yml_files:
            raise ValueError(f"디렉터리에서 Sigma rule 파일을 찾을 수 없습니다: {input_path}")
        
        return sorted(yml_files)
    
    else:
        raise ValueError(f"존재하지 않는 경로입니다: {input_path}")


def validate_sigma_rules(rule_files: List[str], sigma_cli_path: str = None) -> Dict[str, bool]:
    """
    Sigma rule 파일들의 유효성을 검사합니다.
    
    Args:
        rule_files: 검사할 Sigma rule 파일 경로 리스트
        sigma_cli_path: Sigma CLI 경로
        
    Returns:
        파일별 유효성 검사 결과 딕셔너리
    """
    converter = get_sigma_converter(sigma_cli_path)
    results = {}
    
    for rule_file in rule_files:
        try:
            is_valid = converter.validate_sigma_rule(rule_file)
            results[rule_file] = is_valid
            status = "✅ 유효" if is_valid else "❌ 유효하지 않음"
            click.echo(f"{status}: {rule_file}")
        except Exception as e:
            results[rule_file] = False
            click.echo(f"❌ 검사 실패: {rule_file} - {e}")
    
    return results


def convert_sigma_rules(rule_files: List[str], output_dir: str = None, 
                       pipeline: str = "ecs_windows", sigma_cli_path: str = None,
                       additional_fields: Dict[str, Any] = None) -> List[str]:
    """
    Sigma rule 파일들을 Detection Rule로 변환합니다.
    
    Args:
        rule_files: 변환할 Sigma rule 파일 경로 리스트
        output_dir: 출력 디렉터리 (None이면 각 파일과 같은 위치)
        pipeline: Sigma CLI 파이프라인
        sigma_cli_path: Sigma CLI 경로
        additional_fields: 추가 필드
        
    Returns:
        생성된 Detection Rule JSON 파일 경로 리스트
    """
    converter = get_sigma_converter(sigma_cli_path)
    output_files = []
    
    for rule_file in rule_files:
        try:
            if output_dir:
                # 출력 디렉터리가 지정된 경우
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                input_path = Path(rule_file)
                output_file = str(output_path / f"{input_path.stem}.detection_rule.json")
            else:
                # 출력 디렉터리가 지정되지 않은 경우 (기존 동작)
                output_file = None
            
            converted_file = converter.convert_file(
                rule_file, 
                output_file, 
                pipeline, 
                additional_fields
            )
            output_files.append(converted_file)
            click.echo(f"✅ 변환 완료: {rule_file} → {converted_file}")
            
        except Exception as e:
            click.echo(f"❌ 변환 실패: {rule_file} - {e}", err=True)
    
    return output_files


def create_detection_rules_batch(json_files: List[str], kibana_url: str = None, 
                                username: str = None, password: str = None) -> Dict[str, Any]:
    """
    여러 Detection Rule JSON 파일을 일괄로 Kibana에 등록합니다.
    
    Args:
        json_files: 등록할 Detection Rule JSON 파일 경로 리스트
        kibana_url: Kibana 서버 URL
        username: Kibana 사용자명
        password: Kibana 비밀번호
        
    Returns:
        등록 결과 요약
    """
    client = get_kibana_client(kibana_url, username, password)
    results = {
        'total': len(json_files),
        'success': 0,
        'failed': 0,
        'success_files': [],
        'failed_files': []
    }
    
    for json_file in json_files:
        try:
            # JSON 파일 로드
            with open(json_file, 'r', encoding='utf-8') as f:
                detection_rule = json.load(f)
            
            # Detection Rule 생성
            rule_id = client.create_rule(detection_rule)
            results['success'] += 1
            results['success_files'].append(json_file)
            click.echo(f"✅ 등록 완료: {json_file} → Rule ID: {rule_id}")
            
        except Exception as e:
            results['failed'] += 1
            results['failed_files'].append(json_file)
            click.echo(f"❌ 등록 실패: {json_file} - {e}", err=True)
    
    # 결과 요약 출력
    click.echo(f"\n📊 일괄 등록 결과:")
    click.echo(f"   - 총 파일 수: {results['total']}")
    click.echo(f"   - 성공: {results['success']}")
    click.echo(f"   - 실패: {results['failed']}")
    
    if results['failed'] > 0:
        click.echo(f"   - 실패한 파일들:")
        for failed_file in results['failed_files']:
            click.echo(f"     • {failed_file}")
    
    return results


@click.group()
def cli():
    """Sigma CLI를 사용한 Sigma rule to Kibana Detection Rules 변환 및 관리 도구"""
    pass


@cli.command()
@click.option('--sigma-cli-path', default=__get_default_sigma_cli_path, help='Sigma CLI 명령어 경로')
def check_sigma_cli(sigma_cli_path):
    """Sigma CLI 설치 상태를 확인합니다."""
    try:
        manager = get_sigma_manager(sigma_cli_path)
        
        if manager.check_installation():
            version = manager.get_version()
            click.echo(f"✅ Sigma CLI 확인됨: {version}")
            
            # 사용 가능한 대상 조회
            try:
                targets = manager.list_available_targets()
                click.echo("📋 사용 가능한 변환 대상: ")
                for target in targets:
                    click.echo(target)
            except Exception as e:
                click.echo(f"⚠️ 대상 조회 실패: {e}")
            
            # 사용 가능한 파이프라인 조회
            try:
                pipelines = manager.list_available_pipelines()
                click.echo("🔧 사용 가능한 파이프라인: ")
                for pipeline in pipelines:
                    click.echo(pipeline)
            except Exception as e:
                click.echo(f"⚠️ 파이프라인 조회 실패: {e}")
            
            # 설치된 플러그인 조회
            try:
                plugins = manager.list_installed_plugins()
                click.echo("📦 설치된 플러그인: ")
                for plugin in plugins:
                    click.echo(plugin)
            except Exception as e:
                click.echo(f"⚠️ 플러그인 조회 실패: {e}")
                
        else:
            click.echo("❌ Sigma CLI가 설치되지 않았습니다.")
            click.echo(manager.get_installation_guide())
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"확인 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--sigma-cli-path', default=__get_default_sigma_cli_path, help='Sigma CLI 명령어 경로')
@click.option('--required-plugins', help='필요한 플러그인 목록 (쉼표로 구분)')
def setup_sigma_cli(sigma_cli_path, required_plugins):
    """Sigma CLI 환경을 설정합니다."""
    try:
        manager = get_sigma_manager(sigma_cli_path)
        
        # 필요한 플러그인 파싱
        plugins = None
        if required_plugins:
            plugins = [p.strip() for p in required_plugins.split(',')]
        
        success = manager.setup_environment(plugins)
        if success:
            click.echo("✅ Sigma CLI 환경 설정 완료")
        else:
            click.echo("❌ Sigma CLI 환경 설정 실패", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"설정 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='입력 Sigma rule 파일 경로')
@click.option('--pipeline', default='ecs_windows', help='Sigma CLI 파이프라인 (기본값: ecs_windows)')
@click.option('--sigma-cli-path', default=__get_default_sigma_cli_path, help='Sigma CLI 명령어 경로')
def convert_to_lucene(input, pipeline, sigma_cli_path):
    """Sigma rule을 단순히 Lucene 쿼리로 변환합니다."""
    try:
        converter = get_sigma_converter(sigma_cli_path)
        lucene_query = converter.convert_to_lucene(input, pipeline)
        click.echo(f"생성된 Lucene 쿼리:")
        click.echo(lucene_query)
    except Exception as e:
        click.echo(f"변환 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='입력 Sigma rule 파일 또는 디렉터리 경로')
@click.option('--output', '-o', help='출력 JSON 파일 경로 또는 디렉터리 (선택사항)')
@click.option('--pipeline', default='ecs_windows', help='Sigma CLI 파이프라인 (기본값: ecs_windows)')
@click.option('--sigma-cli-path', default=__get_default_sigma_cli_path, help='Sigma CLI 명령어 경로')
@click.option('--additional-fields', help='추가 필드를 JSON 형식으로 설정 (예: \'{"interval": "10m", "max_signals": 200}\')')
def convert_to_detection_rule(input, output, pipeline, sigma_cli_path, additional_fields):
    """Sigma rule을 Kibana Detection Rule로 변환합니다. (파일 또는 디렉터리 지원)"""
    try:
        # 추가 필드 파싱
        parsed_additional_fields = None
        if additional_fields:
            try:
                parsed_additional_fields = json.loads(additional_fields)
                click.echo(f"추가 필드 설정: {parsed_additional_fields}")
            except json.JSONDecodeError as e:
                click.echo(f"❌ 오류: 추가 필드 JSON 파싱 실패: {e}", err=True)
                click.echo("올바른 JSON 형식으로 입력해주세요.")
                click.echo("예시: --additional-fields '{\"interval\": \"10m\", \"max_signals\": 200}'")
                sys.exit(1)
        
        # 입력 경로에서 Sigma rule 파일들 찾기
        try:
            rule_files = get_sigma_rule_files(input)
            click.echo(f"📁 처리할 Sigma rule 파일 {len(rule_files)}개 발견:")
            for rule_file in rule_files:
                click.echo(f"   • {rule_file}")
        except ValueError as e:
            click.echo(f"❌ 오류: {e}", err=True)
            sys.exit(1)
        
        # 변환 실행
        if len(rule_files) == 1:
            # 단일 파일인 경우 (기존 동작 유지)
            converter = get_sigma_converter(sigma_cli_path)
            output_file = converter.convert_file(rule_files[0], output, pipeline, parsed_additional_fields)
            click.echo(f"✅ Kibana Detection Rule 변환 완료: {output_file}")
        else:
            # 여러 파일인 경우 (새로운 기능)
            output_files = convert_sigma_rules(
                rule_files, 
                output,  # output이 디렉터리로 사용됨
                pipeline, 
                sigma_cli_path, 
                parsed_additional_fields
            )
            click.echo(f"✅ 총 {len(output_files)}개 파일 변환 완료")
            
    except Exception as e:
        click.echo(f"변환 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='입력 JSON 파일 경로')
@click.option('--kibana-url', default=__get_default_kibana_url, help='Kibana 서버 URL')
@click.option('--username', default=__get_default_kibana_username, help='Kibana 사용자명')
@click.option('--password', default=__get_default_kibana_password, help='Kibana 비밀번호')
def create_rule(input, kibana_url, username, password):
    """Detection Rule을 Kibana에 생성합니다."""
    try:
        client = get_kibana_client(kibana_url, username, password)
        
        # 연결 테스트
        if not client.test_connection():
            click.echo("Kibana 연결에 실패했습니다.\n환경변수를 확인하거나 CLI 옵션을 사용하세요.\n\n예시:")
            click.echo("python src/main.py create_rule -i examples/suspicious_process_creation.json --kibana-url http://localhost:5601 --username elastic --password changeme")
            sys.exit(1)
        
        # 파일 확장자 확인
        if not input.lower().endswith('.json'):
            click.echo(f"❌ 오류: '{input}' 파일이 JSON 형식이 아닙니다.")
            click.echo("JSON 파일(.json)을 입력해주세요.")
            click.echo("\n예시:")
            click.echo("python src/main.py create_rule -i examples/suspicious_process_creation.json")
            sys.exit(1)
        
        # Detection Rule 로드 및 생성
        try:
            with open(input, 'r', encoding='utf-8') as f:
                import json
                rule_data = json.load(f)
        except json.JSONDecodeError as e:
            click.echo(f"❌ 오류: '{input}' 파일이 유효한 JSON 형식이 아닙니다.")
            click.echo(f"JSON 파싱 오류: {e}")
            click.echo("\n올바른 JSON 형식의 Detection Rule 파일을 입력해주세요.")
            sys.exit(1)
        except FileNotFoundError:
            click.echo(f"❌ 오류: '{input}' 파일을 찾을 수 없습니다.")
            click.echo("파일 경로를 확인해주세요.")
            sys.exit(1)
        
        rule_id = client.create_detection_rule(rule_data)
        if rule_id:
            click.echo(f"Detection Rule 생성 완료: {rule_id}")
        else:
            click.echo("Detection Rule 생성에 실패했습니다.", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"생성 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--rule-id', required=True, help='업데이트할 규칙 ID')
@click.option('--input', '-i', required=True, help='업데이트할 JSON 파일 경로')
@click.option('--kibana-url', default=__get_default_kibana_url, help='Kibana 서버 URL')
@click.option('--username', default=__get_default_kibana_username, help='Kibana 사용자명')
@click.option('--password', default=__get_default_kibana_password, help='Kibana 비밀번호')
def update_rule(rule_id, input, kibana_url, username, password):
    """Detection Rule을 업데이트합니다."""
    try:
        client = get_kibana_client(kibana_url, username, password)
        
        # 연결 테스트
        if not client.test_connection():
            click.echo("Kibana 연결에 실패했습니다.", err=True)
            sys.exit(1)
        
        # Detection Rule 로드 및 업데이트
        with open(input, 'r', encoding='utf-8') as f:
            import json
            rule_data = json.load(f)
        
        success = client.update_rule(rule_id, rule_data)
        if success:
            click.echo(f"Detection Rule 업데이트 완료: {rule_id}")
        else:
            click.echo("Detection Rule 업데이트에 실패했습니다.", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"업데이트 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--rule-id', required=True, help='삭제할 규칙 ID')
@click.option('--kibana-url', default=__get_default_kibana_url, help='Kibana 서버 URL')
@click.option('--username', default=__get_default_kibana_username, help='Kibana 사용자명')
@click.option('--password', default=__get_default_kibana_password, help='Kibana 비밀번호')
def delete_rule(rule_id, kibana_url, username, password):
    """Detection Rule을 삭제합니다."""
    try:
        client = get_kibana_client(kibana_url, username, password)
        
        # 연결 테스트
        if not client.test_connection():
            click.echo("Kibana 연결에 실패했습니다.", err=True)
            sys.exit(1)
        
        # Detection Rule 삭제
        success = client.delete_rule(rule_id)
        if success:
            click.echo(f"Detection Rule 삭제 완료: {rule_id}")
        else:
            click.echo("Detection Rule 삭제에 실패했습니다.", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"삭제 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--kibana-url', default=__get_default_kibana_url, help='Kibana 서버 URL')
@click.option('--username', default=__get_default_kibana_username, help='Kibana 사용자명')
@click.option('--password', default=__get_default_kibana_password, help='Kibana 비밀번호')
@click.option('--page', default=1, help='페이지 번호 (기본값: 1)')
@click.option('--per-page', default=100, help='페이지당 규칙 수 (기본값: 100)')
@click.option('--sort-field', default='created_at', help='정렬 필드 (기본값: created_at)')
@click.option('--sort-order', default='desc', type=click.Choice(['asc', 'desc']), help='정렬 순서 (기본값: desc)')
@click.option('--filter', help='필터 쿼리 (예: alert.attributes.name:windows)')
def list_rules(kibana_url, username, password, page, per_page, sort_field, sort_order, filter):
    """Detection Rules를 조회합니다."""
    try:
        client = get_kibana_client(kibana_url, username, password)
        
        # 연결 테스트
        if not client.test_connection():
            click.echo("Kibana 연결에 실패했습니다.", err=True)
            sys.exit(1)
        
        # Detection Rules 조회
        rules = client.list_detection_rules(
            page=page,
            per_page=per_page,
            sort_field=sort_field,
            sort_order=sort_order,
            filter_query=filter
        )
        
        if not rules:
            click.echo("등록된 Detection Rules가 없습니다.")
            return
        
        click.echo(f"등록된 Detection Rules 목록 ({len(rules)}개):")
        click.echo("-" * 80)
        
        for rule in rules:
            click.echo(f"ID: {rule.get('rule_id', 'N/A')}")
            click.echo(f"이름: {rule.get('name', 'N/A')}")
            click.echo(f"위험도: {rule.get('severity', 'N/A')}")
            click.echo(f"활성화: {rule.get('enabled', 'N/A')}")
            click.echo("-" * 80)
            
    except Exception as e:
        click.echo(f"조회 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--rule-id', required=True, help='조회할 규칙 ID')
@click.option('--kibana-url', default=__get_default_kibana_url, help='Kibana 서버 URL')
@click.option('--username', default=__get_default_kibana_username, help='Kibana 사용자명')
@click.option('--password', default=__get_default_kibana_password, help='Kibana 비밀번호')
def get_rule(rule_id, kibana_url, username, password):
    """특정 Detection Rule을 조회합니다."""
    try:
        client = get_kibana_client(kibana_url, username, password)
        
        # 연결 테스트
        if not client.test_connection():
            click.echo("Kibana 연결에 실패했습니다.", err=True)
            sys.exit(1)
        
        # Detection Rule 조회
        rule = client.get_rule_by_id(rule_id)
        
        if rule:
            click.echo(f"Detection Rule 정보:")
            click.echo(f"ID: {rule.get('rule_id', 'N/A')}")
            click.echo(f"이름: {rule.get('name', 'N/A')}")
            click.echo(f"설명: {rule.get('description', 'N/A')}")
            click.echo(f"위험도: {rule.get('severity', 'N/A')}")
            click.echo(f"활성화: {rule.get('enabled', 'N/A')}")
            click.echo(f"쿼리: {rule.get('query', 'N/A')}")
        else:
            click.echo(f"규칙 ID '{rule_id}'를 찾을 수 없습니다.")
            
    except Exception as e:
        click.echo(f"조회 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='입력 Sigma rule 파일 경로')
@click.option('--kibana-url', default=__get_default_kibana_url, help='Kibana 서버 URL')
@click.option('--username', default=__get_default_kibana_username, help='Kibana 사용자명')
@click.option('--password', default=__get_default_kibana_password, help='Kibana 비밀번호')
@click.option('--pipeline', default='ecs_windows', help='Sigma CLI 파이프라인')
@click.option('--sigma-cli-path', default=__get_default_sigma_cli_path, help='Sigma CLI 명령어 경로')
@click.option('--additional-fields', help='추가 필드를 JSON 형식으로 설정 (예: \'{"interval": "10m", "max_signals": 200}\')')
def convert_and_create(input, kibana_url, username, password, pipeline, sigma_cli_path, additional_fields):
    """Sigma rule을 변환하고 Kibana에 생성합니다. (단일 파일만 지원)"""
    try:
        # 추가 필드 파싱
        parsed_additional_fields = None
        if additional_fields:
            try:
                parsed_additional_fields = json.loads(additional_fields)
                click.echo(f"추가 필드 설정: {parsed_additional_fields}")
            except json.JSONDecodeError as e:
                click.echo(f"❌ 오류: 추가 필드 JSON 파싱 실패: {e}", err=True)
                click.echo("올바른 JSON 형식으로 입력해주세요.")
                click.echo("예시: --additional-fields '{\"interval\": \"10m\", \"max_signals\": 200}'")
                sys.exit(1)
        
        # 단일 파일인지 확인
        rule_files = get_sigma_rule_files(input)
        if len(rule_files) != 1:
            click.echo(f"❌ 오류: convert-and-create 명령어는 단일 파일만 지원합니다.")
            click.echo(f"디렉터리나 여러 파일을 처리하려면 convert-and-create-batch 명령어를 사용하세요.")
            sys.exit(1)
        
        # 변환
        converter = get_sigma_converter(sigma_cli_path)
        output_file = converter.convert_file(rule_files[0], None, pipeline, parsed_additional_fields)
        click.echo(f"Kibana Detection Rule 변환 완료: {output_file}")
        
        # 생성
        client = get_kibana_client(kibana_url, username, password)
        
        # 연결 테스트
        if not client.test_connection():
            click.echo("Kibana 연결에 실패했습니다.", err=True)
            sys.exit(1)
        
        # Detection Rule 생성
        with open(output_file, 'r', encoding='utf-8') as f:
            rule_data = json.load(f)
        
        rule_id = client.create_detection_rule(rule_data)
        if rule_id:
            click.echo(f"Detection Rule 생성 완료: {rule_id}")
        else:
            click.echo("Detection Rule 생성에 실패했습니다.", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"처리 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--sigma-cli-path', default=__get_default_sigma_cli_path, help='Sigma CLI 명령어 경로')
def list_sigma_cli_info(sigma_cli_path):
    """Sigma CLI 정보를 조회합니다."""
    try:
        manager = get_sigma_manager(sigma_cli_path)
        
        click.echo("=== Sigma CLI 정보 ===")
        
        # 사용 가능한 대상 조회
        targets = manager.list_available_targets()
        click.echo(f"📋 사용 가능한 변환 대상: {len(targets)}개")
        for target in targets:
            click.echo(f"   - {target}")
        
        # 사용 가능한 파이프라인 조회
        pipelines = manager.list_available_pipelines()
        click.echo(f"\n🔧 사용 가능한 파이프라인: {len(pipelines)}개")
        for pipeline in pipelines:
            click.echo(f"   - {pipeline}")
        
        click.echo(f"\n💡 사용 예시:")
        click.echo(f"   python src/main.py convert-to-lucene -i examples/suspicious_process_creation.yml")
        click.echo(f"   python src/main.py convert-and-create -i examples/suspicious_process_creation.yml")
        
    except Exception as e:
        click.echo(f"Sigma CLI 정보 조회 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='입력 Sigma rule 파일 또는 디렉터리 경로')
@click.option('--sigma-cli-path', default=__get_default_sigma_cli_path, help='Sigma CLI 명령어 경로')
def validate_rule(input, sigma_cli_path):
    """Sigma rule의 유효성을 검사합니다. (파일 또는 디렉터리 지원)"""
    try:
        # 입력 경로에서 Sigma rule 파일들 찾기
        try:
            rule_files = get_sigma_rule_files(input)
            click.echo(f"📁 검사할 Sigma rule 파일 {len(rule_files)}개 발견:")
            for rule_file in rule_files:
                click.echo(f"   • {rule_file}")
        except ValueError as e:
            click.echo(f"❌ 오류: {e}", err=True)
            sys.exit(1)
        
        # 유효성 검사 실행
        results = validate_sigma_rules(rule_files, sigma_cli_path)
        
        # 결과 요약
        valid_count = sum(1 for is_valid in results.values() if is_valid)
        invalid_count = len(results) - valid_count
        
        click.echo(f"\n📊 유효성 검사 결과:")
        click.echo(f"   - 총 파일 수: {len(results)}")
        click.echo(f"   - 유효한 파일: {valid_count}")
        click.echo(f"   - 유효하지 않은 파일: {invalid_count}")
        
        if invalid_count > 0:
            click.echo(f"\n❌ 유효하지 않은 파일들:")
            for rule_file, is_valid in results.items():
                if not is_valid:
                    click.echo(f"   • {rule_file}")
            sys.exit(1)
        else:
            click.echo(f"\n✅ 모든 파일이 유효합니다!")
            
    except Exception as e:
        click.echo(f"검사 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='입력 Sigma rule 파일 또는 디렉터리 경로')
@click.option('--output', '-o', help='출력 디렉터리 (선택사항)')
@click.option('--pipeline', default='ecs_windows', help='Sigma CLI 파이프라인 (기본값: ecs_windows)')
@click.option('--sigma-cli-path', default=__get_default_sigma_cli_path, help='Sigma CLI 명령어 경로')
@click.option('--additional-fields', help='추가 필드를 JSON 형식으로 설정 (예: \'{"interval": "10m", "max_signals": 200}\')')
@click.option('--kibana-url', default=__get_default_kibana_url, help='Kibana 서버 URL')
@click.option('--username', default=__get_default_kibana_username, help='Kibana 사용자명')
@click.option('--password', default=__get_default_kibana_password, help='Kibana 비밀번호')
def convert_and_create_batch(input, output, pipeline, sigma_cli_path, additional_fields, kibana_url, username, password):
    """Sigma rule을 변환하고 Kibana에 일괄 생성합니다. (파일 또는 디렉터리 지원)"""
    try:
        # 추가 필드 파싱
        parsed_additional_fields = None
        if additional_fields:
            try:
                parsed_additional_fields = json.loads(additional_fields)
                click.echo(f"추가 필드 설정: {parsed_additional_fields}")
            except json.JSONDecodeError as e:
                click.echo(f"❌ 오류: 추가 필드 JSON 파싱 실패: {e}", err=True)
                click.echo("올바른 JSON 형식으로 입력해주세요.")
                click.echo("예시: --additional-fields '{\"interval\": \"10m\", \"max_signals\": 200}'")
                sys.exit(1)
        
        # 입력 경로에서 Sigma rule 파일들 찾기
        try:
            rule_files = get_sigma_rule_files(input)
            click.echo(f"📁 처리할 Sigma rule 파일 {len(rule_files)}개 발견:")
            for rule_file in rule_files:
                click.echo(f"   • {rule_file}")
        except ValueError as e:
            click.echo(f"❌ 오류: {e}", err=True)
            sys.exit(1)
        
        # 1단계: 변환
        click.echo(f"\n🔄 1단계: Sigma rule 변환 중...")
        output_files = convert_sigma_rules(
            rule_files, 
            output, 
            pipeline, 
            sigma_cli_path, 
            parsed_additional_fields
        )
        
        if not output_files:
            click.echo("❌ 변환된 파일이 없습니다.")
            sys.exit(1)
        
        # 2단계: Kibana 연결 테스트
        click.echo(f"\n🔗 2단계: Kibana 연결 테스트 중...")
        client = get_kibana_client(kibana_url, username, password)
        if not client.test_connection():
            click.echo("❌ Kibana 연결에 실패했습니다.", err=True)
            sys.exit(1)
        click.echo("✅ Kibana 연결 성공")
        
        # 3단계: 일괄 등록
        click.echo(f"\n📤 3단계: Detection Rules 일괄 등록 중...")
        results = create_detection_rules_batch(output_files, kibana_url, username, password)
        
        # 최종 결과
        if results['failed'] == 0:
            click.echo(f"\n🎉 모든 Detection Rules가 성공적으로 등록되었습니다!")
        else:
            click.echo(f"\n⚠️ 일부 Detection Rules 등록에 실패했습니다.")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"처리 실패: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='입력 JSON 파일 또는 디렉터리 경로')
@click.option('--kibana-url', default=__get_default_kibana_url, help='Kibana 서버 URL')
@click.option('--username', default=__get_default_kibana_username, help='Kibana 사용자명')
@click.option('--password', default=__get_default_kibana_password, help='Kibana 비밀번호')
def create_rules_batch(input, kibana_url, username, password):
    """여러 Detection Rule JSON 파일을 일괄로 Kibana에 등록합니다."""
    try:
        # 입력 경로에서 JSON 파일들 찾기
        path = Path(input)
        json_files = []
        
        if path.is_file():
            # 단일 파일인 경우
            if path.suffix.lower() == '.json':
                json_files = [str(path)]
            else:
                raise ValueError(f"지원하지 않는 파일 형식입니다: {path.suffix}")
        elif path.is_dir():
            # 디렉터리인 경우 모든 .json 파일 찾기
            for file_path in path.rglob('*.json'):
                json_files.append(str(file_path))
            
            if not json_files:
                raise ValueError(f"디렉터리에서 JSON 파일을 찾을 수 없습니다: {input}")
        else:
            raise ValueError(f"존재하지 않는 경로입니다: {input}")
        
        click.echo(f"📁 등록할 Detection Rule JSON 파일 {len(json_files)}개 발견:")
        for json_file in json_files:
            click.echo(f"   • {json_file}")
        
        # Kibana 연결 테스트
        click.echo(f"\n🔗 Kibana 연결 테스트 중...")
        client = get_kibana_client(kibana_url, username, password)
        if not client.test_connection():
            click.echo("❌ Kibana 연결에 실패했습니다.", err=True)
            sys.exit(1)
        click.echo("✅ Kibana 연결 성공")
        
        # 일괄 등록
        click.echo(f"\n📤 Detection Rules 일괄 등록 중...")
        results = create_detection_rules_batch(json_files, kibana_url, username, password)
        
        # 최종 결과
        if results['failed'] == 0:
            click.echo(f"\n🎉 모든 Detection Rules가 성공적으로 등록되었습니다!")
        else:
            click.echo(f"\n⚠️ 일부 Detection Rules 등록에 실패했습니다.")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"등록 실패: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli() 