#!/bin/bash

# PKMS Task Manager Installation Script for Unix/Mac
# This script sets up the environment and installs all dependencies

set -e  # Exit on error

echo "================================"
echo "PKMS Task Manager Installation"
echo "================================"
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PIP_CMD=pip3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    PIP_CMD=pip
else
    echo "❌ Error: Python not found"
    echo "Please install Python 3.9 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"

# Check if version is 3.9+
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info[1])')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "❌ Error: Python 3.9 or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "✓ Virtual environment already exists"
else
    $PYTHON_CMD -m venv venv
    echo "✓ Virtual environment created"
fi

echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""

# Upgrade pip
echo "Upgrading pip..."
$PIP_CMD install --upgrade pip > /dev/null 2>&1
echo "✓ Pip upgraded"

echo ""

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    $PIP_CMD install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p data/docs/pdfs
mkdir -p data/docs/docx
mkdir -p data/docs/txt
mkdir -p data/doc_cache
mkdir -p data/backups
mkdir -p exports
echo "✓ Data directories created"

echo ""

# Check for API key
echo "Checking for OpenAI API key..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OpenAI API key not found"
    echo ""
    echo "To use AI features, you need to set your OpenAI API key:"
    echo ""
    echo "  For current session:"
    echo "    export OPENAI_API_KEY='sk-your-key-here'"
    echo ""
    echo "  For permanent setup (add to ~/.bashrc or ~/.zshrc):"
    echo "    echo \"export OPENAI_API_KEY='sk-your-key-here'\" >> ~/.bashrc"
    echo "    source ~/.bashrc"
    echo ""
    echo "Get your API key at: https://platform.openai.com/api-keys"
else
    echo "✓ OpenAI API key found"
fi

echo ""
echo "================================"
echo "Installation Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate the virtual environment (if not already active):"
echo "   source venv/bin/activate"
echo ""
echo "2. Set your OpenAI API key (if not already set):"
echo "   export OPENAI_API_KEY='sk-your-key-here'"
echo ""
echo "3. Run the application:"
echo "   python main.py"
echo ""
echo "For help, see:"
echo "  - README.md for overview"
echo "  - USER_GUIDE.md for tutorials"
echo "  - COMMANDS.md for command reference"
echo ""
echo "Happy organizing! 🚀"
echo ""
