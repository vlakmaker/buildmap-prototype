#!/usr/bin/env python3
"""
Test the complete workflow update process to identify 400 error
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from n8n_integration.n8n_client import n8n_client


def test_workflow_update_issue():
    print("🔍 Testing Workflow Update Process")
    print("=" * 50)
    print()

    # Test the actual workflow that's failing
    phase2_workflow = {
        "name": "Email Triage - Phase 2: Rule-Based Classification",
        "nodes": [
            {
                "parameters": {
                    "conditions": {
                        "options": {
                            "caseSensitive": False,
                            "leftValue": "",
                            "typeValidation": "strict",
                        },
                        "conditions": [
                            {
                                "id": "condition-1",
                                "leftValue": "={{ $json.payload.parts[0]?.body?.data || '' }}",
                                "rightValue": "noreply",
                                "operator": {"type": "string", "operation": "contains"},
                            },
                            {
                                "id": "condition-2",
                                "leftValue": "={{ $json.payload.parts[0]?.body?.data || '' }}",
                                "rightValue": "unsubscribe",
                                "operator": {"type": "string", "operation": "contains"},
                            },
                        ],
                        "combinator": "or",
                    }
                },
                "name": "IF Newsletter",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [650, 300],
            },
            {
                "parameters": {
                    "resource": "message",
                    "operation": "addLabel",
                    "messageId": "={{ $json.id }}",
                    "labelIds": ["triage-newsletter"],
                },
                "name": "Add Label: Newsletter",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 1,
                "position": [850, 450],
            },
        ],
        "connections": {
            "Gmail Trigger": {
                "main": [[{"node": "IF Newsletter", "type": "main", "index": 0}]]
            },
            "IF Newsletter": {
                "main": [
                    [{"node": "Add Label: Newsletter", "type": "main", "index": 0}]
                ]
            },
        },
        "settings": {
            "saveExecutionProgress": True,
            "saveManualExecutions": True,
            "saveDataErrorExecution": "all",
            "saveDataSuccessExecution": "all",
            "executionTimeout": 3600,
            "timezone": "UTC",
        },
    }

    print("🧪 **Testing validation on Phase 2 workflow:**")
    is_valid, msg = n8n_client.validate_workflow_json(phase2_workflow)
    print(f"   Valid: {is_valid}")
    print(f"   Message: {msg}")
    print()

    # Test getting an existing workflow (simulate the update process)
    if n8n_client.test_connection()["connected"]:
        print("🔗 **Testing actual update process:**")

        # Try to get the workflow we created earlier
        existing_result = n8n_client.get_workflow(
            "4q0jF2LCziQHzhpQ"
        )  # From our earlier test

        if existing_result["success"]:
            print("✅ Retrieved existing workflow")
            existing_workflow = existing_result["workflow"]

            print(
                f"   Existing workflow has {len(existing_workflow.get('nodes', []))} nodes"
            )
            print(f"   New workflow has {len(phase2_workflow.get('nodes', []))} nodes")
            print()

            # Test merge
            print("🔧 **Testing merge:**")
            merged_workflow = n8n_client.merge_workflows(
                existing_workflow, phase2_workflow
            )
            print(
                f"   Merged workflow has {len(merged_workflow.get('nodes', []))} nodes"
            )
            print()

            # Validate merged workflow
            print("🧪 **Validating merged workflow:**")
            merged_valid, merged_msg = n8n_client.validate_workflow_json(
                merged_workflow
            )
            print(f"   Valid: {merged_valid}")
            print(f"   Message: {merged_msg}")

            if not merged_valid:
                print("❌ Merged workflow validation failed!")
                print("   This is likely the cause of 400 error")
            else:
                print("✅ Merged workflow validation passed")
                print("   Trying to update...")

                # Try actual update
                update_result = n8n_client.update_workflow(
                    "4q0jF2LCziQHzhpQ", merged_workflow
                )
                if update_result["success"]:
                    print("✅ Workflow updated successfully!")
                else:
                    print(f"❌ Update failed: {update_result.get('error')}")
                    print(f"   Details: {update_result.get('details')}")
        else:
            print(
                f"❌ Could not retrieve existing workflow: {existing_result.get('error')}"
            )
    else:
        print("❌ Not connected to n8n - can't test actual update")


if __name__ == "__main__":
    test_workflow_update_issue()
