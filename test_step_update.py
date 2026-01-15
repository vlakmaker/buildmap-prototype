#!/usr/bin/env python3
"""
Test workflow update with manual step-by-step approach
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from n8n_integration.n8n_client import n8n_client


def test_step_by_step_update():
    print("🔬 Step-by-Step Workflow Update Test")
    print("=" * 50)
    print()

    # Get existing workflow
    existing_result = n8n_client.get_workflow("4q0jF2LCziQHzhpQ")
    existing_workflow = existing_result["workflow"]

    # Create simple Phase 2 workflow
    phase2_simple = {
        "name": "Email Triage - Phase 2: Rule-Based Classification",
        "nodes": [
            {
                "name": "IF Newsletter",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [650, 300],
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

    print("1️⃣ **Testing direct update with Phase 2 workflow (no merge):**")
    result1 = n8n_client.update_workflow("4q0jF2LCziQHzhpQ", phase2_simple)
    print(f"   Success: {result1.get('success')}")
    if not result1.get("success"):
        print(f"   Error: {result1.get('error')}")
        print(f"   Details: {result1.get('details')}")

    print()
    print("2️⃣ **Testing with description field removed:**")
    phase2_no_desc = phase2_simple.copy()
    if "description" in phase2_no_desc:
        del phase2_no_desc["description"]

    result2 = n8n_client.update_workflow("4q0jF2LCziQHzhpQ", phase2_no_desc)
    print(f"   Success: {result2.get('success')}")
    if not result2.get("success"):
        print(f"   Error: {result2.get('error')}")
        print(f"   Details: {result2.get('details')}")

    print()
    print("3️⃣ **Testing with minimal settings:**")
    phase2_minimal = phase2_simple.copy()
    phase2_minimal["settings"] = {}

    result3 = n8n_client.update_workflow("4q0jF2LCziQHzhpQ", phase2_minimal)
    print(f"   Success: {result3.get('success')}")
    if not result3.get("success"):
        print(f"   Error: {result3.get('error')}")
        print(f"   Details: {result3.get('details')}")

    print()
    print("4️⃣ **Testing merge then clean manually:**")
    merged_workflow = n8n_client.merge_workflows(existing_workflow, phase2_simple)

    # Manually create a clean version
    clean_merged = {
        "name": merged_workflow.get("name"),
        "nodes": merged_workflow.get("nodes", []),
        "connections": merged_workflow.get("connections", {}),
        "settings": merged_workflow.get("settings", {}),
    }

    # Remove all read-only fields manually
    for field in [
        "description",
        "active",
        "tags",
        "createdAt",
        "updatedAt",
        "id",
        "versionId",
    ]:
        clean_merged.pop(field, None)

    # Clean nodes
    for node in clean_merged.get("nodes", []):
        node.pop("id", None)

    result4 = n8n_client.update_workflow("4q0jF2LCziQHzhpQ", clean_merged)
    print(f"   Success: {result4.get('success')}")
    if not result4.get("success"):
        print(f"   Error: {result4.get('error')}")
        print(f"   Details: {result4.get('details')}")

    print()
    print("5️⃣ **Final analysis:**")
    if (
        result1.get("success")
        or result2.get("success")
        or result3.get("success")
        or result4.get("success")
    ):
        print("✅ At least one approach worked!")
    else:
        print("❌ All approaches failed - need deeper investigation")
        print()
        print("🔍 **Comparing structures:**")
        print(f"   Phase 2 keys: {list(phase2_simple.keys())}")
        print(f"   Merged keys: {list(merged_workflow.keys())}")
        print(f"   Clean merged keys: {list(clean_merged.keys())}")


if __name__ == "__main__":
    test_step_by_step_update()
