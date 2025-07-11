#!/usr/bin/env python3
# Sigma CLI Manager
# Handles Sigma CLI installation check, initialization, plugin management, etc.

import subprocess
import sys
from typing import List, Optional, Tuple
import os

class SigmaCLIManager:
    """Sigma CLI Manager class"""
    def __init__(self, sigma_cli_path: str = None):
        # Initialize Sigma CLI Manager
        self.sigma_cli_path = sigma_cli_path or ".env SIGMA_CLI_PATH"

    def check_installation(self):
        # Check if Sigma CLI is installed
        try:
            result = subprocess.run([self.sigma_cli_path, 'version'], 
                                    capture_output=True, 
                                    text=True,
                                    check=True
                                    )
            if result.returncode == 0:
                print(f"[OK] Sigma CLI found: {result.stdout.strip()}")
                return True
            else:
                print(f"[ERROR] Sigma CLI not found.")
                return False
        except Exception as e:
            print(f"[ERROR] Error checking Sigma CLI: {e}")
            return False

    def get_version(self):
        # Get Sigma CLI version
        try:
            result = subprocess.run([self.sigma_cli_path, 'version'], 
                                    capture_output=True, 
                                    text=True,
                                    check=True
                                    )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
        except Exception:
            return None

    def list_available_targets(self):
        # List available conversion targets
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "list", "targets"],
                capture_output=True,
                text=True,
                check=True
            )
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"[ERROR] Error listing available targets: {e.stderr}")

    def list_available_pipelines(self):
        # List available pipelines
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "list", "pipelines"],
                capture_output=True,
                text=True,
                check=True
            )
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"[ERROR] Error listing available pipelines: {e.stderr}")

    def list_installed_plugins(self):
        # List installed plugins
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "plugin", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"[ERROR] Error listing installed plugins: {e.stderr}")

    def install_plugin(self, plugin_name: str) -> bool:
        """
        Install a plugin
        
        Args:
            plugin_name: The name of the plugin to install
            
        Returns:
            True if the plugin was installed successfully, False otherwise
        """
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "plugin", "install", plugin_name],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"[OK] Plugin '{plugin_name}' installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install plugin '{plugin_name}': {e.stderr}")
            return False
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """
        Uninstall a plugin
        
        Args:
            plugin_name: The name of the plugin to uninstall
            
        Returns:
            True if the plugin was uninstalled successfully, False otherwise
        """
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "plugin", "uninstall", plugin_name],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"[OK] Plugin '{plugin_name}' uninstalled successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to uninstall plugin '{plugin_name}': {e.stderr}")
            return False
    
    def get_installation_guide(self) -> str:
        """
        Return the installation guide for Sigma CLI
        
        Returns:
            The installation guide as a string
        """
        return """
Sigma CLI installation guide:

1. Install with pip:
   pip install sigma-cli

2. Install with pipx (recommended):
   pipx install sigma-cli

3. Install required plugins:
   sigma plugin install lucene
   sigma plugin install ecs_windows

4. Check installation:
   sigma version
        """
    
    def check_required_plugins(self, required_plugins: List[str]) -> Tuple[bool, List[str]]:
        """
        Check if required plugins are installed
        
        Args:
            required_plugins: The list of required plugins
            
        Returns:
            (True if all plugins are installed, False otherwise, list of missing plugins)
        """
        try:
            installed_plugins = self.list_installed_plugins()
            missing_plugins = [plugin for plugin in required_plugins if plugin not in installed_plugins]
            return len(missing_plugins) == 0, missing_plugins
        except Exception:
            return False, required_plugins
    
    def setup_environment(self, required_plugins: Optional[List[str]] = None) -> bool:
        """
        Set up Sigma CLI environment
        
        Args:
            required_plugins: The list of required plugins (default: ["lucene", "ecs_windows"])
            
        Returns:
            True if the environment was set up successfully, False otherwise
        """
        if required_plugins is None:
            required_plugins = ["lucene", "ecs_windows", "sysmon", "ecs_windows_old", "ecs_kubernetes", "ecs_zeek_beats"]
        
        # Check if Sigma CLI is installed
        if not self.check_installation():
            print("[ERROR] Sigma CLI is not installed.")
            print(self.get_installation_guide())
            return False
        
        # Check if required plugins are installed and install them if not
        all_installed, missing_plugins = self.check_required_plugins(required_plugins)
        
        if not all_installed:
            print(f"[ERROR] Required plugins are not installed: {missing_plugins}")
            print("Installing plugins...")
            
            for plugin in missing_plugins:
                if not self.install_plugin(plugin):
                    print(f"[ERROR] Failed to install plugin '{plugin}'")
                    return False
        
        print("[OK] Sigma CLI environment setup complete")
        return True