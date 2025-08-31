import unittest
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Discover and run all tests
if __name__ == '__main__':
    # Set the test directory
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)