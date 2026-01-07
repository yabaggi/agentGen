# 🤖 Simple AI Agent Generator

A web-based tool to create custom AI agents without writing code. Generate fully functional AI-powered applications with a beautiful web interface in minutes.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [What It Can Do](#-what-it-can-do)
- [What It Cannot Do](#-what-it-cannot-do)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Supported LLM Providers](#-supported-llm-providers)
- [Available Tools](#-available-tools)
- [Output Formats](#-output-formats)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)
- [Limitations](#-limitations)
- [License](#license)

---

## Overview

**Simple AI Agent Generator** is a no-code platform that allows you to create custom AI agents through a step-by-step wizard interface. Each generated agent comes with:

- A standalone **web application** (Flask-based UI)
- A **command-line interface** (CLI)
- **Configuration files** for easy customization
- **Pre-built tool integrations** (web scraping, RSS feeds, etc.)

Perfect for creating content summarizers, flashcard generators, email writers, Q&A bots, and more!

---

## Features

| Feature | Description |
|---------|-------------|
| 🎨 **Visual Wizard** | 6-step guided interface to configure your agent |
| 🤖 **Multi-Provider LLM Support** | Google Gemini, Groq, and OpenAI models |
| 🛠️ **Built-in Tools** | Web scraper, RSS reader, text cleaner, file reader |
| 📤 **Multiple Output Formats** | Plain text, JSON, CSV, Markdown, HTML |
| 🌐 **Auto-Generated Web UI** | Each agent gets a beautiful, responsive web interface |
| 💻 **CLI Support** | Command-line interface for terminal users |
| 📝 **Template Library** | Quick-start templates for common use cases |
| ⚙️ **Fully Configurable** | Adjust temperature, max tokens, system prompts |
| 📁 **Clean Code Output** | Well-structured, readable Python code |

---

## ✅ What It Can Do

### Agent Types You Can Create

| Agent Type | Example Use Case |
|------------|------------------|
| **Content Summarizer** | Summarize articles, documents, or web pages |
| **Flashcard Generator** | Create Q&A pairs from study material |
| **Email Writer** | Generate professional emails from bullet points |
| **Q&A Bot** | Answer questions based on provided context |
| **Content Transformer** | Convert content between formats |
| **Text Analyzer** | Analyze sentiment, extract keywords |
| **RSS Digest Creator** | Summarize RSS feed articles |
| **Web Content Processor** | Scrape and process web pages |

### Capabilities

- ✅ Generate standalone Python applications
- ✅ Create web interfaces automatically
- ✅ Support multiple LLM providers
- ✅ Preprocess input with built-in tools
- ✅ Handle multiple input fields
- ✅ Format output in various styles
- ✅ Run agents locally without deployment
- ✅ Customize system prompts and personas
- ✅ Adjust model parameters (temperature, tokens)

---

## ❌ What It Cannot Do

| Limitation | Description |
|------------|-------------|
| **No Multi-Turn Conversations** | Agents are single-request/response, no chat memory |
| **No Agent Chaining** | Cannot connect multiple agents in a pipeline |
| **No Authentication** | Generated apps have no user login system |
| **No Database Storage** | No persistent storage for conversations |
| **No Deployment Tools** | No built-in cloud deployment (local only) |
| **No Fine-Tuning** | Uses pre-trained models only |
| **No Image/Audio Processing** | Text-only input and output |
| **No Real-Time Streaming** | Responses are returned all at once |
| **No Custom Tool Creation** | Limited to 5 pre-built tools |
| **No API Rate Limiting** | No built-in protection against API limits |

---

## Requirements

- **Python 3.8+**
- **pip** (Python package manager)
- **API Key** from at least one provider:
  - Google AI Studio (Gemini) - [Get Key](https://makersuite.google.com/app/apikey)
  - Groq - [Get Key](https://console.groq.com/keys)
  - OpenAI - [Get Key](https://platform.openai.com/api-keys)

---

## Installation

### 1. Clone or Download

```bash
# Create project directory
mkdir ai-agent-generator
cd ai-agent-generator

### 2. Create Project Structure

```bash
mkdir -p templates static/css static/js
3. Add Project Files
Copy the following files to their respective locations:

* app.py → project root
* index.html → templates/
* style.css → static/css/
* app.js → static/js/

4. Install Dependencies
bashDownloadCopy codepip install flask pyyaml requests
Optional (for tools):
bashDownloadCopy codepip install beautifulsoup4 feedparser
5. Run the Generator
bashDownloadCopy codepython app.py
6. Open in Browser
http://localhost:5000


Quick Start
Create Your First Agent in 2 Minutes

1. Open http://localhost:5000
2. Step 1: Name your agent (e.g., summarizer)
3. Step 2: Select model (e.g., Gemini Flash) and set persona
4. Step 3: Click "📝 Summarizer" template button
5. Step 4: Skip tools (optional)
6. Step 5: Select output format (Plain Text)
7. Step 6: Click "🚀 Create Agent"

Run Your Agent
bashDownloadCopy code# Set your API key first
nano generated_agents/config/global_config.yaml

# Run the agent
cd generated_agents/agents/summarizer
python web_app.py

# Open http://localhost:5001

Usage Guide
Step-by-Step Wizard
Step 1: Basic Information

* Agent Name: Lowercase, underscores allowed (e.g., content_summarizer)
* Description: Brief explanation of what your agent does

Step 2: Model Configuration

* LLM Model: Choose from Google, Groq, or OpenAI models
* System Role: Define the AI's persona and behavior
* Max Tokens: Maximum response length (100-4000)
* Temperature: Creativity level (0.0 = focused, 1.0 = creative)

Step 3: Prompt Configuration

* Quick Templates: Pre-built configurations for common agents
* Required Fields: Input variables your agent needs
* Prompt Template: Instructions sent to the LLM (use {field_name} for variables)

Step 4: Tools Selection

* Select preprocessing tools (optional)
* Multiple tools can be selected
* Tools automatically process input before sending to LLM

Step 5: Output Format

* Choose how the LLM response should be displayed
* Affects the generated web UI's rendering

Step 6: Review & Create

* Preview generated files
* Confirm configuration
* Generate the agent


🤖 Supported LLM Providers
Google (Gemini)
ModelIDBest ForGemini Flashgemini-flashFast responses, general tasksGemini Progemini-proComplex reasoning, longer content
Groq (Fast Inference)
ModelIDBest ForLlama 3.3 70Bllama-3.3-70b-versatileHigh quality, complex tasksLlama 3.1 8Bllama-3.1-8b-instantFast, simple tasksMixtral 8x7Bmixtral-8x7b-32768Long context, codingGemma 2 9Bgemma2-9b-itEfficient, balanced
OpenAI
ModelIDBest ForGPT-4ogpt-4oBest quality, multimodalGPT-4o Minigpt-4o-miniCost-effective, fastGPT-3.5 Turbogpt-3.5-turboBudget option

🛠️ Available Tools
ToolTrigger FieldDescriptionWeb ScraperurlExtracts text content from web pagesText CleanercontentNormalizes whitespace, cleans textRSS Readerrss_urlFetches articles from RSS feedsFile Readerfile_pathReads content from local filesJSON ParserManualParses JSON strings (for code use)
How Tools Work
Tools automatically preprocess input before sending to the LLM:
User Input → Tool Processing → Prompt Template → LLM → Output

Example: If you select "Web Scraper" and include a url field:

1. User enters a URL
2. Web Scraper fetches the page content
3. Content is added to the content field
4. LLM processes the full content


---

## **README.md - PART 3 of 4**

```markdown
---

## 📤 Output Formats

| Format | Display | Best For |
|--------|---------|----------|
| **Plain Text** | Pre-formatted text block | General responses |
| **JSON** | Formatted cards/items | Structured data, flashcards |
| **CSV** | HTML table | Tabular data, lists |
| **Markdown** | Rendered headings, bold, italic | Documentation, articles |
| **HTML** | Raw HTML rendered | Custom formatting |

---

## 📁 Project Structure


ai-agent-generator/
├── app.py                    # Main generator application
├── README.md                 # This file
├── templates/
│   └── index.html            # Generator web interface
├── static/
│   ├── css/
│   │   └── style.css         # Generator styles
│   └── js/
│       └── app.js            # Generator frontend logic
│
└── generated_agents/         # Created after first agent
├── config/
│   └── global_config.yaml    # API keys (edit this!)
├── core/
│   ├── init.py
│   ├── utils.py              # Utility functions
│   ├── input_validator.py    # Input validation
│   ├── llm_caller.py         # Multi-provider LLM client
│   └── tools/
│       ├── init.py
│       ├── web_scraper.py
│       ├── text_cleaner.py
│       ├── rss_reader.py
│       ├── file_reader.py
│       └── json_parser.py
└── agents/
└── your_agent_name/
├── init.py
├── agent.py          # Core agent logic
├── config.json       # Agent configuration
├── web_app.py        # Standalone web interface
├── run_cli.py        # Command-line interface
├── test_agent.py     # Unit tests
└── README.md         # Agent documentation

---

## ⚙️ Configuration

### Global Configuration

Edit `generated_agents/config/global_config.yaml`:

```yaml
# API Keys - Add your keys here
GOOGLE_API_KEY: "your-google-api-key"
GROQ_API_KEY: "your-groq-api-key"
OPENAI_API_KEY: "your-openai-api-key"

Agent Configuration
Each agent has a config.json:
jsonDownloadCopy code{
  "agent_name": "summarizer",
  "description": "Summarizes content",
  "model": {
    "id": "gemini-flash",
    "provider": "google",
    "role": "You are an expert summarizer...",
    "max_tokens": 1000,
    "temperature": 0.7
  },
  "required_fields": ["content", "length"],
  "prompt_template": "Summarize in {length} sentences:\n\n{content}",
  "tools": ["text_cleaner"],
  "output_format": "plain_text"
}

📝 Examples
Example 1: Flashcard Generator
Configuration:

* Name: flashcard_maker
* Model: Gemini Flash
* Role: You are an expert educator who creates clear, memorable flashcards.
* Fields: content, num_cards
* Template:

Create {num_cards} flashcard Q&A pairs from this content:

{content}

Return as JSON array: [{"question": "...", "answer": "..."}]


* Output: JSON

Usage:
Content: [Paste study material]
Num Cards: 10
→ Generates 10 Q&A flashcards


Example 2: Web Article Summarizer
Configuration:

* Name: article_summarizer
* Model: Llama 3.3 70B (Groq)
* Role: You summarize articles clearly and concisely.
* Fields: url, content
* Tools: ✅ Web Scraper, ✅ Text Cleaner
* Template:

Summarize this article in 3 bullet points:

{content}


* Output: Markdown

Usage:
URL: https://example.com/article
→ Scrapes page, summarizes content


Example 3: Email Writer
Configuration:

* Name: email_writer
* Model: GPT-4o Mini
* Fields: recipient, subject, tone, key_points
* Template:

Write a {tone} email to {recipient} about: {subject}

Key points:
{key_points}

Include appropriate greeting and signature.


* Output: Plain Text


---

## **README.md - PART 4 of 4**

```markdown
---

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'agents'` | Run from `generated_agents` folder, or check `sys.path` in web_app.py |
| `GOOGLE_API_KEY not set` | Edit `generated_agents/config/global_config.yaml` |
| `429 Too Many Requests` | You've hit API rate limits. Wait or use different provider |
| `Connection refused on port 5001` | Another agent is running. Stop it or change port |
| Fields not being added | Type fields, then press Enter (not just Tab) |
| Tools not working | Ensure field names match: `url`, `rss_url`, `file_path` |

### Checking Logs

```bash
# Run with debug output
python web_app.py

# Check terminal for error messages


⚠️ Limitations

1. Single-Turn Only: No conversation memory between requests
2. No Streaming: Full response returned at once (may feel slow)
3. Local Only: No built-in deployment to cloud
4. API Costs: You pay for API usage to your chosen provider
5. No Auth: Generated apps are open to anyone with the URL
6. Text Only: No image, audio, or video processing
7. 5 Tools Only: Cannot add custom tools without modifying code
8. Basic Error Handling: Limited retry logic for API failures


🚀 Future Improvements (Not Implemented)

*  Conversation memory / chat mode
*  Agent chaining (pipelines)
*  Custom tool creation UI
*  Response streaming
*  User authentication
*  Database storage
*  One-click cloud deployment
*  More LLM providers (Anthropic, Cohere, etc.)
*  Image input support


🤝 Contributing
Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request


📄 License
MIT License - Feel free to use, modify, and distribute.

🙏 Acknowledgments

* Flask - Web framework
* Google Gemini - LLM provider
* Groq - Fast inference
* OpenAI - LLM provider


Made with ❤️ for the AI community

---

## **How to Combine**

Copy in this order:
1. **Part 1** (from earlier) - starts with `# 🤖 Simple AI Agent Generator`
2. **Part 2** (above) - starts with `### 2. Create Project Structure`
3. **Part 3** (above) - starts with `## 📤 Output Formats`
4. **Part 4** (above) - starts with `## 🔧 Troubleshooting`

Save all as one file: `README.md`

---

## **Complete Sections in README**

| Section | Part |
|---------|------|
| Title, Overview, Features | Part 1 |
| What It Can/Cannot Do | Part 1 |
| Requirements | Part 1 |
| Installation (start) | Part 1 |
| Installation (finish) | Part 2 |
| Quick Start | Part 2 |
| Usage Guide | Part 2 |
| Supported LLM Providers | Part 2 |
| Available Tools | Part 2 |
| Output Formats | Part 3 |
| Project Structure | Part 3 |
| Configuration | Part 3 |
| Examples (3) | Part 3 |
| Troubleshooting | Part 4 |
| Limitations | Part 4 |
| Future Improvements | Part 4 |
| Contributing, License | Part 4 |

🎯
