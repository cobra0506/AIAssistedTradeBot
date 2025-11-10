# root/main.py - Dashboard GUI
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
from simple_strategy.trading.parameter_gui import ParameterGUI

class TradingBotDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Trading Bot Control Center")
        self.root.geometry("600x500")
        self.create_widgets()
    
    def create_widgets(self):
        # Data Collection Section
        self.create_data_collection_section()
        # Simple Strategy Section (NEW - FUNCTIONAL)
        self.create_simple_strategy_section()
        # Placeholder sections for future modules
        self.create_placeholder_section("🤖 SL AI MODULE", "sl_ai")
        self.create_placeholder_section("🧠 RL AI MODULE", "rl_ai")
        # Bottom buttons
        self.create_bottom_buttons()
    
    def create_data_collection_section(self):
        # Data Collection Frame
        dc_frame = ttk.LabelFrame(self.root, text="📊 DATA COLLECTION MODULE", padding=10)
        dc_frame.pack(fill="x", padx=10, pady=5)
        
        # Status
        self.dc_status = tk.StringVar(value="🔴 STOPPED")
        status_label = ttk.Label(dc_frame, textvariable=self.dc_status, font=("Arial", 10, "bold"))
        status_label.pack(anchor="w")
        
        # Buttons
        button_frame = ttk.Frame(dc_frame)
        button_frame.pack(fill="x", pady=5)
        
        self.dc_start_btn = ttk.Button(button_frame, text="START DATA COLLECTION",
                                    command=self.start_data_collection)
        self.dc_start_btn.pack(side="left", padx=5)
        
        self.dc_stop_btn = ttk.Button(button_frame, text="STOP DATA COLLECTION",
                                    command=self.stop_data_collection, state="disabled")
        self.dc_stop_btn.pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="SETTINGS",
                  command=self.open_data_collection_settings).pack(side="left", padx=5)
    
    def create_simple_strategy_section(self):
        # Simple Strategy Frame (NEW - FUNCTIONAL)
        ss_frame = ttk.LabelFrame(self.root, text="📈 SIMPLE STRATEGY MODULE", padding=10)
        ss_frame.pack(fill="x", padx=10, pady=5)
        
        # Status
        self.ss_status = tk.StringVar(value="🔴 STOPPED")
        status_label = ttk.Label(ss_frame, textvariable=self.ss_status, font=("Arial", 10, "bold"))
        status_label.pack(anchor="w")
        
        # Buttons
        button_frame = ttk.Frame(ss_frame)
        button_frame.pack(fill="x", pady=5)
        
        # FIXED: Don't track process, allow multiple instances
        self.ss_start_btn = ttk.Button(button_frame, text="OPEN BACKTESTER",
                                    command=self.start_simple_strategy)
        self.ss_start_btn.pack(side="left", padx=5)
        
        # No stop button needed since we allow multiple instances
        ttk.Button(button_frame, text="SETTINGS",
                  command=self.open_simple_strategy_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="PARAMETER MANAGER",  
              command=self.open_parameter_manager).pack(side="left", padx=5)  
        
        # Info label
        info_label = ttk.Label(ss_frame, text="Open multiple backtest windows to test different strategies simultaneously",
                            font=("Arial", 9), foreground="gray")
        info_label.pack(anchor="w", pady=(5, 0))
    
    def create_placeholder_section(self, title, module_name):
        frame = ttk.LabelFrame(self.root, text=f"{title} (Coming Soon)", padding=10)
        frame.pack(fill="x", padx=10, pady=5)
        
        status_var = tk.StringVar(value="⚫ NOT IMPLEMENTED")
        ttk.Label(frame, textvariable=status_var, font=("Arial", 10, "bold")).pack(anchor="w")
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=5)
        
        ttk.Button(button_frame, text="START", state="disabled").pack(side="left", padx=5)
        ttk.Button(button_frame, text="SETTINGS", state="disabled").pack(side="left", padx=5)
    
    def create_bottom_buttons(self):
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(bottom_frame, text="📋 SYSTEM LOGS").pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="🔧 GLOBAL SETTINGS").pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="❌ EXIT", command=self.root.quit).pack(side="right", padx=5)
    
    def start_data_collection(self):
        try:
            # Start data collection using the launcher script in data_collection folder
            launcher_path = os.path.join(os.path.dirname(__file__), 
                                      "shared_modules", "data_collection", "launch_data_collection.py")
            self.data_collection_process = subprocess.Popen([sys.executable, launcher_path])
            
            # Update UI
            self.dc_status.set("🟢 RUNNING")
            self.dc_start_btn.config(state="disabled")
            self.dc_stop_btn.config(state="normal")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start data collection: {e}")
    
    def stop_data_collection(self):
        if self.data_collection_process:
            try:
                self.data_collection_process.terminate()
                self.data_collection_process = None
                
                # Update UI
                self.dc_status.set("🔴 STOPPED")
                self.dc_start_btn.config(state="normal")
                self.dc_stop_btn.config(state="disabled")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop data collection: {e}")
    
    def open_data_collection_settings(self):
        # Open data collection settings (could open config file or settings GUI)
        messagebox.showinfo("Settings", "Data collection settings would open here")
    
    def start_simple_strategy(self):
        try:
            # FIXED: Start simple strategy backtester without tracking process
            launcher_path = os.path.join(os.path.dirname(__file__), 
                                      "simple_strategy", "gui_monitor.py")
            
            # FIXED: Use subprocess.Popen without tracking - allows multiple instances
            subprocess.Popen([sys.executable, launcher_path])
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start simple strategy backtester: {e}")
    
    def open_simple_strategy_settings(self):
        # Open simple strategy settings (could open config file or settings GUI)
        messagebox.showinfo("Settings", "Simple strategy settings would open here")

    def open_parameter_manager(self):  
        # Open the parameter manager GUI
        param_window = tk.Toplevel(self.root)
        ParameterGUI(param_window)

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotDashboard(root)
    root.mainloop()