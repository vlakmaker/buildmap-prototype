# n8n API Fix Summary

## Critical Discovery: PUT vs PATCH

### The Problem
BuildMap was experiencing **405 Method Not Allowed** errors when attempting to update workflows in n8n. The implementation was using `PATCH` requests for workflow updates, which is not supported by the n8n Public API.

### Root Cause
After analyzing the complete n8n Public API v1.1.1 OpenAPI specification, we discovered:

**Workflows use PUT (full replacement), not PATCH**

```json
"/workflows/{id}": {
  "put": {
    "summary": "Update a workflow",
    "description": "Update a workflow. If the workflow is published, the updated version will be automatically re-published."
  }
}
```

**However, Credentials DO support PATCH:**
```json
"/credentials/{id}": {
  "patch": {
    "summary": "Update a credential"
  }
}
```

This inconsistency in the API design is what caused the confusion.

---

## What Was Fixed

### 1. n8n_client.py - `update_workflow()` method
**File:** `n8n_integration/n8n_client.py:283-421`

**Changed from:**
```python
response = requests.patch(
    f"{self.base_url}/api/v1/workflows/{workflow_id}",
    headers=headers,
    json=workflow_json,
    timeout=15,
)
```

**Changed to:**
```python
# n8n API uses PUT for workflow updates (full replacement)
response = requests.put(
    f"{self.base_url}/api/v1/workflows/{workflow_id}",
    headers=headers,
    json=workflow_json,
    timeout=15,
    verify=True,
)
```

**Additional improvements:**
- Enhanced error handling with specific status codes (401, 403, 404, 405, 400, 409)
- Added detailed error messages with debugging suggestions
- Added SSL verification
- Return includes workflow ID, name, and URL on success
- Added explicit 405 handler to catch any future PATCH attempts

### 2. n8n_client.py - `get_workflow()` method
**File:** `n8n_integration/n8n_client.py:423-500`

**Improvements:**
- Enhanced error handling matching `update_workflow()` and `create_workflow()`
- Added specific handlers for 401, 403, 404 status codes
- Added SSL error handling
- Added timeout handling
- Added connection error handling
- Consistent error response format with details and suggestions

### 3. test_n8n_integration.py - Integration tests
**File:** `n8n_integration/test_n8n_integration.py:151-170`

**Updated test pattern:**
```python
# OLD (incorrect pattern):
updated_workflow = sample_workflow.copy()
updated_workflow["name"] = "Updated Test Workflow"
update_result = n8n_client.update_workflow(workflow_id, updated_workflow)

# NEW (correct GET → Modify → PUT pattern):
get_result = n8n_client.get_workflow(workflow_id)
if get_result["success"]:
    existing_workflow = get_result["workflow"]
    existing_workflow["name"] = "Updated Test Workflow"
    update_result = n8n_client.update_workflow(workflow_id, existing_workflow)
```

This follows the recommended approach from the API documentation:
1. GET the existing workflow
2. Modify the fields you want to change
3. PUT the complete workflow back

---

## How to Use the Updated API

### Creating a Workflow (POST)
```python
workflow = {
    "name": "My Workflow",
    "nodes": [...],
    "connections": {...}
}

result = n8n_client.create_workflow(workflow)
if result["success"]:
    workflow_id = result["id"]
    print(f"Created: {result['url']}")
```

### Updating a Workflow (GET → Modify → PUT)
```python
# Step 1: Get existing workflow
get_result = n8n_client.get_workflow(workflow_id)

if get_result["success"]:
    existing = get_result["workflow"]

    # Step 2: Modify as needed
    existing["name"] = "Updated Name"
    existing["nodes"].append(new_node)
    existing["connections"]["New Node"] = {...}

    # Step 3: Update with complete workflow
    update_result = n8n_client.update_workflow(workflow_id, existing)

    if update_result["success"]:
        print(f"Updated: {update_result['url']}")
    else:
        print(f"Error: {update_result['error']}")
        print(f"Details: {update_result.get('details', 'N/A')}")
        print(f"Suggestion: {update_result.get('suggestion', 'N/A')}")
```

### Multi-Phase Workflow Building
The `workflow_manager.py` already implements the correct pattern:

```python
def update_existing_workflow(self, workflow_json, original_response):
    # 1. Get existing workflow
    existing_result = self.client.get_workflow(st.session_state.current_workflow_id)

    # 2. Merge workflows
    existing_workflow = existing_result["workflow"]
    merged_workflow = self.client.merge_workflows(existing_workflow, workflow_json)

    # 3. Update with PUT (complete workflow)
    update_result = self.client.update_workflow(
        st.session_state.current_workflow_id,
        merged_workflow
    )
```

---

## Important Notes

### Read-Only Fields
The following fields are automatically removed by `validate_workflow_json()`:
- `id`
- `active`
- `tags`
- `version`
- `versionId`
- `createdAt`
- `updatedAt`

### Required Fields
Every workflow MUST have:
- `name` (non-empty string)
- `nodes` (array with at least one node)
- `connections` (object, can be empty)
- `settings` (object, can be empty - added automatically if missing)

### Active Workflows
**Important:** If a workflow is published (active), updating it will automatically re-publish the new version. This happens server-side and cannot be prevented when using PUT.

---

## Testing the Fix

Run the integration test to verify everything works:

```bash
python n8n_integration/test_n8n_integration.py
```

Expected output:
```
🧪 Testing n8n Client...
   Connected: True

🧪 Testing Full Integration...
1. Creating test workflow...
   ✅ Workflow created: Test Integration Workflow
   🔗 URL: http://localhost:5678/workflow/xxx

2. Retrieving workflow...
   ✅ Workflow retrieved: Test Integration Workflow

3. Updating workflow...
   ✅ Workflow updated successfully
   🔗 URL: http://localhost:5678/workflow/xxx

4. Cleaning up...
   ✅ Test workflow deleted
```

---

## References

- **API Documentation:** `n8n_integration/N8N_API_REFERENCE.md`
- **OpenAPI Spec:** n8n Public API v1.1.1
- **Issue:** 405 Method Not Allowed on workflow updates
- **Fix Date:** 2026-01-14
