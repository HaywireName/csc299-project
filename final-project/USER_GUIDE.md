# USER_GUIDE.md - Comprehensive User Guide

Complete guide to using PKMS Task Manager effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Task Management Tutorial](#task-management-tutorial)
3. [Document Library Guide](#document-library-guide)
4. [AI Chat Assistant](#ai-chat-assistant)
5. [Data Management](#data-management)
6. [API Cost Tracking](#api-cost-tracking)
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
pkms> status
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

**Task List Features**:
- **IDs**: Pending tasks use numbers (1, 2, 3...), completed tasks use letters (a, b, c...)
- **Sorting**: Priority (High→Medium→Low), then nearest deadline, then oldest first
- **Color Coding**: Overdue deadlines in red, deadlines within 2 days in yellow
- **Priority Display**: Capitalized (High, Medium, Low)

**View Task Details**:
```bash
tasks> view 1
```

**Edit Task**:
```bash
# Update deadline
tasks> edit 1 -dl 2025-12-15

# Change priority
tasks> edit 1 -p high

# Add description
tasks> edit 1 -desc New details about the task
```

**Complete Tasks**:
```bash
# Single task
tasks> complete 1

# Multiple tasks
tasks> complete 1 2 3

# Note: After completion, tasks get letter IDs (a, b, c...)
# You can still edit or remove them: edit a, remove b
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

### Removing Documents

**Remove Entire Document**:
```bash
docs> remove 1
# Prompt: Delete document 'filename.pdf'? (yes/no):
```

**Remove Only Summary** (keep document):
```bash
docs> remove -s 1
# Warning: Summaries use API costs and are saved to reduce costs
# Prompt: Are you sure you want to remove this summary? (yes/no):
```

**Note**: Removing only the summary (`-s` flag) keeps the document but deletes the AI-generated summary. You can regenerate it later with `summarize`, but this will cost API credits again.

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
chat> /context tasks
```

**Chat with Document Context**:
```bash
chat> /context docs
```

**Chat with All Context**:
```bash
chat> /context all
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

### Intelligent Task Creation

The AI assistant can intelligently understand your intent and suggest tasks during natural conversation:

**How It Works**:
- The AI uses reasoning to determine if you want to CREATE a task or just DISCUSS it
- Asks for clarification when references are ambiguous ("a report" vs "the report")
- Uses chat history and workspace context to understand what you mean
- Offers structured task suggestions that you can approve or reject

**Examples**:

**Ambiguous Request - AI Asks for Details**:
```
chat[tasks]> I need to work on a report
AI: Which report are you referring to? Can you provide more details about 
what you need to accomplish?
```

**Clear Intent - AI Suggests Task**:
```
chat[tasks]> I should finish the quarterly analysis by Friday
AI: Based on your message, it sounds like you want to create a task for 
completing the quarterly analysis.

[TASK_SUGGESTION]
Title: Complete quarterly analysis
Description: Finish quarterly analysis report
Deadline: [appropriate Friday date]
Priority: high

Would you like me to create this task?

Create this task? (yes/no): yes
✓ Task created successfully!
```

**Request for Recommendations - AI Doesn't Auto-Create**:
```
chat[tasks]> I need to add a task, what do you recommend?
AI: I'd be happy to help! What project or work are you planning? 
Understanding your goals will help me suggest the best approach.
```

**Context-Aware Suggestions**:
```
chat[all]> I need to review the AI research paper before the meeting
AI: [Checks documents and finds "AI Research Paper.pdf"]
I see you have the "AI Research Paper" document. Would you like to 
create a task to review it?

[TASK_SUGGESTION]
Title: Review AI research paper
Description: Review AI Research Paper.pdf before meeting
Deadline: [date based on context]
Priority: high

Create this task? (yes/no): 
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

## API Cost Tracking

PKMS Task Manager includes comprehensive API cost tracking to help you monitor and manage your OpenAI API usage across all features.

### Understanding Costs

**Models and Pricing**:
- **gpt-4o-mini**: Used for task/document summaries
  - Input: $0.150 per 1M tokens
  - Output: $0.600 per 1M tokens
  - Typical cost per operation: ~$0.0001-0.001

- **gpt-4o**: Used for chat, task analysis, and knowledge synthesis
  - Input: $2.50 per 1M tokens
  - Output: $10.00 per 1M tokens
  - Typical cost per operation: ~$0.001-0.02

### Viewing Cost Statistics

**From Main Menu**:
```bash
pkms> status
```

Shows:
- Current session costs (broken down by operation type)
- Previous session total
- All-time total costs

**Example Output**:
```
============================================================
📊 System Statistics
============================================================

Tasks:
  Total tasks: 42
  Pending: 35
  Completed: 7
  Folders: 5

Documents:
  Total documents: 15
  PDFs: 8
  DOCX: 4
  TXT: 3

API Usage & Costs:
  Current Session:
    • Chat messages: $0.0234 (3 calls)
    • Task summaries: $0.0012 (5 calls)
    • Document summaries: $0.0089 (2 calls)
    • Task analysis: $0.0156 (1 call)
    • Knowledge synthesis: $0.0201 (1 call)
    ─────────────────────────────────────
    Total: $0.0692

  Previous Session: $0.1234
  All-Time Total: $2.4567
============================================================
```

### Session Cost Summary on Exit

When you exit the program, you'll see a summary:

```bash
pkms> exit

============================================================
💰 Session API Cost Summary
============================================================
Total API calls: 12
Total cost: $0.0692

Breakdown by operation:
  • chat_message: $0.0234 (3 calls)
  • task_summary: $0.0012 (5 calls)
  • doc_summary: $0.0089 (2 calls)
  • task_analysis: $0.0156 (1 call)
  • knowledge_synthesis: $0.0201 (1 call)
============================================================
Goodbye!
```

### Cost History

All API usage is automatically saved to `data/cost_history.json` with:
- Timestamp of each session
- Total costs per session
- Breakdown by operation type
- Token usage (input/output)

### Tracked Operations

**Task Operations**:
- `task_summary`: AI-generated task summaries

**Document Operations**:
- `doc_summary`: AI-generated document summaries

**Chat Operations**:
- `chat_message`: Interactive chat conversations

**Agent Operations** (via chat slash commands):
- `/analyze`: Task analysis and prioritization recommendations
- `/synthesize`: Knowledge synthesis across documents
- `/connections`: Finding relationships between tasks and documents

### Cost Management Tips

1. **Use Summaries Wisely**: Only summarize tasks/documents you frequently reference
2. **Batch Operations**: Analyze multiple documents at once with `/synthesize`
3. **Clear Context**: Use `/clear` in chat to start fresh conversations
4. **Check Regularly**: Run `status` command to monitor cumulative costs
5. **Use Mini for Simple Tasks**: Task and document summaries automatically use the cheaper gpt-4o-mini model

### Example: Monitoring Daily Usage

```bash
# Morning: Start fresh
pkms> status
# Note starting all-time total

# During day: Use features as needed
pkms> tasks
tasks> summarize 1
tasks> summarize 2
tasks> home

pkms> chat
chat> chat --context tasks
chat[tasks]> What should I work on today?
chat[tasks]> /analyze
chat[tasks]> /exit

# Evening: Check costs
pkms> status
# Review session and total costs
```

### Budget Planning

**Typical Daily Usage**:
- Light use (5-10 summaries, minimal chat): ~$0.01-0.05
- Moderate use (10-20 summaries, regular chat): ~$0.05-0.15
- Heavy use (many summaries, extensive chat/analysis): ~$0.15-0.50

**Monthly Estimates**:
- Light user: ~$0.30-1.50/month
- Moderate user: ~$1.50-4.50/month
- Heavy user: ~$4.50-15.00/month

These are rough estimates and will vary based on:
- Length of chat conversations
- Complexity of documents being summarized
- Frequency of task analysis operations

---

## Common Workflows

### Daily Task Review

```bash
pkms> tasks
tasks[default]> list
# Review tasks (sorted by priority, then deadline)
# Red deadlines = overdue, yellow = due soon

tasks[default]> complete <completed_ids>
# Mark completed (they'll become letters: a, b, c...)

tasks[default]> add "New task" -dl tomorrow
# Add tomorrow's tasks

tasks[default]> home
pkms> status
# Check overall progress and API costs
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
# Completed tasks show as letters (a, b, c...)

# 2. Create this week's folder
tasks[last-week]> folder -a this-week
tasks[this-week]> add "Monday: Team standup" -p high -dl 2025-12-02
tasks[this-week]> add "Tuesday: Client presentation" -p high -dl 2025-12-03
tasks[this-week]> add "Wednesday: Code review" -p medium -dl 2025-12-04
# Tasks will be sorted: High priority first, then by deadline

# 3. View organized list
tasks[this-week]> list
# Red = overdue, Yellow = due within 2 days

# 4. Plan with AI
tasks[this-week]> home
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

- Check costs regularly: Use `status` command
- Chat uses more expensive model (gpt-4o)
- Summaries use cheaper model (gpt-4o-mini)
- All costs tracked by operation type
- Session history saved automatically
- Exit summary shows total usage

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
