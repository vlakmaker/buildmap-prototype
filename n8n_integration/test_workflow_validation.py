#!/usr/bin/env python3
"""
Test workflow validation fixes
"""

from n8n_integration.n8n_client import n8n_client
from n8n_integration.workflow_manager import workflow_manager


def test_validation():
    """Test workflow validation with various scenarios"""
    # Initialize session state for testing
    workflow_manager.initialize_session_state()

    print("🧪 Testing Workflow Validation Fixes")
    print("=" * 40)

    # Test 1: Valid workflow
    print("\n1. Testing valid workflow...")
    valid_workflow = {
        "name": "Test Workflow",
        "nodes": [
            {
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "parameters": {},
                "position": [250, 300],
                "id": "manual-trigger",
            }
        ],
        "connections": {},
    }

    is_valid, msg = n8n_client.validate_workflow_json(valid_workflow)
    print(f"   Result: {'✅ Valid' if is_valid else '❌ Invalid'} - {msg}")

    # Test 2: Missing name field
    print("\n2. Testing workflow with missing name...")
    invalid_workflow = {
        "nodes": [
            {
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "parameters": {},
                "position": [250, 300],
                "id": "manual-trigger",
            }
        ],
        "connections": {},
    }

    is_valid, msg = n8n_client.validate_workflow_json(invalid_workflow)
    print(f"   Result: {'✅ Valid' if is_valid else '❌ Invalid'} - {msg}")

    # Test 3: Empty name field
    print("\n3. Testing workflow with empty name...")
    empty_name_workflow = {
        "name": "",
        "nodes": [
            {
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "parameters": {},
                "position": [250, 300],
                "id": "manual-trigger",
            }
        ],
        "connections": {},
    }

    is_valid, msg = n8n_client.validate_workflow_json(empty_name_workflow)
    print(f"   Result: {'✅ Valid' if is_valid else '❌ Invalid'} - {msg}")

    # Test 4: Workflow with active field (should be removed)
    print("\n4. Testing workflow with active field...")
    active_workflow = {
        "name": "Test Workflow",
        "nodes": [
            {
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "parameters": {},
                "position": [250, 300],
                "id": "manual-trigger",
            }
        ],
        "connections": {},
        "active": False,
        "settings": {},
        "tags": ["test"],
    }

    is_valid, msg = n8n_client.validate_workflow_json(active_workflow)
    print(f"   Result: {'✅ Valid' if is_valid else '❌ Invalid'} - {msg}")
    print(f"   Active field removed: {'active' not in active_workflow}")
    print(f"   Settings field added: {'settings' in active_workflow}")
    print(f"   Connections field added: {'connections' in active_workflow}")

    # Test 5: Workflow name extraction from text
    print("\n5. Testing workflow name extraction...")

    # Simulate AI response with workflow JSON
    ai_response = """
    Here's the workflow for Phase 1:
    
    ```json
    {
      "nodes": [
        {
          "name": "Manual Trigger",
          "type": "n8n-nodes-base.manualTrigger",
          "parameters": {},
          "position": [250, 300],
          "id": "manual-trigger"
        }
      ],
      "connections": {}
    }
    ```
    
    This workflow will get email data.
    """

    extracted = workflow_manager.extract_workflow_json_from_text(ai_response)
    if extracted:
        print(f"   Extracted workflow: {bool(extracted)}")
        if "name" not in extracted:
            print(f"   Name field missing: True")
            # Test name extraction
            handled_response = workflow_manager.handle_workflow_creation(
                extracted, ai_response
            )
            print(f"   Name added: {'name' in extracted}")
            print(f"   Final name: {extracted.get('name', 'None')}")
    else:
        print("   No workflow JSON found in response")

    print("\n✅ All validation tests completed!")


if __name__ == "__main__":
    test_validation()
