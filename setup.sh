#!/bin/sh
##################################################################
#  setup.sh - Creates the AI Agent Generator project structure
##################################################################

PROJECT_NAME="agent_generator"

echo "Creating $PROJECT_NAME..."

# Create directories
mkdir -p "$PROJECT_NAME/static/css"
mkdir -p "$PROJECT_NAME/static/js"
mkdir -p "$PROJECT_NAME/templates"
mkdir -p "$PROJECT_NAME/generated_agents"

echo "Folder structure created!"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. Copy the following files to their locations:"
echo "   - app.py"
echo "   - templates/index.html"
echo "   - static/css/style.css"
echo "   - static/js/app.js"
echo "   - requirements.txt"
echo "3. pip install -r requirements.txt"
echo "4. python app.py"
echo "5. Open http://localhost:5000"
