"""
DM Sentinel - Payment Gateway Hub
PROMPT 6: El Hub de Pasarelas Fiat-Crypto (Fullstack + PO)

Author: DM Sentinel Security Team
Role: Fullstack Developer + Product Owner
Date: 2026-03-12

Purpose:
    Unified payment orchestrator for fiat and crypto payment methods.
    Handles webhooks from Stripe, Mercado Pago, Pix, and USDC.
    Manages payment state transitions and activates treasury monitoring.

Payment Flow:
    1. Webhook received from payment provider
    2. Validate webhook signature
    3. Update CRM status:
       - Fiat (Stripe/MP/Pix): FIAT_CONFIRMED
       - Crypto (USDC): WAITING_CONFIRMATIONS → WEB3_CONFIRMED
    4. Activate TreasuryWatcher for client wallet
    5. Persist client_id → target_wallet mapping

Dependencies:
    - FastAPI (web framework)
    - uvicorn (ASGI server)
    - Web3.py (blockchain integration)
    - sentinel_payment_validator (USDC validation)
    - sentinel_treasury_monitor (wallet monitoring)
"""

import asyncio
import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Set
from pathlib import Path
import sqlite3

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import DM Sentinel modules
try:
    from sentinel_payment_validator import USDCPaymentValidator, USDCPayment
    from sentinel_treasury_monitor import TreasuryWatcher
except ImportError:
    print("⚠️  Warning: DM Sentinel modules not found. Running in standalone mode.")
    USDCPaymentValidator = None
    TreasuryWatcher = None


# ============================================================================
# Enums and Data Models
# ============================================================================

class PaymentProvider(Enum):
    """Supported payment providers."""
    STRIPE = "stripe"
    MERCADO_PAGO = "mercado_pago"
    PIX = "pix"
    USDC = "usdc"


class PaymentStatus(Enum):
    """Payment lifecycle states."""
    PENDING = "PENDING"
    FIAT_CONFIRMED = "FIAT_CONFIRMED"
    WAITING_CONFIRMATIONS = "WAITING_CONFIRMATIONS"
    WEB3_CONFIRMED = "WEB3_CONFIRMED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class ServiceTier(Enum):
    """DM Sentinel service tiers."""
    BASIC = "BASIC"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"


@dataclass
class ClientWalletMapping:
    """Persistent mapping of client to wallet."""
    client_id: str
    target_wallet: str
    service_tier: ServiceTier
    payment_provider: PaymentProvider
    payment_amount: Decimal
    payment_status: PaymentStatus
    created_at: float = field(default_factory=time.time)
    confirmed_at: Optional[float] = None
    monitoring_active: bool = False


class WebhookPayload(BaseModel):
    """Generic webhook payload."""
    provider: str
    event_type: str
    data: Dict
    signature: Optional[str] = None


class StripeWebhookData(BaseModel):
    """Stripe webhook specific data."""
    payment_intent_id: str
    amount: int
    currency: str
    customer_id: str
    metadata: Dict = Field(default_factory=dict)


class MercadoPagoWebhookData(BaseModel):
    """Mercado Pago webhook specific data."""
    payment_id: str
    status: str
    transaction_amount: float
    currency_id: str
    payer_email: str
    external_reference: Optional[str] = None


class PixWebhookData(BaseModel):
    """Pix webhook specific data."""
    txid: str
    amount: float
    payer_document: str
    end_to_end_id: str


class USDCWebhookData(BaseModel):
    """USDC payment data."""
    tx_hash: str
    from_address: str
    to_address: str
    amount: float
    confirmations: int


class PaymentConfirmationResponse(BaseModel):
    """Response after payment confirmation."""
    success: bool
    client_id: str
    payment_status: PaymentStatus
    monitoring_activated: bool
    message: str


# ============================================================================
# Payment Gateway Hub
# ============================================================================

class PaymentGatewayHub:
    """
    Unified payment orchestrator for fiat and crypto payments.
    
    Features:
    - Webhook handling for multiple payment providers
    - Payment state management (PENDING → CONFIRMED)
    - CRM integration
    - TreasuryWatcher activation
    - Persistent client-wallet mapping
    
    Architecture:
    1. Webhook received → validate signature
    2. Extract payment data → normalize across providers
    3. Update CRM status → FIAT_CONFIRMED or WAITING_CONFIRMATIONS
    4. Activate treasury monitoring → TreasuryWatcher for client wallet
    5. Persist mapping → client_id → target_wallet
    """
    
    def __init__(
        self,
        db_path: str = "sentinel_gateway.db",
        rpc_endpoint: str = "https://eth.llamarpc.com",
        usdc_contract: str = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None
    ):
        """
        Initialize Payment Gateway Hub.
        
        Args:
            db_path: Path to SQLite database for persistent storage
            rpc_endpoint: Ethereum RPC endpoint
            usdc_contract: USDC contract address
            telegram_bot_token: Telegram bot token for alerts
            telegram_chat_id: Telegram chat ID for alerts
        """
        self.db_path = db_path
        self.rpc_endpoint = rpc_endpoint
        self.usdc_contract = usdc_contract
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        
        # Initialize components
        self._init_database()
        
        # Payment validator (USDC)
        if USDCPaymentValidator:
            self.usdc_validator = USDCPaymentValidator(
                rpc_endpoint=rpc_endpoint,
                usdc_contract=usdc_contract
            )
        else:
            self.usdc_validator = None
        
        # Treasury watcher (24/7 monitoring)
        if TreasuryWatcher:
            self.treasury_watcher = TreasuryWatcher(
                rpc_endpoint=rpc_endpoint,
                telegram_bot_token=telegram_bot_token,
                telegram_chat_id=telegram_chat_id
            )
        else:
            self.treasury_watcher = None
        
        # Webhook secrets (store in environment variables in production)
        self.webhook_secrets = {
            PaymentProvider.STRIPE: "whsec_stripe_secret_key",
            PaymentProvider.MERCADO_PAGO: "mercado_pago_webhook_secret",
            PaymentProvider.PIX: "pix_webhook_secret",
            PaymentProvider.USDC: "usdc_webhook_secret"
        }
        
        # Statistics
        self.total_payments = 0
        self.confirmed_payments = 0
        self.monitoring_activations = 0
        
        print("🛡️  DM Sentinel - Payment Gateway Hub initialized")
        print(f"   Database: {db_path}")
        print(f"   RPC: {rpc_endpoint}")
        print(f"   USDC Contract: {usdc_contract}")
    
    def _init_database(self) -> None:
        """Initialize SQLite database for persistent storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create client_wallet_mappings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS client_wallet_mappings (
                client_id TEXT PRIMARY KEY,
                target_wallet TEXT NOT NULL,
                service_tier TEXT NOT NULL,
                payment_provider TEXT NOT NULL,
                payment_amount REAL NOT NULL,
                payment_status TEXT NOT NULL,
                created_at REAL NOT NULL,
                confirmed_at REAL,
                monitoring_active INTEGER DEFAULT 0
            )
        """)
        
        # Create payment_events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id TEXT NOT NULL,
                provider TEXT NOT NULL,
                event_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp REAL NOT NULL,
                FOREIGN KEY (client_id) REFERENCES client_wallet_mappings(client_id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Database initialized")
    
    def _save_mapping(self, mapping: ClientWalletMapping) -> None:
        """Save client-wallet mapping to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO client_wallet_mappings
            (client_id, target_wallet, service_tier, payment_provider, 
             payment_amount, payment_status, created_at, confirmed_at, monitoring_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mapping.client_id,
            mapping.target_wallet,
            mapping.service_tier.value,
            mapping.payment_provider.value,
            float(mapping.payment_amount),
            mapping.payment_status.value,
            mapping.created_at,
            mapping.confirmed_at,
            1 if mapping.monitoring_active else 0
        ))
        
        conn.commit()
        conn.close()
    
    def _get_mapping(self, client_id: str) -> Optional[ClientWalletMapping]:
        """Retrieve client-wallet mapping from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT client_id, target_wallet, service_tier, payment_provider,
                   payment_amount, payment_status, created_at, confirmed_at, monitoring_active
            FROM client_wallet_mappings
            WHERE client_id = ?
        """, (client_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return ClientWalletMapping(
                client_id=row[0],
                target_wallet=row[1],
                service_tier=ServiceTier(row[2]),
                payment_provider=PaymentProvider(row[3]),
                payment_amount=Decimal(str(row[4])),
                payment_status=PaymentStatus(row[5]),
                created_at=row[6],
                confirmed_at=row[7],
                monitoring_active=bool(row[8])
            )
        return None
    
    def _log_payment_event(
        self,
        client_id: str,
        provider: PaymentProvider,
        event_type: str,
        payload: Dict,
        status: PaymentStatus
    ) -> None:
        """Log payment event to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO payment_events
            (client_id, provider, event_type, payload, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            client_id,
            provider.value,
            event_type,
            json.dumps(payload),
            status.value,
            time.time()
        ))
        
        conn.commit()
        conn.close()
    
    def _verify_webhook_signature(
        self,
        provider: PaymentProvider,
        payload: bytes,
        signature: str
    ) -> bool:
        """
        Verify webhook signature for security.
        
        Args:
            provider: Payment provider
            payload: Raw webhook payload
            signature: Signature from webhook header
        
        Returns:
            True if signature is valid
        """
        secret = self.webhook_secrets.get(provider)
        if not secret:
            print(f"⚠️  No webhook secret configured for {provider.value}")
            return True  # Allow in development mode
        
        # Compute HMAC SHA256 signature
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    async def handle_stripe_webhook(
        self,
        payload: Dict,
        signature: str
    ) -> PaymentConfirmationResponse:
        """
        Handle Stripe webhook.
        
        Stripe Events:
        - payment_intent.succeeded
        - payment_intent.payment_failed
        - charge.refunded
        
        Args:
            payload: Stripe webhook payload
            signature: Stripe signature header
        
        Returns:
            Payment confirmation response
        """
        event_type = payload.get("type")
        data = payload.get("data", {}).get("object", {})
        
        print(f"\n{'='*80}")
        print(f"💳 STRIPE WEBHOOK RECEIVED")
        print(f"{'='*80}")
        print(f"Event: {event_type}")
        print(f"Payment Intent: {data.get('id')}")
        print(f"Amount: ${data.get('amount', 0) / 100:.2f}")
        
        if event_type == "payment_intent.succeeded":
            # Extract payment details
            client_id = data.get("metadata", {}).get("client_id")
            target_wallet = data.get("metadata", {}).get("target_wallet")
            service_tier = data.get("metadata", {}).get("service_tier", "BASIC")
            amount = Decimal(str(data.get("amount", 0))) / 100
            
            if not client_id or not target_wallet:
                raise HTTPException(
                    status_code=400,
                    detail="Missing client_id or target_wallet in metadata"
                )
            
            # Create mapping
            mapping = ClientWalletMapping(
                client_id=client_id,
                target_wallet=target_wallet,
                service_tier=ServiceTier(service_tier),
                payment_provider=PaymentProvider.STRIPE,
                payment_amount=amount,
                payment_status=PaymentStatus.FIAT_CONFIRMED,
                confirmed_at=time.time()
            )
            
            # Save to database
            self._save_mapping(mapping)
            self._log_payment_event(
                client_id=client_id,
                provider=PaymentProvider.STRIPE,
                event_type=event_type,
                payload=payload,
                status=PaymentStatus.FIAT_CONFIRMED
            )
            
            # Activate treasury monitoring
            monitoring_activated = await self._activate_treasury_monitoring(mapping)
            
            self.total_payments += 1
            self.confirmed_payments += 1
            
            print(f"✅ Stripe payment confirmed")
            print(f"   Client: {client_id}")
            print(f"   Wallet: {target_wallet}")
            print(f"   Amount: ${amount}")
            print(f"   Monitoring: {'ACTIVE' if monitoring_activated else 'INACTIVE'}")
            print(f"{'='*80}\n")
            
            return PaymentConfirmationResponse(
                success=True,
                client_id=client_id,
                payment_status=PaymentStatus.FIAT_CONFIRMED,
                monitoring_activated=monitoring_activated,
                message="Stripe payment confirmed successfully"
            )
        
        elif event_type == "payment_intent.payment_failed":
            client_id = data.get("metadata", {}).get("client_id")
            if client_id:
                mapping = self._get_mapping(client_id)
                if mapping:
                    mapping.payment_status = PaymentStatus.FAILED
                    self._save_mapping(mapping)
            
            return PaymentConfirmationResponse(
                success=False,
                client_id=client_id or "unknown",
                payment_status=PaymentStatus.FAILED,
                monitoring_activated=False,
                message="Stripe payment failed"
            )
        
        return PaymentConfirmationResponse(
            success=True,
            client_id="unknown",
            payment_status=PaymentStatus.PENDING,
            monitoring_activated=False,
            message=f"Stripe event {event_type} acknowledged"
        )
    
    async def handle_mercado_pago_webhook(
        self,
        payload: Dict,
        signature: str
    ) -> PaymentConfirmationResponse:
        """
        Handle Mercado Pago webhook.
        
        Mercado Pago Events:
        - payment.approved
        - payment.rejected
        - payment.refunded
        
        Args:
            payload: Mercado Pago webhook payload
            signature: Mercado Pago signature header
        
        Returns:
            Payment confirmation response
        """
        action = payload.get("action")
        data = payload.get("data", {})
        
        print(f"\n{'='*80}")
        print(f"💰 MERCADO PAGO WEBHOOK RECEIVED")
        print(f"{'='*80}")
        print(f"Action: {action}")
        print(f"Payment ID: {data.get('id')}")
        
        if action == "payment.approved":
            # Extract payment details (from external_reference)
            external_reference = data.get("external_reference", "")
            parts = external_reference.split("|")
            
            if len(parts) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid external_reference format"
                )
            
            client_id = parts[0]
            target_wallet = parts[1]
            service_tier = parts[2] if len(parts) > 2 else "BASIC"
            amount = Decimal(str(data.get("transaction_amount", 0)))
            
            # Create mapping
            mapping = ClientWalletMapping(
                client_id=client_id,
                target_wallet=target_wallet,
                service_tier=ServiceTier(service_tier),
                payment_provider=PaymentProvider.MERCADO_PAGO,
                payment_amount=amount,
                payment_status=PaymentStatus.FIAT_CONFIRMED,
                confirmed_at=time.time()
            )
            
            # Save to database
            self._save_mapping(mapping)
            self._log_payment_event(
                client_id=client_id,
                provider=PaymentProvider.MERCADO_PAGO,
                event_type=action,
                payload=payload,
                status=PaymentStatus.FIAT_CONFIRMED
            )
            
            # Activate treasury monitoring
            monitoring_activated = await self._activate_treasury_monitoring(mapping)
            
            self.total_payments += 1
            self.confirmed_payments += 1
            
            print(f"✅ Mercado Pago payment confirmed")
            print(f"   Client: {client_id}")
            print(f"   Wallet: {target_wallet}")
            print(f"   Amount: ${amount}")
            print(f"   Monitoring: {'ACTIVE' if monitoring_activated else 'INACTIVE'}")
            print(f"{'='*80}\n")
            
            return PaymentConfirmationResponse(
                success=True,
                client_id=client_id,
                payment_status=PaymentStatus.FIAT_CONFIRMED,
                monitoring_activated=monitoring_activated,
                message="Mercado Pago payment confirmed successfully"
            )
        
        return PaymentConfirmationResponse(
            success=True,
            client_id="unknown",
            payment_status=PaymentStatus.PENDING,
            monitoring_activated=False,
            message=f"Mercado Pago event {action} acknowledged"
        )
    
    async def handle_pix_webhook(
        self,
        payload: Dict,
        signature: str
    ) -> PaymentConfirmationResponse:
        """
        Handle Pix webhook.
        
        Pix Events:
        - pix.received
        - pix.refunded
        
        Args:
            payload: Pix webhook payload
            signature: Pix signature header
        
        Returns:
            Payment confirmation response
        """
        event_type = payload.get("event")
        data = payload.get("pix", {})
        
        print(f"\n{'='*80}")
        print(f"🇧🇷 PIX WEBHOOK RECEIVED")
        print(f"{'='*80}")
        print(f"Event: {event_type}")
        print(f"TXID: {data.get('txid')}")
        
        if event_type == "pix.received":
            # Extract payment details
            txid = data.get("txid")
            amount = Decimal(str(data.get("valor", 0)))
            
            # Parse client_id and target_wallet from txid or metadata
            metadata = data.get("infoAdicionais", [])
            client_id = None
            target_wallet = None
            service_tier = "BASIC"
            
            for info in metadata:
                if info.get("nome") == "client_id":
                    client_id = info.get("valor")
                elif info.get("nome") == "target_wallet":
                    target_wallet = info.get("valor")
                elif info.get("nome") == "service_tier":
                    service_tier = info.get("valor")
            
            if not client_id or not target_wallet:
                raise HTTPException(
                    status_code=400,
                    detail="Missing client_id or target_wallet in Pix metadata"
                )
            
            # Create mapping
            mapping = ClientWalletMapping(
                client_id=client_id,
                target_wallet=target_wallet,
                service_tier=ServiceTier(service_tier),
                payment_provider=PaymentProvider.PIX,
                payment_amount=amount,
                payment_status=PaymentStatus.FIAT_CONFIRMED,
                confirmed_at=time.time()
            )
            
            # Save to database
            self._save_mapping(mapping)
            self._log_payment_event(
                client_id=client_id,
                provider=PaymentProvider.PIX,
                event_type=event_type,
                payload=payload,
                status=PaymentStatus.FIAT_CONFIRMED
            )
            
            # Activate treasury monitoring
            monitoring_activated = await self._activate_treasury_monitoring(mapping)
            
            self.total_payments += 1
            self.confirmed_payments += 1
            
            print(f"✅ Pix payment confirmed")
            print(f"   Client: {client_id}")
            print(f"   Wallet: {target_wallet}")
            print(f"   Amount: R$ {amount}")
            print(f"   Monitoring: {'ACTIVE' if monitoring_activated else 'INACTIVE'}")
            print(f"{'='*80}\n")
            
            return PaymentConfirmationResponse(
                success=True,
                client_id=client_id,
                payment_status=PaymentStatus.FIAT_CONFIRMED,
                monitoring_activated=monitoring_activated,
                message="Pix payment confirmed successfully"
            )
        
        return PaymentConfirmationResponse(
            success=True,
            client_id="unknown",
            payment_status=PaymentStatus.PENDING,
            monitoring_activated=False,
            message=f"Pix event {event_type} acknowledged"
        )
    
    async def handle_usdc_webhook(
        self,
        payload: Dict,
        signature: str
    ) -> PaymentConfirmationResponse:
        """
        Handle USDC payment webhook.
        
        USDC Payment Flow:
        1. Transaction detected → WAITING_CONFIRMATIONS
        2. 12 confirmations reached → WEB3_CONFIRMED
        3. Activate treasury monitoring
        
        Args:
            payload: USDC webhook payload
            signature: USDC signature header
        
        Returns:
            Payment confirmation response
        """
        tx_hash = payload.get("tx_hash")
        from_address = payload.get("from_address")
        to_address = payload.get("to_address")
        amount = Decimal(str(payload.get("amount", 0)))
        confirmations = payload.get("confirmations", 0)
        
        print(f"\n{'='*80}")
        print(f"💎 USDC WEBHOOK RECEIVED")
        print(f"{'='*80}")
        print(f"TX Hash: {tx_hash}")
        print(f"From: {from_address}")
        print(f"To: {to_address}")
        print(f"Amount: ${amount} USDC")
        print(f"Confirmations: {confirmations}/12")
        
        # Extract client_id from metadata (stored in payment validator)
        client_id = payload.get("client_id")
        target_wallet = from_address  # Client's wallet
        service_tier = payload.get("service_tier", "BASIC")
        
        if not client_id:
            raise HTTPException(
                status_code=400,
                detail="Missing client_id in USDC webhook"
            )
        
        # Determine status based on confirmations
        if confirmations < 12:
            status = PaymentStatus.WAITING_CONFIRMATIONS
            confirmed_at = None
        else:
            status = PaymentStatus.WEB3_CONFIRMED
            confirmed_at = time.time()
        
        # Create or update mapping
        mapping = ClientWalletMapping(
            client_id=client_id,
            target_wallet=target_wallet,
            service_tier=ServiceTier(service_tier),
            payment_provider=PaymentProvider.USDC,
            payment_amount=amount,
            payment_status=status,
            confirmed_at=confirmed_at
        )
        
        # Save to database
        self._save_mapping(mapping)
        self._log_payment_event(
            client_id=client_id,
            provider=PaymentProvider.USDC,
            event_type=f"confirmations_{confirmations}",
            payload=payload,
            status=status
        )
        
        monitoring_activated = False
        
        # Activate treasury monitoring if fully confirmed
        if status == PaymentStatus.WEB3_CONFIRMED:
            monitoring_activated = await self._activate_treasury_monitoring(mapping)
            self.confirmed_payments += 1
        
        self.total_payments += 1
        
        print(f"✅ USDC payment {'confirmed' if status == PaymentStatus.WEB3_CONFIRMED else 'waiting'}")
        print(f"   Client: {client_id}")
        print(f"   Wallet: {target_wallet}")
        print(f"   Amount: ${amount} USDC")
        print(f"   Status: {status.value}")
        print(f"   Monitoring: {'ACTIVE' if monitoring_activated else 'INACTIVE'}")
        print(f"{'='*80}\n")
        
        return PaymentConfirmationResponse(
            success=True,
            client_id=client_id,
            payment_status=status,
            monitoring_activated=monitoring_activated,
            message=f"USDC payment {status.value.lower()}"
        )
    
    async def _activate_treasury_monitoring(
        self,
        mapping: ClientWalletMapping
    ) -> bool:
        """
        Activate TreasuryWatcher for client wallet.
        
        Args:
            mapping: Client-wallet mapping
        
        Returns:
            True if monitoring was activated successfully
        """
        if not self.treasury_watcher:
            print("⚠️  TreasuryWatcher not available")
            return False
        
        try:
            # Add wallet to treasury watcher
            self.treasury_watcher.add_wallet(mapping.target_wallet)
            
            # Update mapping
            mapping.monitoring_active = True
            self._save_mapping(mapping)
            
            self.monitoring_activations += 1
            
            print(f"🛡️  Treasury monitoring activated for {mapping.target_wallet}")
            
            return True
        
        except Exception as e:
            print(f"❌ Failed to activate treasury monitoring: {e}")
            return False
    
    def get_client_status(self, client_id: str) -> Optional[Dict]:
        """
        Get client payment and monitoring status.
        
        Args:
            client_id: Client ID
        
        Returns:
            Client status dictionary or None
        """
        mapping = self._get_mapping(client_id)
        
        if not mapping:
            return None
        
        return {
            "client_id": mapping.client_id,
            "target_wallet": mapping.target_wallet,
            "service_tier": mapping.service_tier.value,
            "payment_provider": mapping.payment_provider.value,
            "payment_amount": float(mapping.payment_amount),
            "payment_status": mapping.payment_status.value,
            "created_at": datetime.fromtimestamp(mapping.created_at).isoformat(),
            "confirmed_at": datetime.fromtimestamp(mapping.confirmed_at).isoformat() if mapping.confirmed_at else None,
            "monitoring_active": mapping.monitoring_active
        }
    
    def get_statistics(self) -> Dict:
        """Get gateway statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM client_wallet_mappings")
        total_clients = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM client_wallet_mappings WHERE monitoring_active = 1")
        active_monitoring = cursor.fetchone()[0]
        
        cursor.execute("SELECT payment_provider, COUNT(*) FROM client_wallet_mappings GROUP BY payment_provider")
        payment_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_payments": self.total_payments,
            "confirmed_payments": self.confirmed_payments,
            "monitoring_activations": self.monitoring_activations,
            "total_clients": total_clients,
            "active_monitoring": active_monitoring,
            "payment_breakdown": payment_breakdown
        }


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="DM Sentinel - Payment Gateway Hub",
    description="Unified payment orchestrator for fiat and crypto payments",
    version="1.0.0"
)

# Initialize gateway hub
gateway_hub = PaymentGatewayHub()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "DM Sentinel Payment Gateway Hub",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/payment/webhook/{provider}")
async def payment_webhook(
    provider: str,
    request: Request,
    background_tasks: BackgroundTasks,
    signature: Optional[str] = Header(None, alias="X-Signature")
):
    """
    Unified webhook endpoint for all payment providers.
    
    Supported providers:
    - stripe
    - mercado_pago
    - pix
    - usdc
    
    Args:
        provider: Payment provider name
        request: FastAPI request object
        background_tasks: Background tasks for async processing
        signature: Webhook signature header
    
    Returns:
        Payment confirmation response
    """
    try:
        # Parse provider
        try:
            provider_enum = PaymentProvider(provider)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider: {provider}"
            )
        
        # Get raw payload
        raw_payload = await request.body()
        payload = await request.json()
        
        # Verify signature
        if signature:
            is_valid = gateway_hub._verify_webhook_signature(
                provider=provider_enum,
                payload=raw_payload,
                signature=signature
            )
            
            if not is_valid:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid webhook signature"
                )
        
        # Route to provider-specific handler
        if provider_enum == PaymentProvider.STRIPE:
            response = await gateway_hub.handle_stripe_webhook(payload, signature or "")
        
        elif provider_enum == PaymentProvider.MERCADO_PAGO:
            response = await gateway_hub.handle_mercado_pago_webhook(payload, signature or "")
        
        elif provider_enum == PaymentProvider.PIX:
            response = await gateway_hub.handle_pix_webhook(payload, signature or "")
        
        elif provider_enum == PaymentProvider.USDC:
            response = await gateway_hub.handle_usdc_webhook(payload, signature or "")
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Provider {provider} not implemented"
            )
        
        return response
    
    except HTTPException:
        raise
    
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/v1/client/{client_id}/status")
async def get_client_status(client_id: str):
    """
    Get client payment and monitoring status.
    
    Args:
        client_id: Client ID
    
    Returns:
        Client status information
    """
    status = gateway_hub.get_client_status(client_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Client {client_id} not found"
        )
    
    return status


@app.get("/api/v1/statistics")
async def get_statistics():
    """Get gateway statistics."""
    return gateway_hub.get_statistics()


@app.post("/api/v1/monitoring/start")
async def start_monitoring():
    """Start treasury monitoring (if not already running)."""
    if not gateway_hub.treasury_watcher:
        raise HTTPException(
            status_code=503,
            detail="TreasuryWatcher not available"
        )
    
    # Start monitoring in background
    asyncio.create_task(gateway_hub.treasury_watcher.start_monitoring())
    
    return {
        "success": True,
        "message": "Treasury monitoring started"
    }


@app.post("/api/v1/monitoring/stop")
async def stop_monitoring():
    """Stop treasury monitoring."""
    if not gateway_hub.treasury_watcher:
        raise HTTPException(
            status_code=503,
            detail="TreasuryWatcher not available"
        )
    
    gateway_hub.treasury_watcher.stop_monitoring()
    
    return {
        "success": True,
        "message": "Treasury monitoring stopped"
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🛡️  DM SENTINEL - PAYMENT GATEWAY HUB")
    print("   PROMPT 6: El Hub de Pasarelas Fiat-Crypto")
    print("=" * 80)
    print("Starting FastAPI server...")
    print("Endpoints:")
    print("  POST /api/v1/payment/webhook/{provider}")
    print("  GET  /api/v1/client/{client_id}/status")
    print("  GET  /api/v1/statistics")
    print("  POST /api/v1/monitoring/start")
    print("  POST /api/v1/monitoring/stop")
    print("=" * 80 + "\n")
    
    # Run FastAPI with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
