# n8n Public API Reference

Complete reference for n8n Public API v1.1.1 operations available to BuildMap.

**Base URL:** `/api/v1`
**Authentication:** `X-N8N-API-KEY` header

---

## Workflow Operations

### Create Workflow
```
POST /workflows
```
Create a new workflow in your n8n instance.

**Request Body:**
```json
{
  "name": "My Workflow",
  "nodes": [...],
  "connections": {...},
  "settings": {...}
}
```

**Response:** Workflow object with ID

---

### Get All Workflows
```
GET /workflows
```
Retrieve all workflows from your instance.

**Query Parameters:**
- `active` (boolean) - Filter by active status
- `tags` (string) - Filter by tags (comma-separated)
- `name` (string) - Filter by name
- `projectId` (string) - Filter by project
- `excludePinnedData` (boolean) - Exclude pinned data
- `limit` (number, max 250, default 100)
- `cursor` (string) - Pagination cursor

**Response:**
```json
{
  "data": [workflow objects],
  "nextCursor": "..."
}
```

---

### Get Workflow by ID
```
GET /workflows/{id}
```
Retrieve a specific workflow.

**Query Parameters:**
- `excludePinnedData` (boolean) - Exclude pinned data

**Response:** Workflow object

---

### Update Workflow ⚠️ **USES PUT, NOT PATCH**
```
PUT /workflows/{id}
```
**Update a workflow. If the workflow is published, the updated version will be automatically re-published.**

**IMPORTANT:** This is a **PUT** operation (full replacement), not PATCH (partial update).

**Request Body:** Complete workflow object
```json
{
  "name": "Updated Workflow",
  "nodes": [...],
  "connections": {...},
  "settings": {...}
}
```

**Response:** Updated workflow object

---

### Delete Workflow
```
DELETE /workflows/{id}
```
Delete a workflow from your instance.

**Response:** Deleted workflow object

---

### Activate/Publish Workflow
```
POST /workflows/{id}/activate
```
Publish a workflow (formerly called "activating" in n8n v1).

**Request Body (optional):**
```json
{
  "versionId": "specific-version-id",  // Optional
  "name": "Version name",              // Optional
  "description": "Version description" // Optional
}
```

**Response:** Workflow object with `active: true`

---

### Deactivate Workflow
```
POST /workflows/{id}/deactivate
```
Deactivate a workflow.

**Response:** Workflow object with `active: false`

---

### Get Workflow Version
```
GET /workflows/{id}/{versionId}
```
Retrieve a specific version of a workflow from workflow history.

**Response:** Workflow version object

---

### Transfer Workflow to Project
```
PUT /workflows/{id}/transfer
```
Transfer a workflow to another project.

**Request Body:**
```json
{
  "destinationProjectId": "project-id"
}
```

---

### Get Workflow Tags
```
GET /workflows/{id}/tags
```
Get tags assigned to a workflow.

**Response:** Array of tag objects

---

### Update Workflow Tags
```
PUT /workflows/{id}/tags
```
Update tags assigned to a workflow.

**Request Body:**
```json
[
  {"id": "tag-id-1"},
  {"id": "tag-id-2"}
]
```

---

## Execution Operations

### Get All Executions
```
GET /executions
```
Retrieve all executions from your instance.

**Query Parameters:**
- `includeData` (boolean) - Include execution data
- `status` (string) - Filter by status: `canceled`, `error`, `running`, `success`, `waiting`
- `workflowId` (string) - Filter by workflow
- `projectId` (string) - Filter by project
- `limit` (number, max 250, default 100)
- `cursor` (string) - Pagination cursor

---

### Get Execution by ID
```
GET /executions/{id}
```
Retrieve a specific execution.

**Query Parameters:**
- `includeData` (boolean) - Include execution data

---

### Delete Execution
```
DELETE /executions/{id}
```
Delete an execution from your instance.

---

### Retry Execution
```
POST /executions/{id}/retry
```
Retry a failed execution.

**Request Body (optional):**
```json
{
  "loadWorkflow": true  // Use latest workflow version (default: false)
}
```

---

## Credential Operations

### Create Credential
```
POST /credentials
```
Create a credential that can be used by nodes.

**Request Body:**
```json
{
  "name": "My Credential",
  "type": "credentialType",
  "data": {
    "apiKey": "...",
    "domain": "..."
  }
}
```

---

### Update Credential
```
PATCH /credentials/{id}
```
**Note:** Credentials use PATCH (partial update).

**Request Body:**
```json
{
  "name": "Updated Name",  // Optional
  "type": "newType",       // Optional (requires data)
  "data": {...},           // Optional
  "isPartialData": false   // Merge vs replace (default: false)
}
```

---

### Delete Credential
```
DELETE /credentials/{id}
```
Delete a credential. You must be the owner.

---

### Get Credential Schema
```
GET /credentials/schema/{credentialTypeName}
```
Get the JSON schema for a credential type.

**Example:** `/credentials/schema/githubApi`

---

## Tag Operations

### Create Tag
```
POST /tags
```

### Get All Tags
```
GET /tags
```

### Get Tag by ID
```
GET /tags/{id}
```

### Update Tag
```
PUT /tags/{id}
```

### Delete Tag
```
DELETE /tags/{id}
```

---

## User Operations (Enterprise)

### Get All Users
```
GET /users
```
**Requires:** Instance owner

**Query Parameters:**
- `limit`, `cursor` - Pagination
- `includeRole` (boolean) - Include role info
- `projectId` (string) - Filter by project

---

### Create Users
```
POST /users
```
**Requires:** Instance owner

**Request Body:**
```json
[
  {
    "email": "user@example.com",
    "role": "global:member"
  }
]
```

---

### Get User by ID/Email
```
GET /users/{id}
```

### Delete User
```
DELETE /users/{id}
```

### Change User Role
```
PATCH /users/{id}/role
```

**Request Body:**
```json
{
  "newRoleName": "global:member"
}
```

---

## Variable Operations

### Create Variable
```
POST /variables
```

### Get All Variables
```
GET /variables
```

### Update Variable
```
PUT /variables/{id}
```

### Delete Variable
```
DELETE /variables/{id}
```

---

## Project Operations (Enterprise)

### Create Project
```
POST /projects
```

### Get All Projects
```
GET /projects
```

### Update Project
```
PUT /projects/{projectId}
```

### Delete Project
```
DELETE /projects/{projectId}
```

### Add Users to Project
```
POST /projects/{projectId}/users
```

### Remove User from Project
```
DELETE /projects/{projectId}/users/{userId}
```

### Change User Role in Project
```
PATCH /projects/{projectId}/users/{userId}
```

---

## Audit Operations (Enterprise)

### Generate Security Audit
```
POST /audit
```

**Request Body:**
```json
{
  "additionalOptions": {
    "daysAbandonedWorkflow": 90,
    "categories": [
      "credentials",
      "database",
      "nodes",
      "filesystem",
      "instance"
    ]
  }
}
```

---

## Source Control Operations (Enterprise)

### Pull from Remote Repository
```
POST /source-control/pull
```

**Request Body:**
```json
{
  "force": true,
  "variables": {
    "key": "value"
  }
}
```

---

## Key Findings for BuildMap

### ✅ Supported Operations
1. **Create workflows** - POST /workflows
2. **Update workflows** - **PUT /workflows/{id}** (full replacement)
3. **Get workflows** - GET /workflows, GET /workflows/{id}
4. **Delete workflows** - DELETE /workflows/{id}
5. **Activate/deactivate** - POST /workflows/{id}/activate|deactivate
6. **Manage tags** - GET/PUT /workflows/{id}/tags
7. **View executions** - GET /executions
8. **Retry executions** - POST /executions/{id}/retry

### ❌ Important Limitations
1. **No PATCH for workflows** - Must use PUT (full replacement)
2. **PUT requires complete workflow** - Cannot do partial updates
3. **Version history is read-only** - Can view but not directly manipulate
4. **Active workflows auto-republish** - Updating active workflow re-publishes it

### 🎯 Recommended Approach for Multi-Phase Workflows

**Option 1: GET + Merge + PUT (Current approach is correct!)**
```python
# 1. Get existing workflow
existing = GET /workflows/{id}

# 2. Merge with new nodes
merged = merge_workflows(existing, new_phase_nodes)

# 3. Update via PUT
updated = PUT /workflows/{id} with merged workflow
```

**Option 2: Create New Workflow (Simpler)**
```python
# 1. Get existing workflow
existing = GET /workflows/{id}

# 2. Merge with new nodes
merged = merge_workflows(existing, new_phase_nodes)

# 3. Create as new workflow
new_workflow = POST /workflows with merged workflow
```

---

## Workflow Schema

### Required Fields
```json
{
  "name": "string (required)",
  "nodes": "array (required)",
  "connections": "object (required)",
  "settings": "object (required)"
}
```

### Read-Only Fields
- `id`
- `active`
- `createdAt`
- `updatedAt`
- `tags` (managed separately via /workflows/{id}/tags)

### Settings Object
```json
{
  "saveExecutionProgress": boolean,
  "saveManualExecutions": boolean,
  "saveDataErrorExecution": "all" | "none",
  "saveDataSuccessExecution": "all" | "none",
  "executionTimeout": number,
  "errorWorkflow": "workflow-id",
  "timezone": "string",
  "callerPolicy": "any" | "none" | "workflowsFromAList" | "workflowsFromSameOwner",
  "callerIds": "string",
  "availableInMCP": boolean
}
```

---

## Authentication

All requests require:
```
X-N8N-API-KEY: your-api-key-here
```

Generate API keys in n8n UI: Settings → API → Create API Key

---

## Pagination

List endpoints support cursor-based pagination:
```
GET /workflows?limit=100&cursor=nextCursorFromPreviousResponse
```

Response includes `nextCursor` for next page (null if last page).

---

## Error Responses

- `400` - Bad Request (malformed data)
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict
- `415` - Unsupported Media Type

---

## Rate Limiting

Not documented in API spec - check n8n instance configuration.
