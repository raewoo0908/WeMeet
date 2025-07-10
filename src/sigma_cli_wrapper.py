#!/usr/bin/env python3
"""
Sigma CLI Wrapper
Wrapper for Sigma CLI to provide an interface for use in our project
"""

import subprocess
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml


class SigmaCLIWrapper:
    """Class that wraps Sigma CLI"""
    
    def __init__(self, sigma_cli_path: str = "sigma"):
        """
        Initialize Sigma CLI wrapper
        
        Args:
            sigma_cli_path: sigma CLI command path (default: "sigma")
        """
        self.sigma_cli_path = sigma_cli_path
        self._check_sigma_cli()
    
    def _check_sigma_cli(self):
        """Check if Sigma CLI is installed"""
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"[OK] Sigma CLI verified: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                f"Sigma CLI not found. Installation methods:\n"
                f"pip install sigma-cli\n"
                f"or\n"
                f"pipx install sigma-cli"
            )
    
    def convert_to_lucene(self, sigma_rule_path: str, pipeline: str = "ecs_windows") -> str:
        """
        Convert Sigma rule to Lucene query
        
        Args:
            sigma_rule_path: Sigma rule file path
            pipeline: Processing pipeline to use (default: "ecs_windows")
            
        Returns:
            Converted Lucene query string
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
            raise RuntimeError(f"Sigma CLI conversion failed: {e.stderr}")
    
    def convert_to_elasticsearch(self, sigma_rule_path: str, pipeline: str = "ecs_windows") -> str:
        """
        Convert Sigma rule to Elasticsearch query
        
        Args:
            sigma_rule_path: Sigma rule file path
            pipeline: Processing pipeline to use (default: "ecs_windows")
            
        Returns:
            Converted Elasticsearch query string
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
            raise RuntimeError(f"Sigma CLI conversion failed: {e.stderr}")
    
    def convert_sigma_rule_dict(self, sigma_rule: Dict[str, Any], 
                               target: str = "lucene", 
                               pipeline: str = "ecs_windows") -> str:
        """
        Save Sigma rule dictionary to temporary file and convert
        
        Args:
            sigma_rule: Sigma rule dictionary
            target: Conversion target (lucene, elasticsearch, etc.)
            pipeline: Processing pipeline to use
            
        Returns:
            Converted query string
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
                raise ValueError(f"Unsupported conversion target: {target}")
        finally:
            # Delete temporary file
            os.unlink(temp_file_path)
    
    def list_available_targets(self) -> List[str]:
        """List available conversion targets"""
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "list", "targets"],
                capture_output=True,
                text=True,
                check=True
            )
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to list targets: {e.stderr}")
    
    def list_available_pipelines(self) -> List[str]:
        """List available pipelines"""
        try:
            result = subprocess.run(
                [self.sigma_cli_path, "list", "pipelines"],
                capture_output=True,
                text=True,
                check=True
            )
            return [line.strip() for line in result.stdout.split('\n') if line.strip()]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to list pipelines: {e.stderr}")
    
    def validate_sigma_rule(self, sigma_rule_path: str) -> bool:
        """
        Validate Sigma rule
        
        Args:
            sigma_rule_path: Sigma rule file path
            
        Returns:
            Validation result
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
    """Enhanced Kibana converter using Sigma CLI"""
    
    def __init__(self, sigma_cli_path: str = "sigma"):
        """
        Initialize enhanced Kibana converter
        
        Args:
            sigma_cli_path: sigma CLI command path
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
        Convert Sigma rule to KQL (using Sigma CLI)
        
        Args:
            sigma_rule: Sigma rule dictionary
            pipeline: Processing pipeline to use
            
        Returns:
            Converted KQL query
        """
        try:
            # Create Lucene query using Sigma CLI
            lucene_query = self.sigma_cli.convert_sigma_rule_dict(
                sigma_rule, target="lucene", pipeline=pipeline
            )
            
            # Convert Lucene to KQL (if needed)
            kql_query = self._lucene_to_kql(lucene_query)
            
            return kql_query
            
        except Exception as e:
            print(f"Sigma CLI conversion failed, using fallback converter: {e}")
            # Use fallback converter on failure
            return self._fallback_conversion(sigma_rule)
    
    def _lucene_to_kql(self, lucene_query: str) -> str:
        """
        Convert Lucene query to KQL
        
        Args:
            lucene_query: Lucene query string
            
        Returns:
            KQL query string
        """
        # Lucene and KQL are very similar, so most can be used as-is
        # Implement additional conversion logic if needed
        return lucene_query
    
    def _fallback_conversion(self, sigma_rule: Dict[str, Any]) -> str:
        """Fallback to existing converter"""
        from .kibana_converter import SigmaToKibanaConverter
        converter = SigmaToKibanaConverter()
        return converter.convert_to_kql_query(sigma_rule)
    
    def convert_to_detection_rule(self, sigma_rule: Dict[str, Any], 
                                pipeline: str = "ecs_windows") -> Dict[str, Any]:
        """
        Convert Sigma rule to Kibana Detection Rule
        
        Args:
            sigma_rule: Sigma rule dictionary
            pipeline: Processing pipeline to use
            
        Returns:
            Kibana Detection Rule dictionary
        """
        # Use existing converter (Detection Rule structure is the same)
        from .kibana_converter import SigmaToKibanaConverter
        converter = SigmaToKibanaConverter()
        
        # Create KQL query using Sigma CLI
        kql_query = self.convert_sigma_to_kql(sigma_rule, pipeline)
        
        # Create Detection Rule structure
        detection_rule = converter.convert_to_detection_rule(sigma_rule)
        
        # Update KQL query
        detection_rule['query'] = kql_query
        
        return detection_rule


if __name__ == "__main__":
    test_sigma_cli_integration() 