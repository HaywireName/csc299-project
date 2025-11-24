#!/usr/bin/env python3
"""Test script to verify deadline parsing functionality"""

from datetime import datetime, timedelta

def parse_deadline(deadline_str):
    """
    Parse deadline from various formats and return DD-MM-YYYY format.
    Supports: MM-DD-YYYY, YYYY-DD-MM, MM/DD, MM-YY, MM/DD/YYYY, YYYY/DD/MM, and 'tomorrow'
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

# Test cases
test_dates = [
    "12-25-2025",      # MM-DD-YYYY
    "2025-25-12",      # YYYY-DD-MM
    "12/25/2025",      # MM/DD/YYYY
    "12/25",           # MM/DD (current year)
    "12-25",           # MM-DD (current year)
    "12-25",           # MM-YY
    "tomorrow",        # tomorrow
]

print("Testing deadline parsing:\n")
for test_date in test_dates:
    try:
        result = parse_deadline(test_date)
        print(f"✓ '{test_date}' -> {result}")
    except ValueError as e:
        print(f"✗ '{test_date}' -> Error: {e}")

print("\n" + "="*50)
print("Testing description truncation:\n")

# Test description truncation
descriptions = [
    "This is a short description",
    "This is a much longer description that should be truncated at fifteen words so we can test the functionality properly here",
    "",
]

for desc in descriptions:
    desc_words = desc.split()
    if len(desc_words) > 15:
        truncated_desc = ' '.join(desc_words[:15]) + '...'
    else:
        truncated_desc = ' '.join(desc_words) if desc_words else '-'
    
    print(f"Original ({len(desc_words)} words): {desc}")
    print(f"Truncated: {truncated_desc}\n")
