"""
Custom exceptions for PKMS application.

Provides specific exception types for different error scenarios,
enabling better error handling and user-friendly error messages.
"""

class PKMSError(Exception):
    """Base exception for all PKMS errors."""
    pass


class TaskNotFoundError(PKMSError):
    """Raised when a task ID cannot be found."""
    
    def __init__(self, task_id, available_ids=None):
        self.task_id = task_id
        self.available_ids = available_ids or []
        
        if available_ids:
            msg = f"Task not found: {task_id}\nAvailable task IDs: {', '.join(map(str, available_ids[:10]))}"
            if len(available_ids) > 10:
                msg += f" (and {len(available_ids) - 10} more)"
        else:
            msg = f"Task not found: {task_id}\nNo tasks available. Use 'add' to create a task."
        
        super().__init__(msg)


class PDFNotFoundError(PKMSError):
    """Raised when a PDF/document ID cannot be found."""
    
    def __init__(self, doc_id, available_ids=None):
        self.doc_id = doc_id
        self.available_ids = available_ids or []
        
        if available_ids:
            msg = f"Document not found: {doc_id}\nAvailable document IDs: {', '.join(map(str, available_ids[:10]))}"
            if len(available_ids) > 10:
                msg += f" (and {len(available_ids) - 10} more)"
        else:
            msg = f"Document not found: {doc_id}\nNo documents available. Use 'docs-add' to add a document."
        
        super().__init__(msg)


class InvalidInputError(PKMSError):
    """Raised when user input is invalid."""
    
    def __init__(self, message, field=None, valid_values=None):
        self.field = field
        self.valid_values = valid_values
        
        if field and valid_values:
            msg = f"Invalid {field}: {message}\nValid values: {', '.join(map(str, valid_values))}"
        elif field:
            msg = f"Invalid {field}: {message}"
        else:
            msg = message
        
        super().__init__(msg)


class APIError(PKMSError):
    """Raised when OpenAI API calls fail."""
    
    def __init__(self, message, error_type=None, suggestion=None):
        self.error_type = error_type
        self.suggestion = suggestion
        
        msg = f"API Error: {message}"
        
        if error_type == "authentication":
            msg += "\n💡 Check your API key in settings: settings > show"
        elif error_type == "rate_limit":
            msg += "\n💡 You've hit the rate limit. Wait a moment and try again."
        elif error_type == "quota":
            msg += "\n💡 API quota exceeded. Check your OpenAI account billing."
        elif error_type == "network":
            msg += "\n💡 Network error. Check your internet connection."
        elif suggestion:
            msg += f"\n💡 {suggestion}"
        
        super().__init__(msg)


class StorageError(PKMSError):
    """Raised when file system operations fail."""
    
    def __init__(self, message, filepath=None, operation=None):
        self.filepath = filepath
        self.operation = operation
        
        if filepath and operation:
            msg = f"Storage Error ({operation}): {message}\nFile: {filepath}"
        elif operation:
            msg = f"Storage Error ({operation}): {message}"
        else:
            msg = f"Storage Error: {message}"
        
        super().__init__(msg)


class ValidationError(PKMSError):
    """Raised when data validation fails."""
    
    def __init__(self, message, field=None, expected_format=None):
        self.field = field
        self.expected_format = expected_format
        
        if field and expected_format:
            msg = f"Validation Error ({field}): {message}\nExpected format: {expected_format}"
        elif field:
            msg = f"Validation Error ({field}): {message}"
        else:
            msg = f"Validation Error: {message}"
        
        super().__init__(msg)
