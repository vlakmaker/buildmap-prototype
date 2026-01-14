#!/usr/bin/env python3
"""
Quick test to verify tags field is removed by validation
"""

import sys

sys.path.insert(0, "/home/vlakmaker/buildmap-prototype")

from n8n_integration.n8n_client import n8n_client


def test_tags_removal():
    """Test that tags field is removed during validation"""
    print("🧪 Testing Tags Field Removal")
    print("=" * 50)

    # Create workflow with tags field (as the AI was instructed to do)
    workflow_with_tags = {
        "name": "Test Workflow with Tags",
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
        "tags": ["buildmap", "phase-1"],  # This should be removed
    }

    print("\nBefore validation:")
    print(f"  - 'tags' field present: {'tags' in workflow_with_tags}")
    print(f"  - 'active' field present: {'active' in workflow_with_tags}")
    print(f"  - Tags value: {workflow_with_tags.get('tags', 'N/A')}")

    # Run validation
    is_valid, msg = n8n_client.validate_workflow_json(workflow_with_tags)

    print(f"\nValidation result: {'✅ Valid' if is_valid else '❌ Invalid'}")
    print(f"Message: {msg}")

    print("\nAfter validation:")
    print(f"  - 'tags' field present: {'tags' in workflow_with_tags}")
    print(f"  - 'active' field present: {'active' in workflow_with_tags}")
    print(f"  - 'settings' field present: {'settings' in workflow_with_tags}")
    print(f"  - 'connections' field present: {'connections' in workflow_with_tags}")

    # Verify
    if "tags" not in workflow_with_tags and "active" not in workflow_with_tags:
        print("\n✅ SUCCESS: Read-only fields removed correctly!")
        return True
    else:
        print("\n❌ FAILURE: Read-only fields still present!")
        return False


if __name__ == "__main__":
    success = test_tags_removal()
    sys.exit(0 if success else 1)
