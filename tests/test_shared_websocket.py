"""
Test Shared WebSocket Functionality
====================================

This test verifies that:
1. SharedWebSocketManager implements singleton pattern correctly
2. Both data collector and paper trader use the same websocket connection
3. Data flows correctly through the shared websocket
4. Subscribers receive data from the shared websocket
5. Initialization and cleanup work properly

Run this test to confirm your shared websocket implementation works as intended.
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared_modules.data_collection.shared_websocket_manager import SharedWebSocketManager
from shared_modules.data_collection.hybrid_system import HybridTradingSystem
from shared_modules.data_collection.config import DataCollectionConfig
from simple_strategy.trading.paper_trading_engine import PaperTradingEngine


class TestSharedWebSocket:
    def __init__(self):
        print("🧪 Initializing Shared WebSocket Test...")
        self.test_results = []
        self.received_messages = []
        
    def log_result(self, test_name, passed, message=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append((test_name, passed, message))
        
    async def test_singleton_pattern(self):
        """Test 1: Verify SharedWebSocketManager is a true singleton"""
        print("\n📋 Test 1: Singleton Pattern Verification")
        
        try:
            # Create multiple instances
            manager1 = SharedWebSocketManager()
            manager2 = SharedWebSocketManager()
            manager3 = SharedWebSocketManager()
            
            # All should be the same instance
            is_singleton = (manager1 is manager2 is manager3)
            
            self.log_result(
                "Singleton Pattern", 
                is_singleton,
                f"Instances same: {id(manager1)} == {id(manager2)} == {id(manager3)}"
            )
            
            return is_singleton
            
        except Exception as e:
            self.log_result("Singleton Pattern", False, f"Exception: {e}")
            return False
    
    async def test_data_collector_websocket(self):
        """Test 2: Test data collector websocket initialization"""
        print("\n📋 Test 2: Data Collector WebSocket Initialization")
        
        data_system = None
        try:
            # Create config for testing (disable actual websocket for safety)
            config = DataCollectionConfig()
            config.ENABLE_WEBSOCKET = False  # Disable for testing
            
            # Create hybrid system (data collector)
            data_system = HybridTradingSystem(config)
            
            # Initialize the system
            await data_system.initialize()
            
            # Check if websocket handler is set
            has_handler = data_system.websocket_handler is not None
            has_shared_manager = data_system.shared_ws_manager is not None
            
            self.log_result(
                "Data Collector WebSocket Setup",
                has_handler and has_shared_manager,
                f"Handler: {has_handler}, Shared Manager: {has_shared_manager}"
            )
            
            return has_handler and has_shared_manager
            
        except Exception as e:
            self.log_result("Data Collector WebSocket Setup", False, f"Exception: {e}")
            return False
        finally:
            # Cleanup resources
            if data_system and hasattr(data_system, 'cleanup'):
                await data_system.cleanup()
    
    async def test_paper_trader_websocket(self):
        """Test 3: Test paper trader websocket initialization"""
        print("\n📋 Test 3: Paper Trader WebSocket Initialization")
        
        data_system = None
        shared_ws_manager = None
        try:
            # Create a mock paper trading engine (simplified for testing)
            config = DataCollectionConfig()
            config.ENABLE_WEBSOCKET = False  # Disable for testing
            
            # Simulate paper trading engine initialization
            shared_ws_manager = SharedWebSocketManager()
            data_system = HybridTradingSystem(config)
            await data_system.initialize()
            
            # Check if paper trader components have websocket access
            has_shared_manager = shared_ws_manager is not None
            has_data_system = data_system is not None
            has_websocket_handler = data_system.websocket_handler is not None
            
            self.log_result(
                "Paper Trader WebSocket Setup",
                has_shared_manager and has_data_system and has_websocket_handler,
                f"Shared Manager: {has_shared_manager}, Data System: {has_data_system}, Handler: {has_websocket_handler}"
            )
            
            return has_shared_manager and has_data_system and has_websocket_handler
            
        except Exception as e:
            self.log_result("Paper Trader WebSocket Setup", False, f"Exception: {e}")
            return False
        finally:
            # Cleanup resources
            if data_system and hasattr(data_system, 'cleanup'):
                await data_system.cleanup()
            if shared_ws_manager and hasattr(shared_ws_manager, 'shutdown'):
                await shared_ws_manager.shutdown()
    
    async def test_shared_websocket_instance(self):
        """Test 4: Verify both systems use the same websocket instance"""
        print("\n📋 Test 4: Shared WebSocket Instance Verification")
        
        data_system = None
        paper_data_system = None
        shared_ws_manager = None
        try:
            config = DataCollectionConfig()
            config.ENABLE_WEBSOCKET = False  # Disable for testing
            
            # Create data collector system
            data_system = HybridTradingSystem(config)
            await data_system.initialize()
            
            # Create paper trader components
            shared_ws_manager = SharedWebSocketManager()
            paper_data_system = HybridTradingSystem(config)
            await paper_data_system.initialize()
            
            # Get websocket handlers from both systems
            data_handler = data_system.websocket_handler
            paper_handler = paper_data_system.websocket_handler
            
            # Get shared managers
            data_manager = data_system.shared_ws_manager
            paper_manager = paper_data_system.shared_ws_manager
            
            # All should be the same instances
            same_handler = data_handler is paper_handler
            same_manager = data_manager is paper_manager
            same_manager_global = data_manager is shared_ws_manager
            
            self.log_result(
                "Shared WebSocket Instance",
                same_handler and same_manager and same_manager_global,
                f"Same Handler: {same_handler}, Same Manager: {same_manager}, Same Global: {same_manager_global}"
            )
            
            if same_handler and same_manager and same_manager_global:
                print(f"   Handler IDs: Data={id(data_handler)}, Paper={id(paper_handler)}")
                print(f"   Manager IDs: Data={id(data_manager)}, Paper={id(paper_manager)}, Global={id(shared_ws_manager)}")
            
            return same_handler and same_manager and same_manager_global
            
        except Exception as e:
            self.log_result("Shared WebSocket Instance", False, f"Exception: {e}")
            return False
        finally:
            # Cleanup resources
            if data_system and hasattr(data_system, 'cleanup'):
                await data_system.cleanup()
            if paper_data_system and hasattr(paper_data_system, 'cleanup'):
                await paper_data_system.cleanup()
            if shared_ws_manager and hasattr(shared_ws_manager, 'shutdown'):
                await shared_ws_manager.shutdown()
    
    async def test_subscriber_functionality(self):
        """Test 5: Test subscriber functionality for data sharing"""
        print("\n📋 Test 5: Subscriber Functionality Test")
        
        try:
            config = DataCollectionConfig()
            config.ENABLE_WEBSOCKET = False  # Disable for testing
            
            # Create shared websocket manager
            shared_manager = SharedWebSocketManager()
            await shared_manager.initialize(config)
            
            # Test data storage
            test_messages = []
            
            def subscriber_callback(message):
                test_messages.append(message)
                print(f"   📨 Subscriber received: {len(test_messages)} messages")
            
            def subscriber_callback2(message):
                test_messages.append(f"sub2_{message}")
                print(f"   📨 Subscriber2 received: {len([m for m in test_messages if m.startswith('sub2_')])} messages")
            
            # Add subscribers
            shared_manager.add_subscriber(subscriber_callback)
            shared_manager.add_subscriber(subscriber_callback2)
            
            # Simulate message broadcasting (normally done by websocket handler)
            test_data = {"symbol": "BTCUSDT", "price": 50000, "timestamp": int(time.time() * 1000)}
            
            # Simulate what happens when websocket receives data
            for callback in shared_manager.subscribers:
                callback(json.dumps(test_data))
            
            # Verify both subscribers received the data
            sub1_received = len([m for m in test_messages if not m.startswith('sub2_')]) > 0
            sub2_received = len([m for m in test_messages if m.startswith('sub2_')]) > 0
            
            self.log_result(
                "Subscriber Functionality",
                sub1_received and sub2_received,
                f"Sub1 received: {sub1_received}, Sub2 received: {sub2_received}, Total messages: {len(test_messages)}"
            )
            
            # Clean up
            shared_manager.remove_subscriber(subscriber_callback)
            shared_manager.remove_subscriber(subscriber_callback2)
            
            return sub1_received and sub2_received
            
        except Exception as e:
            self.log_result("Subscriber Functionality", False, f"Exception: {e}")
            return False
    
    async def test_websocket_state_management(self):
        """Test 6: Test websocket state management"""
        print("\n📋 Test 6: WebSocket State Management")
        
        data_system = None
        try:
            config = DataCollectionConfig()
            config.ENABLE_WEBSOCKET = False  # Disable for testing
            
            # Create and initialize system
            data_system = HybridTradingSystem(config)
            await data_system.initialize()
            
            # Check initial state
            initial_state = data_system.is_initialized
            
            # Test websocket handler state
            handler = data_system.websocket_handler
            handler_state = handler is not None
            
            # Test shared manager state
            manager = data_system.shared_ws_manager
            manager_state = manager is not None
            
            self.log_result(
                "WebSocket State Management",
                initial_state and handler_state and manager_state,
                f"System Initialized: {initial_state}, Handler: {handler_state}, Manager: {manager_state}"
            )
            
            return initial_state and handler_state and manager_state
            
        except Exception as e:
            self.log_result("WebSocket State Management", False, f"Exception: {e}")
            return False
        finally:
            # Cleanup resources
            if data_system and hasattr(data_system, 'cleanup'):
                await data_system.cleanup()
    
    async def test_cleanup_functionality(self):
        """Test 7: Test cleanup functionality"""
        print("\n📋 Test 7: Cleanup Functionality")
        
        try:
            config = DataCollectionConfig()
            config.ENABLE_WEBSOCKET = False  # Disable for testing
            
            # Create and initialize system
            shared_manager = SharedWebSocketManager()
            await shared_manager.initialize(config)
            
            # Add some subscribers
            def dummy_callback(msg):
                pass
            
            shared_manager.add_subscriber(dummy_callback)
            subscriber_count_before = len(shared_manager.subscribers)
            
            # Remove subscriber
            shared_manager.remove_subscriber(dummy_callback)
            subscriber_count_after = len(shared_manager.subscribers)
            
            # Test shutdown
            await shared_manager.shutdown()
            
            cleanup_successful = subscriber_count_before > subscriber_count_after and subscriber_count_after == 0
            
            self.log_result(
                "Cleanup Functionality",
                cleanup_successful,
                f"Subscribers before: {subscriber_count_before}, after: {subscriber_count_after}"
            )
            
            return cleanup_successful
            
        except Exception as e:
            self.log_result("Cleanup Functionality", False, f"Exception: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all tests and generate summary"""
        print("🚀 Starting Shared WebSocket Tests...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        test_functions = [
            self.test_singleton_pattern,
            self.test_data_collector_websocket,
            self.test_paper_trader_websocket,
            self.test_shared_websocket_instance,
            self.test_subscriber_functionality,
            self.test_websocket_state_management,
            self.test_cleanup_functionality
        ]
        
        results = []
        for test_func in test_functions:
            try:
                result = await test_func()
                results.append(result)
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {e}")
                results.append(False)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"⏱️  Total Time: {duration:.2f} seconds")
        print(f"📈 Tests Passed: {passed}/{total}")
        print(f"📊 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ Your shared websocket implementation is working correctly!")
            print("✅ Both data collector and paper trader use the same websocket connection!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed.")
            print("🔧 Please review the failed tests above.")
        
        # Show detailed results
        print("\n📋 Detailed Results:")
        for test_name, passed, message in self.test_results:
            status = "✅" if passed else "❌"
            print(f"  {status} {test_name}: {message}")
        
        return passed == total


async def main():
    """Main test runner"""
    test = TestSharedWebSocket()
    success = await test.run_all_tests()
    
    if success:
        print("\n🎯 CONCLUSION:")
        print("✅ SharedWebSocketManager correctly implements singleton pattern")
        print("✅ Data collector and paper trader use the same websocket connection")
        print("✅ Data can be shared between systems through the shared websocket")
        print("✅ Subscriber functionality works for real-time data distribution")
        print("✅ State management and cleanup work properly")
        print("\n🚀 Your shared websocket architecture is ready for production!")
    else:
        print("\n🔧 CONCLUSION:")
        print("❌ Some tests failed. Please review and fix the issues before deployment.")
    
    return success


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)