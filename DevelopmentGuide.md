# AI Assisted TradeBot - Development Guide

## 📋 Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Code Structure and Conventions](#code-structure-and-conventions)
4. [Component Development Guidelines](#component-development-guidelines)
5. [Testing Strategy](#testing-strategy)
6. [Deployment Process](#deployment-process)
7. [Troubleshooting Common Issues](#troubleshooting-common-issues)

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
│                    Dashboard GUI (main.py)                    │
│                 Control Center & Launcher                     │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                Data Collection System                        │
│          (shared_modules/data_collection/)                   │
├─────────────────────────────────────────────────────────────┤
│  Historical Data ←→ Real-time Data ←→ CSV Storage            │
│  (optimized_data_fetcher) (websocket_handler) (csv_manager) │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    CSV Data Files                          │
│                 (data/ directory)                          │
│  BTCUSDT_1m.csv  ETHUSDT_1m.csv  SOLUSDT_1m.csv ...        │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│              Future Components (Planned)                    │
│  Simple Strategy → SL AI → RL AI → Advanced Features       │
└─────────────────────────────────────────────────────────────┘ 

### Component Communication
Components communicate through **CSV files** and **subprocess calls**:
- **Data Flow**: Data Collection → CSV Files → Strategy/AI Components
- **Control Flow**: Dashboard → Component Launchers → Individual Components
- **Data Format**: Standardized CSV with OHLCV + indicators structure

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
Directory Structure 

AIAssistedTradeBot/
├── main.py                          # Dashboard GUI (entry point)
├── requirements.txt                 # Python dependencies
├── .vscode/                         # VS Code configuration
├── venv/                            # Virtual environment
├── data/                            # Runtime data files (CSV)
├── shared_modules/                  # Core functionality
│   ├── __init__.py                  # Package initialization
│   ├── data_collection/             # Data collection system
│   │   ├── __init__.py
│   │   ├── launch_data_collection.py  # Component launcher
│   │   ├── main.py                  # Entry point
│   │   ├── console_main.py          # Core logic
│   │   ├── gui_monitor.py           # GUI interface
│   │   ├── hybrid_system.py         # System orchestrator
│   │   ├── optimized_data_fetcher.py # Historical data
│   │   ├── websocket_handler.py     # Real-time data
│   │   ├── csv_manager.py           # Data persistence
│   │   ├── data_integrity.py        # Data validation
│   │   ├── logging_utils.py        # Logging system
│   │   └── config.py                # Configuration
│   ├── simple_strategy/             # Future: Traditional strategies
│   ├── sl_ai/                       # Future: Supervised Learning
│   └── rl_ai/                       # Future: Reinforcement Learning
└── docs/                            # Documentation
    ├── README.md
    ├── DataFetchingInfo.md
    ├── ImplementationStatus.md
    ├── ProgrammingPlan.md
    └── TaskList.md
 
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
     

Data Collection Components 
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
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
    
    return logger
 
🧪 Testing Strategy 
Testing Philosophy 

     Unit Tests: Test individual components in isolation
     Integration Tests: Test component interactions
     Performance Tests: Ensure system meets performance requirements
     Error Handling Tests: Verify proper error handling and recovery
     

Test Structure 

tests/
├── unit/
│   ├── test_data_fetcher.py
│   ├── test_websocket_handler.py
│   ├── test_csv_manager.py
│   └── test_data_integrity.py
├── integration/
│   ├── test_hybrid_system.py
│   ├── test_full_data_collection.py
│   └── test_gui_integration.py
├── performance/
│   ├── test_bulk_processing.py
│   ├── test_websocket_performance.py
│   └── test_memory_usage.py
└── fixtures/
    ├── sample_data.csv
    ├── config_test.py
    └── mock_responses.json
  
 
Example Unit Test 
python

"""
Unit tests for data fetcher component.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch

from shared_modules.data_collection.optimized_data_fetcher import OptimizedDataFetcher
from shared_modules.data_collection.config import DataCollectionConfig

@pytest.fixture
def config():
    """Create test configuration."""
    return DataCollectionConfig(
        SYMBOLS=['BTCUSDT'],
        TIMEFRAMES=['1'],
        BULK_BATCH_SIZE=1,
        BULK_REQUEST_DELAY_MS=1
    )

@pytest.fixture
def data_fetcher(config):
    """Create data fetcher instance for testing."""
    return OptimizedDataFetcher(config)

@pytest.mark.asyncio
async def test_fetch_historical_data(data_fetcher):
    """Test historical data fetching."""
    with patch('aiohttp.ClientSession.get') as mock_get:
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': {
                'list': [
                    {'open': '45000', 'high': '45100', 'low': '44900', 'close': '45050', 'volume': '1000', 'timestamp': '1630000000'}
                ]
            }
        }
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Test data fetching
        data = await data_fetcher.fetch_historical_data('BTCUSDT', '1', 1)
        
        assert len(data) == 1
        assert data[0]['open'] == 45000
        assert mock_get.called_once()

def test_config_validation():
    """Test configuration validation."""
    with pytest.raises(ValueError):
        DataCollectionConfig(DATA_DIR='')
    
    with pytest.raises(ValueError):
        DataCollectionConfig(BULK_BATCH_SIZE=0)
 
Running Tests 
bash

# Run all tests
pytest

# Run with coverage
pytest --cov=shared_modules

# Run specific test file
pytest tests/unit/test_data_fetcher.py

# Run with verbose output
pytest -v
 
 
 
🚀 Deployment Process 
Development to Production Workflow 

     Development: Feature development in feature branches
     Testing: Comprehensive testing including integration tests
     Staging: Deploy to staging environment for validation
     Production: Deploy to production with monitoring
     

Deployment Checklist 

     All tests pass
     Documentation updated
     Configuration validated
     Performance benchmarks met
     Error handling tested
     Logging configured
     Backup procedures in place
     

Windows Deployment 
powershell

# 1. Create deployment package
python -m pip install pyinstaller
pyinstaller --onefile --windowed main.py

# 2. Create installer (optional)
# Use Inno Setup or similar to create installer

# 3. Deploy
# Copy executable and required files to target system

🔧 Troubleshooting Common Issues 
Import Errors 

Problem: ImportError: attempted relative import with no known parent package 

Solution: Ensure components are launched through proper launcher scripts: 
python

# Use launcher script instead of direct execution
python shared_modules/data_collection/launch_data_collection.py
# NOT: python shared_modules/data_collection/gui_monitor.py

WebSocket Connection Issues 

Problem: WebSocket connection fails or disconnects frequently 

Solution: 

     Check internet connection
     Verify API credentials
     Check rate limiting settings
     Review firewall settings
     Enable debug logging:
     

python

import logging
logging.basicConfig(level=logging.DEBUG)
 
CSV File Issues 

Problem: CSV files are not created or contain invalid data 

Solution: 

     Check write permissions in data directory
     Verify data directory exists
     Check disk space
     Validate data format before writing
     

Performance Issues 

Problem: System is slow or uses excessive memory 

Solution: 

     Reduce batch size in configuration
     Increase delay between requests
     Monitor memory usage with task manager
     Consider reducing number of symbols/timeframes
     

GUI Issues 

Problem: GUI doesn't start or freezes 

Solution: 

     Try running in console mode first
     Check tkinter installation:
     

bash

python -m tkinter

     Verify display settings on Windows
     Check for conflicting applications
     

Configuration Issues 

Problem: Configuration changes don't take effect 

Solution: 

     Verify configuration file syntax
     Check environment variable names
     Restart application after changes
     Validate configuration values
     

📞 Getting Help 
Resources 

     Documentation: Check all .md files in docs/ directory
     Code Comments: Read inline documentation in source files
     Test Files: Review test files for usage examples
     

Debugging Tips 

     Enable Debug Logging: Set logging level to DEBUG
     Use Print Statements: Add temporary print statements for debugging
     Test Components Individually: Run components in isolation
     Check Dependencies: Verify all required packages are installed
     

Common Debug Commands 
bash

# Check Python version
python --version

# Check installed packages
pip list

# Test individual components
python -c "from shared_modules.data_collection.config import DataCollectionConfig; print('OK')"

# Run with verbose output
python main.py --verbose

Remember to always test changes in a development environment before deploying to production! 