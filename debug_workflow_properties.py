#!/usr/bin/env python3
"""
Debug what properties are causing the 400 error
"""

import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from n8n_integration.n8n_client import n8n_client


def debug_workflow_properties():
    print("🔍 Debugging Workflow Properties")
    print("=" * 50)
    print()

    # Get the existing workflow that's failing
    existing_result = n8n_client.get_workflow("4q0jF2LCziQHzhpQ")

    if not existing_result["success"]:
        print("❌ Could not get workflow")
        return

    existing_workflow = existing_result["workflow"]

    # Create Phase 2 workflow (same as before)
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
                            }
                        ],
                        "combinator": "or",
                    }
                },
                "name": "IF Newsletter",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [650, 300],
            }
        ],
        "connections": {},
        "settings": {
            "saveExecutionProgress": True,
            "saveManualExecutions": True,
            "saveDataErrorExecution": "all",
            "saveDataSuccessExecution": "all",
            "executionTimeout": 3600,
            "timezone": "UTC",
        },
    }

    # Merge the workflows
    merged_workflow = n8n_client.merge_workflows(existing_workflow, phase2_workflow)

    print("🔍 **Analyzing merged workflow structure:**")
    print(f"   Top-level keys: {list(merged_workflow.keys())}")
    print()

    # Check for read-only fields that shouldn't be sent
    read_only_fields = ["id", "active", "tags", "createdAt", "updatedAt", "versionId"]
    found_read_only = []

    for field in read_only_fields:
        if field in merged_workflow:
            found_read_only.append(field)

    if found_read_only:
        print(f"❌ Found read-only fields that should be removed: {found_read_only}")
    else:
        print("✅ No read-only fields found at top level")

    print()
    print("🔍 **Analyzing node structure:**")
    for i, node in enumerate(merged_workflow.get("nodes", [])):
        node_name = node.get("name", f"Node {i}")
        node_keys = list(node.keys())

        print(f"   Node {i + 1}: {node_name}")
        print(f"     Keys: {node_keys}")

        # Check for read-only fields in nodes
        node_read_only = []
        for field in read_only_fields:
            if field in node:
                node_read_only.append(field)

        if node_read_only:
            print(f"     ❌ Read-only fields in node: {node_read_only}")
        else:
            print(f"     ✅ No read-only fields")

    print()
    print("🔍 **Settings structure:**")
    settings = merged_workflow.get("settings", {})
    print(f"   Settings keys: {list(settings.keys())}")

    # Check for invalid settings
    valid_settings = [
        "saveExecutionProgress",
        "saveManualExecutions",
        "saveDataErrorExecution",
        "saveDataSuccessExecution",
        "executionTimeout",
        "timezone",
        "callerPolicy",
        "callerIds",
        "availableInMCP",
        "errorWorkflow",
    ]

    invalid_settings = []
    for key in settings:
        if key not in valid_settings:
            invalid_settings.append(key)

    if invalid_settings:
        print(f"   ❌ Invalid settings: {invalid_settings}")
    else:
        print(f"   ✅ All settings look valid")

    print()
    print("🔍 **Sample of merged workflow JSON:**")
    # Create a cleaned version for comparison
    cleaned = merged_workflow.copy()

    # Remove potentially problematic fields for debugging
    for field in read_only_fields:
        cleaned.pop(field, None)

    # Show limited sample
    sample = {
        "name": cleaned.get("name"),
        "nodes": len(cleaned.get("nodes", [])),
        "connections": len(cleaned.get("connections", {})),
        "settings": cleaned.get("settings", {}),
    }
    print(json.dumps(sample, indent=2))


if __name__ == "__main__":
    debug_workflow_properties()
