#!/usr/bin/env python3
"""
Test runner for TCG App tests.

Usage:
    python run_tests.py           # Run all tests
    python run_tests.py -v        # Run with verbose output
    python run_tests.py module    # Run specific test module
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_tests(verbosity=2, pattern='test_*.py'):
    """
    Discover and run all tests.

    Args:
        verbosity: Test output verbosity level (0-2)
        pattern: Pattern for test file discovery

    Returns:
        True if all tests passed, False otherwise
    """
    # Get the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))

    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir, pattern=pattern)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    return result.wasSuccessful()


def main():
    """Main entry point."""
    verbosity = 2 if '-v' in sys.argv or '--verbose' in sys.argv else 1

    # Check for specific test module
    modules = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

    if modules:
        # Run specific module(s)
        pattern = f"test_{modules[0]}*.py" if not modules[0].startswith('test_') else f"{modules[0]}*.py"
    else:
        pattern = 'test_*.py'

    success = run_tests(verbosity=verbosity, pattern=pattern)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
