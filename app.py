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

# Quick Templates - Using YOUR WORKING prompt format (NO JSON BRACES!)
QUICK_TEMPLATES = {
    'bullet_extractor': {
        'name': 'bullet_extractor',
        'description': 'Extracts key bullet points from text',
        'model': 'gemini-flash',
        'fields': ['content', 'num_points'],
        'prompt_template': 'Extract {num_points} key bullet points from the following content:\n\n{content}'
    },
    'flashcard_generator': {
        'name': 'flashcard_generator',
        'description': 'Generates flashcards from content',
        'model': 'gemini-flash',
        'fields': ['content', 'num_cards'],
        # FIXED: Using YOUR working prompt format - NO JSON BRACES!
        'prompt_template': '''You are a helpful study assistant. Create exactly {num_cards} flashcards from the following text.

Rules:
- Each flashcard must be a clear question and a concise answer (under 30 words).
- Do NOT include markdown, numbering, or extra text.
- Avoid yes/no questions.
- Base answers ONLY on the provided text. Do not invent facts.

Text: "{content}"

Output format (one per line):
Q: [question text]
A: [answer text]'''
    },
    'summarizer': {
        'name': 'summarizer',
        'description': 'Summarizes text to specified length',
        'model': 'gemini-flash',
        'fields': ['content', 'length'],
        'prompt_template': 'Summarize the following content in {length} words:\n\n{content}'
    },
    'email_writer': {
        'name': 'email_writer',
        'description': 'Writes professional emails',
        'model': 'gemini-flash',
        'fields': ['topic', 'tone'],
        'prompt_template': 'Write a {tone} email about the following topic:\n\n{topic}'
    },
    'code_explainer': {
        'name': 'code_explainer',
        'description': 'Explains code in simple terms',
        'model': 'gemini-flash',
        'fields': ['code', 'language'],
        'prompt_template': 'Explain this {language} code in simple terms:\n\n{code}'
    },
    'blog_writer': {
        'name': 'blog_writer',
        'description': 'Writes blog posts on any topic',
        'model': 'gemini-flash',
        'fields': ['topic', 'word_count'],
        'prompt_template': 'Write a {word_count} word blog post about:\n\n{topic}'
    },
    'quiz_generator': {
        'name': 'quiz_generator',
        'description': 'Creates multiple choice quizzes',
        'model': 'gemini-flash',
        'fields': ['topic', 'num_questions'],
        'prompt_template': 'Create a {num_questions} question multiple choice quiz about:\n\n{topic}\n\nFor each question provide:\n- The question\n- 4 options (A, B, C, D)\n- The correct answer'
    },
    'social_media_post': {
        'name': 'social_media_post',
        'description': 'Creates engaging social media posts',
        'model': 'gemini-flash',
        'fields': ['topic', 'platform'],
        'prompt_template': 'Write an engaging {platform} post about:\n\n{topic}'
    },
    'meeting_notes': {
        'name': 'meeting_notes',
        'description': 'Organizes meeting notes with action items',
        'model': 'gemini-flash',
        'fields': ['notes'],
        'prompt_template': 'Organize these meeting notes into sections:\n\n1. Summary\n2. Key Points\n3. Action Items\n4. Next Steps\n\nNotes:\n{notes}'
    },
    'product_description': {
        'name': 'product_description',
        'description': 'Writes compelling product descriptions',
        'model': 'gemini-flash',
        'fields': ['product_name', 'features'],
        'prompt_template': 'Write a compelling product description for {product_name} with these features:\n\n{features}'
    },
    'code_reviewer': {
        'name': 'code_reviewer',
        'description': 'Reviews code and suggests improvements',
        'model': 'gemini-flash',
        'fields': ['code', 'language'],
        'prompt_template': 'Review this {language} code and suggest improvements for readability, performance, security, and best practices:\n\n{code}'
    },
    'essay_writer': {
        'name': 'essay_writer',
        'description': 'Writes structured essays',
        'model': 'gemini-flash',
        'fields': ['topic', 'word_count'],
        'prompt_template': 'Write a {word_count} word essay on:\n\n{topic}\n\nInclude:\n- Introduction with thesis statement\n- 3 body paragraphs with supporting evidence\n- Conclusion that reinforces the thesis'
    },
    'job_description': {
        'name': 'job_description',
        'description': 'Creates professional job descriptions',
        'model': 'gemini-flash',
        'fields': ['job_title', 'requirements'],
        'prompt_template': 'Write a professional job description for {job_title} with these requirements:\n\n{requirements}\n\nInclude:\n- Overview\n- Responsibilities\n- Qualifications\n- Benefits'
    },
    'story_writer': {
        'name': 'story_writer',
        'description': 'Writes creative short stories',
        'model': 'gemini-flash',
        'fields': ['theme', 'word_count'],
        'prompt_template': 'Write a {word_count} word creative story about:\n\n{theme}'
    },
    'recipe_generator': {
        'name': 'recipe_generator',
        'description': 'Creates detailed recipes',
        'model': 'gemini-flash',
        'fields': ['dish_name', 'servings'],
        'prompt_template': 'Create a detailed recipe for {dish_name} that serves {servings} people.\n\nInclude:\n- Ingredients list\n- Step-by-step instructions\n- Prep time\n- Cook time\n- Tips'
    },
    'study_guide': {
        'name': 'study_guide',
        'description': 'Creates comprehensive study guides',
        'model': 'gemini-flash',
        'fields': ['topic', 'content'],
        'prompt_template': 'Create a comprehensive study guide for {topic} covering:\n\n{content}\n\nInclude:\n- Key Concepts\n- Important Terms and Definitions\n- Practice Questions\n- Study Tips'
    },
    'cover_letter': {
        'name': 'cover_letter',
        'description': 'Writes professional cover letters',
        'model': 'gemini-flash',
        'fields': ['job_title', 'company', 'experience'],
        'prompt_template': 'Write a professional cover letter for the position of {job_title} at {company}.\n\nHighlight this experience:\n{experience}'
    },
    'press_release': {
        'name': 'press_release',
        'description': 'Writes formal press releases',
        'model': 'gemini-flash',
        'fields': ['announcement', 'company'],
        'prompt_template': 'Write a professional press release for {company} announcing:\n\n{announcement}\n\nFollow standard press release format with headline, dateline, body, and boilerplate.'
    },
    'translation': {
        'name': 'translation',
        'description': 'Translates text between languages',
        'model': 'gemini-flash',
        'fields': ['text', 'source_lang', 'target_lang'],
        'prompt_template': 'Translate this text from {source_lang} to {target_lang}:\n\n{text}'
    },
    'seo_optimizer': {
        'name': 'seo_optimizer',
        'description': 'Optimizes content for SEO',
        'model': 'gemini-flash',
        'fields': ['content', 'keywords'],
        'prompt_template': 'Optimize this content for SEO using these keywords: {keywords}\n\nOriginal content:\n{content}\n\nProvide:\n1. Optimized title (60 chars max)\n2. Meta description (155 chars max)\n3. Improved content with keywords naturally integrated'
    }
}

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
    json_path = os.path.join("static", "data", "promptTemplates.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                return jsonify(json.load(f))
        except Exception as e:
            print(f"Error loading templates from JSON: {e}")
    
    return jsonify(list(QUICK_TEMPLATES.values()))

@app.route("/api/quick/<template_name>", methods=["GET"])
def quick_template(template_name):
    if template_name not in QUICK_TEMPLATES:
        return jsonify({"success": False, "error": "Template not found"}), 404
    
    try:
        template = QUICK_TEMPLATES[template_name]
        agent_dir = os.path.join(OUTPUT_DIR, "agents", template['name'])
        os.makedirs(os.path.join(agent_dir, "core", "tools"), exist_ok=True)
        os.makedirs(os.path.join(agent_dir, "config"), exist_ok=True)
        
        data = {
            "agent_name": template['name'],
            "agent_description": template['description'],
            "model_id": template['model'],
            "prompt_template": template['prompt_template'],
            "required_fields": template['fields'],
            "tools": [],
            "output_format": "plain_text"
        }
        
        files = generate_agent_files(data, template['name'])
        for fname, content in files.items():
            fpath = os.path.join(agent_dir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
        
        generate_infra(agent_dir)
        
        return jsonify({"success": True, "path": agent_dir, "agent_name": template['name']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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
        form_html += '<textarea id="' + field + '" name="' + field + '" rows="4" placeholder="Enter ' + label.lower() + '..." required></textarea>'
        form_html += '</div>'
    
    html = []
    html.append('<!DOCTYPE html>')
    html.append('<html lang="en">')
    html.append('<head>')
    html.append('<meta charset="UTF-8">')
    html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html.append('<title>' + display_name + '</title>')
    html.append('<style>')
    html.append('* { margin: 0; padding: 0; box-sizing: border-box; }')
    html.append('body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; min-height: 100vh; padding-bottom: 120px; }')
    html.append('.container { max-width: 700px; margin: 0 auto; padding: 20px; }')
    html.append('.header { text-align: center; padding: 30px 0; border-bottom: 2px solid #334155; margin-bottom: 30px; }')
    html.append('.header h1 { font-size: 2rem; margin-bottom: 10px; background: linear-gradient(135deg, #6366f1, #a855f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }')
    html.append('.header p { color: #94a3b8; font-size: 1rem; }')
    html.append('.card { background: #1e293b; border-radius: 16px; padding: 30px; margin-bottom: 20px; border: 1px solid #334155; }')
    html.append('.input-group { margin-bottom: 24px; }')
    html.append('label { display: block; font-weight: 600; margin-bottom: 8px; color: #e2e8f0; }')
    html.append('textarea { width: 100%; padding: 14px; font-size: 16px; border: 2px solid #334155; border-radius: 10px; background: #0f172a; color: #f8fafc; resize: vertical; font-family: inherit; }')
    html.append('textarea:focus { outline: none; border-color: #6366f1; }')
    html.append('.btn-fixed { position: fixed; bottom: 0; left: 0; right: 0; padding: 20px; background: linear-gradient(to top, #0f172a 80%, transparent); }')
    html.append('.btn { width: 100%; max-width: 700px; margin: 0 auto; display: block; padding: 16px; font-size: 1.1rem; font-weight: 600; color: white; background: linear-gradient(135deg, #6366f1, #4f46e5); border: none; border-radius: 12px; cursor: pointer; transition: transform 0.1s; }')
    html.append('.btn:active { transform: scale(0.98); }')
    html.append('.btn:disabled { opacity: 0.6; cursor: not-allowed; }')
    html.append('.result-card { background: #1e293b; border-radius: 16px; padding: 24px; border: 1px solid #334155; display: none; }')
    html.append('.result-card.show { display: block; animation: fadeIn 0.3s; }')
    html.append('.result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }')
    html.append('.result-title { font-weight: 700; color: #94a3b8; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; }')
    html.append('.result-content { line-height: 1.8; white-space: pre-wrap; word-wrap: break-word; }')
    html.append('.copy-btn { background: #334155; border: none; color: #f8fafc; padding: 6px 14px; border-radius: 6px; font-size: 0.85rem; cursor: pointer; }')
    html.append('.copy-btn:hover { background: #475569; }')
    html.append('@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }')
    html.append('</style>')
    html.append('</head>')
    html.append('<body>')
    html.append('<div class="container">')
    html.append('<div class="header">')
    html.append('<h1>' + display_name + '</h1>')
    html.append('<p>' + (description or 'AI-powered assistant') + '</p>')
    html.append('</div>')
    html.append('<div id="inputCard" class="card">')
    html.append(form_html)
    html.append('</div>')
    html.append('<div id="resultCard" class="result-card">')
    html.append('<div class="result-header">')
    html.append('<span class="result-title">Result</span>')
    html.append('<button class="copy-btn" onclick="copyToClipboard()">Copy</button>')
    html.append('</div>')
    html.append('<div id="resultContent" class="result-content"></div>')
    html.append('</div>')
    html.append('</div>')
    html.append('<div class="btn-fixed">')
    html.append('<button class="btn" id="submitBtn" onclick="handleSubmit()">Generate Response</button>')
    html.append('</div>')
    html.append('<script>')
    html.append('async function handleSubmit() {')
    html.append('  const btn = document.getElementById("submitBtn");')
    html.append('  const resultCard = document.getElementById("resultCard");')
    html.append('  const resultContent = document.getElementById("resultContent");')
    html.append('  const inputs = document.querySelectorAll("textarea");')
    html.append('  let isValid = true;')
    html.append('  inputs.forEach(input => {')
    html.append('    if (input.required && !input.value.trim()) {')
    html.append('      isValid = false;')
    html.append('      input.style.borderColor = "#ef4444";')
    html.append('    } else {')
    html.append('      input.style.borderColor = "#334155";')
    html.append('    }')
    html.append('  });')
    html.append('  if (!isValid) {')
    html.append('    alert("Please fill in all required fields");')
    html.append('    return;')
    html.append('  }')
    html.append('  btn.disabled = true;')
    html.append('  btn.textContent = "Processing...";')
    html.append('  resultCard.classList.remove("show");')
    html.append('  const data = {};')
    html.append('  inputs.forEach(input => {')
    html.append('    data[input.name] = input.value;')
    html.append('  });')
    html.append('  try {')
    html.append('    const response = await fetch("/run", {')
    html.append('      method: "POST",')
    html.append('      headers: { "Content-Type": "application/json" },')
    html.append('      body: JSON.stringify(data)')
    html.append('    });')
    html.append('    const result = await response.json();')
    html.append('    resultContent.textContent = result.response || result.error || "No response received";')
    html.append('    resultCard.classList.add("show");')
    html.append('    resultCard.scrollIntoView({ behavior: "smooth", block: "start" });')
    html.append('  } catch (error) {')
    html.append('    resultContent.textContent = "Error: " + error.message;')
    html.append('    resultCard.classList.add("show");')
    html.append('  }')
    html.append('  btn.disabled = false;')
    html.append('  btn.textContent = "Generate Response";')
    html.append('}')
    html.append('function copyToClipboard() {')
    html.append('  const content = document.getElementById("resultContent").textContent;')
    html.append('  navigator.clipboard.writeText(content).then(() => {')
    html.append('    const btn = event.target;')
    html.append('    btn.textContent = "Copied!";')
    html.append('    setTimeout(() => btn.textContent = "Copy", 2000);')
    html.append('  });')
    html.append('}')
    html.append('</script>')
    html.append('</body>')
    html.append('</html>')
    
    return "\n".join(html)


def generate_agent_files(data, name):
    cls = name.title().replace("_", "")
    fields = data.get("required_fields", [])
    description = data.get("agent_description", "")
    prompt_template = data.get("prompt_template", "").strip()
    
    if not prompt_template:
        field_placeholders = "\n".join([f"{field.replace('_', ' ').title()}: {{{field}}}" for field in fields])
        prompt_template = field_placeholders
    
    cfg = {
        "name": name,
        "description": description,
        "model": data.get("model_id"),
        "role": data.get("model_role", ""),
        "prompt_template": prompt_template,
        "required_fields": fields,
        "tools": data.get("tools", []),
        "output_format": data.get("output_format", "plain_text")
    }

    # Generate agent.py with DEBUG LOGGING
    a = []
    a.append("import os, json, logging")
    a.append("from core.llm_caller import call_llm")
    a.append("")
    a.append("logging.basicConfig(level=logging.INFO)")
    a.append("")
    a.append("class " + cls + "Agent:")
    a.append("    def __init__(self):")
    a.append("        p = os.path.join(os.path.dirname(__file__), 'config.json')")
    a.append("        with open(p, 'r') as f:")
    a.append("            self.config = json.load(f)")
    a.append("")
    a.append("    def run(self, **kw):")
    a.append("        # DEBUG: Log what we received")
    a.append("        logging.info(f'Received kwargs: {kw}')")
    a.append("        ")
    a.append("        # Get the prompt template")
    a.append("        prompt_template = self.config['prompt_template']")
    a.append("        logging.info(f'Prompt template: {prompt_template}')")
    a.append("        ")
    a.append("        # Format the prompt with provided arguments")
    a.append("        try:")
    a.append("            prompt = prompt_template.format(**kw)")
    a.append("            logging.info(f'Formatted prompt (first 200 chars): {prompt[:200]}...')")
    a.append("        except KeyError as e:")
    a.append("            logging.error(f'Missing required field in prompt template: {e}')")
    a.append("            return f'Error: Missing required field {e}'")
    a.append("        except Exception as e:")
    a.append("            logging.error(f'Error formatting prompt: {e}')")
    a.append("            return f'Error formatting prompt: {e}'")
    a.append("        ")
    a.append("        # Call the LLM")
    a.append("        result = call_llm(prompt, self.config['model'])")
    a.append("        logging.info(f'LLM result (first 100 chars): {result[:100]}...')")
    a.append("        ")
    a.append("        return result")
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
    """Generate core infrastructure with CORRECT Gemini model names."""
    core = os.path.join(base, "core")
    
    # utils.py
    u = []
    u.append("import yaml")
    u.append("import os")
    u.append("import logging")
    u.append("")
    u.append("logging.basicConfig(level=logging.INFO)")
    u.append("")
    u.append("def get_key(provider):")
    u.append("    keys_path = os.path.join(os.path.dirname(__file__), '../config/keys.yaml')")
    u.append("    if not os.path.exists(keys_path):")
    u.append("        return ''")
    u.append("    with open(keys_path, 'r') as f:")
    u.append("        keys = yaml.safe_load(f) or {}")
    u.append("        return keys.get(provider.upper() + '_API_KEY', '')")
    with open(os.path.join(core, "utils.py"), "w") as f:
        f.write("\n".join(u))

    # llm_caller.py - FIXED: Correct Gemini model names
    l = []
    l.append("import requests")
    l.append("import logging")
    l.append("from .utils import get_key")
    l.append("")
    l.append("def call_llm(prompt, model_id):")
    l.append("    \"\"\"Routes to appropriate LLM provider based on model_id.\"\"\"")
    l.append("    if 'gemini' in model_id or 'google' in model_id:")
    l.append("        return call_google(prompt, model_id)")
    l.append("    elif 'gpt' in model_id or 'openai' in model_id:")
    l.append("        return call_openai(prompt, model_id)")
    l.append("    elif 'llama' in model_id or 'mixtral' in model_id or 'groq' in model_id:")
    l.append("        return call_groq(prompt, model_id)")
    l.append("    elif 'ollama' in model_id:")
    l.append("        return call_ollama(prompt, model_id)")
    l.append("    else:")
    l.append("        return f'Error: Unsupported model - {model_id}'")
    l.append("")
    l.append("def call_google(prompt, model_id):")
    l.append("    \"\"\"Generates content using Gemini API with correct model names.\"\"\"")
    l.append("    api_key = get_key('gemini')")
    l.append("    if not api_key or api_key == 'your_key_here':")
    l.append("        return 'Error: GEMINI_API_KEY not configured in config/keys.yaml'")
    l.append("    ")
    l.append("    # FIXED: Use correct Gemini model names (no version prefix)")
    l.append("    if 'flash' in model_id.lower():")
    l.append("        model_name = 'gemini-flash-latest'")
    l.append("    elif 'pro' in model_id.lower():")
    l.append("        model_name = 'gemini-pro-latest'")
    l.append("    else:")
    l.append("        model_name = 'gemini-flash-latest'")
    l.append("    ")
    l.append("    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}'")
    l.append("    payload = {'contents': [{'parts': [{'text': prompt}]}]}")
    l.append("    ")
    l.append("    try:")
    l.append("        response = requests.post(url, json=payload, timeout=30.0)")
    l.append("        ")
    l.append("        if response.status_code != 200:")
    l.append("            error_detail = 'Unknown error.'")
    l.append("            try:")
    l.append("                error_detail = response.json().get('error', {}).get('message', 'Unknown error.')")
    l.append("            except Exception:")
    l.append("                pass")
    l.append("            logging.error(f'Gemini API returned non-200 status: {response.status_code} - {error_detail}')")
    l.append("            return f'Gemini API error: {error_detail}'")
    l.append("        ")
    l.append("        return response.json()['candidates'][0]['content']['parts'][0]['text'].strip()")
    l.append("    ")
    l.append("    except requests.RequestException as e:")
    l.append("        logging.error(f'Request to Gemini failed: {e}')")
    l.append("        return f'Failed to connect to Gemini API: {str(e)}'")
    l.append("    except (KeyError, IndexError, TypeError) as e:")
    l.append("        logging.exception('Failed to parse Gemini response:')")
    l.append("        return 'Failed to parse response from Gemini.'")
    l.append("")
    l.append("def call_groq(prompt, model_id):")
    l.append("    \"\"\"Generates content using the Groq API.\"\"\"")
    l.append("    api_key = get_key('groq')")
    l.append("    if not api_key or api_key == 'your_key_here':")
    l.append("        return 'Error: GROQ_API_KEY not configured in config/keys.yaml'")
    l.append("    ")
    l.append("    url = 'https://api.groq.com/openai/v1/chat/completions'")
    l.append("    headers = {")
    l.append("        'Authorization': f'Bearer {api_key}',")
    l.append("        'Content-Type': 'application/json'")
    l.append("    }")
    l.append("    model = model_id if 'llama' in model_id or 'mixtral' in model_id else 'llama-3.1-8b-instant'")
    l.append("    payload = {")
    l.append("        'model': model,")
    l.append("        'messages': [{'role': 'user', 'content': prompt}],")
    l.append("        'temperature': 0.3")
    l.append("    }")
    l.append("    ")
    l.append("    try:")
    l.append("        response = requests.post(url, json=payload, headers=headers, timeout=30.0)")
    l.append("        ")
    l.append("        if response.status_code != 200:")
    l.append("            error_detail = 'Unknown error.'")
    l.append("            try:")
    l.append("                error_detail = response.json().get('error', {}).get('message', 'Unknown error.')")
    l.append("            except Exception:")
    l.append("                pass")
    l.append("            logging.error(f'Groq API returned non-200 status: {response.status_code} - {error_detail}')")
    l.append("            return f'Groq API error: {error_detail}'")
    l.append("        ")
    l.append("        return response.json()['choices'][0]['message']['content'].strip()")
    l.append("    ")
    l.append("    except requests.RequestException as e:")
    l.append("        logging.error(f'Request to Groq failed: {e}')")
    l.append("        return f'Failed to connect to Groq API: {str(e)}'")
    l.append("    except (KeyError, IndexError, TypeError) as e:")
    l.append("        logging.exception('Failed to parse Groq response:')")
    l.append("        return 'Failed to parse response from Groq.'")
    l.append("")
    l.append("def call_openai(prompt, model_id):")
    l.append("    \"\"\"Generates content using the OpenAI API.\"\"\"")
    l.append("    api_key = get_key('openai')")
    l.append("    if not api_key or api_key == 'your_key_here':")
    l.append("        return 'Error: OPENAI_API_KEY not configured in config/keys.yaml'")
    l.append("    ")
    l.append("    url = 'https://api.openai.com/v1/chat/completions'")
    l.append("    headers = {")
    l.append("        'Authorization': f'Bearer {api_key}',")
    l.append("        'Content-Type': 'application/json'")
    l.append("    }")
    l.append("    model = model_id if 'gpt' in model_id else 'gpt-4o-mini'")
    l.append("    payload = {")
    l.append("        'model': model,")
    l.append("        'messages': [{'role': 'user', 'content': prompt}],")
    l.append("        'temperature': 0.3")
    l.append("    }")
    l.append("    ")
    l.append("    try:")
    l.append("        response = requests.post(url, json=payload, headers=headers, timeout=30.0)")
    l.append("        ")
    l.append("        if response.status_code == 429:")
    l.append("            error_detail = response.json().get('error', {}).get('message', 'Rate limit exceeded.')")
    l.append("            return f'OpenAI API rate limit exceeded: {error_detail}'")
    l.append("        elif response.status_code != 200:")
    l.append("            error_detail = response.json().get('error', {}).get('message', 'Unknown error.')")
    l.append("            logging.error(f'OpenAI API returned non-200 status: {response.status_code} - {error_detail}')")
    l.append("            return f'OpenAI API error: {error_detail}'")
    l.append("        ")
    l.append("        return response.json()['choices'][0]['message']['content'].strip()")
    l.append("    ")
    l.append("    except requests.RequestException as e:")
    l.append("        logging.error(f'Request to OpenAI failed: {e}')")
    l.append("        return f'Failed to connect to OpenAI API: {str(e)}'")
    l.append("    except (KeyError, IndexError, TypeError) as e:")
    l.append("        logging.exception('Failed to parse OpenAI response:')")
    l.append("        return 'Failed to parse response from OpenAI.'")
    l.append("")
    l.append("def call_ollama(prompt, model_id):")
    l.append("    \"\"\"Generates content using local Ollama.\"\"\"")
    l.append("    url = 'http://localhost:11434/api/generate'")
    l.append("    model = 'llama3'")
    l.append("    if 'llama' in model_id:")
    l.append("        model = model_id")
    l.append("    ")
    l.append("    payload = {")
    l.append("        'model': model,")
    l.append("        'prompt': prompt,")
    l.append("        'stream': False")
    l.append("    }")
    l.append("    ")
    l.append("    try:")
    l.append("        response = requests.post(url, json=payload, timeout=60.0)")
    l.append("        ")
    l.append("        if response.status_code != 200:")
    l.append("            logging.error(f'Ollama returned non-200 status: {response.status_code}')")
    l.append("            return f'Ollama error: {response.text}'")
    l.append("        ")
    l.append("        return response.json().get('response', '').strip()")
    l.append("    ")
    l.append("    except requests.RequestException as e:")
    l.append("        logging.error(f'Request to Ollama failed: {e}')")
    l.append("        return 'Failed to connect to Ollama. Is it running?'")
    l.append("    except (KeyError, IndexError, TypeError) as e:")
    l.append("        logging.exception('Failed to parse Ollama response:')")
    l.append("        return 'Failed to parse response from Ollama.'")
    
    with open(os.path.join(core, "llm_caller.py"), "w") as f:
        f.write("\n".join(l))

    # keys.yaml
    k = []
    k.append("# Add your API keys here")
    k.append("# Gemini: https://makersuite.google.com/app/apikey")
    k.append("# Groq: https://console.groq.com/keys")
    k.append("# OpenAI: https://platform.openai.com/api-keys")
    k.append("")
    k.append("GEMINI_API_KEY: your_key_here")
    k.append("GROQ_API_KEY: your_key_here")
    k.append("OPENAI_API_KEY: your_key_here")
    
    with open(os.path.join(base, "config", "keys.yaml"), "w") as f:
        f.write("\n".join(k))

    # __init__.py files
    open(os.path.join(core, "__init__.py"), "a").close()
    open(os.path.join(core, "tools", "__init__.py"), "a").close()

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(port=5000, debug=True)
