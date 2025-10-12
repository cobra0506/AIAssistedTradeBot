"""
Integration Tests for Indicators + Signals + Strategy Builder
Tests the complete workflow from indicators to trading signals
Author: AI Assisted TradeBot Team
Date: 2025
"""

import unittest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, sma, ema, macd, bollinger_bands, stochastic
from simple_strategy.strategies.signals_library import overbought_oversold, ma_crossover, macd_signals, bollinger_bands_signals

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete strategy workflow"""
    
    def setUp(self):
        """Set up test data"""
        np.random.seed(42)
        self.dates = pd.date_range('2023-01-01', periods=100, freq='D')
        
        # Create realistic price data
        base_price = 20000
        self.prices = pd.Series([
            base_price + i * 10 + np.random.normal(0, 50) 
            for i in range(100)
        ], index=self.dates, name='close')
        
        # Create OHLCV data
        self.data = pd.DataFrame({
            'open': self.prices + np.random.normal(0, 10, 100),
            'high': self.prices + abs(np.random.normal(20, 10, 100)),
            'low': self.prices - abs(np.random.normal(20, 10, 100)),
            'close': self.prices,
            'volume': np.random.uniform(1000, 10000, 100)
        }, index=self.dates)

    def test_rsi_overbought_oversold_integration(self):
        """Test RSI indicator with overbought/oversold signals"""
        print("\n🔗 Testing RSI + Overbought/Oversold integration...")
        
        # Create strategy with RSI and overbought/oversold signals
        strategy = StrategyBuilder(['BTCUSDT'], ['1D'])
        strategy.add_indicator('rsi', rsi, period=14)
        strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                               indicator='rsi', overbought=70, oversold=30)
        
        # Build strategy
        built_strategy = strategy.build()
        
        # Test signal generation
        signals = built_strategy.generate_signals(self.data)
        
        # Verify signals are generated
        self.assertIsNotNone(signals, "Should generate signals")
        self.assertTrue(len(signals) > 0, "Should generate non-empty signals")
        
        # Verify signal values
        unique_signals = set(signals['signal'].dropna())
        self.assertIn('BUY', unique_signals, "Should generate BUY signals")
        self.assertIn('SELL', unique_signals, "Should generate SELL signals")
        self.assertIn('HOLD', unique_signals, "Should generate HOLD signals")
        
        print("✅ RSI + Overbought/Oversold integration test passed")

    def test_ma_crossover_integration(self):
        """Test Moving Average crossover integration"""
        print("\n🔗 Testing MA Crossover integration...")
        
        # Create strategy with MA crossover
        strategy = StrategyBuilder(['BTCUSDT'], ['1D'])
        strategy.add_indicator('sma_fast', sma, period=10)
        strategy.add_indicator('sma_slow', sma, period=20)
        strategy.add_signal_rule('ma_cross', ma_crossover, 
                               fast_ma='sma_fast', slow_ma='sma_slow')
        
        # Build strategy
        built_strategy = strategy.build()
        
        # Test signal generation
        signals = built_strategy.generate_signals(self.data)
        
        # Verify signals are generated
        self.assertIsNotNone(signals, "Should generate signals")
        self.assertTrue(len(signals) > 0, "Should generate non-empty signals")
        
        # Verify signal values
        unique_signals = set(signals['signal'].dropna())
        self.assertIn('BUY', unique_signals, "Should generate BUY signals")
        self.assertIn('SELL', unique_signals, "Should generate SELL signals")
        self.assertIn('HOLD', unique_signals, "Should generate HOLD signals")
        
        print("✅ MA Crossover integration test passed")

    def test_macd_integration(self):
        """Test MACD integration"""
        print("\n🔗 Testing MACD integration...")
        
        # Create strategy with MACD
        strategy = StrategyBuilder(['BTCUSDT'], ['1D'])
        strategy.add_indicator('macd_line', macd, fast_period=12, slow_period=26, signal_period=9)
        strategy.add_signal_rule('macd_signal', macd_signals, 
                               macd_line='macd_line', signal_line='signal_line')
        
        # Build strategy
        built_strategy = strategy.build()
        
        # Test signal generation
        signals = built_strategy.generate_signals(self.data)
        
        # Verify signals are generated
        self.assertIsNotNone(signals, "Should generate signals")
        self.assertTrue(len(signals) > 0, "Should generate non-empty signals")
        
        print("✅ MACD integration test passed")

    def test_bollinger_bands_integration(self):
        """Test Bollinger Bands integration"""
        print("\n🔗 Testing Bollinger Bands integration...")
        
        # Create strategy with Bollinger Bands
        strategy = StrategyBuilder(['BTCUSDT'], ['1D'])
        strategy.add_indicator('bb', bollinger_bands, period=20, std_dev=2)
        strategy.add_signal_rule('bb_signal', bollinger_bands_signals, 
                               price='close', upper_band='upper_band', lower_band='lower_band')
        
        # Build strategy
        built_strategy = strategy.build()
        
        # Test signal generation
        signals = built_strategy.generate_signals(self.data)
        
        # Verify signals are generated
        self.assertIsNotNone(signals, "Should generate signals")
        self.assertTrue(len(signals) > 0, "Should generate non-empty signals")
        
        print("✅ Bollinger Bands integration test passed")

    def test_multi_indicator_strategy(self):
        """Test strategy with multiple indicators"""
        print("\n🔗 Testing multi-indicator strategy...")
        
        # Create strategy with multiple indicators
        strategy = StrategyBuilder(['BTCUSDT'], ['1D'])
        strategy.add_indicator('rsi', rsi, period=14)
        strategy.add_indicator('sma_fast', sma, period=10)
        strategy.add_indicator('sma_slow', sma, period=20)
        
        strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                               indicator='rsi', overbought=70, oversold=30)
        strategy.add_signal_rule('ma_cross', ma_crossover, 
                               fast_ma='sma_fast', slow_ma='sma_slow')
        
        # Set majority vote for signal combination
        strategy.set_signal_combination('majority_vote')
        
        # Build strategy
        built_strategy = strategy.build()
        
        # Test signal generation
        signals = built_strategy.generate_signals(self.data)
        
        # Verify signals are generated
        self.assertIsNotNone(signals, "Should generate signals")
        self.assertTrue(len(signals) > 0, "Should generate non-empty signals")
        
        print("✅ Multi-indicator strategy test passed")

    def test_strategy_builder_validation(self):
        """Test Strategy Builder validation"""
        print("\n🔗 Testing Strategy Builder validation...")
        
        # Test with invalid indicator reference
        strategy = StrategyBuilder(['BTCUSDT'], ['1D'])
        strategy.add_signal_rule('invalid_signal', overbought_oversold, 
                               indicator='nonexistent_indicator')
        
        # Should raise error when building
        with self.assertRaises(ValueError):
            strategy.build()
        
        print("✅ Strategy Builder validation test passed")

    def test_signal_combination_methods(self):
        """Test different signal combination methods"""
        print("\n🔗 Testing signal combination methods...")
        
        # Create strategy with multiple signals
        strategy = StrategyBuilder(['BTCUSDT'], ['1D'])
        strategy.add_indicator('rsi', rsi, period=14)
        strategy.add_indicator('sma_fast', sma, period=10)
        strategy.add_indicator('sma_slow', sma, period=20)
        
        strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                               indicator='rsi', overbought=70, oversold=30)
        strategy.add_signal_rule('ma_cross', ma_crossover, 
                               fast_ma='sma_fast', slow_ma='sma_slow')
        
        # Test majority vote
        strategy.set_signal_combination('majority_vote')
        built_strategy = strategy.build()
        signals_majority = built_strategy.generate_signals(self.data)
        
        # Test unanimous
        strategy.set_signal_combination('unanimous')
        built_strategy = strategy.build()
        signals_unanimous = built_strategy.generate_signals(self.data)
        
        # Verify both methods generate signals
        self.assertIsNotNone(signals_majority, "Majority vote should generate signals")
        self.assertIsNotNone(signals_unanimous, "Unanimous should generate signals")
        
        print("✅ Signal combination methods test passed")

if __name__ == '__main__':
    print("🚀 Running Integration Tests...")
    print("=" * 60)
    
    unittest.main(verbosity=2)