import os

def check_directory_structure():
    """Check the actual directory structure"""
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"📁 Project Root: {project_root}")
    print("=" * 60)
    
    # Check simple_strategy directory
    simple_strategy_path = os.path.join(project_root, 'simple_strategy')
    if os.path.exists(simple_strategy_path):
        print("✅ simple_strategy directory exists")
        
        # Check backtester subdirectory
        backtester_path = os.path.join(simple_strategy_path, 'backtester')
        if os.path.exists(backtester_path):
            print("✅ backtester directory exists")
            
            # List files in backtester directory
            files = os.listdir(backtester_path)
            print("Files in backtester directory:")
            for file in files:
                if file.endswith('.py'):
                    print(f"• {file}")
                    
        else:
            print("❌ backtester directory does not exist")
            
        # Check strategies subdirectory
        strategies_path = os.path.join(simple_strategy_path, 'strategies')
        if os.path.exists(strategies_path):
            print("✅ strategies directory exists")
            
            # List files in strategies directory
            files = os.listdir(strategies_path)
            print("Files in strategies directory:")
            for file in files:
                if file.endswith('.py'):
                    print(f"• {file}")
                    
        else:
            print("❌ strategies directory does not exist")
            
    else:
        print("❌ simple_strategy directory does not exist")

if __name__ == "__main__":
    check_directory_structure()