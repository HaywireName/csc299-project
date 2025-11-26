"""Cost tracking module for OpenAI API usage.

This module provides comprehensive tracking of OpenAI API costs across sessions,
storing session history and calculating costs based on token usage and model pricing.
"""

import json
import os
from datetime import datetime
from pathlib import Path


class CostTracker:
    """Track OpenAI API costs across sessions.
    
    Monitors API usage by operation type, calculates costs based on token
    consumption and model pricing, and maintains persistent session history.
    
    Attributes:
        data_dir: Path to data directory for cost history storage.
        cost_file: Path to cost_history.json file.
        history: Dictionary containing all session history.
        current_session: Dictionary tracking current session costs.
        PRICING: Model pricing table (cost per 1M tokens).
    """
    
    # Pricing in USD per 1 million tokens
    PRICING = {
        'gpt-4o': {'input': 2.50, 'output': 10.00},
        'gpt-4o-mini': {'input': 0.150, 'output': 0.600},
        'gpt-4-turbo': {'input': 10.00, 'output': 30.00},
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
    }
    
    def __init__(self, data_dir):
        """Initialize CostTracker with data directory.
        
        Args:
            data_dir: Path to data directory (string or Path object).
        """
        self.data_dir = Path(data_dir)
        self.cost_file = self.data_dir / 'cost_history.json'
        self.history = self._load_cost_history()
        self.current_session = {
            'total_cost': 0.0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'by_operation': {}
        }
    
    def _load_cost_history(self):
        """Load cost history from file, create if doesn't exist.
        
        Returns:
            dict: Cost history with sessions list and all-time total.
        """
        if not self.cost_file.exists():
            # First time - create empty history
            history = {
                "sessions": [],
                "total_all_time": 0.0
            }
            self._save_history(history)
            return history
        
        try:
            with open(self.cost_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load cost history: {e}")
            return {"sessions": [], "total_all_time": 0.0}
    
    def _save_history(self, history=None):
        """Save cost history to file.
        
        Args:
            history: History dict to save. Uses self.history if None.
        """
        if history is None:
            history = self.history
        
        try:
            with open(self.cost_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save cost history: {e}")
    
    def _get_model_pricing(self, model):
        """Get pricing for model, use default if unknown.
        
        Args:
            model: Model name (e.g., 'gpt-4o-mini').
        
        Returns:
            dict: Pricing dict with 'input' and 'output' keys.
        """
        if model in self.PRICING:
            return self.PRICING[model]
        else:
            # Use gpt-4o-mini pricing as conservative default
            print(f"  (Warning: Unknown model '{model}', using default pricing)")
            return self.PRICING['gpt-4o-mini']
    
    def track_api_call(self, operation_type, model, input_tokens, output_tokens):
        """Track a single API call and calculate its cost.
        
        Args:
            operation_type: Type of operation (e.g., 'task_summary', 'chat_message').
            model: Model name used (e.g., 'gpt-4o-mini').
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.
        
        Returns:
            float: Cost of this call in USD.
        """
        # Get pricing for this model
        pricing = self._get_model_pricing(model)
        
        # Calculate cost (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * pricing['input']
        output_cost = (output_tokens / 1_000_000) * pricing['output']
        total_cost = input_cost + output_cost
        
        # Update session totals
        self.current_session['total_cost'] += total_cost
        self.current_session['total_input_tokens'] += input_tokens
        self.current_session['total_output_tokens'] += output_tokens
        
        # Update operation type tracking
        if operation_type not in self.current_session['by_operation']:
            self.current_session['by_operation'][operation_type] = {
                'count': 0,
                'cost': 0.0,
                'input_tokens': 0,
                'output_tokens': 0
            }
        
        op_data = self.current_session['by_operation'][operation_type]
        op_data['count'] += 1
        op_data['cost'] += total_cost
        op_data['input_tokens'] += input_tokens
        op_data['output_tokens'] += output_tokens
        
        return total_cost
    
    def get_session_summary(self):
        """Get current session cost breakdown.
        
        Returns:
            dict: Session summary with total_cost and by_operation breakdown.
        """
        return {
            'total_cost': self.current_session['total_cost'],
            'total_input_tokens': self.current_session['total_input_tokens'],
            'total_output_tokens': self.current_session['total_output_tokens'],
            'by_operation': dict(self.current_session['by_operation'])
        }
    
    def save_session(self):
        """Save current session to cost_history.json and reset current session.
        
        Appends current session to history with timestamp and updates all-time total.
        """
        # Only save if there were API calls
        if self.current_session['total_cost'] > 0:
            session_record = {
                'timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'total_cost': self.current_session['total_cost'],
                'total_input_tokens': self.current_session['total_input_tokens'],
                'total_output_tokens': self.current_session['total_output_tokens'],
                'operations': self.current_session['by_operation']
            }
            
            # Add to history
            self.history['sessions'].append(session_record)
            self.history['total_all_time'] += self.current_session['total_cost']
            
            # Save to file
            self._save_history()
        
        # Reset current session
        self.current_session = {
            'total_cost': 0.0,
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'by_operation': {}
        }
    
    def get_previous_session_cost(self):
        """Get the most recent previous session's total cost.
        
        Returns:
            float: Previous session cost, or 0.0 if no history.
        """
        if self.history['sessions']:
            return self.history['sessions'][-1]['total_cost']
        return 0.0
    
    def get_all_time_cost(self):
        """Calculate total cost across all sessions.
        
        Returns:
            float: Total cost since tracking began.
        """
        # Include current session in all-time total
        return self.history['total_all_time'] + self.current_session['total_cost']
    
    def get_session_count(self):
        """Get total number of sessions tracked.
        
        Returns:
            int: Number of sessions in history.
        """
        return len(self.history['sessions'])


def track_api_call_safe(cost_tracker, operation_type, model, response):
    """Safely track API call, handling missing usage data.
    
    Wrapper function for safe cost tracking that handles errors gracefully.
    
    Args:
        cost_tracker: CostTracker instance.
        operation_type: Type of operation (e.g., 'task_summary').
        model: Model name used.
        response: OpenAI API response object.
    
    Returns:
        float: Cost of the call, or 0.0 if tracking failed.
    """
    try:
        if cost_tracker and hasattr(response, 'usage') and response.usage:
            return cost_tracker.track_api_call(
                operation_type=operation_type,
                model=model,
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens
            )
        elif cost_tracker:
            print("  (Warning: Could not track API cost - no usage data)")
        return 0.0
    except Exception as e:
        print(f"  (Warning: Cost tracking error: {e})")
        return 0.0
