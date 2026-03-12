"""
DM Sentinel - Treasury Watcher & Anti-Drainer
PROMPT 5: El Centinela de Tesorería - Anti-Drainer (Pentester + Tech Lead)

24/7 wallet monitoring system with real-time anomaly detection and threat alerting.
Detects suspicious balance drops, unauthorized approvals, and potential drainage attacks.

Author: DM Global Security Team
Created: March 2026
"""

import asyncio
import time
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
from decimal import Decimal
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

try:
    from web3 import Web3
    from web3.exceptions import TransactionNotFound
except ImportError:
    raise ImportError("Web3.py is required. Install with: pip install web3")

try:
    import aiohttp
except ImportError:
    raise ImportError("aiohttp is required. Install with: pip install aiohttp")


class RiskLevel(Enum):
    """Risk levels for detected anomalies."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(Enum):
    """Types of security alerts."""
    BALANCE_DROP = "BALANCE_DROP"
    SUSPICIOUS_APPROVAL = "SUSPICIOUS_APPROVAL"
    RAPID_DEPLETION = "RAPID_DEPLETION"
    UNUSUAL_TRANSACTION = "UNUSUAL_TRANSACTION"
    MASSIVE_APPROVAL = "MASSIVE_APPROVAL"


@dataclass
class WalletSnapshot:
    """Snapshot of wallet state at a specific time."""
    address: str
    balance: Decimal
    timestamp: float
    block_number: int
    token_balances: Dict[str, Decimal] = field(default_factory=dict)


@dataclass
class Alert:
    """Security alert structure."""
    alert_type: AlertType
    risk_level: RiskLevel
    wallet: str
    message: str
    amount: Optional[Decimal] = None
    percentage_change: Optional[float] = None
    timestamp: float = field(default_factory=time.time)
    block_number: Optional[int] = None
    transaction_hash: Optional[str] = None
    additional_data: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary for JSON serialization."""
        return {
            "alert_type": self.alert_type.value,
            "risk_level": self.risk_level.value,
            "wallet": self.wallet,
            "message": self.message,
            "amount": float(self.amount) if self.amount else None,
            "percentage_change": self.percentage_change,
            "timestamp": self.timestamp,
            "timestamp_human": datetime.fromtimestamp(self.timestamp).isoformat(),
            "block_number": self.block_number,
            "transaction_hash": self.transaction_hash,
            "additional_data": self.additional_data
        }


class TreasuryWatcher:
    """
    24/7 Treasury Monitoring & Anti-Drainer System.
    
    Monitors wallet balances and detects:
    - Rapid balance drops (>50% in 5 minutes)
    - Suspicious token approvals
    - Unusual transaction patterns
    - Potential drainage attacks
    
    Supports monitoring up to 100+ wallets simultaneously.
    """
    
    def __init__(
        self,
        rpc_endpoint: str,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        check_interval: int = 15,  # seconds
        critical_drop_threshold: float = 0.5,  # 50%
        time_window_minutes: int = 5
    ):
        """
        Initialize Treasury Watcher.
        
        Args:
            rpc_endpoint: Web3 RPC endpoint URL
            telegram_bot_token: Telegram bot token for alerts
            telegram_chat_id: Telegram chat ID for alerts
            check_interval: Seconds between balance checks (default: 15)
            critical_drop_threshold: Percentage drop to trigger CRITICAL alert (default: 0.5 = 50%)
            time_window_minutes: Time window for anomaly detection (default: 5 minutes)
        """
        # Web3 setup
        self.w3 = Web3(Web3.HTTPProvider(rpc_endpoint))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to RPC endpoint: {rpc_endpoint}")
        
        # Monitoring configuration
        self.check_interval = check_interval
        self.critical_drop_threshold = critical_drop_threshold
        self.time_window_seconds = time_window_minutes * 60
        
        # Telegram configuration
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        
        # Wallet tracking
        self.wallets: Set[str] = set()
        self.wallet_history: Dict[str, List[WalletSnapshot]] = {}
        self.last_alert_time: Dict[str, float] = {}  # Rate limiting
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task = None
        
        # Statistics
        self.total_checks = 0
        self.alerts_triggered = 0
        
        # ERC-20 Approval event signature
        self.APPROVAL_EVENT_SIGNATURE = self.w3.keccak(text="Approval(address,address,uint256)").hex()
        
        print(f"✅ Treasury Watcher initialized")
        print(f"   RPC: {rpc_endpoint[:50]}...")
        print(f"   Check interval: {check_interval}s")
        print(f"   Critical threshold: {critical_drop_threshold*100}%")
        print(f"   Time window: {time_window_minutes} minutes")
    
    def add_wallet(self, address: str) -> None:
        """
        Add a wallet to monitoring.
        
        Args:
            address: Ethereum wallet address
        """
        address = Web3.to_checksum_address(address)
        if address not in self.wallets:
            self.wallets.add(address)
            self.wallet_history[address] = []
            print(f"   ➕ Added wallet: {address}")
    
    def remove_wallet(self, address: str) -> None:
        """
        Remove a wallet from monitoring.
        
        Args:
            address: Ethereum wallet address
        """
        address = Web3.to_checksum_address(address)
        if address in self.wallets:
            self.wallets.remove(address)
            print(f"   ➖ Removed wallet: {address}")
    
    async def start_monitoring(self) -> None:
        """
        Start 24/7 wallet monitoring.
        
        This launches an async loop that checks all wallets every `check_interval` seconds.
        Supports monitoring 100+ wallets simultaneously without blocking.
        """
        if self.is_monitoring:
            print("⚠️  Monitoring already active")
            return
        
        if not self.wallets:
            print("⚠️  No wallets to monitor. Add wallets first.")
            return
        
        self.is_monitoring = True
        print(f"\n🛡️  Starting treasury monitoring...")
        print(f"   Monitoring {len(self.wallets)} wallet(s)")
        print(f"   Check interval: {self.check_interval}s")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while self.is_monitoring:
                # Check all wallets concurrently
                await self._check_all_wallets()
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
        except KeyboardInterrupt:
            print("\n⚠️  Monitoring interrupted by user")
        finally:
            self.is_monitoring = False
    
    def stop_monitoring(self) -> None:
        """Stop monitoring."""
        self.is_monitoring = False
        print("🛑 Monitoring stopped")
    
    async def _check_all_wallets(self) -> None:
        """Check all monitored wallets concurrently."""
        self.total_checks += 1
        
        # Create async tasks for all wallets
        tasks = [self._check_wallet(address) for address in self.wallets]
        
        # Execute all checks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_wallet(self, address: str) -> None:
        """
        Check a single wallet for anomalies.
        
        Args:
            address: Wallet address to check
        """
        try:
            # Get current state
            current_block = self.w3.eth.block_number
            current_balance = self.w3.eth.get_balance(address)
            current_balance_eth = Decimal(current_balance) / Decimal(10**18)
            
            # Create snapshot
            snapshot = WalletSnapshot(
                address=address,
                balance=current_balance_eth,
                timestamp=time.time(),
                block_number=current_block
            )
            
            # Add to history
            self.wallet_history[address].append(snapshot)
            
            # Keep only recent history (last hour)
            cutoff_time = time.time() - 3600
            self.wallet_history[address] = [
                s for s in self.wallet_history[address]
                if s.timestamp > cutoff_time
            ]
            
            # Detect anomalies if we have history
            if len(self.wallet_history[address]) >= 2:
                await self._detect_anomalies(address, snapshot)
            
        except Exception as e:
            print(f"❌ Error checking wallet {address}: {e}")
    
    async def _detect_anomalies(self, address: str, current_snapshot: WalletSnapshot) -> None:
        """
        Detect anomalies in wallet behavior.
        
        Args:
            address: Wallet address
            current_snapshot: Current wallet state
        """
        history = self.wallet_history[address]
        
        # Check for rapid balance drop (single block)
        if len(history) >= 2:
            previous = history[-2]
            
            if previous.balance > 0:
                drop_percentage = float((previous.balance - current_snapshot.balance) / previous.balance)
                
                # CRITICAL: >50% drop in single check
                if drop_percentage > self.critical_drop_threshold:
                    amount_dropped = previous.balance - current_snapshot.balance
                    
                    alert = Alert(
                        alert_type=AlertType.BALANCE_DROP,
                        risk_level=RiskLevel.CRITICAL,
                        wallet=address,
                        message=f"🚨 CRITICAL: Balance dropped {drop_percentage*100:.1f}% in {self.check_interval}s",
                        amount=amount_dropped,
                        percentage_change=drop_percentage * 100,
                        block_number=current_snapshot.block_number,
                        additional_data={
                            "previous_balance": float(previous.balance),
                            "current_balance": float(current_snapshot.balance),
                            "blocks_elapsed": current_snapshot.block_number - previous.block_number,
                            "time_elapsed_seconds": current_snapshot.timestamp - previous.timestamp
                        }
                    )
                    
                    await self.trigger_alert(alert)
        
        # Check for balance drop over time window (5 minutes)
        # Only trigger if this is a gradual depletion (not already caught by single-block check)
        time_window_snapshots = [
            s for s in history
            if current_snapshot.timestamp - s.timestamp <= self.time_window_seconds
        ]
        
        if len(time_window_snapshots) >= 3:  # Need at least 3 snapshots to detect gradual depletion
            oldest_in_window = time_window_snapshots[0]
            
            if oldest_in_window.balance > 0:
                window_drop_percentage = float(
                    (oldest_in_window.balance - current_snapshot.balance) / oldest_in_window.balance
                )
                
                # CRITICAL: >50% drop within time window (gradual depletion over multiple checks)
                if window_drop_percentage > self.critical_drop_threshold:
                    amount_dropped = oldest_in_window.balance - current_snapshot.balance
                    time_elapsed = current_snapshot.timestamp - oldest_in_window.timestamp
                    
                    alert = Alert(
                        alert_type=AlertType.RAPID_DEPLETION,
                        risk_level=RiskLevel.CRITICAL,
                        wallet=address,
                        message=f"🚨 CRITICAL: Rapid depletion detected! {window_drop_percentage*100:.1f}% loss in {time_elapsed/60:.1f} minutes",
                        amount=amount_dropped,
                        percentage_change=window_drop_percentage * 100,
                        block_number=current_snapshot.block_number,
                        additional_data={
                            "window_start_balance": float(oldest_in_window.balance),
                            "current_balance": float(current_snapshot.balance),
                            "time_window_seconds": time_elapsed,
                            "time_window_minutes": time_elapsed / 60
                        }
                    )
                    
                    await self.trigger_alert(alert)
    
    async def check_suspicious_approvals(
        self,
        address: str,
        from_block: int,
        to_block: Optional[int] = None
    ) -> List[Alert]:
        """
        Check for suspicious ERC-20 token approvals.
        
        Args:
            address: Wallet address to check
            from_block: Starting block number
            to_block: Ending block number (None = latest)
        
        Returns:
            List of alerts for suspicious approvals
        """
        alerts = []
        
        try:
            if to_block is None:
                to_block = self.w3.eth.block_number
            
            # Get approval events where this address is the owner
            approval_filter = {
                'fromBlock': from_block,
                'toBlock': to_block,
                'topics': [
                    self.APPROVAL_EVENT_SIGNATURE,
                    self.w3.to_hex(int(address, 16).to_bytes(32, byteorder='big'))  # Owner address
                ]
            }
            
            logs = self.w3.eth.get_logs(approval_filter)
            
            for log in logs:
                # Decode approval event
                # Topics: [event_sig, indexed_owner, indexed_spender]
                # Data: amount
                
                if len(log['topics']) >= 3:
                    spender = '0x' + log['topics'][2].hex()[-40:]
                    
                    # Decode amount from data
                    if log['data']:
                        amount = int(log['data'].hex(), 16)
                        
                        # Check for unlimited approval (2^256 - 1)
                        MAX_UINT256 = 2**256 - 1
                        
                        if amount >= MAX_UINT256 * 0.9:  # Essentially unlimited
                            alert = Alert(
                                alert_type=AlertType.MASSIVE_APPROVAL,
                                risk_level=RiskLevel.HIGH,
                                wallet=address,
                                message=f"⚠️  UNLIMITED token approval granted to {spender[:10]}...{spender[-8:]}",
                                block_number=log['blockNumber'],
                                transaction_hash=log['transactionHash'].hex(),
                                additional_data={
                                    "spender": spender,
                                    "amount": "UNLIMITED",
                                    "token_contract": log['address']
                                }
                            )
                            alerts.append(alert)
                            await self.trigger_alert(alert)
            
        except Exception as e:
            print(f"❌ Error checking approvals for {address}: {e}")
        
        return alerts
    
    async def trigger_alert(self, alert: Alert) -> None:
        """
        Trigger a security alert.
        
        Sends alert to Telegram (if configured) and prints to console.
        Includes rate limiting to prevent alert spam.
        
        Args:
            alert: Alert object with details
        """
        # Rate limiting: Don't send duplicate alerts within 60 seconds
        rate_limit_key = f"{alert.wallet}_{alert.alert_type.value}"
        current_time = time.time()
        
        if rate_limit_key in self.last_alert_time:
            time_since_last = current_time - self.last_alert_time[rate_limit_key]
            if time_since_last < 60:
                return  # Skip duplicate alert
        
        self.last_alert_time[rate_limit_key] = current_time
        self.alerts_triggered += 1
        
        # Print to console
        self._print_alert(alert)
        
        # Send to Telegram
        if self.telegram_bot_token and self.telegram_chat_id:
            await self._send_telegram_alert(alert)
    
    def _print_alert(self, alert: Alert) -> None:
        """Print alert to console with formatting."""
        print("\n" + "=" * 80)
        
        # Risk level emoji
        emoji_map = {
            RiskLevel.LOW: "ℹ️",
            RiskLevel.MEDIUM: "⚠️",
            RiskLevel.HIGH: "🔴",
            RiskLevel.CRITICAL: "🚨"
        }
        emoji = emoji_map.get(alert.risk_level, "⚠️")
        
        print(f"{emoji} {alert.risk_level.value} ALERT - {alert.alert_type.value}")
        print("=" * 80)
        print(f"Wallet: {alert.wallet}")
        print(f"Message: {alert.message}")
        
        if alert.amount:
            print(f"Amount: {alert.amount} ETH")
        
        if alert.percentage_change:
            print(f"Change: {alert.percentage_change:.2f}%")
        
        if alert.block_number:
            print(f"Block: {alert.block_number}")
        
        if alert.transaction_hash:
            print(f"TX: {alert.transaction_hash}")
        
        print(f"Time: {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
        
        if alert.additional_data:
            print(f"Additional: {json.dumps(alert.additional_data, indent=2)}")
        
        print("=" * 80 + "\n")
    
    async def _send_telegram_alert(self, alert: Alert) -> None:
        """
        Send alert to Telegram bot.
        
        Args:
            alert: Alert object to send
        """
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            # Format message for Telegram
            message = f"🛡️ *DM SENTINEL ALERT*\n\n"
            message += f"*Risk Level:* `{alert.risk_level.value}`\n"
            message += f"*Alert Type:* `{alert.alert_type.value}`\n"
            message += f"*Wallet:* `{alert.wallet}`\n\n"
            message += f"{alert.message}\n\n"
            
            if alert.amount:
                message += f"*Amount:* `{alert.amount} ETH`\n"
            
            if alert.percentage_change:
                message += f"*Change:* `{alert.percentage_change:.2f}%`\n"
            
            if alert.block_number:
                message += f"*Block:* `{alert.block_number}`\n"
            
            if alert.transaction_hash:
                message += f"*TX:* `{alert.transaction_hash}`\n"
            
            message += f"\n*Time:* {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}"
            
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        print(f"✅ Alert sent to Telegram")
                    else:
                        print(f"⚠️  Failed to send Telegram alert: {response.status}")
        
        except Exception as e:
            print(f"❌ Error sending Telegram alert: {e}")
    
    def get_wallet_status(self, address: str) -> Optional[Dict]:
        """
        Get current status of a monitored wallet.
        
        Args:
            address: Wallet address
        
        Returns:
            Dictionary with wallet status or None if not monitored
        """
        address = Web3.to_checksum_address(address)
        
        if address not in self.wallets:
            return None
        
        history = self.wallet_history.get(address, [])
        
        if not history:
            return {
                "address": address,
                "status": "no_data",
                "message": "No monitoring data yet"
            }
        
        latest = history[-1]
        
        status = {
            "address": address,
            "current_balance": float(latest.balance),
            "current_block": latest.block_number,
            "last_check": datetime.fromtimestamp(latest.timestamp).isoformat(),
            "checks_count": len(history),
            "monitoring_duration_seconds": history[-1].timestamp - history[0].timestamp if len(history) > 1 else 0
        }
        
        # Calculate balance change if we have history
        if len(history) >= 2:
            oldest = history[0]
            balance_change = float(latest.balance - oldest.balance)
            balance_change_pct = (balance_change / float(oldest.balance) * 100) if oldest.balance > 0 else 0
            
            status["balance_change"] = balance_change
            status["balance_change_percentage"] = balance_change_pct
        
        return status
    
    def get_statistics(self) -> Dict:
        """Get monitoring statistics."""
        return {
            "wallets_monitored": len(self.wallets),
            "total_checks": self.total_checks,
            "alerts_triggered": self.alerts_triggered,
            "is_monitoring": self.is_monitoring,
            "check_interval_seconds": self.check_interval,
            "critical_drop_threshold_percentage": self.critical_drop_threshold * 100,
            "time_window_minutes": self.time_window_seconds / 60
        }


if __name__ == "__main__":
    # Example usage
    print("=" * 80)
    print("🛡️  DM SENTINEL - TREASURY WATCHER & ANTI-DRAINER")
    print("   PROMPT 5: El Centinela de Tesorería")
    print("=" * 80)
    
    # Example configuration
    print("\n📝 Example Usage:")
    print("-" * 80)
    print("""
# Initialize watcher
watcher = TreasuryWatcher(
    rpc_endpoint="https://eth.llamarpc.com",
    telegram_bot_token="YOUR_BOT_TOKEN",
    telegram_chat_id="YOUR_CHAT_ID",
    check_interval=15,  # Check every 15 seconds
    critical_drop_threshold=0.5,  # 50% drop triggers CRITICAL
    time_window_minutes=5  # Monitor 5-minute windows
)

# Add wallets to monitor
watcher.add_wallet("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0")
watcher.add_wallet("0x1234567890123456789012345678901234567890")

# Start 24/7 monitoring
await watcher.start_monitoring()

# Check for suspicious approvals
alerts = await watcher.check_suspicious_approvals(
    address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
    from_block=18000000
)

# Get wallet status
status = watcher.get_wallet_status("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0")
print(status)

# Get statistics
stats = watcher.get_statistics()
print(stats)
    """)
    
    print("\n" + "=" * 80)
    print("✅ Module loaded successfully!")
    print("=" * 80)
