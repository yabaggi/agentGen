let currentStep = 1;
const totalSteps = 6;
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

const promptTemplates = {
    summarizer: {
        fields: ['content', 'length'],
        template: `Summarize the following content in {length} sentences:

{content}

Provide a clear, concise summary capturing the main points.`
    },
    flashcard: {
        fields: ['content', 'num_cards'],
        template: `Create {num_cards} flashcard Q&A pairs from this content:

{content}

Return as JSON array: [{"question": "...", "answer": "..."}]`
    },
    email: {
        fields: ['recipient', 'subject', 'tone', 'key_points'],
        template: `Write a {tone} email to {recipient} about: {subject}

Key points to include:
{key_points}

Output only the email text with appropriate greeting and signature.`
    },
    qa: {
        fields: ['context', 'question'],
        template: `Based on the following context, answer the question.

Context:
{context}

Question: {question}

Provide a clear and accurate answer based only on the given context.`
    }
};

document.addEventListener('DOMContentLoaded', function() {
    loadTools();
    loadFormats();
    loadModels();
    setupEventListeners();
    updateProgress();
});

function setupEventListeners() {
    document.getElementById('prevBtn').addEventListener('click', prevStep);
    document.getElementById('nextBtn').addEventListener('click', nextStep);
    document.getElementById('createBtn').addEventListener('click', createAgent);

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

    document.querySelectorAll('.btn-template').forEach(btn => {
        btn.addEventListener('click', function() {
            applyTemplate(this.dataset.template);
        });
    });

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
    tag.innerHTML = field + ' <button type="button" onclick="removeField(\'' + field + '\', this)">&times;</button>';
    container.insertBefore(tag, input);
}

function removeField(field, button) {
    formData.required_fields = formData.required_fields.filter(f => f !== field);
    button.parentElement.remove();
    updateHiddenFieldsInput();
}

function updateHiddenFieldsInput() {
    document.getElementById('requiredFields').value = formData.required_fields.join(',');
}

function applyTemplate(templateName) {
    const template = promptTemplates[templateName];
    if (!template) return;
    formData.required_fields = [];
    document.querySelectorAll('#fieldsContainer .field-tag').forEach(tag => tag.remove());
    template.fields.forEach(field => {
        formData.required_fields.push(field);
        addFieldTag(field);
    });
    updateHiddenFieldsInput();
    document.getElementById('promptTemplate').value = template.template;
    formData.prompt_template = template.template;
}
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

function updateProgress() {
    const progress = ((currentStep - 1) / (totalSteps - 1)) * 100;
    document.getElementById('progressFill').style.width = progress + '%';
    document.querySelectorAll('.step').forEach((step, index) => {
        const stepNum = index + 1;
        step.classList.remove('active', 'completed');
        if (stepNum === currentStep) step.classList.add('active');
        else if (stepNum < currentStep) step.classList.add('completed');
    });
}

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
    if (formatRadio) formData.output_format = formatRadio.value;
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
                case 'config': content = data.files['config.json']; break;
                case 'agent': content = data.files['agent.py']; break;
                case 'readme': content = data.files['README.md']; break;
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

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('show');
}

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('show');
    }
});
