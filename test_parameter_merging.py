#!/usr/bin/env python3
"""
Test the improved merge_workflows functionality
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from n8n_integration.n8n_client import n8n_client


def test_parameter_merging():
    print("🧪 Testing Parameter Merging Functionality")
    print("=" * 50)
    print()

    # Create Phase 1 workflow (basic Gmail Trigger)
    phase1_workflow = {
        "name": "Email Triage - Phase 1",
        "nodes": [
            {
                "name": "Gmail Trigger",
                "type": "n8n-nodes-base.gmailTrigger",
                "parameters": {"triggerOn": "newEmail", "status": "unread"},
                "position": [100, 100],
            },
            {
                "name": "Gmail Get Message",
                "type": "n8n-nodes-base.gmail",
                "parameters": {"operation": "get", "messageId": "={{ $json.id }}"},
                "position": [300, 100],
            },
        ],
        "connections": {
            "Gmail Trigger": {
                "main": [[{"node": "Gmail Get Message", "type": "main", "index": 0}]]
            }
        },
        "settings": {},
    }

    # Create Phase 2 workflow (updated Gmail Trigger + new IF node)
    phase2_workflow = {
        "name": "Email Triage - Phase 2",
        "nodes": [
            {
                "name": "Gmail Trigger",
                "type": "n8n-nodes-base.gmailTrigger",
                "parameters": {
                    "triggerOn": "newEmail",
                    "status": "unread",
                    "includeLabels": True,  # NEW PARAMETER
                    "filter": "triage",  # NEW PARAMETER
                },
                "position": [100, 100],  # Same position
            },
            {
                "name": "IF Newsletter",
                "type": "n8n-nodes-base.if",
                "parameters": {
                    "conditions": {
                        "options": {"caseSensitive": False},
                        "conditions": [
                            {
                                "id": "cond-1",
                                "leftValue": "={{ $json.body }}",
                                "rightValue": "newsletter",
                                "operator": {"type": "string", "operation": "contains"},
                            }
                        ],
                        "combinator": "or",
                    }
                },
                "position": [500, 100],
            },
        ],
        "connections": {
            "Gmail Get Message": {
                "main": [[{"node": "IF Newsletter", "type": "main", "index": 0}]]
            }
        },
        "settings": {},
    }

    print("🔧 **Testing merge:**")
    print()

    # Test the merge
    merged_workflow = n8n_client.merge_workflows(phase1_workflow, phase2_workflow)

    print(f"📊 **Merged workflow stats:**")
    print(f"   Total nodes: {len(merged_workflow.get('nodes', []))}")
    print(f"   Total connections: {len(merged_workflow.get('connections', {}))}")
    print()

    # Check Gmail Trigger parameters
    gmail_trigger = None
    for node in merged_workflow.get("nodes", []):
        if node.get("name") == "Gmail Trigger":
            gmail_trigger = node
            break

    if gmail_trigger:
        print("✅ **Gmail Trigger parameters after merge:**")
        params = gmail_trigger.get("parameters", {})
        for key, value in params.items():
            print(f"   {key}: {value}")

        # Verify merge worked correctly
        expected_params = {
            "triggerOn": "newEmail",
            "status": "unread",
            "includeLabels": True,  # Should be added
            "filter": "triage",  # Should be added
        }

        all_good = True
        for key, expected_value in expected_params.items():
            actual_value = params.get(key)
            if actual_value != expected_value:
                print(
                    f"❌ Mismatch in {key}: expected {expected_value}, got {actual_value}"
                )
                all_good = False

        if all_good:
            print("✅ All parameters merged correctly!")
        else:
            print("❌ Parameter merging failed")
    else:
        print("❌ Gmail Trigger not found in merged workflow")

    print()
    print("📝 **All nodes in merged workflow:**")
    for i, node in enumerate(merged_workflow.get("nodes", [])):
        print(f"   {i + 1}. {node.get('name')} ({node.get('type')})")

    print()
    print("🔗 **Connections in merged workflow:**")
    for source, conn_data in merged_workflow.get("connections", {}).items():
        print(f"   {source} -> {conn_data}")


if __name__ == "__main__":
    test_parameter_merging()
