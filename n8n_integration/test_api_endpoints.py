#!/usr/bin/env python3
"""
Test n8n API endpoints directly
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
N8N_BASE_URL = os.environ.get("N8N_BASE_URL", "https://n8n.bittygpt.com")
N8N_API_KEY = os.environ.get("N8N_API_KEY", "")

def test_endpoint(endpoint_name: str, path: str):
    """Test a specific API endpoint"""
    print(f"\n🧪 Testing {endpoint_name}...")
    # Clean URL to avoid double slashes
    clean_url = f"{N8N_BASE_URL.rstrip('/')}{path}"
    print(f"URL: {clean_url}")
    
    if not N8N_API_KEY:
        print("❌ API key not set")
        return False
    
    try:
        headers = {
            "X-N8N-API-KEY": N8N_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            clean_url,
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Endpoint accessible")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed - check API key")
            return False
        elif response.status_code == 404:
            print("❌ Endpoint not found")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_workflow_creation():
    """Test workflow creation"""
    print(f"\n🧪 Testing workflow creation...")
    
    # Create a minimal valid workflow for your n8n version
    test_workflow = {
        "name": "BuildMap Test Workflow",
        "nodes": [
            {
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "parameters": {},
                "position": [250, 300],
                "id": "manual-trigger"
            }
        ],
        "connections": {},
        "settings": {}  # Required by your n8n version
    }
    
    try:
        headers = {
            "X-N8N-API-KEY": N8N_API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{N8N_BASE_URL.rstrip('/')}/api/v1/workflows",
            headers=headers,
            json=test_workflow,
            timeout=15
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            workflow = response.json()
            print("✅ Workflow creation successful!")
            print(f"Workflow ID: {workflow['id']}")
            
            # Clean up
            delete_response = requests.delete(
                f"{N8N_BASE_URL}/api/v1/workflows/{workflow['id']}",
                headers=headers,
                timeout=10
            )
            
            if delete_response.status_code == 200:
                print("✅ Test workflow cleaned up")
            else:
                print(f"⚠️  Could not delete test workflow: {delete_response.status_code}")
            
            return True
        else:
            print(f"❌ Workflow creation failed: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Run endpoint tests"""
    print("🚀 Testing n8n API Endpoints")
    print("=" * 50)
    print(f"Base URL: {N8N_BASE_URL}")
    print(f"API Key: {'Set' if N8N_API_KEY else 'Not set'}")
    
    # Test endpoints
    endpoints = [
        ("Meta endpoint", "/api/v1/meta"),
        ("Workflows endpoint", "/api/v1/workflows"),
        ("Executions endpoint", "/api/v1/executions"),
        ("Credentials endpoint", "/api/v1/credentials"),
    ]
    
    results = []
    for endpoint_name, path in endpoints:
        result = test_endpoint(endpoint_name, path)
        results.append((endpoint_name, result))
    
    # Test workflow creation
    workflow_result = test_workflow_creation()
    results.append(("Workflow Creation", workflow_result))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for endpoint_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {endpoint_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All endpoints working! Update your configuration:")
        print(f"N8N_BASE_URL={N8N_BASE_URL}")
        print(f"N8N_API_KEY={N8N_API_KEY[:10]}...")
    else:
        print("❌ Some endpoints failed. Check your n8n configuration.")

if __name__ == "__main__":
    main()