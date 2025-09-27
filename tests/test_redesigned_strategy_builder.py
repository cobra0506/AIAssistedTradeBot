"""
Comprehensive Test for Redesigned Strategy Builder
=================================================

This test thoroughly verifies the new, clean API:
1. All indicator operations work correctly
2. All signal rule operations work correctly  
3. Strategy Builder creates functional strategies
4. Integration with existing backtesting system
5. Error handling works properly
6. New API is intuitive and clear

Author: AI Assisted TradeBot Team
Date: 2025
"""

import pandas as pd
import numpy as np
import logging
import sys
import os
from typing import Dict, List, Tuple, Any

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our building block system
from simple_strategy.strategies.indicators_library import *
from simple_strategy.strategies.signals_library import *
from simple_strategy.strategies.strategy_builder import StrategyBuilder

# Import existing system components
from simple_strategy.shared.strategy_base import StrategyBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedesignedStrategyBuilderTest:
    """
    Comprehensive test suite for the redesigned Strategy Builder
    """
    
    def __init__(self):
        self.test_results = []
        self.sample_data = self._create_sample_data()
        
    def _create_sample_data(self) -> Dict[str, pd.DataFrame]:
        """Create sample OHLCV data for testing"""
        np.random.seed(42)  # For reproducible tests
        
        dates = pd.date_range('2023-01-01', periods=100, freq='1min')
        
        # Generate realistic price data
        base_price = 50000
        price_changes = np.random.normal(0, 0.001, 100)
        prices = [base_price]
        
        for change in price_changes[1:]:
            prices.append(prices[-1] * (1 + change))
        
        prices = np.array(prices)
        
        data = pd.DataFrame({
            'timestamp': (dates.astype(np.int64) // 10**9).values,
            'datetime': dates,
            'open': prices * (1 + np.random.normal(0, 0.0005, 100)),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.001, 100))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.001, 100))),
            'close': prices,
            'volume': np.random.randint(100, 1000, 100)
        })
        
        return {
            'BTCUSDT': {'1m': data.set_index('datetime')}
        }
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        logger.info("🧪 Starting comprehensive redesigned Strategy Builder test...")
        
        tests = [
            self.test_indicator_operations,
            self.test_signal_rule_operations,
            self.test_strategy_building,
            self.test_signal_combination_methods,
            self.test_risk_management,
            self.test_error_handling,
            self.test_integration,
            self.test_api_clarity
        ]
        
        results = {}
        for test in tests:
            test_name = test.__name__
            try:
                result = test()
                results[test_name] = result
                status = "✅ PASSED" if result else "❌ FAILED"
                logger.info(f"{status}: {test_name}")
            except Exception as e:
                results[test_name] = False
                logger.error(f"❌ FAILED: {test_name} - {e}")
        
        # Summary
        passed = sum(results.values())
        total = len(results)
        logger.info(f"\n🎯 Test Summary: {passed}/{total} tests passed")
        
        return results
    
    def test_indicator_operations(self) -> bool:
        """Test all indicator operations"""
        logger.info("📊 Testing indicator operations...")
        
        passed_tests = 0
        total_tests = 0
        
        try:
            # Test 1: Add single indicator
            total_tests += 1
            strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
            strategy.add_indicator('rsi', rsi, period=14)
            
            if 'rsi' in strategy.indicators:
                logger.debug("✅ Add single indicator: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Add single indicator: Failed")
            
            # Test 2: Add multiple indicators
            total_tests += 1
            strategy.add_indicator('sma_short', sma, period=20)
            strategy.add_indicator('sma_long', sma, period=50)
            strategy.add_indicator('macd', macd, fast_period=12, slow_period=26)
            
            if len(strategy.indicators) == 4:
                logger.debug("✅ Add multiple indicators: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Add multiple indicators: Failed")
            
            # Test 3: Indicator parameter storage
            total_tests += 1
            rsi_config = strategy.indicators['rsi']
            if (rsi_config['function'] == rsi and 
                rsi_config['params']['period'] == 14):
                logger.debug("✅ Indicator parameter storage: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Indicator parameter storage: Failed")
            
            # Test 4: Overwrite existing indicator
            total_tests += 1
            strategy.add_indicator('rsi', rsi, period=21)  # Different period
            
            if strategy.indicators['rsi']['params']['period'] == 21:
                logger.debug("✅ Overwrite existing indicator: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Overwrite existing indicator: Failed")
            
            # Test 5: Method chaining
            total_tests += 1
            chained_result = (StrategyBuilder(['BTCUSDT'], ['1m'])
                              .add_indicator('rsi', rsi, period=14)
                              .add_indicator('sma', sma, period=20))
            
            if len(chained_result.indicators) == 2:
                logger.debug("✅ Method chaining: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Method chaining: Failed")
            
        except Exception as e:
            logger.error(f"❌ Indicator operations test error: {e}")
        
        logger.info(f"📊 Indicator operations test: {passed_tests}/{total_tests} passed")
        return passed_tests == total_tests
    
    def test_signal_rule_operations(self) -> bool:
        """Test all signal rule operations"""
        logger.info("📈 Testing signal rule operations...")
        
        passed_tests = 0
        total_tests = 0
        
        try:
            # Test 1: Add simple signal rule
            total_tests += 1
            strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
            strategy.add_indicator('rsi', rsi, period=14)
            strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                                   indicator='rsi', overbought=70, oversold=30)
            
            if 'rsi_signal' in strategy.signal_rules:
                logger.debug("✅ Add simple signal rule: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Add simple signal rule: Failed")
            
            # Test 2: Signal rule with multiple indicators
            total_tests += 1
            strategy.add_indicator('sma_short', sma, period=20)
            strategy.add_indicator('sma_long', sma, period=50)
            strategy.add_signal_rule('ma_cross', ma_crossover,
                                   fast_ma='sma_short', slow_ma='sma_long')
            
            if len(strategy.signal_rules) == 2:
                logger.debug("✅ Multiple signal rules: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Multiple signal rules: Failed")
            
            # Test 3: Signal rule parameter separation
            total_tests += 1
            ma_config = strategy.signal_rules['ma_cross']
            indicator_refs = ma_config['indicator_refs']
            signal_params = ma_config['params']
            
            if (len(indicator_refs) == 2 and len(signal_params) == 0 and
                indicator_refs[0] == ('fast_ma', 'sma_short') and
                indicator_refs[1] == ('slow_ma', 'sma_long')):
                logger.debug("✅ Parameter separation: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Parameter separation: Failed")
            
            # Test 4: Error - non-existent indicator
            total_tests += 1
            try:
                strategy.add_signal_rule('bad_signal', overbought_oversold,
                                       indicator='nonexistent', overbought=70, oversold=30)
                logger.error("❌ Should have raised error for non-existent indicator")
            except ValueError:
                logger.debug("✅ Non-existent indicator error: Passed")
                passed_tests += 1
            except Exception:
                logger.error("❌ Wrong exception type for non-existent indicator")
            
            # Test 5: Signal rule method chaining
            total_tests += 1
            chained_result = (StrategyBuilder(['BTCUSDT'], ['1m'])
                              .add_indicator('rsi', rsi, period=14)
                              .add_signal_rule('rsi_signal', overbought_oversold,
                                             indicator='rsi', overbought=70, oversold=30))
            
            if len(chained_result.signal_rules) == 1:
                logger.debug("✅ Signal rule chaining: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Signal rule chaining: Failed")
            
        except Exception as e:
            logger.error(f"❌ Signal rule operations test error: {e}")
        
        logger.info(f"📈 Signal rule operations test: {passed_tests}/{total_tests} passed")
        return passed_tests == total_tests
    
    def test_strategy_building(self) -> bool:
        """Test strategy building functionality"""
        logger.info("🏗️ Testing strategy building...")
        
        passed_tests = 0
        total_tests = 0
        
        try:
            # Test 1: Build simple strategy
            total_tests += 1
            strategy1 = StrategyBuilder(['BTCUSDT'], ['1m'])
            strategy1.add_indicator('rsi', rsi, period=14)
            strategy1.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi', overbought=70, oversold=30)
            strategy1.add_risk_rule('stop_loss', percent=2.0)
            strategy1.set_strategy_info('SimpleRSI', '1.0.0')
            
            built_strategy1 = strategy1.build()
            
            if (isinstance(built_strategy1, StrategyBase) and 
                built_strategy1.strategy_name == 'SimpleRSI'):
                logger.debug("✅ Build simple strategy: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Build simple strategy: Failed")
            
            # Test 2: Build complex strategy
            total_tests += 1
            strategy2 = StrategyBuilder(['BTCUSDT', 'ETHUSDT'], ['1m', '5m'])
            strategy2.add_indicator('rsi', rsi, period=14)
            strategy2.add_indicator('sma_short', sma, period=20)
            strategy2.add_indicator('sma_long', sma, period=50)
            strategy2.add_indicator('macd', macd, fast_period=12, slow_period=26)
            
            strategy2.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi', overbought=70, oversold=30)
            strategy2.add_signal_rule('ma_cross', ma_crossover,
                                   fast_ma='sma_short', slow_ma='sma_long')
            strategy2.add_signal_rule('macd_signal', macd_signals,
                                   macd_line='macd', signal_line='macd')
            
            strategy2.set_signal_combination('majority_vote')
            strategy2.add_risk_rule('stop_loss', percent=1.5)
            strategy2.add_risk_rule('take_profit', percent=3.0)
            strategy2.set_strategy_info('ComplexStrategy', '1.0.0')
            
            built_strategy2 = strategy2.build()
            
            if (isinstance(built_strategy2, StrategyBase) and 
                len(built_strategy2.indicators) == 4 and
                len(built_strategy2.signal_rules) == 3):
                logger.debug("✅ Build complex strategy: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Build complex strategy: Failed")
            
            # Test 3: Strategy signal generation
            total_tests += 1
            signals = built_strategy1.generate_signals(self.sample_data)
            
            if (isinstance(signals, dict) and 
                'BTCUSDT' in signals and 
                '1m' in signals['BTCUSDT'] and
                signals['BTCUSDT']['1m'] in ['BUY', 'SELL', 'HOLD']):
                logger.debug("✅ Strategy signal generation: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Strategy signal generation: Failed")
            
            # Test 4: Strategy info
            total_tests += 1
            info = built_strategy1.get_strategy_info()
            
            if (isinstance(info, dict) and 
                'strategy_name' in info and
                'indicators' in info and
                'signal_rules' in info and
                info['strategy_name'] == 'SimpleRSI'):
                logger.debug("✅ Strategy info: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Strategy info: Failed")
            
            # Test 5: Multi-symbol strategy
            total_tests += 1
            multi_strategy = StrategyBuilder(['BTCUSDT', 'ETHUSDT'], ['1m'])
            multi_strategy.add_indicator('rsi', rsi, period=14)
            multi_strategy.add_signal_rule('rsi_signal', overbought_oversold,
                                        indicator='rsi', overbought=70, oversold=30)
            multi_strategy.set_strategy_info('MultiSymbol', '1.0.0')
            
            built_multi = multi_strategy.build()
            signals = built_multi.generate_signals(self.sample_data)
            
            if (isinstance(signals, dict) and 
                len(signals) == 2 and  # BTCUSDT and ETHUSDT
                all('1m' in symbol_signals for symbol_signals in signals.values())):
                logger.debug("✅ Multi-symbol strategy: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Multi-symbol strategy: Failed")
            
        except Exception as e:
            logger.error(f"❌ Strategy building test error: {e}")
        
        logger.info(f"🏗️ Strategy building test: {passed_tests}/{total_tests} passed")
        return passed_tests == total_tests
    
    def test_signal_combination_methods(self) -> bool:
        """Test signal combination methods"""
        logger.info("🔀 Testing signal combination methods...")
        
        passed_tests = 0
        total_tests = 0
        
        try:
            # Test 1: Majority vote combination
            total_tests += 1
            strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
            strategy.add_indicator('rsi', rsi, period=14)
            strategy.add_indicator('sma_short', sma, period=20)
            strategy.add_indicator('sma_long', sma, period=50)
            
            strategy.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi', overbought=70, oversold=30)
            strategy.add_signal_rule('ma_cross', ma_crossover,
                                   fast_ma='sma_short', slow_ma='sma_long')
            
            strategy.set_signal_combination('majority_vote')
            built_strategy = strategy.build()
            
            if built_strategy.signal_combination == 'majority_vote':
                logger.debug("✅ Majority vote combination: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Majority vote combination: Failed")
            
            # Test 2: Weighted combination
            total_tests += 1
            strategy.set_signal_combination('weighted', weights={
                'rsi_signal': 0.6,
                'ma_cross': 0.4
            })
            built_strategy = strategy.build()
            
            if (built_strategy.signal_combination == 'weighted' and
                built_strategy.signal_weights == {'rsi_signal': 0.6, 'ma_cross': 0.4}):
                logger.debug("✅ Weighted combination: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Weighted combination: Failed")
            
            # Test 3: Unanimous combination
            total_tests += 1
            strategy.set_signal_combination('unanimous')
            built_strategy = strategy.build()
            
            if built_strategy.signal_combination == 'unanimous':
                logger.debug("✅ Unanimous combination: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Unanimous combination: Failed")
            
            # Test 4: Invalid combination method
            total_tests += 1
            try:
                strategy.set_signal_combination('invalid_method')
                logger.error("❌ Should have raised error for invalid method")
            except ValueError:
                logger.debug("✅ Invalid combination method error: Passed")
                passed_tests += 1
            except Exception:
                logger.error("❌ Wrong exception type for invalid method")
            
            # Test 5: Invalid weights
            total_tests += 1
            try:
                strategy.set_signal_combination('weighted', weights={
                    'nonexistent_signal': 1.0
                })
                logger.error("❌ Should have raised error for invalid weights")
            except ValueError:
                logger.debug("✅ Invalid weights error: Passed")
                passed_tests += 1
            except Exception:
                logger.error("❌ Wrong exception type for invalid weights")
            
        except Exception as e:
            logger.error(f"❌ Signal combination test error: {e}")
        
        logger.info(f"🔀 Signal combination test: {passed_tests}/{total_tests} passed")
        return passed_tests == total_tests
    
    def test_risk_management(self) -> bool:
        """Test risk management functionality"""
        logger.info("🛡️ Testing risk management...")
        
        passed_tests = 0
        total_tests = 0
        
        try:
            # Test 1: Add risk rules
            total_tests += 1
            strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
            strategy.add_risk_rule('stop_loss', percent=2.0)
            strategy.add_risk_rule('take_profit', percent=4.0)
            strategy.add_risk_rule('max_position_size', percent=10.0)
            
            if len(strategy.risk_rules) == 3:
                logger.debug("✅ Add risk rules: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Add risk rules: Failed")
            
            # Test 2: Risk rule parameters
            total_tests += 1
            stop_loss_rule = strategy.risk_rules['stop_loss']
            if stop_loss_rule['percent'] == 2.0:
                logger.debug("✅ Risk rule parameters: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Risk rule parameters: Failed")
            
            # Test 3: Position size calculation
            total_tests += 1
            strategy.add_indicator('rsi', rsi, period=14)
            strategy.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi', overbought=70, oversold=30)
            strategy.set_strategy_info('RiskTest', '1.0.0')
            
            built_strategy = strategy.build()
            position_size = built_strategy.calculate_position_size('BTCUSDT', 'BUY', 50000.0, 10000.0)
            
            if isinstance(position_size, (int, float)) and position_size > 0:
                logger.debug("✅ Position size calculation: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Position size calculation: Failed")
            
            # Test 4: Stop loss/take profit calculation
            total_tests += 1
            sl, tp = built_strategy.get_stop_loss_take_profit('BTCUSDT', 'BUY', 50000.0)
            
            if (isinstance(sl, (int, float)) and isinstance(tp, (int, float)) and 
                sl < tp and sl < 50000.0 and tp > 50000.0):
                logger.debug("✅ Stop loss/take profit calculation: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Stop loss/take profit calculation: Failed")
            
            # Test 5: Risk rule chaining
            total_tests += 1
            chained_result = (StrategyBuilder(['BTCUSDT'], ['1m'])
                              .add_risk_rule('stop_loss', percent=2.0)
                              .add_risk_rule('take_profit', percent=4.0))
            
            if len(chained_result.risk_rules) == 2:
                logger.debug("✅ Risk rule chaining: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Risk rule chaining: Failed")
            
        except Exception as e:
            logger.error(f"❌ Risk management test error: {e}")
        
        logger.info(f"🛡️ Risk management test: {passed_tests}/{total_tests} passed")
        return passed_tests == total_tests
    
    def test_error_handling(self) -> bool:
        """Test error handling"""
        logger.info("🛡️ Testing error handling...")
        
        passed_tests = 0
        total_tests = 0
        
        try:
            # Test 1: Build strategy without indicators
            total_tests += 1
            try:
                strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
                strategy.add_signal_rule('rsi_signal', overbought_oversold,
                                       indicator='rsi', overbought=70, oversold=30)
                strategy.build()  # Should fail
                logger.error("❌ Should have raised error for missing indicators")
            except ValueError:
                logger.debug("✅ Missing indicators error: Passed")
                passed_tests += 1
            except Exception:
                logger.error("❌ Wrong exception type for missing indicators")
            
            # Test 2: Build strategy without signal rules
            total_tests += 1
            try:
                strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
                strategy.add_indicator('rsi', rsi, period=14)
                strategy.build()  # Should fail
                logger.error("❌ Should have raised error for missing signal rules")
            except ValueError:
                logger.debug("✅ Missing signal rules error: Passed")
                passed_tests += 1
            except Exception:
                logger.error("❌ Wrong exception type for missing signal rules")
            
            # Test 3: Reference non-existent indicator
            total_tests += 1
            try:
                strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
                strategy.add_indicator('rsi', rsi, period=14)
                strategy.add_signal_rule('bad_signal', overbought_oversold,
                                       indicator='nonexistent', overbought=70, oversold=30)
                strategy.build()  # Should fail
                logger.error("❌ Should have raised error for non-existent indicator")
            except ValueError:
                logger.debug("✅ Non-existent indicator error: Passed")
                passed_tests += 1
            except Exception:
                logger.error("❌ Wrong exception type for non-existent indicator")
            
            # Test 4: Invalid signal combination method
            total_tests += 1
            try:
                strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
                strategy.add_indicator('rsi', rsi, period=14)
                strategy.add_signal_rule('rsi_signal', overbought_oversold,
                                       indicator='rsi', overbought=70, oversold=30)
                strategy.set_signal_combination('invalid_method')
                strategy.build()  # Should fail
                logger.error("❌ Should have raised error for invalid combination method")
            except ValueError:
                logger.debug("✅ Invalid combination method error: Passed")
                passed_tests += 1
            except Exception:
                logger.error("❌ Wrong exception type for invalid combination method")
            
            # Test 5: Invalid weights
            total_tests += 1
            try:
                strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
                strategy.add_indicator('rsi', rsi, period=14)
                strategy.add_signal_rule('rsi_signal', overbought_oversold,
                                       indicator='rsi', overbought=70, oversold=30)
                strategy.set_signal_combination('weighted', weights={
                    'nonexistent_signal': 1.0
                })
                strategy.build()  # Should fail
                logger.error("❌ Should have raised error for invalid weights")
            except ValueError:
                logger.debug("✅ Invalid weights error: Passed")
                passed_tests += 1
            except Exception:
                logger.error("❌ Wrong exception type for invalid weights")
            
        except Exception as e:
            logger.error(f"❌ Error handling test error: {e}")
        
        logger.info(f"🛡️ Error handling test: {passed_tests}/{total_tests} passed")
        return passed_tests == total_tests
    
    def test_integration(self) -> bool:
        """Test integration with existing backtesting system"""
        logger.info("🔗 Testing integration...")
        
        passed_tests = 0
        total_tests = 0
        
        try:
            # Test 1: Strategy inherits from StrategyBase
            total_tests += 1
            strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
            strategy.add_indicator('rsi', rsi, period=14)
            strategy.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi', overbought=70, oversold=30)
            strategy.add_risk_rule('stop_loss', percent=2.0)
            strategy.set_strategy_info('IntegrationTest', '1.0.0')
            
            test_strategy = strategy.build()
            
            if isinstance(test_strategy, StrategyBase):
                logger.debug("✅ StrategyBase inheritance: Passed")
                passed_tests += 1
            else:
                logger.error("❌ StrategyBase inheritance: Failed")
            
            # Test 2: Required methods exist
            total_tests += 1
            required_methods = ['generate_signals', 'calculate_position_size', 'get_stop_loss_take_profit', 'get_strategy_info']
            if all(hasattr(test_strategy, method) for method in required_methods):
                logger.debug("✅ Required methods: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Required methods: Failed")
            
            # Test 3: Strategy works with sample data
            total_tests += 1
            signals = test_strategy.generate_signals(self.sample_data)
            
            if (isinstance(signals, dict) and 
                'BTCUSDT' in signals and 
                '1m' in signals['BTCUSDT'] and
                signals['BTCUSDT']['1m'] in ['BUY', 'SELL', 'HOLD']):
                logger.debug("✅ Strategy works with sample data: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Strategy works with sample data: Failed")
            
            # Test 4: Multi-timeframe support
            total_tests += 1
            multi_tf_strategy = StrategyBuilder(['BTCUSDT'], ['1m', '5m'])
            multi_tf_strategy.add_indicator('rsi', rsi, period=14)
            multi_tf_strategy.add_signal_rule('rsi_signal', overbought_oversold,
                                          indicator='rsi', overbought=70, oversold=30)
            multi_tf_strategy.set_strategy_info('MultiTimeframeTest', '1.0.0')
            
            built_multi_tf = multi_tf_strategy.build()
            
            if built_multi_tf.timeframes == ['1m', '5m']:
                logger.debug("✅ Multi-timeframe support: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Multi-timeframe support: Failed")
            
            # Test 5: Strategy info completeness
            total_tests += 1
            info = test_strategy.get_strategy_info()
            
            required_keys = ['strategy_name', 'version', 'symbols', 'timeframes', 'indicators', 'signal_rules']
            if all(key in info for key in required_keys):
                logger.debug("✅ Strategy info completeness: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Strategy info completeness: Failed")
            
        except Exception as e:
            logger.error(f"❌ Integration test error: {e}")
        
        logger.info(f"🔗 Integration test: {passed_tests}/{total_tests} passed")
        return passed_tests == total_tests
    
    def test_api_clarity(self) -> bool:
        """Test that the new API is clear and intuitive"""
        logger.info("📝 Testing API clarity...")
        
        passed_tests = 0
        total_tests = 0
        
        try:
            # Test 1: Clear method names
            total_tests += 1
            strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
            
            # Check that all method names are clear and descriptive
            method_names = [method for method in dir(strategy) if not method.startswith('_')]
            clear_methods = ['add_indicator', 'add_signal_rule', 'add_risk_rule', 
                            'set_signal_combination', 'set_strategy_info', 'build']
            
            if all(method in method_names for method in clear_methods):
                logger.debug("✅ Clear method names: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Clear method names: Failed")
            
            # Test 2: Intuitive parameter names
            total_tests += 1
            # Add an indicator and check that parameters are stored with clear names
            strategy.add_indicator('rsi', rsi, period=14)
            
            if 'period' in strategy.indicators['rsi']['params']:
                logger.debug("✅ Intuitive parameter names: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Intuitive parameter names: Failed")
            
            # Test 3: Clear indicator references
            total_tests += 1
            strategy.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi', overbought=70, oversold=30)
            
            signal_config = strategy.signal_rules['rsi_signal']
            indicator_refs = signal_config['indicator_refs']
            
            if indicator_refs == [('indicator', 'rsi')]:
                logger.debug("✅ Clear indicator references: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Clear indicator references: Failed")
            
            # Test 4: Separation of concerns
            total_tests += 1
            # Indicators and signal parameters should be clearly separated
            signal_params = signal_config['params']
            
            if ('overbought' in signal_params and 'oversold' in signal_params and
                'indicator' not in signal_params):
                logger.debug("✅ Separation of concerns: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Separation of concerns: Failed")
            
            # Test 5: Method chaining works
            total_tests += 1
            chained_strategy = (StrategyBuilder(['BTCUSDT'], ['1m'])
                               .add_indicator('rsi', rsi, period=14)
                               .add_signal_rule('rsi_signal', overbought_oversold,
                                              indicator='rsi', overbought=70, oversold=30)
                               .add_risk_rule('stop_loss', percent=2.0)
                               .set_strategy_info('ChainedTest', '1.0.0'))
            
            if (len(chained_strategy.indicators) == 1 and
                len(chained_strategy.signal_rules) == 1 and
                len(chained_strategy.risk_rules) == 1 and
                chained_strategy.strategy_name == 'ChainedTest'):
                logger.debug("✅ Method chaining works: Passed")
                passed_tests += 1
            else:
                logger.error("❌ Method chaining works: Failed")
            
        except Exception as e:
            logger.error(f"❌ API clarity test error: {e}")
        
        logger.info(f"📝 API clarity test: {passed_tests}/{total_tests} passed")
        return passed_tests == total_tests


def main():
    """Main test runner"""
    print("🧪 Redesigned Strategy Builder - Comprehensive Test")
    print("=" * 60)
    
    # Run tests
    test_runner = RedesignedStrategyBuilderTest()
    results = test_runner.run_all_tests()
    
    # Print final results
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS:")
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n📊 Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Redesigned Strategy Builder is working perfectly!")
        print("🚀 The new API is clear, intuitive, and robust!")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)