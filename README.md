AI Assisted TradeBot

A comprehensive cryptocurrency trading bot system that combines traditional technical analysis strategies with advanced AI approaches (Supervised Learning and Reinforcement Learning).
🎯 Project Vision

Create a modular, extensible trading system that can:

    Collect historical and real-time market data from Bybit exchange
    Implement traditional trading strategies (RSI, EMA, Stochastic, etc.)
    Develop AI-powered trading strategies using Supervised Learning
    Build advanced trading agents using Reinforcement Learning
    Support backtesting, paper trading (Bybit Demo Mode), and live trading

🏗️ Architecture Overview

This project consists of three distinct programs that share common modules:
Program 1: Simple Strategy Program

Traditional technical analysis strategies with:

    Backtesting engine for historical testing
    Parameter optimization system
    Trading interface for paper and live trading
    Reusable strategy framework

Program 2: SL AI Program

Supervised Learning approaches with progressive complexity:

    Classification Approach (Buy/Sell/Hold signals)
    Regression Approach (Price prediction)
    Hybrid Approach (Combined classification + regression)

Program 3: RL AI Program

Reinforcement Learning approaches:

    Library-Based Approach (Using Stable Baselines3, etc.)
    Progressive Approach (Custom implementation from scratch)

📊 Current Status

    ✅ Phase 1 Complete: Data collection system working
        Historical data fetching from Bybit
        Real-time WebSocket streaming
        CSV storage with integrity validation
        Professional GUI monitoring

    🔄 Next Phase: Simple Strategy Program development

    ⏳ Future: SL AI and RL AI Programs

🚀 Getting Started
Prerequisites

    Python 3.8+
    Bybit API credentials (for live trading)
    Stable internet connection

Installation

git clone https://github.com/cobra0506/AIAssistedTradeBot.git
cd AIAssistedTradeBot
pip install -r requirements.txt

Running the Data Collection System 
bash
 
 
 
1
python main.py
 
 
 
📁 Project Structure 
 
 
 
1
2
3
4
5
6
7
8
9
10
11
12
AIAssistedTradeBot/
├── shared_modules/           # Core functionality for all programs
├── simple_strategy/          # Traditional trading strategies
├── sl_ai/                   # Supervised Learning AI approaches
├── rl_ai/                   # Reinforcement Learning AI approaches
├── data/                    # CSV data files
├── old_files/               # Original implementation files
├── [existing files]          # Current working data collection
├── DataFetchingInfo.md      # Phase 1 documentation
├── DevelopmentGuide.md       # Complete development plan
├── ProgrammingPlan.md       # Technical specifications
└── requirements.txt         # Python dependencies
 
 
 
📖 Documentation 

     Development Guide  - Complete project structure and module descriptions
     Programming Plan  - Technical specifications and requirements
     Data Fetching Info  - Phase 1 data collection system documentation
     Implementation Status  - Current implementation progress
     Task List  - Immediate next steps and priorities
     

🤝 Contributing 

This project follows a modular development approach. Each component is developed and tested independently before integration. 
📄 License 

This project is for educational and research purposes. 
⚠️ Disclaimer 

This software is for educational purposes only. Trading cryptocurrencies involves significant risk. Use at your own risk. 

