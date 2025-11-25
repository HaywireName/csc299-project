import os
import uuid
import textwrap
from datetime import datetime
from openai import OpenAI


class ChatManager:
    """Manages interactive chat sessions with OpenAI GPT models.
    
    The ChatManager provides an interactive chat interface with context-aware
    conversations. Supports multiple context modes (general, tasks, pdfs, all)
    to provide the AI with relevant information from the user's workspace.
    Features conversation history, streaming responses, and cost tracking.
    
    Attributes:
        data_manager: Data persistence manager for chat history.
        registry: Command registry for registering chat commands.
        openai_client: OpenAI API client instance.
        current_conversation_id: ID of the active conversation.
        conversations: List of all conversation histories.
        context_type: Current context mode (general/tasks/pdfs/all).
        context_data: Loaded context data for the AI.
        session_cost: Cumulative API cost for the session.
        session_input_tokens: Total input tokens used in session.
        session_output_tokens: Total output tokens used in session.
    """
    
    def __init__(self, data_manager, registry, agent_manager=None):
        """Initialize ChatManager with dependencies.
        
        Loads conversation history, initializes OpenAI client, and registers
        chat commands.
        
        Args:
            data_manager: Data persistence manager instance.
            registry: Command registry instance for registering commands.
            agent_manager: AgentManager instance for agent commands (optional).
        """
        self.data_manager = data_manager
        self.registry = registry
        self.agent_manager = agent_manager
        self.openai_client = None
        self.current_conversation_id = None
        self.conversations = []
        self.context_type = 'general'
        self.context_data = None
        self.session_cost = 0.0
        self.session_input_tokens = 0
        self.session_output_tokens = 0
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

    def _load_pdfs_context(self):
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
        context mode.
        
        Returns:
            str: Complete system message with embedded context information.
        """
        base_message = "You are a helpful assistant for a task and knowledge management system."
        
        if self.context_type == 'general':
            return base_message
        
        context_parts = [base_message]
        
        if self.context_type in ['tasks', 'all']:
            tasks_context = self._load_tasks_context()
            context_parts.append("\nYou have access to the user's tasks:\n")
            context_parts.append(tasks_context)
        
        if self.context_type in ['pdfs', 'all']:
            pdfs_context = self._load_pdfs_context()
            context_parts.append("\nYou have access to these documents:\n")
            context_parts.append(pdfs_context)
        
        return "\n".join(context_parts)

    def set_context(self, context_type):
        """Set the current context type and reload context data.
        
        Changes the active context mode and loads the corresponding data.
        Valid modes: general (no context), tasks (task data only),
        pdfs (document data only), all (both tasks and documents).
        
        Args:
            context_type: Type of context to use ('general', 'tasks', 'pdfs', 'all').
        
        Returns:
            bool: True if context was successfully set, False if invalid type.
        """
        valid_contexts = ['general', 'tasks', 'pdfs', 'all']
        if context_type not in valid_contexts:
            print(f"Error: Invalid context type. Valid options: {', '.join(valid_contexts)}")
            return False
        
        self.context_type = context_type
        self.context_data = self._build_context_message()
        return True

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
            
            for chunk in stream:
                # Track usage from the last chunk which contains total usage
                if hasattr(chunk, 'usage') and chunk.usage:
                    self.session_input_tokens += chunk.usage.prompt_tokens
                    self.session_output_tokens += chunk.usage.completion_tokens
                    # Calculate cost: gpt-4o pricing
                    # Input: $2.50 per 1M tokens, Output: $10.00 per 1M tokens
                    input_cost = (chunk.usage.prompt_tokens / 1_000_000) * 2.50
                    output_cost = (chunk.usage.completion_tokens / 1_000_000) * 10.00
                    self.session_cost += input_cost + output_cost
                
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    print(content, end='', flush=True)
                    full_response += content
                    chunk_count += 1
            
            # If streaming didn't provide usage, estimate it
            if chunk_count > 0 and self.session_input_tokens == 0:
                # Rough estimation: 4 chars per token
                estimated_input = len(system_message + message) // 4
                estimated_output = len(full_response) // 4
                self.session_input_tokens += estimated_input
                self.session_output_tokens += estimated_output
                input_cost = (estimated_input / 1_000_000) * 2.50
                output_cost = (estimated_output / 1_000_000) * 10.00
                self.session_cost += input_cost + output_cost
            
            print()  # New line after response
            
            # Save assistant response
            self._save_message('assistant', full_response)
            
            return full_response
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"\r{error_msg}")
            return error_msg

    def _show_chat_help(self):
        """Display chat mode help.
        
        Shows available chat commands and their descriptions.
        """
        print("\nChat Mode Commands:")
        print("  /home            - Return to main menu")
        print("  /clear           - Clear conversation history")
        print("  /context <type>  - Switch context (general, tasks, pdfs, all)")
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
                # Dynamic prompt based on context
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
                            print("✓ Conversation history cleared.")
                        else:
                            print("No conversation to clear.")
                    elif command == '/context':
                        if args:
                            print(f"Switching to {args} context...")
                            if self.set_context(args):
                                print(f"✓ Context updated. I now have access to your {args} data.")
                        else:
                            print("Usage: /context <type>")
                            print("Valid types: general, tasks, pdfs, all")
                    elif command == '/refresh':
                        print("Reloading context data...")
                        self.context_data = self._build_context_message()
                        print("✓ Context data refreshed.")
                    elif command == '/cost':
                        print(f"\n💰 Session API Usage:")
                        print(f"   Input tokens:  {self.session_input_tokens:,}")
                        print(f"   Output tokens: {self.session_output_tokens:,}")
                        print(f"   Total cost:    ${self.session_cost:.4f}")
                        print()
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
            context_type: Type of context to use ('general', 'tasks', 'pdfs', 'all').
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
        print("\n" + "=" * 60)
        print("Chat Mode - Available Commands")
        print("=" * 60)
        print("\n💬 Chat Commands:")
        print("  /home            - Return to main menu")
        print("  /clear           - Clear conversation history")
        print("  /context <type>  - Switch context (general, tasks, pdfs, all)")
        print("  /refresh         - Reload context data")
        print("  /cost            - Show API usage and costs")
        print("  /analyze         - Analyze tasks with AI insights")
        print("  /synthesize      - Synthesize knowledge about a topic")
        print("  /connections     - Show connections between documents and tasks")
        print("  /help            - Show this help")
        print("\nType your message to chat with AI, or use slash commands above.")
        print("=" * 60 + "\n")
        
        # Run chat loop
        self._chat_loop()
        
        print("Exiting chat mode.")
        
        # Show session summary if any API calls were made
        if self.session_cost > 0:
            print(f"\n💰 Session Summary: ${self.session_cost:.4f} ({self.session_input_tokens:,} input, {self.session_output_tokens:,} output tokens)")

    def _register_commands(self):
        """Register chat-related commands.
        
        Registers the chat command with the command registry.
        """
        self.registry.register_command('chat', self.cmd_chat, 'Enter interactive chat mode', 'global')

    def cmd_chat(self, *args):
        """Command to enter chat mode.
        
        Starts an interactive chat session. Supports --context flag to
        specify the context mode.
        
        Args:
            *args: Command arguments. Use '--context <type>' to specify
                context mode (general/tasks/pdfs/all).
        """
        context_type = 'general'
        
        # Parse arguments for --context flag
        args_list = list(args)
        if '--context' in args_list:
            try:
                context_index = args_list.index('--context')
                if context_index + 1 < len(args_list):
                    context_type = args_list[context_index + 1]
                    if context_type not in ['general', 'tasks', 'pdfs', 'all']:
                        print(f"Error: Invalid context type '{context_type}'")
                        print("Valid options: general, tasks, pdfs, all")
                        return
                else:
                    print("Error: --context flag requires a value")
                    print("Valid options: general, tasks, pdfs, all")
                    return
            except ValueError:
                pass
        
        self.start_chat(context_type)
