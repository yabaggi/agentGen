from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

OUTPUT_DIR = "generated_agents"

MODELS = [
    {"id": "gemini-flash", "name": "Gemini Flash", "provider": "google"},
    {"id": "gemini-pro", "name": "Gemini Pro", "provider": "google"},
    {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B", "provider": "groq"},
    {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B", "provider": "groq"},
    {"id": "mixtral-8x7b-32768", "name": "Mixtral 8x7B", "provider": "groq"},
    {"id": "gpt-4o", "name": "GPT-4o", "provider": "openai"},
    {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "provider": "openai"},
    {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "openai"},
]

TOOLS = [
    {"id": "web_scraper", "name": "Web Scraper", "description": "Extract content from URLs"},
    {"id": "text_cleaner", "name": "Text Cleaner", "description": "Clean and normalize text"},
    {"id": "file_reader", "name": "File Reader", "description": "Read content from files"},
    {"id": "pdf_parser", "name": "PDF Parser", "description": "Extract text from PDFs"},
    {"id": "image_analyzer", "name": "Image Analyzer", "description": "Analyze images"},
    {"id": "data_validator", "name": "Data Validator", "description": "Validate data formats"},
    {"id": "api_caller", "name": "API Caller", "description": "Make external API requests"},
    {"id": "calculator", "name": "Calculator", "description": "Math calculations"},
    {"id": "translator", "name": "Translator", "description": "Translate between languages"},
    {"id": "summarizer", "name": "Summarizer", "description": "Summarize long texts"},
    {"id": "sentiment_analyzer", "name": "Sentiment Analyzer", "description": "Analyze sentiment"},
    {"id": "keyword_extractor", "name": "Keyword Extractor", "description": "Extract keywords"},
]

OUTPUT_FORMATS = [
    {"id": "plain_text", "name": "Plain Text", "description": "Simple text output"},
    {"id": "json", "name": "JSON", "description": "Structured JSON data"},
    {"id": "markdown", "name": "Markdown", "description": "Formatted markdown"},
    {"id": "html", "name": "HTML", "description": "HTML formatted output"},
    {"id": "csv", "name": "CSV", "description": "Comma-separated values"},
    {"id": "xml", "name": "XML", "description": "XML structured data"},
    {"id": "yaml", "name": "YAML", "description": "YAML formatted output"},
    {"id": "table", "name": "Table", "description": "Tabular format"},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/models", methods=["GET"])
def get_models():
    return jsonify(MODELS)

@app.route("/api/tools", methods=["GET"])
def get_tools():
    return jsonify(TOOLS)

@app.route("/api/formats", methods=["GET"])
def get_formats():
    return jsonify(OUTPUT_FORMATS)

@app.route("/api/templates", methods=["GET"])
def get_templates():
    path = os.path.join("static", "data", "promptTemplates.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return jsonify(json.load(f))
    return jsonify({})

@app.route("/api/create", methods=["POST"])
def create_agent():
    data = request.json
    try:
        name = data.get("agent_name", "my_agent").lower().replace(" ", "_")
        agent_dir = os.path.join(OUTPUT_DIR, "agents", name)
        os.makedirs(os.path.join(agent_dir, "core", "tools"), exist_ok=True)
        os.makedirs(os.path.join(agent_dir, "config"), exist_ok=True)
        files = generate_agent_files(data, name)
        for fname, content in files.items():
            fpath = os.path.join(agent_dir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
        generate_infra(agent_dir)
        return jsonify({"success": True, "path": agent_dir})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/preview", methods=["POST"])
def preview_agent():
    try:
        data = request.json
        name = data.get("agent_name", "my_agent").lower().replace(" ", "_")
        files = generate_agent_files(data, name)
        return jsonify({"success": True, "files": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def generate_agent_files(data, name):
    cls = name.title().replace("_", "")
    fields = data.get("required_fields", [])
    
    cfg = {
        "name": name,
        "model": data.get("model_id"),
        "role": data.get("model_role"),
        "prompt_template": data.get("prompt_template"),
        "required_fields": fields,
        "tools": data.get("tools", []),
        "output_format": data.get("output_format", "plain_text")
    }

    a = []
    a.append("import os, json")
    a.append("from core.llm_caller import call_llm")
    a.append("")
    a.append("class " + cls + "Agent:")
    a.append("    def __init__(self):")
    a.append("        p = os.path.join(os.path.dirname(__file__), 'config.json')")
    a.append("        with open(p, 'r') as f:")
    a.append("            self.config = json.load(f)")
    a.append("")
    a.append("    def run(self, **kw):")
    a.append("        prompt = self.config['prompt_template'].format(**kw)")
    a.append("        return call_llm(prompt, self.config['model'])")
    agent_py = "\n".join(a)

    form_fields = ""
    for field in fields:
        label = field.replace("_", " ").title()
        form_fields += "<label>" + label + "</label>"
        form_fields += "<textarea name='" + field + "' rows='3' required></textarea>"

    w = []
    w.append("from flask import Flask, request, jsonify, render_template_string")
    w.append("from agent import " + cls + "Agent")
    w.append("")
    w.append("app = Flask(__name__)")
    w.append("agent = " + cls + "Agent()")
    w.append("")
    w.append("HTML = '''")
    w.append("<!DOCTYPE html>")
    w.append("<html>")
    w.append("<head>")
    w.append("    <title>" + name.upper() + " Agent</title>")
    w.append("    <style>")
    w.append("        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }")
    w.append("        h1 { color: #333; }")
    w.append("        label { display: block; margin-top: 15px; font-weight: bold; }")
    w.append("        textarea { width: 100%; padding: 10px; margin-top: 5px; }")
    w.append("        button { margin-top: 20px; padding: 12px 24px; background: #007bff; color: white; border: none; cursor: pointer; }")
    w.append("        button:hover { background: #0056b3; }")
    w.append("        #result { margin-top: 20px; padding: 15px; background: #f5f5f5; white-space: pre-wrap; }")
    w.append("    </style>")
    w.append("</head>")
    w.append("<body>")
    w.append("    <h1>" + name.replace("_", " ").title() + " Agent</h1>")
    w.append("    <form id='agentForm'>")
    w.append("        " + form_fields)
    w.append("        <button type='submit'>Run Agent</button>")
    w.append("    </form>")
    w.append("    <div id='result'></div>")
    w.append("    <script>")
    w.append("        document.getElementById('agentForm').onsubmit = async function(e) {")
    w.append("            e.preventDefault();")
    w.append("            const formData = new FormData(this);")
    w.append("            const data = Object.fromEntries(formData.entries());")
    w.append("            document.getElementById('result').innerText = 'Processing...';")
    w.append("            const res = await fetch('/run', {")
    w.append("                method: 'POST',")
    w.append("                headers: {'Content-Type': 'application/json'},")
    w.append("                body: JSON.stringify(data)")
    w.append("            });")
    w.append("            const json = await res.json();")
    w.append("            document.getElementById('result').innerText = json.response || json.error;")
    w.append("        };")
    w.append("    </script>")
    w.append("</body>")
    w.append("</html>")
    w.append("'''")
    w.append("")
    w.append("@app.route('/')")
    w.append("def home():")
    w.append("    return render_template_string(HTML)")
    w.append("")
    w.append("@app.route('/run', methods=['POST'])")
    w.append("def run():")
    w.append("    data = request.json")
    w.append("    try:")
    w.append("        res = agent.run(**data)")
    w.append("        return jsonify({'success': True, 'response': res})")
    w.append("    except Exception as e:")
    w.append("        return jsonify({'success': False, 'error': str(e)})")
    w.append("")
    w.append("if __name__ == '__main__':")
    w.append("    print('Agent running at http://localhost:5001')")
    w.append("    app.run(port=5001, debug=True)")
    web_py = "\n".join(w)

    r = []
    r.append("AGENT: " + name.upper())
    r.append("")
    r.append("SETUP:")
    r.append("1. Edit config/keys.yaml with your API keys")
    r.append("2. pip install flask pyyaml requests")
    r.append("3. python web_app.py")
    r.append("4. Open http://localhost:5001")
    readme = "\n".join(r)

    return {
        "config.json": json.dumps(cfg, indent=2),
        "agent.py": agent_py,
        "web_app.py": web_py,
        "README.txt": readme
    }

def generate_infra(base):
    core = os.path.join(base, "core")
    
    u = []
    u.append("import yaml, os")
    u.append("def get_key(prov):")
    u.append("    p = os.path.join(os.path.dirname(__file__), '../config/keys.yaml')")
    u.append("    if not os.path.exists(p): return ''")
    u.append("    with open(p, 'r') as f:")
    u.append("        keys = yaml.safe_load(f)")
    u.append("        return keys.get(prov.upper() + '_API_KEY', '')")
    with open(os.path.join(core, "utils.py"), "w") as f:
        f.write("\n".join(u))

    l = []
    l.append("from .utils import get_key")
    l.append("def call_llm(prompt, model):")
    l.append("    key = get_key('google')")
    l.append("    return 'Response from ' + model")
    with open(os.path.join(core, "llm_caller.py"), "w") as f:
        f.write("\n".join(l))

    k = []
    k.append("GOOGLE_API_KEY: your_key_here")
    k.append("GROQ_API_KEY: your_key_here")
    k.append("OPENAI_API_KEY: your_key_here")
    with open(os.path.join(base, "config", "keys.yaml"), "w") as f:
        f.write("\n".join(k))

    open(os.path.join(core, "__init__.py"), "a").close()
    open(os.path.join(core, "tools", "__init__.py"), "a").close()

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(port=5000, debug=True)
