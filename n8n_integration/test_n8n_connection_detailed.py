#!/usr/bin/env python3
"""
Detailed n8n Connection Test Script
Tests various aspects of n8n API connectivity with comprehensive debugging
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configuration
N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "https://n8n.bittygpt.com/rest")
N8N_API_KEY = os.environ.get("N8N_API_KEY", "")

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print header text"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")

def print_success(text: str):
    """Print success text"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning text"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error text"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info text"""
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def test_basic_connectivity():
    """Test basic network connectivity"""
    print_header("1. Testing Basic Connectivity")
    
    try:
        # Test if we can reach the server at all
        response = requests.get(
            N8N_BASE_URL,
            timeout=5,
            allow_redirects=True
        )
        print_success(f"Server reachable: HTTP {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server")
        print_warning(f"Check if {N8N_BASE_URL} is accessible")
        return False
    except requests.exceptions.Timeout:
        print_error("Connection timed out")
        print_warning("Server may be down or network issue")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False

def test_api_endpoint_exists():
    """Test if API endpoint exists"""
    print_header("2. Testing API Endpoint Availability")
    
    api_url = f"{N8N_BASE_URL}/api/v1/meta"
    
    try:
        # Test without auth first to see if endpoint exists
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 401:
            print_success("API endpoint found (requires authentication)")
            return True
        elif response.status_code == 200:
            print_success("API endpoint found (no auth required)")
            return True
        elif response.status_code == 404:
            print_error("API endpoint not found (404)")
            print_warning("Check N8N_ENDPOINT_REST=rest in docker-compose.yml")
            return False
        else:
            print_error(f"Unexpected status: {response.status_code}")
            print_warning(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API endpoint")
        return False
    except Exception as e:
        print_error(f"Error testing endpoint: {e}")
        return False

def test_api_key_authentication():
    """Test API key authentication"""
    print_header("3. Testing API Key Authentication")
    
    if not N8N_API_KEY:
        print_error("N8N_API_KEY not set in .env")
        print_warning("Add N8N_API_KEY=your_api_key to .env file")
        return False
    
    api_url = f"{N8N_BASE_URL}/api/v1/meta"
    
    try:
        headers = {
            "X-N8N-API-KEY": N8N_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            api_url,
            headers=headers,
            timeout=10,
            verify=True
        )
        
        if response.status_code == 200:
            meta = response.json()
            print_success("API key authentication successful!")
            print_info(f"n8n Version: {meta.get('version', 'unknown')}")
            print_info(f"Instance ID: {meta.get('instanceId', 'unknown')}")
            return True
        elif response.status_code == 401:
            print_error("API key authentication failed (401)")
            print_warning("Check if API key is valid and has permissions")
            print_warning("Create new API key in n8n UI: Settings → API")
            return False
        elif response.status_code == 403:
            print_error("API key forbidden (403)")
            print_warning("API key may not have sufficient permissions")
            return False
        else:
            print_error(f"Unexpected response: {response.status_code}")
            print_warning(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.SSLError as e:
        print_error("SSL certificate error")
        print_warning(f"SSL verification failed: {e}")
        print_warning("Try adding verify=False to requests, or fix SSL certificates")
        return False
    except Exception as e:
        print_error(f"Error during authentication: {e}")
        return False

def test_workflow_creation():
    """Test actual workflow creation"""
    print_header("4. Testing Workflow Creation")
    
    # Simple test workflow
    test_workflow = {
        "name": "BuildMap Test Workflow",
        "nodes": [
            {
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "parameters": {},
                "position": [250, 300],
                "id": "manual-trigger"
            },
            {
                "name": "Set Variable",
                "type": "n8n-nodes-base.set",
                "parameters": {
                    "values": {
                        "string": [{"name": "test", "value": "success"}]
                    }
                },
                "position": [450, 300],
                "id": "set-variable"
            }
        ],
        "connections": {
            "Manual Trigger": {
                "main": [[{"node": "Set Variable", "type": "main", "index": 0}]]
            }
        },
        "active": False,
        "settings": {},
        "tags": ["buildmap", "test"]
    }
    
    try:
        headers = {
            "X-N8N-API-KEY": N8N_API_KEY,
            "Content-Type": "application/json"
        }
        
        workflow_url = f"{N8N_BASE_URL}/api/v1/workflows"
        response = requests.post(
            workflow_url,
            headers=headers,
            json=test_workflow,
            timeout=15,
            verify=True
        )
        
        if response.status_code == 200:
            workflow = response.json()
            print_success("Workflow creation successful!")
            print_info(f"Workflow ID: {workflow['id']}")
            print_info(f"Workflow Name: {workflow['name']}")
            print_info(f"Direct URL: {N8N_BASE_URL.replace('/rest', '')}/workflow/{workflow['id']}")
            
            # Clean up - delete the test workflow
            delete_response = requests.delete(
                f"{N8N_BASE_URL}/api/v1/workflows/{workflow['id']}",
                headers=headers,
                timeout=10
            )
            
            if delete_response.status_code == 200:
                print_success("Test workflow cleaned up successfully")
            else:
                print_warning(f"Could not delete test workflow: {delete_response.status_code}")
            
            return True
        else:
            print_error(f"Workflow creation failed: {response.status_code}")
            print_warning(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print_error(f"Error creating workflow: {e}")
        return False

def test_n8n_client_module():
    """Test the n8n_client module directly"""
    print_header("5. Testing n8n_client Module")
    
    try:
        from n8n_integration.n8n_client import n8n_client
        
        # Test connection
        result = n8n_client.test_connection()
        
        if result.get("connected"):
            print_success("n8n_client connection test passed!")
            print_info(f"Version: {result.get('version', 'unknown')}")
            print_info(f"Instance ID: {result.get('instance_id', 'unknown')}")
            return True
        else:
            print_error("n8n_client connection test failed!")
            print_error(f"Error: {result.get('error', 'Unknown')}")
            print_warning(f"Details: {result.get('details', 'None')}")
            print_warning(f"Suggestion: {result.get('suggestion', 'None')}")
            return False
            
    except ImportError as e:
        print_error(f"Cannot import n8n_client: {e}")
        return False
    except Exception as e:
        print_error(f"Error testing n8n_client: {e}")
        return False

def show_configuration():
    """Show current configuration"""
    print_header("📋 Current Configuration")
    
    print(f"{Colors.BOLD}N8N_BASE_URL:{Colors.ENDC} {N8N_BASE_URL}")
    print(f"{Colors.BOLD}N8N_API_KEY:{Colors.ENDC} {'Set' if N8N_API_KEY else 'Not set'}")
    
    if not N8N_API_KEY:
        print_warning("API key not configured - some tests will fail")

def show_troubleshooting_guide():
    """Show troubleshooting guide"""
    print_header("🚧 Troubleshooting Guide")
    
    issues = [
        {
            "symptom": "404 Not Found",
            "cause": "REST API endpoint not exposed",
            "solution": "Add N8N_ENDPOINT_REST=rest to docker-compose.yml"
        },
        {
            "symptom": "401 Unauthorized",
            "cause": "Invalid or missing API key",
            "solution": "Create new API key in n8n UI (Settings → API)"
        },
        {
            "symptom": "403 Forbidden",
            "cause": "API key lacks permissions",
            "solution": "Check API key permissions in n8n"
        },
        {
            "symptom": "SSL Errors",
            "cause": "Certificate verification failed",
            "solution": "Fix SSL certificates or use verify=False for testing"
        },
        {
            "symptom": "Connection Timeout",
            "cause": "Server not reachable",
            "solution": "Check if n8n container is running and accessible"
        }
    ]
    
    for i, issue in enumerate(issues, 1):
        print(f"\n{i}. {Colors.BOLD}{issue['symptom']}{Colors.ENDC}")
        print(f"   Cause: {issue['cause']}")
        print(f"   Solution: {issue['solution']}")

def main():
    """Run all tests"""
    print(f"{Colors.HEADER}")
    print("🚀 BuildMap n8n Connection Test Suite")
    print("=" * 50)
    print(f"{Colors.ENDC}")
    
    # Show configuration
    show_configuration()
    
    # Run tests
    tests = [
        ("Basic Connectivity", test_basic_connectivity),
        ("API Endpoint", test_api_endpoint_exists),
        ("API Authentication", test_api_key_authentication),
        ("Workflow Creation", test_workflow_creation),
        ("n8n_client Module", test_n8n_client_module),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Show summary
    print_header("📊 Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        color = Colors.OKGREEN if result else Colors.FAIL
        print(f"{color}{status}{Colors.ENDC} {test_name}")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print_success("🎉 All tests passed! n8n integration is working correctly.")
    else:
        print_error("❌ Some tests failed. Check the issues above.")
        show_troubleshooting_guide()
    
    print(f"\n{Colors.HEADER}")
    print("📚 Next Steps")
    print(f"{Colors.ENDC}")
    
    if passed == total:
        print_info("1. Update your .env file with the correct configuration")
        print_info("2. Restart BuildMap to apply changes")
        print_info("3. Start building workflows directly in n8n!")
    else:
        print_info("1. Review the failed tests above")
        print_info("2. Check the troubleshooting guide")
        print_info("3. Update your docker-compose.yml if needed")
        print_info("4. Verify your n8n API key")
        print_info("5. Run this test again after making changes")

if __name__ == "__main__":
    main()