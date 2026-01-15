#!/usr/bin/env python3
"""
Create a minimal test to isolate the 400 error
"""

import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from n8n_integration.n8n_client import n8n_client


def test_minimal_workflow():
    print("🔬 Testing Minimal Workflow Structure")
    print("=" * 50)
    print()

    # Get the failing merged workflow
    existing_result = n8n_client.get_workflow("4q0jF2LCziQHzhpQ")
    existing_workflow = existing_result["workflow"]

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

    merged_workflow = n8n_client.merge_workflows(existing_workflow, phase2_workflow)

    print("🧹 **After cleaning, what's left:**")

    # Manually clean and check
    n8n_client._clean_workflow_for_api(merged_workflow)

    print(f"   Top-level keys: {list(merged_workflow.keys())}")
    print()

    # Check each node
    for i, node in enumerate(merged_workflow.get("nodes", [])):
        node_name = node.get("name", f"Node {i}")
        node_keys = list(node.keys())
        print(f"   Node {i + 1}: {node_name}")
        print(f"     Keys: {node_keys}")

        # Check parameter structure
        params = node.get("parameters", {})
        if params:
            print(f"     Parameter keys: {list(params.keys())}")

            # Check for problematic nested structures
            for key, value in params.items():
                if isinstance(value, dict):
                    print(f"       {key} (dict): {list(value.keys())}")
                elif isinstance(value, list):
                    print(f"       {key} (list): length {len(value)}")

        print()

    # Try to identify what specific field is causing the issue
    print("🔍 **Trying to identify problematic field:**")

    # Test minimal version first
    minimal_workflow = {
        "name": "Test Workflow",
        "nodes": [
            {
                "name": "Test Node",
                "type": "n8n-nodes-base.noOp",
                "typeVersion": 1,
                "position": [100, 100],
            }
        ],
        "connections": {},
        "settings": {},
    }

    print("   Testing minimal workflow structure...")
    result = n8n_client.create_workflow(minimal_workflow)
    print(f"   Result: {result.get('success', False)}")
    if not result.get("success"):
        print(f"   Error: {result.get('error')}")

    print()
    print("📝 **Actual cleaned workflow to debug:**")
    cleaned = {
        "name": merged_workflow.get("name"),
        "nodes": merged_workflow.get("nodes", []),
        "connections": merged_workflow.get("connections", {}),
        "settings": merged_workflow.get("settings", {}),
    }

    # Show first node details
    if cleaned.get("nodes"):
        first_node = cleaned["nodes"][0]
        print(f"   First node: {first_node.get('name')}")
        print(
            f"   First node params: {json.dumps(first_node.get('parameters', {}), indent=2)}"
        )


if __name__ == "__main__":
    test_minimal_workflow()
