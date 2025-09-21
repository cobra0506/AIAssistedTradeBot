# main.py - Launcher script for AI Assisted TradeBot
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    if len(sys.argv) > 1:
        component = sys.argv[1]
        if component == "data_collection":
            from shared_modules.data_collection.main import run_data_collection
            run_data_collection()
        elif component == "simple_strategy":
            # Will be implemented later
            print("Simple Strategy component not yet implemented")
        elif component == "sl_ai":
            # Will be implemented later
            print("SL AI component not yet implemented")
        elif component == "rl_ai":
            # Will be implemented later
            print("RL AI component not yet implemented")
        else:
            print(f"Unknown component: {component}")
    else:
        print("Usage: python main.py [component]")
        print("Components: data_collection, simple_strategy, sl_ai, rl_ai")
        print("\nFor data collection with GUI, use:")
        print("python main.py data_collection")

if __name__ == "__main__":
    main()