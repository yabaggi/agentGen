<think>The user wants a README.md file for the agent generator app. This should be comprehensive and include:

1. Overview/Description of what the app does
2. Features
3. Demo/Screenshots (placeholder)
4. Tech stack
5. Installation instructions (local)
6. Deployment instructions (Vercel)
7. Usage guide
8. File structure
9. Configuration
10. API endpoints
11. Customization
12. Troubleshooting
13. Contributing
14. License

Let me create a professional, comprehensive README that covers all aspects of the agent generator app.</think># **README.md for Agent Generator App**

```markdown
# 🤖 AI Agent Generator

A powerful web application that lets you create custom AI agents with an intuitive UI. Generate ready-to-deploy AI agents in minutes without writing code!

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone)

## ✨ Features

- 🎯 **16+ Pre-built Templates** - Email writer, flashcard generator, translator, blog writer, and more
- 🔧 **Custom Agent Builder** - Create agents from scratch with a step-by-step wizard
- 🤖 **Multi-Model Support** - Gemini, GPT, Llama, Mixtral, and more
- 📋 **Smart Form Hints** - Built-in guidance for each input field
- 🎨 **Mobile-Friendly UI** - Responsive design for all devices
- 📦 **Instant Download** - Get your agent as a ready-to-run ZIP file
- 💾 **Copy & Paste Ready** - View and copy generated files directly in the browser
- 🚀 **Serverless Compatible** - Deploy on Vercel with zero configuration

## 🎬 Demo

![Agent Generator Demo](docs/demo.gif)

**Live Demo:** [https://your-agent-generator.vercel.app](https://your-agent-generator.vercel.app)

## 🏗️ Tech Stack

**Frontend:**
- Vanilla JavaScript (ES6+)
- CSS3 with custom animations
- Responsive design

**Backend:**
- Python 3.8+
- Flask
- PyYAML
- Requests

**Deployment:**
- Vercel (serverless)
- Works on any Python hosting platform

## 📦 Installation

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/agent-generator.git
   cd agent-generator
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   ```
   http://localhost:5000
   ```

### Requirements

Create a `requirements.txt` file:
```
Flask==3.0.0
PyYAML==6.0.1
requests==2.31.0
```

## 🚀 Deployment

### Deploy to Vercel

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Deploy:**
   ```bash
   vercel
   ```

3. **Configure:**
   - Framework Preset: `Other`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

### Deploy to Other Platforms

**Heroku:**
```bash
heroku create your-agent-generator
git push heroku main
```

**Railway:**
```bash
railway init
railway up
```

**PythonAnywhere / Replit:**
- Upload files
- Install requirements
- Run `app.py`

## 📖 Usage Guide

### Quick Start - Use a Template

1. **Select a template** from the pre-built options (Email, Flashcard, Translator, etc.)
2. **Click through the wizard** - all fields are pre-filled
3. **Review and generate** - preview files in the final step
4. **Download or copy** - get your agent as ZIP or copy individual files

### Custom Agent Creation

#### Step 1: Basic Info
- **Agent Name:** Unique identifier (e.g., `resume_analyzer`)
- **Description:** Brief description of what your agent does

#### Step 2: Model Configuration
- **Select Model:** Choose from Gemini, GPT, Llama, etc.
- **System Role:** Define the agent's persona (e.g., "You are an expert resume reviewer...")
- **Parameters:** Set max tokens and temperature

#### Step 3: Prompt & Fields
- **Required Fields:** Add input fields (e.g., `resume_text`, `job_description`)
- **Prompt Template:** Define the prompt with placeholders:
  ```
  Analyze this resume: {resume_text}
  
  For job role: {job_description}
  
  Provide: scores, strengths, weaknesses, and recommendations.
  ```

#### Step 4: Tools (Optional)
- Select helper tools: web scraper, text cleaner, PDF parser, etc.

#### Step 5: Output Format
- Choose: Plain Text, JSON, Markdown, HTML, CSV, etc.

#### Step 6: Review & Generate
- Preview all generated files
- Download as ZIP or copy individual files

### Running a Generated Agent

1. **Extract the ZIP file:**
   ```bash
   unzip my_agent.zip
   cd my_agent
   ```

2. **Install dependencies:**
   ```bash
   pip install flask pyyaml requests
   ```

3. **Add API key** in `config/keys.yaml`:
   ```yaml
   GEMINI_API_KEY: your_actual_key_here
   GROQ_API_KEY: your_actual_key_here
   OPENAI_API_KEY: your_actual_key_here
   ```

4. **Run the agent:**
   ```bash
   python web_app.py
   ```

5. **Open browser:**
   ```
   http://localhost:5001
   ```

## 📁 Project Structure

```
agent-generator/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── vercel.json                     # Vercel configuration (optional)
│
├── static/
│   ├── css/
│   │   └── style.css              # All styles
│   ├── js/
│   │   └── app.js                 # Frontend logic
│   └── data/
│       └── promptTemplates.json   # Agent templates
│
└── templates/
    └── index.html                 # Main UI template
```

### Generated Agent Structure

```
my_agent/
├── agent.py                       # Core agent logic
├── web_app.py                     # Web interface
├── config.json                    # Agent configuration
├── README.txt                     # Setup instructions
│
├── core/
│   ├── __init__.py
│   ├── llm_caller.py             # LLM API integration
│   ├── utils.py                  # Helper functions
│   └── tools/
│       └── __init__.py
│
└── config/
    └── keys.yaml                 # API keys (user adds)
```

## ⚙️ Configuration

### Adding New Templates

Edit `static/data/promptTemplates.json`:

```json
{
  "my_template": {
    "name": "🎯 My Custom Template",
    "agent_name": "my_custom_agent",
    "description": "What this agent does",
    "fields": ["field1", "field2"],
    "hints": {
      "field1": "Helpful hint for field1",
      "field2": "Helpful hint for field2"
    },
    "role": "You are an expert at...",
    "template": "Prompt with {field1} and {field2}",
    "output_format": "plain_text",
    "suggested_model": "gemini-flash",
    "tools": []
  }
}
```

### Supported Models

**Google Gemini:**
- `gemini-flash` - Fast, cost-effective
- `gemini-pro` - More capable

**Groq:**
- `llama-3.3-70b-versatile` - Large, powerful
- `llama-3.1-8b-instant` - Fast, efficient
- `mixtral-8x7b-32768` - Large context

**OpenAI:**
- `gpt-4o` - Most capable
- `gpt-4o-mini` - Balanced
- `gpt-3.5-turbo` - Fast, affordable

### Environment Variables

For deployment, you can set:

```bash
FLASK_ENV=production
PORT=5000
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main UI |
| `/api/templates` | GET | Get all templates |
| `/api/models` | GET | Get available models |
| `/api/tools` | GET | Get available tools |
| `/api/formats` | GET | Get output formats |
| `/api/quick/<template_id>` | GET | Generate from template |
| `/api/preview` | POST | Preview generated files |
| `/api/create` | POST | Create agent (returns files) |
| `/api/download/<agent_name>` | POST | Download as ZIP |

### Example API Usage

**Preview files:**
```javascript
fetch('/api/preview', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    agent_name: "my_agent",
    agent_description: "Test agent",
    model_id: "gemini-flash",
    model_role: "You are helpful",
    prompt_template: "Answer: {question}",
    required_fields: ["question"],
    field_hints: {"question": "Enter your question"},
    tools: [],
    output_format: "plain_text"
  })
})
```

## 🎨 Customization

### Styling

Edit `static/css/style.css` to customize:
- Color scheme
- Fonts
- Layout
- Animations

### UI Components

Edit `static/js/app.js` to modify:
- Form behavior
- Validation rules
- Preview display
- File structure

### Backend Logic

Edit `app.py` to add:
- New models
- Custom tools
- Additional validation
- File generation logic

## 🐛 Troubleshooting

### Common Issues

**1. "Read-only file system" error on Vercel**
- ✅ Fixed in latest version (no disk writes)
- Files are generated in memory

**2. API key errors**
- Check `config/keys.yaml` in generated agent
- Ensure key is valid and has credits
- Use correct key for selected model

**3. Template not loading**
- Verify `promptTemplates.json` is valid JSON
- Check browser console for errors
- Clear browser cache

**4. Generated agent won't run**
- Install all dependencies: `pip install flask pyyaml requests`
- Check Python version (3.8+)
- Verify API key is configured

**5. CORS errors**
- If deploying separately, configure CORS in `app.py`:
  ```python
  from flask_cors import CORS
  CORS(app)
  ```

### Debug Mode

Enable debug logging in generated agents:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork the repository**
2. **Create a feature branch:**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes:**
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push to the branch:**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Contribution Ideas

- 🎨 New agent templates
- 🔧 Additional tools
- 🌐 Internationalization
- 📱 Mobile app wrapper
- 🧪 Unit tests
- 📚 Documentation improvements

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 Acknowledgments

- Flask framework
- Google Gemini API
- Groq API
- OpenAI API
- All contributors

## 📧 Contact

- **Author:** Your Name
- **Email:** your.email@example.com
- **GitHub:** [@yourusername](https://github.com/yourusername)
- **Website:** [https://yourwebsite.com](https://yourwebsite.com)

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Agent marketplace
- [ ] Real-time collaboration
- [ ] Version control for agents
- [ ] Agent testing framework
- [ ] Analytics dashboard
- [ ] Team workspaces
- [ ] API key management UI

---

**⭐ If you find this project helpful, please give it a star!**

**🐛 Found a bug? [Open an issue](https://github.com/yourusername/agent-generator/issues)**

**💡 Have an idea? [Start a discussion](https://github.com/yourusername/agent-generator/discussions)**
```

---

## **Additional Files to Include**

### **LICENSE** (MIT License)

Create `LICENSE` file:

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### **.gitignore**

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Flask
instance/
.webassets-cache

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Generated agents (optional)
generated_agents/

# Environment
.env
.env.local

# Vercel
.vercel
```

### **vercel.json** (optional)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ]
}
```

---

This README provides comprehensive documentation for users, contributors, and developers! 🚀