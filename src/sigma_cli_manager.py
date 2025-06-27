#!/usr/bin/env python3
"""
Sigma CLI 관리자
Sigma CLI 설치 확인, 초기화, 플러그인 관리 등을 담당
"""

import subprocess
import sys
from typing import List, Optional, Tuple
import os

class SigmaCLIManager:
    """Sigma CLI 관리자 클래스"""
    
    def __init__(self, sigma_cli_path: str = os.getenv('SIGMA_CLI_PATH', 'sigma')):
        """
        Sigma CLI 관리자 초기화
        
        Args:
            sigma_cli_path: sigma CLI 명령어 경로 (기본값: ".env에 있는 SIGMA_CLI_PATH")
        """
        self.sigma_cli_path = sigma_cli_path
    
    def check_installation(self) -> bool:
        """
        Sigma CLI가 설치되어 있는지 확인
        
        Returns:
            설치 여부
        """
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ Sigma CLI 확인됨: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ Sigma CLI를 찾을 수 없습니다.")
            return False
    
    def get_version(self) -> Optional[str]:
        """
        Sigma CLI 버전 조회
        
        Returns:
            버전 문자열 또는 None
        """
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "version"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def list_available_targets(self) -> List[str]:
        """
        사용 가능한 변환 대상을 조회
        
        Returns:
            사용 가능한 대상 목록
        """
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
        """
        사용 가능한 파이프라인을 조회
        
        Returns:
            사용 가능한 파이프라인 목록
        """
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
    
    def list_installed_plugins(self) -> List[str]:
        """
        설치된 플러그인 목록 조회
        
        Returns:
            설치된 플러그인 목록
        """
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "plugin", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"플러그인 목록 조회 실패: {e.stderr}")
    
    def install_plugin(self, plugin_name: str) -> bool:
        """
        플러그인 설치
        
        Args:
            plugin_name: 설치할 플러그인 이름
            
        Returns:
            설치 성공 여부
        """
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "plugin", "install", plugin_name],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ 플러그인 '{plugin_name}' 설치 완료")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 플러그인 '{plugin_name}' 설치 실패: {e.stderr}")
            return False
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """
        플러그인 제거
        
        Args:
            plugin_name: 제거할 플러그인 이름
            
        Returns:
            제거 성공 여부
        """
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "plugin", "uninstall", plugin_name],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ 플러그인 '{plugin_name}' 제거 완료")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 플러그인 '{plugin_name}' 제거 실패: {e.stderr}")
            return False
    
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
    
    def get_installation_guide(self) -> str:
        """
        Sigma CLI 설치 가이드 반환
        
        Returns:
            설치 가이드 문자열
        """
        return """
Sigma CLI 설치 가이드:

1. pip로 설치:
   pip install sigma-cli

2. pipx로 설치 (권장):
   pipx install sigma-cli

3. 필요한 플러그인 설치:
   sigma plugin install lucene
   sigma plugin install ecs_windows

4. 설치 확인:
   sigma --version
        """
    
    def check_required_plugins(self, required_plugins: List[str]) -> Tuple[bool, List[str]]:
        """
        필요한 플러그인이 설치되어 있는지 확인
        
        Args:
            required_plugins: 필요한 플러그인 목록
            
        Returns:
            (모든 플러그인 설치 여부, 설치되지 않은 플러그인 목록)
        """
        try:
            installed_plugins = self.list_installed_plugins()
            missing_plugins = [plugin for plugin in required_plugins if plugin not in installed_plugins]
            return len(missing_plugins) == 0, missing_plugins
        except Exception:
            return False, required_plugins
    
    def setup_environment(self, required_plugins: Optional[List[str]] = None) -> bool:
        """
        Sigma CLI 환경 설정
        
        Args:
            required_plugins: 필요한 플러그인 목록 (기본값: ["lucene", "ecs_windows"])
            
        Returns:
            설정 성공 여부
        """
        if required_plugins is None:
            required_plugins = ["lucene", "ecs_windows"]
        
        # Sigma CLI 설치 확인
        if not self.check_installation():
            print("❌ Sigma CLI가 설치되지 않았습니다.")
            print(self.get_installation_guide())
            return False
        
        # 필요한 플러그인 확인 및 설치
        all_installed, missing_plugins = self.check_required_plugins(required_plugins)
        
        if not all_installed:
            print(f"⚠️ 필요한 플러그인이 설치되지 않았습니다: {missing_plugins}")
            print("플러그인을 설치합니다...")
            
            for plugin in missing_plugins:
                if not self.install_plugin(plugin):
                    print(f"❌ 플러그인 '{plugin}' 설치에 실패했습니다.")
                    return False
        
        print("✅ Sigma CLI 환경 설정 완료")
        return True


def test_sigma_cli_manager():
    """Sigma CLI 관리자 테스트"""
    print("=== Sigma CLI 관리자 테스트 ===")
    
    manager = SigmaCLIManager()
    
    # 설치 확인
    if manager.check_installation():
        print(f"✅ Sigma CLI 버전: {manager.get_version()}")
        
        # 사용 가능한 대상 조회
        try:
            targets = manager.list_available_targets()
            print(f"📋 사용 가능한 변환 대상: {targets}")
        except Exception as e:
            print(f"⚠️ 대상 조회 실패: {e}")
        
        # 사용 가능한 파이프라인 조회
        try:
            pipelines = manager.list_available_pipelines()
            print(f"🔧 사용 가능한 파이프라인: {pipelines}")
        except Exception as e:
            print(f"⚠️ 파이프라인 조회 실패: {e}")
        
        # 설치된 플러그인 조회
        try:
            plugins = manager.list_installed_plugins()
            print(f"📦 설치된 플러그인: {plugins}")
        except Exception as e:
            print(f"⚠️ 플러그인 조회 실패: {e}")
        
        # 환경 설정
        manager.setup_environment()
        
    else:
        print("❌ Sigma CLI가 설치되지 않았습니다.")
        print(manager.get_installation_guide())


if __name__ == "__main__":
    test_sigma_cli_manager() 