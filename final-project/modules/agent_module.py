import os
import json
from datetime import datetime, timedelta
from openai import OpenAI


class AgentManager:
    """Manages AI-powered agent features for task analysis and knowledge synthesis.
    
    The AgentManager provides intelligent analysis capabilities including task
    analysis with complexity estimates and priority suggestions, cross-workspace
    knowledge synthesis, and connection mapping between tasks and documents.
    Uses OpenAI's GPT-4o for advanced reasoning and insights.
    
    Attributes:
        data_manager: Data persistence manager.
        task_manager: TaskManager instance for accessing task data.
        document_manager: DocumentManager instance for accessing documents (optional).
        registry: Command registry for registering agent commands.
        openai_client: OpenAI API client instance.
    """
    
    def __init__(self, data_manager, task_manager, registry, document_manager=None, cost_tracker=None):
        """Initialize AgentManager with dependencies.
        
        Sets up agent features with access to task and document managers,
        initializes OpenAI client, and registers agent commands.
        
        Args:
            data_manager: Data persistence manager instance.
            task_manager: TaskManager instance for task operations.
            registry: Command registry instance for registering commands.
            document_manager: DocumentManager instance for document operations.
                Defaults to None (document features will be limited).
            cost_tracker: CostTracker instance for tracking API costs (optional).
        """
        self.data_manager = data_manager
        self.task_manager = task_manager
        self.document_manager = document_manager
        self.registry = registry
        self.cost_tracker = cost_tracker
        self.openai_client = None
        self._init_openai_client()
        self._register_commands()

    def _init_openai_client(self):
        """Initialize OpenAI client with API key from environment.
        
        Attempts to create an OpenAI client using the API key from the
        OPENAI_API_KEY environment variable. Agent functionality will be
        disabled if the key is not found.
        """
        try:
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                print("Warning: OPENAI_API_KEY not found. Agent functionality will be disabled.")
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")

    def _parse_date(self, date_str):
        """Parse date string to datetime object.
        
        Attempts to parse date strings in various common formats including
        MM-DD-YYYY, YYYY-MM-DD, MM/DD/YYYY, MM/DD (current year), and others.
        
        Args:
            date_str: Date string in various supported formats.
        
        Returns:
            datetime: Parsed datetime object, or None if parsing fails or
                input is empty.
        """
        if not date_str:
            return None
        
        # Common date formats to try
        formats = [
            "%m-%d-%Y",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
        ]
        
        # Try formats with full dates first
        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed
            except ValueError:
                continue
        
        # Handle formats without year by appending current year
        current_year = datetime.now().year
        short_formats = [
            ("%m/%d", f"{date_str}/{current_year}", "%m/%d/%Y"),
            ("%m-%d", f"{date_str}-{current_year}", "%m-%d-%Y"),
        ]
        
        for pattern, date_with_year, fmt in short_formats:
            if date_str.count('/') == 1 or date_str.count('-') == 1:
                try:
                    parsed = datetime.strptime(date_with_year, fmt)
                    return parsed
                except ValueError:
                    continue
        
        return None

    def _categorize_tasks(self, tasks):
        """Categorize tasks by urgency and status.
        
        Groups tasks into categories: overdue, due soon (within 3 days),
        no deadline, high priority pending, and all tasks. Used for
        generating analysis insights.
        
        Args:
            tasks: List of task dictionaries.
        
        Returns:
            dict: Dictionary with category keys mapping to lists of tasks:
                - overdue: Past deadline, not completed.
                - due_soon: Deadline within next 3 days, not completed.
                - no_deadline: Tasks without deadlines.
                - high_priority_pending: High priority tasks that are pending.
                - all_tasks: Complete list of all tasks.
        """
        now = datetime.now()
        today = now.date()
        soon_threshold = today + timedelta(days=3)
        
        categories = {
            'overdue': [],
            'due_soon': [],
            'no_deadline': [],
            'high_priority_pending': [],
            'all_tasks': tasks
        }
        
        for task in tasks:
            deadline_str = task.get('deadline')
            priority = task.get('priority', 'medium')
            status = task.get('status', 'pending')
            
            # High priority pending tasks
            if priority == 'high' and status == 'pending':
                categories['high_priority_pending'].append(task)
            
            # No deadline
            if not deadline_str or deadline_str == 'None':
                categories['no_deadline'].append(task)
                continue
            
            # Parse deadline
            deadline = self._parse_date(deadline_str)
            if not deadline:
                categories['no_deadline'].append(task)
                continue
            
            deadline_date = deadline.date()
            
            # Overdue
            if deadline_date < today and status != 'completed':
                categories['overdue'].append(task)
            # Due soon
            elif deadline_date <= soon_threshold and status != 'completed':
                categories['due_soon'].append(task)
        
        return categories

    def _call_openai_analysis(self, tasks_data, categories):
        """Send tasks to OpenAI for AI-powered analysis.
        
        Sends task data to GPT-4o for comprehensive analysis including
        complexity estimates, priority suggestions, related task identification,
        deadline recommendations, and general insights. Returns structured
        JSON response.
        
        Args:
            tasks_data: List of task dictionaries with metadata.
            categories: Pre-categorized tasks for context.
        
        Returns:
            dict: Parsed JSON analysis containing complexity_estimates,
                priority_suggestions, related_tasks, deadline_suggestions,
                and insights. Returns None if analysis fails.
        """
        if not self.openai_client:
            return None
        
        system_prompt = """You are a task analysis assistant. Analyze the provided tasks and provide insights about:
1. Complexity estimates (based on description length and content)
2. Priority adjustment suggestions (based on deadlines and descriptions)
3. Related tasks (tasks that seem connected by keywords or themes)
4. Deadline suggestions for tasks without deadlines
5. Any other productivity insights

Respond in JSON format with this structure:
{
  "complexity_estimates": [
    {"task_id": "1", "task_title": "...", "complexity": "high/medium/low", "estimated_hours": "2-4", "reason": "..."}
  ],
  "priority_suggestions": [
    {"task_id": "1", "current_priority": "...", "suggested_priority": "...", "reason": "..."}
  ],
  "related_tasks": [
    {"task_ids": ["1", "2"], "relationship": "...", "suggestion": "..."}
  ],
  "deadline_suggestions": [
    {"task_id": "1", "suggested_deadline": "YYYY-MM-DD", "reason": "..."}
  ],
  "insights": [
    "General productivity insight or observation"
  ]
}"""
        
        # Prepare task data for analysis
        tasks_summary = []
        for task in tasks_data:
            tasks_summary.append({
                'id': task.get('id'),
                'title': task.get('title', '').strip('"'),
                'description': task.get('description', '').strip('"')[:200],  # Limit description
                'deadline': task.get('deadline'),
                'priority': task.get('priority'),
                'status': task.get('status')
            })
        
        user_prompt = f"""Analyze these tasks:\n\n{json.dumps(tasks_summary, indent=2)}

Additional context:
- Overdue tasks: {len(categories['overdue'])}
- Due soon (3 days): {len(categories['due_soon'])}
- No deadline: {len(categories['no_deadline'])}
- High priority pending: {len(categories['high_priority_pending'])}

Provide analysis in the specified JSON format."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Track API costs
            if self.cost_tracker and hasattr(response, 'usage') and response.usage:
                self.cost_tracker.track_api_call(
                    operation_type='task_analysis',
                    model="gpt-4o",
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens
                )
            
            analysis_text = response.choices[0].message.content
            return json.loads(analysis_text)
            
        except Exception as e:
            print(f"Error during AI analysis: {e}")
            return None

    def _format_analysis_report(self, categories, ai_analysis, folder_name):
        """Format analysis results as readable report.
        
        Creates a comprehensive formatted report with categorized tasks
        (overdue, due soon, no deadline, high priority) and AI-generated
        insights including complexity estimates, priority suggestions,
        related tasks, and deadline recommendations.
        
        Args:
            categories: Dictionary of categorized tasks.
            ai_analysis: AI analysis results from OpenAI.
            folder_name: Name of the analyzed folder.
        
        Returns:
            str: Multi-line formatted report string with sections and visual separators.
        """
        lines = []
        lines.append("\n" + "=" * 50)
        lines.append("Task Analysis Report")
        lines.append(f"Folder: {folder_name}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 50 + "\n")
        
        # Overdue tasks
        if categories['overdue']:
            lines.append(f"⚠️  OVERDUE ({len(categories['overdue'])})")
            for task in categories['overdue']:
                task_id = task.get('id')
                title = task.get('title', '').strip('"')
                deadline = task.get('deadline', 'No deadline')
                lines.append(f"- [{task_id}] {title} - Due: {deadline}")
            lines.append("")
        
        # Due soon
        if categories['due_soon']:
            lines.append(f"🔔 DUE SOON - Next 3 days ({len(categories['due_soon'])})")
            for task in categories['due_soon']:
                task_id = task.get('id')
                title = task.get('title', '').strip('"')
                deadline = task.get('deadline', 'No deadline')
                
                # Calculate days until due
                deadline_date = self._parse_date(deadline)
                if deadline_date:
                    days_until = (deadline_date.date() - datetime.now().date()).days
                    if days_until == 0:
                        due_text = "Due TODAY"
                    elif days_until == 1:
                        due_text = "Due tomorrow"
                    else:
                        due_text = f"Due in {days_until} days"
                else:
                    due_text = f"Due: {deadline}"
                
                lines.append(f"- [{task_id}] {title} - {due_text}")
            lines.append("")
        
        # No deadline
        if categories['no_deadline']:
            lines.append(f"📋 NO DEADLINE ({len(categories['no_deadline'])})")
            for task in categories['no_deadline'][:5]:  # Show first 5
                task_id = task.get('id')
                title = task.get('title', '').strip('"')
                lines.append(f"- [{task_id}] {title}")
            if len(categories['no_deadline']) > 5:
                lines.append(f"  ... and {len(categories['no_deadline']) - 5} more")
            lines.append("")
        
        # High priority pending
        if categories['high_priority_pending']:
            lines.append(f"🔥 HIGH PRIORITY PENDING ({len(categories['high_priority_pending'])})")
            for task in categories['high_priority_pending']:
                task_id = task.get('id')
                title = task.get('title', '').strip('"')
                deadline = task.get('deadline', 'No deadline')
                lines.append(f"- [{task_id}] {title} - Due: {deadline}")
            lines.append("")
        
        # AI Analysis sections
        if ai_analysis:
            lines.append("💡 AI-POWERED INSIGHTS")
            lines.append("-" * 50)
            
            # Complexity estimates
            if ai_analysis.get('complexity_estimates'):
                lines.append("\n📊 Complexity Estimates:")
                for estimate in ai_analysis['complexity_estimates'][:5]:
                    task_title = estimate.get('task_title', '').strip('"')
                    complexity = estimate.get('complexity', 'medium')
                    hours = estimate.get('estimated_hours', 'N/A')
                    reason = estimate.get('reason', '')
                    lines.append(f"  • \"{task_title}\" - {complexity.upper()} complexity (~{hours} hours)")
                    lines.append(f"    Reason: {reason}")
            
            # Priority suggestions
            if ai_analysis.get('priority_suggestions'):
                lines.append("\n⚡ Priority Adjustments:")
                for suggestion in ai_analysis['priority_suggestions']:
                    task_id = suggestion.get('task_id')
                    current = suggestion.get('current_priority', 'medium')
                    suggested = suggestion.get('suggested_priority', 'medium')
                    reason = suggestion.get('reason', '')
                    lines.append(f"  • Task [{task_id}]: {current} → {suggested}")
                    lines.append(f"    Reason: {reason}")
            
            # Related tasks
            if ai_analysis.get('related_tasks'):
                lines.append("\n🔗 Related Tasks:")
                for relation in ai_analysis['related_tasks']:
                    task_ids = relation.get('task_ids', [])
                    relationship = relation.get('relationship', '')
                    suggestion = relation.get('suggestion', '')
                    lines.append(f"  • Tasks {task_ids} are related: {relationship}")
                    if suggestion:
                        lines.append(f"    Suggestion: {suggestion}")
            
            # Deadline suggestions
            if ai_analysis.get('deadline_suggestions'):
                lines.append("\n📅 Deadline Suggestions:")
                for suggestion in ai_analysis['deadline_suggestions']:
                    task_id = suggestion.get('task_id')
                    suggested_deadline = suggestion.get('suggested_deadline')
                    reason = suggestion.get('reason', '')
                    lines.append(f"  • Task [{task_id}]: Set deadline to {suggested_deadline}")
                    lines.append(f"    Reason: {reason}")
            
            # General insights
            if ai_analysis.get('insights'):
                lines.append("\n💭 General Insights:")
                for insight in ai_analysis['insights']:
                    lines.append(f"  • {insight}")
        
        lines.append("\n" + "=" * 50 + "\n")
        
        return "\n".join(lines)

    def _apply_suggestions_interactive(self, ai_analysis):
        """Walk through AI suggestions and apply them interactively.
        
        Presents each priority and deadline suggestion to the user one by one,
        allowing them to accept, reject, or skip each suggestion. Applies
        accepted suggestions immediately via the task manager.
        
        Args:
            ai_analysis: AI analysis results containing suggestions.
        
        Returns:
            tuple: (applied_count (int), total_suggestions (int)) indicating
                how many suggestions were applied and total presented.
        """
        if not ai_analysis:
            return 0
        
        applied_count = 0
        total_suggestions = 0
        
        # Priority suggestions
        priority_suggestions = ai_analysis.get('priority_suggestions', [])
        for i, suggestion in enumerate(priority_suggestions, 1):
            total_suggestions += 1
            task_id = suggestion.get('task_id')
            current = suggestion.get('current_priority')
            suggested = suggestion.get('suggested_priority')
            reason = suggestion.get('reason', '')
            
            print(f"\nSuggestion {i}/{len(priority_suggestions)}: Increase priority of task [{task_id}] from {current} to {suggested}")
            print(f"Reason: {reason}")
            
            choice = input("Apply this suggestion? (y/n/skip): ").strip().lower()
            
            if choice == 'y':
                try:
                    # Update priority using task_manager
                    self.task_manager.update_task(task_id, priority=suggested)
                    print(f"✓ Priority updated for task [{task_id}]")
                    applied_count += 1
                except Exception as e:
                    print(f"✗ Error updating task: {e}")
            elif choice == 'skip':
                print("Skipped.")
            else:
                print("Skipped.")
        
        # Deadline suggestions
        deadline_suggestions = ai_analysis.get('deadline_suggestions', [])
        for i, suggestion in enumerate(deadline_suggestions, 1):
            total_suggestions += 1
            task_id = suggestion.get('task_id')
            suggested_deadline = suggestion.get('suggested_deadline')
            reason = suggestion.get('reason', '')
            
            print(f"\nSuggestion {len(priority_suggestions) + i}/{len(priority_suggestions) + len(deadline_suggestions)}: Set deadline for task [{task_id}] to {suggested_deadline}")
            print(f"Reason: {reason}")
            
            choice = input("Apply this suggestion? (y/n/skip): ").strip().lower()
            
            if choice == 'y':
                try:
                    # Update deadline using task_manager
                    self.task_manager.update_task(task_id, deadline=suggested_deadline)
                    print(f"✓ Deadline updated for task [{task_id}]")
                    applied_count += 1
                except Exception as e:
                    print(f"✗ Error updating task: {e}")
            elif choice == 'skip':
                print("Skipped.")
            else:
                print("Skipped.")
        
        return applied_count, total_suggestions

    def analyze_tasks(self, folder_name=None):
        """Analyze tasks in a folder with AI assistance.
        
        Performs comprehensive AI-powered analysis of tasks including urgency
        categorization, complexity estimation, priority recommendations, and
        related task identification. Optionally allows interactive application
        of AI suggestions.
        
        Args:
            folder_name: Folder to analyze. Uses current folder if None.
                Defaults to None.
        
        Returns:
            str: Formatted analysis report, or None if analysis fails or
                folder has no tasks.
        """
        if not self.openai_client:
            print("Error: AI analysis requires OpenAI API key.")
            print("Please set OPENAI_API_KEY environment variable.")
            return None
        
        # Get folder name
        if not folder_name:
            folder_name = self.task_manager.data.get('current_folder', 'default')
        
        # Get tasks from folder
        folders = self.task_manager.data.get('folders', {})
        if folder_name not in folders:
            print(f"Error: Folder '{folder_name}' not found.")
            return None
        
        tasks = folders[folder_name]
        
        if not tasks:
            print(f"No tasks found in folder '{folder_name}'.")
            return None
        
        print(f"Analyzing {len(tasks)} tasks in folder '{folder_name}'...")
        print("Running AI analysis...\n")
        
        # Categorize tasks
        categories = self._categorize_tasks(tasks)
        
        # Call OpenAI for analysis
        ai_analysis = self._call_openai_analysis(tasks, categories)
        
        # Format and display report
        report = self._format_analysis_report(categories, ai_analysis, folder_name)
        print(report)
        
        # Offer to apply suggestions
        if ai_analysis and (ai_analysis.get('priority_suggestions') or ai_analysis.get('deadline_suggestions')):
            choice = input("Would you like to apply these suggestions? (y/n): ").strip().lower()
            
            if choice == 'y':
                print()
                applied, total = self._apply_suggestions_interactive(ai_analysis)
                print(f"\n✓ Analysis complete. {applied} of {total} suggestions applied.")
            else:
                print("Suggestions not applied.")
        
        return report

    def _find_relevant_pdfs(self, topic):
        """Search document text and summaries for topic.
        
        Searches through document titles, summaries, and cached full text
        for relevance to the given topic. Calculates relevance scores and
        extracts context snippets around matches.
        
        Args:
            topic: Topic string to search for.
        
        Returns:
            list: List of relevant document dictionaries with relevance_score
                and context_snippets, sorted by relevance (highest first).
                Empty list if no documents match or document_manager unavailable.
        """
        if not self.document_manager:
            return []
        
        docs_data = self.data_manager.load("docs_metadata.json")
        if not docs_data:
            return []
        
        relevant_docs = []
        topic_lower = topic.lower()
        
        for doc in docs_data:
            doc_id = doc.get('id')
            title = doc.get('title', doc.get('filename', 'Untitled'))
            summary = doc.get('summary', '')
            extension = doc.get('extension', '')
            
            # Check if topic is in title or summary
            relevance_score = 0
            context_snippets = []
            
            if topic_lower in title.lower():
                relevance_score += 10
                context_snippets.append(f"Title: {title}")
            
            if summary and topic_lower in summary.lower():
                relevance_score += 5
                # Extract context around topic
                summary_lower = summary.lower()
                idx = summary_lower.find(topic_lower)
                if idx != -1:
                    start = max(0, idx - 100)
                    end = min(len(summary), idx + len(topic) + 100)
                    snippet = summary[start:end]
                    context_snippets.append(f"Summary: ...{snippet}...")
            
            # Try to search in cached full text
            if relevance_score < 5:  # Only if not found in title/summary
                try:
                    cache_path = self.document_manager._get_cache_path(doc_id, 'full')
                    if os.path.exists(cache_path):
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            text = f.read()
                            if topic_lower in text.lower():
                                relevance_score += 3
                                # Extract context
                                text_lower = text.lower()
                                idx = text_lower.find(topic_lower)
                                if idx != -1:
                                    start = max(0, idx - 150)
                                    end = min(len(text), idx + len(topic) + 150)
                                    snippet = text[start:end].replace('\n', ' ')
                                    context_snippets.append(f"Content: ...{snippet}...")
                except Exception:
                    pass
            
            if relevance_score > 0:
                relevant_docs.append({
                    'id': doc_id,
                    'title': title,
                    'extension': extension,
                    'page_count': doc.get('page_count'),
                    'word_count': doc.get('word_count'),
                    'summary': summary,
                    'relevance_score': relevance_score,
                    'context_snippets': context_snippets
                })
        
        # Sort by relevance
        relevant_docs.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_docs

    def _find_relevant_tasks(self, topic):
        """Search task titles and descriptions for topic.
        
        Searches through all tasks across all folders for relevance to the
        given topic. Calculates relevance scores and extracts context snippets
        around matches in titles and descriptions.
        
        Args:
            topic: Topic string to search for.
        
        Returns:
            list: List of relevant task dictionaries with relevance_score,
                folder, and context_snippets, sorted by relevance (highest first).
        """
        tasks_data = self.data_manager.load("tasks.json")
        if not tasks_data or 'folders' not in tasks_data:
            return []
        
        relevant_tasks = []
        topic_lower = topic.lower()
        
        for folder_name, tasks in tasks_data['folders'].items():
            for task in tasks:
                task_id = task.get('id')
                title = task.get('title', '').strip('"')
                description = task.get('description', '').strip('"')
                deadline = task.get('deadline')
                priority = task.get('priority')
                status = task.get('status')
                
                relevance_score = 0
                context_snippets = []
                
                if topic_lower in title.lower():
                    relevance_score += 10
                    context_snippets.append(f"Title: {title}")
                
                if topic_lower in description.lower():
                    relevance_score += 5
                    # Extract context around topic
                    desc_lower = description.lower()
                    idx = desc_lower.find(topic_lower)
                    if idx != -1:
                        start = max(0, idx - 100)
                        end = min(len(description), idx + len(topic) + 100)
                        snippet = description[start:end]
                        context_snippets.append(f"Description: ...{snippet}...")
                
                if relevance_score > 0:
                    relevant_tasks.append({
                        'id': task_id,
                        'title': title,
                        'description': description[:200],
                        'folder': folder_name,
                        'deadline': deadline,
                        'priority': priority,
                        'status': status,
                        'relevance_score': relevance_score,
                        'context_snippets': context_snippets
                    })
        
        # Sort by relevance
        relevant_tasks.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_tasks

    def _call_synthesis(self, topic, pdfs, tasks):
        """Send to OpenAI for knowledge synthesis.
        
        Sends relevant documents and tasks to GPT-4o for comprehensive
        knowledge synthesis about the topic. AI integrates information
        from multiple sources and provides actionable insights.
        
        Args:
            topic: Topic to synthesize information about.
            pdfs: List of relevant document dictionaries.
            tasks: List of relevant task dictionaries.
        
        Returns:
            str: AI-generated synthesis with overview, key points, and
                actionable insights. Returns None if synthesis fails.
        """
        if not self.openai_client:
            return None
        
        system_prompt = f"""You are a knowledge synthesis assistant. Synthesize information about "{topic}" from the provided sources. 

Provide a comprehensive overview that:
1. Integrates information from all sources
2. Identifies key points and themes
3. Provides actionable insights
4. Cites sources using [source_id] format

Structure your response as:
- Overview paragraph
- Key Points (bulleted)
- Actionable Insights (bulleted)"""
        
        # Build user prompt with sources
        sources = []
        
        # Add PDFs
        for pdf in pdfs[:5]:  # Limit to top 5
            sources.append(f"[{pdf['id']}] Document: {pdf['title']}")
            if pdf.get('summary'):
                sources.append(f"   Summary: {pdf['summary'][:300]}")
            for snippet in pdf['context_snippets'][:2]:
                sources.append(f"   {snippet}")
            sources.append("")
        
        # Add tasks
        for task in tasks[:5]:  # Limit to top 5
            sources.append(f"[{task['id']}] Task: {task['title']} (folder: {task['folder']})")
            sources.append(f"   Status: {task['status']}, Priority: {task['priority']}")
            if task.get('deadline'):
                sources.append(f"   Deadline: {task['deadline']}")
            for snippet in task['context_snippets'][:2]:
                sources.append(f"   {snippet}")
            sources.append("")
        
        user_prompt = f"Synthesize information about: {topic}\n\nSources:\n" + "\n".join(sources)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            # Track API costs
            if self.cost_tracker and hasattr(response, 'usage') and response.usage:
                self.cost_tracker.track_api_call(
                    operation_type='knowledge_synthesis',
                    model="gpt-4o",
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens
                )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error during synthesis: {e}")
            return None

    def synthesize_topic(self, topic):
        """Search documents and tasks for topic and synthesize with AI.
        
        Performs comprehensive knowledge synthesis by:
        1. Searching all documents and tasks for relevant content
        2. Sending relevant sources to AI for synthesis
        3. Formatting results with source citations and related information
        
        Args:
            topic: Topic to synthesize information about.
        
        Returns:
            str: Formatted synthesis report with sources, synthesis text,
                and related information. Returns None if no relevant sources
                found or synthesis fails.
        """
        if not self.openai_client:
            print("Error: Synthesis requires OpenAI API key.")
            return None
        
        print(f"Searching knowledge base for '{topic}'...")
        
        # Find relevant sources
        relevant_pdfs = self._find_relevant_pdfs(topic) if self.document_manager else []
        relevant_tasks = self._find_relevant_tasks(topic)
        
        print(f"Found {len(relevant_pdfs)} documents and {len(relevant_tasks)} tasks related to \"{topic}\"\n")
        
        if not relevant_pdfs and not relevant_tasks:
            print(f"No information found about '{topic}' in your knowledge base.")
            return None
        
        print("Synthesizing information...\n")
        
        # Get AI synthesis
        synthesis_text = self._call_synthesis(topic, relevant_pdfs, relevant_tasks)
        
        if not synthesis_text:
            print("Failed to generate synthesis.")
            return None
        
        # Format output
        lines = []
        lines.append("=" * 60)
        lines.append(f"Knowledge Synthesis: {topic}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60 + "\n")
        
        # Sources section
        lines.append("📚 SOURCES")
        for pdf in relevant_pdfs[:5]:
            pages_info = f"{pdf.get('page_count', 'N/A')} pages" if pdf.get('page_count') else f"{pdf.get('word_count', 'N/A')} words"
            ext = pdf['extension'].upper().replace('.', '')
            lines.append(f"- [{pdf['id']}] {pdf['title']} ({ext}, {pages_info})")
        
        for task in relevant_tasks[:5]:
            lines.append(f"- [{task['id']}] {task['title']} (Task, {task['folder']} folder)")
        
        lines.append("\n" + "=" * 60 + "\n")
        
        # Synthesis
        lines.append("📖 SYNTHESIS\n")
        lines.append(synthesis_text)
        
        lines.append("\n" + "=" * 60 + "\n")
        
        # Related information
        lines.append("🔗 RELATED INFORMATION")
        for task in relevant_tasks[:3]:
            deadline_info = f" due {task['deadline']}" if task['deadline'] else ""
            lines.append(f"- Task \"{task['title']}\" [{task['folder']}]{deadline_info}")
        
        for pdf in relevant_pdfs[:3]:
            lines.append(f"- Document \"{pdf['title']}\" has relevant coverage")
        
        lines.append("\n" + "=" * 60 + "\n")
        
        output = "\n".join(lines)
        print(output)
        return output

    def show_connections(self):
        """Display connections between documents and tasks.
        
        Analyzes the workspace to find connections between documents and tasks
        by detecting mentions, references, and shared context. Shows how
        knowledge is interconnected across the workspace.
        
        Returns:
            str: Formatted connections report showing links between documents
                and tasks with statistics.
        """
        print("Analyzing knowledge connections...\n")
        
        # Load all data
        docs_data = self.data_manager.load("docs_metadata.json") if self.document_manager else []
        tasks_data = self.data_manager.load("tasks.json")
        
        if not docs_data:
            docs_data = []
        
        connections = []
        
        # Find connections: tasks mentioning documents
        if tasks_data and 'folders' in tasks_data:
            for folder_name, tasks in tasks_data['folders'].items():
                for task in tasks:
                    task_id = task.get('id')
                    task_title = task.get('title', '').strip('"')
                    task_desc = task.get('description', '').strip('"').lower()
                    
                    # Find docs mentioned in task
                    connected_docs = []
                    for doc in docs_data:
                        doc_title = doc.get('title', '').lower()
                        doc_filename = doc.get('filename', '').lower()
                        
                        # Check if doc title/filename appears in task description
                        if doc_title in task_desc or doc_filename in task_desc:
                            connected_docs.append({
                                'id': doc.get('id'),
                                'title': doc.get('title', doc.get('filename')),
                                'type': 'mentioned'
                            })
                    
                    if connected_docs:
                        connections.append({
                            'type': 'task',
                            'id': task_id,
                            'title': task_title,
                            'folder': folder_name,
                            'connections': connected_docs
                        })
        
        # Find connections: docs that relate to tasks (by folder or keywords)
        for doc in docs_data:
            doc_id = doc.get('id')
            doc_title = doc.get('title', doc.get('filename', 'Untitled'))
            doc_summary = (doc.get('summary') or '').lower()
            
            connected_tasks = []
            
            if tasks_data and 'folders' in tasks_data:
                for folder_name, tasks in tasks_data['folders'].items():
                    for task in tasks:
                        task_title = task.get('title', '').strip('"')
                        task_title_lower = task_title.lower()
                        
                        # Check if task title appears in doc summary
                        if task_title_lower in doc_summary:
                            connected_tasks.append({
                                'id': task.get('id'),
                                'title': task_title,
                                'folder': folder_name,
                                'type': 'referenced'
                            })
                        # Check if they share same folder name (inferred connection)
                        elif folder_name.lower() in doc_title.lower():
                            connected_tasks.append({
                                'id': task.get('id'),
                                'title': task_title,
                                'folder': folder_name,
                                'type': 'same_context',
                                'deadline': task.get('deadline')
                            })
            
            if connected_tasks:
                connections.append({
                    'type': 'doc',
                    'id': doc_id,
                    'title': doc_title,
                    'connections': connected_tasks
                })
        
        # Format output
        lines = []
        lines.append("=" * 60)
        lines.append("Knowledge Connections")
        lines.append("=" * 60 + "\n")
        
        if not connections:
            lines.append("No connections found between documents and tasks.")
            lines.append("\nTip: Connections are found when:")
            lines.append("- Task descriptions mention document names")
            lines.append("- Document summaries reference task titles")
            lines.append("- Documents and tasks share folder contexts")
        else:
            doc_count = sum(1 for c in connections if c['type'] == 'doc')
            task_count = sum(1 for c in connections if c['type'] == 'task')
            total_links = sum(len(c['connections']) for c in connections)
            
            for conn in connections:
                if conn['type'] == 'doc':
                    lines.append(f"📄 [{conn['id']}] {conn['title']}")
                    for task_conn in conn['connections']:
                        deadline_info = f" (due {task_conn.get('deadline')})" if task_conn.get('deadline') else ""
                        lines.append(f"   └─ 📋 [{task_conn['id']}] {task_conn['title']} [{task_conn['folder']}]{deadline_info}")
                    lines.append("")
                elif conn['type'] == 'task':
                    lines.append(f"📋 [{conn['id']}] {conn['title']} [{conn['folder']}]")
                    for doc_conn in conn['connections']:
                        lines.append(f"   └─ 📄 [{doc_conn['id']}] {doc_conn['title']} ({doc_conn['type']})")
                    lines.append("")
            
            lines.append("=" * 60)
            lines.append(f"Total: {doc_count} documents, {task_count} tasks, {total_links} connections")
        
        lines.append("=" * 60 + "\n")
        
        output = "\n".join(lines)
        print(output)
        return output

    def _register_commands(self):
        """Register agent-related commands.
        
        Registers AI agent commands (analyze-tasks, synthesize, connections)
        with the command registry.
        """
        self.registry.register_command('analyze-tasks', self.cmd_analyze_tasks, 
                                      'Analyze tasks with AI insights', 'agent')
        self.registry.register_command('synthesize', self.cmd_synthesize,
                                      'Synthesize knowledge about a topic', 'agent')
        self.registry.register_command('connections', self.cmd_connections,
                                      'Show connections between documents and tasks', 'agent')

    def cmd_analyze_tasks(self, *args):
        """Command to analyze tasks in a folder.
        
        Runs AI-powered task analysis on the specified folder or current folder.
        
        Args:
            *args: Command arguments. Use '--folder <name>' to specify folder.
        """
        folder_name = None
        
        # Parse arguments for --folder flag
        args_list = list(args)
        if '--folder' in args_list:
            try:
                folder_index = args_list.index('--folder')
                if folder_index + 1 < len(args_list):
                    folder_name = args_list[folder_index + 1]
                else:
                    print("Error: --folder flag requires a value")
                    return
            except ValueError:
                pass
        
        self.analyze_tasks(folder_name)

    def cmd_synthesize(self, *args):
        """Command to synthesize knowledge about a topic.
        
        Searches workspace for relevant information and generates AI synthesis.
        
        Args:
            *args: Topic words to search for (joined into single topic string).
        """
        if not args:
            print("Usage: synthesize <topic>")
            print("Example: synthesize machine learning")
            return
        
        # Join all args as the topic
        topic = " ".join(args)
        self.synthesize_topic(topic)

    def cmd_connections(self, *args):
        """Command to show connections between documents and tasks.
        
        Displays a report of all detected connections in the workspace.
        
        Args:
            *args: Unused command arguments.
        """
        self.show_connections()
