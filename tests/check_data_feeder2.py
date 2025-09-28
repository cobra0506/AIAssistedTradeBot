import sys
import os
import inspect

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from shared.data_feeder import DataFeeder
    
    print("✅ Successfully imported DataFeeder")
    
    # Get the constructor signature
    sig = inspect.signature(DataFeeder.__init__)
    print("\n📊 DataFeeder.__init__ parameters:")
    print("=" * 50)
    
    for param_name, param in sig.parameters.items():
        if param_name != 'self':
            print(f"• {param_name}: {param.annotation}")
            if param.default != inspect.Parameter.empty:
                print(f"  Default: {param.default}")
    
    print("\n📋 Full signature:")
    print(f"DataFeeder{sig}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
    # Try alternative import paths
    try:
        from simple_strategy.shared.data_feeder import DataFeeder
        print("\n✅ Successfully imported DataFeeder from alternative path")
        
        sig = inspect.signature(DataFeeder.__init__)
        print(f"\n📋 Full signature from alternative path:")
        print(f"DataFeeder{sig}")
        
    except Exception as e2:
        print(f"❌ Alternative import also failed: {e2}")