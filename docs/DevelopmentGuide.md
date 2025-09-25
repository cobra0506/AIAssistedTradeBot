# AI Assisted TradeBot - Development Guide

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Code Structure and Conventions](#code-structure-and-conventions)
4. [Component Development Guidelines](#component-development-guidelines)
5. [Testing Strategy](#testing-strategy)
6. [Current Development Status](#current-development-status)
7. [Next Phase Development](#next-phase-development)
8. [Deployment Process](#deployment-process)
9. [Troubleshooting Common Issues](#troubleshooting-common-issues)

## 🏗️ Architecture Overview

### System Design Philosophy
The AI Assisted TradeBot follows a **modular, plug-in architecture** with the following principles:
1. **Separation of Concerns**: Each component has a single, well-defined responsibility
2. **Loose Coupling**: Components communicate through well-defined interfaces
3. **Data Independence**: CSV files serve as the universal data exchange format
4. **Incremental Development**: Start with core functionality, add features as plugins
5. **Windows Optimization**: Designed specifically for Windows PC deployment

### Current Architecture

┌─────────────────────────────────────────────────────────────┐
│ Dashboard GUI (main.py) │
│ Control Center & Launcher │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ Data Collection System ✅ COMPLETE │
│ (shared_modules/data_collection/) │
├─────────────────────────────────────────────────────────────┤
│ Historical Data ←→ Real-time Data ←→ CSV Storage │
│ (optimized_data_fetcher) (websocket_handler) (csv_manager) │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ CSV Data Files │
│ (data/ directory) │
│ BTCUSDT_1m.csv ETHUSDT_1m.csv SOLUSDT_1m.csv ... │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ Strategy Base System ✅ COMPLETE │
│ (shared_modules/simple_strategy/) │
├─────────────────────────────────────────────────────────────┤
│ Strategy Framework │
│ (strategy_base.py with complete building blocks) │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ Next Phase: Backtesting Engine 🔄 IN PLANNING │
│ Simple Strategy → SL AI → RL AI → Advanced Features │
└─────────────────────────────────────────────────────────────┘ 
 
### Component Communication
Components communicate through **CSV files** and **direct integration**:
- **Data Flow**: Data Collection → CSV Files → Strategy Components
- **Control Flow**: Dashboard → Component Launchers → Individual Components
- **Data Format**: Standardized CSV with OHLCV + indicators structure
- **Integration**: Direct Python imports between completed components

## 💻 Development Environment Setup

### Prerequisites
- **Python 3.8+**: Latest stable version recommended
- **Windows OS**: Primary development platform
- **VS Code**: Recommended IDE with Python extension
- **Git**: Version control
- **Bybit API Keys**: For live trading (optional for development)

### Initial Setup
```bash
# 1. Clone the repository
git clone https://github.com/cobra0506/AIAssistedTradeBot.git
cd AIAssistedTradeBot

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables (optional)
set BYBIT_API_KEY=your_api_key_here
set BYBIT_API_SECRET=your_api_secret_here

VS Code Configuration 

Create .vscode/settings.json: 
json

{
  "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false
}

Recommended VS Code Extensions 

     Python: Microsoft Python extension
     Pylint: Code linting
     Black: Code formatting
     GitLens: Git integration
     Material Icon Theme: Better file icons
     

📁 Code Structure and Conventions 
Current Directory Structure 

AIAssistedTradeBot/
├── main.py # Dashboard GUI (entry point)
├── requirements.txt # Python dependencies
├── .vscode/ # VS Code configuration
├── venv/ # Virtual environment
├── data/ # Runtime data files (CSV)
├── shared_modules/ # Core functionality
│   ├── __init__.py # Package initialization
│   ├── data_collection/ ✅ COMPLETE
│   │   ├── __init__.py
│   │   ├── launch_data_collection.py # Component launcher
│   │   ├── main.py # Entry point
│   │   ├── console_main.py # Core logic
│   │   ├── gui_monitor.py # GUI interface
│   │   ├── hybrid_system.py ✅ System orchestrator
│   │   ├── optimized_data_fetcher.py ✅ Historical data
│   │   ├── websocket_handler.py ✅ Real-time data
│   │   ├── csv_manager.py ✅ Data persistence
│   │   ├── data_integrity.py ✅ Data validation
│   │   ├── logging_utils.py ✅ Logging system
│   │   └── config.py ✅ Configuration
│   ├── simple_strategy/ ✅ BASE COMPLETE
│   │   ├── __init__.py
│   │   ├── shared/
│   │   │   ├── __init__.py
│   │   │   └── strategy_base.py ✅ Strategy framework
│   │   └── strategies/ # Future implementations
│   ├── sl_ai/ # Future: Supervised Learning
│   └── rl_ai/ # Future: Reinforcement Learning
├── tests/ ✅ COMPREHENSIVE TEST SUITE
│   ├── Enhanced_final_verification.py ✅ Data feeder tests
│   ├── test_strategy_base_complete.py ✅ Strategy base tests
│   └── [other test files...]
└── docs/ # Documentation
    ├── README.md
    ├── DataFetchingInfo.md ✅ UP TO DATE
    ├── ImplementationStatus.md
    ├── ProgrammingPlan.md
    ├── TaskList.md
    └── BacktesterImplementationGuide.md 🔄 NEEDS UPDATING

Naming Conventions 

     Files: snake_case.py (e.g., data_fetcher.py, gui_monitor.py)
     Classes: PascalCase (e.g., DataCollectionConfig, HybridTradingSystem)
     Functions: snake_case() (e.g., fetch_historical_data(), process_websocket_message())
     Variables: snake_case (e.g., api_key, websocket_connection)
     Constants: UPPER_SNAKE_CASE (e.g., API_BASE_URL, MAX_RETRIES)
     Private Members: _single_leading_underscore (e.g., _internal_method())
     

Code Style Guidelines 

     Indentation: 4 spaces (no tabs)
     Line Length: Maximum 120 characters
     Imports: Group imports (standard library, third-party, local)
     Docstrings: Use triple quotes for all public functions and classes
     Comments: Explain why, not what
     Error Handling: Use specific exception types, include context
     

Example Code Structure 
python

"""
Module description goes here.
This module provides functionality for...
"""
import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from .config import DataCollectionConfig
from .logging_utils import setup_logging

logger = logging.getLogger(__name__)

@dataclass
class DataPoint:
    """Represents a single data point with OHLCV data."""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

class DataProcessor:
    """Processes and analyzes market data."""
    
    def __init__(self, config: DataCollectionConfig):
        """Initialize the data processor.
        
        Args:
            config: Configuration object with processing parameters
        """
        self.config = config
        self.logger = setup_logging(__name__)
    
    async def process_data(self, data: List[DataPoint]) -> Dict[str, float]:
        """Process a list of data points and return indicators.
        
        Args:
            data: List of data points to process
            
        Returns:
            Dictionary containing calculated indicators
            
        Raises:
            ValueError: If data is empty or invalid
        """
        if not data:
            raise ValueError("Data list cannot be empty")
        
        try:
            # Processing logic here
            indicators = {}
            indicators['sma_20'] = self._calculate_sma(data, 20)
            indicators['rsi'] = self._calculate_rsi(data, 14)
            return indicators
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            raise
    
    def _calculate_sma(self, data: List[DataPoint], period: int) -> float:
        """Calculate Simple Moving Average."""
        # Implementation here
        pass
    
    def _calculate_rsi(self, data: List[DataPoint], period: int) -> float:
        """Calculate Relative Strength Index."""
        # Implementation here
        pass

🧩 Component Development Guidelines 
General Principles 

     Single Responsibility: Each component does one thing well
     Dependency Injection: Pass dependencies through constructors
     Configuration Driven: Use config objects, not hardcoded values
     Async/Await: Use async for I/O operations
     Error Handling: Handle exceptions gracefully and provide context
     

Data Collection Components ✅ COMPLETE 

These components are finished and fully tested: 
Launchers (launch_*.py) 
python

"""
Component launcher for data collection.
Handles proper package context and subprocess management.
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from shared_modules.data_collection.gui_monitor import main

if __name__ == "__main__":
    main()

Entry Points (main.py) 
python

"""
Entry point for component with GUI/console fallback.
"""
import asyncio
from .console_main import console_main

def run_component():
    """Entry point with error handling and fallback."""
    try:
        # Try to start GUI
        from .gui_monitor import main as gui_main
        gui_main()
    except ImportError:
        print("GUI not available, running in console mode...")
        asyncio.run(console_main())
    except Exception as e:
        print(f"Failed to start component: {e}")
        asyncio.run(console_main())

Core Logic (console_main.py) 

     Contains the main business logic
     Uses async/await for I/O operations
     Implements proper error handling
     Includes performance monitoring

GUI Components (gui_monitor.py) 

     Uses tkinter for cross-platform compatibility
     Implements proper event handling
     Provides real-time status updates
     Includes configuration controls
     

Configuration Management 
python

"""
Centralized configuration management.
"""
import os
from dataclasses import dataclass
from typing import List

@dataclass
class DataCollectionConfig:
    """Configuration for data collection component."""
    
    # API Settings
    BYBIT_API_KEY: str = os.getenv('BYBIT_API_KEY', '')
    BYBIT_API_SECRET: str = os.getenv('BYBIT_API_SECRET', '')
    API_BASE_URL: str = 'https://api.bybit.com'
    
    # Data Settings
    SYMBOLS: List[str] = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    TIMEFRAMES: List[str] = ['1', '5', '15']
    DATA_DIR: str = 'data'
    
    # Performance Settings
    BULK_BATCH_SIZE: int = 20
    BULK_REQUEST_DELAY_MS: int = 10
    BULK_MAX_RETRIES: int = 5
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.DATA_DIR:
            raise ValueError("DATA_DIR cannot be empty")
        if self.BULK_BATCH_SIZE <= 0:
            raise ValueError("BULK_BATCH_SIZE must be positive")

Logging Standards 
python

"""
Standardized logging setup.
"""
import logging
import sys
from typing import Optional

def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up logging with consistent formatting.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

🧪 Testing Strategy 
Current Testing Status ✅ COMPLETE 

The project has comprehensive test coverage for all completed components: 
Data Collection System Tests 

     File: Enhanced_final_verification.py
     Coverage: 8 comprehensive test cases
     Status: ✅ ALL TESTS PASSING
     Tests Include:
         Basic functionality
         CSV manager functionality
         Data persistence
         Data reading
         Data integrity
         Configuration validation
         Hybrid system integration
         Complete workflow

Strategy Base System Tests 

     File: test_strategy_base_complete.py
     Coverage: 16 comprehensive test cases
     Status: ✅ ALL TESTS PASSING
     Tests Include:
         Strategy base initialization
         Position sizing calculations
         Signal validation
         Strategy state management
         Signal generation
         Portfolio risk calculation
         All technical indicators (RSI, SMA, EMA, Stochastic, SRSI)
         Signal detection (oversold, overbought, crossover, crossunder)
         Multi-timeframe data alignment

Testing Guidelines for New Components 

     Test-Driven Development: Write tests before implementation
     Comprehensive Coverage: Test all public methods and edge cases
     Integration Testing: Test component interactions
     Performance Testing: Test with realistic data volumes
     Error Testing: Test error conditions and recovery
     

Test Structure 
python

"""
Example test structure for new components.
"""
import unittest
import asyncio
import tempfile
import shutil
from pathlib import Path

class TestNewComponent(unittest.TestCase):
    """Test cases for new component."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        # Setup test data
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        
    async def test_component_functionality(self):
        """Test core component functionality."""
        # Test implementation
        pass
        
    def test_component_integration(self):
        """Test integration with existing components."""
        # Test integration
        pass

if __name__ == '__main__':
    unittest.main()

📊 Current Development Status 
✅ COMPLETED COMPONENTS 
Phase 1: Data Collection System - COMPLETE 

     OptimizedDataFetcher: Historical data fetching with rate limiting
     WebSocketHandler: Real-time data streaming with auto-reconnection
     CSVManager: Data persistence with configurable retention
     DataIntegrity: Data validation and gap detection
     HybridSystem: System orchestration and integration
     Configuration: Centralized configuration management
     Logging: Professional logging system
     GUI Monitor: Real-time monitoring and control
     Testing: Comprehensive test coverage (8/8 tests passing)
     

Phase 1.2: Strategy Base System - COMPLETE 

     StrategyBase: Abstract base class for all strategies
     Building Blocks: Complete indicator library (RSI, SMA, EMA, Stochastic, SRSI)
     Signal Processing: Oversold/overbought detection, crossover/crossunder
     Multi-Timeframe Support: Data alignment across timeframes
     Position Sizing: Risk-based position calculation
     Risk Management: Signal validation and portfolio risk
     Testing: Comprehensive test coverage (16/16 tests passing)
     

🔄 CURRENT DEVELOPMENT FOCUS 
Phase 2: Backtesting Engine - PLANNING 

Ready to begin implementation using completed components: 

Priority Components: 

     Backtester Engine: Core backtesting logic
     Performance Tracker: Performance metrics and analysis
     Position Manager: Position and balance management
     Risk Manager: Advanced risk management
     

Integration Points: 

     Use existing HybridTradingSystem for data access
     Leverage completed StrategyBase for strategy development
     Utilize existing CSV data files for historical testing
     

🎯 Next Phase Development 
Phase 2: Backtesting Engine Implementation 
Step 1: Core Backtesting Components 
python

# Create backtester directory structure
shared_modules/simple_strategy/backtester/
├── __init__.py
├── backtester_engine.py
├── performance_tracker.py
├── position_manager.py
├── risk_manager.py
└── results_analyzer.py

Step 2: Integration with Existing Systems 
python

"""
Example integration with completed data collection system.
"""
from shared_modules.data_collection.hybrid_system import HybridTradingSystem
from shared_modules.simple_strategy.shared.strategy_base import StrategyBase

class BacktestingEngine:
    def __init__(self, config):
        # Use existing data collection system
        self.data_system = HybridTradingSystem(config)
        # Use existing strategy framework
        self.strategy = StrategyBase("TestStrategy", config.SYMBOLS, config.TIMEFRAMES, config)

Step 3: Strategy Implementation 
python

"""
Example strategy using completed base framework.
"""
class SimpleMAStrategy(StrategyBase):
    def generate_signals(self, data):
        # Use existing building blocks
        sma_20 = self.calculate_sma(data, 20)
        sma_50 = self.calculate_sma(data, 50)
        
        # Use existing signal detection
        if self.check_crossover(sma_20, sma_50):
            return "BUY"
        elif self.check_crossunder(sma_20, sma_50):
            return "SELL"
        
        return "HOLD"
  
Development Timeline 

     Week 1-2: Core backtesting components
     Week 2-3: Performance tracking and risk management
     Week 3-4: Strategy implementation and integration
     Week 4-5: GUI and user interface
     Week 5-6: Testing and optimization
     

🚀 Deployment Process 
Current Deployment Status 

     Data Collection System: ✅ Ready for production use
     Strategy Base System: ✅ Ready for strategy development
     Testing Framework: ✅ Comprehensive and reliable
     Documentation: ✅ Up to date and comprehensive
     

Deployment for Development 
bash

# 1. Ensure all tests pass
python tests/Enhanced_final_verification.py
python tests/test_strategy_base_complete.py

# 2. Start data collection (if needed)
python main.py

# 3. Begin strategy development
# Use completed StrategyBase as foundation

 
Production Deployment Considerations 

     Data Collection: System is production-ready with proper error handling
     Strategy Development: Use completed framework for reliable strategy creation
     Testing: All components thoroughly tested and validated
     Monitoring: Built-in monitoring and logging capabilities
     

🔧 Troubleshooting Common Issues 
Common Issues and Solutions 
Data Collection Issues 

Problem: WebSocket connection fails 
python

# Solution: Check configuration and network
config.ENABLE_WEBSOCKET = True
config.SYMBOLS = ['BTCUSDT']  # Start with single symbol

Problem: CSV file permissions 
python

# Solution: Ensure data directory exists and is writable
import os
os.makedirs(config.DATA_DIR, exist_ok=True)

Strategy Development Issues 

Problem: Strategy base import errors 
python

# Solution: Use correct import path
from shared_modules.simple_strategy.shared.strategy_base import StrategyBase

Problem: Indicator calculation errors 
python

# Solution: Ensure sufficient data length
# Most indicators need at least 'period' data points
if len(data) < period:
    return None  # Or handle appropriately

Testing Issues 

Problem: Tests failing due to missing dependencies 
bash

# Solution: Install all requirements
pip install -r requirements.txt


Problem: Test data not found 
python

# Solution: Tests create temporary data automatically
# No manual setup required

Getting Help 

     Check Documentation: Review DataFetchingInfo.md and this guide
     Run Tests: Execute test suite to identify issues
     Check Logs: Review system logs for error details
     Verify Configuration: Ensure all config values are correct
     

📈 Project Success Metrics 
Completed Metrics ✅ 

     Data Collection: 100% functional with comprehensive testing
     Strategy Framework: 100% functional with 16/16 tests passing
     Code Quality: Professional standards with proper documentation
     Testing: Comprehensive test coverage for all components
     Documentation: Up-to-date and comprehensive
     

Next Phase Metrics 🔄 

     Backtesting Engine: Core functionality and integration
     Performance Tracking: Metrics calculation and analysis
     Strategy Implementation: Working sample strategies
     User Interface: GUI for backtesting operations
     

Last Updated: September 25, 2025
Status: Phase 1 Complete, Ready for Phase 2 (Backtesting Engine)
Completed Components: Data Collection System, Strategy Base Framework
Next Priority: Backtester Engine Implementation
Testing Status: All Tests Passing (24/24 total) 