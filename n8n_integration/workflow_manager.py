"""
BuildMap Workflow Manager - Handles workflow creation and phase management
"""

import re
import json
from typing import Dict, Any, Optional, Tuple
from n8n_integration.n8n_client import n8n_client
import streamlit as st

class WorkflowManager:
    """Manages workflow creation and phase-by-phase building"""
    
    def __init__(self):
        self.client = n8n_client
        
    def initialize_session_state(self):
        """Initialize workflow-related session state variables"""
        if 'current_workflow_id' not in st.session_state:
            st.session_state.current_workflow_id = None
        if 'current_workflow_name' not in st.session_state:
            st.session_state.current_workflow_name = None
        if 'current_phase' not in st.session_state:
            st.session_state.current_phase = 1
        if 'workflow_phase_history' not in st.session_state:
            st.session_state.workflow_phase_history = []
    
    def extract_workflow_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract workflow JSON from AI response text"""
        # Look for JSON in code blocks (more flexible pattern)
        json_match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        
        if json_match:
            try:
                json_str = json_match.group(1).strip()
                workflow_json = json.loads(json_str)
                return workflow_json
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return None
        
        # Try alternative code block patterns
        alt_matches = [
            re.search(r'```\n(.*?)\n```', text, re.DOTALL),  # Generic code block
            re.search(r'```javascript\n(.*?)\n```', text, re.DOTALL),  # JS code block
        ]
        
        for match in alt_matches:
            if match:
                try:
                    json_str = match.group(1).strip()
                    workflow_json = json.loads(json_str)
                    return workflow_json
                except json.JSONDecodeError:
                    continue
        
        # Look for JSON in regular text (more robust approach)
        try:
            # Find potential JSON objects
            json_objects = []
            stack = []
            json_start = -1
            
            for i, char in enumerate(text):
                if char == '{':
                    stack.append(i)
                elif char == '}' and stack:
                    start = stack.pop()
                    if not stack:  # Found complete object
                        json_str = text[start:i+1]
                        try:
                            workflow_json = json.loads(json_str)
                            # Check if it looks like a workflow
                            if 'nodes' in workflow_json and 'connections' in workflow_json:
                                return workflow_json
                        except json.JSONDecodeError:
                            pass
        except:
            pass
        
        return None
    
    def process_ai_response(self, ai_response: str) -> str:
        """Process AI response and create/update workflows in n8n"""
        workflow_json = self.extract_workflow_json_from_text(ai_response)
        
        if workflow_json:
            return self.handle_workflow_creation(workflow_json, ai_response)
        else:
            return ai_response
    
    def handle_workflow_creation(self, workflow_json: Dict[str, Any], original_response: str) -> str:
        """Handle workflow creation or update in n8n"""
        # Check if this is a phase-based workflow
        phase_match = re.search(r'Phase\s+(\d+)', workflow_json.get('name', ''), re.IGNORECASE)
        
        if phase_match:
            phase_number = int(phase_match.group(1))
            st.session_state.current_phase = phase_number
        
        if st.session_state.current_workflow_id:
            # Update existing workflow (Phase 2+)
            return self.update_existing_workflow(workflow_json, original_response)
        else:
            # Create new workflow (Phase 1)
            return self.create_new_workflow(workflow_json, original_response)
    
    def create_new_workflow(self, workflow_json: Dict[str, Any], original_response: str) -> str:
        """Create a new workflow in n8n"""
        result = self.client.create_workflow(workflow_json)
        
        if result["success"]:
            # Store workflow info in session
            st.session_state.current_workflow_id = result["id"]
            st.session_state.current_workflow_name = workflow_json.get("name", "Unnamed Workflow")
            st.session_state.workflow_phase_history.append({
                "phase": st.session_state.current_phase,
                "workflow_id": result["id"],
                "name": workflow_json.get("name", "Unnamed")
            })
            
            # Enhance the response with direct n8n link
            n8n_link = result["url"]
            return f"{original_response}\n\n🎉 **Phase {st.session_state.current_phase} created in n8n!**\n\n[Open in n8n]({n8n_link})\n\n**Next Steps:**\n1. Test the workflow in n8n\n2. Come back here when ready for Phase {st.session_state.current_phase + 1}"
        else:
            return f"{original_response}\n\n❌ **Failed to create workflow in n8n:** {result['error']}"
    
    def update_existing_workflow(self, workflow_json: Dict[str, Any], original_response: str) -> str:
        """Update existing workflow with new phase"""
        # First, get the existing workflow
        existing_result = self.client.get_workflow(st.session_state.current_workflow_id)
        
        if not existing_result["success"]:
            return f"{original_response}\n\n❌ **Cannot update workflow:** {existing_result['error']}"
        
        # Merge the workflows
        existing_workflow = existing_result["workflow"]
        merged_workflow = self.client.merge_workflows(existing_workflow, workflow_json)
        
        # Update the workflow
        update_result = self.client.update_workflow(st.session_state.current_workflow_id, merged_workflow)
        
        if update_result["success"]:
            # Update phase history
            st.session_state.workflow_phase_history.append({
                "phase": st.session_state.current_phase,
                "workflow_id": st.session_state.current_workflow_id,
                "name": workflow_json.get("name", "Unnamed")
            })
            
            n8n_link = self.client.get_workflow_url(st.session_state.current_workflow_id)
            return f"{original_response}\n\n✅ **Phase {st.session_state.current_phase} added to workflow!**\n\n[Open in n8n]({n8n_link})\n\n**Next Steps:**\n1. Test the updated workflow\n2. Continue with Phase {st.session_state.current_phase + 1} when ready"
        else:
            return f"{original_response}\n\n❌ **Failed to update workflow:** {update_result['error']}"
    
    def reset_current_workflow(self):
        """Reset the current workflow state"""
        st.session_state.current_workflow_id = None
        st.session_state.current_workflow_name = None
        st.session_state.current_phase = 1
        st.session_state.workflow_phase_history = []
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status for UI display"""
        try:
            if hasattr(st.session_state, 'current_workflow_id') and st.session_state.current_workflow_id:
                return {
                    "has_workflow": True,
                    "workflow_id": st.session_state.current_workflow_id,
                    "workflow_name": getattr(st.session_state, 'current_workflow_name', 'Unnamed Workflow'),
                    "current_phase": getattr(st.session_state, 'current_phase', 1),
                    "phase_history": getattr(st.session_state, 'workflow_phase_history', []),
                    "n8n_url": self.client.get_workflow_url(st.session_state.current_workflow_id)
                }
            else:
                return {
                    "has_workflow": False,
                    "message": "No active workflow"
                }
        except Exception:
            # Handle cases where session state is not available (e.g., testing)
            return {
                "has_workflow": False,
                "message": "Session not initialized"
            }

# Singleton instance
workflow_manager = WorkflowManager()