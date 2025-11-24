import os
import uuid
import textwrap
from datetime import datetime
from openai import OpenAI


class ChatManager:
    def __init__(self, data_manager, registry):
        """
        Initialize ChatManager with dependencies.
        :param data_manager: Handles data storage and retrieval.
        :param registry: Command registry for registering commands.
        """
        self.data_manager = data_manager
        self.registry = registry
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
        """Initialize OpenAI client with API key from environment."""
        try:
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                print("Warning: OPENAI_API_KEY not found. Chat functionality will be disabled.")
        except Exception as e:
            print(f"Warning: Failed to initialize OpenAI client: {e}")

    def _load_conversations(self):
        """Load conversation history from storage."""
        data = self.data_manager.load("chat_history.json")
        if data and 'conversations' in data:
            self.conversations = data['conversations']
        else:
            self.conversations = []

    def _save_conversations(self):
        """Save conversation history to storage."""
        data = {'conversations': self.conversations}
        self.data_manager.save("chat_history.json", data)

    def _get_current_conversation(self):
        """Get or create current conversation."""
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
        """
        Get last N messages from current conversation.
        :param limit: Maximum number of messages to retrieve
        :return: List of messages
        """
        conversation = self._get_current_conversation()
        messages = conversation['messages']
        
        # Return last N messages
        if len(messages) <= limit:
            return messages
        else:
            return messages[-limit:]

    def _save_message(self, role, content):
        """
        Save a message to the current conversation.
        :param role: Message role (user/assistant)
        :param content: Message content
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
        """Clear the current conversation history."""
        if self.current_conversation_id:
            for conv in self.conversations:
                if conv['id'] == self.current_conversation_id:
                    conv['messages'] = []
                    self._save_conversations()
                    return True
        return False

    def _format_response(self, text, width=80):
        """
        Format response text with word wrapping.
        :param text: Text to format
        :param width: Maximum line width
        :return: Formatted text
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
        """
        Load all tasks from all folders and format for AI context.
        :return: Formatted task context string
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
        """
        Load all PDFs and their summaries and format for AI context.
        :return: Formatted PDF context string
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
        """
        Build system message with relevant context based on context_type.
        :return: System message with context
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
        """
        Set the current context type and reload context data.
        :param context_type: Type of context ('general', 'tasks', 'pdfs', 'all')
        :return: Success status
        """
        valid_contexts = ['general', 'tasks', 'pdfs', 'all']
        if context_type not in valid_contexts:
            print(f"Error: Invalid context type. Valid options: {', '.join(valid_contexts)}")
            return False
        
        self.context_type = context_type
        self.context_data = self._build_context_message()
        return True

    def send_message(self, message):
        """
        Send a message to OpenAI and get response.
        :param message: User message
        :return: Assistant response
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
        """Display chat mode help."""
        print("\nChat Mode Commands:")
        print("  /exit, /quit     - Return to main menu")
        print("  /clear           - Clear conversation history")
        print("  /context <type>  - Switch context (general, tasks, pdfs, all)")
        print("  /refresh         - Reload context data")
        print("  /cost            - Show API usage and costs for this session")
        print("  /help            - Show this help")
        print()

    def _chat_loop(self):
        """Inner loop for chat mode."""
        while True:
            try:
                # Dynamic prompt based on context
                prompt = f"chat[{self.context_type}]> "
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.startswith('/'):
                    command_parts = user_input.lower().split(maxsplit=1)
                    command = command_parts[0]
                    args = command_parts[1] if len(command_parts) > 1 else None
                    
                    if command in ['/exit', '/quit']:
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
        """
        Enter interactive chat mode.
        :param context_type: Type of context to use
        """
        if not self.openai_client:
            print("Error: Chat mode requires OpenAI API key.")
            print("Please set OPENAI_API_KEY environment variable.")
            return
        
        # Set context
        if context_type != 'general':
            print(f"Loading {context_type} context...")
        
        self.set_context(context_type)
        
        if context_type == 'general':
            print("Entering chat mode. Type '/exit' to leave, '/help' for commands.\n")
        else:
            print(f"Entering chat mode with {context_type} context.\n")
        
        # Run chat loop
        self._chat_loop()
        
        print("Exiting chat mode.")
        
        # Show session summary if any API calls were made
        if self.session_cost > 0:
            print(f"\n💰 Session Summary: ${self.session_cost:.4f} ({self.session_input_tokens:,} input, {self.session_output_tokens:,} output tokens)")

    def _register_commands(self):
        """Register chat-related commands."""
        self.registry.register_command('chat', self.cmd_chat, 'Enter interactive chat mode', 'chat')

    def cmd_chat(self, *args):
        """
        Command to enter chat mode.
        Accepts --context flag to specify context type.
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
