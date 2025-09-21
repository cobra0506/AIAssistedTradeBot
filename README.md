# AI Assisted TradeBot

A comprehensive cryptocurrency trading bot system that combines traditional technical analysis strategies with advanced AI approaches (Supervised Learning and Reinforcement Learning).

## 🎯 Project Vision

Create a modular, extensible trading system that can:
- Collect historical and real-time market data from Bybit exchange
- Implement traditional trading strategies (RSI, EMA, Stochastic, etc.)
- Develop AI-powered trading strategies using Supervised Learning
- Build advanced trading agents using Reinforcement Learning
- Support backtesting, paper trading (Bybit Demo Mode), and live trading

## 🏗️ Current Architecture

### Phase 1: ✅ COMPLETE - Data Collection System

AIAssistedTradeBot/
├── main.py                    # Dashboard GUI (Control Center)
├── requirements.txt           # Python dependencies
├── data/                      # CSV data files
└── shared_modules/
    └── data_collection/       # Complete data collection system
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
 
### Future Phases: 🔄 PLANNED

├── simple_strategy/          # Traditional trading strategies
├── sl_ai/                    # Supervised Learning AI
└── rl_ai/                    # Reinforcement Learning AI 

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Bybit API credentials (for live trading)
- Stable internet connection
- Windows PC (optimized for Windows deployment)

### Installation
```bash
git clone https://github.com/cobra0506/AIAssistedTradeBot.git
cd AIAssistedTradeBot
pip install -r requirements.txt
 
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
📊 Current Status 
✅ Phase 1 Complete: Data Collection System 

     Historical data fetching from Bybit
     Real-time WebSocket streaming
     CSV storage with integrity validation
     Professional GUI monitoring
     Dashboard control center
     Modular architecture foundation
     

🔄 Next Phase: Simple Strategy Program 

     Strategy framework implementation
     Backtesting engine
     Paper trading interface
     Technical indicators library
     

⏳ Future Phases 

     SL AI Program (Supervised Learning)
     RL AI Program (Reinforcement Learning)
     

📁 Project Structure (Current) 
 
AIAssistedTradeBot/
├── main.py                              # Dashboard GUI (Control Center)
├── requirements.txt                     # Python dependencies
├── data/                               # CSV data files (created at runtime)
│   ├── BTCUSDT_1m.csv
│   ├── BTCUSDT_5m.csv
│   └── ... (per symbol/timeframe)
├── shared_modules/                     # Core functionality
│   ├── __init__.py
│   ├── data_collection/                # Data collection system
│   │   ├── __init__.py
│   │   ├── launch_data_collection.py  # Component launcher
│   │   ├── main.py                    # Data collection entry point
│   │   ├── console_main.py            # Core functionality
│   │   ├── gui_monitor.py            # GUI interface
│   │   ├── hybrid_system.py          # System orchestrator
│   │   ├── optimized_data_fetcher.py # Historical data fetcher
│   │   ├── websocket_handler.py      # Real-time data handler
│   │   ├── csv_manager.py            # CSV file operations
│   │   ├── data_integrity.py         # Data validation
│   │   ├── logging_utils.py          # Logging utilities
│   │   └── config.py                 # Configuration settings
│   ├── simple_strategy/              # Future: Traditional strategies
│   │   ├── __init__.py
│   │   ├── shared/
│   │   └── strategies/
│   ├── sl_ai/                        # Future: Supervised Learning
│   │   ├── __init__.py
│   │   ├── shared/
│   │   ├── 01_classification/
│   │   ├── 02_regression/
│   │   └── 03_hybrid/
│   └── rl_ai/                        # Future: Reinforcement Learning
│       ├── __init__.py
│       ├── shared/
│       ├── 01_library_based/
│       └── 02_progressive/
└── docs/                              # Documentation
    ├── README.md
    ├── DataFetchingInfo.md
    ├── ImplementationStatus.md
    ├── ProgrammingPlan.md
    └── TaskList.md
 
 
 
📖 Documentation 

     README.md - Project overview and quick start
     DataFetchingInfo.md - Detailed data collection documentation
     ImplementationStatus.md - Current implementation status
     ProgrammingPlan.md - Technical specifications and requirements
     TaskList.md - Immediate next steps and priorities
     

🤝 Contributing 

This project follows a modular development approach. Each component is developed and tested independently before integration. 
📄 License 

This project is for educational and research purposes. 
⚠️ Disclaimer 

This software is for educational purposes only. Trading cryptocurrencies involves significant risk. Use at your own risk. 