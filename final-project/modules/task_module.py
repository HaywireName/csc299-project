import uuid
from datetime import datetime
from tabulate import tabulate

class TaskManager:
    def __init__(self, data_manager, registry):
        """
        Initialize TaskManager with dependencies.
        :param data_manager: Handles data storage and retrieval.
        :param registry: Command registry for registering commands.
        """
        self.data_manager = data_manager
        self.registry = registry
        self.tasks = []  # In-memory task list
        self._load_tasks()
        self._register_commands()

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

    def add_task(self, title, description="", deadline=None, priority="medium"):
        """
        Add a new task.
        :param title: Title of the task.
        :param description: Description of the task.
        :param deadline: Deadline in DD-MM-YYYY format.
        :param priority: Priority level (low/medium/high).
        :return: The created task.
        """
        if not title.strip():
            raise ValueError("Task title cannot be empty.")

        task = {
            "id": self._generate_id(),
            "title": title[:30],
            "description": description,
            "deadline": deadline,
            "priority": priority,
            "status": "pending",
            "created": datetime.now().strftime("%d-%m-%YT%H:%M:%S")
        }
        self.tasks.append(task)
        self._save_tasks()
        return task

    def list_tasks(self):
        """
        List all tasks sorted by status and deadline.
        Completed tasks are displayed at the bottom.
        :return: Sorted list of tasks.
        """
        return sorted(self.tasks, key=lambda t: (t['status'] == 'completed', t['deadline'] or ""))

    def complete_task(self, task_id):
        """
        Mark a task as completed.
        :param task_id: ID or partial ID of the task.
        """
        task = self.get_task(task_id)
        if task:
            task['status'] = 'completed'
            self._save_tasks()
        else:
            raise ValueError(f"Task with ID {task_id} not found.")

    def remove_task(self, task_id):
        """
        Remove a task by ID.
        :param task_id: ID or partial ID of the task.
        """
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            self._save_tasks()
        else:
            raise ValueError(f"Task with ID {task_id} not found.")

    def get_task(self, task_id):
        """
        Retrieve a task by full or partial ID.
        :param task_id: Full or partial ID of the task.
        :return: The matching task.
        """
        for task in self.tasks:
            if task['id'].startswith(task_id):
                return task
        return None

    def _register_commands(self):
        """Register task-related commands."""
        self.registry.register_command('add', self.cmd_add, 'Add a new task', 'tasks')
        self.registry.register_command('list', self.cmd_list, 'List all tasks', 'tasks')
        self.registry.register_command('complete', self.cmd_complete, 'Mark task as completed', 'tasks')
        self.registry.register_command('remove', self.cmd_remove, 'Remove a task', 'tasks')

    def cmd_add(self, *args):
        """Command to add a task."""
        if not args:
            print("Error: Task title is required.")
            return
        # Join all arguments to form the full title
        title = " ".join(args)
        task = self.add_task(title)
        print(f"✓ Task added: {task['title']} #{task['id']}")

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
            table.append([t['id'], t['title'], t['deadline'] or "-", t['priority'], status])

        # Print table without borders
        print(tabulate(table, headers=["ID", "Title", "Deadline", "Priority", "Status"], tablefmt="plain"))

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