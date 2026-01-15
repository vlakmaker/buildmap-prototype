#!/usr/bin/env python3
"""
Example script to upload the corrected Phase 2 workflow to n8n
"""

import json
from n8n_integration.n8n_client import n8n_client
from n8n_integration.workflow_manager import workflow_manager


def upload_phase2_workflow():
    """Upload the corrected Phase 2 workflow to n8n"""

    # Load the corrected workflow JSON
    with open("phase2_minimal_workflow.json", "r") as f:
        workflow_json = json.load(f)

    print("🚀 Uploading Phase 2 Email Triage Workflow to n8n...")

    # Test connection first
    connection_test = n8n_client.test_connection()
    if not connection_test["connected"]:
        print(f"❌ Connection failed: {connection_test.get('error')}")
        print(f"Details: {connection_test.get('details')}")
        return False

    print("✅ Connected to n8n successfully")

    # Create the workflow
    result = n8n_client.create_workflow(workflow_json)

    if result["success"]:
        print(f"🎉 Workflow created successfully!")
        print(f"   ID: {result['id']}")
        print(f"   Name: {result['name']}")
        print(f"   URL: {result['url']}")
        return True
    else:
        print(f"❌ Failed to create workflow:")
        print(f"   Error: {result.get('error')}")
        print(f"   Details: {result.get('details')}")
        print(f"   Suggestion: {result.get('suggestion')}")
        return False


if __name__ == "__main__":
    upload_phase2_workflow()
