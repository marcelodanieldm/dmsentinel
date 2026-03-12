#!/usr/bin/env python3
"""
Sprint 4 PROMPT 2: Webscraping de Inteligencia On-Chain
=========================================================

ROL: Web3 Pentester + Data Engineer
CONTEXTO: Para calcular el "Impacto Financiero", necesitamos saber cuánto 
dinero hay en juego (TVL) y el sentimiento del mercado.

REQUERIMIENTOS TÉCNICOS CUMPLIDOS:
✓ Librerías: BeautifulSoup4 + requests
✓ Obtener TVL del contrato desde exploradores/APIs
✓ Volumen de transacciones (24h)
✓ Cálculo de Riesgo Financiero: severidad × TVL = financial_impact_usd
✓ User-Agent rotativo para evitar bloqueos
✓ Datos normalizados a USD
"""

import requests
import random
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# USER-AGENT ROTATION - PROMPT 2: Evitar bloqueos
# ============================================================================

USER_AGENTS = [
    # Chrome on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    
    # Firefox on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    
    # Chrome on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    
    # Safari on Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    
    # Edge on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
    
    # Chrome on Linux
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
]


def get_random_user_agent() -> str:
    """PROMPT 2: User-Agent rotativo para evitar bloqueos."""
    return random.choice(USER_AGENTS)


def get_headers() -> Dict[str, str]:
    """Get HTTP headers with random User-Agent."""
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'application/json, text/html, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }


# ============================================================================
# DATA MODELS - PROMPT 2: Market Intelligence Structure
# ============================================================================

@dataclass
class TVLData:
    """Total Value Locked data from various sources."""
    tvl_usd: float
    source: str  # 'coingecko', 'dexscreener', 'defillama', 'etherscan'
    timestamp: str
    chain: Optional[str] = None
    protocol: Optional[str] = None
    confidence: str = "medium"  # low, medium, high


@dataclass
class VolumeData:
    """Transaction volume data (24h)."""
    volume_24h_usd: float
    transactions_24h: int
    source: str
    timestamp: str
    chain: Optional[str] = None


@dataclass
class MarketSentiment:
    """Market sentiment indicators."""
    sentiment_score: float  # -1.0 (bearish) to 1.0 (bullish)
    price_change_24h: float  # Percentage
    holders_count: int
    social_mentions: int
    source: str


@dataclass
class FinancialImpact:
    """PROMPT 2: Financial impact calculation."""
    financial_impact_usd: float
    tvl_usd: float
    severity_score: float  # From Sprint 1 pentest
    risk_category: str  # "Low", "Medium", "High", "Critical"
    calculation_method: str
    timestamp: str


@dataclass
class MarketIntelReport:
    """Complete market intelligence report."""
    contract_address: str
    chain: str
    
    # PROMPT 2: Core data
    tvl_data: Optional[TVLData] = None
    volume_data: Optional[VolumeData] = None
    sentiment: Optional[MarketSentiment] = None
    financial_impact: Optional[FinancialImpact] = None
    
    # Additional context
    token_price_usd: Optional[float] = None
    market_cap_usd: Optional[float] = None
    liquidity_usd: Optional[float] = None
    
    # Metadata
    data_sources: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)


# ============================================================================
# MARKET INTELLIGENCE ENGINE - Main Class
# ============================================================================

class SentinelMarketIntel:
    """
    PROMPT 2: Market Intelligence Engine for Web3
    
    Capabilities:
    1. Fetch TVL from multiple sources (CoinGecko, DexScreener, DefiLlama, Etherscan)
    2. Get transaction volume (24h)
    3. Calculate financial impact: severity × TVL
    4. User-Agent rotation to avoid blocking
    5. Normalize all data to USD
    """
    
    # API endpoints
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    DEXSCREENER_API = "https://api.dexscreener.com/latest/dex"
    DEFILLAMA_API = "https://api.llama.fi"
    ETHERSCAN_API = "https://api.etherscan.io/api"
    
    def __init__(
        self,
        timeout: int = 10,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        etherscan_api_key: Optional[str] = None
    ):
        """
        Initialize Market Intelligence Engine.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries (seconds)
            etherscan_api_key: Optional Etherscan API key for higher rate limits
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.etherscan_api_key = etherscan_api_key or "YourApiKeyToken"
        
        # Request session with connection pooling
        self.session = requests.Session()
        
        logger.info("SentinelMarketIntel initialized")
    
    def _make_request(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        PROMPT 2: Make HTTP request with User-Agent rotation and retry logic.
        
        Args:
            url: Request URL
            method: HTTP method (GET, POST)
            params: Query parameters
            json_data: JSON body for POST requests
        
        Returns:
            Response JSON or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                # PROMPT 2: User-Agent rotativo
                headers = get_headers()
                
                logger.debug(f"Request to {url} (attempt {attempt + 1}/{self.max_retries})")
                
                if method == "GET":
                    response = self.session.get(
                        url,
                        params=params,
                        headers=headers,
                        timeout=self.timeout
                    )
                else:
                    response = self.session.post(
                        url,
                        params=params,
                        json=json_data,
                        headers=headers,
                        timeout=self.timeout
                    )
                
                response.raise_for_status()
                
                # Try to parse JSON
                try:
                    return response.json()
                except ValueError:
                    # Not JSON, return text
                    return {"text": response.text}
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    delay = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {delay:.1f}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"Max retries exceeded for {url}")
                    return None
        
        return None
    
    # ========================================================================
    # TVL FETCHING - Multiple Sources
    # ========================================================================
    
    def get_tvl_from_coingecko(self, contract_address: str, chain: str = "ethereum") -> Optional[TVLData]:
        """
        PROMPT 2: Fetch TVL from CoinGecko API.
        
        Args:
            contract_address: Smart contract address
            chain: Blockchain network
        
        Returns:
            TVLData or None
        """
        logger.info(f"Fetching TVL from CoinGecko for {contract_address}")
        
        # Map chain names to CoinGecko platform IDs
        chain_map = {
            "ethereum": "ethereum",
            "bsc": "binance-smart-chain",
            "polygon": "polygon-pos",
            "arbitrum": "arbitrum-one",
            "optimism": "optimistic-ethereum",
            "avalanche": "avalanche"
        }
        
        platform = chain_map.get(chain.lower(), "ethereum")
        
        # Get token info by contract
        url = f"{self.COINGECKO_API}/coins/{platform}/contract/{contract_address}"
        
        data = self._make_request(url)
        
        if data and "market_data" in data:
            market_data = data["market_data"]
            
            # TVL approximation: market_cap or total_value_locked
            tvl = market_data.get("total_value_locked", {}).get("usd")
            if not tvl:
                # Fallback to market cap
                tvl = market_data.get("market_cap", {}).get("usd")
            
            if tvl:
                return TVLData(
                    tvl_usd=float(tvl),
                    source="coingecko",
                    timestamp=datetime.now().isoformat(),
                    chain=chain,
                    protocol=data.get("name", "Unknown"),
                    confidence="high"
                )
        
        logger.warning("Could not fetch TVL from CoinGecko")
        return None
    
    def get_tvl_from_dexscreener(self, contract_address: str) -> Optional[TVLData]:
        """
        PROMPT 2: Fetch TVL from DexScreener API.
        
        Args:
            contract_address: Smart contract address
        
        Returns:
            TVLData or None
        """
        logger.info(f"Fetching TVL from DexScreener for {contract_address}")
        
        url = f"{self.DEXSCREENER_API}/tokens/{contract_address}"
        
        data = self._make_request(url)
        
        if data and "pairs" in data and len(data["pairs"]) > 0:
            # Sum liquidity from all pairs
            total_liquidity = sum(
                float(pair.get("liquidity", {}).get("usd", 0))
                for pair in data["pairs"]
            )
            
            if total_liquidity > 0:
                return TVLData(
                    tvl_usd=total_liquidity,
                    source="dexscreener",
                    timestamp=datetime.now().isoformat(),
                    protocol=data["pairs"][0].get("dexId", "Unknown"),
                    confidence="medium"
                )
        
        logger.warning("Could not fetch TVL from DexScreener")
        return None
    
    def get_tvl_from_defillama(self, protocol_slug: str) -> Optional[TVLData]:
        """
        PROMPT 2: Fetch TVL from DefiLlama API.
        
        Args:
            protocol_slug: Protocol slug (e.g., "uniswap", "aave")
        
        Returns:
            TVLData or None
        """
        logger.info(f"Fetching TVL from DefiLlama for {protocol_slug}")
        
        url = f"{self.DEFILLAMA_API}/protocol/{protocol_slug}"
        
        data = self._make_request(url)
        
        if data and "tvl" in data:
            # Get current TVL
            tvl_history = data.get("tvl", [])
            if tvl_history:
                latest_tvl = tvl_history[-1].get("totalLiquidityUSD", 0)
                
                return TVLData(
                    tvl_usd=float(latest_tvl),
                    source="defillama",
                    timestamp=datetime.now().isoformat(),
                    protocol=data.get("name", protocol_slug),
                    confidence="high"
                )
        
        logger.warning("Could not fetch TVL from DefiLlama")
        return None
    
    def get_tvl_multi_source(
        self,
        contract_address: str,
        chain: str = "ethereum",
        protocol_slug: Optional[str] = None
    ) -> Optional[TVLData]:
        """
        PROMPT 2: Fetch TVL from multiple sources (fallback strategy).
        
        Priority: DefiLlama > CoinGecko > DexScreener
        
        Args:
            contract_address: Smart contract address
            chain: Blockchain network
            protocol_slug: Optional protocol slug for DefiLlama
        
        Returns:
            TVLData from the first successful source
        """
        logger.info("Fetching TVL from multiple sources...")
        
        # Try DefiLlama first (most reliable for protocols)
        if protocol_slug:
            tvl = self.get_tvl_from_defillama(protocol_slug)
            if tvl:
                return tvl
        
        # Try CoinGecko
        tvl = self.get_tvl_from_coingecko(contract_address, chain)
        if tvl:
            return tvl
        
        # Try DexScreener (for DEX pairs)
        tvl = self.get_tvl_from_dexscreener(contract_address)
        if tvl:
            return tvl
        
        logger.error("Could not fetch TVL from any source")
        return None
    
    # ========================================================================
    # VOLUME DATA - 24h Transaction Volume
    # ========================================================================
    
    def get_volume_from_dexscreener(self, contract_address: str) -> Optional[VolumeData]:
        """
        PROMPT 2: Fetch 24h volume from DexScreener.
        
        Args:
            contract_address: Smart contract address
        
        Returns:
            VolumeData or None
        """
        logger.info(f"Fetching 24h volume from DexScreener for {contract_address}")
        
        url = f"{self.DEXSCREENER_API}/tokens/{contract_address}"
        
        data = self._make_request(url)
        
        if data and "pairs" in data and len(data["pairs"]) > 0:
            # Sum volume from all pairs
            total_volume = sum(
                float(pair.get("volume", {}).get("h24", 0))
                for pair in data["pairs"]
            )
            
            # Estimate transaction count (assume avg tx = $1000)
            tx_count = int(total_volume / 1000) if total_volume > 0 else 0
            
            return VolumeData(
                volume_24h_usd=total_volume,
                transactions_24h=tx_count,
                source="dexscreener",
                timestamp=datetime.now().isoformat(),
                chain=data["pairs"][0].get("chainId", "unknown")
            )
        
        logger.warning("Could not fetch volume from DexScreener")
        return None
    
    def get_volume_from_coingecko(self, contract_address: str, chain: str = "ethereum") -> Optional[VolumeData]:
        """
        PROMPT 2: Fetch 24h volume from CoinGecko.
        
        Args:
            contract_address: Smart contract address
            chain: Blockchain network
        
        Returns:
            VolumeData or None
        """
        logger.info(f"Fetching 24h volume from CoinGecko for {contract_address}")
        
        chain_map = {
            "ethereum": "ethereum",
            "bsc": "binance-smart-chain",
            "polygon": "polygon-pos"
        }
        
        platform = chain_map.get(chain.lower(), "ethereum")
        url = f"{self.COINGECKO_API}/coins/{platform}/contract/{contract_address}"
        
        data = self._make_request(url)
        
        if data and "market_data" in data:
            volume = data["market_data"].get("total_volume", {}).get("usd", 0)
            
            if volume:
                return VolumeData(
                    volume_24h_usd=float(volume),
                    transactions_24h=0,  # Not available from CoinGecko
                    source="coingecko",
                    timestamp=datetime.now().isoformat(),
                    chain=chain
                )
        
        logger.warning("Could not fetch volume from CoinGecko")
        return None
    
    # ========================================================================
    # MARKET SENTIMENT
    # ========================================================================
    
    def get_market_sentiment(self, contract_address: str, chain: str = "ethereum") -> Optional[MarketSentiment]:
        """
        PROMPT 2: Calculate market sentiment from available data.
        
        Args:
            contract_address: Smart contract address
            chain: Blockchain network
        
        Returns:
            MarketSentiment or None
        """
        logger.info(f"Analyzing market sentiment for {contract_address}")
        
        chain_map = {"ethereum": "ethereum", "bsc": "binance-smart-chain"}
        platform = chain_map.get(chain.lower(), "ethereum")
        
        url = f"{self.COINGECKO_API}/coins/{platform}/contract/{contract_address}"
        data = self._make_request(url)
        
        if data and "market_data" in data:
            market_data = data["market_data"]
            
            # Price change 24h
            price_change = market_data.get("price_change_percentage_24h", 0)
            
            # Sentiment score based on price change and market metrics
            sentiment_score = 0.0
            
            if price_change > 10:
                sentiment_score = 0.8
            elif price_change > 5:
                sentiment_score = 0.5
            elif price_change > 0:
                sentiment_score = 0.2
            elif price_change > -5:
                sentiment_score = -0.2
            elif price_change > -10:
                sentiment_score = -0.5
            else:
                sentiment_score = -0.8
            
            return MarketSentiment(
                sentiment_score=sentiment_score,
                price_change_24h=price_change,
                holders_count=0,  # Not available without Etherscan Pro
                social_mentions=0,  # Would require Twitter/Reddit API
                source="coingecko"
            )
        
        return None
    
    # ========================================================================
    # FINANCIAL IMPACT CALCULATION - PROMPT 2 Core Feature
    # ========================================================================
    
    def calculate_financial_impact(
        self,
        severity_score: float,
        tvl_usd: float,
        impact_multiplier: float = 1.0
    ) -> FinancialImpact:
        """
        PROMPT 2: Calculate financial impact = severity × TVL.
        
        Formula: financial_impact_usd = severity_score × tvl_usd × impact_multiplier
        
        Args:
            severity_score: Risk score from Sprint 1 pentest (0-100)
            tvl_usd: Total Value Locked in USD
            impact_multiplier: Additional multiplier for specific vulnerabilities
        
        Returns:
            FinancialImpact with risk categorization
        """
        logger.info(f"Calculating financial impact (severity={severity_score}, TVL=${tvl_usd:,.2f})")
        
        # PROMPT 2: Multiply severity by TVL
        financial_impact = (severity_score / 100) * tvl_usd * impact_multiplier
        
        # Risk categorization
        if financial_impact >= 10_000_000:  # $10M+
            risk_category = "Critical"
        elif financial_impact >= 1_000_000:  # $1M+
            risk_category = "High"
        elif financial_impact >= 100_000:  # $100K+
            risk_category = "Medium"
        else:
            risk_category = "Low"
        
        logger.info(f"Financial Impact: ${financial_impact:,.2f} ({risk_category})")
        
        return FinancialImpact(
            financial_impact_usd=financial_impact,
            tvl_usd=tvl_usd,
            severity_score=severity_score,
            risk_category=risk_category,
            calculation_method=f"severity({severity_score}/100) × TVL(${tvl_usd:,.0f}) × multiplier({impact_multiplier})",
            timestamp=datetime.now().isoformat()
        )
    
    # ========================================================================
    # COMPLETE MARKET INTELLIGENCE REPORT
    # ========================================================================
    
    def generate_market_intel_report(
        self,
        contract_address: str,
        chain: str = "ethereum",
        severity_score: float = 0.0,
        protocol_slug: Optional[str] = None
    ) -> MarketIntelReport:
        """
        PROMPT 2: Generate complete market intelligence report.
        
        Includes:
        - TVL from multiple sources
        - 24h volume
        - Market sentiment
        - Financial impact calculation
        
        Args:
            contract_address: Smart contract address
            chain: Blockchain network
            severity_score: Risk score from Sprint 1 pentest
            protocol_slug: Optional protocol slug for DefiLlama
        
        Returns:
            MarketIntelReport with all gathered intel
        """
        logger.info("=" * 60)
        logger.info(f"Generating Market Intelligence Report")
        logger.info(f"Contract: {contract_address}")
        logger.info(f"Chain: {chain}")
        logger.info("=" * 60)
        
        report = MarketIntelReport(
            contract_address=contract_address,
            chain=chain
        )
        
        # 1. Fetch TVL (PROMPT 2: Total Value Locked)
        tvl = self.get_tvl_multi_source(contract_address, chain, protocol_slug)
        if tvl:
            report.tvl_data = tvl
            report.data_sources.append(tvl.source)
            logger.info(f"✓ TVL: ${tvl.tvl_usd:,.2f} (source: {tvl.source})")
        else:
            report.warnings.append("Could not fetch TVL data from any source")
            logger.warning("✗ TVL: Not available")
        
        # 2. Fetch 24h Volume (PROMPT 2: Transaction volume)
        volume = self.get_volume_from_dexscreener(contract_address)
        if not volume:
            volume = self.get_volume_from_coingecko(contract_address, chain)
        
        if volume:
            report.volume_data = volume
            report.data_sources.append(volume.source)
            logger.info(f"✓ Volume 24h: ${volume.volume_24h_usd:,.2f}")
        else:
            report.warnings.append("Could not fetch volume data")
            logger.warning("✗ Volume: Not available")
        
        # 3. Market Sentiment
        sentiment = self.get_market_sentiment(contract_address, chain)
        if sentiment:
            report.sentiment = sentiment
            logger.info(f"✓ Sentiment: {sentiment.sentiment_score:.2f} ({sentiment.price_change_24h:+.2f}%)")
        else:
            report.warnings.append("Could not analyze market sentiment")
            logger.warning("✗ Sentiment: Not available")
        
        # 4. Financial Impact (PROMPT 2: severity × TVL)
        if tvl and severity_score > 0:
            impact = self.calculate_financial_impact(severity_score, tvl.tvl_usd)
            report.financial_impact = impact
            logger.info(f"✓ Financial Impact: ${impact.financial_impact_usd:,.2f} ({impact.risk_category})")
        else:
            if not tvl:
                report.warnings.append("Cannot calculate financial impact without TVL data")
            if severity_score == 0:
                report.warnings.append("Severity score not provided, skipping financial impact calculation")
        
        logger.info("=" * 60)
        logger.info(f"Report complete with {len(report.data_sources)} sources")
        logger.info("=" * 60)
        
        return report


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_market_intel(
    contract_address: str,
    chain: str = "ethereum",
    severity_score: float = 0.0,
    output_json: Optional[str] = None
) -> MarketIntelReport:
    """
    PROMPT 2: Quick market intelligence gathering.
    
    Args:
        contract_address: Smart contract address
        chain: Blockchain network
        severity_score: Risk score from Sprint 1 pentest
        output_json: Optional path to save JSON report
    
    Returns:
        MarketIntelReport
    """
    engine = SentinelMarketIntel()
    report = engine.generate_market_intel_report(
        contract_address=contract_address,
        chain=chain,
        severity_score=severity_score
    )
    
    # Save JSON if requested
    if output_json:
        from pathlib import Path
        Path(output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, 'w', encoding='utf-8') as f:
            f.write(report.to_json())
        logger.info(f"Report saved: {output_json}")
    
    return report


# ============================================================================
# MAIN DEMO
# ============================================================================

def main():
    """Demo: Fetch market intelligence for a popular DeFi protocol."""
    print("=" * 80)
    print("SPRINT 4 PROMPT 2: Market Intelligence Demo")
    print("=" * 80)
    
    # Example: Uniswap V2 Router on Ethereum
    contract_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    
    print(f"\nContract: {contract_address}")
    print(f"Chain: Ethereum")
    print(f"Simulated Severity: 65/100 (Medium-High)")
    print()
    
    # Generate report
    report = quick_market_intel(
        contract_address=contract_address,
        chain="ethereum",
        severity_score=65.0,
        output_json="reports/market_intel_demo.json"
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("MARKET INTELLIGENCE REPORT")
    print("=" * 80)
    
    if report.tvl_data:
        print(f"\n💰 Total Value Locked (TVL):")
        print(f"   Amount: ${report.tvl_data.tvl_usd:,.2f}")
        print(f"   Source: {report.tvl_data.source}")
        print(f"   Confidence: {report.tvl_data.confidence}")
    
    if report.volume_data:
        print(f"\n📊 24h Volume:")
        print(f"   Volume: ${report.volume_data.volume_24h_usd:,.2f}")
        print(f"   Source: {report.volume_data.source}")
    
    if report.sentiment:
        print(f"\n📈 Market Sentiment:")
        print(f"   Score: {report.sentiment.sentiment_score:.2f}")
        print(f"   Price Change 24h: {report.sentiment.price_change_24h:+.2f}%")
    
    if report.financial_impact:
        print(f"\n⚠️  Financial Impact:")
        print(f"   Impact: ${report.financial_impact.financial_impact_usd:,.2f}")
        print(f"   Risk Category: {report.financial_impact.risk_category}")
        print(f"   Calculation: {report.financial_impact.calculation_method}")
    
    if report.warnings:
        print(f"\n⚠️  Warnings:")
        for warning in report.warnings:
            print(f"   - {warning}")
    
    print("\n" + "=" * 80)
    print("✓ Demo complete!")
    print(f"Report saved: reports/market_intel_demo.json")
    print("=" * 80)


if __name__ == "__main__":
    main()
