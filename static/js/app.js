let currentStep = 1;
const totalSteps = 6;
let promptTemplates = {};
let formData = {
    agent_name: '',
    agent_description: '',
    model_id: 'gemini-flash',
    model_role: '',
    max_tokens: 1000,
    temperature: 0.7,
    required_fields: [],
    prompt_template: '',
    tools: [],
    output_format: 'plain_text'
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadTemplates();
    loadTools();
    loadFormats();
    loadModels();
    setupEventListeners();
    updateProgress();
});

// Load templates from JSON file
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

// Render template buttons dynamically
function renderTemplateButtons() {
    const container = document.querySelector('.template-buttons');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Show only first 6 templates as buttons
    const templateEntries = Object.entries(promptTemplates);
    const visibleTemplates = templateEntries.slice(0, 6);
    
    for (const [key, template] of visibleTemplates) {
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
    
    // Show count of additional templates
    if (templateEntries.length > 6) {
        const moreBtn = document.createElement('button');
        moreBtn.type = 'button';
        moreBtn.className = 'btn-template';
        moreBtn.textContent = `+${templateEntries.length - 6} more`;
        moreBtn.title = 'Click "All Templates" to see more';
        moreBtn.addEventListener('click', toggleDropdown);
        container.appendChild(moreBtn);
    }
}

// Render dropdown menu with all templates
function renderDropdownMenu() {
    const container = document.getElementById('dropdownContent');
    if (!container) return;
    
    container.innerHTML = '';
    
    for (const [key, template] of Object.entries(promptTemplates)) {
        const item = document.createElement('div');
        item.className = 'dropdown-item';
        item.dataset.template = key;
        item.innerHTML = `
            <div class="dropdown-item-name">${template.name}</div>
            <div class="dropdown-item-desc">${template.description}</div>
        `;
        item.addEventListener('click', function() {
            applyTemplate(this.dataset.template);
            closeDropdown();
        });
        container.appendChild(item);
    }
}

// Toggle dropdown menu
function toggleDropdown() {
    const dropdown = document.getElementById('dropdownMenu');
    dropdown.classList.toggle('show');
}

// Close dropdown menu
function closeDropdown() {
    const dropdown = document.getElementById('dropdownMenu');
    dropdown.classList.remove('show');
}

// Setup all event listeners
function setupEventListeners() {
    document.getElementById('prevBtn').addEventListener('click', prevStep);
    document.getElementById('nextBtn').addEventListener('click', nextStep);
    document.getElementById('createBtn').addEventListener('click', createAgent);

    // Hamburger button
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', toggleDropdown);
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        const dropdown = document.getElementById('dropdownMenu');
        const hamburgerBtn = document.getElementById('hamburgerBtn');
        if (dropdown && hamburgerBtn && !dropdown.contains(e.target) && !hamburgerBtn.contains(e.target)) {
            closeDropdown();
        }
    });

    // Temperature slider
    const tempSlider = document.getElementById('temperature');
    if (tempSlider) {
        tempSlider.addEventListener('input', function() {
            document.getElementById('tempValue').textContent = this.value;
        });
    }

    // Field input handler
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

    // Tab buttons for file preview
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            updateFilePreview(this.dataset.tab);
        });
    });
}

// Add fields from input
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

// Add field tag element
function addFieldTag(field) {
    const container = document.getElementById('fieldsContainer');
    const input = document.getElementById('fieldInput');
    const tag = document.createElement('span');
    tag.className = 'field-tag';
    tag.dataset.field = field;
    tag.innerHTML = `${field} <button type="button" onclick="removeField('${field}', this)">×</button>`;
    container.insertBefore(tag, input);
}

// Remove field
function removeField(field, button) {
    formData.required_fields = formData.required_fields.filter(f => f !== field);
    button.parentElement.remove();
    updateHiddenFieldsInput();
}

// Update hidden input
function updateHiddenFieldsInput() {
    document.getElementById('requiredFields').value = formData.required_fields.join(',');
}
// Apply template - AUTO POPULATES ALL FIELDS
function applyTemplate(templateName) {
    const template = promptTemplates[templateName];
    if (!template) return;
    
    // 1. Set Agent Name
    if (template.agent_name) {
        document.getElementById('agentName').value = template.agent_name;
        formData.agent_name = template.agent_name;
    }
    
    // 2. Set Agent Description
    if (template.description) {
        document.getElementById('agentDescription').value = template.description;
        formData.agent_description = template.description;
    }
    
    // 3. Clear existing fields and add new ones
    formData.required_fields = [];
    document.querySelectorAll('#fieldsContainer .field-tag').forEach(tag => tag.remove());
    
    template.fields.forEach(field => {
        formData.required_fields.push(field);
        addFieldTag(field);
    });
    updateHiddenFieldsInput();
    
    // 4. Set prompt template
    document.getElementById('promptTemplate').value = template.template;
    formData.prompt_template = template.template;
    
    // 5. Set model role
    if (template.role) {
        document.getElementById('modelRole').value = template.role;
        formData.model_role = template.role;
    }
    
    // 6. Set suggested model
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
    
    // 7. Set tools
    // First, uncheck all tools
    document.querySelectorAll('#toolsGrid input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
        cb.closest('.tool-card')?.classList.remove('selected');
    });
    
    // Then check the template's tools
    if (template.tools && Array.isArray(template.tools)) {
        template.tools.forEach(toolId => {
            const checkbox = document.querySelector(`#toolsGrid input[value="${toolId}"]`);
            if (checkbox) {
                checkbox.checked = true;
                checkbox.closest('.tool-card')?.classList.add('selected');
            }
        });
        formData.tools = [...template.tools];
    } else {
        formData.tools = [];
    }
    
    // 8. Set output format
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
    
    // 9. Visual feedback - highlight active template button
    document.querySelectorAll('.btn-template').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.template === templateName) {
            btn.classList.add('active');
        }
    });
    
    // 10. Show selected template indicator
    showTemplateIndicator(template.name, templateName);
}

// Show template indicator
function showTemplateIndicator(name, key) {
    let indicator = document.querySelector('.template-selected');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'template-selected';
        indicator.innerHTML = `
            <span>Using template: <span class="template-name"></span></span>
            <button type="button" class="clear-btn" onclick="clearTemplate()">✕ Clear</button>
        `;
        const templateButtons = document.querySelector('.template-buttons');
        if (templateButtons) {
            templateButtons.after(indicator);
        }
    }
    
    indicator.querySelector('.template-name').textContent = name;
    indicator.classList.add('show');
}

// Clear template
function clearTemplate() {
    // Clear agent name and description
    document.getElementById('agentName').value = '';
    document.getElementById('agentDescription').value = '';
    formData.agent_name = '';
    formData.agent_description = '';
    
    // Clear fields
    formData.required_fields = [];
    document.querySelectorAll('#fieldsContainer .field-tag').forEach(tag => tag.remove());
    updateHiddenFieldsInput();
    
    // Clear prompt
    document.getElementById('promptTemplate').value = '';
    formData.prompt_template = '';
    
    // Clear model role
    document.getElementById('modelRole').value = '';
    formData.model_role = '';
    
    // Reset model to default
    const modelSelect = document.getElementById('modelSelect');
    if (modelSelect && modelSelect.options.length > 0) {
        modelSelect.selectedIndex = 0;
        formData.model_id = modelSelect.value;
    }
    
    // Clear all tools
    document.querySelectorAll('#toolsGrid input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
        cb.closest('.tool-card')?.classList.remove('selected');
    });
    formData.tools = [];
    
    // Reset output format to default
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
    
    // Remove active state from buttons
    document.querySelectorAll('.btn-template').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Hide indicator
    const indicator = document.querySelector('.template-selected');
    if (indicator) {
        indicator.classList.remove('show');
    }
}

// Load tools from API
async function loadTools() {
    try {
        const response = await fetch('/api/tools');
        const tools = await response.json();
        const grid = document.getElementById('toolsGrid');
        
        grid.innerHTML = tools.map(tool => `
            <div class="tool-card" data-tool-id="${tool.id}">
                <label class="tool-label">
                    <input type="checkbox" name="tools" value="${tool.id}">
                    <span class="tool-checkbox"></span>
                    <div class="tool-content">
                        <span class="tool-name">${tool.name}</span>
                        <span class="tool-description">${tool.description}</span>
                    </div>
                </label>
            </div>
        `).join('');

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

// Load formats from API
async function loadFormats() {
    try {
        const response = await fetch('/api/formats');
        const formats = await response.json();
        const grid = document.getElementById('formatGrid');
        
        grid.innerHTML = formats.map((format, index) => `
            <div class="format-card ${index === 0 ? 'selected' : ''}" data-format-id="${format.id}">
                <input type="radio" name="output_format" id="format_${format.id}" 
                       value="${format.id}" ${index === 0 ? 'checked' : ''}>
                <label for="format_${format.id}">
                    <span class="format-name">${format.name}</span>
                    <span class="format-description">${format.description}</span>
                </label>
            </div>
        `).join('');

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

// Load models from API
async function loadModels() {
    try {
        const response = await fetch('/api/models');
        const models = await response.json();
        const select = document.getElementById('modelSelect');
        select.innerHTML = models.map(model => 
            `<option value="${model.id}">${model.name}</option>`
        ).join('');
    } catch (error) {
        console.error('Error loading models:', error);
    }
}
// Update progress bar
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

// Show specific step
function showStep(step) {
    document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
    document.querySelector(`.form-step[data-step="${step}"]`).classList.add('active');
    
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

// Collect all form data
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
}

// Validate current step
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
                alert('Please add at least one required field.\n\nType field names separated by commas, then press Enter.');
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

// Go to next step
function nextStep() {
    if (validateStep(currentStep)) {
        currentStep++;
        showStep(currentStep);
    }
}

// Go to previous step
function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
    }
}

// Update review section
function updateReview() {
    collectFormData();
    
    const summary = document.getElementById('configSummary');
    summary.innerHTML = `
        <div class="summary-item"><strong>Name:</strong> ${formData.agent_name}</div>
        <div class="summary-item"><strong>Description:</strong> ${formData.agent_description || 'N/A'}</div>
        <div class="summary-item"><strong>Model:</strong> ${formData.model_id}</div>
        <div class="summary-item"><strong>Max Tokens:</strong> ${formData.max_tokens}</div>
        <div class="summary-item"><strong>Temperature:</strong> ${formData.temperature}</div>
        <div class="summary-item"><strong>Required Fields:</strong> ${formData.required_fields.join(', ')}</div>
        <div class="summary-item"><strong>Tools:</strong> ${formData.tools.length > 0 ? formData.tools.join(', ') : 'None'}</div>
        <div class="summary-item"><strong>Output Format:</strong> ${formData.output_format}</div>
    `;
    
    updateFilePreview('config');
}

// Update file preview
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
                    content = data.files['README.md'];
                    break;
            }
            preview.querySelector('code').textContent = content;
        }
    } catch (error) {
        preview.querySelector('code').textContent = 'Error generating preview';
    }
}

// Create the agent
async function createAgent() {
    collectFormData();
    
    const createBtn = document.getElementById('createBtn');
    createBtn.disabled = true;
    createBtn.textContent = 'Creating...';

    try {
        const response = await fetch('/api/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('successMessage').innerHTML = `
                Agent created at:<br>
                <code>${data.path}</code><br><br>
                <strong>Files created:</strong><br>
                • config.json<br>
                • agent.py<br>
                • web_app.py (Web Interface)<br>
                • run_cli.py (CLI)<br>
                • README.md<br><br>
                <strong>To run:</strong><br>
                <code>cd ${data.path} && python web_app.py</code>
            `;
            document.getElementById('successModal').classList.add('show');
        } else {
            document.getElementById('errorMessage').textContent = data.error;
            document.getElementById('errorModal').classList.add('show');
        }
    } catch (error) {
        document.getElementById('errorMessage').textContent = error.message;
        document.getElementById('errorModal').classList.add('show');
    }
    
    createBtn.disabled = false;
    createBtn.textContent = '🚀 Create Agent';
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

// Close modal on backdrop click
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('show');
    }
});
