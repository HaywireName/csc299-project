# USER_GUIDE.md - Comprehensive User Guide

Complete guide to using PKMS Task Manager effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Task Management Tutorial](#task-management-tutorial)
3. [Document Library Guide](#document-library-guide)
4. [AI Chat Assistant](#ai-chat-assistant)
5. [AI Agents](#ai-agents)
6. [Data Management](#data-management)
7. [Common Workflows](#common-workflows)
8. [Tips and Tricks](#tips-and-tricks)
9. [Best Practices](#best-practices)

---

## Getting Started

### First Launch

1. Ensure your OpenAI API key is set
2. Run: `python main.py`
3. You'll see the main menu with quick stats
4. Type `help` to see available commands

### Understanding the Interface

**Prompts**:
- `pkms>`: Main menu
- `tasks[folder]>`: Tasks module
- `docs>`: Documents module
- `chat>`: Chat module
- `agent>`: Agent module

**Context**: The prompt shows your current location. Commands are context-sensitive.

### Your First Actions

```bash
# 1. Create a task
pkms> tasks
tasks[default]> add "Learn PKMS" -p high

# 2. Add a document
tasks[default]> home
pkms> docs
docs> add ~/Documents/guide.pdf

# 3. Check status
docs> home
pkms> stats
```

---

## Task Management Tutorial

### Creating Tasks

**Basic Task**:
```bash
tasks> add "Buy groceries"
```

**Task with Priority**:
```bash
tasks> add "Submit report" -p high
```

**Task with Deadline**:
```bash
tasks> add "Team meeting" -dl 2025-12-01
```

**Complete Task**:
```bash
tasks> add "Research project" -p high -desc "Investigate AI applications in education including GPT models and automated grading systems" -dl tomorrow
```

### Organizing with Folders

**Create Project Folders**:
```bash
tasks> folder -a work
tasks> folder -a personal
tasks> folder -a urgent
```

**Switch Between Folders**:
```bash
tasks> folder work
tasks[work]> add "Prepare presentation"
tasks[work]> folder personal
tasks[personal]> add "Call dentist"
```

**View All Folders**:
```bash
tasks> folders
```

### Managing Tasks

**View Task List**:
```bash
tasks> list
```

**View Task Details**:
```bash
tasks> view 1
```

**Edit Task**:
```bash
# Update deadline
tasks> edit 1 --deadline 2025-12-15

# Change priority
tasks> edit 1 --priority high

# Add description
tasks> edit 1 --description "New details about the task"
```

**Complete Tasks**:
```bash
# Single task
tasks> complete 1

# Multiple tasks
tasks> complete 1 2 3
```

**Search Tasks**:
```bash
tasks> search report
tasks> search urgent meeting
```

### AI Task Summaries

For tasks with long descriptions (20+ words):

```bash
tasks> summarize 1
```

This generates a concise 10-15 word summary using AI.

### Example Workflow: Weekly Planning

```bash
# 1. Create work folder
tasks> folder -a week-48

# 2. Add this week's tasks
tasks[week-48]> add "Monday: Team standup" -dl 2025-11-25
tasks[week-48]> add "Tuesday: Client presentation" -p high -dl 2025-11-26
tasks[week-48]> add "Wednesday: Code review" -dl 2025-11-27
tasks[week-48]> add "Thursday: Documentation" -dl 2025-11-28
tasks[week-48]> add "Friday: Sprint retrospective" -dl 2025-11-29

# 3. View weekly tasks
tasks[week-48]> list

# 4. As week progresses, mark tasks complete
tasks[week-48]> complete 1
```

---

## Document Library Guide

### Adding Documents

**Single Document**:
```bash
docs> add ~/Documents/research-paper.pdf
```

**Multiple Documents**:
```bash
docs> add ~/Documents/paper1.pdf
docs> add ~/Documents/paper2.docx
docs> add ~/Documents/notes.txt
```

**Drag and Drop** (if supported by terminal):
- Some terminals allow dragging files to get full paths

### Viewing Documents

**List All Documents**:
```bash
docs> list
```

**View Document Details**:
```bash
docs> view 1
```

This shows:
- Title (auto-extracted)
- File type and size
- Added and accessed dates
- Summary (if generated)
- Preview text

### Extracting Text

**Full Document**:
```bash
docs> extract 1
```

**Specific Page** (PDFs only):
```bash
docs> extract 1 --page 5
```

Text is cached for faster future access.

### Searching Documents

**Simple Search**:
```bash
docs> search "machine learning"
```

**Multiple Words**:
```bash
docs> search methodology results
```

Results show:
- Document title and ID
- Page number (for PDFs)
- Context with search term highlighted

### Intelligent Title Extraction

Documents are automatically assigned meaningful titles extracted from their content:

**How it works**:
- PDFs: Extracts title from first page if metadata is generic (e.g., "(anonymous)")
- DOCX: Extracts title from document content if properties show "Word Document"
- TXT: Finds first meaningful line, skipping empty lines and page numbers
- Fallback: Uses filename if no content-based title can be extracted

**Features**:
- Skips page markers ("--- Page 1 ---") and numbers
- Ignores very short lines (< 3 characters)
- Truncates very long titles to 100 characters
- Preserves original document content

**Refresh Titles**:
If you have old documents with generic titles, update them:
```bash
docs> refresh
```

This re-extracts titles for all documents with generic names.

### AI Document Summaries

**Generate Summary**:
```bash
docs> summarize 1
```

**Custom Length**:
```bash
docs> summarize 1 --max-words 300
```

Summaries are saved and displayed in `list` and `view` commands.

### Example Workflow: Research Paper Library

```bash
# 1. Add papers
docs> add ~/Research/ml-basics.pdf
docs> add ~/Research/deep-learning.pdf
docs> add ~/Research/nlp-survey.pdf

# 2. Generate summaries
docs> summarize 1
docs> summarize 2
docs> summarize 3

# 3. Search across papers
docs> search "neural networks"
docs> search "attention mechanism"

# 4. Extract relevant sections
docs> extract 2 --page 10

# 5. View organized list
docs> list
```

---

## AI Chat Assistant

### Starting a Chat

**Basic Chat**:
```bash
chat> chat
```

**Chat with Task Context**:
```bash
chat> chat --context tasks
```

**Chat with Document Context**:
```bash
chat> chat --context pdfs
```

**Chat with All Context**:
```bash
chat> chat --context all
```

### In-Chat Commands

While in chat mode, use slash commands:

```
chat[tasks]> /help          # Show chat commands
chat[tasks]> /context all   # Switch context
chat[tasks]> /clear         # Clear history
chat[tasks]> /cost          # Check API usage
chat[tasks]> /exit          # Leave chat
```

### Example Conversations

**Task Help**:
```
chat> chat --context tasks
chat[tasks]> What tasks do I have due this week?
chat[tasks]> Which high-priority tasks should I focus on?
chat[tasks]> Help me organize my work tasks
```

**Document Questions**:
```
chat> chat --context pdfs
chat[pdfs]> What are the main topics in my documents?
chat[pdfs]> Summarize the key findings from my research papers
chat[pdfs]> Which documents discuss machine learning?
```

**Combined Context**:
```
chat> chat --context all
chat[all]> What should I prioritize today based on my tasks and research?
chat[all]> Help me plan next week considering my deadlines
```

### Conversation Management

**Clear History**:
```
chat[tasks]> /clear
```

This removes conversation history while staying in chat mode.

**Switch Context**:
```
chat[tasks]> /context pdfs
```

Loads new context without restarting chat.

**Check Costs**:
```
chat[tasks]> /cost
```

Shows API usage and costs for current session.

---

## AI Agents

### Task Analysis

Analyzes your tasks and provides insights:

```bash
agent> analyze
```

**Provides**:
- Priority recommendations
- Overdue task warnings
- Workload balance
- Time management tips

### Document Synthesis

Combines information from multiple documents:

```bash
agent> synthesize 1 2 3
```

**Provides**:
- Common themes
- Key insights
- Relationships between documents

### Example Workflow: Weekly Review

```bash
# 1. Analyze tasks
agent> analyze
# Review priorities and adjust as needed

# 2. Synthesize week's reading
agent> synthesize 1 2 3 4
# Get overview of research

# 3. Chat for planning
agent> home
pkms> chat
chat> chat --context all
chat[all]> Based on my tasks and readings, what should I focus on next week?
```

---

## Data Management

### Backups

**Automatic Backups**:
- Created on program start
- Stored in `data/backups/`
- Format: `backup_YYYYMMDD_HHMMSS.zip`

**Manual Backup**:
```bash
pkms> backup
```

**Restore from Backup**:
```bash
# List backups
pkms> restore

# Restore specific backup
pkms> restore backup_20251124_103045.zip
```

### Export and Import

**Export All Data**:
```bash
pkms> export
```

Creates ZIP in `exports/` directory with:
- All tasks
- All documents
- Chat history
- Settings

**Import Data**:
```bash
pkms> import exports/pkms_export_20251124_103045.zip
```

Choose mode:
- `merge`: Combine with existing data
- `replace`: Replace all data (creates backup first)

### Storage Locations

```
data/
├── tasks.json              # Task data
├── docs_metadata.json      # Document metadata
├── chat_history.json       # Chat conversations
├── settings.json           # App settings
├── docs/                   # Document files
│   ├── pdfs/
│   ├── docx/
│   └── txt/
├── doc_cache/              # Extracted text
└── backups/                # Auto and manual backups

exports/                    # Export archives
```

---

## Common Workflows

### Daily Task Review

```bash
pkms> tasks
tasks[default]> list
# Review today's tasks

tasks[default]> complete <completed_ids>
# Mark completed tasks

tasks[default]> add "New task" -dl tomorrow
# Add tomorrow's tasks

tasks[default]> home
pkms> stats
# Check overall progress
```

### Research Session

```bash
# 1. Add new papers
pkms> docs
docs> add ~/Downloads/paper1.pdf
docs> add ~/Downloads/paper2.pdf

# 2. Generate summaries
docs> summarize 1
docs> summarize 2

# 3. Search for topics
docs> search "methodology"

# 4. Extract relevant sections
docs> extract 1

# 5. Ask AI about papers
docs> home
pkms> chat
chat> chat --context pdfs
chat[pdfs]> Compare the methodologies in my recent papers
```

### Weekly Planning

```bash
# 1. Review last week
pkms> tasks
tasks[default]> folder last-week
tasks[last-week]> list

# 2. Create this week's folder
tasks[last-week]> folder -a this-week
tasks[this-week]> add "Monday tasks" -dl 2025-12-02
tasks[this-week]> add "Tuesday tasks" -dl 2025-12-03
# ... add all week's tasks

# 3. Get AI insights
tasks[this-week]> home
pkms> agent
agent> analyze

# 4. Plan with AI
agent> home
pkms> chat
chat> chat --context tasks
chat[tasks]> Help me prioritize this week's tasks
```

### Document Organization

```bash
# 1. Add all documents
pkms> docs
docs> add ~/Documents/*.pdf
# (Add each file individually)

# 2. Generate summaries for all
docs> list
docs> summarize 1
docs> summarize 2
# ... for each document

# 3. Search and tag
docs> search "project X"
# Note relevant document IDs

# 4. Synthesize related documents
docs> home
pkms> agent
agent> synthesize 1 3 5
# Combine related documents
```

---

## Tips and Tricks

### Keyboard Shortcuts

- **↑/↓ arrows**: Navigate command history
- **Ctrl+C**: Cancel current operation
- **Ctrl+D**: Exit program (same as `exit`)

### Partial ID Matching

Don't type full IDs:
```bash
# Instead of:
tasks> view a3d5f2b8

# Use:
tasks> view a3d5
# or even:
tasks> view a3
```

### Command Aliases

- `exit` = `quit`
- `home` = `menu`

### Date Format Tips

Multiple formats supported:
```bash
tasks> add "Task" -dl 25-12-2025
tasks> add "Task" -dl 12/25/2025
tasks> add "Task" -dl tomorrow
```

### Search Tips

- Searches are case-insensitive
- Multi-word queries search for all words
- Use quotes for exact phrases (in some contexts)

### Cost Management

- Check costs regularly: `cost` command in tasks/docs modules
- Chat uses more expensive model (gpt-4o)
- Summaries use cheaper model (gpt-4o-mini)
- Typical costs:
  - Task summary: ~$0.0001
  - Doc summary: ~$0.001-0.01
  - Chat message: ~$0.001-0.01

### Performance Tips

- Text extraction is cached (first extraction slower)
- Large PDFs: Use `--page` flag to extract specific pages
- Summaries are saved (no need to regenerate)

---

## Best Practices

### Task Management

1. **Use Descriptive Titles**: Clear, action-oriented titles
2. **Set Priorities**: Mark high-priority tasks immediately
3. **Add Deadlines**: Even approximate dates help prioritization
4. **Use Folders**: Organize by project, time period, or category
5. **Regular Reviews**: Daily list check, weekly folder review
6. **Complete Promptly**: Mark tasks done to maintain accurate stats

### Document Management

1. **Add Immediately**: Add documents when you receive them
2. **Generate Summaries**: Summarize key documents for quick reference
3. **Consistent Naming**: Use clear, descriptive filenames
4. **Regular Cleanup**: Remove outdated documents
5. **Search First**: Use search before adding duplicates
6. **Extract Key Sections**: Cache important pages/sections

### AI Usage

1. **Use Context**: Load appropriate context for better responses
2. **Be Specific**: Ask clear, detailed questions
3. **Iterate**: Refine questions based on responses
4. **Monitor Costs**: Check API usage regularly
5. **Clear History**: Clear chat history when changing topics

### Data Management

1. **Regular Backups**: Create manual backups before major changes
2. **Export Often**: Export data monthly or before system changes
3. **Test Restores**: Occasionally test backup restoration
4. **Clean Up**: Remove old backups to save space
5. **Version Control**: Keep important exports in version control

### Workflow Optimization

1. **Morning Routine**: Review tasks, plan day
2. **Evening Routine**: Complete tasks, add tomorrow's tasks
3. **Weekly Review**: Analyze tasks, clean up folders, export data
4. **Monthly Archive**: Archive completed projects
5. **Continuous Learning**: Review stats to improve productivity

---

## Troubleshooting

See [README.md](README.md#troubleshooting) for common issues and solutions.

---

For complete command reference, see [COMMANDS.md](COMMANDS.md).

For technical details, see [ARCHITECTURE.md](ARCHITECTURE.md).
