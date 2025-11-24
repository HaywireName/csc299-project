import sys
from config import check_api_key

def main():
    # Check API key first
    if not check_api_key():
        sys.exit(1)

    # API key is valid, continue with program
    print("\n✓ OpenAI API key found and validated")
    print("Welcome to PKMS Task Manager!")
    print("Type 'help' for available commands.\n")

    while True:
        try:
            user_input = input("pkms> ").strip()
            if not user_input:
                continue

            command = user_input.split()[0].lower()

            if command == 'help':
                print("Available commands: help, exit")
            elif command == 'exit':
                print("Goodbye!")
                break
            else:
                print(f"Unknown command: {command}")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

if __name__ == '__main__':
    main()