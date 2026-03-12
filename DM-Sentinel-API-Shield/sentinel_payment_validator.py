"""
DM Sentinel - USDC Payment Validator
PROMPT 4: El Validador de Depósitos USDC (Tech Lead + Pentester)

This module validates USDC (ERC-20) payments on multiple blockchains (Ethereum, Polygon, BSC)
with proper confirmation tracking and security validations.

Author: DM Global Security Team
Created: March 2026
"""

import time
from typing import Dict, Tuple, Optional
from enum import Enum
from decimal import Decimal

try:
    from web3 import Web3
    from web3.exceptions import TransactionNotFound, BlockNotFound
    from eth_typing import ChecksumAddress
except ImportError:
    raise ImportError(
        "Web3.py is required. Install with: pip install web3"
    )


class PaymentStatus(Enum):
    """Payment verification status codes."""
    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"
    REVERTED = "REVERTED"
    INVALID_AMOUNT = "INVALID_AMOUNT"
    INVALID_RECIPIENT = "INVALID_RECIPIENT"
    INVALID_CONTRACT = "INVALID_CONTRACT"
    INSUFFICIENT_CONFIRMATIONS = "INSUFFICIENT_CONFIRMATIONS"
    TRANSACTION_NOT_FOUND = "TRANSACTION_NOT_FOUND"


class BlockchainNetwork(Enum):
    """Supported blockchain networks."""
    ETHEREUM_MAINNET = "ethereum_mainnet"
    POLYGON = "polygon"
    BSC = "bsc"
    ETHEREUM_SEPOLIA = "ethereum_sepolia"  # Testnet


# USDC Contract Addresses (Official)
USDC_CONTRACTS = {
    BlockchainNetwork.ETHEREUM_MAINNET: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    BlockchainNetwork.POLYGON: "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",  # USDC (native)
    BlockchainNetwork.BSC: "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
    BlockchainNetwork.ETHEREUM_SEPOLIA: "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",  # Testnet
}

# DM Global Treasury Addresses (one per network)
DM_GLOBAL_TREASURY = {
    BlockchainNetwork.ETHEREUM_MAINNET: "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",  # Example
    BlockchainNetwork.POLYGON: "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
    BlockchainNetwork.BSC: "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
    BlockchainNetwork.ETHEREUM_SEPOLIA: "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",  # Test
}

# Default RPC Endpoints (can be overridden)
DEFAULT_RPC_ENDPOINTS = {
    BlockchainNetwork.ETHEREUM_MAINNET: "https://eth.llamarpc.com",
    BlockchainNetwork.POLYGON: "https://polygon-rpc.com",
    BlockchainNetwork.BSC: "https://bsc-dataseed.binance.org",
    BlockchainNetwork.ETHEREUM_SEPOLIA: "https://rpc.sepolia.org",
}

# USDC uses 6 decimals (not 18 like ETH/most ERC-20s)
USDC_DECIMALS = 6

# Required block confirmations for statistical finality
REQUIRED_CONFIRMATIONS = 12

# Minimal ERC-20 ABI for Transfer event
ERC20_TRANSFER_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "from", "type": "address"},
            {"indexed": True, "name": "to", "type": "address"},
            {"indexed": False, "name": "value", "type": "uint256"}
        ],
        "name": "Transfer",
        "type": "event"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]


class USDCPaymentValidator:
    """
    USDC Payment Validator for DM Sentinel.
    
    Validates USDC payments with proper confirmation tracking and security checks.
    """
    
    def __init__(
        self,
        network: BlockchainNetwork = BlockchainNetwork.ETHEREUM_MAINNET,
        rpc_endpoint: Optional[str] = None,
        treasury_address: Optional[str] = None
    ):
        """
        Initialize the payment validator.
        
        Args:
            network: Blockchain network to use
            rpc_endpoint: Custom RPC endpoint (optional, uses default if not provided)
            treasury_address: Custom treasury address (optional, uses default if not provided)
        """
        self.network = network
        self.rpc_endpoint = rpc_endpoint or DEFAULT_RPC_ENDPOINTS[network]
        self.treasury_address = treasury_address or DM_GLOBAL_TREASURY[network]
        
        # Initialize Web3
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_endpoint))
            if not self.w3.is_connected():
                raise ConnectionError(f"Failed to connect to {network.value} at {self.rpc_endpoint}")
        except Exception as e:
            raise ConnectionError(f"Web3 initialization failed: {str(e)}")
        
        # Get USDC contract address for this network
        self.usdc_contract_address = USDC_CONTRACTS[network]
        
        # Initialize USDC contract
        self.usdc_contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.usdc_contract_address),
            abi=ERC20_TRANSFER_ABI
        )
        
        print(f"✅ USDC Payment Validator initialized")
        print(f"   Network: {network.value}")
        print(f"   RPC: {self.rpc_endpoint}")
        print(f"   USDC Contract: {self.usdc_contract_address}")
        print(f"   Treasury: {self.treasury_address}")
    
    def verify_usdc_payment(
        self,
        tx_hash: str,
        expected_amount_usd: float,
        tolerance_percentage: float = 0.01  # 1% tolerance for rounding
    ) -> Tuple[PaymentStatus, Dict]:
        """
        Verify a USDC payment transaction.
        
        PROMPT 4 Requirements:
        - Wait for 12 block confirmations before returning SUCCESS
        - Validate 'to' address is DM Global treasury
        - Handle USDC's 6 decimals (not 18)
        - Verify contract address is official USDC
        - Handle failed/reverted transactions
        
        Args:
            tx_hash: Transaction hash to verify
            expected_amount_usd: Expected payment amount in USD
            tolerance_percentage: Allowed difference for floating-point rounding
        
        Returns:
            Tuple of (PaymentStatus, details_dict)
            
        Example:
            >>> validator = USDCPaymentValidator(BlockchainNetwork.ETHEREUM_MAINNET)
            >>> status, details = validator.verify_usdc_payment(
            ...     "0xabc123...",
            ...     100.0  # $100 USDC
            ... )
            >>> if status == PaymentStatus.SUCCESS:
            ...     print("Payment verified!")
        """
        details = {
            "tx_hash": tx_hash,
            "network": self.network.value,
            "expected_amount": expected_amount_usd,
            "actual_amount": None,
            "confirmations": 0,
            "from_address": None,
            "to_address": None,
            "contract_address": None,
            "block_number": None,
            "timestamp": None,
            "error": None
        }
        
        try:
            # Step 1: Fetch transaction receipt
            print(f"\n🔍 Verifying transaction: {tx_hash}")
            print(f"   Expected amount: ${expected_amount_usd} USDC")
            
            try:
                tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                tx = self.w3.eth.get_transaction(tx_hash)
            except TransactionNotFound:
                details["error"] = "Transaction not found on blockchain"
                return PaymentStatus.TRANSACTION_NOT_FOUND, details
            
            # Step 2: Check if transaction was reverted
            if tx_receipt['status'] == 0:
                details["error"] = "Transaction was reverted"
                print(f"   ❌ Transaction reverted")
                return PaymentStatus.REVERTED, details
            
            # Step 3: Verify contract address
            contract_address = tx['to']
            details["contract_address"] = contract_address
            
            if contract_address.lower() != self.usdc_contract_address.lower():
                details["error"] = f"Invalid contract: {contract_address} (expected {self.usdc_contract_address})"
                print(f"   ❌ Invalid contract address")
                return PaymentStatus.INVALID_CONTRACT, details
            
            print(f"   ✅ Contract validated: {contract_address}")
            
            # Step 4: Parse Transfer event from logs
            transfer_event = None
            for log in tx_receipt['logs']:
                try:
                    decoded = self.usdc_contract.events.Transfer().process_log(log)
                    transfer_event = decoded
                    break
                except Exception:
                    continue
            
            if not transfer_event:
                details["error"] = "No Transfer event found in transaction"
                return PaymentStatus.FAILED, details
            
            # Step 5: Extract transfer details
            from_address = transfer_event['args']['from']
            to_address = transfer_event['args']['to']
            value_raw = transfer_event['args']['value']
            
            details["from_address"] = from_address
            details["to_address"] = to_address
            details["block_number"] = tx_receipt['blockNumber']
            
            # Step 6: Validate recipient is DM Global treasury
            if to_address.lower() != self.treasury_address.lower():
                details["error"] = f"Invalid recipient: {to_address} (expected {self.treasury_address})"
                print(f"   ❌ Payment not sent to treasury")
                return PaymentStatus.INVALID_RECIPIENT, details
            
            print(f"   ✅ Recipient validated: {to_address}")
            
            # Step 7: Convert USDC amount (6 decimals, not 18)
            actual_amount = Decimal(value_raw) / Decimal(10 ** USDC_DECIMALS)
            details["actual_amount"] = float(actual_amount)
            
            print(f"   💰 Amount: ${actual_amount} USDC")
            
            # Step 8: Validate amount matches expected (with tolerance)
            expected_decimal = Decimal(str(expected_amount_usd))
            tolerance = expected_decimal * Decimal(str(tolerance_percentage))
            
            if abs(actual_amount - expected_decimal) > tolerance:
                details["error"] = f"Amount mismatch: expected ${expected_decimal}, got ${actual_amount}"
                print(f"   ❌ Amount mismatch")
                return PaymentStatus.INVALID_AMOUNT, details
            
            print(f"   ✅ Amount validated")
            
            # Step 9: Check block confirmations (CRITICAL - Wait for 12 confirmations)
            current_block = self.w3.eth.block_number
            tx_block = tx_receipt['blockNumber']
            confirmations = current_block - tx_block + 1
            details["confirmations"] = confirmations
            
            print(f"   📦 Confirmations: {confirmations}/{REQUIRED_CONFIRMATIONS}")
            
            if confirmations < REQUIRED_CONFIRMATIONS:
                details["error"] = f"Insufficient confirmations: {confirmations}/{REQUIRED_CONFIRMATIONS}"
                print(f"   ⏳ Waiting for more confirmations...")
                return PaymentStatus.INSUFFICIENT_CONFIRMATIONS, details
            
            # Step 10: Get timestamp
            block = self.w3.eth.get_block(tx_block)
            details["timestamp"] = block['timestamp']
            
            # SUCCESS - All validations passed
            print(f"   ✅ Payment verified successfully!")
            return PaymentStatus.SUCCESS, details
        
        except Exception as e:
            details["error"] = f"Unexpected error: {str(e)}"
            print(f"   ❌ Error: {str(e)}")
            return PaymentStatus.FAILED, details
    
    def wait_for_confirmations(
        self,
        tx_hash: str,
        expected_amount_usd: float,
        max_wait_seconds: int = 600,  # 10 minutes default
        poll_interval: int = 15  # Check every 15 seconds
    ) -> Tuple[PaymentStatus, Dict]:
        """
        Wait for transaction to reach required confirmations.
        
        This function will poll the blockchain until the transaction has
        12 confirmations or the timeout is reached.
        
        Args:
            tx_hash: Transaction hash
            expected_amount_usd: Expected payment amount
            max_wait_seconds: Maximum time to wait (default 10 minutes)
            poll_interval: Seconds between checks (default 15 seconds)
        
        Returns:
            Tuple of (PaymentStatus, details_dict)
        """
        print(f"\n⏳ Waiting for {REQUIRED_CONFIRMATIONS} confirmations...")
        print(f"   Max wait time: {max_wait_seconds}s")
        print(f"   Poll interval: {poll_interval}s")
        
        start_time = time.time()
        attempt = 0
        
        while time.time() - start_time < max_wait_seconds:
            attempt += 1
            print(f"\n🔄 Attempt {attempt}")
            
            status, details = self.verify_usdc_payment(tx_hash, expected_amount_usd)
            
            # Return immediately if SUCCESS or terminal failure
            if status == PaymentStatus.SUCCESS:
                print(f"\n🎉 Payment verified after {int(time.time() - start_time)}s")
                return status, details
            
            if status in [
                PaymentStatus.REVERTED,
                PaymentStatus.INVALID_AMOUNT,
                PaymentStatus.INVALID_RECIPIENT,
                PaymentStatus.INVALID_CONTRACT,
                PaymentStatus.TRANSACTION_NOT_FOUND
            ]:
                # Terminal failure - no point waiting
                return status, details
            
            # Wait before next poll
            if time.time() - start_time < max_wait_seconds:
                print(f"   Waiting {poll_interval}s before next check...")
                time.sleep(poll_interval)
        
        # Timeout reached
        print(f"\n⏱️ Timeout reached after {max_wait_seconds}s")
        return PaymentStatus.INSUFFICIENT_CONFIRMATIONS, details
    
    def get_transaction_status(self, tx_hash: str) -> Dict:
        """
        Get quick transaction status without full validation.
        
        Useful for checking if a transaction exists and how many confirmations it has.
        
        Args:
            tx_hash: Transaction hash
        
        Returns:
            Dictionary with status information
        """
        try:
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            current_block = self.w3.eth.block_number
            tx_block = tx_receipt['blockNumber']
            confirmations = current_block - tx_block + 1
            
            return {
                "found": True,
                "status": "success" if tx_receipt['status'] == 1 else "reverted",
                "block_number": tx_block,
                "confirmations": confirmations,
                "has_required_confirmations": confirmations >= REQUIRED_CONFIRMATIONS
            }
        except TransactionNotFound:
            return {
                "found": False,
                "error": "Transaction not found"
            }
        except Exception as e:
            return {
                "found": False,
                "error": str(e)
            }


# Convenience function for quick validation
def verify_payment(
    tx_hash: str,
    expected_amount_usd: float,
    network: BlockchainNetwork = BlockchainNetwork.ETHEREUM_MAINNET,
    wait_for_confirmations: bool = False,
    max_wait_seconds: int = 600
) -> Tuple[PaymentStatus, Dict]:
    """
    Convenience function to verify a USDC payment.
    
    Args:
        tx_hash: Transaction hash
        expected_amount_usd: Expected payment amount in USD
        network: Blockchain network
        wait_for_confirmations: If True, wait for 12 confirmations
        max_wait_seconds: Maximum wait time if waiting for confirmations
    
    Returns:
        Tuple of (PaymentStatus, details_dict)
    
    Example:
        >>> status, details = verify_payment(
        ...     "0xabc123...",
        ...     100.0,
        ...     network=BlockchainNetwork.POLYGON,
        ...     wait_for_confirmations=True
        ... )
        >>> print(status)
        PaymentStatus.SUCCESS
    """
    validator = USDCPaymentValidator(network=network)
    
    if wait_for_confirmations:
        return validator.wait_for_confirmations(
            tx_hash,
            expected_amount_usd,
            max_wait_seconds=max_wait_seconds
        )
    else:
        return validator.verify_usdc_payment(tx_hash, expected_amount_usd)


if __name__ == "__main__":
    # Example usage
    print("=" * 80)
    print("🛡️  DM SENTINEL - USDC PAYMENT VALIDATOR")
    print("   PROMPT 4: El Validador de Depósitos USDC")
    print("=" * 80)
    
    # Example 1: Ethereum Mainnet validation
    print("\n📝 Example 1: Ethereum Mainnet Validation")
    print("-" * 80)
    try:
        validator = USDCPaymentValidator(BlockchainNetwork.ETHEREUM_MAINNET)
        print("\nValidator initialized successfully!")
        print("\nUsage example:")
        print('  status, details = validator.verify_usdc_payment(')
        print('      tx_hash="0x...",')
        print('      expected_amount_usd=100.0')
        print('  )')
        print('  if status == PaymentStatus.SUCCESS:')
        print('      print("Payment verified!")')
    except Exception as e:
        print(f"⚠️  Error: {e}")
        print("   (This is expected if RPC endpoint is unavailable)")
    
    # Example 2: Show supported networks
    print("\n📝 Example 2: Supported Networks")
    print("-" * 80)
    for network in BlockchainNetwork:
        print(f"  • {network.value}")
        print(f"    USDC: {USDC_CONTRACTS[network]}")
        print(f"    Treasury: {DM_GLOBAL_TREASURY[network]}")
    
    print("\n" + "=" * 80)
    print("✅ Module loaded successfully!")
    print("=" * 80)
