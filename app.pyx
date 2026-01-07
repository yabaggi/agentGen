#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
import os
import json
import re

app = Flask(__name__)
BASE_OUTPUT_DIR = "generated_agents"

AVAILABLE_TOOLS = {
    "rss_reader": {
        "name": "RSS Reader",
        "description": "Fetch and parse RSS feeds",
        "import_statement": "from core.tools.rss_reader import fetch_rss",
        "code": "import feedparser\n\ndef fetch_rss(url, limit=5):\n    feed = feedparser.parse(url)\n    return [{'title': e.title, 'content': getattr(e, 'summary', '')} for e in feed.entries[:limit]]\n"
    },
    "web_scraper": {
        "name": "Web Scraper",
        "description": "Scrape content from web pages",
        "import_statement": "from core.tools.web_scraper import scrape_url",
        "code": "import requests\nfrom bs4 import BeautifulSoup\n\ndef scrape_url(url):\n    resp = requests.get(url, timeout=10)\n    soup = BeautifulSoup(resp.text, 'html.parser')\n    for s in soup(['script', 'style']): s.decompose()\n    return soup.get_text(separator=' ', strip=True)\n"
    },
    "text_cleaner": {
        "name": "Text Cleaner",
        "description": "Clean and normalize text",
        "import_statement": "from core.tools.text_cleaner import clean_text",
        "code": "import re\n\ndef clean_text(text):\n    return re.sub(r'\\s+', ' ', text).strip()\n"
    },
    "file_reader": {
        "name": "File Reader",
        "description": "Read content from files",
        "import_statement": "from core.tools.file_reader import read_file",
        "code": "def read_file(filepath):\n    with open(filepath, 'r', encoding='utf-8') as f:\n        return f.read()\n"
    },
    "json_parser": {
        "name": "JSON Parser",
        "description": "Parse and validate JSON",
        "import_statement": "from core.tools.json_parser import parse_json",
        "code": "import json\n\ndef parse_json(text):\n    try:\n        return json.loads(text)\n    except json.JSONDecodeError as e:\n        return {'error': str(e)}\n"
    }
}

OUTPUT_FORMATS = {
    "plain_text": {"name": "Plain Text", "description": "Simple text output"},
    "csv": {"name": "CSV", "description": "Comma-separated values"},
    "json": {"name": "JSON", "description": "JSON formatted output"},
    "markdown": {"name": "Markdown", "description": "Markdown formatted output"},
    "html": {"name": "HTML", "description": "HTML formatted output"}
}

LLM_MODELS = [
    {"id": "gemini-flash", "name": "Gemini Flash (Google)", "provider": "google"},
    {"id": "gemini-pro", "name": "Gemini Pro (Google)", "provider": "google"},
    {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B (Groq)", "provider": "groq"},
    {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B Instant (Groq)", "provider": "groq"},
    {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B (Groq)", "provider": "groq"},
    {"id": "gemma2-9b-it", "name": "Gemma 2 9B (Groq)", "provider": "groq"},
    {"id": "gpt-4o", "name": "GPT-4o (OpenAI)", "provider": "openai"},
    {"id": "gpt-4o-mini", "name": "GPT-4o Mini (OpenAI)", "provider": "openai"},
    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo (OpenAI)", "provider": "openai"},
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tools", methods=["GET"])
def get_tools():
    tools = [{"id": k, "name": v["name"], "description": v["description"]} for k, v in AVAILABLE_TOOLS.items()]
    return jsonify(tools)


@app.route("/api/formats", methods=["GET"])
def get_formats():
    formats = [{"id": k, "name": v["name"], "description": v["description"]} for k, v in OUTPUT_FORMATS.items()]
    return jsonify(formats)


@app.route("/api/models", methods=["GET"])
def get_models():
    return jsonify(LLM_MODELS)


@app.route("/api/preview", methods=["POST"])
def preview_agent():
    data = request.json
    files = generate_agent_files(data, preview=True)
    return jsonify({"success": True, "files": files})


@app.route("/api/create", methods=["POST"])
def create_agent():
    data = request.json
    agent_name = data.get("agent_name", "").strip()
    if not agent_name:
        return jsonify({"success": False, "error": "Agent name is required"}), 400
    agent_name = re.sub(r"[^a-zA-Z0-9_]", "_", agent_name).lower()
    try:
        result = generate_agent_files(data, preview=False)
        return jsonify({"success": True, "message": "Agent created!", "path": result["path"], "files": result["files"]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
def generate_agent_files(data, preview=True):
    agent_name = re.sub(r"[^a-zA-Z0-9_]", "_", data.get("agent_name", "my_agent")).lower()
    agent_description = data.get("agent_description", "")
    model_id = data.get("model_id", "gemini-flash")
    model_role = data.get("model_role", "You are a helpful assistant.")
    prompt_template = data.get("prompt_template", "{input}")
    required_fields = data.get("required_fields", ["input"])
    selected_tools = data.get("tools", [])
    output_format = data.get("output_format", "plain_text")
    max_tokens = data.get("max_tokens", 500)
    temperature = data.get("temperature", 0.7)

    # Find provider for selected model
    provider = "google"
    for m in LLM_MODELS:
        if m["id"] == model_id:
            provider = m["provider"]
            break

    if isinstance(required_fields, str):
        required_fields = [f.strip() for f in required_fields.split(",") if f.strip()]

    files = {}

    config = {
        "agent_name": agent_name,
        "description": agent_description,
        "model": {
            "id": model_id,
            "provider": provider,
            "role": model_role,
            "max_tokens": max_tokens,
            "temperature": temperature
        },
        "required_fields": required_fields,
        "prompt_template": prompt_template,
        "tools": selected_tools,
        "output_format": output_format
    }
    files["config.json"] = json.dumps(config, indent=2)

    tool_imports = "\n".join([AVAILABLE_TOOLS[t]["import_statement"] for t in selected_tools if t in AVAILABLE_TOOLS])
    if not tool_imports:
        tool_imports = "# No additional tools"

    test_dict = ", ".join(['"{0}": "test"'.format(f) for f in required_fields])

    agent_py = '#!/usr/bin/env python3\n'
    agent_py += 'import sys\nimport os\n'
    agent_py += 'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))\n\n'
    agent_py += 'from core.input_validator import validate_input\n'
    agent_py += 'from core.llm_caller import call_llm\n'
    agent_py += 'from core.utils import load_agent_config\n'
    agent_py += tool_imports + '\n\n'
    agent_py += 'class Agent:\n'
    agent_py += '    def __init__(self):\n'
    agent_py += '        self.config = load_agent_config("{}")\n'.format(agent_name)
    agent_py += '        self.required_fields = self.config.get("required_fields", [])\n'
    agent_py += '        self.prompt_template = self.config.get("prompt_template", "{input}")\n'
    agent_py += '        self.model_config = self.config.get("model", {})\n'
    agent_py += '        self.model_id = self.model_config.get("id", "gemini-flash")\n'
    agent_py += '        self.provider = self.model_config.get("provider", "google")\n'
    agent_py += '        self.max_tokens = self.model_config.get("max_tokens", 500)\n'
    agent_py += '        self.temperature = self.model_config.get("temperature", 0.7)\n'
    agent_py += '        self.system_role = self.model_config.get("role", "You are a helpful assistant.")\n\n'
    agent_py += '    def run(self, user_input):\n'
    agent_py += '        validated = validate_input(user_input, self.required_fields)\n'
    agent_py += '        prompt = self.prompt_template.format(**validated)\n'
    agent_py += '        raw_output = call_llm(\n'
    agent_py += '            prompt=prompt,\n'
    agent_py += '            system_role=self.system_role,\n'
    agent_py += '            model_id=self.model_id,\n'
    agent_py += '            provider=self.provider,\n'
    agent_py += '            max_tokens=self.max_tokens,\n'
    agent_py += '            temperature=self.temperature\n'
    agent_py += '        )\n'
    agent_py += '        return raw_output.strip()\n\n'
    agent_py += 'if __name__ == "__main__":\n'
    agent_py += '    agent = Agent()\n'
    agent_py += '    test_input = {' + test_dict + '}\n'
    agent_py += '    print("Running agent...")\n'
    agent_py += '    try:\n'
    agent_py += '        result = agent.run(test_input)\n'
    agent_py += '        print("Output:", result)\n'
    agent_py += '    except Exception as e:\n'
    agent_py += '        print("Error:", e)\n'

    files["agent.py"] = agent_py
    files["__init__.py"] = 'from .agent import Agent\n'

    readme = "# " + agent_name.replace("_", " ").title() + " Agent\n\n"
    readme += agent_description + "\n\n"
    readme += "## Configuration\n"
    readme += "- Model: " + model_id + " (" + provider + ")\n"
    readme += "- Output: " + output_format + "\n"
    readme += "- Tools: " + (", ".join(selected_tools) if selected_tools else "None") + "\n\n"
    readme += "## Required Fields\n"
    for f in required_fields:
        readme += "- " + f + "\n"
    readme += "\n## How to Run\n"
    readme += "```bash\ncd generated_agents/agents/" + agent_name + "\npython web_app.py\n# Open http://localhost:5001\n```\n"

    files["README.md"] = readme

    test_py = '#!/usr/bin/env python3\n'
    test_py += 'import unittest\nimport sys\nimport os\n'
    test_py += 'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))\n'
    test_py += 'from agents.{}.agent import Agent\n\n'.format(agent_name)
    test_py += 'class TestAgent(unittest.TestCase):\n'
    test_py += '    def setUp(self):\n'
    test_py += '        self.agent = Agent()\n\n'
    test_py += '    def test_config_loaded(self):\n'
    test_py += '        self.assertIsNotNone(self.agent.config)\n\n'
    test_py += 'if __name__ == "__main__":\n'
    test_py += '    unittest.main()\n'

    files["test_agent.py"] = test_py
    files["web_app.py"] = generate_web_app(agent_name, agent_description, required_fields, output_format)
    files["run_cli.py"] = generate_cli_app(agent_name, required_fields)

    if not preview:
        agent_dir = os.path.join(BASE_OUTPUT_DIR, "agents", agent_name)
        os.makedirs(agent_dir, exist_ok=True)
        for filename, content in files.items():
            with open(os.path.join(agent_dir, filename), "w", encoding="utf-8") as f:
                f.write(content)
        ensure_core_files_exist()
        return {"path": agent_dir, "files": files}

    return files
def generate_web_app(agent_name, description, required_fields, output_format):
    title = agent_name.replace("_", " ").title()
    
    input_fields_html = ""
    for field in required_fields:
        field_label = field.replace("_", " ").title()
        if field in ["content", "text", "input", "description", "body", "message"]:
            input_fields_html += '            <div class="form-group">\n'
            input_fields_html += '                <label>{}</label>\n'.format(field_label)
            input_fields_html += '                <textarea id="{}" placeholder="Enter {}..."></textarea>\n'.format(field, field_label.lower())
            input_fields_html += '            </div>\n'
        elif field in ["num", "number", "count", "num_cards", "num_items", "limit"]:
            input_fields_html += '            <div class="form-group">\n'
            input_fields_html += '                <label>{}</label>\n'.format(field_label)
            input_fields_html += '                <input type="number" id="{}" value="5" min="1" max="50">\n'.format(field)
            input_fields_html += '            </div>\n'
        elif field in ["url", "link", "website"]:
            input_fields_html += '            <div class="form-group">\n'
            input_fields_html += '                <label>{}</label>\n'.format(field_label)
            input_fields_html += '                <input type="url" id="{}" placeholder="https://...">\n'.format(field)
            input_fields_html += '            </div>\n'
        else:
            input_fields_html += '            <div class="form-group">\n'
            input_fields_html += '                <label>{}</label>\n'.format(field_label)
            input_fields_html += '                <input type="text" id="{}" placeholder="Enter {}...">\n'.format(field, field_label.lower())
            input_fields_html += '            </div>\n'

    collect_inputs_js = "{\n"
    for field in required_fields:
        collect_inputs_js += '                    "{}": document.getElementById("{}").value,\n'.format(field, field)
    collect_inputs_js += "                }"

    if output_format == "json":
        display_fn = 'function displayOutput(r){const o=document.getElementById("output");try{const d=JSON.parse(r);let h="<div>";if(Array.isArray(d)){d.forEach((item,i)=>{h+="<div class=\\"item\\"><div class=\\"item-header\\">Item "+(i+1)+"</div>";for(const[k,v]of Object.entries(item)){h+="<div><strong>"+k+":</strong> "+v+"</div>";}h+="</div>";});}else{for(const[k,v]of Object.entries(d)){h+="<div><strong>"+k+":</strong> "+v+"</div>";}}h+="</div>";o.innerHTML=h;}catch(e){o.innerHTML="<pre>"+r+"</pre>";}}'
    elif output_format == "csv":
        display_fn = 'function displayOutput(r){const o=document.getElementById("output");const lines=r.trim().split("\\n");let h="<table class=\\"csv-table\\"><thead><tr>";lines[0].split(",").forEach(x=>{h+="<th>"+x.trim()+"</th>";});h+="</tr></thead><tbody>";for(let i=1;i<lines.length;i++){h+="<tr>";lines[i].split(",").forEach(c=>{h+="<td>"+c.trim()+"</td>";});h+="</tr>";}h+="</tbody></table>";o.innerHTML=h;}'
    elif output_format == "markdown":
        display_fn = 'function displayOutput(r){const o=document.getElementById("output");let h=r.replace(/^### (.*$)/gim,"<h3>$1</h3>").replace(/^## (.*$)/gim,"<h2>$1</h2>").replace(/^# (.*$)/gim,"<h1>$1</h1>").replace(/\\*\\*(.*?)\\*\\*/g,"<strong>$1</strong>").replace(/\\*(.*?)\\*/g,"<em>$1</em>").replace(/\\n/g,"<br>");o.innerHTML="<div>"+h+"</div>";}'
    elif output_format == "html":
        display_fn = 'function displayOutput(r){document.getElementById("output").innerHTML=r;}'
    else:
        display_fn = 'function displayOutput(r){document.getElementById("output").innerHTML="<pre>"+r+"</pre>";}'

    web_app = '#!/usr/bin/env python3\n'
    web_app += '"""Web interface for {} - Auto-generated"""\n'.format(title)
    web_app += 'from flask import Flask, render_template_string, request, jsonify\n'
    web_app += 'import sys\nimport os\n\n'
    web_app += 'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))\n'
    web_app += 'from agents.{}.agent import Agent\n\n'.format(agent_name)
    web_app += 'app = Flask(__name__)\n'
    web_app += 'agent = Agent()\n\n'
    web_app += 'HTML = """<!DOCTYPE html>\n'
    web_app += '<html><head><title>{}</title>\n'.format(title)
    web_app += '<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'
    web_app += '<style>\n'
    web_app += '*{margin:0;padding:0;box-sizing:border-box;}\n'
    web_app += 'body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:linear-gradient(135deg,#0f172a,#1e293b);color:#f8fafc;min-height:100vh;padding:2rem;}\n'
    web_app += '.container{max-width:900px;margin:0 auto;}\n'
    web_app += 'header{text-align:center;margin-bottom:2rem;}\n'
    web_app += 'h1{color:#818cf8;font-size:2rem;margin-bottom:0.5rem;}\n'
    web_app += '.desc{color:#94a3b8;}\n'
    web_app += '.card{background:rgba(30,41,59,0.8);border-radius:12px;padding:1.5rem;margin-bottom:1.5rem;border:1px solid #334155;}\n'
    web_app += '.form-group{margin-bottom:1rem;}\n'
    web_app += 'label{display:block;margin-bottom:0.5rem;font-weight:500;color:#e2e8f0;}\n'
    web_app += 'textarea,input{width:100%;padding:0.75rem;background:#0f172a;border:1px solid #334155;border-radius:8px;color:#f8fafc;font-size:1rem;}\n'
    web_app += 'textarea{min-height:150px;resize:vertical;}\n'
    web_app += 'textarea:focus,input:focus{border-color:#6366f1;outline:none;}\n'
    web_app += 'button{width:100%;padding:1rem;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;border:none;border-radius:8px;font-size:1rem;font-weight:600;cursor:pointer;}\n'
    web_app += 'button:hover{opacity:0.9;}\n'
    web_app += 'button:disabled{opacity:0.5;cursor:not-allowed;}\n'
    web_app += '#output{min-height:100px;padding:1rem;background:#0f172a;border-radius:8px;border:1px solid #334155;}\n'
    web_app += '.item{background:#1e293b;padding:1rem;border-radius:8px;margin-bottom:0.5rem;border-left:3px solid #6366f1;}\n'
    web_app += '.item-header{font-weight:600;color:#818cf8;margin-bottom:0.5rem;}\n'
    web_app += '.csv-table{width:100%;border-collapse:collapse;}\n'
    web_app += '.csv-table th,.csv-table td{padding:0.5rem;border:1px solid #334155;text-align:left;}\n'
    web_app += '.csv-table th{background:#1e293b;color:#818cf8;}\n'
    web_app += 'pre{white-space:pre-wrap;word-wrap:break-word;}\n'
    web_app += '.error{color:#ef4444;}\n'
    web_app += '</style></head>\n'
    web_app += '<body><div class="container">\n'
    web_app += '<header><h1>{}</h1><p class="desc">{}</p></header>\n'.format(title, description)
    web_app += '<div class="card"><form id="agentForm" onsubmit="return false;">\n'
    web_app += input_fields_html
    web_app += '<button type="button" onclick="runAgent()">Generate</button>\n'
    web_app += '</form></div>\n'
    web_app += '<div class="card"><h3 style="margin-bottom:1rem;color:#818cf8;">Output</h3>\n'
    web_app += '<div id="output"><p style="color:#64748b;">Results will appear here...</p></div></div>\n'
    web_app += '</div>\n'
    web_app += '<script>\n'
    web_app += 'async function runAgent(){\n'
    web_app += 'const btn=document.querySelector("button");const output=document.getElementById("output");\n'
    web_app += 'btn.disabled=true;btn.textContent="Processing...";\n'
    web_app += 'output.innerHTML="<p>Generating...</p>";\n'
    web_app += 'try{\n'
    web_app += 'const resp=await fetch("/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(' + collect_inputs_js + ')});\n'
    web_app += 'const data=await resp.json();\n'
    web_app += 'if(data.success){displayOutput(data.result);}else{output.innerHTML="<p class=\\"error\\">Error: "+data.error+"</p>";}\n'
    web_app += '}catch(e){output.innerHTML="<p class=\\"error\\">Error: "+e.message+"</p>";}\n'
    web_app += 'btn.disabled=false;btn.textContent="Generate";}\n'
    web_app += display_fn + '\n'
    web_app += '</script></body></html>"""\n\n'
    web_app += '@app.route("/")\n'
    web_app += 'def index():\n'
    web_app += '    return render_template_string(HTML)\n\n'
    web_app += '@app.route("/run", methods=["POST"])\n'
    web_app += 'def run():\n'
    web_app += '    try:\n'
    web_app += '        data = request.json\n'
    web_app += '        result = agent.run(data)\n'
    web_app += '        return jsonify({"success": True, "result": result})\n'
    web_app += '    except Exception as e:\n'
    web_app += '        return jsonify({"success": False, "error": str(e)})\n\n'
    web_app += 'if __name__ == "__main__":\n'
    web_app += '    print("=" * 50)\n'
    web_app += '    print("{}")\n'.format(title)
    web_app += '    print("Open http://localhost:5001")\n'
    web_app += '    print("=" * 50)\n'
    web_app += '    app.run(debug=True, port=5001)\n'

    return web_app


def generate_cli_app(agent_name, required_fields):
    title = agent_name.replace("_", " ").title()
    
    input_prompts = ""
    input_dict_items = ""
    for field in required_fields:
        field_label = field.replace("_", " ").title()
        if field in ["content", "text", "input", "description", "body", "message"]:
            input_prompts += '    print("Enter {} (press Enter twice when done):")\n'.format(field_label)
            input_prompts += '    lines = []\n'
            input_prompts += '    while True:\n'
            input_prompts += '        line = input()\n'
            input_prompts += '        if line == "": break\n'
            input_prompts += '        lines.append(line)\n'
            input_prompts += '    {} = "\\n".join(lines)\n\n'.format(field)
        else:
            input_prompts += '    {} = input("Enter {}: ")\n\n'.format(field, field_label)
        input_dict_items += '        "{}": {},\n'.format(field, field)

    cli_app = '#!/usr/bin/env python3\n'
    cli_app += '"""CLI for {} - Auto-generated"""\n'.format(title)
    cli_app += 'import sys\nimport os\n'
    cli_app += 'sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))\n'
    cli_app += 'from agents.{}.agent import Agent\n\n'.format(agent_name)
    cli_app += 'def main():\n'
    cli_app += '    agent = Agent()\n'
    cli_app += '    print("=" * 50)\n'
    cli_app += '    print("{}")\n'.format(title)
    cli_app += '    print("=" * 50)\n'
    cli_app += '    print()\n\n'
    cli_app += input_prompts
    cli_app += '    print("\\nProcessing...")\n'
    cli_app += '    print("-" * 50)\n\n'
    cli_app += '    try:\n'
    cli_app += '        result = agent.run({\n'
    cli_app += input_dict_items
    cli_app += '        })\n'
    cli_app += '        print("\\nResult:\\n")\n'
    cli_app += '        print(result)\n'
    cli_app += '    except Exception as e:\n'
    cli_app += '        print("Error:", e)\n\n'
    cli_app += 'if __name__ == "__main__":\n'
    cli_app += '    main()\n'

    return cli_app
def ensure_core_files_exist():
    core_dir = os.path.join(BASE_OUTPUT_DIR, "core")
    tools_dir = os.path.join(core_dir, "tools")
    config_dir = os.path.join(BASE_OUTPUT_DIR, "config")
    agents_dir = os.path.join(BASE_OUTPUT_DIR, "agents")

    for d in [core_dir, tools_dir, config_dir, agents_dir]:
        os.makedirs(d, exist_ok=True)

    for d in [core_dir, tools_dir, agents_dir]:
        init_file = os.path.join(d, "__init__.py")
        if not os.path.exists(init_file):
            open(init_file, "w").close()

    utils_file = os.path.join(core_dir, "utils.py")
    if not os.path.exists(utils_file):
        with open(utils_file, "w") as f:
            f.write('import yaml\nimport json\nimport os\n\n')
            f.write('BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n\n')
            f.write('def load_global_config():\n')
            f.write('    with open(os.path.join(BASE_DIR, "config", "global_config.yaml"), "r") as f:\n')
            f.write('        return yaml.safe_load(f)\n\n')
            f.write('def load_agent_config(agent_name):\n')
            f.write('    with open(os.path.join(BASE_DIR, "agents", agent_name, "config.json"), "r") as f:\n')
            f.write('        return json.load(f)\n')

    validator_file = os.path.join(core_dir, "input_validator.py")
    if not os.path.exists(validator_file):
        with open(validator_file, "w") as f:
            f.write('def validate_input(user_input, required_fields):\n')
            f.write('    missing = [f for f in required_fields if f not in user_input]\n')
            f.write('    if missing:\n')
            f.write('        raise ValueError("Missing required fields: " + ", ".join(missing))\n')
            f.write('    return user_input\n')

    # Multi-provider LLM caller
    llm_file = os.path.join(core_dir, "llm_caller.py")
    with open(llm_file, "w") as f:
        f.write('import requests\n')
        f.write('from core.utils import load_global_config\n\n')
        f.write('CONFIG = load_global_config()\n\n')
        f.write('def call_llm(prompt, system_role="You are a helpful assistant.", model_id="gemini-flash", provider="google", max_tokens=500, temperature=0.7):\n')
        f.write('    if provider == "google":\n')
        f.write('        return call_google(prompt, system_role, model_id, max_tokens, temperature)\n')
        f.write('    elif provider == "groq":\n')
        f.write('        return call_groq(prompt, system_role, model_id, max_tokens, temperature)\n')
        f.write('    elif provider == "openai":\n')
        f.write('        return call_openai(prompt, system_role, model_id, max_tokens, temperature)\n')
        f.write('    else:\n')
        f.write('        raise ValueError(f"Unknown provider: {provider}")\n\n')
        f.write('def call_google(prompt, system_role, model_id, max_tokens, temperature):\n')
        f.write('    api_key = CONFIG.get("GOOGLE_API_KEY", "")\n')
        f.write('    if not api_key:\n')
        f.write('        raise ValueError("GOOGLE_API_KEY not set in config")\n')
        f.write('    \n')
        f.write('    model_name = "gemini-1.5-flash-latest" if "flash" in model_id else "gemini-1.5-pro-latest"\n')
        f.write('    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"\n')
        f.write('    \n')
        f.write('    payload = {\n')
        f.write('        "contents": [{"parts": [{"text": f"{system_role}\\n\\n{prompt}"}]}],\n')
        f.write('        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature}\n')
        f.write('    }\n')
        f.write('    \n')
        f.write('    response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})\n')
        f.write('    response.raise_for_status()\n')
        f.write('    data = response.json()\n')
        f.write('    \n')
        f.write('    return data["candidates"][0]["content"]["parts"][0]["text"]\n\n')
        f.write('def call_groq(prompt, system_role, model_id, max_tokens, temperature):\n')
        f.write('    api_key = CONFIG.get("GROQ_API_KEY", "")\n')
        f.write('    if not api_key:\n')
        f.write('        raise ValueError("GROQ_API_KEY not set in config")\n')
        f.write('    \n')
        f.write('    url = "https://api.groq.com/openai/v1/chat/completions"\n')
        f.write('    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}\n')
        f.write('    \n')
        f.write('    payload = {\n')
        f.write('        "model": model_id,\n')
        f.write('        "messages": [\n')
        f.write('            {"role": "system", "content": system_role},\n')
        f.write('            {"role": "user", "content": prompt}\n')
        f.write('        ],\n')
        f.write('        "max_tokens": max_tokens,\n')
        f.write('        "temperature": temperature\n')
        f.write('    }\n')
        f.write('    \n')
        f.write('    response = requests.post(url, json=payload, headers=headers)\n')
        f.write('    response.raise_for_status()\n')
        f.write('    data = response.json()\n')
        f.write('    \n')
        f.write('    return data["choices"][0]["message"]["content"]\n\n')
        f.write('def call_openai(prompt, system_role, model_id, max_tokens, temperature):\n')
        f.write('    api_key = CONFIG.get("OPENAI_API_KEY", "")\n')
        f.write('    if not api_key:\n')
        f.write('        raise ValueError("OPENAI_API_KEY not set in config")\n')
        f.write('    \n')
        f.write('    url = "https://api.openai.com/v1/chat/completions"\n')
        f.write('    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}\n')
        f.write('    \n')
        f.write('    payload = {\n')
        f.write('        "model": model_id,\n')
        f.write('        "messages": [\n')
        f.write('            {"role": "system", "content": system_role},\n')
        f.write('            {"role": "user", "content": prompt}\n')
        f.write('        ],\n')
        f.write('        "max_tokens": max_tokens,\n')
        f.write('        "temperature": temperature\n')
        f.write('    }\n')
        f.write('    \n')
        f.write('    response = requests.post(url, json=payload, headers=headers)\n')
        f.write('    response.raise_for_status()\n')
        f.write('    data = response.json()\n')
        f.write('    \n')
        f.write('    return data["choices"][0]["message"]["content"]\n')

    # Updated config file with all API keys
    config_file = os.path.join(config_dir, "global_config.yaml")
    if not os.path.exists(config_file):
        with open(config_file, "w") as f:
            f.write('# API Keys - Add your keys here\n')
            f.write('GOOGLE_API_KEY: "your-google-api-key-here"\n')
            f.write('GROQ_API_KEY: "your-groq-api-key-here"\n')
            f.write('OPENAI_API_KEY: "your-openai-api-key-here"\n')

    for tool_id, tool_data in AVAILABLE_TOOLS.items():
        tool_file = os.path.join(tools_dir, tool_id + ".py")
        if not os.path.exists(tool_file):
            with open(tool_file, "w") as f:
                f.write(tool_data["code"])


if __name__ == "__main__":
    os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)
    print("=" * 50)
    print("AI Agent Generator")
    print("Open http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
