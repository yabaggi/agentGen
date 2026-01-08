import os
import json
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, jsonify
import yaml

app = Flask(__name__)

# Configuration
BASE_DIR = Path(__file__).parent
GENERATED_DIR = BASE_DIR / "generated_agents"
CONFIG_DIR = GENERATED_DIR / "config"
CORE_DIR = GENERATED_DIR / "core"
TOOLS_DIR = CORE_DIR / "tools"

# Ensure directories exist
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(TOOLS_DIR, exist_ok=True)

# Global config template
GLOBAL_CONFIG_TEMPLATE = {
    "GOOGLE_API_KEY": "your-google-api-key",
    "GROQ_API_KEY": "your-groq-api-key",
    "OPENAI_API_KEY": "your-openai-api-key"
}

# Models configuration
AVAILABLE_MODELS = [
    {"id": "gemini-flash", "name": "Google Gemini Flash", "provider": "google"},
    {"id": "gemini-pro", "name": "Google Gemini Pro", "provider": "google"},
    {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B (Groq)", "provider": "groq"},
    {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B (Groq)", "provider": "groq"},
    {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B (Groq)", "provider": "groq"},
    {"id": "gemma2-9b-it", "name": "Gemma 2 9B (Groq)", "provider": "groq"},
    {"id": "gpt-4o", "name": "GPT-4o (OpenAI)", "provider": "openai"},
    {"id": "gpt-4o-mini", "name": "GPT-4o Mini (OpenAI)", "provider": "openai"},
    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo (OpenAI)", "provider": "openai"}
]

# Tools configuration
AVAILABLE_TOOLS = [
    {"id": "web_scraper", "name": "Web Scraper", "description": "Extracts text content from URLs"},
    {"id": "text_cleaner", "name": "Text Cleaner", "description": "Normalizes whitespace and cleans text"},
    {"id": "rss_reader", "name": "RSS Reader", "description": "Fetches and parses RSS feeds"},
    {"id": "file_reader", "name": "File Reader", "description": "Reads content from local files"},
    {"id": "json_parser", "name": "JSON Parser", "description": "Validates and parses JSON"}
]

# Output formats
OUTPUT_FORMATS = [
    {"id": "plain_text", "name": "Plain Text", "description": "Simple text output"},
    {"id": "json", "name": "JSON", "description": "Structured JSON data"},
    {"id": "csv", "name": "CSV", "description": "Comma-separated values"},
    {"id": "markdown", "name": "Markdown", "description": "Formatted markdown"},
    {"id": "html", "name": "HTML", "description": "HTML markup"}
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/models", methods=["GET"])
def get_models():
    return jsonify(AVAILABLE_MODELS)

@app.route("/api/tools", methods=["GET"])
def get_tools():
    return jsonify(AVAILABLE_TOOLS)

@app.route("/api/formats", methods=["GET"])
def get_formats():
    return jsonify(OUTPUT_FORMATS)

@app.route("/api/templates", methods=["GET"])
def get_templates():
    templates_file = os.path.join("static", "data", "promptTemplates.json")
    try:
        with open(templates_file, "r", encoding="utf-8") as f:
            templates = json.load(f)
        return jsonify(templates)
    except FileNotFoundError:
        return jsonify({})

@app.route("/api/preview", methods=["POST"])
def preview_agent():
    try:
        data = request.get_json()
        
        # Create config.json preview
        config = {
            "agent_name": data["agent_name"],
            "agent_description": data["agent_description"],
            "model": {
                "id": data["model_id"],
                "provider": next((m["provider"] for m in AVAILABLE_MODELS if m["id"] == data["model_id"]), "google"),
                "role": data["model_role"],
                "max_tokens": data.get("max_tokens", 1000),
                "temperature": data.get("temperature", 0.7)
            },
            "required_fields": data["required_fields"],
            "prompt_template": data["prompt_template"],
            "tools": data.get("tools", []),
            "output_format": data.get("output_format", "plain_text"),
            "created_at": datetime.now().isoformat()
        }
        
        preview_files = {
            "config.json": json.dumps(config, indent=2),
            "agent.py": generate_agent_py_preview(data),
            "README.md": generate_readme_preview(data)
        }
        
        return jsonify({"success": True, "files": preview_files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def generate_agent_py_preview(data):
    agent_class_name = data["agent_name"].title().replace("_", "")
    fields_dict = ", ".join([f'"{field}": "example_{field}"' for field in data["required_fields"]])
    
    return f'''#!/usr/bin/env python3
"""
Agent: {data["agent_name"]}
Generated on: {datetime.now().strftime("%Y-%m-%d")}
"""

import sys
import os
from pathlib import Path

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

from core.llm_caller import LLMCaller
from core.utils import load_agent_config

class {agent_class_name}Agent:
    def __init__(self):
        self.config = load_agent_config(__file__)
        self.llm = LLMCaller()
        
    def run(self, inputs):
        """Run the agent with provided inputs"""
        for field in self.config["required_fields"]:
            if field not in inputs:
                raise ValueError(f"Missing required field: {{field}}")
        
        prompt = self.generate_prompt(inputs)
        
        response = self.llm.call(
            model_id=self.config["model"]["id"],
            prompt=prompt,
            system_role=self.config["model"]["role"],
            max_tokens=self.config["model"]["max_tokens"],
            temperature=self.config["model"]["temperature"]
        )
        
        return response
    
    def generate_prompt(self, inputs):
        template = self.config["prompt_template"]
        for key, value in inputs.items():
            placeholder = "{{" + key + "}}"
            template = template.replace(placeholder, str(value))
        return template

if __name__ == "__main__":
    agent = {agent_class_name}Agent()
    example_inputs = {{{fields_dict}}}
    result = agent.run(example_inputs)
    print(result)
'''

def generate_readme_preview(data):
    tools_str = ", ".join(data.get("tools", [])) if data.get("tools") else "None"
    fields_list = "\n".join([f"- **{field}**" for field in data["required_fields"]])
    
    return f'''# {data["agent_name"].replace("_", " ").title()} Agent

## Description
{data["agent_description"] or "No description provided"}

## Configuration
- **Model**: {data["model_id"]}
- **Max Tokens**: {data.get("max_tokens", 1000)}
- **Temperature**: {data.get("temperature", 0.7)}
- **Tools**: {tools_str}
- **Output Format**: {data.get("output_format", "plain_text")}

## Required Inputs
{fields_list}

## Usage
```bash
cd generated_agents/agents/{data["agent_name"]}
python web_app.py 
Open http://localhost:5001 in your browser.
'''
@app.route("/api/create", methods=["POST"])
def create_agent():
    try:
        data = request.get_json()
        
        # Validate
        if not data.get("agent_name"):
            return jsonify({"success": False, "error": "Agent name is required"})
        
        # Create agent directory
        agent_dir = GENERATED_DIR / "agents" / data["agent_name"]
        if agent_dir.exists():
            return jsonify({"success": False, "error": f"Agent '{data['agent_name']}' already exists"})
        
        agent_dir.mkdir(parents=True)
        
        # Create global config if not exists
        global_config_path = CONFIG_DIR / "global_config.yaml"
        if not global_config_path.exists():
            with open(global_config_path, "w") as f:
                yaml.dump(GLOBAL_CONFIG_TEMPLATE, f, default_flow_style=False)
        
        # Create core files if not exist
        create_core_files()
        
        # Generate agent files
        generate_agent_files(data, agent_dir)
        
        return jsonify({
            "success": True,
            "path": str(agent_dir)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def generate_agent_files(data, agent_dir):
    """Generate all agent files"""
    
    # Create __init__.py
    (agent_dir / "__init__.py").touch()
    
    # Create config.json
    config = {
        "agent_name": data["agent_name"],
        "agent_description": data["agent_description"],
        "model": {
            "id": data["model_id"],
            "provider": next((m["provider"] for m in AVAILABLE_MODELS if m["id"] == data["model_id"]), "google"),
            "role": data["model_role"],
            "max_tokens": data.get("max_tokens", 1000),
            "temperature": data.get("temperature", 0.7)
        },
        "required_fields": data["required_fields"],
        "prompt_template": data["prompt_template"],
        "tools": data.get("tools", []),
        "output_format": data.get("output_format", "plain_text"),
        "created_at": datetime.now().isoformat()
    }
    
    with open(agent_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)

    # Create agent.py
    agent_class_name = data["agent_name"].title().replace("_", "")
    fields_dict = ", ".join([f'"{field}": "example_{field}"' for field in data["required_fields"]])
    
    agent_content = f'''#!/usr/bin/env python3
"""
Agent: {data["agent_name"]}
Description: {data["agent_description"]}
Generated on: {datetime.now().strftime("%Y-%m-%d")}
"""

import sys
import os
from pathlib import Path

# Add parent directories to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

from core.llm_caller import LLMCaller
from core.utils import load_agent_config

class {agent_class_name}Agent:
    def __init__(self):
        self.config = load_agent_config(__file__)
        self.llm = LLMCaller()
        
    def run(self, inputs):
        """Run the agent with provided inputs"""
        # Validate inputs
        for field in self.config["required_fields"]:
            if field not in inputs:
                raise ValueError(f"Missing required field: {{field}}")
        
        # Generate prompt
        prompt = self.generate_prompt(inputs)
        
        # Call LLM
        response = self.llm.call(
            model_id=self.config["model"]["id"],
            prompt=prompt,
            system_role=self.config["model"]["role"],
            max_tokens=self.config["model"]["max_tokens"],
            temperature=self.config["model"]["temperature"]
        )
        
        return response
    
    def generate_prompt(self, inputs):
        """Generate prompt from template and inputs"""
        template = self.config["prompt_template"]
        for key, value in inputs.items():
            placeholder = "{{" + key + "}}"
            template = template.replace(placeholder, str(value))
        return template

if __name__ == "__main__":
    agent = {agent_class_name}Agent()
    
    # Example usage
    print("Agent: {data['agent_name']}")
    print("-" * 40)
    
    # Example inputs
    example_inputs = {{{fields_dict}}}
    
    print("Running with example inputs:")
    for key, value in example_inputs.items():
        print(f"  {{key}}: {{value}}")
    
    print("\\nProcessing...")
    result = agent.run(example_inputs)
    print("\\nResult:")
    print(result)
'''
    
    with open(agent_dir / "agent.py", "w") as f:
        f.write(agent_content)

    # Create web_app.py
    form_fields_html = ""
    for field in data["required_fields"]:
        field_label = field.replace("_", " ").title()
        form_fields_html += f'''
        <div class="form-group">
            <label for="{field}">{field_label}</label>
            <textarea id="{field}" name="{field}" rows="3" required></textarea>
        </div>'''
    
    web_app_content = f'''#!/usr/bin/env python3
"""
Web Interface for {data["agent_name"]}
"""

from flask import Flask, render_template_string, request, jsonify
import sys
import os
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

from core.llm_caller import LLMCaller
from core.utils import load_agent_config

app = Flask(__name__)

config = load_agent_config(__file__)
llm = LLMCaller()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{{{ config['agent_name'].replace('_', ' ').title() }}}}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
               background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
               min-height: 100vh; padding: 2rem; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; 
                      border-radius: 12px; padding: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        h1 {{ color: #333; margin-bottom: 0.5rem; }}
        .description {{ color: #666; margin-bottom: 2rem; }}
        .form-group {{ margin-bottom: 1.5rem; }}
        label {{ display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; }}
        input, textarea {{ width: 100%; padding: 0.75rem; border: 2px solid #ddd; 
                          border-radius: 6px; font-size: 1rem; font-family: inherit; }}
        input:focus, textarea:focus {{ outline: none; border-color: #667eea; }}
        button {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                 color: white; padding: 0.75rem 2rem; border: none; 
                 border-radius: 6px; font-size: 1rem; cursor: pointer; 
                 font-weight: 600; transition: transform 0.2s; }}
        button:hover {{ transform: translateY(-2px); }}
        button:disabled {{ opacity: 0.6; cursor: not-allowed; }}
        #result {{ margin-top: 2rem; padding: 1.5rem; background: #f8f9fa; 
                  border-radius: 6px; border-left: 4px solid #667eea; display: none; }}
        #result.show {{ display: block; }}
        .loading {{ text-align: center; color: #667eea; font-weight: 600; }}
        pre {{ white-space: pre-wrap; word-wrap: break-word; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{{{{ config['agent_name'].replace('_', ' ').title() }}}}</h1>
        <p class="description">{{{{ config.get('agent_description', 'AI Agent') }}}}</p>
        <form id="agentForm">{form_fields_html}
            <button type="submit" id="submitBtn">Run Agent</button>
        </form>
        <div id="result"></div>
    </div>
    
    <script>
        document.getElementById('agentForm').onsubmit = async function(e) {{
            e.preventDefault();
            
            const formData = new FormData(this);
            const inputs = {{}};
            for (let [key, value] of formData.entries()) {{
                inputs[key] = value;
            }}
            
            const resultDiv = document.getElementById('result');
            const submitBtn = document.getElementById('submitBtn');
            
            resultDiv.innerHTML = '<p class="loading">Processing...</p>';
            resultDiv.classList.add('show');
            submitBtn.disabled = true;
            
            try {{
                const response = await fetch('/run', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(inputs)
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    resultDiv.innerHTML = '<h3>Result:</h3><pre>' + result.output + '</pre>';
                }} else {{
                    resultDiv.innerHTML = '<h3 style="color: red;">Error:</h3><p>' + result.error + '</p>';
                }}
            }} catch (error) {{
                resultDiv.innerHTML = '<h3 style="color: red;">Error:</h3><p>' + error.message + '</p>';
            }} finally {{
                submitBtn.disabled = false;
            }}
        }};
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, config=config)

@app.route("/run", methods=["POST"])
def run_agent():
    try:
        inputs = request.get_json()
        
        # Validate inputs
        for field in config["required_fields"]:
            if field not in inputs:
                return jsonify({{"success": False, "error": f"Missing field: {{field}}"}})
        
        # Generate prompt
        prompt = config["prompt_template"]
        for key, value in inputs.items():
            placeholder = "{{" + key + "}}"
            prompt = prompt.replace(placeholder, str(value))
        
        # Call LLM
        output = llm.call(
            model_id=config["model"]["id"],
            prompt=prompt,
            system_role=config["model"]["role"],
            max_tokens=config["model"]["max_tokens"],
            temperature=config["model"]["temperature"]
        )
        
        return jsonify({{"success": True, "output": output}})
    except Exception as e:
        return jsonify({{"success": False, "error": str(e)}})

if __name__ == "__main__":
    print(f"Starting {{config['agent_name']}} at http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=True)
'''
    
    with open(agent_dir / "web_app.py", "w") as f:
        f.write(web_app_content)

    # Create run_cli.py
    cli_content = f'''#!/usr/bin/env python3
"""
CLI Interface for {data["agent_name"]}
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent.parent))

from core.llm_caller import LLMCaller
from core.utils import load_agent_config

config = load_agent_config(__file__)
llm = LLMCaller()

def main():
    print("=" * 50)
    print(f"Agent: {{config['agent_name']}}")
    print("=" * 50)
    print()
    
    inputs = {{}}
    for field in config["required_fields"]:
        value = input(f"Enter {{field.replace('_', ' ')}}: ")
        inputs[field] = value
    
    print("\\nProcessing...")
    
    # Generate prompt
    prompt = config["prompt_template"]
    for key, value in inputs.items():
        placeholder = "{{" + key + "}}"
        prompt = prompt.replace(placeholder, str(value))
    
    # Call LLM
    output = llm.call(
        model_id=config["model"]["id"],
        prompt=prompt,
        system_role=config["model"]["role"],
        max_tokens=config["model"]["max_tokens"],
        temperature=config["model"]["temperature"]
    )
    
    print("\\n" + "=" * 50)
    print("Result:")
    print("=" * 50)
    print(output)

if __name__ == "__main__":
    main()
'''
    
    with open(agent_dir / "run_cli.py", "w") as f:
        f.write(cli_content)
    
    # Create README.md
    tools_str = ", ".join(data.get("tools", [])) if data.get("tools") else "None"
    fields_list = "\n".join([f"- **{field}**" for field in data["required_fields"]])
    
    readme_content = f'''# {data["agent_name"].replace("_", " ").title()} Agent

## Description
{data["agent_description"] or "No description provided"}

## Configuration
- **Model**: {data["model_id"]}
- **Max Tokens**: {data.get("max_tokens", 1000)}
- **Temperature**: {data.get("temperature", 0.7)}
- **Tools**: {tools_str}
- **Output Format**: {data.get("output_format", "plain_text")}

## Required Inputs
{fields_list}

## Installation

Make sure you have the required dependencies:

```bash
pip install flask pyyaml requests google-generativeai groq openai
Configure your API keys in generated_agents/config/global_config.yaml:
Generated Files
config.json - Agent configuration
agent.py - Core agent class
web_app.py - Web interface
run_cli.py - Command-line interface
README.md - This file
Generated by AI Agent Generator
'''
def create_core_files():
    """Create core utility files if they don't exist"""
    
    if not CORE_DIR.exists():
        CORE_DIR.mkdir(parents=True)
    
    # Create __init__.py
    (CORE_DIR / "__init__.py").touch()
    (TOOLS_DIR / "__init__.py").touch()
    
    # Create llm_caller.py
    llm_caller_content = '''"""LLM Caller - handles all LLM API calls"""

import os
import yaml
from pathlib import Path

class LLMCaller:
    def __init__(self):
        self.config = self.load_config()
        
    def load_config(self):
        config_path = Path(__file__).parent.parent / "config" / "global_config.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def call(self, model_id, prompt, system_role="", max_tokens=1000, temperature=0.7):
        """Call the appropriate LLM based on model_id"""
        
        if model_id.startswith("gemini"):
            return self.call_google(model_id, prompt, system_role, max_tokens, temperature)
        elif model_id.startswith("gpt"):
            return self.call_openai(model_id, prompt, system_role, max_tokens, temperature)
        else:
            return self.call_groq(model_id, prompt, system_role, max_tokens, temperature)
    
    def call_google(self, model_id, prompt, system_role, max_tokens, temperature):
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.config.get("GOOGLE_API_KEY"))
            
            model_name = "gemini-1.5-flash" if "flash" in model_id else "gemini-1.5-pro"
            model = genai.GenerativeModel(model_name)
            
            full_prompt = f"{system_role}\\n\\n{prompt}" if system_role else prompt
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error calling Google AI: {str(e)}"
    
    def call_openai(self, model_id, prompt, system_role, max_tokens, temperature):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.config.get("OPENAI_API_KEY"))
            
            messages = []
            if system_role:
                messages.append({"role": "system", "content": system_role})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"
    
    def call_groq(self, model_id, prompt, system_role, max_tokens, temperature):
        try:
            from groq import Groq
            client = Groq(api_key=self.config.get("GROQ_API_KEY"))
            
            messages = []
            if system_role:
                messages.append({"role": "system", "content": system_role})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling Groq: {str(e)}"
'''
    
    with open(CORE_DIR / "llm_caller.py", "w") as f:
        f.write(llm_caller_content)
    # Create utils.py
    utils_content = '''"""Utility functions"""

import json
import yaml
from pathlib import Path

def load_global_config():
    """Load global configuration"""
    config_path = Path(__file__).parent.parent / "config" / "global_config.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

def load_agent_config(agent_file):
    """Load agent configuration from config.json"""
    agent_dir = Path(agent_file).parent
    config_path = agent_dir / "config.json"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    
    raise FileNotFoundError(f"Config file not found: {config_path}")
'''
    
    with open(CORE_DIR / "utils.py", "w") as f:
        f.write(utils_content)

if __name__ == "__main__":
    print("🤖 AI Agent Generator")
    print("=" * 50)
    print("Starting server at http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=True)
