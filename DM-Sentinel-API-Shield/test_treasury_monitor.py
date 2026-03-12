"""
Test Suite for DM Sentinel - Treasury Watcher & Anti-Drainer
PROMPT 5: El Centinela de Tesorería - Anti-Drainer

Comprehensive tests for 24/7 wallet monitoring and anomaly detection.

Author: DM Global Security Team
Created: March 2026
"""

import asyncio
import unittest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from decimal import Decimal
import time

# Import the module under test
try:
    from sentinel_treasury_monitor import (
        TreasuryWatcher,
        RiskLevel,
        AlertType,
        Alert,
        WalletSnapshot
    )
except ImportError as e:
    print(f"❌ Error importing sentinel_treasury_monitor: {e}")
    print("   Make sure sentinel_treasury_monitor.py is in the same directory")
    exit(1)


class TestTreasuryWatcher(unittest.TestCase):
    """Test suite for Treasury Watcher."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_wallet = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
        self.test_rpc = "https://eth.llamarpc.com"
        self.initial_balance = Decimal("10.0")  # 10 ETH
        
        # Create event loop for async tests
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
    
    def tearDown(self):
        """Clean up after tests."""
        if self.loop:
            self.loop.close()
    
    def run_async(self, coro):
        """Helper to run async code in tests."""
        return self.loop.run_until_complete(coro)
    
    @patch('sentinel_treasury_monitor.Web3')
    def test_initialization(self, mock_web3_class):
        """Test 1: Treasury Watcher initialization."""
        print("\n" + "=" * 80)
        print("TEST 1: Treasury Watcher Initialization")
        print("=" * 80)
        
        # Mock Web3 connection
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_web3_class.return_value = mock_w3
        mock_web3_class.HTTPProvider.return_value = Mock()
        mock_w3.keccak.return_value = Mock(hex=lambda: "0xabc123")
        
        # Initialize watcher
        watcher = TreasuryWatcher(
            rpc_endpoint=self.test_rpc,
            check_interval=15,
            critical_drop_threshold=0.5,
            time_window_minutes=5
        )
        
        # Assertions
        self.assertEqual(watcher.check_interval, 15)
        self.assertEqual(watcher.critical_drop_threshold, 0.5)
        self.assertEqual(watcher.time_window_seconds, 300)
        self.assertFalse(watcher.is_monitoring)
        self.assertEqual(len(watcher.wallets), 0)
        
        print(f"✅ Watcher initialized successfully")
        print(f"   Check interval: {watcher.check_interval}s")
        print(f"   Critical threshold: {watcher.critical_drop_threshold*100}%")
        print(f"   Time window: {watcher.time_window_seconds}s")
    
    @patch('sentinel_treasury_monitor.Web3')
    def test_add_remove_wallets(self, mock_web3_class):
        """Test 2: Adding and removing wallets."""
        print("\n" + "=" * 80)
        print("TEST 2: Add/Remove Wallets")
        print("=" * 80)
        
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_web3_class.return_value = mock_w3
        mock_web3_class.HTTPProvider.return_value = Mock()
        mock_web3_class.to_checksum_address = lambda x: x
        mock_w3.keccak.return_value = Mock(hex=lambda: "0xabc123")
        
        watcher = TreasuryWatcher(rpc_endpoint=self.test_rpc)
        
        # Add wallet
        watcher.add_wallet(self.test_wallet)
        self.assertIn(self.test_wallet, watcher.wallets)
        self.assertEqual(len(watcher.wallets), 1)
        
        # Add multiple wallets
        wallet2 = "0x1234567890123456789012345678901234567890"
        wallet3 = "0xabcdef1234567890abcdef1234567890abcdef12"
        watcher.add_wallet(wallet2)
        watcher.add_wallet(wallet3)
        self.assertEqual(len(watcher.wallets), 3)
        
        # Remove wallet
        watcher.remove_wallet(self.test_wallet)
        self.assertNotIn(self.test_wallet, watcher.wallets)
        self.assertEqual(len(watcher.wallets), 2)
        
        print(f"✅ Wallet management working correctly")
        print(f"   Added 3 wallets, removed 1, remaining: {len(watcher.wallets)}")
    
    @patch('sentinel_treasury_monitor.Web3')
    def test_critical_balance_drop_single_block(self, mock_web3_class):
        """Test 3: Detect >50% balance drop in single check."""
        print("\n" + "=" * 80)
        print("TEST 3: Critical Balance Drop (Single Block)")
        print("=" * 80)
        
        mock_w3 = self._setup_web3_mock(mock_web3_class)
        
        watcher = TreasuryWatcher(
            rpc_endpoint=self.test_rpc,
            critical_drop_threshold=0.5
        )
        watcher.add_wallet(self.test_wallet)
        
        # First check: 10 ETH
        mock_w3.eth.block_number = 18000000
        mock_w3.eth.get_balance.return_value = int(self.initial_balance * 10**18)
        
        self.run_async(watcher._check_wallet(self.test_wallet))
        
        # Second check: 4 ETH (60% drop - should trigger CRITICAL)
        mock_w3.eth.block_number = 18000001
        dropped_balance = self.initial_balance * Decimal("0.4")  # 4 ETH
        mock_w3.eth.get_balance.return_value = int(dropped_balance * 10**18)
        
        # Mock trigger_alert to capture the alert
        alerts_triggered = []
        
        async def mock_trigger_alert(alert):
            alerts_triggered.append(alert)
        
        watcher.trigger_alert = mock_trigger_alert
        
        self.run_async(watcher._check_wallet(self.test_wallet))
        
        # Assertions
        self.assertEqual(len(alerts_triggered), 1)
        alert = alerts_triggered[0]
        self.assertEqual(alert.alert_type, AlertType.BALANCE_DROP)
        self.assertEqual(alert.risk_level, RiskLevel.CRITICAL)
        self.assertGreater(alert.percentage_change, 50)
        
        print(f"✅ Critical drop detected correctly")
        print(f"   Alert type: {alert.alert_type.value}")
        print(f"   Risk level: {alert.risk_level.value}")
        print(f"   Drop: {alert.percentage_change:.1f}%")
        print(f"   Amount: {alert.amount} ETH")
    
    @patch('sentinel_treasury_monitor.Web3')
    def test_rapid_depletion_time_window(self, mock_web3_class):
        """Test 4: Detect >50% drop within 5-minute window."""
        print("\n" + "=" * 80)
        print("TEST 4: Rapid Depletion (5-Minute Window)")
        print("=" * 80)
        
        mock_w3 = self._setup_web3_mock(mock_web3_class)
        
        watcher = TreasuryWatcher(
            rpc_endpoint=self.test_rpc,
            critical_drop_threshold=0.5,
            time_window_minutes=5
        )
        watcher.add_wallet(self.test_wallet)
        
        current_time = time.time()
        
        # Simulate gradual drop over 4 minutes
        # T=0: 10 ETH
        mock_w3.eth.block_number = 18000000
        mock_w3.eth.get_balance.return_value = int(self.initial_balance * 10**18)
        
        snapshot1 = WalletSnapshot(
            address=self.test_wallet,
            balance=self.initial_balance,
            timestamp=current_time,
            block_number=18000000
        )
        watcher.wallet_history[self.test_wallet] = [snapshot1]
        
        # T=1min: 8 ETH
        snapshot2 = WalletSnapshot(
            address=self.test_wallet,
            balance=Decimal("8.0"),
            timestamp=current_time + 60,
            block_number=18000005
        )
        watcher.wallet_history[self.test_wallet].append(snapshot2)
        
        # T=3min: 6 ETH
        snapshot3 = WalletSnapshot(
            address=self.test_wallet,
            balance=Decimal("6.0"),
            timestamp=current_time + 180,
            block_number=18000015
        )
        watcher.wallet_history[self.test_wallet].append(snapshot3)
        
        # T=4min: 4 ETH (60% total drop - should trigger)
        current_snapshot = WalletSnapshot(
            address=self.test_wallet,
            balance=Decimal("4.0"),
            timestamp=current_time + 240,
            block_number=18000020
        )
        watcher.wallet_history[self.test_wallet].append(current_snapshot)
        
        # Mock trigger_alert
        alerts_triggered = []
        
        async def mock_trigger_alert(alert):
            alerts_triggered.append(alert)
        
        watcher.trigger_alert = mock_trigger_alert
        
        # Detect anomalies
        self.run_async(watcher._detect_anomalies(self.test_wallet, current_snapshot))
        
        # Assertions - should detect rapid depletion
        self.assertGreater(len(alerts_triggered), 0)
        
        rapid_depletion_alerts = [
            a for a in alerts_triggered
            if a.alert_type == AlertType.RAPID_DEPLETION
        ]
        self.assertGreater(len(rapid_depletion_alerts), 0)
        
        alert = rapid_depletion_alerts[0]
        self.assertEqual(alert.risk_level, RiskLevel.CRITICAL)
        self.assertGreater(alert.percentage_change, 50)
        
        print(f"✅ Rapid depletion detected correctly")
        print(f"   Alert type: {alert.alert_type.value}")
        print(f"   Risk level: {alert.risk_level.value}")
        print(f"   Drop: {alert.percentage_change:.1f}%")
        print(f"   Time window: {alert.additional_data.get('time_window_minutes', 0):.1f} minutes")
    
    @patch('sentinel_treasury_monitor.Web3')
    def test_no_false_positive_normal_activity(self, mock_web3_class):
        """Test 5: No alerts for normal activity (<50% change)."""
        print("\n" + "=" * 80)
        print("TEST 5: No False Positives (Normal Activity)")
        print("=" * 80)
        
        mock_w3 = self._setup_web3_mock(mock_web3_class)
        
        watcher = TreasuryWatcher(
            rpc_endpoint=self.test_rpc,
            critical_drop_threshold=0.5
        )
        watcher.add_wallet(self.test_wallet)
        
        # First check: 10 ETH
        mock_w3.eth.block_number = 18000000
        mock_w3.eth.get_balance.return_value = int(self.initial_balance * 10**18)
        
        self.run_async(watcher._check_wallet(self.test_wallet))
        
        # Second check: 7 ETH (30% drop - should NOT trigger)
        mock_w3.eth.block_number = 18000001
        normal_balance = self.initial_balance * Decimal("0.7")
        mock_w3.eth.get_balance.return_value = int(normal_balance * 10**18)
        
        alerts_triggered = []
        
        async def mock_trigger_alert(alert):
            alerts_triggered.append(alert)
        
        watcher.trigger_alert = mock_trigger_alert
        
        self.run_async(watcher._check_wallet(self.test_wallet))
        
        # Assertions - no alerts for 30% drop
        self.assertEqual(len(alerts_triggered), 0)
        
        print(f"✅ No false positives")
        print(f"   30% drop did not trigger alert (threshold: 50%)")
        print(f"   Alerts triggered: {len(alerts_triggered)}")
    
    @patch('sentinel_treasury_monitor.Web3')
    def test_suspicious_approval_detection(self, mock_web3_class):
        """Test 6: Detect suspicious unlimited token approvals."""
        print("\n" + "=" * 80)
        print("TEST 6: Suspicious Approval Detection")
        print("=" * 80)
        
        mock_w3 = self._setup_web3_mock(mock_web3_class)
        
        watcher = TreasuryWatcher(rpc_endpoint=self.test_rpc)
        watcher.add_wallet(self.test_wallet)
        
        # Mock approval event log
        MAX_UINT256 = 2**256 - 1
        
        mock_log = {
            'address': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  # USDC
            'topics': [
                Mock(hex=lambda: '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925'),  # Approval sig
                Mock(hex=lambda: '0x000000000000000000000000742d35Cc6634C0532925a3b844Bc9e7595f0bEb0'),  # Owner
                Mock(hex=lambda: '0x0000000000000000000000001234567890123456789012345678901234567890')   # Spender
            ],
            'data': Mock(hex=lambda: hex(MAX_UINT256)),  # Unlimited approval
            'blockNumber': 18000000,
            'transactionHash': Mock(hex=lambda: '0xabc123def456')
        }
        
        mock_w3.eth.get_logs.return_value = [mock_log]
        
        # Check for approvals
        alerts = self.run_async(watcher.check_suspicious_approvals(
            address=self.test_wallet,
            from_block=18000000,
            to_block=18000010
        ))
        
        # Assertions
        self.assertGreater(len(alerts), 0)
        alert = alerts[0]
        self.assertEqual(alert.alert_type, AlertType.MASSIVE_APPROVAL)
        self.assertEqual(alert.risk_level, RiskLevel.HIGH)
        self.assertEqual(alert.additional_data['amount'], 'UNLIMITED')
        
        print(f"✅ Suspicious approval detected")
        print(f"   Alert type: {alert.alert_type.value}")
        print(f"   Risk level: {alert.risk_level.value}")
        print(f"   Amount: {alert.additional_data['amount']}")
        print(f"   Spender: {alert.additional_data['spender']}")
    
    @patch('sentinel_treasury_monitor.Web3')
    def test_concurrent_wallet_monitoring(self, mock_web3_class):
        """Test 7: Monitor 100+ wallets concurrently."""
        print("\n" + "=" * 80)
        print("TEST 7: Concurrent Monitoring (100 Wallets)")
        print("=" * 80)
        
        mock_w3 = self._setup_web3_mock(mock_web3_class)
        
        watcher = TreasuryWatcher(rpc_endpoint=self.test_rpc)
        
        # Add 100 wallets
        for i in range(100):
            wallet = f"0x{str(i).zfill(40)}"
            watcher.add_wallet(wallet)
        
        self.assertEqual(len(watcher.wallets), 100)
        
        # Mock balance checks
        mock_w3.eth.block_number = 18000000
        mock_w3.eth.get_balance.return_value = int(10 * 10**18)
        
        # Test concurrent checking (should not block)
        # Create new event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(watcher._check_all_wallets())
        finally:
            loop.close()
        
        # Verify all wallets have history
        self.assertEqual(len(watcher.wallet_history), 100)
        
        print(f"✅ Concurrent monitoring working")
        print(f"   Wallets monitored: {len(watcher.wallets)}")
        print(f"   Total checks: {watcher.total_checks}")
        print(f"   Wallets with history: {len(watcher.wallet_history)}")
    
    @patch('sentinel_treasury_monitor.Web3')
    def test_wallet_status_tracking(self, mock_web3_class):
        """Test 8: Wallet status and statistics tracking."""
        print("\n" + "=" * 80)
        print("TEST 8: Wallet Status Tracking")
        print("=" * 80)
        
        mock_w3 = self._setup_web3_mock(mock_web3_class)
        
        watcher = TreasuryWatcher(rpc_endpoint=self.test_rpc)
        watcher.add_wallet(self.test_wallet)
        
        # Add some history
        current_time = time.time()
        
        snapshot1 = WalletSnapshot(
            address=self.test_wallet,
            balance=Decimal("10.0"),
            timestamp=current_time,
            block_number=18000000
        )
        
        snapshot2 = WalletSnapshot(
            address=self.test_wallet,
            balance=Decimal("8.5"),
            timestamp=current_time + 60,
            block_number=18000005
        )
        
        watcher.wallet_history[self.test_wallet] = [snapshot1, snapshot2]
        
        # Get wallet status
        status = watcher.get_wallet_status(self.test_wallet)
        
        # Assertions
        self.assertIsNotNone(status)
        self.assertEqual(status['address'], self.test_wallet)
        self.assertEqual(status['current_balance'], 8.5)
        self.assertEqual(status['checks_count'], 2)
        self.assertIn('balance_change', status)
        
        # Get statistics
        stats = watcher.get_statistics()
        self.assertEqual(stats['wallets_monitored'], 1)
        
        print(f"✅ Status tracking working")
        print(f"   Current balance: {status['current_balance']} ETH")
        print(f"   Balance change: {status.get('balance_change', 0)} ETH")
        print(f"   Checks count: {status['checks_count']}")
    
    @patch('sentinel_treasury_monitor.Web3')
    @patch('sentinel_treasury_monitor.aiohttp.ClientSession')
    def test_telegram_alert_integration(self, mock_session_class, mock_web3_class):
        """Test 9: Telegram alert integration."""
        print("\n" + "=" * 80)
        print("TEST 9: Telegram Alert Integration")
        print("=" * 80)
        
        mock_w3 = self._setup_web3_mock(mock_web3_class)
        
        # Mock aiohttp session
        mock_response = AsyncMock()
        mock_response.status = 200
        
        mock_post = AsyncMock(return_value=mock_response)
        mock_session = AsyncMock()
        mock_session.post = mock_post
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        
        mock_session_class.return_value = mock_session
        
        watcher = TreasuryWatcher(
            rpc_endpoint=self.test_rpc,
            telegram_bot_token="test_bot_token",
            telegram_chat_id="test_chat_id"
        )
        
        # Create test alert
        alert = Alert(
            alert_type=AlertType.BALANCE_DROP,
            risk_level=RiskLevel.CRITICAL,
            wallet=self.test_wallet,
            message="Test alert",
            amount=Decimal("5.0"),
            percentage_change=60.0
        )
        
        # Send alert
        self.run_async(watcher._send_telegram_alert(alert))
        
        # Verify Telegram API was called
        self.assertTrue(mock_post.called)
        
        print(f"✅ Telegram integration working")
        print(f"   API called: {mock_post.called}")
        print(f"   Alert sent successfully")
    
    @patch('sentinel_treasury_monitor.Web3')
    def test_alert_rate_limiting(self, mock_web3_class):
        """Test 10: Alert rate limiting (no spam)."""
        print("\n" + "=" * 80)
        print("TEST 10: Alert Rate Limiting")
        print("=" * 80)
        
        mock_w3 = self._setup_web3_mock(mock_web3_class)
        
        # Create watcher with Telegram credentials so _send_telegram_alert is called
        watcher = TreasuryWatcher(
            rpc_endpoint=self.test_rpc,
            telegram_bot_token="test_token",
            telegram_chat_id="test_chat_id"
        )
        
        # Create duplicate alerts
        alert = Alert(
            alert_type=AlertType.BALANCE_DROP,
            risk_level=RiskLevel.CRITICAL,
            wallet=self.test_wallet,
            message="Test alert"
        )
        
        # Mock _send_telegram_alert and _print_alert
        telegram_calls = []
        
        async def mock_send_telegram(a):
            telegram_calls.append(a)
        
        watcher._send_telegram_alert = mock_send_telegram
        
        # Create new event loop for this test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Trigger alert multiple times
            loop.run_until_complete(watcher.trigger_alert(alert))
            watcher.alerts_triggered = 0  # Reset counter
            loop.run_until_complete(watcher.trigger_alert(alert))  # Should be rate-limited
            watcher.alerts_triggered = 0
            loop.run_until_complete(watcher.trigger_alert(alert))  # Should be rate-limited
        finally:
            loop.close()
        
        # Verify only first alert was sent (others rate-limited)
        self.assertEqual(len(telegram_calls), 1)
        
        print(f"✅ Rate limiting working")
        print(f"   Alerts triggered: 3")
        print(f"   Alerts sent: {len(telegram_calls)} (rate-limited)")
    
    def _setup_web3_mock(self, mock_web3_class):
        """Helper to set up Web3 mocks."""
        mock_w3 = Mock()
        mock_w3.is_connected.return_value = True
        mock_w3.eth.block_number = 18000000
        mock_w3.eth.get_balance.return_value = int(10 * 10**18)
        mock_w3.keccak.return_value = Mock(hex=lambda: "0xabc123")
        mock_w3.to_hex = lambda x: "0x" + x.hex()
        
        mock_web3_class.return_value = mock_w3
        mock_web3_class.HTTPProvider.return_value = Mock()
        mock_web3_class.to_checksum_address = lambda x: x
        
        return mock_w3


async def run_all_tests():
    """Run all test cases."""
    print("\n")
    print("=" * 80)
    print("🛡️  DM SENTINEL - TREASURY WATCHER TEST SUITE")
    print("   PROMPT 5: El Centinela de Tesorería - Anti-Drainer")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestTreasuryWatcher)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    tests_run = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = tests_run - failures - errors
    
    print(f"\n📋 Results:")
    print(f"   ✅ Passed: {passed}/{tests_run}")
    if failures > 0:
        print(f"   ❌ Failed: {failures}")
    if errors > 0:
        print(f"   ⚠️  Errors: {errors}")
    
    print(f"\n📊 Total: {passed}/{tests_run} tests passed ({int(passed/tests_run*100)}%)")
    
    if passed == tests_run:
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 80)
        print("\n✅ Acceptance Criteria Validated (PROMPT 5):")
        print("   ✅ Real-time monitoring (async loop, 15s interval)")
        print("   ✅ Anomaly detection (>50% drop triggers CRITICAL)")
        print("   ✅ Time window detection (5-minute monitoring)")
        print("   ✅ Suspicious approval detection")
        print("   ✅ Telegram alert integration")
        print("   ✅ Concurrent monitoring (100+ wallets)")
        print("   ✅ Alert rate limiting (no spam)")
        print("   ✅ Wallet status tracking")
        print("\n🚀 PROMPT 5 ready for production!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("⚠️  SOME TESTS FAILED")
        print("=" * 80)
        print("\nReview failures above for details.")
    
    return result


if __name__ == "__main__":
    # Run async test suite
    result = asyncio.run(run_all_tests())
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
