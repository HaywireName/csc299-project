"""
Shim entry point to allow `python main.py ...` to run the CLI.
Delegates to src.cli.main:main().
"""
from src.cli.main import main


if __name__ == "__main__":
    raise SystemExit(main())
