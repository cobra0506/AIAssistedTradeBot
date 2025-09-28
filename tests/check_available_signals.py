import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from simple_strategy.strategies import signals_library
    print("✅ Successfully imported signals_library")
    
    # Get all functions from the module
    import inspect
    functions = inspect.getmembers(signals_library, inspect.isfunction)
    
    print("\n📊 Available signals in signals_library:")
    print("=" * 50)
    
    for name, func in functions:
        if not name.startswith('_'):  # Skip private functions
            print(f"• {name}")
            
    print(f"\n📈 Total available signals: {len([f for f in functions if not f[0].startswith('_')])}")
    
except ImportError as e:
    print(f"❌ Error importing signals_library: {e}")
except Exception as e:
    print(f"❌ Error checking signals: {e}")