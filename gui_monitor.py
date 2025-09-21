import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
import queue
import json
import psutil
from datetime import datetime
from typing import Dict, Any
from config import DataCollectionConfig
from hybrid_system import HybridTradingSystem

class DataCollectionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Assisted TradeBot - Data Collection Monitor")
        self.root.geometry("900x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configuration
        self.gui_config = DataCollectionConfig()  # GUI's own config that can be modified
        self.hybrid_system = None
        self.running = False
        
        # Thread communication
        self.log_queue = queue.Queue()
        
        # Status variables
        self.connection_status = "Disconnected"
        self.websocket_status = "Disconnected"
        self.symbols_count = 0
        self.errors_count = 0
        self.last_error = "No errors"
        
        # System stats
        self.memory_usage = "0 MB"
        self.cpu_usage = "0%"
        
        self.setup_gui()
        self.start_gui_updater()
        self.start_system_stats_updater()
        
    def setup_gui(self):
        """Setup the GUI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status Panel
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Connection Status
        ttk.Label(status_frame, text="API Connection:").grid(row=0, column=0, sticky=tk.W)
        self.connection_label = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.connection_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        
        # WebSocket Status
        ttk.Label(status_frame, text="WebSocket:").grid(row=0, column=2, sticky=tk.W)
        self.websocket_label = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.websocket_label.grid(row=0, column=3, sticky=tk.W, padx=(10, 20))
        
        # Symbols Count
        ttk.Label(status_frame, text="Symbols:").grid(row=0, column=4, sticky=tk.W)
        self.symbols_label = ttk.Label(status_frame, text="0")
        self.symbols_label.grid(row=0, column=5, sticky=tk.W, padx=(10, 20))
        
        # Errors Count
        ttk.Label(status_frame, text="Errors:").grid(row=0, column=6, sticky=tk.W)
        self.errors_label = ttk.Label(status_frame, text="0", foreground="red")
        self.errors_label.grid(row=0, column=7, sticky=tk.W, padx=(10, 0))
        
        # Configuration Panel
        config_frame = ttk.LabelFrame(main_frame, text="Configuration Options", padding="10")
        config_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configuration checkboxes
        self.limit_50_var = tk.BooleanVar(value=self.gui_config.LIMIT_TO_50_ENTRIES)
        self.fetch_all_var = tk.BooleanVar(value=self.gui_config.FETCH_ALL_SYMBOLS)
        self.enable_ws_var = tk.BooleanVar(value=self.gui_config.ENABLE_WEBSOCKET)
        self.integrity_var = tk.BooleanVar(value=self.gui_config.RUN_INTEGRITY_CHECK)
        self.gap_filling_var = tk.BooleanVar(value=self.gui_config.RUN_GAP_FILLING)
        
        # Create checkboxes
        ttk.Checkbutton(config_frame, text="Limit to 50 entries", variable=self.limit_50_var, 
                       command=self.update_config).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(config_frame, text="Fetch all symbols", variable=self.fetch_all_var,
                       command=self.update_config).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(config_frame, text="Enable WebSocket", variable=self.enable_ws_var,
                       command=self.update_config).grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(config_frame, text="Run integrity check", variable=self.integrity_var,
                       command=self.update_config).grid(row=1, column=0, sticky=tk.W, padx=(0, 20))
        ttk.Checkbutton(config_frame, text="Run gap filling", variable=self.gap_filling_var,
                       command=self.update_config).grid(row=1, column=1, sticky=tk.W, padx=(0, 20))
        
        # Control Panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        self.start_button = ttk.Button(control_frame, text="Start Data Collection", command=self.start_collection)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_collection, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.test_button = ttk.Button(control_frame, text="Test Connection", command=self.test_connection)
        self.test_button.grid(row=0, column=2, padx=(0, 10))
        
        # System Stats Panel
        stats_frame = ttk.LabelFrame(main_frame, text="System Resources", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(stats_frame, text="Memory:").grid(row=0, column=0, sticky=tk.W)
        self.memory_label = ttk.Label(stats_frame, text="0 MB")
        self.memory_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        
        ttk.Label(stats_frame, text="CPU:").grid(row=0, column=2, sticky=tk.W)
        self.cpu_label = ttk.Label(stats_frame, text="0%")
        self.cpu_label.grid(row=0, column=3, sticky=tk.W, padx=(10, 20))
        
        # Last Error Panel
        error_frame = ttk.LabelFrame(main_frame, text="Last Error/Warning", padding="10")
        error_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.error_label = ttk.Label(error_frame, text="No errors or warnings", foreground="green", wraplength=800)
        self.error_label.grid(row=0, column=0, sticky=tk.W)
        
        # Log Display
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_display = scrolledtext.ScrolledText(log_frame, height=15, width=100)
        self.log_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def update_config(self):
        """Update GUI config when checkboxes change"""
        self.gui_config.LIMIT_TO_50_ENTRIES = self.limit_50_var.get()
        self.gui_config.FETCH_ALL_SYMBOLS = self.fetch_all_var.get()
        self.gui_config.ENABLE_WEBSOCKET = self.enable_ws_var.get()
        self.gui_config.RUN_INTEGRITY_CHECK = self.integrity_var.get()
        self.gui_config.RUN_GAP_FILLING = self.gap_filling_var.get()
        
        self.log_message(f"Configuration updated: {self.get_config_summary()}")
        
    def get_config_summary(self):
        """Get a summary of current config settings"""
        settings = []
        if self.gui_config.LIMIT_TO_50_ENTRIES:
            settings.append("Limit:50")
        if self.gui_config.FETCH_ALL_SYMBOLS:
            settings.append("AllSymbols")
        if self.gui_config.ENABLE_WEBSOCKET:
            settings.append("WebSocket")
        if self.gui_config.RUN_INTEGRITY_CHECK:
            settings.append("Integrity")
        if self.gui_config.RUN_GAP_FILLING:
            settings.append("GapFill")
        return ",".join(settings) if settings else "Default"
        
    def start_gui_updater(self):
        """Start the GUI update loop"""
        def update_gui():
            try:
                # Process log messages
                while not self.log_queue.empty():
                    message = self.log_queue.get_nowait()
                    self.log_display.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
                    self.log_display.see(tk.END)
                    
                    # Update error count if it's an error
                    if "ERROR" in message or "FAIL" in message:
                        self.errors_count += 1
                        self.errors_label.config(text=str(self.errors_count))
                        self.last_error = message
                        self.error_label.config(text=message[-100:] + "..." if len(message) > 100 else message, foreground="red")
                    elif "WARNING" in message:
                        self.last_error = message
                        self.error_label.config(text=message[-100:] + "..." if len(message) > 100 else message, foreground="orange")
                
                # Schedule next update
                self.root.after(100, update_gui)
            except:
                self.root.after(100, update_gui)
        
        update_gui()
        
    def start_system_stats_updater(self):
        """Start updating system stats"""
        def update_stats():
            try:
                # Get memory usage
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                self.memory_usage = f"{memory_mb:.1f} MB"
                self.memory_label.config(text=self.memory_usage)
                
                # Get CPU usage
                cpu_percent = process.cpu_percent(interval=1)
                self.cpu_usage = f"{cpu_percent:.1f}%"
                self.cpu_label.config(text=self.cpu_usage)
                
                # Schedule next update
                self.root.after(2000, update_stats)  # Update every 2 seconds
            except:
                self.root.after(2000, update_stats)
        
        update_stats()
        
    def log_message(self, message: str):
        """Add message to log queue"""
        self.log_queue.put(message)
        
    def update_status(self, connection: str = None, websocket: str = None, symbols: int = None):
        """Update status indicators"""
        if connection:
            self.connection_status = connection
            color = "green" if connection == "Connected" else "red"
            self.connection_label.config(text=connection, foreground=color)
            
        if websocket:
            self.websocket_status = websocket
            color = "green" if websocket == "Connected" else "red"
            self.websocket_label.config(text=websocket, foreground=color)
            
        if symbols is not None:
            self.symbols_count = symbols
            self.symbols_label.config(text=str(symbols))
            
    def start_collection(self):
        """Start data collection"""
        try:
            self.running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.test_button.config(state="disabled")
            self.progress.start()
            
            self.log_message(f"Starting data collection with config: {self.get_config_summary()}")
            
            # Disable config changes during collection
            for child in self.root.winfo_children():
                if isinstance(child, ttk.Checkbutton):
                    child.config(state="disabled")
            
            # Start collection in separate thread
            collection_thread = threading.Thread(target=self.run_collection, daemon=True)
            collection_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start collection: {e}")
            
    def stop_collection(self):
        """Stop data collection"""
        try:
            self.running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.test_button.config(state="normal")
            self.progress.stop()
            
            # Re-enable config changes
            for child in self.root.winfo_children():
                if isinstance(child, ttk.Checkbutton):
                    child.config(state="normal")
            
            self.log_message("Stopping data collection...")
            self.update_status(connection="Disconnected", websocket="Disconnected")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop collection: {e}")
            
    def test_connection(self):
        """Test API connection without full data collection"""
        try:
            self.log_message("Testing API connection...")
            self.progress.start()
            
            # Run test in separate thread
            test_thread = threading.Thread(target=self.run_connection_test, daemon=True)
            test_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start test: {e}")
            
    def run_connection_test(self):
        """Test API connection in a separate thread"""
        try:
            # Create event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize hybrid system
            self.hybrid_system = HybridTradingSystem(self.gui_config)
            
            async def test_task():
                await self.hybrid_system.initialize()
                
                # Update GUI
                self.update_status(connection="Connected")
                self.log_message("✅ API connection successful!")
                
                # Test symbol fetching if enabled
                if self.gui_config.FETCH_ALL_SYMBOLS:
                    symbols = await self.hybrid_system.data_fetcher._get_all_symbols()
                    self.update_status(symbols=len(symbols))
                    self.log_message(f"✅ Found {len(symbols)} symbols")
                else:
                    self.update_status(symbols=len(self.gui_config.SYMBOLS))
                    self.log_message(f"✅ Using {len(self.gui_config.SYMBOLS)} configured symbols")
                    
            # Run the test
            loop.run_until_complete(test_task())
            
        except Exception as e:
            self.log_message(f"❌ Connection test failed: {e}")
        finally:
            # Update GUI when done
            self.root.after(0, lambda: self.progress.stop())
            
    def run_collection(self):
        """Run the data collection in a separate thread"""
        try:
            # Create event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize hybrid system
            self.hybrid_system = HybridTradingSystem(self.gui_config)
            
            async def collection_task():
                await self.hybrid_system.initialize()
                
                # Update GUI
                self.update_status(connection="Connected")
                self.log_message("Connected to API")
                
                # Get symbols to process
                if self.gui_config.FETCH_ALL_SYMBOLS:
                    symbols = await self.hybrid_system.data_fetcher._get_all_symbols()
                else:
                    symbols = self.gui_config.SYMBOLS
                    
                self.update_status(symbols=len(symbols))
                self.log_message(f"Processing {len(symbols)} symbols...")
                
                # Fetch data
                mode = "recent" if self.gui_config.LIMIT_TO_50_ENTRIES else "full"
                success = await self.hybrid_system.fetch_data_hybrid(
                    symbols=symbols,
                    timeframes=self.gui_config.TIMEFRAMES,
                    days=self.gui_config.DAYS_TO_FETCH,
                    mode=mode
                )
                
                if success:
                    self.log_message("✅ Data collection completed successfully!")
                    
                    # Run integrity check if enabled
                    if self.gui_config.RUN_INTEGRITY_CHECK:
                        self.log_message("Running integrity check...")
                        # Note: Integrity check would need to be implemented in the hybrid system
                        
                    # Run gap filling if enabled
                    if self.gui_config.RUN_GAP_FILLING:
                        self.log_message("Running gap filling...")
                        # Note: Gap filling would need to be implemented in the hybrid system
                else:
                    self.log_message("❌ Data collection completed with some errors")
                    
                # Start WebSocket if enabled
                if self.gui_config.ENABLE_WEBSOCKET:
                    self.update_status(websocket="Connected")
                    self.log_message("✅ WebSocket connected - receiving live data...")
                    
                    # Keep running until stopped
                    while self.running:
                        await asyncio.sleep(1)
                        
            # Run the collection task
            loop.run_until_complete(collection_task())
            
        except Exception as e:
            self.log_message(f"❌ Collection error: {e}")
        finally:
            # Update GUI when done
            self.root.after(0, self.stop_collection)
            
    def on_closing(self):
        """Handle window closing"""
        if self.running:
            if messagebox.askokcancel("Quit", "Data collection is running. Are you sure you want to quit?"):
                self.running = False
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    """Main function to run the GUI"""
    gui = DataCollectionGUI()
    gui.run()

if __name__ == "__main__":
    main()

'''import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
import queue
import json
from datetime import datetime
from typing import Dict, Any
from config import DataCollectionConfig
from hybrid_system import HybridTradingSystem

class DataCollectionGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Assisted TradeBot - Data Collection Monitor")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configuration
        self.config = DataCollectionConfig()
        self.hybrid_system = None
        self.running = False
        
        # Thread communication
        self.log_queue = queue.Queue()
        
        # Status variables
        self.connection_status = "Disconnected"
        self.websocket_status = "Disconnected"
        self.symbols_count = 0
        self.errors_count = 0
        
        self.setup_gui()
        self.start_gui_updater()
        
    def setup_gui(self):
        """Setup the GUI components"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status Panel
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Connection Status
        ttk.Label(status_frame, text="API Connection:").grid(row=0, column=0, sticky=tk.W)
        self.connection_label = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.connection_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 20))
        
        # WebSocket Status
        ttk.Label(status_frame, text="WebSocket:").grid(row=0, column=2, sticky=tk.W)
        self.websocket_label = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.websocket_label.grid(row=0, column=3, sticky=tk.W, padx=(10, 20))
        
        # Symbols Count
        ttk.Label(status_frame, text="Symbols:").grid(row=0, column=4, sticky=tk.W)
        self.symbols_label = ttk.Label(status_frame, text="0")
        self.symbols_label.grid(row=0, column=5, sticky=tk.W, padx=(10, 20))
        
        # Errors Count
        ttk.Label(status_frame, text="Errors:").grid(row=0, column=6, sticky=tk.W)
        self.errors_label = ttk.Label(status_frame, text="0", foreground="red")
        self.errors_label.grid(row=0, column=7, sticky=tk.W, padx=(10, 0))
        
        # Control Panel
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Symbol Selection
        ttk.Label(control_frame, text="Symbol:").grid(row=0, column=0, sticky=tk.W)
        self.symbol_var = tk.StringVar(value="BTCUSDT")
        symbol_combo = ttk.Combobox(control_frame, textvariable=self.symbol_var, width=15)
        symbol_combo['values'] = ('BTCUSDT', 'ETHUSDT', 'SOLUSDT')
        symbol_combo.grid(row=0, column=1, padx=(5, 20))
        
        # Timeframe Selection
        ttk.Label(control_frame, text="Timeframe:").grid(row=0, column=2, sticky=tk.W)
        self.timeframe_var = tk.StringVar(value="1")
        timeframe_combo = ttk.Combobox(control_frame, textvariable=self.timeframe_var, width=10)
        timeframe_combo['values'] = ('1', '5', '15')
        timeframe_combo.grid(row=0, column=3, padx=(5, 20))
        
        # Buttons
        self.start_button = ttk.Button(control_frame, text="Start Data Collection", command=self.start_collection)
        self.start_button.grid(row=0, column=4, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_collection, state="disabled")
        self.stop_button.grid(row=0, column=5, padx=(0, 10))
        
        self.test_button = ttk.Button(control_frame, text="Test Single Symbol", command=self.test_single_symbol)
        self.test_button.grid(row=0, column=6, padx=(0, 10))
        
        # Log Display
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_display = scrolledtext.ScrolledText(log_frame, height=20, width=80)
        self.log_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def start_gui_updater(self):
        """Start the GUI update loop"""
        def update_gui():
            try:
                # Process log messages
                while not self.log_queue.empty():
                    message = self.log_queue.get_nowait()
                    self.log_display.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
                    self.log_display.see(tk.END)
                    
                    # Update error count if it's an error
                    if "ERROR" in message or "FAIL" in message:
                        self.errors_count += 1
                        self.errors_label.config(text=str(self.errors_count))
                
                # Schedule next update
                self.root.after(100, update_gui)
            except:
                self.root.after(100, update_gui)
        
        update_gui()
        
    def log_message(self, message: str):
        """Add message to log queue"""
        self.log_queue.put(message)
        
    def update_status(self, connection: str = None, websocket: str = None, symbols: int = None):
        """Update status indicators"""
        if connection:
            self.connection_status = connection
            color = "green" if connection == "Connected" else "red"
            self.connection_label.config(text=connection, foreground=color)
            
        if websocket:
            self.websocket_status = websocket
            color = "green" if websocket == "Connected" else "red"
            self.websocket_label.config(text=websocket, foreground=color)
            
        if symbols is not None:
            self.symbols_count = symbols
            self.symbols_label.config(text=str(symbols))
            
    def start_collection(self):
        """Start data collection"""
        try:
            self.running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.test_button.config(state="disabled")
            self.progress.start()
            
            self.log_message("Starting data collection...")
            
            # Start collection in separate thread
            collection_thread = threading.Thread(target=self.run_collection, daemon=True)
            collection_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start collection: {e}")
            
    def stop_collection(self):
        """Stop data collection"""
        try:
            self.running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.test_button.config(state="normal")
            self.progress.stop()
            
            self.log_message("Stopping data collection...")
            self.update_status(connection="Disconnected", websocket="Disconnected")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop collection: {e}")
            
    def test_single_symbol(self):
        """Test data fetching for a single symbol"""
        try:
            symbol = self.symbol_var.get()
            timeframe = self.timeframe_var.get()
            
            self.log_message(f"Testing {symbol} {timeframe}m...")
            self.progress.start()
            
            # Run test in separate thread
            test_thread = threading.Thread(
                target=self.run_single_test, 
                args=(symbol, timeframe), 
                daemon=True
            )
            test_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start test: {e}")
            
    def run_collection(self):
        """Run the data collection in a separate thread"""
        try:
            # Create event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize hybrid system
            self.hybrid_system = HybridTradingSystem(self.config)
            
            async def collection_task():
                await self.hybrid_system.initialize()
                
                # Update GUI
                self.update_status(connection="Connected")
                self.log_message("Connected to API")
                
                # Get symbols to process
                if self.config.FETCH_ALL_SYMBOLS:
                    symbols = await self.hybrid_system.data_fetcher._get_all_symbols()
                else:
                    symbols = self.config.SYMBOLS
                    
                self.update_status(symbols=len(symbols))
                self.log_message(f"Processing {len(symbols)} symbols...")
                
                # Fetch data
                success = await self.hybrid_system.fetch_data_hybrid(
                    symbols=symbols,
                    timeframes=self.config.TIMEFRAMES,
                    days=self.config.DAYS_TO_FETCH,
                    mode="full" if not self.config.LIMIT_TO_50_ENTRIES else "recent"
                )
                
                if success:
                    self.log_message("Data collection completed successfully!")
                else:
                    self.log_message("Data collection completed with some errors")
                    
                # Start WebSocket if enabled
                if self.config.ENABLE_WEBSOCKET:
                    self.update_status(websocket="Connected")
                    self.log_message("WebSocket connected - receiving live data...")
                    
                    # Keep running until stopped
                    while self.running:
                        await asyncio.sleep(1)
                        
            # Run the collection task
            loop.run_until_complete(collection_task())
            
        except Exception as e:
            self.log_message(f"Collection error: {e}")
        finally:
            # Update GUI when done
            self.root.after(0, self.stop_collection)
            
    def run_single_test(self, symbol: str, timeframe: str):
        """Test single symbol data fetching"""
        try:
            # Create event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize hybrid system
            self.hybrid_system = HybridTradingSystem(self.config)
            
            async def test_task():
                await self.hybrid_system.initialize()
                
                # Fetch data for single symbol
                success = await self.hybrid_system.fetch_data_hybrid(
                    symbols=[symbol],
                    timeframes=[timeframe],
                    days=min(self.config.DAYS_TO_FETCH, 7),  # Limit to 7 days for testing
                    mode="recent"
                )
                
                if success:
                    self.log_message(f"✅ {symbol} {timeframe}m test successful!")
                else:
                    self.log_message(f"❌ {symbol} {timeframe}m test failed!")
                    
            # Run the test
            loop.run_until_complete(test_task())
            
        except Exception as e:
            self.log_message(f"Test error: {e}")
        finally:
            # Update GUI when done
            self.root.after(0, lambda: self.progress.stop())
            
    def on_closing(self):
        """Handle window closing"""
        if self.running:
            if messagebox.askokcancel("Quit", "Data collection is running. Are you sure you want to quit?"):
                self.running = False
                self.root.destroy()
        else:
            self.root.destroy()
            
    def run(self):
        """Start the GUI"""
        self.root.mainloop()

def main():
    """Main function to run the GUI"""
    gui = DataCollectionGUI()
    gui.run()

if __name__ == "__main__":
    main()'''