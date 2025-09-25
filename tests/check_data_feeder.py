import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from simple_strategy.shared.data_feeder import DataFeeder

def check_data_feeder_methods():
    """Check what methods DataFeeder has"""
    print("=== DataFeeder Methods ===")
    
    # Create a temporary directory for testing
    import tempfile
    temp_dir = tempfile.mkdtemp()
    print(f"Using temp directory: {temp_dir}")
    
    try:
        feeder = DataFeeder(data_dir=temp_dir)
        
        print("Available methods:")
        for method in dir(feeder):
            if not method.startswith('_'):
                print(f"  - {method}")
        
        print("\nMethod signatures:")
        import inspect
        for method in dir(feeder):
            if not method.startswith('_') and callable(getattr(feeder, method)):
                try:
                    sig = inspect.signature(getattr(feeder, method))
                    print(f"  {method}{sig}")
                except:
                    print(f"  {method}()")
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    check_data_feeder_methods()