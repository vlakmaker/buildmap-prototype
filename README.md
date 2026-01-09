# 🎯 BuildMap - n8n Workflow Builder Prototype

BuildMap is a conversational AI assistant that helps you build n8n workflows incrementally through phase-by-phase guidance. Instead of generating entire workflows at once, BuildMap breaks down complex automation into small, testable phases (1-3 nodes each) and validates each phase before moving forward.

## 🌟 Key Features

- **Phase-by-Phase Guidance**: Build workflows in small, manageable steps
- **Conversational Interface**: Natural language interaction to understand your needs
- **Strategic Planning**: Get multiple approaches with trade-offs before starting
- **Test-Driven**: Validate each phase before proceeding to the next
- **Copy-Paste Ready**: Exact node configurations you can use immediately
- **Multi-Model Support**: Choose from Claude Sonnet 4, GPT-4o, and more
- **Clean UI**: Streamlit-based chat interface with streaming responses

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenRouter API key ([get one here](https://openrouter.ai/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/buildmap-prototype.git
   cd buildmap-prototype
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=your_actual_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run buildmap.py
   ```

5. **Open your browser**

   Streamlit will automatically open `http://localhost:8501` in your browser.

## 🔑 Getting an OpenRouter API Key

1. Go to [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for a free account
3. Navigate to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Copy the key and paste it into your `.env` file

OpenRouter provides access to multiple AI models through a single API, including Claude, GPT-4, and others. You only pay for what you use.

## 💡 How It Works

BuildMap follows a structured approach to workflow building:

### 1. Discovery Phase
BuildMap asks clarifying questions to understand:
- What problem you're solving
- What tools/services are involved
- Your technical comfort level
- Success criteria and constraints

### 2. Strategy Phase
You'll get 2-3 different approaches with:
- Clear pros and cons
- Cost implications
- Complexity levels
- Best-fit scenarios

### 3. Implementation Phases
Your chosen approach is broken into phases:
- **Phase 1**: Data access/input (establish data flow)
- **Phase 2**: Core logic/transformation
- **Phase 3**: Actions/outputs
- **Phase 4+**: Enhancements and error handling

### 4. Validation Checkpoints
After each phase:
- You add the recommended nodes
- Test the workflow
- Confirm it works before proceeding
- Troubleshoot any issues together

## 🎨 Available Models

Choose from multiple AI models in the sidebar:

- **Claude Sonnet 4** (Default) - Best balance of capability and cost
- **Claude 3.5 Sonnet** - Excellent reasoning and long context
- **GPT-4o** - Strong general performance
- **GPT-4o Mini** - Fast and cost-effective
- **Claude 3 Haiku** - Very fast and economical

## 📝 Usage Example

**You**: I want to automatically triage my Gmail inbox

**BuildMap**: Great! Let me understand your needs better:
1. How many emails do you receive daily?
2. What types of emails? (newsletters, work, personal, etc.)
3. What do you currently do with them manually?
...

After gathering information, BuildMap will:
1. Recommend 2-3 approaches (rule-based, AI-powered, hybrid)
2. Help you choose based on your needs
3. Break implementation into testable phases
4. Guide you through each phase with exact configurations
5. Validate each phase works before moving forward

## 🗂️ Project Structure

```
buildmap-prototype/
├── .gitignore              # Git ignore rules
├── .env.example            # Environment variables template
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── buildmap.py             # Main Streamlit application
└── prompts/
    └── system_prompt.txt   # BuildMap system prompt
```

## 🛠️ Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run buildmap.py
```

### Modifying the System Prompt

The AI's behavior is controlled by `prompts/system_prompt.txt`. Edit this file to change how BuildMap guides users through workflow building.

After editing, restart the Streamlit app to see changes.

## 🎯 Design Philosophy

BuildMap is designed around these principles:

1. **Incremental Progress**: Small steps prevent overwhelming complexity
2. **Test-Driven**: Validate each piece before building on it
3. **Educational**: Users learn n8n while building
4. **Practical**: Copy-paste ready configurations, not vague instructions
5. **Adaptive**: Adjusts based on user's responses and feedback

## 🐛 Troubleshooting

### "OPENROUTER_API_KEY not found"
- Make sure you created a `.env` file (not `.env.example`)
- Verify your API key is correct
- Restart the Streamlit app after adding the key

### Streaming Responses Not Working
- Check your internet connection
- Verify your OpenRouter API key is valid
- Try a different model from the dropdown

### Import Errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- You may need to upgrade pip: `pip install --upgrade pip`

## 🚧 Known Limitations

This is a prototype focused on testing the conversational approach:

- No conversation persistence (cleared on page refresh)
- No user authentication
- No database storage
- Basic error handling
- Not optimized for mobile

These will be addressed in the production version.

## 📊 Technology Stack

- **Frontend**: Streamlit
- **AI Integration**: OpenRouter API (via OpenAI Python SDK)
- **Models**: Claude Sonnet 4, GPT-4o, and others
- **Language**: Python 3.8+

## 🤝 Contributing

This is a prototype for testing. Feedback and suggestions are welcome!

## 📄 License

This project is provided as-is for testing and evaluation purposes.

## 🔗 Related Links

- [n8n Documentation](https://docs.n8n.io/)
- [OpenRouter](https://openrouter.ai/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 📬 Questions?

Open an issue on GitHub or reach out with questions about using BuildMap.

---

**Built with ❤️ to make workflow automation more accessible**
