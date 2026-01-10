"""
BuildMap n8n Client - Handles all communication with n8n API
"""

import os
import requests
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# n8n Configuration
N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "http://localhost:5678")
N8N_API_KEY = os.environ.get("N8N_API_KEY", "")

class N8NClient:
    """Client for interacting with n8n REST API"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """Initialize n8n client with optional custom configuration"""
        self.base_url = (base_url or N8N_BASE_URL).rstrip('/')  # Remove trailing slash
        self.api_key = api_key or N8N_API_KEY
        
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to n8n instance with detailed error reporting"""
        if not self.api_key or not self.base_url:
            return {
                "connected": False,
                "error": "N8N_BASE_URL or N8N_API_KEY not configured",
                "details": f"Base URL: {self.base_url}, API Key: {'set' if self.api_key else 'not set'}"
            }

        try:
            headers = {
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }

            # Test the workflows endpoint first (more reliable across n8n versions)
            workflows_url = f"{self.base_url}/api/v1/workflows"
            response = requests.get(
                workflows_url,
                headers=headers,
                timeout=10,
                verify=True
            )

            if response.status_code == 200:
                return {
                    "connected": True,
                    "base_url": self.base_url,
                    "message": "Successfully connected to n8n REST API",
                    "endpoint": "workflows"
                }
            elif response.status_code == 401:
                return {
                    "connected": False,
                    "error": "Authentication failed",
                    "details": "Check your N8N_API_KEY - it may be invalid or expired",
                    "status_code": 401,
                    "suggestion": "Create a new API key in n8n UI (Settings → API)"
                }
            elif response.status_code == 404:
                return {
                    "connected": False,
                    "error": "API endpoint not found",
                    "details": f"Tried to access {workflows_url} - endpoint may not be exposed",
                    "status_code": 404,
                    "suggestion": "Check if REST API is enabled in n8n configuration"
                }
            else:
                return {
                    "connected": False,
                    "error": f"API error: {response.status_code}",
                    "details": response.text[:200],
                    "status_code": response.status_code,
                    "suggestion": "Check n8n logs for more details"
                }

        except requests.exceptions.SSLError as e:
            return {
                "connected": False,
                "error": "SSL certificate error",
                "details": f"SSL verification failed: {str(e)}",
                "suggestion": "Check SSL certificates or try verify=False for testing"
            }
        except requests.exceptions.Timeout:
            return {
                "connected": False,
                "error": "Connection timeout",
                "details": "Server did not respond within 10 seconds",
                "suggestion": "Check if n8n server is running and accessible"
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "connected": False,
                "error": "Connection error",
                "details": f"Could not connect to server: {str(e)}",
                "suggestion": "Check network connectivity, DNS, and server URL"
            }
        except Exception as e:
            return {
                "connected": False,
                "error": "Unexpected error",
                "details": f"{type(e).__name__}: {str(e)}",
                "suggestion": "Check n8n_client.py implementation"
            }

    def validate_workflow_json(self, workflow_json: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate workflow JSON before sending to n8n"""
        required_fields = ["name", "nodes"]  # connections may be optional

        # Check required fields with more detailed error messages
        for field in required_fields:
            if field not in workflow_json:
                return False, f"Missing required field: '{field}'. Workflow JSON must contain: {required_fields}"
            if field == "name" and (not workflow_json["name"] or not str(workflow_json["name"]).strip()):
                return False, "Workflow name is empty or invalid. Please provide a valid workflow name."

        if not workflow_json["nodes"] or len(workflow_json["nodes"]) == 0:
            return False, "Workflow must have at least one node. Current nodes: {workflow_json.get('nodes', [])}"

        # Check node structure
        for node in workflow_json["nodes"]:
            if "name" not in node or "type" not in node:
                return False, f"Node missing required fields (name/type): {node}"

        # Remove read-only fields that cause issues in some n8n versions
        # These fields cannot be set when creating/updating workflows via API
        read_only_fields = ["active", "tags", "version", "createdAt", "updatedAt", "id", "versionId"]
        for field in read_only_fields:
            if field in workflow_json:
                del workflow_json[field]

        # Ensure settings field exists (required by some n8n versions)
        if 'settings' not in workflow_json:
            workflow_json['settings'] = {}

        # Ensure connections field exists
        if 'connections' not in workflow_json:
            workflow_json['connections'] = {}

        return True, "Valid workflow"

    def create_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow in n8n with enhanced error handling"""
        # Validate connection
        connection_test = self.test_connection()
        if not connection_test["connected"]:
            return {
                "success": False,
                "error": f"Cannot connect to n8n: {connection_test.get('error', 'Unknown error')}",
                "details": connection_test.get('details', ''),
                "suggestion": connection_test.get('suggestion', 'Check connection settings')
            }

        # Validate workflow JSON
        is_valid, validation_msg = self.validate_workflow_json(workflow_json)
        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid workflow: {validation_msg}",
                "suggestion": "Check workflow JSON structure"
            }

        try:
            headers = {
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }

            workflow_url = f"{self.base_url}/api/v1/workflows"
            response = requests.post(
                workflow_url,
                headers=headers,
                json=workflow_json,
                timeout=15,
                verify=True
            )

            # Handle various response scenarios
            if response.status_code == 200:
                workflow = response.json()
                return {
                    "success": True,
                    "id": workflow["id"],
                    "name": workflow["name"],
                    "url": self.get_workflow_url(workflow["id"]),
                    "message": "Workflow created successfully"
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "details": "Check N8N_API_KEY - it may be invalid or expired",
                    "status_code": 401,
                    "suggestion": "Create a new API key in n8n UI (Settings → API)"
                }
            elif response.status_code == 403:
                return {
                    "success": False,
                    "error": "Access denied",
                    "details": "API key may not have sufficient permissions",
                    "status_code": 403,
                    "suggestion": "Check API key permissions in n8n"
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "API endpoint not found",
                    "details": f"Endpoint {workflow_url} not found",
                    "status_code": 404,
                    "suggestion": "Check N8N_BASE_URL and API endpoint configuration"
                }
            elif response.status_code == 400:
                return {
                    "success": False,
                    "error": "Bad request",
                    "details": f"Invalid workflow data: {response.text[:200]}",
                    "status_code": 400,
                    "suggestion": "Validate workflow JSON structure"
                }
            else:
                return {
                    "success": False,
                    "error": f"n8n API error {response.status_code}",
                    "details": response.text[:200],
                    "status_code": response.status_code,
                    "suggestion": "Check n8n logs for more details"
                }

        except requests.exceptions.SSLError as e:
            return {
                "success": False,
                "error": "SSL certificate error",
                "details": f"SSL verification failed: {str(e)}",
                "suggestion": "Check SSL certificates or try verify=False for testing"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Connection timeout",
                "details": "Server did not respond within 15 seconds",
                "suggestion": "Check if n8n server is running and accessible"
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "success": False,
                "error": "Connection error",
                "details": f"Could not connect to server: {str(e)}",
                "suggestion": "Check network connectivity and server URL"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "Unexpected error",
                "details": f"{type(e).__name__}: {str(e)}",
                "suggestion": "Check n8n_client.py implementation"
            }

    def update_workflow(self, workflow_id: str, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing workflow in n8n"""
        # Validate connection
        connection_test = self.test_connection()
        if not connection_test["connected"]:
            return {
                "success": False,
                "error": f"Cannot connect to n8n: {connection_test.get('error', 'Unknown error')}"
            }

        # Validate workflow JSON
        is_valid, validation_msg = self.validate_workflow_json(workflow_json)
        if not is_valid:
            return {
                "success": False,
                "error": f"Invalid workflow: {validation_msg}"
            }

        try:
            headers = {
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }

            response = requests.patch(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers=headers,
                json=workflow_json,
                timeout=15
            )

            if response.status_code == 200:
                return {"success": True}
            elif response.status_code == 404:
                return {"success": False, "error": f"Workflow {workflow_id} not found."}
            else:
                return {
                    "success": False,
                    "error": f"Failed to update workflow: {response.text[:200]}"
                }

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}"}

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow details from n8n"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                headers={"X-N8N-API-KEY": self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "workflow": response.json()
                }
            elif response.status_code == 404:
                return {"success": False, "error": "Workflow not found."}
            else:
                return {"success": False, "error": f"API error: {response.text[:200]}"}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}"}

    def get_workflow_url(self, workflow_id: str) -> str:
        """Generate proper URL for workflow"""
        # For workflow URLs, we need the full editor URL, not the API URL
        editor_base_url = self.base_url.replace('/api/v1', '').replace('/rest', '')
        return f"{editor_base_url.rstrip('/')}/workflow/{workflow_id}"

    def merge_workflows(self, existing_workflow: Dict[str, Any], new_phase: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new phase into existing workflow"""
        merged = existing_workflow.copy()
        
        # Merge nodes (avoid duplicates by name)
        existing_node_names = {node.get("name", "") for node in existing_workflow.get("nodes", [])}
        new_nodes = [node for node in new_phase.get("nodes", []) 
                    if node.get("name", "") not in existing_node_names]
        
        merged["nodes"] = existing_workflow.get("nodes", []) + new_nodes
        
        # Merge connections
        merged["connections"] = {**existing_workflow.get("connections", {}), 
                                 **new_phase.get("connections", {})}
        
        return merged

# Singleton client instance
n8n_client = N8NClient()