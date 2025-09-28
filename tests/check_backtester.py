import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from simple_strategy.backtester import backtester_engine
    print("✅ Successfully imported backtester_engine")
    
    # Get all classes and functions from the module
    import inspect
    classes = inspect.getmembers(backtester_engine, inspect.isclass)
    functions = inspect.getmembers(backtester_engine, inspect.isfunction)
    
    print("\n📊 Available classes in backtester_engine:")
    print("=" * 50)
    
    for name, cls in classes:
        if not name.startswith('_'):  # Skip private classes
            print(f"• {name}")
            
    print("\n📊 Available functions in backtester_engine:")
    print("=" * 50)
    
    for name, func in functions:
        if not name.startswith('_'):  # Skip private functions
            print(f"• {name}")
            
    print(f"\n📈 Total available classes: {len([c for c in classes if not c[0].startswith('_')])}")
    print(f"📈 Total available functions: {len([f for f in functions if not f[0].startswith('_')])}")
    
except ImportError as e:
    print(f"❌ Error importing backtester_engine: {e}")
    
    # Try to check what's in the backtester directory
    try:
        import simple_strategy.backtester
        print(f"✅ Successfully imported simple_strategy.backtester")
        
        # List contents of the backtester module
        print(f"\n📁 Contents of simple_strategy.backtester:")
        print("=" * 50)
        
        for item in dir(simple_strategy.backtester):
            if not item.startswith('_'):
                print(f"• {item}")
                
    except ImportError as e2:
        print(f"❌ Error importing simple_strategy.backtester: {e2}")
        
        # Try to check the directory structure
        backtester_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'simple_strategy', 'backtester')
        print(f"\n📁 Checking directory: {backtester_path}")
        
        if os.path.exists(backtester_path):
            print("✅ Directory exists")
            files = os.listdir(backtester_path)
            print("Files in backtester directory:")
            for file in files:
                print(f"• {file}")
        else:
            print("❌ Directory does not exist")
            
except Exception as e:
    print(f"❌ Error checking backtester: {e}")