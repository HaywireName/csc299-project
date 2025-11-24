import uuid
import os
import time
from datetime import datetime, timedelta
from tabulate import tabulate
from dateutil import parser as date_parser
from openai import OpenAI
from core.errors import TaskNotFoundError, InvalidInputError, APIError, ValidationError
from core.utils import validate_priority, confirm_action, format_success, format_error, format_warning

class TaskManager:
    def __init__(self, data_manager, registry):
        """
        Initialize TaskManager with dependencies.
        """
        self.data_manager = data_manager
        self.registry = registry
        self.data = self.data_manager.load("tasks.json") or {"folders": {"default": []}, "current_folder": "default"}
        self.tasks = self.data["folders"].get(self.data["current_folder"], [])
        self.session_cost = 0.0  # Track cumulative cost for the session
        self.openai_client = None
        self._init_openai_client()
        self._register_commands()

    def _init_openai_client(self):
        """Initialize OpenAI client with API key from environment."""
        try:
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                print("Warning: OPENAI_API_KEY not found. AI features will be disabled.")
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")

    def _save_data(self):
        """Save the entire data structure to tasks.json."""
        self.data_manager.save("tasks.json", self.data)

    def get_folders(self):
        """Return a dictionary of folder names and their task counts."""
        return {folder: len(tasks) for folder, tasks in self.data["folders"].items()}

    def switch_folder(self, folder_name):
        """Switch to a different folder, creating it if necessary."""
        if folder_name not in self.data["folders"]:
            self.data["folders"][folder_name] = []
        self.data["current_folder"] = folder_name
        self.tasks = self.data["folders"][folder_name]
        self._save_data()

    def create_folder(self, folder_name):
        """Create a new folder if it doesn't exist."""
        if folder_name in self.data["folders"]:
            raise ValueError(f"Folder '{folder_name}' already exists.")
        self.data["folders"][folder_name] = []
        self._save_data()

    def delete_folder(self, folder_name):
        """Delete a folder and all its tasks, except the default folder."""
        if folder_name == "default":
            raise ValueError("Cannot delete the default folder.")
        if folder_name not in self.data["folders"]:
            raise ValueError(f"Folder '{folder_name}' does not exist.")
        del self.data["folders"][folder_name]
        if self.data["current_folder"] == folder_name:
            self.switch_folder("default")
        self._save_data()

    def _load_tasks(self):
        """Load tasks from the current folder."""
        folder = self._get_current_folder()
        self.tasks = self.data_manager.load(folder) or []

    def _save_tasks(self):
        """Save tasks to the current folder."""
        folder = self._get_current_folder()
        self.data_manager.save(folder, self.tasks)

    def _get_current_folder(self):
        """Return the current folder name from data."""
        return self.data_manager.get_current_folder()

    def _generate_id(self):
        """Generate a unique ID for a new task."""
        return str(len(self.tasks) + 1)

    def _parse_deadline(self, deadline_str):
        """
        Parse deadline from various formats and return DD-MM-YYYY format.
        Supports: MM-DD-YYYY, YYYY-DD-MM, MM/DD, MM-YY, MM/DD/YYYY, YYYY/DD/MM, and 'tomorrow'
        :param deadline_str: Deadline string in various formats
        :return: Formatted deadline string in DD-MM-YYYY format
        """
        if not deadline_str:
            return None
        
        deadline_str = deadline_str.strip()
        
        # Handle 'tomorrow'
        if deadline_str.lower() == 'tomorrow':
            tomorrow = datetime.now() + timedelta(days=1)
            return tomorrow.strftime("%d-%m-%Y")
        
        # Normalize separators: replace '/' with '-' for consistent parsing
        normalized = deadline_str.replace('/', '-')
        parts = normalized.split('-')
        
        try:
            current_year = datetime.now().year
            
            if len(parts) == 3:
                # Could be MM-DD-YYYY, YYYY-DD-MM, or similar
                if len(parts[0]) == 4:
                    # YYYY-DD-MM format
                    year, day, month = int(parts[0]), int(parts[1]), int(parts[2])
                else:
                    # MM-DD-YYYY format
                    month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                    # Handle 2-digit year
                    if year < 100:
                        year += 2000
            elif len(parts) == 2:
                # Could be MM-DD (current year) or MM-YY
                month, second_part = int(parts[0]), int(parts[1])
                if second_part > 31:
                    # This is MM-YY format
                    year = second_part
                    if year < 100:
                        year += 2000
                    day = 1  # Default to first day of the month
                else:
                    # This is MM-DD format (use current year)
                    day = second_part
                    year = current_year
            else:
                raise ValueError(f"Unrecognized date format: {deadline_str}")
            
            # Validate the date
            parsed_date = datetime(year, month, day)
            return parsed_date.strftime("%d-%m-%Y")
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid deadline format '{deadline_str}'. Supported formats: MM-DD-YYYY, YYYY-DD-MM, MM/DD/YYYY, MM/DD, MM-YY, or 'tomorrow'")

    def _count_words(self, text):
        """Count the number of words in a text string."""
        if not text:
            return 0
        return len(text.split())

    def _call_openai_summary(self, text):
        """
        Call OpenAI API to generate a 10-15 word summary.
        Implements retry logic with exponential backoff.
        :param text: The text to summarize
        :return: Summary string
        :raises APIError: If API call fails after retries
        """
        if not self.openai_client:
            raise APIError(
                "OpenAI client not initialized",
                error_type="authentication",
                suggestion="Check your API key in settings"
            )
        
        max_retries = 3
        base_delay = 1  # Start with 1 second delay
        
        for attempt in range(max_retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "Summarize the following task description in 10-15 words maximum. Be concise and preserve key details."
                        },
                        {
                            "role": "user",
                            "content": text
                        }
                    ],
                    max_tokens=50,
                    temperature=0.7
                )
                
                summary = response.choices[0].message.content.strip()
                
                # Calculate cost (gpt-4o-mini pricing: $0.150/1M input, $0.600/1M output)
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                cost = (input_tokens * 0.150 / 1_000_000) + (output_tokens * 0.600 / 1_000_000)
                self.session_cost += cost
                
                return summary
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check for specific error types
                if "rate_limit" in error_msg or "429" in error_msg:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        print(f"⏳ Rate limit hit. Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        raise APIError("Rate limit exceeded", error_type="rate_limit")
                
                elif "invalid" in error_msg and ("key" in error_msg or "401" in error_msg):
                    raise APIError("Invalid API key", error_type="authentication")
                
                elif "quota" in error_msg or "insufficient" in error_msg:
                    raise APIError("API quota exceeded", error_type="quota")
                
                elif "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        print(f"⏳ Network error. Retrying in {delay} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        raise APIError("Network connection failed", error_type="network")
                
                else:
                    raise APIError(f"Unexpected error: {str(e)}")
        
        raise APIError("Failed to generate summary after multiple attempts")

    def summarize_task(self, task_id):
        """
        Generate an AI summary for a task if description is longer than 100 words.
        :param task_id: ID or partial ID of the task
        :return: The summary string
        :raises TaskNotFoundError: If task not found
        :raises InvalidInputError: If description is too short or missing
        :raises APIError: If OpenAI API call fails
        """
        task = self.get_task(task_id)  # This will raise TaskNotFoundError if not found
        
        description = task.get('description', '')
        if not description:
            raise InvalidInputError("Task has no description to summarize", field="description")
        
        word_count = self._count_words(description)
        if word_count <= 100:
            raise InvalidInputError(
                f"Description is too short ({word_count} words). Minimum 100 words required for summarization.",
                field="description"
            )
        
        # Generate summary (may raise APIError)
        print(f"Generating summary for task '{task['title']}'...")
        summary = self._call_openai_summary(description)
        task['summary'] = summary
        self._save_data()
        
        print(format_success(f"Summary generated ({len(summary)} characters)"))
        return summary

    def add_task(self, title, description="", deadline=None, priority="medium"):
        """
        Add a new task to the current folder.
        :param title: Title of the task.
        :param description: Description of the task.
        :param deadline: Deadline in DD-MM-YYYY format.
        :param priority: Priority level (low/medium/high).
        :return: The created task.
        :raises InvalidInputError: If input validation fails.
        """
        if not title or not title.strip():
            raise InvalidInputError("Task title cannot be empty", field="title")
        
        # Validate priority
        validated_priority = validate_priority(priority)
        if not validated_priority:
            raise InvalidInputError(
                f"Invalid priority: {priority}",
                field="priority",
                valid_values=["low", "medium", "high", "l", "m", "h"]
            )

        task = {
            "id": self._generate_id(),
            "title": title[:30],
            "description": description,
            "deadline": deadline,
            "priority": validated_priority,
            "status": "pending",
            "summary": None,
            "created": datetime.now().strftime("%d-%m-%YT%H:%M:%S")
        }
        self.tasks.append(task)
        self._save_data()
        print(format_success(f"Task added: {task['title']} [ID: {task['id'][:8]}]"))
        return task

    def list_tasks(self):
        """
        List all tasks in the current folder.
        Completed tasks are displayed at the bottom.
        :return: Sorted list of tasks.
        """
        return sorted(self.tasks, key=lambda t: (t['status'] == 'completed', t['deadline'] or ""))

    def complete_task(self, task_id):
        """
        Mark a task as completed.
        :param task_id: ID or partial ID of the task.
        :raises TaskNotFoundError: If task not found.
        """
        task = self.get_task(task_id)  # This will raise TaskNotFoundError if not found
        task['status'] = 'completed'
        self._save_tasks()
        print(format_success(f"Task completed: {task['title']}"))

    def remove_task(self, task_id):
        """
        Remove a task by ID with confirmation.
        :param task_id: ID or partial ID of the task.
        :raises TaskNotFoundError: If task not found.
        """
        task = self.get_task(task_id)  # This will raise TaskNotFoundError if not found
        
        # Confirm deletion
        task_title = task['title']
        if not confirm_action(f"Delete task '{task_title}'? (yes/no):", require_yes=False):
            print(format_warning("Deletion cancelled"))
            return
        
        self.tasks.remove(task)
        self._save_tasks()
        print(format_success(f"Task deleted: {task_title}"))

    def get_task(self, task_id):
        """
        Retrieve a task by full or partial ID.
        :param task_id: Full or partial ID of the task.
        :return: The matching task.
        :raises TaskNotFoundError: If task not found.
        """
        for task in self.tasks:
            if task['id'].startswith(task_id):
                return task
        
        # Task not found - raise error with available IDs
        available_ids = [task['id'][:8] for task in self.tasks]
        raise TaskNotFoundError(task_id, available_ids)

    def edit_task(self, task_id, **kwargs):
        """
        Update task fields (description, deadline, priority).
        :param task_id: ID or partial ID of the task.
        :param kwargs: Fields to update (description, deadline, priority).
        :return: The updated task.
        """
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")
        
        # Update allowed fields
        if 'description' in kwargs:
            task['description'] = kwargs['description']
        if 'deadline' in kwargs:
            task['deadline'] = kwargs['deadline']
        if 'priority' in kwargs:
            priority = kwargs['priority'].lower()
            if priority not in ['low', 'medium', 'high']:
                raise ValueError(f"Invalid priority '{kwargs['priority']}'. Must be low, medium, or high.")
            task['priority'] = priority
        
        self._save_tasks()
        return task

    def update_task(self, task_id, **kwargs):
        """
        Update task fields (wrapper for edit_task for compatibility).
        :param task_id: ID or partial ID of the task.
        :param kwargs: Fields to update (description, deadline, priority).
        :return: The updated task.
        """
        return self.edit_task(task_id, **kwargs)

    def get_task_details(self, task_id):
        """
        Return formatted string with all task fields.
        :param task_id: ID or partial ID of the task.
        :return: Formatted task details string.
        """
        task = self.get_task(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")
        
        details = [
            "Task Details",
            "━" * 40,
            f"ID:          {task['id']}",
            f"Title:       {task['title']}",
            f"Description: {task['description'] or 'N/A'}",
            f"Summary:     {task.get('summary') or 'N/A'}",
            f"Deadline:    {task['deadline'] or 'N/A'}",
            f"Priority:    {task['priority']}",
            f"Status:      {task['status']}",
            f"Created:     {task['created']}",
            "━" * 40
        ]
        return "\n".join(details)

    def search_tasks(self, query):
        """
        Return tasks where query appears in title or description (case-insensitive).
        :param query: Search query string.
        :return: List of matching tasks.
        """
        query_lower = query.lower()
        results = []
        for task in self.tasks:
            title_match = query_lower in task['title'].lower()
            desc_match = query_lower in (task['description'] or '').lower()
            if title_match or desc_match:
                results.append(task)
        return results

    def _register_commands(self):
        """Register task-related commands."""
        self.registry.register_command('add', self.cmd_add, 'Add a new task', 'tasks')
        self.registry.register_command('list', self.cmd_list, 'List all tasks', 'tasks')
        self.registry.register_command('complete', self.cmd_complete, 'Mark task as completed', 'tasks')
        self.registry.register_command('remove', self.cmd_remove, 'Remove a task', 'tasks')
        self.registry.register_command('edit', self.cmd_edit, 'Edit a task', 'tasks')
        self.registry.register_command('view', self.cmd_view, 'View task details', 'tasks')
        self.registry.register_command('search', self.cmd_search, 'Search tasks', 'tasks')
        self.registry.register_command('summarize', self.cmd_summarize, 'Generate AI summary for a task', 'tasks')
        self.registry.register_command('cost', self.cmd_cost, 'Show cumulative OpenAI API cost', 'tasks')
        self.registry.register_command('folders', self.cmd_folders, 'List all folders', 'folders')
        self.registry.register_command('folder', self.cmd_folder, 'Switch to a folder', 'folders')
        self.registry.register_command('folder_create', self.cmd_folder_create, 'Create a new folder', 'folders')
        self.registry.register_command('folder_delete', self.cmd_folder_delete, 'Delete a folder', 'folders')

    def cmd_add(self, *args):
        """Command to add a task with optional deadline, description, and priority."""
        if not args:
            print("Error: Task title is required.")
            return
        
        # Parse arguments
        title_parts = []
        deadline = None
        description = ""
        priority = "medium"
        
        args = list(args)
        i = 0
        
        # First, collect title until we hit a flag
        while i < len(args) and not args[i].startswith('--'):
            title_parts.append(args[i])
            i += 1
        
        if not title_parts:
            print("Error: Task title is required.")
            return
        
        title = " ".join(title_parts)
        
        # Parse optional flags
        while i < len(args):
            if args[i] == '--deadline':
                if i + 1 >= len(args):
                    print("Error: --deadline requires a date argument.")
                    return
                deadline_str = args[i + 1]
                try:
                    deadline = self._parse_deadline(deadline_str)
                except ValueError as e:
                    print(f"Error: {e}")
                    return
                i += 2
            elif args[i] == '--description':
                # Collect all text until next flag or end
                desc_parts = []
                i += 1
                while i < len(args) and not args[i].startswith('--'):
                    desc_parts.append(args[i])
                    i += 1
                description = ' '.join(desc_parts)
            elif args[i] == '--priority':
                if i + 1 >= len(args):
                    print("Error: --priority requires a level argument.")
                    return
                priority = args[i + 1].lower()
                if priority not in ['low', 'medium', 'high']:
                    print(f"Error: Invalid priority '{args[i + 1]}'. Must be low, medium, or high.")
                    return
                i += 2
            else:
                print(f"Error: Unknown flag '{args[i]}'.")
                return
        
        task = self.add_task(title, description=description, deadline=deadline, priority=priority)
        print(f"✓ Task added: {task['title']} #{task['id']}")
        if deadline:
            print(f"  Deadline: {deadline}")
        if description:
            print(f"  Description: {description}")
        if priority != "medium":
            print(f"  Priority: {priority}")

    def cmd_list(self, *args):
        """Command to list tasks."""
        tasks = self.list_tasks()
        if not tasks:
            print("No tasks available.")
            return

        # Separate completed tasks from others
        completed_tasks = [t for t in tasks if t['status'] == 'completed']
        pending_tasks = [t for t in tasks if t['status'] != 'completed']

        # Format tasks for display
        table = []
        for t in pending_tasks + completed_tasks:  # Completed tasks at the bottom
            status = "✓ completed" if t['status'] == "completed" else t['status']
            
            # Show actual title in Title column
            title = t['title']
            
            # Determine what to show in Description column
            summary = t.get('summary')
            description = t.get('description', '') or ''
            
            # If task has AI summary, show it in Description column
            if summary:
                display_desc = summary
                if len(display_desc) > 40:
                    display_desc = display_desc[:37] + "..."
            # Else if description exists, show truncated version
            elif description:
                if len(description) > 40:
                    display_desc = description[:37] + "..."
                else:
                    display_desc = description
            else:
                display_desc = "-"
            
            table.append([t['id'], title, display_desc, t['deadline'] or "-", t['priority'], status])

        # Print headers
        headers = ["ID", "Title", "Description", "Deadline", "Priority", "Status"]
        
        # Add separator row after headers
        if table:
            # Create separator row with dashes matching column widths
            separator = ["─" * 2, "─" * 20, "─" * 40, "─" * 10, "─" * 8, "─" * 10]
            table.insert(0, separator)
        
        # Print table without borders
        print(tabulate(table, headers=headers, tablefmt="plain"))

    def cmd_complete(self, *args):
        """Command to complete a task."""
        if not args:
            print("Error: Task ID is required.")
            return
        for task_id in args:
            try:
                task = self.get_task(task_id)
                if task:
                    self.complete_task(task_id)
                    print(f"✓ Task completed: {task['title']}")
                else:
                    print(f"Error: Task with ID {task_id} not found.")
            except ValueError as e:
                print(e)

    def cmd_remove(self, *args):
        """Command to remove a task."""
        if not args:
            print("Error: Task ID is required.")
            return
        for task_id in args:
            try:
                task = self.get_task(task_id)
                if task:
                    self.remove_task(task_id)
                    print(f"✓ Task removed: {task['title']}")
                else:
                    print(f"Error: Task with ID {task_id} not found.")
            except ValueError as e:
                print(e)

    def cmd_edit(self, *args):
        """Command to edit a task."""
        if not args:
            print("Error: Task ID is required.")
            return
        
        task_id = args[0]
        args = list(args[1:])
        
        # Parse flags
        updates = {}
        i = 0
        while i < len(args):
            if args[i] == '--description':
                # Collect all text until next flag or end
                desc_parts = []
                i += 1
                while i < len(args) and not args[i].startswith('--'):
                    desc_parts.append(args[i])
                    i += 1
                updates['description'] = ' '.join(desc_parts)
            elif args[i] == '--deadline':
                if i + 1 >= len(args):
                    print("Error: --deadline requires a date argument.")
                    return
                deadline_str = args[i + 1]
                # Validate and normalize deadline format
                try:
                    updates['deadline'] = self._parse_deadline(deadline_str)
                except ValueError as e:
                    print(f"Error: {e}")
                    return
                i += 2
            elif args[i] == '--priority':
                if i + 1 >= len(args):
                    print("Error: --priority requires a level argument.")
                    return
                priority = args[i + 1].lower()
                if priority not in ['low', 'medium', 'high']:
                    print(f"Error: Invalid priority '{args[i + 1]}'. Must be low, medium, or high.")
                    return
                updates['priority'] = priority
                i += 2
            else:
                print(f"Error: Unknown flag '{args[i]}'.")
                return
        
        if not updates:
            print("Error: No fields to update. Use --description, --deadline, or --priority.")
            return
        
        try:
            task = self.edit_task(task_id, **updates)
            print(f"✓ Task updated: {task['title']}")
            for key, value in updates.items():
                display_key = key.capitalize()
                print(f"  {display_key}: {value}")
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_view(self, *args):
        """Command to view task details."""
        if not args:
            print("Error: Task ID is required.")
            return
        
        task_id = args[0]
        try:
            details = self.get_task_details(task_id)
            print(details)
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_search(self, *args):
        """Command to search tasks."""
        if not args:
            print("Error: Search query is required.")
            return
        
        query = ' '.join(args)
        results = self.search_tasks(query)
        
        if not results:
            print(f"No tasks found matching '{query}'.")
            return
        
        print(f"Found {len(results)} task(s):")
        table = []
        for t in results:
            status = "✓ completed" if t['status'] == "completed" else t['status']
            
            # Show actual title in Title column
            title = t['title']
            
            # Determine what to show in Description column
            summary = t.get('summary')
            description = t.get('description', '') or ''
            
            # If task has AI summary, show it in Description column
            if summary:
                display_desc = summary
                if len(display_desc) > 40:
                    display_desc = display_desc[:37] + "..."
            # Else if description exists, show truncated version
            elif description:
                if len(description) > 40:
                    display_desc = description[:37] + "..."
                else:
                    display_desc = description
            else:
                display_desc = "-"
            
            table.append([t['id'], title, display_desc, t['deadline'] or "-", t['priority'], status])
        
        print(tabulate(table, headers=["ID", "Title", "Description", "Deadline", "Priority", "Status"], tablefmt="plain"))

    def cmd_folders(self, *args):
        """Command to list all folders with task counts."""
        folders = self.get_folders()
        current_folder = self.data["current_folder"]
        print("Task Folders:")
        for folder, count in folders.items():
            prefix = "*" if folder == current_folder else " "
            print(f"{prefix} {folder} ({count} tasks)")

    def cmd_folder(self, *args):
        """Command to switch to a folder, creating it if necessary."""
        if not args:
            print("Error: Folder name is required.")
            return
        folder_name = args[0]
        try:
            self.switch_folder(folder_name)
            print(f"✓ Switched to folder: {folder_name}")
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_folder_create(self, *args):
        """Command to create a new folder."""
        if not args:
            print("Error: Folder name is required.")
            return
        folder_name = args[0]
        try:
            self.create_folder(folder_name)
            print(f"✓ Created folder: {folder_name}")
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_folder_delete(self, *args):
        """Command to delete a folder after confirmation."""
        if not args:
            print("Error: Folder name is required.")
            return
        folder_name = args[0]
        try:
            if folder_name == "default":
                print("Error: Cannot delete the default folder.")
                return
            task_count = len(self.data["folders"].get(folder_name, []))
            confirmation = input(f"⚠️  WARNING: This will delete folder '{folder_name}' and all {task_count} task(s).\nAre you sure? (yes/no): ")
            if confirmation.lower() == "yes":
                self.delete_folder(folder_name)
                print(f"✓ Folder deleted: {folder_name}")
            else:
                print("✗ Folder deletion canceled.")
        except ValueError as e:
            print(f"Error: {e}")

    def cmd_summarize(self, *args):
        """Command to generate AI summary for a task."""
        if not args:
            print("Error: Task ID is required.")
            return
        
        task_id = args[0]
        try:
            task = self.get_task(task_id)
            if not task:
                print(f"Error: Task with ID {task_id} not found.")
                return
            
            description = task.get('description', '')
            if not description:
                print("Error: Task has no description to summarize.")
                return
            
            word_count = self._count_words(description)
            if word_count <= 100:
                print(f"Description is short ({word_count} words), no summary needed.")
                return
            
            # Check if OpenAI client is available
            if not self.openai_client:
                print("Error: OpenAI client not initialized. Check your OPENAI_API_KEY.")
                return
            
            print("Generating summary...")
            summary = self.summarize_task(task_id)
            print(f"✓ Summary created: {summary}")
            
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def cmd_cost(self, *args):
        """Command to show cumulative OpenAI API cost for the session."""
        if self.session_cost == 0:
            print("No API calls made this session. Cost: $0.00")
        else:
            print(f"Session API Cost: ${self.session_cost:.6f}")
            print(f"Estimated cost: ${self.session_cost:.2f}")
            
            # Provide breakdown if cost > 0
            if self.session_cost > 0:
                print("\nPricing (gpt-4o-mini):")
                print("  Input:  $0.150 per 1M tokens")
                print("  Output: $0.600 per 1M tokens")