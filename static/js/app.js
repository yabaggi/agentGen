let currentStep = 1;
const totalSteps = 6;
let promptTemplates = {};
let showAllTemplates = false;

let formData = {
    agent_name: '',
    agent_description: '',
    model_id: 'gemini-flash',
    model_role: '',
    max_tokens: 1000,
    temperature: 0.7,
    required_fields: [],
    field_hints: {},  // ← ADDED: Store hints
    prompt_template: '',
    tools: [],
    output_format: 'plain_text'
};


document.addEventListener('DOMContentLoaded', function() {
    loadTemplates();
    loadTools();
    loadFormats();
    loadModels();
    setupEventListeners();
    updateProgress();
    showStep(1);
});

async function loadTemplates() {
    try {
        const response = await fetch('/api/templates');
        promptTemplates = await response.json();
        renderTemplateButtons();
        renderDropdownMenu();
    } catch (error) {
        console.error('Error loading templates:', error);
        promptTemplates = {};
    }
}

function renderTemplateButtons() {
    const container = document.querySelector('.template-buttons');
    if (!container) return;
    
    container.innerHTML = '';
    
    const templateEntries = Object.entries(promptTemplates);
    const visibleCount = 5;
    
    const templatesToShow = showAllTemplates ? templateEntries : templateEntries.slice(0, visibleCount);
    
    for (const [key, template] of templatesToShow) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn-template';
        btn.dataset.template = key;
        btn.textContent = template.name;
        btn.title = template.description || '';
        btn.addEventListener('click', function() {
            applyTemplate(this.dataset.template);
        });
        container.appendChild(btn);
    }
    
    if (templateEntries.length > visibleCount) {
        const moreBtn = document.createElement('button');
        moreBtn.type = 'button';
        moreBtn.className = 'btn-template btn-more';
        
        if (showAllTemplates) {
            moreBtn.textContent = 'Show Less';
        } else {
            moreBtn.textContent = '+' + (templateEntries.length - visibleCount) + ' more';
        }
        
        moreBtn.addEventListener('click', function() {
            showAllTemplates = !showAllTemplates;
            renderTemplateButtons();
        });
        container.appendChild(moreBtn);
    }
}

function renderDropdownMenu() {
    const container = document.getElementById('dropdownContent');
    if (!container) return;
    
    container.innerHTML = '';
    
    for (const [key, template] of Object.entries(promptTemplates)) {
        const item = document.createElement('div');
        item.className = 'dropdown-item';
        item.dataset.template = key;
        item.innerHTML = '<div class="dropdown-item-name">' + template.name + '</div><div class="dropdown-item-desc">' + template.description + '</div>';
        item.addEventListener('click', function() {
            applyTemplate(this.dataset.template);
            closeDropdown();
        });
        container.appendChild(item);
    }
}

function toggleDropdown() {
    const dropdown = document.getElementById('dropdownMenu');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

function closeDropdown() {
    const dropdown = document.getElementById('dropdownMenu');
    if (dropdown) {
        dropdown.classList.remove('show');
    }
}

function setupEventListeners() {
    document.getElementById('prevBtn').addEventListener('click', prevStep);
    document.getElementById('nextBtn').addEventListener('click', nextStep);
    document.getElementById('createBtn').addEventListener('click', createAgent);

    const hamburgerBtn = document.getElementById('hamburgerBtn');
    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', toggleDropdown);
    }

    document.addEventListener('click', function(e) {
        const dropdown = document.getElementById('dropdownMenu');
        const hamburgerBtn = document.getElementById('hamburgerBtn');
        if (dropdown && hamburgerBtn && !dropdown.contains(e.target) && !hamburgerBtn.contains(e.target)) {
            closeDropdown();
        }
    });

    const tempSlider = document.getElementById('temperature');
    if (tempSlider) {
        tempSlider.addEventListener('input', function() {
            document.getElementById('tempValue').textContent = this.value;
        });
    }

    const fieldInput = document.getElementById('fieldInput');
    if (fieldInput) {
        fieldInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                addFieldsFromInput(this.value);
                this.value = '';
            }
        });
        fieldInput.addEventListener('blur', function() {
            if (this.value.trim()) {
                addFieldsFromInput(this.value);
                this.value = '';
            }
        });
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            updateFilePreview(this.dataset.tab);
        });
    });
}

function addFieldsFromInput(value) {
    const fields = value.split(/[,\s\n]+/).filter(f => f.trim() !== '');
    fields.forEach(field => {
        const cleanField = field.trim().toLowerCase().replace(/[^a-z0-9_]/g, '_');
        if (cleanField && !formData.required_fields.includes(cleanField)) {
            formData.required_fields.push(cleanField);
            addFieldTag(cleanField);
        }
    });
    updateHiddenFieldsInput();
}

function addFieldTag(field) {
    const container = document.getElementById('fieldsContainer');
    const input = document.getElementById('fieldInput');
    const tag = document.createElement('span');
    tag.className = 'field-tag';
    tag.dataset.field = field;
    tag.innerHTML = field + ' <button type="button" onclick="removeField(\'' + field + '\', this)">×</button>';
    container.insertBefore(tag, input);
}

function removeField(field, button) {
    formData.required_fields = formData.required_fields.filter(f => f !== field);
    // ← ADDED: Also remove hint for this field
    if (formData.field_hints && formData.field_hints[field]) {
        delete formData.field_hints[field];
    }
    button.parentElement.remove();
    updateHiddenFieldsInput();
}

function updateHiddenFieldsInput() {
    document.getElementById('requiredFields').value = formData.required_fields.join(',');
}

function applyTemplate(templateName) {
    const template = promptTemplates[templateName];
    if (!template) return;
    
    if (template.agent_name) {
        document.getElementById('agentName').value = template.agent_name;
        formData.agent_name = template.agent_name;
    }
    
    if (template.description) {
        document.getElementById('agentDescription').value = template.description;
        formData.agent_description = template.description;
    }
    
    formData.required_fields = [];
    formData.field_hints = {};  // ← ADDED: Reset hints
    document.querySelectorAll('#fieldsContainer .field-tag').forEach(tag => tag.remove());
    
    if (template.fields && template.fields.length > 0) {
        template.fields.forEach(field => {
            formData.required_fields.push(field);
            addFieldTag(field);
        });
    }
    updateHiddenFieldsInput();
    
    // ← ADDED: Load hints from template
    if (template.hints) {
        formData.field_hints = { ...template.hints };
        console.log('Loaded hints:', formData.field_hints);
    }
    
    if (template.template) {
        document.getElementById('promptTemplate').value = template.template;
        formData.prompt_template = template.template;
    }
    
    if (template.role) {
        document.getElementById('modelRole').value = template.role;
        formData.model_role = template.role;
    }
    
    if (template.suggested_model) {
        const modelSelect = document.getElementById('modelSelect');
        if (modelSelect) {
            const optionExists = Array.from(modelSelect.options).some(opt => opt.value === template.suggested_model);
            if (optionExists) {
                modelSelect.value = template.suggested_model;
                formData.model_id = template.suggested_model;
            }
        }
    }
    
    document.querySelectorAll('#toolsGrid input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
        const card = cb.closest('.tool-card');
        if (card) card.classList.remove('selected');
    });
    
    if (template.tools && Array.isArray(template.tools)) {
        template.tools.forEach(toolId => {
            const checkbox = document.querySelector('#toolsGrid input[value="' + toolId + '"]');
            if (checkbox) {
                checkbox.checked = true;
                const card = checkbox.closest('.tool-card');
                if (card) card.classList.add('selected');
            }
        });
        formData.tools = [...template.tools];
    } else {
        formData.tools = [];
    }
    
    if (template.output_format) {
        const formatCards = document.querySelectorAll('.format-card');
        formatCards.forEach(card => {
            card.classList.remove('selected');
            const input = card.querySelector('input');
            if (input && input.value === template.output_format) {
                card.classList.add('selected');
                input.checked = true;
            }
        });
        formData.output_format = template.output_format;
    }
    
    document.querySelectorAll('.btn-template').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.template === templateName) {
            btn.classList.add('active');
        }
    });
    
    showTemplateIndicator(template.name, templateName);
}

function showTemplateIndicator(name, key) {
    let indicator = document.querySelector('.template-selected');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'template-selected';
        indicator.innerHTML = '<span>Using template: <span class="template-name"></span></span><button type="button" class="clear-btn" onclick="clearTemplate()">✕ Clear</button>';
        const templateButtons = document.querySelector('.template-buttons');
        if (templateButtons) {
            templateButtons.after(indicator);
        }
    }
    
    indicator.querySelector('.template-name').textContent = name;
    indicator.classList.add('show');
}

function clearTemplate() {
    document.getElementById('agentName').value = '';
    document.getElementById('agentDescription').value = '';
    formData.agent_name = '';
    formData.agent_description = '';
    
    formData.required_fields = [];
    formData.field_hints = {};  // ← ADDED: Clear hints
    document.querySelectorAll('#fieldsContainer .field-tag').forEach(tag => tag.remove());
    updateHiddenFieldsInput();
    
    document.getElementById('promptTemplate').value = '';
    formData.prompt_template = '';
    
    document.getElementById('modelRole').value = '';
    formData.model_role = '';
    
    const modelSelect = document.getElementById('modelSelect');
    if (modelSelect && modelSelect.options.length > 0) {
        modelSelect.selectedIndex = 0;
        formData.model_id = modelSelect.value;
    }
    
    document.querySelectorAll('#toolsGrid input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
        const card = cb.closest('.tool-card');
        if (card) card.classList.remove('selected');
    });
    formData.tools = [];
    
    const formatCards = document.querySelectorAll('.format-card');
    formatCards.forEach((card, index) => {
        card.classList.remove('selected');
        const input = card.querySelector('input');
        if (index === 0 && input) {
            card.classList.add('selected');
            input.checked = true;
        }
    });
    formData.output_format = 'plain_text';
    
    document.querySelectorAll('.btn-template').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const indicator = document.querySelector('.template-selected');
    if (indicator) {
        indicator.classList.remove('show');
    }
}

async function loadTools() {
    try {
        const response = await fetch('/api/tools');
        const tools = await response.json();
        const grid = document.getElementById('toolsGrid');
        
        grid.innerHTML = tools.map(tool => '<div class="tool-card" data-tool-id="' + tool.id + '"><label class="tool-label"><input type="checkbox" name="tools" value="' + tool.id + '"><span class="tool-checkbox"></span><div class="tool-content"><span class="tool-name">' + tool.name + '</span><span class="tool-description">' + tool.description + '</span></div></label></div>').join('');

        grid.querySelectorAll('.tool-card').forEach(card => {
            const checkbox = card.querySelector('input[type="checkbox"]');
            checkbox.addEventListener('change', function() {
                card.classList.toggle('selected', this.checked);
            });
        });
    } catch (error) {
        console.error('Error loading tools:', error);
    }
}

async function loadFormats() {
    try {
        const response = await fetch('/api/formats');
        const formats = await response.json();
        const grid = document.getElementById('formatGrid');
        
        grid.innerHTML = formats.map((format, index) => '<div class="format-card ' + (index === 0 ? 'selected' : '') + '" data-format-id="' + format.id + '"><input type="radio" name="output_format" id="format_' + format.id + '" value="' + format.id + '" ' + (index === 0 ? 'checked' : '') + '><label for="format_' + format.id + '"><span class="format-name">' + format.name + '</span><span class="format-description">' + format.description + '</span></label></div>').join('');

        grid.querySelectorAll('.format-card').forEach(card => {
            card.addEventListener('click', function() {
                grid.querySelectorAll('.format-card').forEach(c => c.classList.remove('selected'));
                this.classList.add('selected');
                this.querySelector('input').checked = true;
            });
        });
    } catch (error) {
        console.error('Error loading formats:', error);
    }
}

async function loadModels() {
    try {
        const response = await fetch('/api/models');
        const models = await response.json();
        const select = document.getElementById('modelSelect');
        select.innerHTML = models.map(model => '<option value="' + model.id + '">' + model.name + '</option>').join('');
    } catch (error) {
        console.error('Error loading models:', error);
    }
}

function updateProgress() {
    const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;
    document.getElementById('progressFill').style.width = progress + '%';
    
    document.querySelectorAll('.step').forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove('active', 'completed');
        if (stepNum === currentStep) {
            step.classList.add('active');
        } else if (stepNum < currentStep) {
            step.classList.add('completed');
        }
    });
}

function showStep(step) {
    document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
    document.querySelector('.form-step[data-step="' + step + '"]').classList.add('active');
    
    document.getElementById('prevBtn').disabled = step === 1;
    
    if (step === totalSteps) {
        document.getElementById('nextBtn').style.display = 'none';
        document.getElementById('createBtn').style.display = 'inline-block';
        updateReview();
    } else {
        document.getElementById('nextBtn').style.display = 'inline-block';
        document.getElementById('createBtn').style.display = 'none';
    }
    
    updateProgress();
}

function collectFormData() {
    formData.agent_name = document.getElementById('agentName').value.trim();
    formData.agent_description = document.getElementById('agentDescription').value.trim();
    formData.model_id = document.getElementById('modelSelect').value;
    formData.model_role = document.getElementById('modelRole').value.trim();
    formData.max_tokens = parseInt(document.getElementById('maxTokens').value) || 1000;
    formData.temperature = parseFloat(document.getElementById('temperature').value) || 0.7;
    formData.prompt_template = document.getElementById('promptTemplate').value.trim();
    
    formData.tools = [];
    document.querySelectorAll('#toolsGrid input[type="checkbox"]:checked').forEach(cb => {
        formData.tools.push(cb.value);
    });
    
    const formatRadio = document.querySelector('input[name="output_format"]:checked');
    if (formatRadio) {
        formData.output_format = formatRadio.value;
    }
    
    // ← ADDED: Log hints being sent (for debugging)
    console.log('Sending formData with hints:', formData.field_hints);
}

function validateStep(step) {
    collectFormData();
    
    switch(step) {
        case 1:
            if (!formData.agent_name) {
                alert('Please enter an agent name');
                return false;
            }
            if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(formData.agent_name)) {
                alert('Agent name must start with a letter and contain only letters, numbers, and underscores');
                return false;
            }
            return true;
        case 2:
            if (!formData.model_role) {
                alert('Please enter a system role/persona');
                return false;
            }
            return true;
        case 3:
            const fieldInput = document.getElementById('fieldInput');
            if (fieldInput && fieldInput.value.trim()) {
                addFieldsFromInput(fieldInput.value);
                fieldInput.value = '';
            }
            if (formData.required_fields.length === 0) {
                alert('Please add at least one required field.');
                return false;
            }
            if (!formData.prompt_template) {
                alert('Please enter a prompt template');
                return false;
            }
            return true;
        default:
            return true;
    }
}

function nextStep() {
    if (validateStep(currentStep)) {
        currentStep++;
        showStep(currentStep);
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
    }
}

function updateReview() {
    collectFormData();
    
    const summary = document.getElementById('configSummary');
    summary.innerHTML = '<div class="summary-item"><strong>Name:</strong> ' + formData.agent_name + '</div><div class="summary-item"><strong>Description:</strong> ' + (formData.agent_description || 'N/A') + '</div><div class="summary-item"><strong>Model:</strong> ' + formData.model_id + '</div><div class="summary-item"><strong>Max Tokens:</strong> ' + formData.max_tokens + '</div><div class="summary-item"><strong>Temperature:</strong> ' + formData.temperature + '</div><div class="summary-item"><strong>Required Fields:</strong> ' + formData.required_fields.join(', ') + '</div><div class="summary-item"><strong>Tools:</strong> ' + (formData.tools.length > 0 ? formData.tools.join(', ') : 'None') + '</div><div class="summary-item"><strong>Output Format:</strong> ' + formData.output_format + '</div>';
    
    updateFilePreview('config');
}

async function updateFilePreview(fileType) {
    const preview = document.getElementById('filePreview');
    
    try {
        const response = await fetch('/api/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            let content = '';
            switch(fileType) {
                case 'config':
                    content = data.files['config.json'];
                    break;
                case 'agent':
                    content = data.files['agent.py'];
                    break;
                case 'readme':
                    content = data.files['README.txt'];
                    break;
            }
            preview.querySelector('code').textContent = content;
        }
    } catch (error) {
        preview.querySelector('code').textContent = 'Error generating preview';
    }
}



async function createAgent() {
    collectFormData();
    
    const createBtn = document.getElementById('createBtn');
    createBtn.disabled = true;
    createBtn.innerHTML = '<span class="btn-loading"></span> Generating...';

    try {
        const response = await fetch('/api/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show generated files in modal
            displayGeneratedFiles(data.files, data.agent_name);
        } else {
            document.getElementById('errorMessage').textContent = data.error;
            document.getElementById('errorModal').classList.add('show');
        }
    } catch (error) {
        document.getElementById('errorMessage').textContent = error.message;
        document.getElementById('errorModal').classList.add('show');
    }
    
    createBtn.disabled = false;
    createBtn.innerHTML = '📦 Create Agent';
}

function displayGeneratedFiles(files, agentName) {
    const modal = document.getElementById('successModal');
    const messageDiv = document.getElementById('successMessage');
    
    // Build file tree HTML
    let html = '<h3>✅ Agent Generated Successfully!</h3>';
    html += '<p>Copy the files below to create your agent:</p>';
    html += '<div class="download-section">';
    html += '<button class="btn-download" onclick="downloadAgentZip(\'' + agentName + '\')">📥 Download as ZIP</button>';
    html += '</div>';
    html += '<div class="files-container">';
    
    // Group files by category
    const fileGroups = {
        'Main Files': ['config.json', 'agent.py', 'web_app.py', 'README.txt'],
        'Core Infrastructure': ['core/utils.py', 'core/llm_caller.py', 'core/__init__.py', 'core/tools/__init__.py'],
        'Configuration': ['config/keys.yaml']
    };
    
    for (const [groupName, groupFiles] of Object.entries(fileGroups)) {
        html += '<div class="file-group">';
        html += '<h4>' + groupName + '</h4>';
        
        for (const filename of groupFiles) {
            if (files[filename]) {
                const fileId = 'file_' + filename.replace(/[^a-z0-9]/gi, '_');
                html += '<div class="file-item">';
                html += '<div class="file-header" onclick="toggleFile(\'' + fileId + '\')">';
                html += '<span class="file-icon">📄</span>';
                html += '<span class="file-name">' + filename + '</span>';
                html += '<button class="btn-copy-inline" onclick="event.stopPropagation(); copyFileContent(\'' + fileId + '\')">Copy</button>';
                html += '</div>';
                html += '<div class="file-content" id="' + fileId + '" style="display: none;">';
                html += '<pre><code>' + escapeHtml(files[filename]) + '</code></pre>';
                html += '</div>';
                html += '</div>';
            }
        }
        
        html += '</div>';
    }
    
    html += '</div>';
    
    messageDiv.innerHTML = html;
    modal.classList.add('show');
}

function toggleFile(fileId) {
    const content = document.getElementById(fileId);
    if (content.style.display === 'none') {
        content.style.display = 'block';
    } else {
        content.style.display = 'none';
    }
}

function copyFileContent(fileId) {
    const content = document.getElementById(fileId).querySelector('code').textContent;
    navigator.clipboard.writeText(content).then(() => {
        // Visual feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓ Copied!';
        btn.style.background = '#10b981';
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
        }, 2000);
    });
}

async function downloadAgentZip(agentName) {
    try {
        const response = await fetch('/api/download/' + agentName, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = agentName + '.zip';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            window.URL.revokeObjectURL(url);
        } else {
            alert('Download failed');
        }
    } catch (error) {
        alert('Download error: ' + error.message);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}


function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('show');
    }
});

