"""
BuildMap - n8n Workflow Builder Prototype
A conversational assistant that guides users through building n8n workflows phase-by-phase.
"""

import os
import json
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="BuildMap - n8n Workflow Builder",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    .message-role {
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1976d2;
    }
    .stButton button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Available models
MODELS = {
    "anthropic/claude-sonnet-4": "Claude Sonnet 4 (Default)",
    "anthropic/claude-3.5-sonnet": "Claude 3.5 Sonnet",
    "openai/gpt-4o": "GPT-4o",
    "openai/gpt-4o-mini": "GPT-4o Mini",
    "anthropic/claude-3-haiku": "Claude 3 Haiku"
}

# Create exports directory
EXPORTS_DIR = Path(__file__).parent / "exports"
os.makedirs(EXPORTS_DIR, exist_ok=True)

def save_workflow(workflow_json: dict, phase_name: str) -> str:
    """Save workflow JSON to file and return filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"workflow_{phase_name}_{timestamp}.json"
    filepath = EXPORTS_DIR / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(workflow_json, f, indent=2)

    return filename

def load_system_prompt() -> str:
    """Load the system prompt from file."""
    prompt_path = Path(__file__).parent / "prompts" / "system_prompt.txt"
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"System prompt file not found at {prompt_path}")
        return "You are a helpful assistant for building n8n workflows."

def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'model' not in st.session_state:
        st.session_state.model = "anthropic/claude-sonnet-4"

def get_openrouter_client() -> OpenAI:
    """Create and return an OpenRouter client."""
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        st.error("⚠️ OPENROUTER_API_KEY not found in environment variables!")
        st.info("Please create a .env file with your OpenRouter API key. See README for instructions.")
        st.stop()

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

def stream_response(client: OpenAI, messages: list, model: str):
    """Stream response from OpenRouter API."""
    try:
        system_prompt = load_system_prompt()

        # Prepare messages with system prompt
        api_messages = [{"role": "system", "content": system_prompt}] + messages

        # Create streaming completion
        stream = client.chat.completions.create(
            model=model,
            messages=api_messages,
            stream=True,
            temperature=0.7,
            max_tokens=4000
        )

        # Stream the response
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        error_msg = f"Error: {str(e)}"
        st.error(error_msg)
        yield error_msg

def display_message(role: str, content: str):
    """Display a chat message with appropriate styling."""
    message_class = "user-message" if role == "user" else "assistant-message"
    role_label = "You" if role == "user" else "BuildMap"

    st.markdown(
        f'<div class="chat-message {message_class}">'
        f'<div class="message-role">{role_label}</div>'
        f'{content}'
        f'</div>',
        unsafe_allow_html=True
    )

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()

    # Get OpenRouter client
    client = get_openrouter_client()

    # Sidebar
    with st.sidebar:
        st.title("🎯 BuildMap")
        st.caption("n8n Workflow Builder")

        st.divider()

        # Model selection
        st.subheader("⚙️ Settings")
        selected_model = st.selectbox(
            "Select Model",
            options=list(MODELS.keys()),
            format_func=lambda x: MODELS[x],
            index=0,
            key="model_selector"
        )
        st.session_state.model = selected_model

        st.divider()

        # Session info
        st.subheader("📊 Session Info")
        st.metric("Messages", len(st.session_state.messages))

        st.divider()

        # Clear conversation button
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        # Export conversation button
        if st.session_state.messages and st.button("💾 Export Conversation", use_container_width=True):
            # Create export text
            export_text = "# BuildMap Conversation Export\n\n"
            for msg in st.session_state.messages:
                role_label = "You" if msg["role"] == "user" else "BuildMap"
                export_text += f"## {role_label}\n\n{msg['content']}\n\n---\n\n"

            st.download_button(
                label="Download as Markdown",
                data=export_text,
                file_name="buildmap_conversation.md",
                mime="text/markdown"
            )

        st.divider()

        # Workflow exports section
        st.subheader("📥 Workflow Exports")
        if EXPORTS_DIR.exists():
            export_files = sorted(
                [f for f in EXPORTS_DIR.iterdir() if f.suffix == '.json'],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            if export_files:
                st.caption(f"Found {len(export_files)} workflow file(s)")
                # Show last 5 exports
                for filepath in export_files[:5]:
                    with open(filepath, 'rb') as f:
                        file_content = f.read()
                        st.download_button(
                            label=f"📄 {filepath.name}",
                            data=file_content,
                            file_name=filepath.name,
                            mime="application/json",
                            key=f"download_{filepath.name}",
                            use_container_width=True
                        )
                if len(export_files) > 5:
                    st.caption(f"+ {len(export_files) - 5} more file(s) in exports/")
            else:
                st.caption("No workflow exports yet")
        else:
            st.caption("No workflow exports yet")

        st.divider()

        # Info section
        st.subheader("ℹ️ About")
        st.caption(
            "BuildMap guides you through building n8n workflows "
            "incrementally, one phase at a time. "
            "Test each phase before moving to the next!"
        )

    # Main chat interface
    st.title("🎯 BuildMap - n8n Workflow Builder")
    st.caption("Build n8n workflows conversationally, phase by phase")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What workflow do you want to automate?"):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # Stream the response
            for chunk in stream_response(
                client,
                st.session_state.messages,
                st.session_state.model
            ):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

        # Rerun to update the display
        st.rerun()

    # Show welcome message if no messages yet
    if not st.session_state.messages:
        st.info(
            "👋 Welcome to BuildMap! I'll help you build n8n workflows step-by-step.\n\n"
            "**How it works:**\n"
            "1. Tell me what you want to automate\n"
            "2. I'll ask clarifying questions\n"
            "3. We'll choose the best approach together\n"
            "4. I'll guide you through implementation in small, testable phases\n\n"
            "**Type your message below to get started!**"
        )

if __name__ == "__main__":
    main()
