"""
Test script for n8n API integration
"""

import os

import requests
from dotenv import load_dotenv

from n8n_integration.n8n_client import N8NClient, n8n_client
from n8n_integration.workflow_manager import WorkflowManager, workflow_manager

# Load environment variables
load_dotenv()


def test_n8n_client():
    """Test n8n client functionality"""
    print("🧪 Testing n8n Client...")

    # Test connection
    print("\n1. Testing connection...")
    connection = n8n_client.test_connection()
    print(f"   Connected: {connection['connected']}")
    if connection["connected"]:
        print(f"   Base URL: {connection.get('base_url', 'N/A')}")
        print(f"   Message: {connection.get('message', 'N/A')}")
        print(f"   Endpoint: {connection.get('endpoint', 'N/A')}")
    else:
        print(f"   Error: {connection.get('error', 'Unknown')}")

    # Test workflow validation
    print("\n2. Testing workflow validation...")

    valid_workflow = {
        "name": "Test Workflow",
        "nodes": [{"name": "Test Node", "type": "test", "parameters": {}}],
        "connections": {},
    }

    is_valid, msg = n8n_client.validate_workflow_json(valid_workflow)
    print(f"   Valid workflow: {is_valid} - {msg}")

    invalid_workflow = {"name": "Invalid"}
    is_valid, msg = n8n_client.validate_workflow_json(invalid_workflow)
    print(f"   Invalid workflow: {is_valid} - {msg}")

    # Test URL generation
    print("\n3. Testing URL generation...")
    url = n8n_client.get_workflow_url("test-id")
    print(f"   Generated URL: {url}")

    print("\n✅ n8n Client tests completed!")


def test_workflow_manager():
    """Test workflow manager functionality"""
    print("\n🧪 Testing Workflow Manager...")

    # Test JSON extraction
    print("\n1. Testing JSON extraction...")

    text_with_json = """
    Here's the workflow:
    
    ```json
    {
      "name": "Test Workflow",
      "nodes": [{"name": "Node1", "type": "test"}],
      "connections": {}
    }
    ```
    
    Let me know if this works!
    """.replace(
        "```", "` ` `"
    )  # Fix triple backticks in Python string

    extracted = workflow_manager.extract_workflow_json_from_text(text_with_json)
    print(f"   Extracted JSON: {extracted is not None}")
    if extracted:
        print(f"   Workflow name: {extracted['name']}")

    # Test status
    print("\n2. Testing workflow status...")
    status = workflow_manager.get_workflow_status()
    print(f"   Has workflow: {status['has_workflow']}")

    print("\n✅ Workflow Manager tests completed!")


def test_full_integration():
    """Test full integration with sample workflow"""
    print("\n🧪 Testing Full Integration...")

    # Only run if connected to n8n
    connection = n8n_client.test_connection()
    if not connection["connected"]:
        print("   ⚠️  Skipping full integration test - not connected to n8n")
        return

    print("   ✅ Connected to n8n, proceeding with integration test...")

    # Sample workflow JSON
    sample_workflow = {
        "name": "Test Integration Workflow",
        "nodes": [
            {
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "parameters": {},
                "position": [250, 300],
                "id": "manual-trigger",
            },
            {
                "name": "Set Variable",
                "type": "n8n-nodes-base.set",
                "parameters": {
                    "values": {"string": [{"name": "test", "value": "integration"}]}
                },
                "position": [450, 300],
                "id": "set-variable",
            },
        ],
        "connections": {
            "Manual Trigger": {
                "main": [[{"node": "Set Variable", "type": "main", "index": 0}]]
            }
        },
        "active": False,
        "settings": {},
        "tags": ["buildmap", "test"],
    }

    print("\n1. Creating test workflow...")
    result = n8n_client.create_workflow(sample_workflow)

    if result["success"]:
        workflow_id = result["id"]
        print(f"   ✅ Workflow created: {result['name']}")
        print(f"   🔗 URL: {result['url']}")

        # Test getting workflow
        print("\n2. Retrieving workflow...")
        get_result = n8n_client.get_workflow(workflow_id)
        if get_result["success"]:
            print(f"   ✅ Workflow retrieved: {get_result['workflow']['name']}")
        else:
            print(f"   ❌ Failed to retrieve: {get_result['error']}")

        # Test updating workflow (using GET → Modify → PUT pattern)
        print("\n3. Updating workflow...")
        # First, get the existing workflow
        get_result = n8n_client.get_workflow(workflow_id)
        if get_result["success"]:
            existing_workflow = get_result["workflow"]
            # Modify the workflow
            existing_workflow["name"] = "Updated Test Workflow"

            # Update using PUT (full replacement)
            update_result = n8n_client.update_workflow(workflow_id, existing_workflow)
            if update_result["success"]:
                print("   ✅ Workflow updated successfully")
                print(f"   🔗 URL: {update_result['url']}")
            else:
                print(f"   ❌ Failed to update: {update_result['error']}")
                if "details" in update_result:
                    print(f"   Details: {update_result['details']}")
        else:
            print(f"   ❌ Failed to get workflow for update: {get_result['error']}")

        # Cleanup - delete the test workflow
        print("\n4. Cleaning up...")
        try:
            delete_response = requests.delete(
                f"{n8n_client.base_url}/api/v1/workflows/{workflow_id}",
                headers={"X-N8N-API-KEY": n8n_client.api_key},
                timeout=10,
            )
            if delete_response.status_code == 200:
                print("   ✅ Test workflow deleted")
            else:
                print(
                    f"   ⚠️  Could not delete test workflow: {delete_response.status_code}"
                )
        except Exception as e:
            print(f"   ⚠️  Error deleting test workflow: {e}")
    else:
        print(f"   ❌ Failed to create workflow: {result['error']}")

    print("\n✅ Full integration tests completed!")


def main():
    """Run all tests"""
    print("🚀 Starting BuildMap n8n Integration Tests")
    print("=" * 50)

    # Show configuration
    print("📋 Configuration:")
    print(f"   N8N_BASE_URL: {os.environ.get('N8N_BASE_URL', 'Not set')}")
    print(f"   N8N_API_KEY: {'Set' if os.environ.get('N8N_API_KEY') else 'Not set'}")
    print()

    try:
        test_n8n_client()
        test_workflow_manager()
        test_full_integration()

        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
