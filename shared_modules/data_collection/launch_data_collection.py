# shared_modules/data_collection/launch_data_collection.py
import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import and run the data collection GUI
from shared_modules.data_collection.gui_monitor import main

if __name__ == "__main__":
    main()