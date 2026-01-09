from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import zipfile
import io

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
        return jsonify({"success": True, "path": agent_dir, "agent_name": name})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/download/<agent_name>", methods=["GET"])
def download_agent(agent_name):
    try:
        agent_dir = os.path.join(OUTPUT_DIR, "agents", agent_name)
        
        if not os.path.exists(agent_dir):
            return jsonify({"success": False, "error": "Agent not found"}), 404
        
        memory_file = io.BytesIO()
        
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(agent_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.join(agent_name, os.path.relpath(file_path, agent_dir))
                    zf.write(file_path, arcname)
        
        memory_file.seek(0)
        
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=agent_name + '.zip'
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/preview", methods=["POST"])
def preview_agent():
    try:
        data = request.json
        name = data.get("agent_name", "my_agent").lower().replace(" ", "_")
        files = generate_agent_files(data, name)
        return jsonify({"success": True, "files": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
def get_mobile_template(name, description, fields):
    display_name = name.replace("_", " ").title()
    
    form_html = ""
    for field in fields:
        label = field.replace("_", " ").title()
        form_html += '<div class="input-group">'
        form_html += '<label for="' + field + '">' + label + '</label>'
        form_html += '<textarea id="' + field + '" name="' + field + '" rows="3" placeholder="Enter ' + label.lower() + '..." required></textarea>'
        form_html += '</div>'
    
    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html lang="en">')
    html.append('<head>')
    html.append('<meta charset="UTF-8">')
    html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">')
    html.append('<title>' + display_name + '</title>')
    html.append('<style>')
    html.append('* { box-sizing: border-box; margin: 0; padding: 0; }')
    html.append(':root { --primary: #6366f1; --primary-dark: #4f46e5; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --text-muted: #94a3b8; --border: #334155; --success: #22c55e; --error: #ef4444; }')
    html.append('body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; min-height: 100dvh; }')
    html.append('.container { max-width: 600px; margin: 0 auto; padding: 16px; padding-bottom: 100px; }')
    html.append('.header { text-align: center; padding: 24px 0; border-bottom: 1px solid var(--border); margin-bottom: 24px; }')
    html.append('.header h1 { font-size: 1.75rem; font-weight: 700; margin-bottom: 8px; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }')
    html.append('.header p { color: var(--text-muted); font-size: 0.95rem; line-height: 1.5; }')
    html.append('.card { background: var(--card); border-radius: 16px; padding: 20px; margin-bottom: 16px; border: 1px solid var(--border); }')
    html.append('.input-group { margin-bottom: 20px; }')
    html.append('.input-group:last-child { margin-bottom: 0; }')
    html.append('label { display: block; font-size: 0.875rem; font-weight: 600; color: var(--text); margin-bottom: 8px; }')
    html.append('textarea { width: 100%; padding: 14px; font-size: 16px; border: 2px solid var(--border); border-radius: 12px; background: var(--bg); color: var(--text); resize: vertical; min-height: 80px; transition: border-color 0.2s, box-shadow 0.2s; }')
    html.append('textarea:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2); }')
    html.append('textarea::placeholder { color: var(--text-muted); }')
    html.append('.btn-container { position: fixed; bottom: 0; left: 0; right: 0; padding: 16px; background: linear-gradient(transparent, var(--bg) 20%); }')
    html.append('.btn { width: 100%; max-width: 600px; margin: 0 auto; display: block; padding: 16px 24px; font-size: 1rem; font-weight: 600; color: white; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); border: none; border-radius: 12px; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; -webkit-tap-highlight-color: transparent; }')
    html.append('.btn:active { transform: scale(0.98); }')
    html.append('.btn:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }')
    html.append('.result-card { background: var(--card); border-radius: 16px; padding: 20px; margin-top: 16px; border: 1px solid var(--border); display: none; }')
    html.append('.result-card.show { display: block; animation: fadeIn 0.3s ease; }')
    html.append('.result-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }')
    html.append('.result-title { font-size: 0.875rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }')
    html.append('.result-content { font-size: 1rem; line-height: 1.7; white-space: pre-wrap; word-break: break-word; }')
    html.append('.copy-btn { padding: 8px 12px; font-size: 0.75rem; background: var(--border); color: var(--text); border: none; border-radius: 8px; cursor: pointer; }')
    html.append('.loading { display: inline-block; width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-radius: 50%; border-top-color: white; animation: spin 0.8s linear infinite; margin-right: 8px; vertical-align: middle; }')
    html.append('.status { text-align: center; padding: 40px 20px; color: var(--text-muted); }')
    html.append('.status.error { color: var(--error); }')
    html.append('.status.success { color: var(--success); }')
    html.append('@keyframes spin { to { transform: rotate(360deg); } }')
    html.append('@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }')
    html.append('@media (min-width: 640px) { .container { padding: 24px; } .header h1 { font-size: 2rem; } .card { padding: 24px; } }')
    html.append('</style>')
    html.append('</head>')
    html.append('<body>')
    html.append('<div class="container">')
    html.append('<div class="header">')
    html.append('<h1>' + display_name + '</h1>')
    html.append('<p>' + (description or 'AI-powered assistant ready to help you.') + '</p>')
    html.append('</div>')
    html.append('<form id="agentForm" class="card">')
    html.append(form_html)
    html.append('</form>')
    html.append('<div id="resultCard" class="result-card">')
    html.append('<div class="result-header">')
    html.append('<span class="result-title">Response</span>')
    html.append('<button type="button" class="copy-btn" onclick="copyResult()">Copy</button>')
    html.append('</div>')
    html.append('<div id="resultContent" class="result-content"></div>')
    html.append('</div>')
    html.append('</div>')
    html.append('<div class="btn-container">')
    html.append('<button type="submit" form="agentForm" class="btn" id="submitBtn">Generate Response</button>')
    html.append('</div>')
    html.append('<script>')
    html.append('const form = document.getElementById("agentForm");')
    html.append('const btn = document.getElementById("submitBtn");')
    html.append('const resultCard = document.getElementById("resultCard");')
    html.append('const resultContent = document.getElementById("resultContent");')
    html.append('form.onsubmit = async function(e) {')
    html.append('  e.preventDefault();')
    html.append('  btn.disabled = true;')
    html.append('  btn.innerHTML = "<span class=\\"loading\\"></span>Processing...";')
    html.append('  resultCard.classList.remove("show");')
    html.append('  const formData = new FormData(this);')
    html.append('  const data = Object.fromEntries(formData.entries());')
    html.append('  try {')
    html.append('    const res = await fetch("/run", {')
    html.append('      method: "POST",')
    html.append('      headers: {"Content-Type": "application/json"},')
    html.append('      body: JSON.stringify(data)')
    html.append('    });')
    html.append('    const json = await res.json();')
    html.append('    resultContent.textContent = json.response || json.error || "No response";')
    html.append('    resultCard.classList.add("show");')
    html.append('  } catch (err) {')
    html.append('    resultContent.textContent = "Error: " + err.message;')
    html.append('    resultCard.classList.add("show");')
    html.append('  }')
    html.append('  btn.disabled = false;')
    html.append('  btn.textContent = "Generate Response";')
    html.append('};')
    html.append('function copyResult() {')
    html.append('  navigator.clipboard.writeText(resultContent.textContent);')
    html.append('  const btn = document.querySelector(".copy-btn");')
    html.append('  btn.textContent = "Copied!";')
    html.append('  setTimeout(() => btn.textContent = "Copy", 2000);')
    html.append('}')
    html.append('</script>')
    html.append('</body>')
    html.append('</html>')
    
    return "\n".join(html)
def generate_agent_files(data, name):
    cls = name.title().replace("_", "")
    fields = data.get("required_fields", [])
    description = data.get("agent_description", "")
    
    cfg = {
        "name": name,
        "description": description,
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

    mobile_html = get_mobile_template(name, description, fields)

    w = []
    w.append("from flask import Flask, request, jsonify")
    w.append("from agent import " + cls + "Agent")
    w.append("")
    w.append("app = Flask(__name__)")
    w.append("agent = " + cls + "Agent()")
    w.append("")
    w.append("HTML = '''" + mobile_html + "'''")
    w.append("")
    w.append("@app.route('/')")
    w.append("def home():")
    w.append("    return HTML")
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
    w.append("    app.run(host='0.0.0.0', port=5001, debug=True)")
    web_py = "\n".join(w)

    return {
        "config.json": json.dumps(cfg, indent=2),
        "agent.py": agent_py,
        "web_app.py": web_py
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
    l.append("    return 'Response from ' + model + ': This is a placeholder. Connect your API.'")
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
