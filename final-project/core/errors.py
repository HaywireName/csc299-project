"""
Custom exceptions for PKMS application.

Provides specific exception types for different error scenarios,
enabling better error handling and user-friendly error messages.
"""

class PKMSError(Exception):
    """Base exception for all PKMS errors.
    
    All custom PKMS exceptions inherit from this base class, allowing
    for catch-all exception handling of application-specific errors.
    """
    pass


class TaskNotFoundError(PKMSError):
    """Raised when a task ID cannot be found.
    
    Provides helpful error messages including available task IDs to guide
    the user toward valid options.
    
    Attributes:
        task_id: The task ID that was not found.
        available_ids: List of valid task IDs that exist.
    """
    
    def __init__(self, task_id, available_ids=None):
        """Initialize TaskNotFoundError.
        
        Args:
            task_id (str or int): The task ID that was not found.
            available_ids (list, optional): List of valid task IDs. Defaults to None.
        """
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
    """Raised when a PDF/document ID cannot be found.
    
    Provides helpful error messages including available document IDs to guide
    the user toward valid options.
    
    Attributes:
        doc_id: The document ID that was not found.
        available_ids: List of valid document IDs that exist.
    """
    
    def __init__(self, doc_id, available_ids=None):
        """Initialize PDFNotFoundError.
        
        Args:
            doc_id (str or int): The document ID that was not found.
            available_ids (list, optional): List of valid document IDs. Defaults to None.
        """
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
    """Raised when user input is invalid.
    
    Provides context about what input was invalid and optionally lists
    valid values to help the user correct their input.
    
    Attributes:
        field: The name of the field that had invalid input.
        valid_values: List of acceptable values for the field.
    """
    
    def __init__(self, message, field=None, valid_values=None):
        """Initialize InvalidInputError.
        
        Args:
            message (str): Description of why the input is invalid.
            field (str, optional): Name of the field with invalid input. Defaults to None.
            valid_values (list, optional): List of valid values for the field. Defaults to None.
        """
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
    """Raised when OpenAI API calls fail.
    
    Provides categorized API errors with helpful suggestions for resolution.
    Includes specific guidance for authentication, rate limiting, quota, and
    network issues.
    
    Attributes:
        error_type: Category of API error (authentication, rate_limit, quota, network).
        suggestion: Custom suggestion for resolving the error.
    """
    
    def __init__(self, message, error_type=None, suggestion=None):
        """Initialize APIError.
        
        Args:
            message (str): Description of the API error.
            error_type (str, optional): Type of error - one of 'authentication',
                'rate_limit', 'quota', 'network'. Defaults to None.
            suggestion (str, optional): Custom suggestion for resolution. Defaults to None.
        """
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
    """Raised when file system operations fail.
    
    Provides detailed information about storage/file system failures including
    the file path and operation that failed.
    
    Attributes:
        filepath: Path to the file involved in the failed operation.
        operation: Type of operation that failed (e.g., 'read', 'write', 'backup').
    """
    
    def __init__(self, message, filepath=None, operation=None):
        """Initialize StorageError.
        
        Args:
            message (str): Description of the storage error.
            filepath (str, optional): Path to the file involved. Defaults to None.
            operation (str, optional): Name of the failed operation. Defaults to None.
        """
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
    """Raised when data validation fails.
    
    Indicates that data doesn't meet expected format or validation rules.
    Provides information about the field and expected format to help debugging.
    
    Attributes:
        field: Name of the field that failed validation.
        expected_format: Description of the expected data format.
    """
    
    def __init__(self, message, field=None, expected_format=None):
        """Initialize ValidationError.
        
        Args:
            message (str): Description of the validation failure.
            field (str, optional): Name of the field that failed. Defaults to None.
            expected_format (str, optional): Description of expected format. Defaults to None.
        """
        self.field = field
        self.expected_format = expected_format
        
        if field and expected_format:
            msg = f"Validation Error ({field}): {message}\nExpected format: {expected_format}"
        elif field:
            msg = f"Validation Error ({field}): {message}"
        else:
            msg = f"Validation Error: {message}"
        
        super().__init__(msg)
