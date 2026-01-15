#!/usr/bin/env python3
"""
Test script to validate the phase management fixes
"""

import json
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from n8n_integration.workflow_manager import WorkflowManager
from n8n_integration.n8n_client import n8n_client


class MockStreamlitState:
    """Mock Streamlit session state for testing"""

    def __init__(self):
        self.state = {}

    def __contains__(self, key):
        return key in self.state

    def __setitem__(self, key, value):
        self.state[key] = value

    def __getitem__(self, key):
        return self.state[key]

    def get(self, key, default=None):
        return self.state.get(key, default)


# Mock streamlit session state
import streamlit as st

st.session_state = MockStreamlitState()


def test_phase_management():
    """Test the phase management logic"""
    print("🧪 Testing Phase Management Logic\n")

    # Initialize workflow manager
    wm = WorkflowManager()
    wm.initialize_session_state()

    print("✅ Initial state:")
    print(f"   current_phase: {st.session_state.get('current_phase')}")
    print(f"   expected_next_phase: {st.session_state.get('expected_next_phase')}")
    print(f"   current_workflow_id: {st.session_state.get('current_workflow_id')}")
    print()

    # Test 1: Try Phase 2 without Phase 1 (should fail)
    print("🧪 Test 1: Try Phase 2 without Phase 1")
    phase2_workflow = {
        "name": "Email Triage - Phase 2: Rule-Based Categorization",
        "nodes": [{"name": "Test Node", "type": "test"}],
        "connections": {},
    }

    result = wm.handle_workflow_creation(phase2_workflow, "AI response with Phase 2")
    if "❌" in result:
        print("✅ Correctly rejected Phase 2 without Phase 1")
    else:
        print("❌ Should have rejected Phase 2")
    print(
        f"   Error: {result.split('❌')[1].strip() if '❌' in result else 'No error'}"
    )
    print()

    # Test 2: Phase 1 (should work)
    print("🧪 Test 2: Phase 1 (should work)")
    phase1_workflow = {
        "name": "Email Triage - Phase 1: Email Access",
        "nodes": [{"name": "Gmail Trigger", "type": "gmailTrigger"}],
        "connections": {},
    }

    result = wm.handle_workflow_creation(phase1_workflow, "AI response with Phase 1")
    print(f"   Result: {result[:100]}...")
    if "🎉" in result or "Phase 1 created" in result:
        print("✅ Phase 1 accepted")
        # Simulate successful workflow creation by setting workflow_id
        st.session_state.current_workflow_id = "test-workflow-id"
        st.session_state.current_workflow_name = "Test Workflow"
        print(f"   current_phase: {st.session_state.get('current_phase')}")
        print(f"   expected_next_phase: {st.session_state.get('expected_next_phase')}")
    else:
        print("❌ Phase 1 should have been accepted")
    print()

    # Test 3: Phase 2 after Phase 1 (should work)
    print("🧪 Test 3: Phase 2 after Phase 1 (should work)")
    result = wm.handle_workflow_creation(phase2_workflow, "AI response with Phase 2")
    if "✅" in result or "Phase 2 added" in result:
        print("✅ Phase 2 accepted after Phase 1")
        print(f"   current_phase: {st.session_state.get('current_phase')}")
        print(f"   expected_next_phase: {st.session_state.get('expected_next_phase')}")
    else:
        print("❌ Phase 2 should have been accepted")
    print()

    # Test 4: Try Phase 2 again (should fail)
    print("🧪 Test 4: Try Phase 2 again (should fail)")
    result = wm.handle_workflow_creation(
        phase2_workflow, "AI response with Phase 2 again"
    )
    if "❌" in result:
        print("✅ Correctly rejected duplicate Phase 2")
        print(f"   Expected Phase 3, got Phase 2")
    else:
        print("❌ Should have rejected duplicate Phase 2")
    print()

    # Test 5: Reset command
    print("🧪 Test 5: Reset workflow command")
    result = wm.process_ai_response("I want to reset workflow")
    if "🔄" in result:
        print("✅ Workflow reset successfully")
        print(f"   current_phase: {st.session_state.get('current_phase')}")
        print(f"   expected_next_phase: {st.session_state.get('expected_next_phase')}")
    else:
        print("❌ Reset should have worked")
    print()

    # Test 6: Get workflow status
    print("🧪 Test 6: Get workflow status")
    status = wm.get_workflow_status()
    print(f"   has_workflow: {status['has_workflow']}")
    print(f"   current_phase: {status['current_phase']}")
    print(f"   expected_next_phase: {status['expected_next_phase']}")
    print()


if __name__ == "__main__":
    test_phase_management()
