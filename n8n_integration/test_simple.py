#!/usr/bin/env python3
"""
Simple n8n API Integration Test
Tests connection, workflow creation, and cleanup
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from n8n_integration.n8n_client import n8n_client
import requests

def main():
    print('🧪 Testing n8n API Integration\n')

    # Test 1: Connection
    print('1. Testing connection...')
    result = n8n_client.test_connection()
    if result['connected']:
        print(f'   ✅ Connected successfully!')
        print(f'   Base URL: {result["base_url"]}')
    else:
        print(f'   ❌ Connection failed: {result["error"]}')
        print(f'   Details: {result.get("details", "N/A")}')
        print(f'   Suggestion: {result.get("suggestion", "N/A")}')
        return False

    # Test 2: Create a test workflow
    print('\n2. Creating test workflow...')
    test_workflow = {
        'name': 'BuildMap API Test',
        'nodes': [
            {
                'name': 'Manual Trigger',
                'type': 'n8n-nodes-base.manualTrigger',
                'parameters': {},
                'position': [250, 300],
                'typeVersion': 1
            }
        ],
        'connections': {},
        'settings': {}
    }

    create_result = n8n_client.create_workflow(test_workflow)
    if create_result['success']:
        print(f'   ✅ Workflow created!')
        print(f'   ID: {create_result["id"]}')
        print(f'   Name: {create_result["name"]}')
        print(f'   URL: {create_result["url"]}')

        # Clean up - delete the test workflow
        print('\n3. Cleaning up test workflow...')
        headers = {'X-N8N-API-KEY': n8n_client.api_key}
        delete_response = requests.delete(
            f'{n8n_client.base_url}/api/v1/workflows/{create_result["id"]}',
            headers=headers,
            timeout=10
        )
        if delete_response.status_code == 200:
            print(f'   ✅ Test workflow cleaned up')
        else:
            print(f'   ⚠️  Could not delete test workflow (ID: {create_result["id"]})')
            print(f'   You may need to delete it manually from n8n UI')
    else:
        print(f'   ❌ Failed: {create_result["error"]}')
        print(f'   Details: {create_result.get("details", "N/A")}')
        print(f'   Suggestion: {create_result.get("suggestion", "N/A")}')
        return False

    print('\n✅ All tests passed! Your n8n API integration is working correctly.')
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
