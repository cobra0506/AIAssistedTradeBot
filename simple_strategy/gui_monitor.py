# simple_strategy/gui_monitor.py - GUI for Simple Strategy Backtester
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from shared.data_feeder import DataFeeder

class SimpleStrategyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Strategy Backtester")
        self.root.geometry("800x600")
        
        # Initialize data feeder
        self.data_feeder = None
        self.loaded_data = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_data_tab()
        self.create_strategy_tab()
        self.create_backtest_tab()
        self.create_results_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_data_tab(self):
        # Data Configuration Tab
        data_frame = ttk.Frame(self.notebook)
        self.notebook.add(data_frame, text="Data Configuration")
        
        # Data Directory
        dir_frame = ttk.LabelFrame(data_frame, text="Data Directory", padding=10)
        dir_frame.pack(fill="x", padx=10, pady=5)
        
        self.data_dir_var = tk.StringVar(value="data")
        ttk.Entry(dir_frame, textvariable=self.data_dir_var, width=50).pack(side="left", padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_data_dir).pack(side="left", padx=5)
        
        # Symbols and Timeframes
        config_frame = ttk.LabelFrame(data_frame, text="Data Configuration", padding=10)
        config_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Symbols
        ttk.Label(config_frame, text="Symbols:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.symbols_var = tk.StringVar(value="BTCUSDT,ETHUSDT")
        ttk.Entry(config_frame, textvariable=self.symbols_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        # Timeframes
        ttk.Label(config_frame, text="Timeframes:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.timeframes_var = tk.StringVar(value="1m,5m,15m")
        ttk.Entry(config_frame, textvariable=self.timeframes_var, width=30).grid(row=1, column=1, padx=5, pady=5)
        
        # Calculate default dates
        today = datetime.today().date()  # Use datetime.today().date() instead of date.today()
        end_date_default = today - timedelta(days=6)  # Today minus 6 days
        start_date_default = today - timedelta(days=1)  # Today minus 1 day
        
        # Date Range
        ttk.Label(config_frame, text="Start Date:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.start_date_var = tk.StringVar(value=end_date_default.strftime("%Y-%m-%d"))
        ttk.Entry(config_frame, textvariable=self.start_date_var, width=30).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(config_frame, text="End Date:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.end_date_var = tk.StringVar(value=start_date_default.strftime("%Y-%m-%d"))
        ttk.Entry(config_frame, textvariable=self.end_date_var, width=30).grid(row=3, column=1, padx=5, pady=5)
        
        # Load Data Button
        ttk.Button(config_frame, text="Load Data", command=self.load_data).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Data Info
        self.data_info_text = tk.Text(config_frame, height=10, width=60)
        self.data_info_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        
        # Scrollbar for data info
        scrollbar = ttk.Scrollbar(config_frame, orient="vertical", command=self.data_info_text.yview)
        scrollbar.grid(row=5, column=2, sticky="ns")
        self.data_info_text.config(yscrollcommand=scrollbar.set)
    
    def create_strategy_tab(self):
        # Strategy Configuration Tab
        strategy_frame = ttk.Frame(self.notebook)
        self.notebook.add(strategy_frame, text="Strategy Configuration")
        
        # Strategy Selection
        select_frame = ttk.LabelFrame(strategy_frame, text="Strategy Selection", padding=10)
        select_frame.pack(fill="x", padx=10, pady=5)
        
        self.strategy_var = tk.StringVar(value="simple_ma")
        strategies = [
            ("Simple Moving Average", "simple_ma"),
            ("Multi-timeframe SRSI", "multi_tf_srsi"),
            ("Custom Strategy", "custom")
        ]
        
        for i, (text, value) in enumerate(strategies):
            ttk.Radiobutton(select_frame, text=text, variable=self.strategy_var, 
                          value=value).grid(row=i, column=0, sticky="w", padx=5, pady=2)
        
        # Strategy Parameters
        param_frame = ttk.LabelFrame(strategy_frame, text="Strategy Parameters", padding=10)
        param_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Common parameters
        ttk.Label(param_frame, text="Initial Balance:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.initial_balance_var = tk.StringVar(value="10000")
        ttk.Entry(param_frame, textvariable=self.initial_balance_var, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Max Risk per Trade (%):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.max_risk_var = tk.StringVar(value="1.0")
        ttk.Entry(param_frame, textvariable=self.max_risk_var, width=20).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Max Positions:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.max_positions_var = tk.StringVar(value="3")
        ttk.Entry(param_frame, textvariable=self.max_positions_var, width=20).grid(row=2, column=1, padx=5, pady=5)
        
        # Strategy-specific parameters (will be updated based on strategy selection)
        self.strategy_params_frame = ttk.LabelFrame(param_frame, text="Strategy Specific Parameters", padding=10)
        self.strategy_params_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        
        self.update_strategy_params()
        
        # Bind strategy selection change
        self.strategy_var.trace('w', lambda *args: self.update_strategy_params())
    
    def create_backtest_tab(self):
        # Backtest Execution Tab
        backtest_frame = ttk.Frame(self.notebook)
        self.notebook.add(backtest_frame, text="Backtest Execution")
        
        # Backtest Controls
        control_frame = ttk.LabelFrame(backtest_frame, text="Backtest Controls", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(control_frame, text="Start Backtest", command=self.start_backtest).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Stop Backtest", command=self.stop_backtest).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Reset", command=self.reset_backtest).pack(side="left", padx=5)
        
        # Progress
        progress_frame = ttk.LabelFrame(backtest_frame, text="Progress", padding=10)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_var = tk.StringVar(value="Ready to start backtest")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(anchor="w")
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=5)
        
        # Log Output
        log_frame = ttk.LabelFrame(backtest_frame, text="Backtest Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=15)
        self.log_text.pack(fill="both", expand=True)
        
        # Scrollbar for log
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=log_scrollbar.set)
    
    def create_results_tab(self):
        # Results Tab
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results")
        
        # Performance Metrics
        metrics_frame = ttk.LabelFrame(results_frame, text="Performance Metrics", padding=10)
        metrics_frame.pack(fill="x", padx=10, pady=5)
        
        # Create metrics display
        metrics = [
            ("Total Return:", "total_return"),
            ("Win Rate:", "win_rate"),
            ("Max Drawdown:", "max_drawdown"),
            ("Profit Factor:", "profit_factor"),
            ("Total Trades:", "total_trades"),
            ("Sharpe Ratio:", "sharpe_ratio")
        ]
        
        self.metrics_vars = {}
        for i, (label, key) in enumerate(metrics):
            ttk.Label(metrics_frame, text=label).grid(row=i//3, column=(i%3)*2, sticky="w", padx=5, pady=2)
            var = tk.StringVar(value="N/A")
            self.metrics_vars[key] = var
            ttk.Label(metrics_frame, textvariable=var, font=("Arial", 10, "bold")).grid(row=i//3, column=(i%3)*2+1, sticky="w", padx=5, pady=2)
        
        # Results Summary
        summary_frame = ttk.LabelFrame(results_frame, text="Results Summary", padding=10)
        summary_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.results_text = tk.Text(summary_frame, height=15)
        self.results_text.pack(fill="both", expand=True)
        
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(summary_frame, orient="vertical", command=self.results_text.yview)
        results_scrollbar.pack(side="right", fill="y")
        self.results_text.config(yscrollcommand=results_scrollbar.set)
    
    def create_status_bar(self):
        # Status Bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", side="bottom")
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var, relief="sunken").pack(fill="x", padx=2, pady=2)
    
    def browse_data_dir(self):
        directory = filedialog.askdirectory(title="Select Data Directory")
        if directory:
            self.data_dir_var.set(directory)
    
    def load_data(self):
        try:
            self.status_var.set("Loading data...")
            
            # Parse symbols and timeframes
            symbols = [s.strip() for s in self.symbols_var.get().split(",")]
            timeframes = [tf.strip() for tf in self.timeframes_var.get().split(",")]
            
            # Parse dates
            start_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
            
            # DEBUG: Print what we're trying to load
            print(f"DEBUG: Attempting to load:")
            print(f"  Data Directory: {self.data_dir_var.get()}")
            print(f"  Symbols: {symbols}")
            print(f"  Timeframes: {timeframes}")
            print(f"  Date Range: {start_date} to {end_date}")
            
            # DEBUG: Check if files exist
            data_dir = Path(self.data_dir_var.get())
            print(f"DEBUG: Checking directory exists: {data_dir.exists()}")
            
            if data_dir.exists():
                files = list(data_dir.glob("*.csv"))
                print(f"DEBUG: Found CSV files: {[f.name for f in files]}")
                
                for symbol in symbols:
                    for timeframe in timeframes:
                        expected_file = data_dir / f"{symbol}_{timeframe}.csv"
                        print(f"DEBUG: Looking for file: {expected_file}")
                        print(f"DEBUG: File exists: {expected_file.exists()}")
            
            # Initialize data feeder
            self.data_feeder = DataFeeder(data_dir=self.data_dir_var.get())
            
            # Load data
            success = self.data_feeder.load_data(symbols, timeframes, start_date, end_date)
            
            if success:
                # Display data info
                info = self.data_feeder.get_data_info()
                self.data_info_text.delete(1.0, tk.END)
                
                for symbol in info:
                    self.data_info_text.insert(tk.END, f"Symbol: {symbol}\n")
                    for timeframe in info[symbol]:
                        data_info = info[symbol][timeframe]
                        self.data_info_text.insert(tk.END, f"  {timeframe}: {data_info['row_count']} rows\n")
                        self.data_info_text.insert(tk.END, f"    Start: {data_info['start_date']}\n")
                        self.data_info_text.insert(tk.END, f"    End: {data_info['end_date']}\n")
                    self.data_info_text.insert(tk.END, "\n")
                
                # Display memory usage
                memory_info = self.data_feeder.get_memory_usage()
                self.data_info_text.insert(tk.END, f"Memory Usage: {memory_info['cache_size_mb']:.2f} MB\n")
                self.data_info_text.insert(tk.END, f"Files Loaded: {memory_info['total_files_loaded']}\n")
                
                self.status_var.set("Data loaded successfully")
                messagebox.showinfo("Success", "Data loaded successfully!")
            else:
                self.status_var.set("Failed to load data")
                messagebox.showerror("Error", "Failed to load data. Check the data directory and file formats.")
                
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            print(f"DEBUG: Exception occurred: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def update_strategy_params(self):
        # Clear existing parameters
        for widget in self.strategy_params_frame.winfo_children():
            widget.destroy()
        
        strategy = self.strategy_var.get()
        
        if strategy == "simple_ma":
            # Simple Moving Average parameters
            ttk.Label(self.strategy_params_frame, text="Fast MA Period:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
            self.fast_ma_var = tk.StringVar(value="10")
            ttk.Entry(self.strategy_params_frame, textvariable=self.fast_ma_var, width=15).grid(row=0, column=1, padx=5, pady=2)
            
            ttk.Label(self.strategy_params_frame, text="Slow MA Period:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
            self.slow_ma_var = tk.StringVar(value="20")
            ttk.Entry(self.strategy_params_frame, textvariable=self.slow_ma_var, width=15).grid(row=1, column=1, padx=5, pady=2)
            
        elif strategy == "multi_tf_srsi":
            # Multi-timeframe SRSI parameters
            ttk.Label(self.strategy_params_frame, text="SRSI Period:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
            self.srsi_period_var = tk.StringVar(value="14")
            ttk.Entry(self.strategy_params_frame, textvariable=self.srsi_period_var, width=15).grid(row=0, column=1, padx=5, pady=2)
            
            ttk.Label(self.strategy_params_frame, text="Oversold Threshold:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
            self.oversold_var = tk.StringVar(value="20")
            ttk.Entry(self.strategy_params_frame, textvariable=self.oversold_var, width=15).grid(row=1, column=1, padx=5, pady=2)
            
            ttk.Label(self.strategy_params_frame, text="Overbought Threshold:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
            self.overbought_var = tk.StringVar(value="80")
            ttk.Entry(self.strategy_params_frame, textvariable=self.overbought_var, width=15).grid(row=2, column=1, padx=5, pady=2)
    
    def start_backtest(self):
        if not self.data_feeder:
            messagebox.showerror("Error", "Please load data first!")
            return
        
        self.status_var.set("Running backtest...")
        self.progress_bar.start()
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Starting backtest...\n")
        
        # This is where we'll implement the actual backtesting logic
        # For now, just simulate a backtest
        self.root.after(2000, self.simulate_backtest)
    
    def stop_backtest(self):
        self.status_var.set("Backtest stopped")
        self.progress_bar.stop()
        self.log_text.insert(tk.END, "Backtest stopped by user.\n")
    
    def reset_backtest(self):
        self.status_var.set("Ready")
        self.progress_bar.stop()
        self.log_text.delete(1.0, tk.END)
        self.results_text.delete(1.0, tk.END)
        
        # Reset metrics
        for var in self.metrics_vars.values():
            var.set("N/A")
    
    def simulate_backtest(self):
        # Simulate backtest completion
        self.progress_bar.stop()
        self.log_text.insert(tk.END, "Backtest completed successfully!\n")
        
        # Simulate some results
        self.metrics_vars['total_return'].set("+15.5%")
        self.metrics_vars['win_rate'].set("65.2%")
        self.metrics_vars['max_drawdown'].set("-8.3%")
        self.metrics_vars['profit_factor'].set("1.85")
        self.metrics_vars['total_trades'].set("142")
        self.metrics_vars['sharpe_ratio'].set("1.42")
        
        # Add results summary
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Backtest Results Summary\n")
        self.results_text.insert(tk.END, "=" * 40 + "\n\n")
        self.results_text.insert(tk.END, "Strategy: Simple Moving Average Crossover\n")
        self.results_text.insert(tk.END, "Symbols: BTCUSDT, ETHUSDT\n")
        self.results_text.insert(tk.END, "Timeframes: 1m, 5m, 15m\n")
        self.results_text.insert(tk.END, "Period: 2023-01-01 to 2023-12-31\n\n")
        self.results_text.insert(tk.END, "Performance Summary:\n")
        self.results_text.insert(tk.END, "- Total Return: +15.5%\n")
        self.results_text.insert(tk.END, "- Win Rate: 65.2%\n")
        self.results_text.insert(tk.END, "- Maximum Drawdown: -8.3%\n")
        self.results_text.insert(tk.END, "- Profit Factor: 1.85\n")
        self.results_text.insert(tk.END, "- Total Trades: 142\n")
        self.results_text.insert(tk.END, "- Sharpe Ratio: 1.42\n\n")
        self.results_text.insert(tk.END, "The strategy performed well with a good risk-adjusted return.\n")
        self.results_text.insert(tk.END, "Consider optimizing parameters for better performance.\n")
        
        self.status_var.set("Backtest completed")
    
    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleStrategyGUI(root)
    root.mainloop()