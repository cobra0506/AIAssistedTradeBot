import os
import json
import time
from datetime import datetime
import ccxt  # For Bybit API connection
from simple_strategy.shared.data_feeder import DataFeeder
from simple_strategy.strategies.strategy_builder import StrategyBuilder

class PaperTradingEngine:
    def __init__(self, api_account, strategy_name, simulated_balance=1000):
        self.api_account = api_account
        self.strategy_name = strategy_name
        self.simulated_balance = float(simulated_balance)
        self.initial_balance = self.simulated_balance
        
        # Initialize components
        self.data_feeder = DataFeeder(data_dir='data')
        self.strategy = None
        self.is_running = False
        self.trades = []
        self.current_positions = {}
        self.exchange = None
        self.bybit_balance = None
        
        print(f"Paper Trading Engine initialized:")
        print(f"  Account: {api_account}")
        print(f"  Strategy: {strategy_name}")
        print(f"  Simulated Balance: ${simulated_balance}")
        
        # Initialize Bybit connection
        self.initialize_exchange()

    def initialize_exchange(self):
        """Initialize Bybit exchange connection for trade execution"""
        try:
            # Load API accounts
            api_accounts_file = os.path.join(os.path.dirname(__file__), 
                                            'api_accounts.json')
            with open(api_accounts_file, 'r') as f:
                accounts = json.load(f)
            
            # Find the selected account
            account_found = False
            for account_type in ['demo_accounts', 'live_accounts']:
                if self.api_account in accounts.get(account_type, {}):
                    account_info = accounts[account_type][self.api_account]
                    api_key = account_info['api_key']
                    api_secret = account_info['api_secret']
                    account_found = True
                    break
            
            if not account_found:
                print(f"Error: Account '{self.api_account}' not found")
                return False
            
            # Initialize Bybit exchange
            self.exchange = ccxt.bybit({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'sandbox': True  # Use testnet for paper trading
            })
            
            # Test connection
            balance = self.exchange.fetch_balance()
            self.bybit_balance = balance['total']['USDT']
            
            print(f"Bybit connection successful")
            print(f"  Bybit balance: ${self.bybit_balance}")
            print(f"  Simulated balance: ${self.simulated_balance}")
            print(f"  Balance offset: ${self.bybit_balance - self.simulated_balance}")
            
            return True
            
        except Exception as e:
            print(f"Error initializing exchange: {e}")
            return False
    
    def load_strategy(self):
        """Load the selected strategy with optimized parameters"""
        try:
            # First, check for optimized parameters
            from simple_strategy.trading.parameter_manager import ParameterManager
            pm = ParameterManager()
            optimized_params = pm.get_parameters(self.strategy_name)
            
            # Import the strategy file
            strategy_module = __import__(f'simple_strategy.strategies.{self.strategy_name}', fromlist=[''])
            
            # Get the strategy function
            if hasattr(strategy_module, 'create_strategy'):
                if optimized_params:
                    # Use optimized parameters
                    self.strategy = strategy_module.create_strategy(**optimized_params)
                    print(f"Strategy '{self.strategy_name}' loaded with optimized parameters")
                    print(f"Last optimized: {optimized_params.get('last_optimized', 'Unknown')}")
                else:
                    # Use default parameters
                    self.strategy = strategy_module.create_strategy()
                    print(f"Strategy '{self.strategy_name}' loaded with default parameters")
                    print("⚠️ Warning: No optimized parameters found")
                return True
            else:
                print(f"Error: Strategy '{self.strategy_name}' missing create_strategy function")
                return False
                
        except Exception as e:
            print(f"Error loading strategy: {e}")
            return False
    
    def start_trading(self):
        """Start paper trading"""
        if not self.load_strategy():
            return False
            
        if not self.exchange:
            print("Error: Exchange not initialized")
            return False
            
        self.is_running = True
        print(f"Paper trading started for {self.strategy_name}")
        
        # Get available symbols from your data collection system
        try:
            # Use your existing data collection system
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
            
            # Get list of symbols that have data files
            symbol_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            available_symbols = [f.replace('.csv', '') for f in symbol_files]
            
            print(f"Found {len(available_symbols)} symbols with data")
            
            # Limit to first 5 symbols for testing
            symbols_to_monitor = available_symbols[:5]
            
        except Exception as e:
            print(f"Error loading symbols from data collection: {e}")
            return False
        
        # Main trading loop
        while self.is_running:
            try:
                # Monitor each symbol using your data collection system
                for symbol in symbols_to_monitor:
                    try:
                        # Get latest data from your data collection system
                        data = self.data_feeder.get_latest_data(symbol, '1m')
                        
                        if data is not None and len(data) > 0:
                            # Generate trading signals using strategy
                            signals = self.generate_signals_for_symbol(symbol, data)
                            
                            # Get current price from the data
                            current_price = data['close'].iloc[-1]
                            
                            # Process signals
                            if signals:
                                self.process_signals(signals, current_price)
                                
                    except Exception as e:
                        print(f"Error processing {symbol}: {e}")
                        continue
                
                # Wait for next iteration
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Error in trading loop: {e}")
                time.sleep(5)
        
        return True
    
    def generate_signals_for_symbol(self, symbol, data):
        """Generate trading signals for a specific symbol using your data"""
        try:
            # Use the data directly from your data collection system
            # It should already be in the right format for your strategy
            
            signals = {}
            
            # Generate signals using the loaded strategy
            if hasattr(self.strategy, 'generate_signals'):
                signals = self.strategy.generate_signals(data)
            else:
                # Fallback simple logic
                last_close = data['close'].iloc[-1]
                prev_close = data['close'].iloc[-2]
                
                if last_close > prev_close:
                    signals[symbol] = 'BUY'
                elif last_close < prev_close:
                    signals[symbol] = 'SELL'
            
            return signals
            
        except Exception as e:
            print(f"Error generating signals for {symbol}: {e}")
            return {}
    
    def stop_trading(self):
        """Stop paper trading"""
        self.is_running = False
        print("Paper trading stopped")
    
    def process_signals(self, signals, current_price):
        """Process trading signals"""
        for symbol, signal in signals.items():
            if signal == 'BUY':
                self.execute_buy(symbol, current_price)
            elif signal == 'SELL':
                self.execute_sell(symbol, current_price)
    
    def execute_buy(self, symbol, current_price):
        """Execute a buy trade"""
        try:
            # Calculate trade amount (10% of simulated balance)
            trade_amount_usd = self.simulated_balance * 0.1
            quantity = trade_amount_usd / current_price
            
            print(f"BUY {symbol}: {quantity:.6f} units at ${current_price:.2f} (${trade_amount_usd:.2f})")
            
            # Record the trade
            trade = {
                'symbol': symbol,
                'type': 'BUY',
                'quantity': quantity,
                'price': current_price,
                'amount_usd': trade_amount_usd,
                'timestamp': datetime.now().isoformat(),
                'balance_before': self.simulated_balance,
                'balance_after': self.simulated_balance  # No change for paper trading
            }
            self.trades.append(trade)
            
            # Update position
            if symbol not in self.current_positions:
                self.current_positions[symbol] = 0
            self.current_positions[symbol] += quantity
            
        except Exception as e:
            print(f"Error executing buy for {symbol}: {e}")
    
    def execute_sell(self, symbol, current_price):
        """Execute a sell trade"""
        try:
            # Check if we have a position to sell
            if symbol not in self.current_positions or self.current_positions[symbol] <= 0:
                print(f"No position to sell for {symbol}")
                return
            
            quantity = self.current_positions[symbol]
            trade_amount_usd = quantity * current_price
            
            print(f"SELL {symbol}: {quantity:.6f} units at ${current_price:.2f} (${trade_amount_usd:.2f})")
            
            # Record the trade
            trade = {
                'symbol': symbol,
                'type': 'SELL',
                'quantity': quantity,
                'price': current_price,
                'amount_usd': trade_amount_usd,
                'timestamp': datetime.now().isoformat(),
                'balance_before': self.simulated_balance,
                'balance_after': self.simulated_balance  # No change for paper trading
            }
            self.trades.append(trade)
            
            # Update position
            self.current_positions[symbol] = 0
            
        except Exception as e:
            print(f"Error executing sell for {symbol}: {e}")
    
    def get_performance_summary(self):
        """Get performance summary"""
        return {
            'initial_balance': self.initial_balance,
            'current_balance': self.simulated_balance,
            'total_trades': len(self.trades),
            'trades': self.trades
        }