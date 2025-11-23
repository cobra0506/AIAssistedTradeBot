import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import json
import random
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

class PaperTradingLauncher:
    def __init__(self, api_account=None, strategy_name=None, simulated_balance=None):
        # If parameters not provided, get from command line arguments
        if api_account is None:
            import sys
            if len(sys.argv) >= 4:
                api_account = sys.argv[1]
                strategy_name = sys.argv[2]
                simulated_balance = sys.argv[3]
            else:
                # Default values for testing
                api_account = "Demo Account 1"
                strategy_name = "Strategy_Simple_RSI"
                simulated_balance = "1000"

        self.api_account = api_account
        self.strategy_name = strategy_name
        self.simulated_balance = float(simulated_balance)  # Convert to float
        
        # Create GUI window
        self.root = tk.Tk()
        self.root.title(f"Paper Trading - {strategy_name}")
        self.root.geometry("800x600")
        
        # Initialize trading engine
        self.trading_engine = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(header_frame, text=f"Paper Trading: {self.strategy_name}", 
                 font=("Arial", 14, "bold")).pack(side="left")
        
        # Account info
        account_frame = ttk.Frame(self.root)
        account_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(account_frame, text=f"Account: {self.api_account}").pack(side="left", padx=5)
        ttk.Label(account_frame, text=f"Balance: ${self.simulated_balance}").pack(side="left", padx=5)
        
        # Parameter status
        param_frame = ttk.Frame(self.root)
        param_frame.pack(fill="x", padx=10, pady=5)
        
        # Check for optimized parameters
        from simple_strategy.trading.parameter_manager import ParameterManager
        pm = ParameterManager()
        optimized_params = pm.get_parameters(self.strategy_name)
        
        if optimized_params:
            param_status = f"✅ Using optimized parameters (Last: {optimized_params.get('last_optimized', 'Unknown')})"
            param_color = "green"
        else:
            param_status = "⚠️ Using default parameters (Not optimized)"
            param_color = "orange"
        
        ttk.Label(param_frame, text=param_status, foreground=param_color).pack(side="left", padx=5)
        
        # Control buttons
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_btn = ttk.Button(control_frame, text="START TRADING", 
                                   command=self.start_trading)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="STOP TRADING", 
                                  command=self.stop_trading, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="🔴 STOPPED")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, 
                               font=("Arial", 10, "bold"))
        status_label.pack(side="left", padx=20)
        
        # Trading log
        log_frame = ttk.LabelFrame(self.root, text="Trading Log", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create text widget with scrollbar
        self.log_text = tk.Text(log_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Performance summary
        perf_frame = ttk.LabelFrame(self.root, text="Performance", padding=10)
        perf_frame.pack(fill="x", padx=10, pady=5)
        
        self.perf_text = tk.Text(perf_frame, height=5, width=80)
        self.perf_text.pack(fill="x")
        
        self.log_message("Paper trading window initialized")
        self.update_performance()
    
    def log_message(self, message):
        """Add message to trading log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")

    def update_status(self, status):
        """Update status display"""
        self.status_var.set(status)
    
    def start_trading(self):
        """Start paper trading"""
        try:
            # Check for optimized parameters first
            from simple_strategy.trading.parameter_manager import ParameterManager
            pm = ParameterManager()
            optimized_params = pm.get_parameters(self.strategy_name)
            
            if not optimized_params:
                # Ask user what to do
                result = messagebox.askyesno(
                    "No Optimized Parameters",
                    f"No optimized parameters found for '{self.strategy_name}'.\n\n"
                    f"Do you want to continue with default parameters?\n\n"
                    f"Yes = Use default parameters\n"
                    f"No = Cancel and optimize first"
                )
                if not result:
                    self.log_message("Trading cancelled - no optimized parameters")
                    return
            
            # Import and create trading engine
            from simple_strategy.trading.paper_trading_engine import PaperTradingEngine
            self.trading_engine = PaperTradingEngine(
                self.api_account,
                self.strategy_name,
                self.simulated_balance,
                log_callback=self.log_message,
                status_callback=self.update_status,
                performance_callback=self.update_performance
            )
            
            # Initialize shared data access after engine creation
            self.trading_engine.initialize_shared_data_access()

            # Start performance update timer
            self.update_performance_timer()
            
            # Start trading in a separate thread (simplified for now)
            self.log_message("Starting paper trading...")
            self.status_var.set("🟢 RUNNING")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            # Start REAL trading
            self.start_real_trading()
            
        except Exception as e:
            self.log_message(f"Error starting trading: {e}")
            messagebox.showerror("Error", f"Failed to start trading: {e}")
    
    def stop_trading(self):
        """Stop paper trading"""
        if self.trading_engine:
            self.trading_engine.stop_trading()
        
        self.log_message("Paper trading stopped")
        self.status_var.set("🔴 STOPPED")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
    
    def start_real_trading(self):
        """Start REAL trading using the trading engine"""
        import threading
        
        def trading_loop():
            try:
                # Start the real trading engine
                success = self.trading_engine.start_trading()
                if success:
                    self.log_message("✅ Real trading started successfully")
                else:
                    self.log_message("❌ Failed to start real trading")
                    self.stop_trading()
            except Exception as e:
                self.log_message(f"❌ Error in real trading: {e}")
                self.stop_trading()
        
        # Start real trading in separate thread
        thread = threading.Thread(target=trading_loop)
        thread.daemon = True
        thread.start()
    
    def update_performance(self):
        """Update performance display"""
        try:
            if hasattr(self, 'trading_engine') and self.trading_engine:
                # Get real performance data from the trading engine
                performance = self.trading_engine.get_performance_summary()
                
                initial_balance = performance['initial_balance']
                current_balance = performance['current_balance']
                total_trades = len(performance['trades'])
                
                # Calculate win rate
                winning_trades = [t for t in performance['trades'] if t.get('pnl', 0) > 0]
                win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
                
                # Calculate profit/loss
                pnl = current_balance - initial_balance
                
                perf_text = f"""Initial Balance: ${initial_balance:.2f}
                    Current Balance: ${current_balance:.2f}
                    Total Trades: {total_trades}
                    Win Rate: {win_rate:.1f}%
                    Profit/Loss: ${pnl:.2f}"""
            else:
                # Fallback to dummy data if engine not available
                perf_text = f"""Initial Balance: $1000.00
                    Current Balance: $1000.00
                    Total Trades: 0
                    Win Rate: 0.0%
                    Profit/Loss: $0.00"""
            
            self.perf_text.delete(1.0, "end")
            self.perf_text.insert(1.0, perf_text)
            
        except Exception as e:
            print(f"Error updating performance: {e}")
    
    def run(self):
        """Run the paper trading window"""
        self.root.mainloop()

    def update_performance_timer(self):
        """Update performance display every 5 seconds"""
        try:
            self.update_performance()
            # Schedule next update
            self.root.after(5000, self.update_performance_timer)
        except Exception as e:
            print(f"Error in performance timer: {e}")

if __name__ == "__main__":
    # Get parameters from command line or use defaults
    import sys
    if len(sys.argv) >= 4:
        launcher = PaperTradingLauncher(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        launcher = PaperTradingLauncher()
    launcher.run()