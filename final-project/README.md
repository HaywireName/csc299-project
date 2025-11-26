# PKMS Task Manager

A powerful, terminal-based Personal Knowledge Management System (PKMS) with integrated task management, document library, and AI-powered features.

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🌟 Features

### 📋 Task Management
- **Smart Task Organization**: Create, edit, and track tasks with priorities, deadlines, and descriptions
- **Intelligent Sorting**: Tasks sorted by priority → nearest deadline → oldest first
- **Visual Deadline Indicators**: Color-coded deadlines (red for overdue, yellow for due within 2 days)
- **Dual ID System**: Numeric IDs for pending tasks (1, 2, 3...), letter IDs for completed tasks (a, b, c...)
- **Folder System**: Organize tasks into custom folders for projects or categories
- **Flexible Deadlines**: Support for multiple date formats (DD-MM-YYYY, MM/DD/YYYY, "tomorrow", etc.)
- **AI Summarization**: Automatically generate concise summaries for lengthy task descriptions (20+ words)
- **Status Tracking**: Monitor pending, completed, and overdue tasks

### 📄 Document Library
- **Multi-Format Support**: Manage PDF, DOCX, and TXT documents in one place
- **Auto-Metadata Extraction**: Automatically extract titles, page counts, and previews
- **Text Extraction**: Extract full or partial text with intelligent caching
- **AI-Powered Summaries**: Generate document summaries using GPT-4o-mini
- **Selective Summary Removal**: Remove only summaries (not documents) with `-s` flag to save storage while keeping files
- **Full-Text Search**: Search across all documents with context highlighting
- **Smart Organization**: Recently accessed documents appear first

### 💬 AI Chat Assistant
- **Conversational Interface**: Natural language interaction with GPT-4o
- **Context-Aware**: Load context from tasks, documents, or both
- **Session Management**: Persistent conversation history
- **Cost Tracking**: Monitor API usage and costs in real-time
- **Streaming Responses**: See AI responses as they're generated

### 🤖 AI Agent System
- **Task Analysis**: Intelligent insights and recommendations for task management
- **Document Synthesis**: Combine information from multiple documents
- **Contextual Intelligence**: Agents understand your entire knowledge base

### 💾 Data Management
- **Automatic Backups**: Auto-backup on program start
- **Export/Import**: Full data portability with ZIP archives
- **Manual Backups**: Create backups anytime
- **Easy Restoration**: Restore from any backup with confirmation

## 📋 Requirements

- **Python**: 3.9 or higher
- **OpenAI API Key**: Required for AI features (chat, summaries, agents)
- **Operating System**: macOS, Linux, or Windows
- **Dependencies**: See `requirements.txt`

## 🚀 Quick Start

### Installation

#### Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HaywireName/csc299-project.git
   cd csc299-project/final-project
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   
   # Activate it:
   # macOS/Linux:
   source venv/bin/activate
   
   # Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your OpenAI API key:**
   ```bash
   # macOS/Linux:
   export OPENAI_API_KEY='sk-your-key-here'
   
   # Windows PowerShell:
   $env:OPENAI_API_KEY="sk-your-key-here"
   
   # Windows CMD:
   set OPENAI_API_KEY=sk-your-key-here
   ```
   
   For permanent setup, add to `.env` file or your shell profile.

5. **Run the application:**
   ```bash
   python main.py
   ```

## 📖 Usage Examples

### Task Management

```bash
# Enter tasks module
pkms> tasks

# Add a task with deadline and priority
tasks[default]> add "Write project report" -p high -dl 2025-12-01

# Add a task with description
tasks[default]> add "Research AI tools" -desc Look into GPT-4 alternatives and compare pricing

# List all tasks (sorted by priority → deadline → age)
# Red deadlines = overdue, yellow = due within 2 days
tasks[default]> list

# Create and switch folders
tasks[default]> folder -a work
tasks[default]> folder work

# View task details
tasks[work]> view 1

# Edit task with short flags
tasks[work]> edit 1 -p medium -dl tomorrow

# Mark task complete (ID becomes letter: a, b, c...)
tasks[work]> complete 1

# Edit or remove completed task
tasks[work]> edit a -desc Updated description
tasks[work]> remove b

# Search tasks
tasks[work]> search report
```

### Document Management

```bash
# Enter docs module
pkms> docs

# Add a document
docs> add ~/Documents/research-paper.pdf

# List all documents
docs> list

# View document details
docs> view 1

# Extract text from document
docs> extract 1

# Search across all documents
docs> search "machine learning"

# Generate AI summary
docs> summarize 1

# Remove only summary (keep document)
docs> remove -s 1

# Remove entire document
docs> remove 1
```

### AI Chat

```bash
# Enter chat module
pkms> chat

# Start chat with task context
chat> /context tasks

# In chat mode:
chat[tasks]> What tasks are due this week?
chat[tasks]> Help me prioritize my work
chat[tasks]> /home
```

### Program Commands

```bash
# Restore previous version
pkms> restore [name]

# Check current context
pkms> status

# Create backup
pkms> backup
pkms> backup [name]

# Get help
pkms> help
```

## 📚 Documentation

- **[COMMANDS.md](COMMANDS.md)**: Complete command reference
- **[USER_GUIDE.md](USER_GUIDE.md)**: Step-by-step tutorials and workflows
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Technical documentation and system design

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required for AI features)

### Data Storage

All data is stored in the `data/` directory:
- `tasks.json`: Task data organized by folders
- `docs_metadata.json`: Document metadata and summaries
- `chat_history.json`: Chat conversation history
- `settings.json`: Application settings
- `docs/`: Document files (PDF, DOCX, TXT)
- `doc_cache/`: Extracted text cache
- `backups/`: Automatic and manual backups

## 🐛 Troubleshooting

### API Key Issues

**Problem**: `OpenAI API Key Not Found`

**Solution**:
1. Ensure your API key is set correctly:
   ```bash
   echo $OPENAI_API_KEY  # macOS/Linux
   echo %OPENAI_API_KEY%  # Windows CMD
   ```
2. Verify the key starts with `sk-`
3. Remove any quotes from environment variable
4. Restart your terminal after setting the key

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**:
1. Activate your virtual environment
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Permission Errors

**Problem**: Cannot write to data directory

**Solution**:
1. Check directory permissions
2. Run from your user directory, not system directories
3. On Unix systems: `chmod -R u+w data/`

### Rate Limits

**Problem**: OpenAI rate limit exceeded

**Solution**:
1. The program automatically retries with exponential backoff
2. Wait a few minutes before making more API calls
3. Check your OpenAI usage limits at platform.openai.com

### Corrupted Data

**Problem**: JSON decode errors

**Solution**:
1. Restore from backup: `pkms> restore`
2. Check `data/backups/` for auto-backups
3. Manually fix JSON files (ensure valid JSON syntax)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python run_tests.py

# Run specific test file
python -m pytest tests/test_tasks.py -v

# Run with coverage
python run_tests.py --coverage
```

## 🤝 Contributing

This is an academic project. For questions or suggestions, please open an issue on GitHub.

## 📄 License

MIT License

Copyright (c) 2025 PKMS Task Manager Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 📞 Support

- **Documentation**: See USER_GUIDE.md for detailed instructions
- **Issues**: Report bugs on GitHub
- **Questions**: Check ARCHITECTURE.md for technical details

## 🙏 Acknowledgments

- Built with Python and OpenAI GPT-4o
- Inspired by personal knowledge management systems
- Developed for CSC299 course project

---

**Version**: 1.0.0  
**Last Updated**: November 2025
