# Task Summarizer (command-line)

A tiny command-prompt tool that uses the OpenAI Chat Completions API to compress paragraph-long task descriptions into a few words (5 or fewer). It prints a numbered list of short summaries to stdout.

What it does:
- Sends each paragraph to the chat completions API and asks for a 5-words-or-less summary.
- Reads your API key from the OPENAI_API_KEY environment variable.
- Prints concise summaries to the terminal.

What it does not do:
- No interactive chat, persistence, or history.
- No CLI arguments or file/stdin input out of the box (tasks are hardcoded in the script).
- No offline mode; requires network and a valid API key.
- No guarantees of perfect accuracy or determinism; outputs can vary by model/settings.
- Not intended for sensitive data; requests are sent to a third-party API.
- Costs may be incurred on your API account.

Prerequisites:
- Python 3.9+
- openai Python package
- An OpenAI API key available to your account

Setup:
- Install dependencies:
  - pip install openai
- Set your API key:
  - macOS/Linux: export OPENAI_API_KEY="sk-..."
  - Windows (PowerShell): setx OPENAI_API_KEY "sk-..." (restart the shell)

Running:
- From the project root, run the module from the src folder:
  - cd /Users/abeerdot/VibeCode/csc299-project/tasks4/src
  - python -m tasks4
- You should see "Task Summaries:" followed by short phrases for each sample task.

Configuration:
- Change the model:
  - Edit src/tasks4/__init__.py and set the model string to one available to your account (the sample uses a placeholder). Example: "gpt-4o-mini" or another supported chat model.
- Change the tasks to summarize:
  - Edit the tasks list in src/tasks4/__init__.py and add or remove paragraphs.

Notes:
- Keep summaries short; the prompt enforces “5 words or less.”
- Be mindful of rate limits and usage costs if you expand this to larger batches.
