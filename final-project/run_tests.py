#!/usr/bin/env python3
"""
Test runner for PKMS Task Manager.

Runs all tests with pytest, displays coverage report, and provides
a color-coded summary of results.
"""
import sys
import subprocess
import os
from pathlib import Path


def print_header(text, char="="):
    """Print a formatted header."""
    width = 60
    print()
    print(char * width)
    print(text.center(width))
    print(char * width)
    print()


def print_section(text):
    """Print a section divider."""
    print()
    print("─" * 60)
    print(f"  {text}")
    print("─" * 60)


def check_pytest_installed():
    """Check if pytest is installed."""
    try:
        import pytest
        return True
    except ImportError:
        return False


def install_test_dependencies():
    """Install test dependencies if not present."""
    print("📦 Installing test dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "pytest", "pytest-cov", "pytest-mock"],
            check=True
        )
        print("✓ Test dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install test dependencies")
        return False


def run_tests(coverage=True, verbose=False):
    """
    Run all tests with pytest.
    
    Args:
        coverage: Whether to collect coverage data
        verbose: Whether to use verbose output
    """
    print_header("PKMS Task Manager - Test Suite")
    
    # Check if pytest is installed
    if not check_pytest_installed():
        print("⚠️  pytest not found")
        if input("Install test dependencies? (y/n): ").lower() == 'y':
            if not install_test_dependencies():
                return 1
        else:
            print("Cannot run tests without pytest")
            return 1
    
    # Get the project root directory
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        print(f"✗ Tests directory not found: {tests_dir}")
        return 1
    
    print_section("Running Tests")
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add tests directory
    cmd.append(str(tests_dir))
    
    # Add options
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage options
    if coverage:
        cmd.extend([
            "--cov=core",
            "--cov=modules",
            "--cov-report=term-missing",
            "--cov-report=html"
        ])
    
    # Add color
    cmd.append("--color=yes")
    
    # Add summary
    cmd.append("-ra")
    
    try:
        # Run pytest
        result = subprocess.run(cmd, cwd=str(project_root))
        
        if result.returncode == 0:
            print_section("Results")
            print("✓ All tests passed!")
            
            if coverage:
                print()
                print("📊 Coverage report generated in: htmlcov/index.html")
                print("   Open it in your browser to see detailed coverage")
            
            return 0
        else:
            print_section("Results")
            print("✗ Some tests failed")
            print()
            print("Tip: Run with --verbose for more details")
            return result.returncode
            
    except KeyboardInterrupt:
        print()
        print("⚠️  Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return 1


def run_specific_test(test_file):
    """Run a specific test file."""
    project_root = Path(__file__).parent
    test_path = project_root / "tests" / test_file
    
    if not test_path.exists():
        print(f"✗ Test file not found: {test_path}")
        return 1
    
    print_header(f"Running {test_file}")
    
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_path),
        "-v",
        "--color=yes"
    ]
    
    result = subprocess.run(cmd, cwd=str(project_root))
    return result.returncode


def show_test_list():
    """Show list of available test files."""
    print_header("Available Test Files")
    
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        print("✗ Tests directory not found")
        return
    
    test_files = sorted(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("No test files found")
        return
    
    print("Test files in tests/:")
    print()
    for i, test_file in enumerate(test_files, 1):
        print(f"  {i}. {test_file.name}")
    
    print()
    print("Run a specific test with:")
    print(f"  python {Path(__file__).name} --file <filename>")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run tests for PKMS Task Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests with coverage
  python run_tests.py --no-coverage      # Run tests without coverage
  python run_tests.py --verbose          # Run with verbose output
  python run_tests.py --list             # List all test files
  python run_tests.py --file test_tasks.py   # Run specific test file
        """
    )
    
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Run tests without coverage report"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose test output"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available test files"
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        metavar="FILENAME",
        help="Run a specific test file"
    )
    
    args = parser.parse_args()
    
    # Handle --list
    if args.list:
        show_test_list()
        return 0
    
    # Handle --file
    if args.file:
        return run_specific_test(args.file)
    
    # Run all tests
    return run_tests(
        coverage=not args.no_coverage,
        verbose=args.verbose
    )


if __name__ == "__main__":
    sys.exit(main())
