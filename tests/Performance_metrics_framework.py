import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import strategy functions
from simple_strategy.strategies.Strategy_1_Trend_Following import create_trend_following_strategy
from simple_strategy.strategies.Strategy_2_mean_reversion import create_mean_reversion_strategy
from simple_strategy.strategies.Strategy_3_Multi_Indicator import create_multi_indicator_strategy

# Import other required modules
from simple_strategy.backtester.backtester_engine import BacktestEngine

class StrategyPerformanceValidator:
    """Comprehensive performance validation for trading strategies"""
    
    def __init__(self):
        self.metrics = {
            'returns': ['total_return', 'annualized_return', 'monthly_returns'],
            'risk': ['sharpe_ratio', 'sortino_ratio', 'max_drawdown', 'var_95', 'cvar'],
            'trading': ['win_rate', 'profit_factor', 'avg_win_loss_ratio', 'total_trades'],
            'stability': ['calmar_ratio', 'stability_score', 'consistency_metric']
        }
    
    def validate_backtest_realism(self, results, market_data):
        """
        Validate that backtest results reflect realistic trading conditions
        """
        validation_report = {}
        
        # 1. Transaction Costs Validation
        validation_report['transaction_costs'] = self._validate_transaction_costs(results)
        
        # 2. Slippage Validation  
        validation_report['slippage'] = self._validate_slippage(results, market_data)
        
        # 3. Market Impact Validation
        validation_report['market_impact'] = self._validate_market_impact(results)
        
        # 4. Liquidity Validation
        validation_report['liquidity'] = self._validate_liquidity(results, market_data)
        
        # 5. Realistic Returns Validation
        validation_report['realistic_returns'] = self._validate_realistic_returns(results)
        
        return validation_report
    
    def _validate_transaction_costs(self, results):
        """Validate transaction costs are properly accounted for"""
        total_trades = results.get('total_trades', 0)
        if total_trades == 0:
            return {'status': 'warning', 'message': 'No trades executed'}
        
        # Estimate transaction costs (0.1% per trade typical for crypto)
        estimated_costs = total_trades * 0.001  # 0.1% per trade
        return {'status': 'info', 'estimated_costs': estimated_costs, 'trades': total_trades}
    
    def _validate_slippage(self, results, market_data):
        """Validate slippage assumptions are realistic"""
        avg_trade_size = results.get('avg_trade_size', 0)
        volatility = market_data['close'].pct_change().std()
        
        # Slippage typically 0.05% - 0.3% for crypto
        expected_slippage = min(0.003, max(0.0005, volatility * 0.5))
        
        return {
            'status': 'info',
            'expected_slippage_pct': expected_slippage,
            'avg_volatility': volatility,
            'avg_trade_size': avg_trade_size
        }
    
    def _validate_market_impact(self, results):
        """Validate market impact considerations"""
        position_size = results.get('max_position_size', 0)
        avg_volume = results.get('avg_daily_volume', 1)
        
        if avg_volume > 0:
            impact_ratio = position_size / avg_volume
            if impact_ratio > 0.01:  # > 1% of daily volume
                return {'status': 'warning', 'impact_ratio': impact_ratio, 'message': 'High market impact risk'}
        
        return {'status': 'ok', 'impact_ratio': 'low'}
    
    def _validate_liquidity(self, results, market_data):
        """Validate liquidity assumptions"""
        avg_volume = market_data['volume'].mean()
        min_volume = market_data['volume'].min()
        
        liquidity_score = 'high' if avg_volume > 1e6 else 'medium' if avg_volume > 1e5 else 'low'
        
        return {
            'status': 'info',
            'liquidity_score': liquidity_score,
            'avg_daily_volume': avg_volume,
            'min_daily_volume': min_volume
        }
    
    def _validate_realistic_returns(self, results):
        """Validate returns are realistic for crypto trading"""
        total_return = results.get('total_return', 0)
        sharpe_ratio = results.get('sharpe_ratio', 0)
        
        # Realistic expectations for crypto strategies
        realistic_annual_return = (-0.5, 2.0)  # -50% to +200% annual
        realistic_sharpe = (0.5, 3.0)  # 0.5 to 3.0
        
        warnings = []
        if total_return > realistic_annual_return[1]:
            warnings.append("Returns seem unusually high")
        if total_return < realistic_annual_return[0]:
            warnings.append("Returns seem unusually low")
        if sharpe_ratio > realistic_sharpe[1]:
            warnings.append("Sharpe ratio seems unusually high")
        
        return {
            'status': 'warning' if warnings else 'ok',
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'warnings': warnings
        }

def run_performance_validation(strategy, market_data, start_date, end_date, initial_capital=10000):
    """
    Run comprehensive performance validation for a strategy
    """
    from simple_strategy.backtester.backtester_engine import BacktestEngine
    
    # Run backtest
    backtest = BacktestEngine(
        strategy=strategy,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )
    results = backtest.run()
    
    # Validate performance
    validator = StrategyPerformanceValidator()
    validation_report = validator.validate_backtest_realism(results, market_data)
    
    return {
        'backtest_results': results,
        'validation_report': validation_report,
        'performance_grade': calculate_performance_grade(results, validation_report)
    }

def calculate_performance_grade(results, validation_report):
    """Calculate overall performance grade"""
    score = 0
    max_score = 100
    
    # Returns score (40 points)
    total_return = results.get('total_return', 0)
    if total_return > 0.5:  # > 50% return
        score += 40
    elif total_return > 0.2:  # > 20% return
        score += 30
    elif total_return > 0:  # Positive return
        score += 20
    else:
        score += 10
    
    # Risk-adjusted returns (30 points)
    sharpe_ratio = results.get('sharpe_ratio', 0)
    if sharpe_ratio > 2.0:
        score += 30
    elif sharpe_ratio > 1.5:
        score += 25
    elif sharpe_ratio > 1.0:
        score += 20
    elif sharpe_ratio > 0.5:
        score += 15
    else:
        score += 5
    
    # Risk management (20 points)
    max_drawdown = results.get('max_drawdown', 1)
    if max_drawdown < 0.1:  # < 10% drawdown
        score += 20
    elif max_drawdown < 0.2:  # < 20% drawdown
        score += 15
    elif max_drawdown < 0.3:  # < 30% drawdown
        score += 10
    else:
        score += 5
    
    # Validation checks (10 points)
    validation_issues = sum(1 for report in validation_report.values() 
                          if report.get('status') == 'warning')
    score += max(0, 10 - validation_issues * 2)
    
    # Convert to letter grade
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    else:
        return 'D'