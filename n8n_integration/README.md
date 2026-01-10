# 🔗 n8n API Integration

This directory contains the n8n API integration components for BuildMap.

## 📁 Files

### `n8n_client.py`
Handles all communication with the n8n REST API:
- Connection testing and validation
- Workflow creation and updates
- Workflow retrieval
- JSON validation
- URL generation
- Workflow merging for phase-based building

### `workflow_manager.py`
Manages the workflow lifecycle and phase-by-phase building:
- Session state management
- JSON extraction from AI responses
- Workflow creation and updates
- Phase tracking
- Status monitoring

### `test_n8n_integration.py`
Comprehensive test suite for the n8n integration:
- Client functionality tests
- Workflow manager tests
- Full integration tests
- Error handling validation

## 🚀 Features

### Automatic Workflow Creation
- AI provides workflow JSON in responses
- BuildMap automatically creates workflows in n8n
- Direct links to test workflows immediately

### Phase-by-Phase Building
- Phase 1: Create new workflow
- Phase 2+: Update existing workflow by merging new nodes
- Automatic phase tracking and history

### Robust Error Handling
- Connection validation
- JSON validation
- API error handling
- Graceful degradation when n8n is unavailable

### User Interface Integration
- Connection status in sidebar
- Current workflow tracking
- Direct links to n8n workflows
- Phase history and progress

## 🔧 Configuration

Add to your `.env` file:

```
# n8n API Configuration
N8N_BASE_URL=https://your-n8n-server.com
N8N_API_KEY=your_n8n_api_key_here
```

## 📝 Usage

### In BuildMap
1. Set up n8n connection in `.env`
2. Restart BuildMap
3. n8n connection status appears in sidebar
4. When AI provides workflow JSON, it's automatically created in n8n
5. Direct links to test workflows are provided

### Testing
Run the test suite:

```bash
python test_n8n_integration.py
```

## 🎯 Integration Points

### Main App (`buildmap.py`)
- Imports `n8n_client` and `workflow_manager`
- Initializes workflow session state
- Processes AI responses through workflow manager
- Displays n8n connection status and workflow info

### System Prompt
- Updated to guide AI to provide workflow JSON
- Standard format for phase-based workflows
- Clear instructions for testing

## 🛡️ Error Handling

The integration handles various error scenarios:
- Missing API keys
- Connection failures
- Invalid workflow JSON
- API errors
- Network timeouts

## 🔗 API Endpoints Used

- `GET /api/v1/meta` - Test connection and get version
- `POST /api/v1/workflows` - Create new workflow
- `GET /api/v1/workflows/{id}` - Get workflow details
- `PATCH /api/v1/workflows/{id}` - Update existing workflow

## 🎨 UI Components

### Sidebar
- n8n connection status (✅/⚠️)
- Current workflow info
- Direct n8n links
- Reset workflow button

### Chat Interface
- Enhanced responses with n8n links
- Phase completion notifications
- Next steps guidance

## 📊 Metrics

- Connection status tracking
- Workflow creation success rate
- Phase completion tracking
- Error logging and reporting

## 🚧 Troubleshooting

### "Cannot connect to n8n"
- Check `N8N_BASE_URL` and `N8N_API_KEY` in `.env`
- Verify n8n server is running
- Check network/firewall settings
- Ensure port 5678 is exposed in Docker

### "Authentication failed"
- Verify `N8N_API_KEY` is correct
- Check API is enabled in n8n settings
- Ensure key has proper permissions

### "Invalid workflow JSON"
- Check AI response format
- Validate JSON structure
- Ensure required fields are present

## 🎯 Design Philosophy

1. **Seamless Integration** - Workflows appear in n8n without manual steps
2. **Phase-by-Phase** - Build incrementally with validation at each step
3. **User Control** - Users can test before automatic creation
4. **Robust Error Handling** - Clear feedback when things go wrong
5. **Transparency** - Users see exactly what's being created

## 📋 Requirements

- n8n 0.200.0+ (with REST API enabled)
- Python 3.8+
- `requests` library
- Valid n8n API key
- Network access to n8n server

## 📊 Performance

- Fast API calls (typically < 1s)
- Minimal overhead on chat responses
- Efficient JSON parsing
- Low memory usage

## 🛠️ Development

To modify or extend:
1. Update `n8n_client.py` for new API features
2. Modify `workflow_manager.py` for new workflow logic
3. Add tests to `test_n8n_integration.py`
4. Update system prompt for new AI guidance

## 🎉 Benefits

- ✅ No manual workflow import/export
- ✅ Direct testing in n8n
- ✅ Phase-by-phase validation
- ✅ Automatic error handling
- ✅ Better user experience
- ✅ Production-ready integration