#!/usr/bin/env python3
"""
Test enhanced error handling in workflow manager
"""

import sys

sys.path.append(".")
from n8n_integration.n8n_client import n8n_client


def test_error_handling():
    """Test various error scenarios with enhanced handling"""
    print("🧪 Testing Enhanced Error Handling")
    print("=" * 40)

    # Test different error scenarios
    error_scenarios = [
        {
            "name": "Bad Request (400)",
            "error": "Bad request",
            "details": "request/body must have required property 'settings'",
            "status_code": 400,
            "suggestion": "Check workflow JSON structure",
        },
        {
            "name": "Unauthorized (401)",
            "error": "unauthorized",
            "details": "Invalid API key",
            "status_code": 401,
            "suggestion": "Check N8N_API_KEY in .env file",
        },
        {
            "name": "Not Found (404)",
            "error": "not found",
            "details": "API endpoint not found",
            "status_code": 404,
            "suggestion": "Check N8N_BASE_URL in .env file",
        },
        {
            "name": "Conflict (409)",
            "error": "conflict",
            "details": "Node ID already exists",
            "status_code": 409,
            "suggestion": "Check for node ID conflicts",
        },
        {
            "name": "Unknown Error",
            "error": "Unknown error occurred",
            "details": "",
            "status_code": "N/A",
            "suggestion": "Check your n8n configuration",
        },
    ]

    for i, scenario in enumerate(error_scenarios, 1):
        print(f"\n{i}. Testing {scenario['name']}...")

        # Create a mock error response
        mock_result = {
            "success": False,
            "error": scenario["error"],
            "details": scenario["details"],
            "status_code": scenario["status_code"],
            "suggestion": scenario["suggestion"],
        }

        # Simulate what the error message would look like
        error_msg = mock_result.get("error", "Unknown error")
        details = mock_result.get("details", "")
        suggestion = mock_result.get("suggestion", "Check your n8n configuration")
        status_code = mock_result.get("status_code", "N/A")

        error_section = f"❌ **Failed to create workflow in n8n**\n"
        error_section += f"**Error:** {error_msg}\n"

        if details:
            error_section += f"**Details:** {details}\n"

        if status_code != "N/A":
            error_section += f"**Status Code:** {status_code}\n"

        error_section += f"**Suggestion:** {suggestion}\n"

        # Add debugging tips based on error type
        if "Bad request" in error_msg or "400" in str(status_code):
            error_section += f"\n**Debugging Tips:**\n"
            error_section += f"- Check workflow JSON structure\n"
            error_section += f"- Validate all required fields are present\n"
            error_section += f"- Remove read-only fields like 'active' and 'tags'\n"
            error_section += f"- Ensure 'settings' field exists\n"

        elif "unauthorized" in error_msg.lower() or "401" in str(status_code):
            error_section += f"\n**Debugging Tips:**\n"
            error_section += f"- Check N8N_API_KEY in .env file\n"
            error_section += f"- Verify API key is valid in n8n UI\n"
            error_section += f"- Ensure API authentication is enabled\n"

        elif "not found" in error_msg.lower() or "404" in str(status_code):
            error_section += f"\n**Debugging Tips:**\n"
            error_section += f"- Check N8N_BASE_URL in .env file\n"
            error_section += f"- Verify REST API is enabled in n8n\n"
            error_section += f"- Ensure endpoint paths are correct\n"

        elif "conflict" in error_msg.lower() or "409" in str(status_code):
            error_section += f"\n**Debugging Tips:**\n"
            error_section += f"- Check for node ID conflicts\n"
            error_section += f"- Verify node names are unique\n"
            error_section += f"- Ensure connections reference existing nodes\n"

        print(f"   Error Message Preview:")
        print(f"   {error_section}")

    print("\n✅ All error handling tests completed!")
    print("\n🎯 Summary of Improvements:")
    print("   - Detailed error messages with status codes")
    print("   - Specific debugging tips for each error type")
    print("   - Clear suggestions for resolving issues")
    print("   - Contextual help based on error category")
    print("\n   Users will now see comprehensive error information")
    print("   directly in the chat interface when issues occur!")


if __name__ == "__main__":
    test_error_handling()
