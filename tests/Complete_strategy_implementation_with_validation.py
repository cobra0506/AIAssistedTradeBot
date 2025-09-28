import sys
import os
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import strategy functions
from simple_strategy.strategies.Strategy_1_Trend_Following import create_trend_following_strategy
from simple_strategy.strategies.Strategy_2_mean_reversion import create_mean_reversion_strategy
from simple_strategy.strategies.Strategy_3_Multi_Indicator import create_multi_indicator_strategy

# Import other required modules
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.backtester.backtester_engine import BacktesterEngine

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

class StrategyImplementationSuite:
    """Complete implementation and validation suite for trading strategies"""
    
    def __init__(self):
        self.strategies = {}
        self.results = {}
        self.validations = {}
    
    def implement_all_strategies(self):
        """Implement all three strategies with different configurations"""
        
        # Strategy 1: Trend Following (Multiple configurations)
        self.strategies['trend_following_conservative'] = create_trend_following_strategy(
            symbols=['BTCUSDT'], 
            timeframes=['4h']  # Longer timeframe for conservative approach
        )
        
        self.strategies['trend_following_aggressive'] = create_trend_following_strategy(
            symbols=['BTCUSDT', 'ETHUSDT'], 
            timeframes=['1h', '2h']  # Shorter timeframes for aggressive approach
        )
        
        # Strategy 2: Mean Reversion (Multiple configurations)
        self.strategies['mean_reversion_standard'] = create_mean_reversion_strategy(
            symbols=['BTCUSDT'], 
            timeframes=['1h']
        )
        
        self.strategies['mean_reversion_multi'] = create_mean_reversion_strategy(
            symbols=['BTCUSDT', 'ETHUSDT', 'SOLUSDT'], 
            timeframes=['1h', '2h']
        )
        
        # Strategy 3: Multi-Indicator (Multiple configurations)
        self.strategies['multi_indicator_balanced'] = create_multi_indicator_strategy(
            symbols=['BTCUSDT'], 
            timeframes=['1h', '4h']
        )
        
        self.strategies['multi_indicator_portfolio'] = create_multi_indicator_strategy(
            symbols=['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT'], 
            timeframes=['1h', '2h', '4h']
        )
        
        return self.strategies
    
    def run_comprehensive_backtests(self, start_date='2023-01-01', end_date='2023-12-31'):
        """Run comprehensive backtests for all strategies"""
        
        for strategy_name, strategy in self.strategies.items():
            print(f"Running backtest for {strategy_name}...")
            
            backtest = BacktesterEngine(
                strategy=strategy,
                start_date=start_date,
                end_date=end_date,
                initial_capital=10000
            )
            
            results = backtest.run()
            self.results[strategy_name] = results
            
            print(f"Completed: Total Return = {results['total_return']:.2f}%, Sharpe = {results['sharpe_ratio']:.2f}")
        
        return self.results
    
    def validate_all_strategies(self, market_data):
        """Validate all strategies for realistic performance"""
        validator = StrategyPerformanceValidator()
        
        for strategy_name, results in self.results.items():
            print(f"Validating {strategy_name}...")
            
            validation_report = validator.validate_backtest_realism(results, market_data)
            self.validations[strategy_name] = validation_report
            
            grade = calculate_performance_grade(results, validation_report)
            print(f"Validation Grade: {grade}")
        
        return self.validations
    
    def generate_performance_report(self):
        """Generate comprehensive performance comparison report"""
        report = {
            'summary': {},
            'detailed_analysis': {},
            'recommendations': {}
        }
        
        # Summary statistics
        for strategy_name, results in self.results.items():
            report['summary'][strategy_name] = {
                'total_return': f"{results['total_return']:.2f}%",
                'sharpe_ratio': f"{results['sharpe_ratio']:.2f}",
                'max_drawdown': f"{results['max_drawdown']:.2f}%",
                'win_rate': f"{results['win_rate']:.2f}%",
                'total_trades': results['total_trades'],
                'grade': calculate_performance_grade(results, self.validations.get(strategy_name, {}))
            }
        
        # Detailed analysis
        best_return = max(self.results.items(), key=lambda x: x[1]['total_return'])
        best_sharpe = max(self.results.items(), key=lambda x: x[1]['sharpe_ratio'])
        lowest_drawdown = min(self.results.items(), key=lambda x: x[1]['max_drawdown'])
        
        report['detailed_analysis'] = {
            'best_total_return': {'strategy': best_return[0], 'value': f"{best_return[1]['total_return']:.2f}%"},
            'best_sharpe_ratio': {'strategy': best_sharpe[0], 'value': f"{best_sharpe[1]['sharpe_ratio']:.2f}"},
            'lowest_max_drawdown': {'strategy': lowest_drawdown[0], 'value': f"{lowest_drawdown[1]['max_drawdown']:.2f}%"}
        }
        
        # Recommendations
        report['recommendations'] = self._generate_recommendations()
        
        return report
    
    def _generate_recommendations(self):
        """Generate recommendations based on performance analysis"""
        recommendations = []
        
        # Analyze performance patterns
        for strategy_name, results in self.results.items():
            if results['sharpe_ratio'] > 1.5 and results['max_drawdown'] < 0.2:
                recommendations.append(f"{strategy_name}: Excellent risk-adjusted returns, suitable for live trading")
            elif results['total_return'] > 0.3 and results['max_drawdown'] < 0.3:
                recommendations.append(f"{strategy_name}: Good returns with acceptable risk, consider for paper trading")
            elif results['win_rate'] > 0.6:
                recommendations.append(f"{strategy_name}: High win rate, good for confidence building")
            else:
                recommendations.append(f"{strategy_name}: Needs optimization before live deployment")
        
        return recommendations

def run_strategy_tests():
    """Run all strategy tests"""
    print("🚀 Starting AI Assisted TradeBot Strategy Development")
    print("=" * 60)
    
    # Step 1: Implement all strategies
    print("📋 Step 1: Implementing Strategies...")
    suite = StrategyImplementationSuite()
    strategies = suite.implement_all_strategies()
    print(f"✅ Implemented {len(strategies)} strategy configurations")
    
    # Step 2: Run tests
    print("\n🧪 Step 2: Running Strategy Tests...")
    test_success = run_simple_tests()
    print(f"✅ Tests {'PASSED' if test_success else 'FAILED'}")
    
    # Step 3: Run backtests
    print("\n📊 Step 3: Running Comprehensive Backtests...")
    results = suite.run_comprehensive_backtests()
    print(f"✅ Completed backtests for {len(results)} strategies")
    
    # Step 4: Validate performance
    print("\n🔍 Step 4: Validating Performance Realism...")
    # Note: In real implementation, you would load actual market data here
    # For now, we'll use placeholder validation
    validations = suite.validate_all_strategies(market_data=None)
    print(f"✅ Completed validation for {len(validations)} strategies")
    
    # Step 5: Generate report
    print("\n📈 Step 5: Generating Performance Report...")
    report = suite.generate_performance_report()
    
    # Display summary
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 60)
    
    for strategy_name, summary in report['summary'].items():
        print(f"\n{strategy_name}:")
        print(f"  Total Return: {summary['total_return']}")
        print(f"  Sharpe Ratio: {summary['sharpe_ratio']}")
        print(f"  Max Drawdown: {summary['max_drawdown']}")
        print(f"  Win Rate: {summary['win_rate']}")
        print(f"  Total Trades: {summary['total_trades']}")
        print(f"  Grade: {summary['grade']}")
    
    print("\n" + "=" * 60)
    print("🎯 RECOMMENDATIONS")
    print("=" * 60)
    
    for rec in report['recommendations']:
        print(f"• {rec}")
    
    print("\n✅ Strategy Development and Validation Complete!")
    return suite, report

def run_simple_tests():
    """Run simple tests to verify everything works"""
    print("🚀 Running Simple Strategy Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(SimpleStrategyTest('test_trend_following_strategy'))
    suite.addTest(SimpleStrategyTest('test_mean_reversion_strategy'))
    suite.addTest(SimpleStrategyTest('test_multi_indicator_strategy'))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
    
    return result.wasSuccessful()

class SimpleStrategyTest(unittest.TestCase):
    """Simple test class to verify strategies work"""
    
    def setUp(self):
        """Set up test data"""
        self.test_data = self.generate_test_data()
        self.start_date = '2023-01-01'
        self.end_date = '2023-12-31'
        self.initial_capital = 10000
    
    def generate_test_data(self):
        """Generate simple test data"""
        dates = pd.date_range(start='2023-01-01', end='2023-03-31', freq='1h')
        n_periods = len(dates)
        
        np.random.seed(42)
        returns = np.random.normal(0.0001, 0.02, n_periods)
        price = 100 * np.exp(np.cumsum(returns))
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': price * (1 + np.random.normal(0, 0.001, n_periods)),
            'high': price * (1 + abs(np.random.normal(0, 0.005, n_periods))),
            'low': price * (1 - abs(np.random.normal(0, 0.005, n_periods))),
            'close': price,
            'volume': np.random.lognormal(10, 1, n_periods)
        })
        
        return data
    
    def test_trend_following_strategy(self):
        """Test trend following strategy"""
        print("Testing Trend Following Strategy...")
        
        try:
            strategy = create_trend_following_strategy()
            print("✅ Strategy created successfully")
            
            # Test basic properties
            self.assertIsNotNone(strategy)
            print("✅ Strategy is not None")
            
            # Test with backtest engine
            backtest = BacktesterEngine(
                strategy=strategy,
                start_date=self.start_date,
                end_date=self.end_date,
                initial_capital=self.initial_capital
            )
            
            results = backtest.run()
            print(f"✅ Backtest completed: {results.get('total_return', 'N/A')}% return")
            
        except Exception as e:
            print(f"❌ Error in trend following strategy: {e}")
            self.fail(f"Trend following strategy failed: {e}")
    
    def test_mean_reversion_strategy(self):
        """Test mean reversion strategy"""
        print("Testing Mean Reversion Strategy...")
        
        try:
            strategy = create_mean_reversion_strategy()
            print("✅ Strategy created successfully")
            
            # Test basic properties
            self.assertIsNotNone(strategy)
            print("✅ Strategy is not None")
            
            # Test with backtest engine
            backtest = BacktesterEngine(
                strategy=strategy,
                start_date=self.start_date,
                end_date=self.end_date,
                initial_capital=self.initial_capital
            )
            
            results = backtest.run()
            print(f"✅ Backtest completed: {results.get('total_return', 'N/A')}% return")
            
        except Exception as e:
            print(f"❌ Error in mean reversion strategy: {e}")
            self.fail(f"Mean reversion strategy failed: {e}")
    
    def test_multi_indicator_strategy(self):
        """Test multi indicator strategy"""
        print("Testing Multi Indicator Strategy...")
        
        try:
            strategy = create_multi_indicator_strategy()
            print("✅ Strategy created successfully")
            
            # Test basic properties
            self.assertIsNotNone(strategy)
            print("✅ Strategy is not None")
            
            # Test with backtest engine
            backtest = BacktesterEngine(
                strategy=strategy,
                start_date=self.start_date,
                end_date=self.end_date,
                initial_capital=self.initial_capital
            )
            
            results = backtest.run()
            print(f"✅ Backtest completed: {results.get('total_return', 'N/A')}% return")
            
        except Exception as e:
            print(f"❌ Error in multi indicator strategy: {e}")
            self.fail(f"Multi indicator strategy failed: {e}")

# Main execution function
def main():
    """Main execution function for strategy development and validation"""
    return run_strategy_tests()

# Execute the main function
if __name__ == "__main__":
    strategy_suite, performance_report = main()