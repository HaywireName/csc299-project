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
    """Manages task operations including CRUD, AI summarization, and folder organization.
    
    The TaskManager handles all task-related functionality including creating, reading,
    updating, and deleting tasks, organizing them into folders, generating AI summaries
    for task descriptions, and tracking API costs for AI operations.
    
    Attributes:
        data_manager: Data persistence manager for loading/saving tasks.
        registry: Command registry for registering task commands.
        data: Complete task data structure with folders and current folder.
        tasks: List of tasks in the current folder.
        session_cost: Cumulative OpenAI API cost for the session.
        openai_client: OpenAI API client instance.
    """
    
    def __init__(self, data_manager, registry):
        """Initialize TaskManager with dependencies.
        
        Loads task data from storage, initializes the OpenAI client for AI features,
        and registers all task-related commands with the command registry.
        
        Args:
            data_manager: Data persistence manager instance.
            registry: Command registry instance for registering commands.
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
        """Initialize OpenAI client with API key from environment.
        
        Attempts to create an OpenAI client using the API key from the
        OPENAI_API_KEY environment variable. If the key is not found or
        initialization fails, AI features will be disabled.
        
        Raises:
            Prints warning if API key not found or initialization fails.
        """
        try:
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                print("Warning: OPENAI_API_KEY not found. AI features will be disabled.")
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")

    def _save_data(self):
        """Save the entire data structure to tasks.json.
        
        Persists the complete task data structure including all folders,
        tasks, and metadata to the tasks.json file.
        """
        self.data_manager.save("tasks.json", self.data)

    def get_folders(self):
        """Return a dictionary of folder names and their task counts.
        
        Returns:
            dict: Dictionary mapping folder names (str) to task counts (int).
        """
        return {folder: len(tasks) for folder, tasks in self.data["folders"].items()}

    def switch_folder(self, folder_name):
        """Switch to a different folder, creating it if necessary.
        
        Changes the current active folder to the specified folder name.
        If the folder doesn't exist, it will be created automatically.
        Updates the tasks reference to point to the new folder's tasks.
        
        Args:
            folder_name: Name of the folder to switch to.
        """
        if folder_name not in self.data["folders"]:
            self.data["folders"][folder_name] = []
        self.data["current_folder"] = folder_name
        self.tasks = self.data["folders"][folder_name]
        self._save_data()

    def create_folder(self, folder_name):
        """Create a new folder if it doesn't exist.
        
        Creates a new empty folder with the specified name. The folder
        is immediately persisted to storage.
        
        Args:
            folder_name: Name of the folder to create.
        
        Raises:
            ValueError: If a folder with the same name already exists.
        """
        if folder_name in self.data["folders"]:
            raise ValueError(f"Folder '{folder_name}' already exists.")
        self.data["folders"][folder_name] = []
        self._save_data()

    def delete_folder(self, folder_name):
        """Delete a folder and all its tasks, except the default folder.
        
        Removes a folder and all tasks contained within it. The default
        folder cannot be deleted. If the deleted folder is the current
        folder, automatically switches to the default folder.
        
        Args:
            folder_name: Name of the folder to delete.
        
        Raises:
            ValueError: If trying to delete the default folder or if the
                folder doesn't exist.
        """
        if folder_name == "default":
            raise ValueError("Cannot delete the default folder.")
        if folder_name not in self.data["folders"]:
            raise ValueError(f"Folder '{folder_name}' does not exist.")
        del self.data["folders"][folder_name]
        if self.data["current_folder"] == folder_name:
            self.switch_folder("default")
        self._save_data()

    def _load_tasks(self):
        """Load tasks from the current folder.
        
        Loads tasks from storage for the currently active folder and
        updates the tasks reference. If no tasks exist, initializes
        with an empty list.
        """
        folder = self._get_current_folder()
        self.tasks = self.data_manager.load(folder) or []

    def _save_tasks(self):
        """Save tasks to the current folder.
        
        Persists the current tasks list to storage in the currently
        active folder.
        """
        folder = self._get_current_folder()
        self.data_manager.save(folder, self.tasks)

    def _get_current_folder(self):
        """Return the current folder name from data.
        
        Returns:
            str: Name of the currently active folder.
        """
        return self.data_manager.get_current_folder()

    def _generate_id(self):
        """Generate a unique ID for a new task.
        
        Creates a simple numeric ID based on the current number of tasks
        in the folder.
        
        Returns:
            str: Unique task ID as a string.
        """
        return str(len(self.tasks) + 1)
    
    def _reindex_tasks(self):
        """Reindex all tasks with sequential IDs, completed tasks have separate numbering."""
        # Separate pending and completed tasks
        pending = [t for t in self.tasks if t['status'] != 'completed']
        completed = [t for t in self.tasks if t['status'] == 'completed']
        
        # Reindex pending tasks (1, 2, 3...)
        for idx, task in enumerate(pending, start=1):
            task['id'] = str(idx)
        
        # Reindex completed tasks separately (1, 2, 3...)
        for idx, task in enumerate(completed, start=1):
            task['id'] = str(idx)
        
        # Update tasks list to maintain order
        self.tasks[:] = pending + completed

    def _parse_deadline(self, deadline_str):
        """Parse deadline from various formats and return DD-MM-YYYY format.
        
        Supports multiple date formats including DD-MM-YYYY, MM-DD-YYYY,
        YYYY-DD-MM, MM/DD, MM-YY, MM/DD/YYYY, YYYY/DD/MM, and the keyword
        'tomorrow'. Automatically handles separators (- or /).
        
        Args:
            deadline_str: Deadline string in various supported formats.
        
        Returns:
            str: Formatted deadline string in DD-MM-YYYY format, or None
                if input is empty.
        
        Raises:
            ValueError: If the deadline format is not recognized or if the
                date is invalid.
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
                # Could be DD-MM-YYYY, MM-DD-YYYY, YYYY-DD-MM, or similar
                if len(parts[0]) == 4:
                    # YYYY-DD-MM format
                    year, day, month = int(parts[0]), int(parts[1]), int(parts[2])
                elif len(parts[2]) == 4:
                    # Either DD-MM-YYYY or MM-DD-YYYY
                    first, second, year = int(parts[0]), int(parts[1]), int(parts[2])
                    # Check if first part is > 12, then it must be DD-MM-YYYY
                    if first > 12:
                        day, month = first, second
                    # Check if second part is > 12, then it must be MM-DD-YYYY
                    elif second > 12:
                        month, day = first, second
                    # Both <= 12, try DD-MM-YYYY first (more common internationally)
                    else:
                        day, month = first, second
                else:
                    # MM-DD-YY format
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
            raise ValueError(f"Invalid deadline format '{deadline_str}'. Supported formats: DD-MM-YYYY, MM-DD-YYYY, YYYY-DD-MM, MM/DD/YYYY, MM/DD, MM-YY, or 'tomorrow'")

    def _count_words(self, text):
        """Count the number of words in a text string.
        
        Splits the text by whitespace and counts the resulting tokens.
        
        Args:
            text: Text string to count words in.
        
        Returns:
            int: Number of words in the text, or 0 if text is empty/None.
        """
        if not text:
            return 0
        return len(text.split())

    def _call_openai_summary(self, text):
        """Call OpenAI API to generate a 10-15 word summary.
        
        Sends text to the OpenAI API for summarization using gpt-4o-mini.
        Implements retry logic with exponential backoff for handling rate
        limits and transient failures. Tracks token usage and costs.
        
        Args:
            text: The text to summarize.
        
        Returns:
            str: AI-generated summary of 10-15 words.
        
        Raises:
            APIError: If the OpenAI client is not initialized, if API call
                fails after retries, or if rate limits/quota are exceeded.
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
        """Generate an AI summary for a task description.
        
        Creates a concise AI-generated summary for tasks with descriptions
        of at least 20 words. The summary is saved to the task metadata.
        
        Args:
            task_id: Full or partial task ID.
        
        Returns:
            str: The generated summary text.
        
        Raises:
            TaskNotFoundError: If the task with the given ID is not found.
            InvalidInputError: If the description is missing or shorter
                than 20 words.
            APIError: If the OpenAI API call fails.
        """
        task = self.get_task(task_id)  # This will raise TaskNotFoundError if not found
        
        description = task.get('description', '')
        if not description:
            raise InvalidInputError("Task has no description to summarize", field="description")
        
        word_count = self._count_words(description)
        if word_count < 20:
            raise InvalidInputError(
                f"Description is too short ({word_count} words). Minimum 20 words required for summarization.",
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
        """Add a new task to the current folder.
        
        Creates a new task with the specified properties and adds it to
        the current folder. Title is truncated to 30 characters if longer.
        Validates priority and generates a unique ID automatically.
        
        Args:
            title: Title of the task (required, max 30 chars displayed).
            description: Detailed description of the task. Defaults to empty string.
            deadline: Deadline in DD-MM-YYYY format. Defaults to None.
            priority: Priority level (low/medium/high or l/m/h). Defaults to 'medium'.
        
        Returns:
            dict: The created task dictionary with all metadata.
        
        Raises:
            InvalidInputError: If title is empty or priority is invalid.
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
        self._reindex_tasks()
        self._save_data()
        print(format_success(f"Task added: {task['title']} [ID: {task['id']}]"))
        return task

    def list_tasks(self):
        """List all tasks in the current folder.
        
        Returns all tasks sorted with completed tasks at the bottom and
        remaining tasks sorted by deadline.
        
        Returns:
            list: Sorted list of task dictionaries.
        """
        return sorted(self.tasks, key=lambda t: (t['status'] == 'completed', t['deadline'] or ""))

    def complete_task(self, task_id):
        """Mark a task as completed.
        
        Updates the task status to 'completed' and saves the changes.
        Reindexes tasks to update IDs.
        
        Args:
            task_id: Full or partial task ID.
        
        Raises:
            TaskNotFoundError: If the task with the given ID is not found.
        """
        task = self.get_task(task_id)  # This will raise TaskNotFoundError if not found
        task['status'] = 'completed'
        self._reindex_tasks()
        self._save_data()

    def remove_task(self, task_id):
        """Remove a task by ID with confirmation.
        
        Prompts for user confirmation before permanently deleting a task
        from the current folder.
        
        Args:
            task_id: Full or partial task ID.
        
        Raises:
            TaskNotFoundError: If the task with the given ID is not found.
        """
        task = self.get_task(task_id)  # This will raise TaskNotFoundError if not found
        
        # Confirm deletion
        task_title = task['title']
        if not confirm_action(f"Delete task '{task_title}'? (yes/no):", require_yes=False):
            print(format_warning("Deletion cancelled"))
            return
        
        self.tasks.remove(task)
        self._reindex_tasks()
        self._save_data()

    def get_task(self, task_id):
        """Retrieve a task by full or partial ID.
        
        Searches for a task where the ID starts with the provided string,
        allowing partial ID matching for convenience.
        
        Args:
            task_id: Full or partial task ID to search for.
        
        Returns:
            dict: The matching task dictionary.
        
        Raises:
            TaskNotFoundError: If no task with matching ID is found. Includes
                list of available task IDs in the error.
        """
        for task in self.tasks:
            if task['id'].startswith(task_id):
                return task
        
        # Task not found - raise error with available IDs
        available_ids = [task['id'][:8] for task in self.tasks]
        raise TaskNotFoundError(task_id, available_ids)

    def edit_task(self, task_id, **kwargs):
        """Update task fields (description, deadline, priority).
        
        Modifies one or more fields of an existing task. Only provided
        fields are updated; others remain unchanged.
        
        Args:
            task_id: Full or partial task ID.
            **kwargs: Fields to update. Supported keys:
                - description: New description text.
                - deadline: New deadline in DD-MM-YYYY format.
                - priority: New priority (low/medium/high).
        
        Returns:
            dict: The updated task dictionary.
        
        Raises:
            ValueError: If task not found or priority value is invalid.
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
        """Update task fields (wrapper for edit_task for compatibility).
        
        Convenience wrapper that calls edit_task. Provided for backward
        compatibility and alternative naming.
        
        Args:
            task_id: Full or partial task ID.
            **kwargs: Fields to update (description, deadline, priority).
        
        Returns:
            dict: The updated task dictionary.
        
        Raises:
            ValueError: If task not found or field value is invalid.
        """
        return self.edit_task(task_id, **kwargs)

    def get_task_details(self, task_id):
        """Return formatted string with all task fields.
        
        Formats all task information into a readable multi-line string
        with headers and separators.
        
        Args:
            task_id: Full or partial task ID.
        
        Returns:
            str: Formatted task details with all fields.
        
        Raises:
            ValueError: If task with the given ID is not found.
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
        """Return tasks where query appears in title or description.
        
        Performs case-insensitive search across task titles and descriptions
        in the current folder.
        
        Args:
            query: Search query string.
        
        Returns:
            list: List of matching task dictionaries.
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
        """Register task-related commands.
        
        Registers all task management commands (add, list, complete, remove,
        edit, view, search, summarize, cost, folders, folder) with the
        command registry.
        """
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
        self.registry.register_command('folder', self.cmd_folder, 'Manage folders (use -a to add, -d to delete)', 'folders')

    def cmd_add(self, *args):
        """Command to add a task with optional deadline, description, and priority.
        
        Parses command-line arguments to create a new task. Supports flags:
        -dl/--deadline, -desc/--description, -p/--priority.
        
        Args:
            *args: Command arguments. First non-flag arguments form the title,
                followed by optional flags and their values.
        """
        if not args:
            print("Error: Task title is required.")
            print("Usage: add <title> [-p priority] [-desc description] [-dl deadline]")
            return
        
        # Parse arguments
        title_parts = []
        deadline = None
        description = ""
        priority = "medium"
        
        args = list(args)
        i = 0
        
        # First, collect title until we hit a flag
        while i < len(args) and not args[i].startswith('-'):
            title_parts.append(args[i])
            i += 1
        
        if not title_parts:
            print("Error: Task title is required.")
            return
        
        title = " ".join(title_parts)
        
        # Parse optional flags (support both old and new format)
        while i < len(args):
            if args[i] in ['-dl', '--deadline']:
                if i + 1 >= len(args):
                    print("Error: -dl requires a date argument.")
                    return
                deadline_str = args[i + 1]
                try:
                    deadline = self._parse_deadline(deadline_str)
                except ValueError as e:
                    print(f"Error: {e}")
                    return
                i += 2
            elif args[i] in ['-desc', '--description']:
                # Collect all text until next flag or end
                desc_parts = []
                i += 1
                while i < len(args) and not args[i].startswith('-'):
                    desc_parts.append(args[i])
                    i += 1
                description = ' '.join(desc_parts)
            elif args[i] in ['-p', '--priority']:
                if i + 1 >= len(args):
                    print("Error: -p requires a level argument.")
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
        # Task add confirmation already printed by add_task()
        if deadline:
            print(f"  Deadline: {deadline}")
        if description:
            print(f"  Description: {description}")
        if priority != "medium":
            print(f"  Priority: {priority}")

    def cmd_list(self, *args):
        """Command to list tasks.
        
        Displays all tasks in the current folder in a formatted table.
        Shows AI summaries when available, completed tasks in separate section.
        
        Args:
            *args: Unused command arguments.
        """
        tasks = self.list_tasks()
        if not tasks:
            print("No tasks available.")
            return

        # Separate completed tasks from others
        completed_tasks = [t for t in tasks if t['status'] == 'completed']
        pending_tasks = [t for t in tasks if t['status'] != 'completed']

        # Helper function to format task row
        def format_task_row(t):
            # Show actual title in Title column (truncate if needed)
            title = t['title']
            if len(title) > 25:
                title = title[:22] + "..."
            
            # Determine what to show in Description column
            summary = t.get('summary')
            description = t.get('description', '') or ''
            
            # If task has AI summary, show it in Description column
            if summary:
                display_desc = summary
                if len(display_desc) > 35:
                    display_desc = display_desc[:32] + "..."
            # Else if description exists, show truncated version
            elif description:
                if len(description) > 35:
                    display_desc = description[:32] + "..."
                else:
                    display_desc = description
            else:
                display_desc = "-"
            
            return [t['id'], title, display_desc, t['deadline'] or "-", t['priority']]

        # Print pending tasks
        if pending_tasks:
            print(f"\n{'ID':<4} {'Title':<26} {'Description':<36} {'Deadline':<12} {'Priority':<10}")
            print("─" * 4 + " " + "─" * 26 + " " + "─" * 36 + " " + "─" * 12 + " " + "─" * 10)
            
            for t in pending_tasks:
                row = format_task_row(t)
                print(f"{row[0]:<4} {row[1]:<26} {row[2]:<36} {row[3]:<12} {row[4]:<10}")
        
        # Print completed tasks section
        if completed_tasks:
            print(f"\n{'Completed Tasks':<90}")
            print("─" * 90)
            print(f"{'ID':<4} {'Title':<26} {'Description':<36} {'Deadline':<12} {'Priority':<10}")
            print("─" * 4 + " " + "─" * 26 + " " + "─" * 36 + " " + "─" * 12 + " " + "─" * 10)
            
            for t in completed_tasks:
                row = format_task_row(t)
                print(f"{row[0]:<4} {row[1]:<26} {row[2]:<36} {row[3]:<12} {row[4]:<10}")
        
        print()

    def cmd_complete(self, *args):
        """Command to complete a task.
        
        Marks one or more tasks as completed by their IDs.
        
        Args:
            *args: One or more task IDs (full or partial) to complete.
        """
        if not args:
            print("Error: Task ID is required.")
            return
        for task_id in args:
            try:
                task = self.get_task(task_id)
                if task:
                    self.complete_task(task_id)
                    print(format_success(f"Task completed: {task['title']}"))
                else:
                    print(f"Error: Task with ID {task_id} not found.")
            except ValueError as e:
                print(e)

    def cmd_remove(self, *args):
        """Command to remove a task.
        
        Deletes one or more tasks by their IDs with confirmation.
        
        Args:
            *args: One or more task IDs (full or partial) to remove.
        """
        if not args:
            print("Error: Task ID is required.")
            return
        for task_id in args:
            try:
                task = self.get_task(task_id)
                if task:
                    task_title = task['title']
                    self.remove_task(task_id)
                    print(format_success(f"Task removed: {task_title}"))
                else:
                    print(f"Error: Task with ID {task_id} not found.")
            except ValueError as e:
                print(e)

    def cmd_edit(self, *args):
        """Command to edit a task.
        
        Modifies task fields using flags: --description, --deadline, --priority.
        
        Args:
            *args: First argument is task ID, followed by flag-value pairs.
        """
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
        """Command to view task details.
        
        Displays all fields of a task in formatted output.
        
        Args:
            *args: Task ID (full or partial) to view.
        """
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
        
        # Separate completed from pending
        completed_results = [t for t in results if t['status'] == 'completed']
        pending_results = [t for t in results if t['status'] != 'completed']
        
        print(f"Found {len(results)} task(s):")
        
        # Helper function to format task row
        def format_task_row(t):
            title = t['title']
            if len(title) > 25:
                title = title[:22] + "..."
            
            summary = t.get('summary')
            description = t.get('description', '') or ''
            
            if summary:
                display_desc = summary
                if len(display_desc) > 35:
                    display_desc = display_desc[:32] + "..."
            elif description:
                if len(description) > 35:
                    display_desc = description[:32] + "..."
                else:
                    display_desc = description
            else:
                display_desc = "-"
            
            return [t['id'], title, display_desc, t['deadline'] or "-", t['priority']]
        
        # Print pending tasks
        if pending_results:
            print(f"\n{'ID':<4} {'Title':<26} {'Description':<36} {'Deadline':<12} {'Priority':<10}")
            print("─" * 4 + " " + "─" * 26 + " " + "─" * 36 + " " + "─" * 12 + " " + "─" * 10)
            
            for t in pending_results:
                row = format_task_row(t)
                print(f"{row[0]:<4} {row[1]:<26} {row[2]:<36} {row[3]:<12} {row[4]:<10}")
        
        # Print completed tasks
        if completed_results:
            print(f"\n{'Completed Tasks':<90}")
            print("─" * 90)
            print(f"{'ID':<4} {'Title':<26} {'Description':<36} {'Deadline':<12} {'Priority':<10}")
            print("─" * 4 + " " + "─" * 26 + " " + "─" * 36 + " " + "─" * 12 + " " + "─" * 10)
            
            for t in completed_results:
                row = format_task_row(t)
                print(f"{row[0]:<4} {row[1]:<26} {row[2]:<36} {row[3]:<12} {row[4]:<10}")
        
        print()

    def cmd_folders(self, *args):
        """Command to list all folders with task counts."""
        folders = self.get_folders()
        current_folder = self.data["current_folder"]
        print("Task Folders:")
        for folder, count in folders.items():
            prefix = "*" if folder == current_folder else " "
            print(f"{prefix} {folder} ({count} tasks)")

    def cmd_folder(self, *args):
        """Command to switch to a folder or manage folders with -a (add) and -d (delete) flags."""
        if not args:
            print("Error: Folder name or flag is required.")
            print("Usage: folder <name>           - Switch to folder")
            print("       folder -a <name>        - Create new folder")
            print("       folder -d <name>        - Delete folder")
            return
        
        # Check for -a flag (add/create)
        if args[0] == '-a':
            if len(args) < 2:
                print("Error: Folder name is required.")
                print("Usage: folder -a <name>")
                return
            folder_name = args[1]
            try:
                self.create_folder(folder_name)
                print(f"✓ Created folder: {folder_name}")
            except ValueError as e:
                print(f"Error: {e}")
            return
        
        # Check for -d flag (delete)
        if args[0] == '-d':
            if len(args) < 2:
                print("Error: Folder name is required.")
                print("Usage: folder -d <name>")
                return
            folder_name = args[1]
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
            return
        
        # No flag - switch to folder
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
            if word_count < 20:
                print(f"Description is short ({word_count} words), no summary needed (minimum 20 words).")
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