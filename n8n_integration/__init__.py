"""
n8n Integration Package

This package provides integration with n8n workflow automation platform.
"""

from n8n_integration.n8n_client import N8NClient
from n8n_integration.workflow_manager import WorkflowManager

__all__ = ["N8NClient", "WorkflowManager"]
__version__ = "0.1.0"
