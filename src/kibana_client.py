#!/usr/bin/env python3
"""
Kibana Detection Rules Client
Module for integrating with Kibana Detection Rules API
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime


class KibanaDetectionClient:
    """Client for integrating with Kibana Detection Rules API"""
    
    def __init__(self, kibana_url: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Kibana client
        
        Args:
            kibana_url: Kibana server URL (e.g., http://localhost:5601)
            username: Username (optional)
            password: Password (optional)
        """
        self.kibana_url = kibana_url.rstrip('/')
        self.username = username
        self.password = password
        
        # Logging configuration
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Session configuration
        self.session = requests.Session()
        if username and password:
            self.session.auth = (username, password)
        
        # Default headers configuration
        self.session.headers.update({
            'Content-Type': 'application/json',
            'kbn-xsrf': 'true'
        })
    
    def test_connection(self) -> bool:
        """Test Kibana connection."""
        try:
            response = self.session.get(f"{self.kibana_url}/api/status")
            if response.status_code == 200:
                self.logger.info("Kibana connection successful")
                return True
            else:
                self.logger.error(f"Kibana connection failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"Error occurred during Kibana connection test: {e}")
            return False
    
    def create_detection_rule(self, rule_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a Detection Rule.
        
        Args:
            rule_data: Detection Rule data
            
        Returns:
            rule_id of the created rule or None
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            
            response = self.session.post(url, json=rule_data)
            
            if response.status_code == 200:
                result = response.json()
                # Return the rule_id of the created rule
                rule_id = result.get('rule_id')
                self.logger.info(f"Detection Rule creation completed: {rule_id}")
                return rule_id
            else:
                self.logger.error(f"Detection Rule creation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error occurred during Detection Rule creation: {e}")
            return None
    
    def update_detection_rule(self, rule_id: str, rule_data: Dict[str, Any]) -> bool:
        """
        Update a Detection Rule.
        
        Args:
            rule_id: Rule ID
            rule_data: Rule data to update
            
        Returns:
            Update success status
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            
            # Add rule_id to the data
            rule_data['rule_id'] = rule_id
            
            response = self.session.put(url, json=rule_data)
            
            if response.status_code == 200:
                self.logger.info(f"Detection Rule update completed: {rule_id}")
                return True
            else:
                self.logger.error(f"Detection Rule update failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error occurred during Detection Rule update: {e}")
            return False
    
    def get_detection_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a Detection Rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Rule data or None
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            params = {'rule_id': rule_id}
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                return result  # Return rule object directly
            else:
                self.logger.info(f"Detection Rule retrieval failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error occurred during Detection Rule retrieval: {e}")
            return None
    
    def list_detection_rules(self, page: int = 1, per_page: int = 100, 
                           sort_field: str = 'created_at', sort_order: str = 'desc',
                           filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all Detection Rules.
        
        Args:
            page: Page number (default: 1)
            per_page: Number of rules per page (default: 100)
            sort_field: Sort field (default: 'created_at')
            sort_order: Sort order ('asc' or 'desc', default: 'desc')
            filter_query: Filter query (optional, e.g., 'alert.attributes.name:windows')
            
        Returns:
            List of rules
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules/_find"
            
            # Set default parameters
            params = {
                'page': page,
                'per_page': per_page,
                'sort_field': sort_field,
                'sort_order': sort_order
            }
            
            # Add filter query if provided
            if filter_query:
                params['filter'] = filter_query
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"List retrieval response: {result}")
                rules = result.get('data', [])
                self.logger.info(f"Number of retrieved rules: {len(rules)}")
                return rules
            else:
                self.logger.error(f"Detection Rule list retrieval failed: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error occurred during Detection Rule list retrieval: {e}")
            return []
    
    def delete_detection_rule(self, rule_id: str) -> bool:
        """
        Delete a Detection Rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Deletion success status
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            params = {'rule_id': rule_id}
            
            response = self.session.delete(url, params=params)
            
            if response.status_code == 200:
                self.logger.info(f"Detection Rule deletion completed: {rule_id}")
                return True
            else:
                self.logger.error(f"Detection Rule deletion failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error occurred during Detection Rule deletion: {e}")
            return False
    
    def enable_detection_rule(self, rule_id: str) -> bool:
        """
        Enable a Detection Rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Enable success status
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            
            data = {
                "rule_id": rule_id,
                "enabled": True
            }
            
            response = self.session.patch(url, json=data)
            
            if response.status_code == 200:
                self.logger.info(f"Detection Rule enable completed: {rule_id}")
                return True
            else:
                self.logger.error(f"Detection Rule enable failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error occurred during Detection Rule enable: {e}")
            return False
    
    def disable_detection_rule(self, rule_id: str) -> bool:
        """
        Disable a Detection Rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Disable success status
        """
        try:
            url = f"{self.kibana_url}/api/detection_engine/rules"
            
            data = {
                "rule_id": rule_id,
                "enabled": False
            }
            
            response = self.session.patch(url, json=data)
            
            if response.status_code == 200:
                self.logger.info(f"Detection Rule disable completed: {rule_id}")
                return True
            else:
                self.logger.error(f"Detection Rule disable failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error occurred during Detection Rule disable: {e}")
            return False
    
    def find_failed_rules(self) -> List[Dict[str, Any]]:
        """
        Find Detection Rules where execution_summary.last_execution.status is failed.
        
        Returns:
            List of rules in failed status
        """
        try:
            # Get all rules
            all_rules = self.list_detection_rules(per_page=1000)  # Set to a large number
            failed_rules = []
            
            for rule in all_rules:
                # Check execution_summary.last_execution.status field
                execution_summary = rule.get('execution_summary', {})
                if isinstance(execution_summary, dict):
                    last_execution = execution_summary.get('last_execution', {})
                    if isinstance(last_execution, dict):
                        status = last_execution.get('status', '')
                        # Consider failed, partial failure, error as failed status
                        if status in ['failed', 'partial failure', 'error']:
                            failed_rules.append(rule)
            
            self.logger.info(f"Number of rules in failed status: {len(failed_rules)}")
            return failed_rules
            
        except Exception as e:
            self.logger.error(f"Error occurred during failed rules retrieval: {e}")
            return []
    
    def delete_failed_rules(self, rule_ids: List[str]) -> Dict[str, bool]:
        """
        Delete specified rule IDs.
        
        Args:
            rule_ids: List of rule IDs to delete
            
        Returns:
            Dictionary of deletion results per rule
        """
        results = {}
        cnt = 0
        total = len(rule_ids)
        
        for rule_id in rule_ids:
            try:
                success = self.delete_detection_rule(rule_id)
                results[rule_id] = success
                if success:
                    cnt += 1
                    self.logger.info(f"Deleted {cnt}/{total} rules")
            except Exception as e:
                self.logger.error(f"Error occurred during rule deletion: {rule_id} - {e}")
                results[rule_id] = False
        
        return results 
    
    def delete_all_rules(self) -> Dict[str, bool]:
        """
        Delete all Detection Rules.
        
        Returns:
            Dictionary of deletion results per rule
        """
        try:
            # Get all rules
            all_rules = self.list_detection_rules(per_page=1000)  # Set to a large number
            results = {}
            cnt = 0
            total = len(all_rules)
            
            for rule in all_rules:
                try:
                    success = self.delete_detection_rule(rule['rule_id'])
                    if success:
                        cnt += 1
                        self.logger.info(f"Deleted {cnt}/{total} rules")
                    results[rule['rule_id']] = success
                    
                except Exception as e:
                    self.logger.error(f"Error occurred during rule deletion: {rule['rule_id']} - {e}")
                    results[rule['rule_id']] = False
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error occurred during all rules deletion: {e}")
            results[rule['rule_id']] = False
            
        return results  