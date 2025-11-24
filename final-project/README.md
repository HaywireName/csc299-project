# PKMS Task Manager

A terminal-based Personal Knowledge Management System and Task Manager with AI capabilities.

## 🔑 Prerequisites

- Python 3.9 or higher
- OpenAI API key (get one at https://platform.openai.com/api-keys)

## 📦 Installation

1. Clone or download this repository

2. **Set up a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   ```

   Activate the virtual environment:
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```
   - **Windows (Command Prompt):**
     ```cmd
     venv\Scripts\activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key as an environment variable**
      
   Quick setup:
   
   **macOS/Linux:**
```bash
   export OPENAI_API_KEY='sk-your-key-here'
```
   
   **Windows (PowerShell):**
```powershell
   $env:OPENAI_API_KEY="sk-your-key-here"
```

5. Run the program:
```bash
   python main.py
```

   See `setup_instructions.txt` for detailed instructions for your OS.

## 🔐 Security

This project uses system environment variables for API keys - NO files contain secrets!

✅ API key is stored in your system, not in project files
✅ API key is never committed to Git
✅ Safe to share entire project folder

## ⚙️ Configuration

The program reads the OpenAI API key from the `OPENAI_API_KEY` environment variable.

To verify your key is set correctly:

**macOS/Linux:**
```bash
echo $OPENAI_API_KEY
```

**Windows:**
```cmd
echo %OPENAI_API_KEY%
```

## 🚀 First Run

When you run the program for the first time:
```bash
python main.py
```

If the API key is not found, you'll see clear instructions on how to set it up.

## 📖 Commands

Type `help` in the program to see all available commands.

## 🐛 Troubleshooting

**"API key not found" error:**
- Follow the setup instructions in `setup_instructions.txt`
- Make sure you've set the environment variable in the current terminal
- On Windows, you may need to restart your terminal after setting a permanent variable
- Try the temporary setup first to test

**Program works in one terminal but not another:**
- You need to set the environment variable in each new terminal session
- Or set it permanently (see `setup_instructions.txt`)

## 📄 License

MIT License