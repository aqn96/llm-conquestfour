#!/usr/bin/env python3
"""
Test Runner for LLM GameMaster: Strategic Connect Four

This script makes it easy to run all tests or specific test categories.
"""
import os
import sys
import argparse
import unittest
import logging

def setup_logging():
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run tests for LLM GameMaster')
    parser.add_argument('--module', type=str, default=None,
                      help='Specific test module to run (e.g., test_model_loader)')
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='Enable verbose output')
    return parser.parse_args()

def main():
    """Main function to run tests"""
    # Parse arguments
    args = parse_arguments()
    
    # Set up logging
    setup_logging()
    
    # Determine test pattern
    if args.module:
        # Run specific test module
        pattern = f"tests.{args.module}"
    else:
        # Run all tests
        pattern = "tests"
    
    # Set verbosity
    verbosity = 2 if args.verbose else 1
    
    # Discover and run tests
    logging.info(f"Running tests with pattern: {pattern}")
    
    # Add tests directory to path if needed
    if not os.path.exists("tests/__init__.py"):
        logging.warning("tests/__init__.py not found, adding tests to sys.path")
        sys.path.insert(0, os.path.abspath('.'))
    
    # Discover and run tests
    test_suite = unittest.defaultTestLoader.discover(
        'tests', 
        pattern='test_*.py'
    )
    
    if args.module:
        # Filter for specific module if provided
        filtered_suite = unittest.TestSuite()
        for test in test_suite:
            for subtest in test:
                if args.module in subtest.id():
                    filtered_suite.addTest(subtest)
        test_suite = filtered_suite
    
    # Run the tests
    unittest.TextTestRunner(verbosity=verbosity).run(test_suite)

if __name__ == "__main__":
    main() 