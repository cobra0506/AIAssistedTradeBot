import sys
import os
import inspect

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from simple_strategy.backtester.backtester_engine import BacktesterEngine
    
    print("✅ Successfully imported BacktesterEngine")
    
    # Get the constructor signature
    sig = inspect.signature(BacktesterEngine.__init__)
    print("\n📊 BacktesterEngine.__init__ parameters:")
    print("=" * 50)
    
    for param_name, param in sig.parameters.items():
        if param_name != 'self':
            print(f"• {param_name}: {param.annotation}")
            if param.default != inspect.Parameter.empty:
                print(f"  Default: {param.default}")
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                print(f"  Kind: **kwargs")
    
    print("\n📋 Full signature:")
    print(f"BacktesterEngine{sig}")
    
except Exception as e:
    print(f"❌ Error: {e}")