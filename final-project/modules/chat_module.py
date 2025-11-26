import os
import uuid
import textwrap
from datetime import datetime
from openai import OpenAI


class ChatManager:
    """Manages interactive chat sessions with OpenAI GPT models.
    
    The ChatManager provides an interactive chat interface with context-aware
    conversations. Supports multiple context modes (general, tasks, docs, all)
    to provide the AI with relevant information from the user's workspace.
    Features conversation history, streaming responses, and cost tracking.
    
    Attributes:
        data_manager: Data persistence manager for chat history.
        registry: Command registry for registering chat commands.
        agent_manager: AgentManager instance for agent slash commands.
        cost_tracker: CostTracker instance for API cost tracking.
        openai_client: OpenAI API client instance.
        current_conversation_id: ID of the active conversation.
        conversations: List of all conversation histories.
        context_type: Current context mode (general/tasks/docs/all).
        context_data: Loaded context data for the AI.
    """
    
    def __init__(self, data_manager, registry, agent_manager=None, cost_tracker=None, task_manager=None, document_manager=None):
        """Initialize ChatManager with dependencies.
        
        Loads conversation history, initializes OpenAI client, and registers
        chat commands.
        
        Args:
            data_manager: Data persistence manager instance.
            registry: Command registry instance for registering commands.
            agent_manager: AgentManager instance for agent commands (optional).
            cost_tracker: CostTracker instance for tracking API costs (optional).
            task_manager: TaskManager instance for creating tasks from chat (optional).
            document_manager: DocumentManager instance for adding docs from chat (optional).
        """
        self.data_manager = data_manager
        self.registry = registry
        self.agent_manager = agent_manager
        self.cost_tracker = cost_tracker
        self.task_manager = task_manager
        self.document_manager = document_manager
        self.openai_client = None
        self.current_conversation_id = None
        self.conversations = []
        self.context_type = 'general'
        self.context_data = None
        self._init_openai_client()
        self._load_conversations()
        self._register_commands()

    def _init_openai_client(self):
        """Initialize OpenAI client with API key from environment.
        
        Attempts to create an OpenAI client using the API key from the
        OPENAI_API_KEY environment variable. Chat functionality will be
        disabled if the key is not found.
        """
        try:
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                print("Warning: OPENAI_API_KEY not found. Chat functionality will be disabled.")
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")

    def _load_conversations(self):
        """Load conversation history from storage.
        
        Loads all saved conversation histories from chat_history.json.
        Initializes with empty list if no history exists.
        """
        data = self.data_manager.load("chat_history.json")
        if data and 'conversations' in data:
            self.conversations = data['conversations']
        else:
            self.conversations = []

    def _save_conversations(self):
        """Save conversation history to storage.
        
        Persists all conversation histories to chat_history.json.
        """
        data = {'conversations': self.conversations}
        self.data_manager.save("chat_history.json", data)

    def _get_current_conversation(self):
        """Get or create current conversation.
        
        Returns the active conversation if one exists, otherwise creates
        a new conversation with a unique ID.
        
        Returns:
            dict: Conversation dictionary with id, started timestamp, and
                messages list.
        """
        if self.current_conversation_id:
            # Find existing conversation
            for conv in self.conversations:
                if conv['id'] == self.current_conversation_id:
                    return conv
        
        # Create new conversation
        conversation = {
            'id': f"conv_{str(uuid.uuid4())[:8]}",
            'started': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            'messages': []
        }
        self.conversations.append(conversation)
        self.current_conversation_id = conversation['id']
        self._save_conversations()
        return conversation

    def _get_conversation_history(self, limit=10):
        """Get last N messages from current conversation.
        
        Retrieves the most recent messages to provide context for the AI.
        Limits message history to prevent token overuse.
        
        Args:
            limit: Maximum number of messages to retrieve. Defaults to 10.
        
        Returns:
            list: List of message dictionaries containing role, content, and timestamp.
        """
        conversation = self._get_current_conversation()
        messages = conversation['messages']
        
        # Return last N messages
        if len(messages) <= limit:
            return messages
        else:
            return messages[-limit:]

    def _save_message(self, role, content):
        """Save a message to the current conversation.
        
        Appends a message to the active conversation history with timestamp
        and persists to storage.
        
        Args:
            role: Message role ('user' or 'assistant').
            content: Message content text.
        """
        conversation = self._get_current_conversation()
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        conversation['messages'].append(message)
        self._save_conversations()

    def _clear_conversation(self):
        """Clear the current conversation history.
        
        Removes all messages from the active conversation while preserving
        the conversation structure.
        
        Returns:
            bool: True if conversation was cleared, False if no active conversation.
        """
        if self.current_conversation_id:
            for conv in self.conversations:
                if conv['id'] == self.current_conversation_id:
                    conv['messages'] = []
                    self._save_conversations()
                    return True
        return False

    def _format_response(self, text, width=80):
        """Format response text with word wrapping.
        
        Wraps long lines while preserving paragraph structure and intentional
        line breaks within paragraphs.
        
        Args:
            text: Text to format.
            width: Maximum line width in characters. Defaults to 80.
        
        Returns:
            str: Formatted text with proper word wrapping.
        """
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            # Preserve single newlines within paragraphs
            lines = para.split('\n')
            formatted_lines = []
            
            for line in lines:
                if line.strip():
                    # Wrap long lines
                    wrapped = textwrap.fill(line, width=width)
                    formatted_lines.append(wrapped)
                else:
                    formatted_lines.append('')
            
            formatted_paragraphs.append('\n'.join(formatted_lines))
        
        return '\n\n'.join(formatted_paragraphs)

    def _load_tasks_context(self):
        """Load all tasks from all folders and format for AI context.
        
        Retrieves all tasks across all folders and formats them into a
        readable context string for the AI assistant.
        
        Returns:
            str: Formatted string containing all tasks organized by folder,
                including task IDs, titles, deadlines, priorities, statuses,
                and descriptions.
        """
        try:
            tasks_data = self.data_manager.load("tasks.json")
            if not tasks_data or 'folders' not in tasks_data:
                return "No tasks found."
            
            context_parts = []
            folders = tasks_data['folders']
            
            for folder_name, tasks in folders.items():
                if not tasks:
                    continue
                
                context_parts.append(f"Folder: {folder_name}")
                for task in tasks:
                    task_id = task.get('id', 'N/A')
                    title = task.get('title', 'Untitled')
                    deadline = task.get('deadline', 'No deadline')
                    priority = task.get('priority', 'medium')
                    status = task.get('status', 'pending')
                    description = task.get('description', '')
                    
                    context_parts.append(f"- [{task_id}] {title} (Due: {deadline}, Priority: {priority}, Status: {status})")
                    if description:
                        context_parts.append(f"  Description: {description}")
                context_parts.append("")  # Empty line between folders
            
            if not context_parts:
                return "No tasks found."
            
            return "\n".join(context_parts)
        except Exception as e:
            return f"Error loading tasks: {e}"

    def _load_docs_context(self):
        """Load all documents and their summaries and format for AI context.
        
        Retrieves all documents (PDFs, DOCX, TXT) with their metadata and
        summaries, formatted for AI comprehension.
        
        Returns:
            str: Formatted string containing all documents with IDs, titles,
                size information, and summaries.
        """
        try:
            docs_data = self.data_manager.load("docs_metadata.json")
            if not docs_data:
                return "No documents found."
            
            context_parts = []
            
            for doc in docs_data:
                doc_id = doc.get('id', 'N/A')
                title = doc.get('title', doc.get('filename', 'Untitled'))
                pages = doc.get('page_count', 'N/A')
                extension = doc.get('extension', 'unknown')
                summary = doc.get('summary', 'No summary available')
                
                # Format pages/word count based on document type
                if extension == '.pdf':
                    size_info = f"{pages} pages"
                elif extension in ['.docx', '.txt']:
                    word_count = doc.get('word_count', 'N/A')
                    size_info = f"{word_count} words"
                else:
                    size_info = "Unknown size"
                
                context_parts.append(f"- [{doc_id}] {title} ({size_info})")
                context_parts.append(f"  Summary: {summary}")
                context_parts.append("")  # Empty line between documents
            
            if not context_parts:
                return "No documents found."
            
            return "\n".join(context_parts)
        except Exception as e:
            return f"Error loading documents: {e}"

    def _build_context_message(self):
        """Build system message with relevant context based on context_type.
        
        Constructs the system prompt for the AI by combining base instructions
        with context data (tasks, documents, or both) depending on the active
        context mode. Includes instructions for structured task/doc suggestions.
        
        Returns:
            str: Complete system message with embedded context information.
        """
        base_message = """You are a helpful assistant for a task and knowledge management system.

When users mention tasks, projects, or work items, use your reasoning to determine their intent:

1. **Creating vs. Discussing**: Distinguish whether the user wants to CREATE a task or just DISCUSS it.
   - "I need to add a task" → User wants recommendations, NOT automatic creation
   - "Create a task for the report" → User wants a task created
   - "I should work on the report" → Ambiguous, ask for clarification
   - "I'm working on the report" → Status update, not a creation request

2. **Ambiguity Resolution**: When references are unclear, ask for details.
   - "a report" (indefinite article) → Ask what report they mean
   - "the report" (definite article) → Check chat history or context for which report

3. **Structured Task Suggestions**: When appropriate to suggest a task, use this EXACT format:
   ```
   [TASK_SUGGESTION]
   Title: <task title, max 30 chars>
   Description: <detailed description>
   Deadline: <DD-MM-YYYY or leave empty>
   Priority: <low/medium/high>
   [/TASK_SUGGESTION]
   ```

4. **Context Awareness**: Use available chat history and workspace context (tasks/docs) to resolve references.
   - Look for previously mentioned projects, reports, or work items
   - Reference existing tasks or documents when suggesting new ones

5. **Ask for Approval**: Always end suggestions with a question asking if the user wants to proceed.

Be conversational and helpful. Only suggest structured tasks when it's clearly beneficial."""
        
        if self.context_type == 'general':
            return base_message
        
        context_parts = [base_message]
        
        if self.context_type in ['tasks', 'all']:
            tasks_context = self._load_tasks_context()
            context_parts.append("\nYou have access to the user's tasks:\n")
            context_parts.append(tasks_context)
        
        if self.context_type in ['docs', 'all']:
            docs_context = self._load_docs_context()
            context_parts.append("\nYou have access to these documents:\n")
            context_parts.append(docs_context)
        
        return "\n".join(context_parts)

    def set_context(self, context_type):
        """Set the current context type and reload context data.
        
        Changes the active context mode and loads the corresponding data.
        Valid modes: general (no context), tasks (task data only),
        docs (document data only), all (both tasks and documents).
        
        Args:
            context_type: Type of context to use ('general', 'tasks', 'docs', 'all').
        
        Returns:
            bool: True if context was successfully set, False if invalid type.
        """
        valid_contexts = ['general', 'tasks', 'docs', 'all']
        if context_type not in valid_contexts:
            print(f"Error: Invalid context type. Valid options: {', '.join(valid_contexts)}")
            return False
        
        self.context_type = context_type
        self.context_data = self._build_context_message()
        return True

    def _parse_task_suggestion(self, response_text):
        """Parse a structured task suggestion from AI response.
        
        Extracts task details from [TASK_SUGGESTION] blocks in the AI's response.
        
        Args:
            response_text: The full AI response text.
        
        Returns:
            dict or None: Dictionary with 'title', 'description', 'deadline', 'priority'
                         if a valid suggestion is found, otherwise None.
        """
        import re
        
        # Look for [TASK_SUGGESTION]...[/TASK_SUGGESTION] block
        pattern = r'\[TASK_SUGGESTION\](.*?)\[/TASK_SUGGESTION\]'
        match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
        
        if not match:
            return None
        
        suggestion_block = match.group(1).strip()
        
        # Parse fields
        task_data = {
            'title': '',
            'description': '',
            'deadline': None,
            'priority': 'medium'
        }
        
        # Extract Title
        title_match = re.search(r'Title:\s*(.+?)(?:\n|$)', suggestion_block, re.IGNORECASE)
        if title_match:
            task_data['title'] = title_match.group(1).strip()
        
        # Extract Description (handle multi-line)
        desc_match = re.search(r'Description:\s*(.+?)(?=\n\s*(?:Deadline|Priority)|\Z)', suggestion_block, re.DOTALL | re.IGNORECASE)
        if desc_match:
            task_data['description'] = desc_match.group(1).strip()
        
        # Extract Deadline
        deadline_match = re.search(r'Deadline:\s*(.+?)(?=\n|$)', suggestion_block, re.IGNORECASE)
        if deadline_match:
            deadline_text = deadline_match.group(1).strip()
            # Check if it's a valid date format or empty (ignore other field names)
            if deadline_text and deadline_text.lower() not in ['none', 'empty', '', 'priority:']:
                # Make sure we didn't capture the start of next field
                if not deadline_text.lower().startswith('priority'):
                    task_data['deadline'] = deadline_text
        
        # Extract Priority
        priority_match = re.search(r'Priority:\s*(.+?)(?:\n|$)', suggestion_block, re.IGNORECASE)
        if priority_match:
            priority_text = priority_match.group(1).strip().lower()
            if priority_text in ['low', 'medium', 'high', 'l', 'm', 'h']:
                task_data['priority'] = priority_text
        
        # Validate that we at least have a title
        if not task_data['title']:
            return None
        
        return task_data

    def _handle_structured_suggestions(self, response_text):
        """Detect and handle structured task suggestions in AI response.
        
        Parses the AI response for structured task suggestions and offers
        the user the option to create them directly.
        
        Args:
            response_text: The full AI response text to parse.
        """
        # Only process if we have task_manager and correct context
        if not self.task_manager:
            return
        # Restrict to tasks/all context only
        if self.context_type not in ['tasks', 'all']:
            print("Task creation is only allowed in tasks or all context mode.")
            return

        task_suggestion = self._parse_task_suggestion(response_text)
        if not task_suggestion:
            return

        # Show the parsed suggestion
        print("\n" + "─" * 60)
        print("✨ Task Suggestion Detected:")
        print(f"   Title: {task_suggestion['title']}")
        if task_suggestion['description']:
            print(f"   Description: {task_suggestion['description']}")
        if task_suggestion['deadline']:
            print(f"   Deadline: {task_suggestion['deadline']}")
        print(f"   Priority: {task_suggestion['priority']}")
        print("─" * 60)
        
        # Ask for confirmation
        try:
            confirm = input("\nCreate this task? (yes/no): ").strip().lower()
            
            if confirm in ['yes', 'y']:
                # Create the task using TaskManager
                try:
                    task = self.task_manager.add_task(
                        title=task_suggestion['title'],
                        description=task_suggestion['description'],
                        deadline=task_suggestion['deadline'],
                        priority=task_suggestion['priority']
                    )
                    print(f"✓ Task created successfully!")
                except Exception as e:
                    print(f"✗ Failed to create task: {e}")
            else:
                print("Task creation cancelled.")
        except (EOFError, KeyboardInterrupt):
            print("\nTask creation cancelled.")

    def send_message(self, message):
        """Send a message to OpenAI and get response.
        
        Sends user message to OpenAI's GPT-4o model with conversation history
        and context. Streams the response in real-time and tracks token usage
        and costs. Saves both user message and assistant response to history.
        
        Args:
            message: User message text.
        
        Returns:
            str: Complete assistant response text, or error message if API call fails.
        """
        if not self.openai_client:
            return "Error: OpenAI client not initialized. Check your OPENAI_API_KEY."
        
        # Save user message
        self._save_message('user', message)
        
        # Get conversation history
        history = self._get_conversation_history(limit=10)
        
        # Build system message with context
        system_message = self._build_context_message()
        
        # Prepare messages for OpenAI
        messages = [
            {
                'role': 'system',
                'content': system_message
            }
        ]
        
        # Add conversation history
        for msg in history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        try:
            # Show waiting indicator
            print("...", end='', flush=True)
            
            # Send to OpenAI with streaming
            stream = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                stream=True,
                temperature=0.7
            )
            
            # Clear waiting indicator
            print("\r   \r", end='', flush=True)
            
            # Collect and display response
            full_response = ""
            chunk_count = 0
            usage_tracked = False
            
            for chunk in stream:
                # Track usage from the last chunk which contains total usage
                if hasattr(chunk, 'usage') and chunk.usage:
                    # Track with cost tracker
                    if self.cost_tracker:
                        self.cost_tracker.track_api_call(
                            operation_type='chat_message',
                            model="gpt-4o",
                            input_tokens=chunk.usage.prompt_tokens,
                            output_tokens=chunk.usage.completion_tokens
                        )
                        usage_tracked = True
                
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end='', flush=True)
                    full_response += content
                    chunk_count += 1
            
            # If streaming didn't provide usage, estimate it
            if chunk_count > 0 and self.cost_tracker and not usage_tracked:
                # Rough estimation: 4 chars per token
                estimated_input = len(system_message + message) // 4
                estimated_output = len(full_response) // 4
                self.cost_tracker.track_api_call(
                    operation_type='chat_message',
                    model="gpt-4o",
                    input_tokens=estimated_input,
                    output_tokens=estimated_output
                )
                print(f"\n⚠️  Usage data not exact. Estimated {estimated_input:,} input and {estimated_output:,} output tokens.")
            
            print()  # New line after response
            
            # Save assistant response
            self._save_message('assistant', full_response)
            
            # Check for structured suggestions and offer to create them
            self._handle_structured_suggestions(full_response)
            
            return full_response
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\r{error_msg}")
            
            # Track estimated cost even on error if we sent a message
            if self.cost_tracker and message:
                estimated_input = len(system_message + message) // 4
                estimated_output = 10  # Minimal for error response
                self.cost_tracker.track_api_call(
                    operation_type='chat_message',
                    model="gpt-4o",
                    input_tokens=estimated_input,
                    output_tokens=estimated_output
                )
            
            return error_msg

    def _show_chat_help(self):
        """Display chat mode help.
        
        Shows available chat commands and their descriptions.
        """
        print("\nChat Mode Commands:")
        print("  /home            - Return to main menu")
        print("  /clear           - Clear conversation history")
        print("  /context <type>  - Switch context (general, tasks, docs, all)")
        print("  /refresh         - Reload context data")
        print("  /cost            - Show API usage and costs for this session")
        print("  /analyze         - Analyze tasks with AI insights")
        print("  /synthesize      - Synthesize knowledge about a topic")
        print("  /connections     - Show connections between documents and tasks")
        print("  /help            - Show this help")
        print()

    def _chat_loop(self):
        """Inner loop for chat mode.
        
        Main interactive loop that handles user input, processes chat commands
        (starting with /), and sends messages to OpenAI. Continues until
        user exits or interrupts.
        """
        while True:
            try:
                # Dynamic prompt based on context with rainbow color
                if hasattr(self, 'color_theme') and self.color_theme:
                    prompt = self.color_theme.chat_prompt(self.context_type)
                else:
                    prompt = f"chat[{self.context_type}]> "
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.startswith('/'):
                    command_parts = user_input.split(maxsplit=1)
                    command = command_parts[0].lower()
                    args = command_parts[1] if len(command_parts) > 1 else None
                    
                    if command == '/home':
                        break
                    elif command == '/clear':
                        if self._clear_conversation():
                            if hasattr(self, 'color_theme') and self.color_theme:
                                print(self.color_theme.success("Conversation history cleared."))
                            else:
                                print("✓ Conversation history cleared.")
                        else:
                            if hasattr(self, 'color_theme') and self.color_theme:
                                print(self.color_theme.info("No conversation to clear."))
                            else:
                                print("No conversation to clear.")
                    elif command == '/context':
                        if args:
                            if hasattr(self, 'color_theme') and self.color_theme:
                                print(self.color_theme.info(f"Switching to {args} context..."))
                            else:
                                print(f"Switching to {args} context...")
                            if self.set_context(args):
                                if hasattr(self, 'color_theme') and self.color_theme:
                                    print(self.color_theme.success(f"Context updated. I now have access to your {args} data."))
                                else:
                                    print(f"✓ Context updated. I now have access to your {args} data.")
                        else:
                            if hasattr(self, 'color_theme') and self.color_theme:
                                print(self.color_theme.warning("Usage: /context <type>"))
                                print(self.color_theme.info("Valid types: general, tasks, docs, all"))
                            else:
                                print("Usage: /context <type>")
                                print("Valid types: general, tasks, docs, all")
                    elif command == '/refresh':
                        if hasattr(self, 'color_theme') and self.color_theme:
                            print(self.color_theme.info("Reloading context data..."))
                        else:
                            print("Reloading context data...")
                        self.context_data = self._build_context_message()
                        if hasattr(self, 'color_theme') and self.color_theme:
                            print(self.color_theme.success("Context data refreshed."))
                        else:
                            print("✓ Context data refreshed.")
                    elif command == '/cost':
                        if self.cost_tracker:
                            summary = self.cost_tracker.get_session_summary()
                            print(f"\n💰 Session API Usage:")
                            print(f"   Total cost:    ${summary['total_cost']:.4f}")
                            print(f"   Input tokens:  {summary['total_input_tokens']:,}")
                            print(f"   Output tokens: {summary['total_output_tokens']:,}")
                            if summary['by_operation']:
                                print(f"\n   By operation:")
                                for op_type, data in summary['by_operation'].items():
                                    print(f"     • {op_type.replace('_', ' ').title()}: ${data['cost']:.4f} ({data['count']} calls)")
                            print()
                        else:
                            print("\n⚠️  Cost tracking not available.\n")
                    elif command == '/analyze':
                        if self.agent_manager:
                            folder_arg = args.split()[1] if args and '--folder' in args else None
                            self.agent_manager.analyze_tasks(folder_arg)
                        else:
                            print("Agent features not available.")
                    elif command == '/synthesize':
                        if self.agent_manager:
                            if args:
                                self.agent_manager.synthesize_topic(args)
                            else:
                                print("Usage: /synthesize <topic>")
                                print("Example: /synthesize machine learning")
                        else:
                            print("Agent features not available.")
                    elif command == '/connections':
                        if self.agent_manager:
                            self.agent_manager.show_connections()
                        else:
                            print("Agent features not available.")
                    elif command == '/help':
                        self._show_chat_help()
                    else:
                        print(f"Unknown command: {user_input}")
                        print("Type '/help' for available commands.")
                else:
                    # Send message to OpenAI
                    self.send_message(user_input)
                    print()  # Extra line for readability
                    
            except KeyboardInterrupt:
                print()
                break
            except EOFError:
                print()
                break

    def start_chat(self, context_type='general'):
        """Enter interactive chat mode.
        
        Initiates an interactive chat session with the specified context mode.
        Shows session summary with cost information upon exit.
        
        Args:
            context_type: Type of context to use ('general', 'tasks', 'docs', 'all').
                Defaults to 'general'.
        """
        if not self.openai_client:
            print("Error: Chat mode requires OpenAI API key.")
            print("Please set OPENAI_API_KEY environment variable.")
            return
        
        # Set context
        if context_type != 'general':
            print(f"Loading {context_type} context...")
        
        self.set_context(context_type)
        
        # Show chat commands
        if hasattr(self, 'color_theme') and self.color_theme:
            print("\n" + self.color_theme.chat_separator())
            print(self.color_theme.chat_header("Chat Mode - Available Commands"))
            print(self.color_theme.chat_separator())
        else:
            print("\n" + "=" * 60)
            print("Chat Mode - Available Commands")
            print("=" * 60)
        
        print("\n💬 Chat Commands:")
        print("  /home            - Return to main menu")
        print("  /clear           - Clear conversation history")
        print("  /context <type>  - Switch context (general, tasks, docs, all)")
        print("  /refresh         - Reload context data")
        print("  /cost            - Show API usage and costs")
        print("  /analyze         - Analyze tasks with AI insights")
        print("  /synthesize      - Synthesize knowledge about a topic")
        print("  /connections     - Show connections between documents and tasks")
        print("  /help            - Show this help")
        print("\nType your message to chat with AI, or use slash commands above.")
        
        if hasattr(self, 'color_theme') and self.color_theme:
            print(self.color_theme.chat_separator() + "\n")
        else:
            print("=" * 60 + "\n")
        
        # Run chat loop
        self._chat_loop()
        
        if hasattr(self, 'color_theme') and self.color_theme:
            print(self.color_theme.info("Exiting chat mode."))
        else:
            print("Exiting chat mode.")
        
        # Show session summary if any API calls were made
        if self.cost_tracker:
            summary = self.cost_tracker.get_session_summary()
            chat_data = summary.get('by_operation', {}).get('chat_message', {})
            if chat_data and chat_data.get('cost', 0) > 0:
                print(f"\n💰 Chat Session: ${chat_data['cost']:.4f} ({chat_data['input_tokens']:,} input, {chat_data['output_tokens']:,} output tokens)")

    def _register_commands(self):
        """Register chat-related commands.
        
        Registers the chat command with the command registry.
        """
        self.registry.register_command('chat', self.cmd_chat, 'Enter interactive chat mode', 'global')

    def cmd_chat(self, *args):
        """Command to enter chat mode.
        
        Starts an interactive chat session in general context mode.
        Use /context command within chat to switch contexts.
        
        Args:
            *args: Command arguments (currently unused).
        """
        # Always start with general context
        # Users can switch context using /context command in chat mode
        self.start_chat('general')
