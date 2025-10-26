# simple_strategy/gui_monitor.py - Dynamic GUI for Simple Strategy Backtester
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import strategy registry
from strategies.strategy_registry import StrategyRegistry

class SimpleStrategyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynamic Strategy Backtester")
        self.root.geometry("900x700")
        
        # Initialize strategy registry
        try:
            self.strategy_registry = StrategyRegistry()
            self.strategies = self.strategy_registry.get_all_strategies()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load strategy registry: {e}")
            self.strategies = {}
        
        # Initialize variables
        self.current_strategy = None
        self.param_widgets = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_strategy_tab()
        self.create_backtest_tab()
        self.create_results_tab()
        
        # Status bar
        self.create_status_bar()
    
    def create_strategy_tab(self):
        # Strategy Configuration Tab
        strategy_frame = ttk.Frame(self.notebook)
        self.notebook.add(strategy_frame, text="Strategy Configuration")
        
        # Strategy Selection
        select_frame = ttk.LabelFrame(strategy_frame, text="Strategy Selection", padding=10)
        select_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(select_frame, text="Select Strategy:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Strategy dropdown
        strategy_names = list(self.strategies.keys()) if self.strategies else ["No strategies found"]
        self.strategy_var = tk.StringVar(value=strategy_names[0] if strategy_names else "")
        
        self.strategy_combo = ttk.Combobox(select_frame, textvariable=self.strategy_var, 
                                         values=strategy_names, state="readonly", width=40)
        self.strategy_combo.grid(row=0, column=1, padx=5, pady=5)
        self.strategy_combo.bind('<<ComboboxSelected>>', self.on_strategy_selected)
        
        # Strategy description
        self.description_text = tk.Text(select_frame, height=3, width=60)
        self.description_text.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Strategy Parameters
        self.param_frame = ttk.LabelFrame(strategy_frame, text="Strategy Parameters", padding=10)
        self.param_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create Strategy Button
        self.create_btn = ttk.Button(self.param_frame, text="🔧 Create Strategy", command=self.create_strategy)
        self.create_btn.grid(row=100, column=0, columnspan=2, pady=10)
        
        # Strategy Info
        self.strategy_info_text = tk.Text(self.param_frame, height=5, width=70)
        self.strategy_info_text.grid(row=101, column=0, columnspan=2, padx=5, pady=5)
        
        # Initialize with first strategy
        if strategy_names:
            self.on_strategy_selected()

    def _bind_mouse_wheel(self):
        """Bind mouse wheel scrolling to the parameter canvas"""
        def _on_mousewheel(event):
            # Check if mouse is over the parameter canvas
            if self.param_canvas.winfo_containing(event.x, event.y):
                # Scroll the canvas
                self.param_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind to all mouse wheel events
        self.param_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # For Linux
        self.param_canvas.bind_all("<Button-4>", lambda e: self.param_canvas.yview_scroll(-1, "units"))
        self.param_canvas.bind_all("<Button-5>", lambda e: self.param_canvas.yview_scroll(1, "units"))
    
    def on_strategy_selected(self, event=None):
        """Called when strategy selection changes"""
        strategy_name = self.strategy_var.get()
        if not strategy_name or strategy_name not in self.strategies:
            return
        
        try:
            # Get strategy info
            strategy_info = self.strategies[strategy_name]
            
            # Update description
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(1.0, strategy_info.get('description', 'No description available'))
            
            # Update parameters
            self.update_parameters(strategy_info.get('parameters', {}))
            
        except Exception as e:
            print(f"Error updating strategy info: {e}")
    
    def update_parameters(self, parameters):
        """Update parameter widgets based on strategy parameters"""
        # Clear existing parameter widgets (except buttons and info text)
        for widget in self.param_frame.winfo_children():
            if widget.grid_info() and widget.grid_info()['row'] >= 2 and widget.grid_info()['row'] < 100:
                widget.destroy()
        
        self.param_widgets.clear()
        
        row = 0
        for param_name, param_info in parameters.items():
            # Parameter label
            label_text = f"{param_name.replace('_', ' ').title()}"
            if 'description' in param_info:
                label_text += f"\n({param_info['description']})"
            
            ttk.Label(self.param_frame, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            
            # Parameter input based on type
            default_value = param_info.get('default', 0)
            
            if param_info.get('type') == 'int':
                var = tk.IntVar(value=default_value)
                min_val = param_info.get('min', 1)
                max_val = param_info.get('max', 100)
                widget = ttk.Spinbox(self.param_frame, from_=min_val, to=max_val, 
                                   textvariable=var, width=15)
            elif param_info.get('type') == 'float':
                var = tk.DoubleVar(value=default_value)
                min_val = param_info.get('min', 0.1)
                max_val = param_info.get('max', 10.0)
                widget = ttk.Spinbox(self.param_frame, from_=min_val, to=max_val, 
                                   textvariable=var, width=15, increment=0.1)
            elif param_info.get('type') == 'str' and 'options' in param_info:
                var = tk.StringVar(value=default_value)
                widget = ttk.Combobox(self.param_frame, textvariable=var, 
                                    values=param_info['options'], state="readonly", width=20)
            else:  # string or other
                var = tk.StringVar(value=str(default_value))
                widget = ttk.Entry(self.param_frame, textvariable=var, width=20)
            
            widget.grid(row=row, column=1, padx=5, pady=5)
            self.param_widgets[param_name] = var
            row += 1
    
    def create_backtest_tab(self):
        # Backtest Configuration Tab
        backtest_frame = ttk.Frame(self.notebook)
        self.notebook.add(backtest_frame, text="Backtest Configuration")
        
        # Data Directory
        dir_frame = ttk.LabelFrame(backtest_frame, text="Data Directory", padding=10)
        dir_frame.pack(fill="x", padx=10, pady=5)
        
        self.data_dir_var = tk.StringVar(value="data")
        ttk.Entry(dir_frame, textvariable=self.data_dir_var, width=50).pack(side="left", padx=5)
        ttk.Button(dir_frame, text="Browse", command=self.browse_data_dir).pack(side="left", padx=5)
        
        # Symbols and Timeframes
        config_frame = ttk.LabelFrame(backtest_frame, text="Backtest Configuration", padding=10)
        config_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Button(config_frame, text="🔍 Check Data Files", command=self.check_data_files).grid(row=5, column=0, columnspan=2, pady=5)
        
        # Symbols
        ttk.Label(config_frame, text="Symbols (comma-separated):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.symbols_var = tk.StringVar(value="BTCUSDT")
        ttk.Entry(config_frame, textvariable=self.symbols_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        
        # Timeframes
        ttk.Label(config_frame, text="Timeframes (comma-separated):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.timeframes_var = tk.StringVar(value="5m")
        ttk.Entry(config_frame, textvariable=self.timeframes_var, width=40).grid(row=1, column=1, padx=5, pady=5)
        
        # Date Range
        # Fix the date calculation - today minus 7 days to today
        today = datetime.today().date()
        start_date_default = today - timedelta(days=7)  # 7 days ago
        end_date_default = today  # Today

        # Date Range
        ttk.Label(config_frame, text="Start Date:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.start_date_var = tk.StringVar(value=start_date_default.strftime("%Y-%m-%d"))
        ttk.Entry(config_frame, textvariable=self.start_date_var, width=40).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(config_frame, text="End Date:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.end_date_var = tk.StringVar(value=end_date_default.strftime("%Y-%m-%d"))
        ttk.Entry(config_frame, textvariable=self.end_date_var, width=40).grid(row=3, column=1, padx=5, pady=5)

        # Trading Settings
        trading_frame = ttk.LabelFrame(backtest_frame, text="Trading Settings", padding=10)
        trading_frame.pack(fill="x", padx=10, pady=5)

        # Initial balance
        ttk.Label(trading_frame, text="Initial Balance ($):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.initial_balance_var = tk.StringVar(value="10000")
        ttk.Entry(trading_frame, textvariable=self.initial_balance_var, width=15).grid(row=0, column=1, padx=5, pady=2)

        # Max positions
        ttk.Label(trading_frame, text="Max Positions:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.max_positions_var = tk.StringVar(value="3")
        ttk.Entry(trading_frame, textvariable=self.max_positions_var, width=15).grid(row=1, column=1, padx=5, pady=2)

        # Risk per trade (%)
        ttk.Label(trading_frame, text="Risk Per Trade (%):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.risk_per_trade_var = tk.StringVar(value="2.0")
        ttk.Entry(trading_frame, textvariable=self.risk_per_trade_var, width=15).grid(row=2, column=1, padx=5, pady=2)

        # Run Backtest Button
        self.run_btn = ttk.Button(config_frame, text="🚀 Run Backtest", command=self.run_backtest)
        self.run_btn.grid(row=4, column=0, columnspan=2, pady=10)
    
    def create_results_tab(self):
        # Results Tab
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Results")
        
        # Results Text
        self.results_text = tk.Text(results_frame, height=25, width=90)
        self.results_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.results_text.config(yscrollcommand=scrollbar.set)
    
    def create_status_bar(self):
        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_data_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.data_dir_var.set(directory)
    
    def create_strategy(self):
        """Create strategy instance with selected parameters"""
        try:
            strategy_name = self.strategy_var.get()
            if not strategy_name:
                messagebox.showerror("Error", "Please select a strategy")
                return
            
            # Get parameter values
            params = {}
            for param_name, var in self.param_widgets.items():
                params[param_name] = var.get()
            
            # Create strategy instance
            self.current_strategy = self.strategy_registry.create_strategy_instance(
                strategy_name, **params)
            
            if self.current_strategy:
                # Update strategy info
                self.strategy_info_text.delete(1.0, tk.END)
                self.strategy_info_text.insert(tk.END, f"✅ Strategy: {strategy_name}\n")
                self.strategy_info_text.insert(tk.END, f"📊 Parameters: {params}\n")
                self.strategy_info_text.insert(tk.END, f"🔧 Status: Strategy created successfully\n")
                self.strategy_info_text.insert(tk.END, f"⚡ Ready for backtest\n")
                
                self.status_var.set("Strategy created successfully")
            else:
                messagebox.showerror("Error", "Failed to create strategy")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create strategy: {str(e)}")
    
    def run_backtest(self):
        """Run backtest with current strategy and configuration"""
        try:
            # Check if strategy is created
            if not hasattr(self, 'current_strategy') or self.current_strategy is None:
                messagebox.showerror("Error", "Please create a strategy first")
                return
            
            # Get trading settings
            try:
                initial_balance = float(self.initial_balance_var.get())
                max_positions = int(self.max_positions_var.get())
                risk_per_trade = float(self.risk_per_trade_var.get()) / 100.0
            except ValueError:
                messagebox.showerror("Error", "Invalid trading settings!")
                return
            
            self.status_var.set("Running backtest...")
            self.results_text.delete(1.0, tk.END)
            
            # Get backtest parameters
            symbols = [s.strip() for s in self.symbols_var.get().split(',') if s.strip()]
            timeframes = [t.strip() for t in self.timeframes_var.get().split(',') if t.strip()]
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            
            # Display backtest info
            self.results_text.insert(tk.END, f"🚀 BACKTEST CONFIGURATION\n")
            self.results_text.insert(tk.END, f"=" * 50 + "\n")
            self.results_text.insert(tk.END, f"Strategy: {self.current_strategy.name}\n")
            self.results_text.insert(tk.END, f"Symbols: {symbols}\n")
            self.results_text.insert(tk.END, f"Timeframes: {timeframes}\n")
            self.results_text.insert(tk.END, f"Date Range: {start_date} to {end_date}\n")
            self.results_text.insert(tk.END, f"Initial Balance: ${initial_balance}\n")
            self.results_text.insert(tk.END, f"Max Positions: {max_positions}\n")
            self.results_text.insert(tk.END, f"Risk Per Trade: {risk_per_trade*100:.1f}%\n")
            self.results_text.insert(tk.END, f"=" * 50 + "\n\n")
            
            # Import and use your existing backtest engine
            try:
                # Try to import the backtest engine
                from backtester.backtester_engine import BacktesterEngine
                from shared.data_feeder import DataFeeder
                from backtester.position_manager import PositionManager
                
                # Create data feeder
                data_feeder = DataFeeder(data_dir=self.data_dir_var.get())
                
                # Create position manager with custom settings
                position_manager = PositionManager(
                    initial_balance=initial_balance,
                    max_positions=max_positions,
                    max_risk_per_trade=risk_per_trade
                )
                
                # Check if data files exist
                self.results_text.insert(tk.END, "🔍 Checking data files...\n")
                self.root.update()  # Update GUI
                
                for symbol in symbols:
                    for timeframe in timeframes:
                        clean_timeframe = timeframe.rstrip('m')
                        file_path = os.path.join(self.data_dir_var.get(), f"{symbol}_{clean_timeframe}.csv")
                        if os.path.exists(file_path):
                            self.results_text.insert(tk.END, f"✅ Found: {file_path}\n")
                        else:
                            self.results_text.insert(tk.END, f"❌ Missing: {file_path}\n")
                
                self.results_text.insert(tk.END, "\n⏳ Running backtest...\n")
                self.root.update()  # Update GUI
                
                # Create backtester
                backtester = BacktesterEngine(
                    data_feeder=data_feeder,
                    strategy=self.current_strategy
                )
                
                # Try to run backtest with error handling
                try:
                    results = backtester.run_backtest(
                        symbols=symbols,
                        timeframes=timeframes,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    # Display results
                    self.results_text.insert(tk.END, "\n" + "="*50 + "\n")
                    self.results_text.insert(tk.END, "📊 BACKTEST RESULTS\n")
                    self.results_text.insert(tk.END, "="*50 + "\n")
                    
                    # Check if results contain the expected metrics
                    if results and isinstance(results, dict):
                        # Handle direct metrics format (your current format)
                        if 'total_return' in results:
                            self.results_text.insert(tk.END, f"💰 Total Return: {results.get('total_return', 0):.2f}%\n")
                            self.results_text.insert(tk.END, f"🎯 Win Rate: {results.get('win_rate', 0):.2f}%\n")
                            self.results_text.insert(tk.END, f"📈 Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}\n")
                            self.results_text.insert(tk.END, f"📉 Max Drawdown: {results.get('max_drawdown', 0):.2f}%\n")
                            self.results_text.insert(tk.END, f"🔄 Total Trades: {results.get('total_trades', 0)}\n")
                        # Handle nested metrics format (alternative format)
                        elif 'performance_metrics' in results:
                            metrics = results['performance_metrics']
                            self.results_text.insert(tk.END, f"💰 Total Return: {metrics.get('total_return', 0):.2f}%\n")
                            self.results_text.insert(tk.END, f"🎯 Win Rate: {metrics.get('win_rate', 0):.2f}%\n")
                            self.results_text.insert(tk.END, f"📈 Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}\n")
                            self.results_text.insert(tk.END, f"📉 Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%\n")
                            self.results_text.insert(tk.END, f"🔄 Total Trades: {metrics.get('total_trades', 0)}\n")
                        else:
                            self.results_text.insert(tk.END, "❌ No performance metrics returned\n")
                            self.results_text.insert(tk.END, f"Results: {results}\n")
                    else:
                        self.results_text.insert(tk.END, "❌ No results returned\n")
                        self.results_text.insert(tk.END, f"Results: {results}\n")
                    
                    self.status_var.set("✅ Backtest completed successfully")
                    
                except Exception as backtest_error:
                    self.results_text.insert(tk.END, f"\n❌ Backtest execution error: {str(backtest_error)}\n")
                    import traceback
                    self.results_text.insert(tk.END, f"Traceback: {traceback.format_exc()}\n")
                    self.status_var.set("❌ Backtest execution failed")
                    
            except ImportError as e:
                self.results_text.insert(tk.END, f"\n❌ Error: Could not import backtest engine\n")
                self.results_text.insert(tk.END, f"Please ensure backtest engine is available\n")
                self.results_text.insert(tk.END, f"Import error: {str(e)}\n")
                self.status_var.set("❌ Backtest failed - import error")
                    
        except Exception as e:
            self.status_var.set(f"❌ Error running backtest: {str(e)}")
            self.results_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")
            import traceback
            self.results_text.insert(tk.END, f"Traceback: {traceback.format_exc()}\n")
            messagebox.showerror("Error", f"Failed to run backtest: {str(e)}")


    def check_data_files(self):
        """Check if required data files exist"""
        symbols = self.symbols_var.get().split(',')
        symbols = [s.strip() for s in symbols if s.strip()]
        
        timeframes = self.timeframes_var.get().split(',')
        timeframes = [t.strip() for t in timeframes if t.strip()]
        
        # Clear results tab
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"🔍 Checking data directory: {self.data_dir_var.get()}\n\n")
        
        # Check files (remove 'm' from timeframe)
        missing_files = []
        found_files = []
        
        for symbol in symbols:
            for timeframe in timeframes:
                # Remove 'm' from timeframe if present
                clean_timeframe = timeframe.rstrip('m')
                filename = f"{self.data_dir_var.get()}\\{symbol}_{clean_timeframe}.csv"
                if not os.path.exists(filename):
                    missing_files.append(filename)
                else:
                    found_files.append(filename)
        
        # Display results
        self.results_text.insert(tk.END, f"📁 Found {len(found_files)} CSV files:\n")
        for file in found_files:
            self.results_text.insert(tk.END, f"  - {os.path.basename(file)}\n")
        
        if missing_files:
            self.results_text.insert(tk.END, f"\n❌ Missing files:\n")
            for file in missing_files:
                self.results_text.insert(tk.END, f"  - {os.path.basename(file)}\n")
        else:
            self.results_text.insert(tk.END, f"\n✅ All required files found!\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleStrategyGUI(root)
    root.mainloop()


