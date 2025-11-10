import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from simple_strategy.trading.parameter_gui import ParameterGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = ParameterGUI(root)
    root.mainloop()