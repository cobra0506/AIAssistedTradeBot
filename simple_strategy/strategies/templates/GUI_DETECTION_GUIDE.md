# GUI Strategy Detection Guide

## How the GUI Detects and Loads Strategies

### Automatic Discovery Process
The GUI automatically discovers strategies using the following logic:

1. **File Pattern Matching**: Scans for files starting with `Strategy_` and ending with `.py`
   - Example: `Strategy_MyStrategy.py` ✅ Will be detected
   - Example: `my_strategy.py` ❌ Will NOT be detected
   - Example: `strategy_builder.py` ❌ Explicitly filtered out

2. **Dynamic Import**: Each matching file is dynamically imported as a Python module

3. **Interface Check**: The GUI looks for these required components:
   - `create_strategy` function (required)
   - `STRATEGY_PARAMETERS` dictionary (optional but recommended)

### Required Strategy Structure

```python
# Your strategy file MUST have:
def create_strategy(symbols=None, timeframes=None, **params):
    # Your strategy creation logic here
    return built_strategy

# Optional but HIGHLY recommended:
STRATEGY_PARAMETERS = {
    'param_name': {
        'type': 'int|str|float',
        'default': value,
        'min': value,           # For numeric types
        'max': value,           # For numeric types
        'options': [list],      # For string types with choices
        'description': 'Human readable description',
        'gui_hint': 'Additional help text for GUI'
    }
}
 
 
 
GUI Integration Flow 

     Discovery: GUI scans simple_strategy/strategies/ directory
     Loading: Each Strategy_*.py file is imported
     Validation: Checks for create_strategy function
     Parameter Extraction: Reads STRATEGY_PARAMETERS for GUI controls
     Instance Creation: Calls create_strategy() when user runs the strategy
     

Best Practices 

     Naming Convention: Always start strategy files with Strategy_
     Parameter Placement: Put STRATEGY_PARAMETERS at the top of the file
     Error Handling: Include try/catch blocks in create_strategy
     Logging: Use logging for debugging and troubleshooting
     Defaults: Always provide sensible defaults for all parameters
     

Troubleshooting 

Strategy not appearing in GUI? 

     Check filename starts with Strategy_
     Verify file is in simple_strategy/strategies/ directory
     Ensure create_strategy function exists
     Check for Python syntax errors
     

Parameters not showing in GUI? 

     Verify STRATEGY_PARAMETERS dictionary exists
     Check parameter structure matches the expected format
     Ensure no syntax errors in the parameters dict
     