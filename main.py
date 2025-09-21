# root/main.py - Dashboard GUI
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class TradingBotDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Trading Bot Control Center")
        self.root.geometry("600x500")
        
        # Track running processes
        self.data_collection_process = None
        
        self.create_widgets()
    
    def create_widgets(self):
        # Data Collection Section
        self.create_data_collection_section()
        
        # Placeholder sections for future modules
        self.create_placeholder_section("📈 SIMPLE STRATEGY MODULE", "simple_strategy")
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

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingBotDashboard(root)
    root.mainloop()
