# AI Assisted TradeBot

A comprehensive cryptocurrency trading bot system that combines traditional technical analysis strategies with advanced AI approaches (Supervised Learning and Reinforcement Learning).

## 🎯 Project Vision

Create a modular, extensible trading system that can:
* Collect historical and real-time market data from Bybit exchange
* Implement traditional trading strategies (RSI, EMA, Stochastic, etc.)
* Develop AI-powered trading strategies using Supervised Learning
* Build advanced trading agents using Reinforcement Learning
* Support backtesting, paper trading (Bybit Demo Mode), and live trading

## 🏗️ Current Architecture

### ✅ Phase 1: COMPLETE - Data Collection System
 
AIAssistedTradeBot/
├── main.py                           # Dashboard GUI (Control Center)
├── requirements.txt                  # Python dependencies
├── data/                             # CSV data files
└── shared_modules/                   # Shared components
    └── data_collection/              # Complete data collection system
        ├── launch_data_collection.py  # Component launcher
        ├── gui_monitor.py            # Data collection GUI
        ├── console_main.py           # Console functionality
        ├── hybrid_system.py          # Core orchestrator
        ├── optimized_data_fetcher.py # Historical data
        ├── websocket_handler.py      # Real-time data
        ├── csv_manager.py            # Data persistence
        ├── data_integrity.py         # Data validation
        ├── logging_utils.py          # Logging system
        └── config.py                 # Configuration 
 

### ✅ Phase 1.2: COMPLETE - Strategy Base Component

simple_strategy/
├── init.py
├── shared/
│   ├── init.py
│   └── strategy_base.py             # Strategy framework and building blocks
└── strategies/                       # Strategy implementations
    ├── init.py
    ├── indicators_library.py        # Technical indicators
    ├── signals_library.py          # Trading signals
    ├── strategy_builder.py         # Strategy Builder system
    └── tests/                       # Strategy tests 

### ✅ Phase 2: COMPLETE - Backtesting Engine

simple_strategy/backtester/           # Backtesting components
├── init.py
├── backtester_engine.py             # Core backtesting logic
├── performance_tracker.py           # Performance tracking
├── position_manager.py             # Position management
└── risk_manager.py                 # Risk management 

### ✅ Phase 2.1: COMPLETE - Building Block Strategy System
We've implemented a revolutionary **Building Block Strategy System** that allows you to create ANY trading strategy you can imagine with unprecedented flexibility and speed!

#### 🎯 Key Features:
* **Unlimited Strategy Combinations**: Mix and match any indicators with any signal logic
* **Rapid Development**: Create complex strategies in minutes, not hours
* **No Code Templates**: No need to copy/modify template files
* **Multi-Symbol & Multi-Timeframe**: Built-in support for complex analysis
* **Risk Management Integration**: Automatic integration with your risk system
* **Backtesting Ready**: All strategies work instantly with your backtesting engine

#### 📚 Strategy Building Components:
1. **Indicators Library** (`strategies/indicators_library.py`): 20+ technical indicators
2. **Signals Library** (`strategies/signals_library.py`): 15+ signal processing functions
3. **Strategy Builder** (`strategies/strategy_builder.py`): Ultimate strategy creation tool

#### 🚀 Quick Start Example:
```python
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, sma, ema
from simple_strategy.strategies.signals_library import overbought_oversold, ma_crossover

# Create ANY strategy you want
strategy = StrategyBuilder(['BTCUSDT', 'ETHUSDT'], ['1m', '5m'])

# Add ANY indicators with ANY parameters
strategy.add_indicator('rsi', rsi, period=14)
strategy.add_indicator('sma_short', sma, period=20)
strategy.add_indicator('sma_long', sma, period=50)

# Add ANY signal logic
strategy.add_signal_rule('rsi_oversold', overbought_oversold, oversold=30)
strategy.add_signal_rule('ma_crossover', ma_crossover)

# Combine signals with majority vote
strategy.set_signal_combination('majority_vote')

# Build and use your strategy
my_strategy = strategy.build()

# Run backtest
from simple_strategy.backtester.backtester_engine import BacktestEngine
backtest = BacktestEngine(
    strategy=my_strategy,
    start_date='2023-01-01',
    end_date='2023-12-31',
    initial_capital=10000
)
results = backtest.run()
print(f"Total Return: {results['total_return']:.2f}%")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")

🎯 MAJOR ACHIEVEMENT: Strategy Builder + Backtest Engine Integration 

Status: ✅ FULLY OPERATIONAL
Testing: ✅ ALL TESTS PASSING
Documentation: ✅ COMPLETE 

We have successfully completed the integration between the Strategy Builder system and the Backtest Engine. This represents a revolutionary approach to strategy development and testing. 

Integration Highlights: 

     Unlimited Strategy Creation: Create ANY trading strategy combination imaginable
     Instant Backtesting: Strategies are immediately compatible with the backtesting engine
     Seamless Workflow: From strategy creation to performance analysis in minutes
     Comprehensive Analysis: Detailed performance metrics and reporting
     Risk Management: Integrated risk controls at all levels
     Multi-Symbol Support: Built-in portfolio management capabilities
     

⏳ Future Phases: PLANNED 

     Phase 3: Optimization Engine
     Phase 4: Trading Interfaces (Paper Trading & Live Trading)
     SL AI Program (Supervised Learning)
     RL AI Program (Reinforcement Learning)
     

🚀 Getting Started 
Prerequisites 

     Python 3.8+
     Bybit API credentials (for live trading)
     Stable internet connection
     Windows PC (optimized for Windows deployment)

Installation 
bash

# 1. Clone the repository
git clone https://github.com/cobra0506/AIAssistedTradeBot.git
cd AIAssistedTradeBot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables (optional, for live trading)
set BYBIT_API_KEY=your_api_key_here
set BYBIT_API_SECRET=your_api_secret_here

Running the Application 
Method 1: Using the Dashboard GUI (Recommended) 
bash

python main.py

This opens the control center dashboard where you can: 

     Start/Stop data collection
     Monitor system status
     Access settings (future components)
     

Method 2: Direct Data Collection 
bash

python shared_modules/data_collection/launch_data_collection.py

This opens only the data collection GUI directly. 
Method 3: Strategy Development and Backtesting 
python

# Create and test strategies
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.backtester.backtester_engine import BacktestEngine

# Create your strategy
strategy = StrategyBuilder(['BTCUSDT'], ['1h'])
strategy.add_indicator('rsi', rsi, period=14)
strategy.add_indicator('sma', sma, period=20)
strategy.add_signal_rule('rsi_signal', overbought_oversold, overbought=70, oversold=30)
my_strategy = strategy.build()

# Run backtest
backtest = BacktestEngine(
    strategy=my_strategy,
    start_date='2023-01-01',
    end_date='2023-12-31',
    initial_capital=10000
)
results = backtest.run()

📊 Current Status 
✅ Phase 1 Complete: Data Collection System 

     Historical data fetching from Bybit
     Real-time WebSocket streaming
     CSV storage with integrity validation
     Professional GUI monitoring
     Dashboard control center
     Modular architecture foundation
     Testing: 8/8 tests passing
     

✅ Phase 1.2 Complete: Strategy Base Component 

     Abstract base class for all strategies (StrategyBase)
     Building block functions for common operations
     Multi-timeframe support
     Position sizing methods
     Risk management integration
     Easy strategy creation interface
     Comprehensive indicator library:
         RSI (Relative Strength Index)
         SMA (Simple Moving Average)
         EMA (Exponential Moving Average)
         Stochastic Oscillator
         SRSI (Stochastic RSI)
         
     Signal building blocks:
         Oversold/Overbought detection
         Crossover/Crossunder detection
         
     Testing: 16/16 tests passing
     

✅ Phase 2 Complete: Backtesting Engine 

     Complete backtesting system with realistic trade simulation
     Performance tracking with comprehensive metrics
     Position management for multi-symbol portfolios
     Risk management with stop-loss and take-profit
     Integration with Strategy Builder system
     Testing: ALL tests passing
     

✅ Phase 2.1 Complete: Building Block Strategy System 

     Strategy Builder with unlimited strategy combinations
     20+ technical indicators (RSI, SMA, EMA, MACD, Bollinger Bands, etc.)
     15+ signal processing functions (overbought/oversold, crossovers, etc.)
     Multi-symbol and multi-timeframe support
     Risk management integration
     Testing: ALL tests passing
     

🎯 MAJOR ACHIEVEMENT: Full Integration 

     Strategy Builder + Backtest Engine: ✅ FULLY OPERATIONAL
     Seamless Workflow: From strategy creation to performance analysis
     Production Ready: System fully operational for strategy development
     Comprehensive Testing: 40+ tests passing across all components
     

📁 Project Structure (Current) 

AIAssistedTradeBot/
├── main.py                           # Dashboard GUI (Control Center)
├── requirements.txt                  # Python dependencies
├── data/                             # CSV data files (created at runtime)
│   ├── BTCUSDT_1m.csv
│   ├── BTCUSDT_5m.csv
│   └── ... (per symbol/timeframe)
├── shared_modules/                   # Core functionality
│   ├── __init__.py
│   ├── data_collection/              # Data collection system ✅ COMPLETE
│   │   ├── __init__.py
│   │   ├── launch_data_collection.py # Component launcher
│   │   ├── main.py                   # Data collection entry point
│   │   ├── console_main.py           # Core functionality
│   │   ├── gui_monitor.py            # GUI interface
│   │   ├── hybrid_system.py          # System orchestrator
│   │   ├── optimized_data_fetcher.py # Historical data fetcher
│   │   ├── websocket_handler.py      # Real-time data handler
│   │   ├── csv_manager.py            # CSV file operations
│   │   ├── data_integrity.py         # Data validation
│   │   ├── logging_utils.py          # Logging utilities
│   │   └── config.py                 # Configuration settings
│   ├── simple_strategy/              # Strategy system ✅ COMPLETE
│   │   ├── __init__.py
│   │   ├── backtester/               # Backtesting components ✅ COMPLETE
│   │   │   ├── __init__.py
│   │   │   ├── backtester_engine.py   # Core backtesting logic
│   │   │   ├── performance_tracker.py # Performance tracking
│   │   │   ├── position_manager.py   # Position management
│   │   │   └── risk_manager.py       # Risk management
│   │   ├── shared/                   # Shared strategy components
│   │   │   ├── __init__.py
│   │   │   └── strategy_base.py      # Strategy framework
│   │   └── strategies/               # Strategy implementations ✅ COMPLETE
│   │       ├── __init__.py
│   │       ├── indicators_library.py  # Technical indicators
│   │       ├── signals_library.py     # Trading signals
│   │       ├── strategy_builder.py    # Strategy Builder system
│   │       └── tests/                 # Strategy tests
│   ├── sl_ai/                         # Future: Supervised Learning
│   │   ├── __init__.py
│   │   ├── shared/
│   │   ├── 01_classification/
│   │   ├── 02_regression/
│   │   └── 03_hybrid/
│   └── rl_ai/                         # Future: Reinforcement Learning
│       ├── __init__.py
│       ├── shared/
│       ├── 01_library_based/
│       └── 02_progressive/
├── tests/                             # Test files
│   ├── Enhanced_final_verification.py     # Data feeder tests
│   ├── test_strategy_base_complete.py     # Strategy base tests
│   ├── test_strategy_builder_backtest_integration.py  # Integration tests
│   └── debug_*.py                       # Debug test files
└── docs/                             # Documentation
    ├── README.md                      # Project overview
    ├── DataFetchingInfo.md           # Data collection documentation
    ├── ImplementationStatus.md       # Current implementation status
    ├── ProgrammingPlan.md             # Technical specifications
    ├── DevelopmentGuide.md            # Development guidelines
    ├── BacktesterImplementationGuide.md # Backtesting guide
    └── TaskList.md                    # Task management

📖 Documentation 

     README.md - Project overview and quick start
     DataFetchingInfo.md - Detailed data collection documentation
     ImplementationStatus.md - Current implementation status
     ProgrammingPlan.md - Technical specifications and requirements
     DevelopmentGuide.md - Development guidelines and best practices
     BacktesterImplementationGuide.md - Complete backtesting guide
     TaskList.md - Immediate next steps and priorities
     

🎯 Key Capabilities 
✅ What You Can Do Now 

    Data Collection 
         Fetch historical OHLCV data for 550+ cryptocurrencies
         Stream real-time data via WebSocket
         Multiple timeframe support (1m, 5m, 15m, 1h, 4h, etc.)
         Data integrity validation and gap filling
         
     

    Strategy Development 
         Create ANY trading strategy combination using the Strategy Builder
         20+ technical indicators with customizable parameters
         15+ signal processing functions
         Multi-symbol and multi-timeframe strategies
         No coding required - use builder pattern
         
     

    Backtesting 
         Test strategies on historical data
         Comprehensive performance metrics (Sharpe ratio, drawdown, win rate, etc.)
         Multi-symbol portfolio backtesting
         Risk management integration
         Detailed performance analysis and reporting
         
     

    Risk Management 
         Position sizing based on risk
         Stop-loss and take-profit mechanisms
         Portfolio risk monitoring
         Maximum drawdown control

🔧 Technical Features 

     Modular Architecture: Plug-in design for easy extension
     Windows Optimized: Designed specifically for Windows PC deployment
     CSV-based Storage: Simple, reliable data exchange format
     Async Processing: Efficient concurrent data handling
     Comprehensive Testing: 40+ test cases with all tests passing
     Professional GUI: Intuitive monitoring and control interface
     

🤝 Contributing 

This project follows a modular development approach. Each component is developed and tested independently before integration. 
Development Guidelines 

     Follow the established code conventions (see DevelopmentGuide.md)
     Write comprehensive tests for new features
     Update documentation for any changes
     Ensure all tests pass before submitting changes
     

How to Contribute 

     Fork the repository
     Create a feature branch
     Implement your changes with tests
     Update documentation
     Submit a pull request
     

📄 License 

This project is for educational and research purposes. 
⚠️ Disclaimer 

This software is for educational purposes only. Trading cryptocurrencies involves significant risk. Use at your own risk. 
Risk Warning 

     Cryptocurrency trading is extremely volatile and risky
     Past performance does not guarantee future results
     Never trade with money you cannot afford to lose
     This software is provided "as is" without warranty
     

Legal Notice 

     This is not financial advice
     Users are responsible for their own trading decisions
     The developers are not responsible for any financial losses
     Use responsibly and at your own risk
     