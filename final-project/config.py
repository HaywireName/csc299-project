import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PDFS_DIR = DATA_DIR / "pdfs"

# Create directories
DATA_DIR.mkdir(parents=True, exist_ok=True)
PDFS_DIR.mkdir(parents=True, exist_ok=True)

def get_api_key():
    """
    Get OpenAI API key from system environment variable.
    Returns: API key string or None if not found
    """
    return os.environ.get('OPENAI_API_KEY')

def check_api_key():
    """
    Check if API key is properly configured.
    Returns: True if valid, False otherwise (also prints instructions)
    """
    api_key = get_api_key()

    if not api_key:
        print("\n" + "="*60)
        print("❌ OpenAI API Key Not Found")
        print("="*60)
        print("\nThis program requires an OpenAI API key set as an")
        print("environment variable named: OPENAI_API_KEY")
        print("\n📖 For setup instructions, see: setup_instructions.txt")
        print("\nQuick setup:")
        print("\n  macOS/Linux:")
        print("    export OPENAI_API_KEY='sk-your-key-here'")
        print("\n  Windows (PowerShell):")
        print("    $env:OPENAI_API_KEY=\"sk-your-key-here\"")
        print("\n  Windows (Command Prompt):")
        print("    set OPENAI_API_KEY=sk-your-key-here")
        print("\nThen restart this program.")
        print("="*60 + "\n")
        return False

    # Validate format
    if not api_key.startswith('sk-'):
        print("\n" + "="*60)
        print("⚠️  Warning: API Key Format Issue")
        print("="*60)
        print("\nYour OPENAI_API_KEY doesn't start with 'sk-'")
        print("This may not be a valid OpenAI API key.")
        print(f"\nCurrent value starts with: {api_key[:7]}...")
        print("\nPlease verify your key at:")
        print("https://platform.openai.com/api-keys")
        print("="*60 + "\n")
        return False

    # Success
    return True