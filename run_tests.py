"""
Test Runner Script
Provides an easy way to run all tests
"""

import pytest
import sys
import os

def run_tests():
    """Run all tests with appropriate configuration"""
    
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Define test arguments
    test_args = [
        'tests/',           # Test directory
        '-v',              # Verbose output
        '--tb=short',      # Short traceback format
        '-m', 'not integration',  # Skip integration tests by default
    ]
    
    # Run tests
    exit_code = pytest.main(test_args)
    
    return exit_code

def run_integration_tests():
    """Run integration tests that require network connection"""
    
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Define test arguments for integration tests
    test_args = [
        'tests/',           # Test directory
        '-v',              # Verbose output
        '--tb=short',      # Short traceback format
        '-m', 'integration',  # Run only integration tests
    ]
    
    # Run integration tests
    exit_code = pytest.main(test_args)
    
    return exit_code

def run_all_tests():
    """Run all tests including integration tests"""
    
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Define test arguments for all tests
    test_args = [
        'tests/',           # Test directory
        '-v',              # Verbose output
        '--tb=short',      # Short traceback format
    ]
    
    # Run all tests
    exit_code = pytest.main(test_args)
    
    return exit_code

if __name__ == '__main__':
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'integration':
            print("Running integration tests...")
            exit_code = run_integration_tests()
        elif sys.argv[1] == 'all':
            print("Running all tests...")
            exit_code = run_all_tests()
        else:
            print("Usage: python run_tests.py [integration|all]")
            print("  No argument: Run unit tests only")
            print("  integration: Run integration tests only")  
            print("  all: Run all tests")
            exit_code = 1
    else:
        print("Running unit tests...")
        exit_code = run_tests()
    
    sys.exit(exit_code)