#!/usr/bin/env python3
"""
A tool to convert Sigma rules to Lucene queries and manage Kibana Detection Rules using Sigma CLI.
"""

import os
import sys
import json
import click
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv, find_dotenv

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.sigma_cli_manager import SigmaCLIManager
from src.sigma_cli_converter import SigmaCLIConverter
from src.kibana_client import KibanaDetectionClient

# Auto load .env file
def _load_env():
    env_path = find_dotenv()
    if env_path:
        load_dotenv(env_path)
        print(f"[INFO] .env file loaded: {env_path}")
    else:
        print("[WARN] .env file not found. Use environment variables or CLI options.")

_load_env()


def _get_kibana_client(kibana_url: str = None, username: str = None, password: str = None):
    """Create a Kibana client."""
    kibana_url = kibana_url or os.getenv('KIBANA_URL', 'http://localhost:5601')
    username = username or os.getenv('KIBANA_USERNAME')
    password = password or os.getenv('KIBANA_PASSWORD')

    click.echo(f"[INFO] Kibana URL: {kibana_url}")
    
    return KibanaDetectionClient(kibana_url, username, password)


def _get_sigma_manager(sigma_cli_path: str = None):
    """Create a Sigma CLI manager."""
    if sigma_cli_path is None:
        sigma_cli_path = os.getenv('SIGMA_CLI_PATH', 'sigma')
    return SigmaCLIManager(sigma_cli_path)


def _get_sigma_converter(sigma_cli_path: str = None):
    """Create a Sigma CLI converter."""
    if sigma_cli_path is None:
        sigma_cli_path = os.getenv('SIGMA_CLI_PATH', 'sigma')
    return SigmaCLIConverter(sigma_cli_path)


def _get_default_sigma_cli_path():
    """Return the default Sigma CLI path."""
    return os.getenv('SIGMA_CLI_PATH', 'sigma')

def _get_default_kibana_url():
    """Return the default Kibana URL."""
    return os.getenv('KIBANA_URL', 'http://localhost:5601')

def _get_default_kibana_username():
    """Return the default Kibana username."""
    return os.getenv('KIBANA_USERNAME', 'elastic')

def _get_default_kibana_password():
    """Return the default Kibana password."""
    return os.getenv('KIBANA_PASSWORD', 'changeme')


def _get_sigma_rule_files(input_path: str) -> List[str]:
    """
    Find Sigma rule files in the input path.
    
    Args:
        input_path: File or directory path
        
    Returns:
        List of Sigma rule file paths
    """
    path = Path(input_path)
    
    if path.is_file():
        # If it's a single file
        if path.suffix.lower() in ['.yml', '.yaml']:
            return [str(path)]
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    elif path.is_dir():
        # If it's a directory, find all .yml, .yaml files
        yml_files = []
        for file_path in path.rglob('*.yml'):
            yml_files.append(str(file_path))
        for file_path in path.rglob('*.yaml'):
            yml_files.append(str(file_path))
        
        if not yml_files:
            raise ValueError(f"No Sigma rule files found in directory: {input_path}")
        
        return sorted(yml_files)
    
    else:
        raise ValueError(f"Path does not exist: {input_path}")


def _validate_sigma_rules(rule_files: List[str], sigma_cli_path: str = None) -> Dict[str, bool]:
    """
    Validate Sigma rule files.
    
    Args:
        rule_files: List of Sigma rule file paths to validate
        sigma_cli_path: Sigma CLI path
        
    Returns:
        Dictionary of validation results per file
    """
    converter = _get_sigma_converter(sigma_cli_path)
    results = {}
    
    for rule_file in rule_files:
        try:
            is_valid = converter.validate_sigma_rule(rule_file)
            results[rule_file] = is_valid
            status = "[OK] Valid" if is_valid else "[ERROR] Invalid"
            click.echo(f"{status}: {rule_file}")
        except Exception as e:
            results[rule_file] = False
            click.echo(f"[ERROR] Validation failed: {rule_file} - {e}")
    
    return results


def _convert_sigma_rules(rule_files: List[str], output_dir: str = None, 
                       pipeline: str = None, sigma_cli_path: str = None,
                       additional_fields: Dict[str, Any] = None) -> List[str]:
    """
    Convert Sigma rule files to Detection Rules.
    
    Args:
        rule_files: List of Sigma rule file paths to convert
        output_dir: Output directory (if None, same as input file)
        pipeline: Sigma CLI pipeline
        sigma_cli_path: Sigma CLI path
        additional_fields: Additional fields
        
    Returns:
        List of generated Detection Rule JSON file paths
    """
    converter = _get_sigma_converter(sigma_cli_path)
    output_files = []
    
    for rule_file in rule_files:
        try:
            if output_dir:
                # If output directory is specified
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                
                input_path = Path(rule_file)
                output_file = str(output_path / f"{input_path.stem}.detection_rule.json")
            else:
                # If output directory is not specified (legacy behavior)
                output_file = None
            
            converted_file = converter.convert_file(
                rule_file, 
                output_file, 
                pipeline, 
                additional_fields
            )
            output_files.append(converted_file)
            click.echo(f"[OK] Conversion complete: {rule_file} → {converted_file}")
            
        except Exception as e:
            click.echo(f"[ERROR] Conversion failed: {rule_file} - {e}", err=True)
    
    return output_files


def _create_detection_rules_batch(json_files: List[str], kibana_url: str = None, 
                                username: str = None, password: str = None) -> Dict[str, Any]:
    """
    Batch register multiple Detection Rule JSON files to Kibana.
    
    Args:
        json_files: List of Detection Rule JSON file paths to register
        kibana_url: Kibana server URL
        username: Kibana username
        password: Kibana password
        
    Returns:
        Summary of registration results
    """
    client = _get_kibana_client(kibana_url, username, password)
    results = {
        'total': len(json_files),
        'success': 0,
        'failed': 0,
        'success_files': [],
        'failed_files': []
    }
    
    for json_file in json_files:
        try:
            # Load JSON file
            with open(json_file, 'r', encoding='utf-8') as f:
                detection_rule = json.load(f)
            
            # Create Detection Rule
            rule_id = client.create_detection_rule(detection_rule)
            results['success'] += 1
            results['success_files'].append(json_file)
            click.echo(f"[OK] Registration complete: {json_file} → Rule ID: {rule_id}")
            
        except Exception as e:
            results['failed'] += 1
            results['failed_files'].append(json_file)
            click.echo(f"[ERROR] Registration failed: {json_file} - {e}", err=True)
    
    if results['failed'] > 0:
        click.echo(f"   - Failed files:")
        for failed_file in results['failed_files']:
            click.echo(f"     • {failed_file}")

    # Output summary
    click.echo(f"\n[INFO] Batch Registration Results:")
    click.echo(f"   - Total files: {results['total']}")
    click.echo(f"   - Success: {results['success']}")
    click.echo(f"   - Failed: {results['failed']}")
    
    return results


def _convert_and_create_with_structure(input_dir: str, output_base_dir: str = "detection_rules",
                                    pipeline: str = None, sigma_cli_path: str = None,
                                    additional_fields: Dict[str, Any] = None,
                                    kibana_url: str = None, username: str = None, password: str = None) -> Dict[str, Any]:
    """
    Convert Sigma rules while maintaining directory structure and register to Kibana.
    
    Args:
        input_dir: Input Sigma rule directory path
        output_base_dir: Output base directory (default: detection_rules)
        pipeline: Sigma CLI pipeline
        sigma_cli_path: Sigma CLI path
        additional_fields: Additional fields
        kibana_url: Kibana server URL
        username: Kibana username
        password: Kibana password
        
    Returns:
        Summary of conversion and registration results
    """
    converter = _get_sigma_converter(sigma_cli_path)
    client = _get_kibana_client(kibana_url, username, password)
    
    input_path = Path(input_dir)
    output_base_path = Path(output_base_dir)
    
    if not input_path.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")
    
    # Find all Sigma rule files
    sigma_files = []
    for file_path in input_path.rglob('*.yml'):
        sigma_files.append(file_path)
    for file_path in input_path.rglob('*.yaml'):
        sigma_files.append(file_path)
    
    if not sigma_files:
        raise ValueError(f"No Sigma rule files found in input directory: {input_dir}")
    
    click.echo(f"[INFO] Found {len(sigma_files)} Sigma rule files.")
    
    results = {
        'total_files': len(sigma_files),
        'converted_files': [],
        'created_rules': [],
        'failed_conversions': [],
        'failed_creations': []
    }
    
    # Process each file
    for sigma_file in sigma_files:
        try:
            # Calculate relative path
            relative_path = sigma_file.relative_to(input_path)
            
            # Generate output path (maintain directory structure)
            output_dir = output_base_path / relative_path.parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / f"{sigma_file.stem}.detection_rule.json"
            
            click.echo(f"[INFO] Converting: {relative_path}")
            
            # Convert Sigma rule
            converted_file = converter.convert_file(
                str(sigma_file),
                str(output_file),
                pipeline,
                additional_fields
            )
            
            results['converted_files'].append(converted_file)
            click.echo(f"[OK] Conversion complete: {converted_file}")
            
            # Register to Kibana
            try:
                with open(converted_file, 'r', encoding='utf-8') as f:
                    detection_rule = json.load(f)
                
                rule_id = detection_rule.get('rule_id')
                if rule_id:
                    # Check if rule exists
                    existing_rule = client.get_detection_rule(rule_id)
                    if existing_rule is not None:
                        # Update existing rule
                        response = client.update_detection_rule(rule_id, detection_rule)
                        click.echo(f"[OK] Updating rule: {rule_id}")
                    else:
                        # Create new rule
                        response = client.create_detection_rule(detection_rule)
                        click.echo(f"[OK] Creating rule: {rule_id}")
                    
                    results['created_rules'].append({
                        'rule_id': rule_id,
                        'file': converted_file,
                        'status': 'success'
                    })
                else:
                    click.echo(f"[ERROR] rule_id not found: {converted_file}")
                    results['failed_creations'].append({
                        'file': converted_file,
                        'error': 'rule_id not found'
                    })
                    
            except Exception as e:
                click.echo(f"[ERROR] Kibana registration failed: {converted_file} - {e}")
                results['failed_creations'].append({
                    'file': converted_file,
                    'error': str(e)
                })
                
        except Exception as e:
            click.echo(f"[ERROR] Conversion failed: {sigma_file} - {e}")
            results['failed_conversions'].append({
                'file': str(sigma_file),
                'error': str(e)
            })
    
    # Output summary
    click.echo(f"\n Processing Summary:")
    click.echo(f"  - Total files: {results['total_files']}")
    click.echo(f"  - Conversion successful: {len(results['converted_files'])}")
    click.echo(f"  - Conversion failed: {len(results['failed_conversions'])}")
    click.echo(f"  - Kibana registration successful: {len(results['created_rules'])}")
    click.echo(f"  - Kibana registration failed: {len(results['failed_creations'])}")
    
    if results['failed_conversions']:
        click.echo(f"\n[ERROR] Files that failed conversion:")
        for failed in results['failed_conversions']:
            click.echo(f"  - {failed['file']}: {failed['error']}")
    
    if results['failed_creations']:
        click.echo(f"\n[ERROR] Files that failed Kibana registration:")
        for failed in results['failed_creations']:
            click.echo(f"  - {failed['file']}: {failed['error']}")
    
    return results


@click.group()
def cli():
    """A tool to convert Sigma rules to Kibana Detection Rules using Sigma CLI."""
    pass


@cli.command()
@click.option('--sigma-cli-path', default=_get_default_sigma_cli_path, help='Sigma CLI command path')
def check_sigma_cli(sigma_cli_path):
    """Check Sigma CLI installation status."""
    try:
        manager = _get_sigma_manager(sigma_cli_path)
        
        if manager.check_installation():
            version = manager.get_version()
            click.echo(f"[OK] Sigma CLI verified: {version}")
            
            # List available targets
            try:
                targets = manager.list_available_targets()
                click.echo("Available conversion targets: ")
                for target in targets:
                    click.echo(target)
            except Exception as e:
                click.echo(f"[ERROR] Failed to list targets: {e}")
            
            # List available pipelines
            try:
                pipelines = manager.list_available_pipelines()
                click.echo("Available pipelines: ")
                for pipeline in pipelines:
                    click.echo(pipeline)
            except Exception as e:
                click.echo(f"[ERROR] Failed to list pipelines: {e}")
            
            # List installed plugins
            try:
                plugins = manager.list_installed_plugins()
                click.echo("Installed plugins: ")
                for plugin in plugins:
                    click.echo(plugin)
            except Exception as e:
                click.echo(f"[ERROR] Failed to list plugins: {e}")
                
        else:
            click.echo("[ERROR] Sigma CLI is not installed.")
            click.echo(manager.get_installation_guide())
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"[ERROR] Verification failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--sigma-cli-path', default=_get_default_sigma_cli_path, help='Sigma CLI command path')
@click.option('--required-plugins', help='List of required plugins (comma-separated)')
def setup_sigma_cli(sigma_cli_path, required_plugins):
    """Set up Sigma CLI environment."""
    try:
        manager = _get_sigma_manager(sigma_cli_path)
        
        # Parse required plugins
        plugins = None
        if required_plugins:
            plugins = [p.strip() for p in required_plugins.split(',')]
        
        success = manager.setup_environment(plugins)
        if success:
            click.echo("[OK] Sigma CLI environment setup complete")
        else:
            click.echo("[ERROR] Sigma CLI environment setup failed", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Setup failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='Input Sigma rule file path')
@click.option('--pipeline', default=None, help='Sigma CLI pipeline (auto-selected if not specified)')
@click.option('--sigma-cli-path', default=_get_default_sigma_cli_path, help='Sigma CLI command path')
def convert_to_lucene(input, pipeline, sigma_cli_path):
    """Convert Sigma rule to a simple Lucene query."""
    try:
        converter = _get_sigma_converter(sigma_cli_path)
        sigma_rule = converter.load_sigma_rule(input)
        pipeline = converter._select_appropriate_pipeline(sigma_rule)
        lucene_query = converter.convert_to_lucene(input, pipeline)
        click.echo(f"Generated Lucene query:")
        click.echo(lucene_query)
    except Exception as e:
        click.echo(f"[ERROR] Conversion failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='Input Sigma rule file or directory path')
@click.option('--output', '-o', help='Output JSON file path or directory (optional)')
@click.option('--pipeline', default=None, help='Sigma CLI pipeline (auto-selected if not specified)')
@click.option('--sigma-cli-path', default=_get_default_sigma_cli_path, help='Sigma CLI command path')
@click.option('--additional-fields', help='Set additional fields in JSON format (e.g., \'{"interval": "10m", "max_signals": 200}\')')
def convert_to_detection_rule(input, output, pipeline, sigma_cli_path, additional_fields):
    """Convert Sigma rule to Kibana Detection Rule. (Supports file or directory.)"""
    try:
        # Parse additional fields
        parsed_additional_fields = None
        if additional_fields:
            try:
                parsed_additional_fields = json.loads(additional_fields)
                click.echo(f"Additional fields set: {parsed_additional_fields}")
            except json.JSONDecodeError as e:
                click.echo(f"[ERROR] Failed to parse additional fields JSON: {e}", err=True)
                click.echo("Please enter a valid JSON format.")
                click.echo("Example: --additional-fields '{\"interval\": \"10m\", \"max_signals\": 200}'")
                sys.exit(1)
        
        # Find Sigma rule files in input path
        try:
            rule_files = _get_sigma_rule_files(input)
            click.echo(f"Found {len(rule_files)} Sigma rule files to process:")
            for rule_file in rule_files:
                click.echo(f"   • {rule_file}")
        except ValueError as e:
            click.echo(f"[ERROR] {e}", err=True)
            sys.exit(1)
        
        # Execute conversion
        if len(rule_files) == 1:
            # If it's a single file (maintain legacy behavior)
            converter = _get_sigma_converter(sigma_cli_path)
            output_file = converter.convert_file(rule_files[0], output, pipeline, parsed_additional_fields)
            click.echo(f"[OK] Kibana Detection Rule conversion complete: {output_file}")
        else:
            # If it's multiple files (new functionality)
            output_files = _convert_sigma_rules(
                rule_files, 
                output,  # output is used as a directory
                pipeline, 
                sigma_cli_path, 
                parsed_additional_fields
            )
            click.echo(f"[OK] Total {len(output_files)} files converted.")
            
    except Exception as e:
        click.echo(f"[ERROR] Conversion failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='Input JSON file path')
@click.option('--kibana-url', default=_get_default_kibana_url, help='Kibana server URL')
@click.option('--username', default=_get_default_kibana_username, help='Kibana username')
@click.option('--password', default=_get_default_kibana_password, help='Kibana password')
def create_rule(input, kibana_url, username, password):
    """Create a Detection Rule in Kibana."""
    try:
        client = _get_kibana_client(kibana_url, username, password)
        
        # Test connection
        if not client.test_connection():
            click.echo("Failed to connect to Kibana.\nPlease check environment variables or CLI options.\n\nExample:")
            click.echo("python src/main.py create_rule -i examples/suspicious_process_creation.json --kibana-url http://localhost:5601 --username elastic --password changeme")
            sys.exit(1)
        
        # Check file extension
        if not input.lower().endswith('.json'):
            click.echo(f"[ERROR] '{input}' file is not in JSON format.")
            click.echo("Please input a JSON file (.json).")
            click.echo("\nExample:")
            click.echo("python src/main.py create_rule -i examples/suspicious_process_creation.json")
            sys.exit(1)
        
        # Load Detection Rule and create
        try:
            with open(input, 'r', encoding='utf-8') as f:
                import json
                rule_data = json.load(f)
        except json.JSONDecodeError as e:
            click.echo(f"[ERROR] '{input}' file is not a valid JSON format.")
            click.echo(f"JSON parsing error: {e}")
            click.echo("\nPlease input a valid JSON format Detection Rule file.")
            sys.exit(1)
        except FileNotFoundError:
            click.echo(f"[ERROR] '{input}' file not found.")
            click.echo("Please check the file path.")
            sys.exit(1)
        
        rule_id = client.create_detection_rule(rule_data)
        if rule_id:
            click.echo(f"Detection Rule creation complete: {rule_id}")
        else:
            click.echo("Failed to create Detection Rule.", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"[ERROR] Creation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--rule-id', required=True, help='Rule ID to update')
@click.option('--input', '-i', required=True, help='Input JSON file path to update')
@click.option('--kibana-url', default=_get_default_kibana_url, help='Kibana server URL')
@click.option('--username', default=_get_default_kibana_username, help='Kibana username')
@click.option('--password', default=_get_default_kibana_password, help='Kibana password')
def update_rule(rule_id, input, kibana_url, username, password):
    """Update a Detection Rule."""
    try:
        client = _get_kibana_client(kibana_url, username, password)
        
        # Test connection
        if not client.test_connection():
            click.echo("Failed to connect to Kibana.", err=True)
            sys.exit(1)
        
        # Load Detection Rule and update
        with open(input, 'r', encoding='utf-8') as f:
            import json
            rule_data = json.load(f)
        
        success = client.update_detection_rule(rule_id, rule_data)
        if success:
            click.echo(f"Detection Rule update complete: {rule_id}")
        else:
            click.echo("Failed to update Detection Rule.", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"[ERROR] Update failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--rule-id', required=True, help='Rule ID to delete')
@click.option('--kibana-url', default=_get_default_kibana_url, help='Kibana server URL')
@click.option('--username', default=_get_default_kibana_username, help='Kibana username')
@click.option('--password', default=_get_default_kibana_password, help='Kibana password')
def delete_rule(rule_id, kibana_url, username, password):
    """Delete a Detection Rule."""
    try:
        client = _get_kibana_client(kibana_url, username, password)
        
        # Test connection
        if not client.test_connection():
            click.echo("Failed to connect to Kibana.", err=True)
            sys.exit(1)
        
        # Delete Detection Rule
        success = client.delete_detection_rule(rule_id)
        if success:
            click.echo(f"Detection Rule deletion complete: {rule_id}")
        else:
            click.echo("Failed to delete Detection Rule.", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"[ERROR] Deletion failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--kibana-url', default=_get_default_kibana_url, help='Kibana server URL')
@click.option('--username', default=_get_default_kibana_username, help='Kibana username')
@click.option('--password', default=_get_default_kibana_password, help='Kibana password')
@click.option('--page', default=1, help='Page number (default: 1)')
@click.option('--per-page', default=100, help='Number of rules per page (default: 100)')
@click.option('--sort-field', default='created_at', help='Sort field (default: created_at)')
@click.option('--sort-order', default='desc', type=click.Choice(['asc', 'desc']), help='Sort order (default: desc)')
@click.option('--filter', help='Filter query (e.g., alert.attributes.name:windows)')
def list_rules(kibana_url, username, password, page, per_page, sort_field, sort_order, filter):
    """List Detection Rules."""
    try:
        client = _get_kibana_client(kibana_url, username, password)
        
        # Test connection
        if not client.test_connection():
            click.echo("Failed to connect to Kibana.", err=True)
            sys.exit(1)
        
        # List Detection Rules
        rules = client.list_detection_rules(
            page=page,
            per_page=per_page,
            sort_field=sort_field,
            sort_order=sort_order,
            filter_query=filter
        )
        
        if not rules:
            click.echo("No registered Detection Rules found.")
            return
        
        click.echo(f"List of registered Detection Rules ({len(rules)} items):")
        click.echo("-" * 80)
        
        for rule in rules:
            click.echo(f"ID: {rule.get('rule_id', 'N/A')}")
            click.echo(f"Name: {rule.get('name', 'N/A')}")
            click.echo(f"Severity: {rule.get('severity', 'N/A')}")
            click.echo(f"Enabled: {rule.get('enabled', 'N/A')}")
            click.echo("-" * 80)
            
    except Exception as e:
        click.echo(f"[ERROR] Query failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--rule-id', required=True, help='Rule ID to get')
@click.option('--kibana-url', default=_get_default_kibana_url, help='Kibana server URL')
@click.option('--username', default=_get_default_kibana_username, help='Kibana username')
@click.option('--password', default=_get_default_kibana_password, help='Kibana password')
def get_rule(rule_id, kibana_url, username, password):
    """Get a specific Detection Rule."""
    try:
        client = _get_kibana_client(kibana_url, username, password)
        
        # Test connection
        if not client.test_connection():
            click.echo("Failed to connect to Kibana.", err=True)
            sys.exit(1)
        
        # Get Detection Rule
        rule = client.get_detection_rule(rule_id)
        
        if rule:
            click.echo(f"Detection Rule information:")
            click.echo(f"ID: {rule.get('rule_id', 'N/A')}")
            click.echo(f"Name: {rule.get('name', 'N/A')}")
            click.echo(f"Description: {rule.get('description', 'N/A')}")
            click.echo(f"Severity: {rule.get('severity', 'N/A')}")
            click.echo(f"Enabled: {rule.get('enabled', 'N/A')}")
            click.echo(f"Query: {rule.get('query', 'N/A')}")
        else:
            click.echo(f"Rule ID '{rule_id}' not found.")
            
    except Exception as e:
        click.echo(f"[ERROR] Query failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='Input Sigma rule file path')
@click.option('--kibana-url', default=_get_default_kibana_url, help='Kibana server URL')
@click.option('--username', default=_get_default_kibana_username, help='Kibana username')
@click.option('--password', default=_get_default_kibana_password, help='Kibana password')
@click.option('--pipeline', default=None, help='Sigma CLI pipeline (auto-selected if not specified)')
@click.option('--sigma-cli-path', default=_get_default_sigma_cli_path, help='Sigma CLI command path')
@click.option('--additional-fields', help='Set additional fields in JSON format (e.g., \'{"interval": "10m", "max_signals": 200}\')')
def convert_and_create_single(input, kibana_url, username, password, pipeline, sigma_cli_path, additional_fields):
    """Convert Sigma rule and create in Kibana. (Supports single file only.)"""
    try:
        # Parse additional fields
        parsed_additional_fields = None
        if additional_fields:
            try:
                parsed_additional_fields = json.loads(additional_fields)
                click.echo(f"Additional fields set: {parsed_additional_fields}")
            except json.JSONDecodeError as e:
                click.echo(f"[ERROR] Failed to parse additional fields JSON: {e}", err=True)
                click.echo("Please enter a valid JSON format.")
                click.echo("Example: --additional-fields '{\"interval\": \"10m\", \"max_signals\": 200}'")
                sys.exit(1)
        
        # Check if it's a single file
        rule_files = _get_sigma_rule_files(input)
        if len(rule_files) != 1:
            click.echo(f"[ERROR] convert-and-create command only supports single files.")
            click.echo(f"If you want to process directories or multiple files, use the convert-and-create-batch command.")
            sys.exit(1)
        
        # Convert
        converter = _get_sigma_converter(sigma_cli_path)
        output_file = converter.convert_file(rule_files[0], None, pipeline, parsed_additional_fields)
        click.echo(f"Kibana Detection Rule conversion complete: {output_file}")
        
        # Create
        client = _get_kibana_client(kibana_url, username, password)
        
        # Test connection
        if not client.test_connection():
            click.echo("Failed to connect to Kibana.", err=True)
            sys.exit(1)
        
        # Create Detection Rule
        with open(output_file, 'r', encoding='utf-8') as f:
            rule_data = json.load(f)
        
        rule_id = client.create_detection_rule(rule_data)
        if rule_id:
            click.echo(f"Detection Rule creation complete: {rule_id}")
        else:
            click.echo("Failed to create Detection Rule.", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"Processing failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--sigma-cli-path', default=_get_default_sigma_cli_path, help='Sigma CLI command path')
def list_sigma_cli_info(sigma_cli_path):
    """List Sigma CLI information."""
    try:
        manager = _get_sigma_manager(sigma_cli_path)
        
        click.echo("=== Sigma CLI Information ===")
        
        # List available targets
        targets = manager.list_available_targets()
        click.echo(f"Available conversion targets: {len(targets)} items")
        for target in targets:
            click.echo(f"   - {target}")
        
        # List available pipelines
        pipelines = manager.list_available_pipelines()
        click.echo(f"\nAvailable pipelines: {len(pipelines)} items")
        for pipeline in pipelines:
            click.echo(f"   - {pipeline}")
        
        click.echo(f"\nExample usage:")
        click.echo(f"   python src/main.py convert-to-lucene -i examples/suspicious_process_creation.yml")
        click.echo(f"   python src/main.py convert-and-create -i examples/suspicious_process_creation.yml")
        
    except Exception as e:
        click.echo(f"[ERROR] Failed to get Sigma CLI information: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='Input Sigma rule file or directory path')
@click.option('--sigma-cli-path', default=_get_default_sigma_cli_path, help='Sigma CLI command path')
def validate_rule(input, sigma_cli_path):
    """Validate Sigma rule files. (Supports file or directory.)"""
    try:
        # Find Sigma rule files in input path
        try:
            rule_files = _get_sigma_rule_files(input)
            click.echo(f"Found {len(rule_files)} Sigma rule files to validate:")
            for rule_file in rule_files:
                click.echo(f"   • {rule_file}")
        except ValueError as e:
            click.echo(f"[ERROR] {e}", err=True)
            sys.exit(1)
        
        # Execute validation
        results = _validate_sigma_rules(rule_files, sigma_cli_path)
        
        # Output summary
        valid_count = sum(1 for is_valid in results.values() if is_valid)
        invalid_count = len(results) - valid_count
        
        click.echo(f"\nValidation Results:")
        click.echo(f"   - Total files: {len(results)}")
        click.echo(f"   - Valid files: {valid_count}")
        click.echo(f"   - Invalid files: {invalid_count}")
        
        if invalid_count > 0:
            click.echo(f"\n[ERROR] Invalid files:")
            for rule_file, is_valid in results.items():
                if not is_valid:
                    click.echo(f"   • {rule_file}")
            sys.exit(1)
        else:
            click.echo(f"\n[OK] All files are valid!")
            
    except Exception as e:
        click.echo(f"[ERROR] Validation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='Input Sigma rule file or directory path')
@click.option('--output', '-o', help='Output directory (optional)')
@click.option('--pipeline', default=None, help='Sigma CLI pipeline (auto-selected if not specified)')
@click.option('--sigma-cli-path', default=_get_default_sigma_cli_path, help='Sigma CLI command path')
@click.option('--additional-fields', help='Set additional fields in JSON format (e.g., \'{"interval": "10m", "max_signals": 200}\')')
@click.option('--kibana-url', default=_get_default_kibana_url, help='Kibana server URL')
@click.option('--username', default=_get_default_kibana_username, help='Kibana username')
@click.option('--password', default=_get_default_kibana_password, help='Kibana password')
def convert_and_create_batch(input, output, pipeline, sigma_cli_path, additional_fields, kibana_url, username, password):
    """Convert Sigma rules and batch create in Kibana. (Supports file or directory.)"""
    try:
        # Parse additional fields
        parsed_additional_fields = None
        if additional_fields:
            try:
                parsed_additional_fields = json.loads(additional_fields)
                click.echo(f"Additional fields set: {parsed_additional_fields}")
            except json.JSONDecodeError as e:
                click.echo(f"[ERROR] Failed to parse additional fields JSON: {e}", err=True)
                click.echo("Please enter a valid JSON format.")
                click.echo("Example: --additional-fields '{\"interval\": \"10m\", \"max_signals\": 200}'")
                sys.exit(1)
        
        # Find Sigma rule files in input path
        try:
            rule_files = _get_sigma_rule_files(input)
            click.echo(f"Found {len(rule_files)} Sigma rule files to process:")
            for rule_file in rule_files:
                click.echo(f"   • {rule_file}")
        except ValueError as e:
            click.echo(f"[ERROR] {e}", err=True)
            sys.exit(1)

        # Step 1: Test Kibana connection
        click.echo(f"\nStep 2: Testing Kibana connection...")
        client = _get_kibana_client(kibana_url, username, password)
        if not client.test_connection():
            click.echo("[ERROR] Failed to connect to Kibana.", err=True)
            sys.exit(1)
        click.echo("[OK] Kibana connection successful")
        
        # Step 2: Convert
        click.echo(f"\nStep 1: Converting Sigma rules...")
        output_files = _convert_sigma_rules(
            rule_files, 
            output, 
            pipeline, 
            sigma_cli_path, 
            parsed_additional_fields
        )
        
        if not output_files:
            click.echo("No converted files.")
            sys.exit(1)
        
        # Step 3: Batch registration
        click.echo(f"\nStep 3: Batch registering Detection Rules...")
        results = _create_detection_rules_batch(output_files, kibana_url, username, password)
        
        # Final result
        if results['failed'] == 0:
            click.echo(f"\n[OK] All Detection Rules were successfully registered!")
        else:
            click.echo(f"\n[ERROR] Some Detection Rules failed to register.")
            sys.exit(1)

    except Exception as e:
        click.echo(f"[ERROR] Processing failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='Input JSON file or directory path')
@click.option('--kibana-url', default=_get_default_kibana_url, help='Kibana server URL')
@click.option('--username', default=_get_default_kibana_username, help='Kibana username')
@click.option('--password', default=_get_default_kibana_password, help='Kibana password')
def create_rules_batch(input, kibana_url, username, password):
    """Batch register multiple Detection Rule JSON files to Kibana."""
    try:
        # Test Kibana connection
        click.echo(f"\nTesting Kibana connection...")
        client = _get_kibana_client(kibana_url, username, password)
        if not client.test_connection():
            click.echo("[ERROR] Failed to connect to Kibana.", err=True)
            sys.exit(1)
        click.echo("[OK] Kibana connection successful")

        # Find JSON files in input path
        path = Path(input)
        json_files = []
        
        if path.is_file():
            # If it's a single file
            if path.suffix.lower() == '.json':
                json_files = [str(path)]
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
        elif path.is_dir():
            # If it's a directory, find all .json files
            for file_path in path.rglob('*.json'):
                json_files.append(str(file_path))
            
            if not json_files:
                raise ValueError(f"No JSON files found in directory: {input}")
        else:
            raise ValueError(f"Path does not exist: {input}")
        
        click.echo(f"Found {len(json_files)} Detection Rule JSON files to register:")
        # for json_file in json_files:
        #     click.echo(f"   • {json_file}")
        
        # Batch registration
        click.echo(f"\nBatch registering Detection Rules...")
        results = _create_detection_rules_batch(json_files, kibana_url, username, password)
        
        # Final result
        if results['failed'] == 0:
            click.echo(f"\n[OK] All Detection Rules were successfully registered!")
        else:
            click.echo(f"\n[ERROR] Some Detection Rules failed to register.")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"[ERROR] Registration failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--kibana-url', default=_get_default_kibana_url, help='Kibana server URL')
@click.option('--username', default=_get_default_kibana_username, help='Kibana username')
@click.option('--password', default=_get_default_kibana_password, help='Kibana password')
@click.option('--force', is_flag=True, help='Force deletion without confirmation')
def delete_failed_rules(kibana_url, username, password, force):
    """Delete Detection Rules with last_response as failed."""
    try:
        # Test Kibana connection
        click.echo(f"\nTesting Kibana connection...")
        client = _get_kibana_client(kibana_url, username, password)
        if not client.test_connection():
            click.echo("[ERROR] Failed to connect to Kibana.", err=True)
            sys.exit(1)
        click.echo("[OK] Kibana connection successful")

        # Find failed rules
        click.echo(f"\nSearching for Detection Rules with failed status...")
        failed_rules = client.find_failed_rules()
        
        if not failed_rules:
            click.echo("[OK] No Detection Rules with failed status found.")
            return
        
        # Display deletion target rule information
        for i, rule in enumerate(failed_rules, 1):
            rule_id = rule.get('rule_id', 'Unknown')
            name = rule.get('name', 'Unknown')
            click.echo(f"   {i}. {name} (ID: {rule_id})")
        click.echo(f"\nTarget Detection Rules for deletion ({len(failed_rules)} items):")
        
        # User confirmation
        if not force:
            click.echo(f"\nDo you want to delete the {len(failed_rules)} Detection Rules above?")
            if not click.confirm("Continue? (y/N)"):
                click.echo("Deletion cancelled.")
                return
        
        # Execute deletion
        click.echo(f"\nDeleting Detection Rules...")
        rule_ids = [rule.get('rule_id') for rule in failed_rules]
        results = client.delete_failed_rules(rule_ids)
        
        # Summary
        success_count = sum(1 for success in results.values() if success)
        failed_count = len(results) - success_count
        
        click.echo(f"\nDeletion Results:")
        click.echo(f"   - Total targets: {len(results)} items")
        click.echo(f"   - Deleted: {success_count} items")
        click.echo(f"   - Failed: {failed_count} items")
        
        if failed_count > 0:
            click.echo(f"\nFailed to delete rules:")
            for rule_id, success in results.items():
                if not success:
                    click.echo(f"   • {rule_id}")
            sys.exit(1)
        else:
            click.echo(f"\n[OK] All Failed Detection Rules were successfully deleted!")
            
    except Exception as e:
        click.echo(f"[ERROR] Deletion failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--input', '-i', required=True, help='Input Sigma rule directory path')
@click.option('--output', '-o', default='detection_rules', help='Output base directory (default: detection_rules)')
@click.option('--pipeline', default=None, help='Sigma CLI pipeline (auto-selected if not specified)')
@click.option('--sigma-cli-path', default=_get_default_sigma_cli_path, help='Sigma CLI command path')
@click.option('--additional-fields', help='Set additional fields in JSON format (e.g., \'{"interval": "10m", "max_signals": 200}\')')
@click.option('--kibana-url', default=_get_default_kibana_url, help='Kibana server URL')
@click.option('--username', default=_get_default_kibana_username, help='Kibana username')
@click.option('--password', default=_get_default_kibana_password, help='Kibana password')
def convert_and_create_batch_structure(input, output, pipeline, sigma_cli_path, additional_fields, 
                                        kibana_url, username, password):
    """Convert Sigma rules while maintaining directory structure and register to Kibana."""
    try:
        # Parse additional fields
        parsed_additional_fields = None
        if additional_fields:
            try:
                parsed_additional_fields = json.loads(additional_fields)
                click.echo(f"Additional fields set: {parsed_additional_fields}")
            except json.JSONDecodeError as e:
                click.echo(f"[ERROR] Failed to parse additional fields JSON: {e}", err=True)
                click.echo("Please enter a valid JSON format.")
                click.echo("Example: --additional-fields '{\"interval\": \"10m\", \"max_signals\": 200}'")
                sys.exit(1)
        
        # Perform conversion and Kibana registration
        results = _convert_and_create_with_structure(
            input, output, pipeline, sigma_cli_path, 
            parsed_additional_fields, kibana_url, username, password
        )
        
        click.echo(f"\n[OK] Processing complete!")
        
    except Exception as e:
        click.echo(f"[ERROR] Processing failed: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli() 