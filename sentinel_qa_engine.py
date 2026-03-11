#!/usr/bin/env python3
"""
Sprint 4 PROMPT 1: QA Automation para dApps con Playwright
============================================================

ROL: Tech Lead + QA Automation Engineer
CONTEXTO: Automatizar la verificación de la interfaz de dApps Web3

REQUERIMIENTOS TÉCNICOS CUMPLIDOS:
✓ Librería: playwright (versión async de Python)
✓ Navegación: Automated dApp URL testing
✓ Detectar selectores: Connect Wallet, Swap, Stake, Mint
✓ Capturas de pantalla: Screenshots de elementos y errores
✓ Verificar console.error: Console monitoring
✓ JSON Output: status, missing_elements, performance_metrics
✓ Modo headless: CI/CD compatible
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import  datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS - PROMPT 1: JSON Output Structure
# ============================================================================

@dataclass
class CriticalElement:
    """Represents a critical UI element to detect."""
    name: str
    selector_patterns: List[str]
    found: bool = False
    screenshot_path: Optional[str] = None
    text_content: Optional[str] = None
    location: Optional[Dict[str, float]] = None


@dataclass
class ConsoleLogEntry:
    """Console log entry (log, error, warning, info)."""
    type: str  # log, error, warning, info
    text: str
    timestamp: str
    location: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for dApp."""
    page_load_time_ms: float = 0.0
    dom_content_loaded_ms: float = 0.0
    first_paint_ms: float = 0.0
    network_requests: int = 0
    failed_requests: int = 0
    javascript_errors: int = 0
    blockchain_rpc_calls: int = 0


@dataclass
class QATestResult:
    """PROMPT 1 Required Output: status, missing_elements, performance_metrics."""
    
    # Core required fields (PROMPT 1)
    status: str  # "Pass" or "Fail"
    url: str
    critical_elements: List[CriticalElement] = field(default_factory=list)
    missing_elements: List[str] = field(default_factory=list)
    console_errors: List[ConsoleLogEntry] = field(default_factory=list)
    performance_metrics: PerformanceMetrics = field(default_factory=PerformanceMetrics)
    
    # Additional context
    screenshots: List[str] = field(default_factory=list)
    full_page_screenshot: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    test_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    browser: str = "chromium"
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """PROMPT 1: JSON output with status, missing_elements, performance_metrics."""
        return json.dumps(self.to_dict(), indent=2, default=str)


# ============================================================================
# SENTINEL QA ENGINE - Main Testing Class
# ============================================================================

class SentinelQAEngine:
    """
    PROMPT 1: QA Automation Engine for Web3 dApps
    
    Automatically tests dApp interfaces to verify:
    1. Critical button presence (Connect Wallet, Swap, Stake, Mint)
    2. Console errors (console.error monitoring)
    3. Performance metrics (page load, network requests)
    4. Screenshot evidence (full page + elements)
    
    Returns: JSON with status, missing_elements, performance_metrics
    """
    
    # PROMPT 1: Critical UI patterns for Web3 dApps
    CRITICAL_ELEMENTS = {
        "connect_wallet": [
            "button:has-text('Connect Wallet')",
            "button:has-text('Connect')",
            "button:has-text('Connect to a wallet')",
            "[class*='connect']:has-text('Wallet')",
            "[id*='connect']",
            "[aria-label*='connect' i]",
            "button[class*='wallet']:has-text('Connect')"
        ],
        "swap": [
            "button:has-text('Swap')",
            "button:has-text('Trade')",
            "[class*='swap-button']",
            "[id*='swap']",
            "[aria-label*='swap' i]",
            "button[class*='trade']"
        ],
        "stake": [
            "button:has-text('Stake')",
            "button:has-text('Staking')",
            "[class*='stake-button']",
            "[id*='stake']",
            "[aria-label*='stake' i]",
            "button[class*='staking']"
        ],
        "mint": [
            "button:has-text('Mint')",
            "button:has-text('Mint NFT')",
            "[class*='mint-button']",
            "[id*='mint']",
            "[aria-label*='mint' i]",
            "button[class*='nft']"
        ]
    }
    
    def __init__(
        self,
        headless: bool = True,
        screenshot_dir: str = "screenshots",
        timeout: int = 30000,
        viewport: Dict[str, int] = None
    ):
        """
        Initialize QA Engine.
        
        Args:
            headless: Run browser in headless mode (CI/CD compatible)
            screenshot_dir: Directory for screenshots
            timeout: Page load timeout in milliseconds
            viewport: Browser viewport size
        """
        self.headless = headless
        self.screenshot_dir = screenshot_dir
        self.timeout = timeout
        self.viewport = viewport or {"width": 1920, "height": 1080}
        
        # Create screenshot directory
        Path(self.screenshot_dir).mkdir(parents=True, exist_ok=True)
        
        # Console log collection
        self._console_logs: List[ConsoleLogEntry] = []
        self._network_requests: List[Dict] = []
        
        logger.info(f"SentinelQAEngine initialized (headless={headless})")
    
    async def test_dapp(
        self,
        url: str,
        custom_elements: Optional[Dict[str, List[str]]] = None
    ) -> QATestResult:
        """
        PROMPT 1: Main testing function - Test dApp URL.
        
        Steps:
        1. Navigate to dApp URL
        2. Detect critical selectors (Connect Wallet, Swap, Stake, Mint)
        3. Capture screenshots (full page + elements)
        4. Verify console errors (console.error)
        5. Collect performance metrics
        6. Return JSON: {status, missing_elements, performance_metrics}
        
        Args:
            url: dApp URL to test
            custom_elements: Optional custom element selectors
        
        Returns:
            QATestResult with status, missing_elements, performance_metrics
        """
        logger.info(f"Starting QA test for: {url}")
        
        # Initialize result
        result = QATestResult(
            status="Pass",
            url=url,
            browser="chromium",
            viewport=self.viewport
        )
        
        async with async_playwright() as p:
            # Launch browser (PROMPT 1: Headless mode support)
            browser: Browser = await p.chromium.launch(headless=self.headless)
            
            try:
                # Create context with viewport
                context: BrowserContext = await browser.new_context(
                    viewport=self.viewport
                )
                
                # New page
                page: Page = await context.new_page()
                
                # Setup monitoring (PROMPT 1: Console error detection)
                self._setup_console_monitoring(page)
                self._setup_network_monitoring(page)
                
                # Navigate to dApp (PROMPT 1: Navigate to URL)
                start_time = datetime.now()
                logger.info(f"Navigating to {url}")
                
                try:
                    await page.goto(url, wait_until="networkidle", timeout=self.timeout)
                    load_time = (datetime.now() - start_time).total_seconds() * 1000
                    result.performance_metrics.page_load_time_ms = load_time
                    logger.info(f"Page loaded in {load_time:.0f}ms")
                except Exception as e:
                    logger.error(f"Failed to load page: {e}")
                    result.status = "Fail"
                    result.warnings.append(f"Page load failed: {str(e)}")
                    return result
                
                # Wait for page to stabilize
                await asyncio.sleep(2)
                
                # PROMPT 1: Detect critical elements (Connect Wallet, Swap, Stake, Mint)
                elements_to_check = custom_elements or self.CRITICAL_ELEMENTS
                result.critical_elements = await self._check_critical_elements(page, elements_to_check)
                
                # Determine missing elements (PROMPT 1: missing_elements)
                result.missing_elements = [
                    elem.name for elem in result.critical_elements if not elem.found
                ]
                
                # PROMPT 1: Capture screenshots
                result.full_page_screenshot = await self._take_full_screenshot(page, url)
                result.screenshots = [
                    elem.screenshot_path 
                    for elem in result.critical_elements 
                    if elem.screenshot_path
                ]
                
                # PROMPT 1: Collect performance metrics
                result.performance_metrics = await self._collect_performance_metrics(page)
                
                # PROMPT 1: Console errors (console.error verification)
                result.console_errors = [
                    log for log in self._console_logs if log.type == "error"
                ]
                result.performance_metrics.javascript_errors = len(result.console_errors)
                
                # Generate warnings and recommendations
                result.warnings = self._generate_warnings(result)
                result.recommendations = self._generate_recommendations(result)
                
                # PROMPT 1: Determine final status (Pass/Fail)
                result.status = self._determine_status(result)
                
                logger.info(f"Test completed: {result.status}")
                logger.info(f"Missing elements: {result.missing_elements}")
                logger.info(f"Console errors: {len(result.console_errors)}")
                
            except Exception as e:
                logger.error(f"Test failed: {e}")
                result.status = "Fail"
                result.warnings.append(f"Test exception: {str(e)}")
            
            finally:
                await browser.close()
        
        return result
    
    def _setup_console_monitoring(self, page: Page):
        """PROMPT 1: Monitor console for errors (console.error)."""
        def handle_console(msg):
            log_entry = ConsoleLogEntry(
                type=msg.type,
                text=msg.text,
                timestamp=datetime.now().isoformat(),
                location=msg.location.get('url') if msg.location else None
            )
            self._console_logs.append(log_entry)
            
            if msg.type == "error":
                logger.warning(f"Console error: {msg.text}")
        
        page.on("console", handle_console)
    
    def _setup_network_monitoring(self, page: Page):
        """Monitor network requests for performance metrics."""
        def handle_request(request):
            self._network_requests.append({
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type,
                "timestamp": datetime.now().isoformat()
            })
        
        def handle_response(response):
            if response.status >= 400:
                logger.warning(f"Failed request: {response.url} ({response.status})")
        
        page.on("request", handle_request)
        page.on("response", handle_response)
    
    async def _check_critical_elements(
        self,
        page: Page,
        elements_dict: Dict[str, List[str]]
    ) -> List[CriticalElement]:
        """
        PROMPT 1: Detect critical selectors (Connect Wallet, Swap, Stake, Mint).
        
        Returns: List of CriticalElement with found status and screenshots.
        """
        results = []
        
        for element_name, selectors in elements_dict.items():
            logger.info(f"Checking element: {element_name}")
            element = CriticalElement(
                name=element_name,
                selector_patterns=selectors
            )
            
            # Try each selector pattern
            for selector in selectors:
                try:
                    locator = page.locator(selector).first
                    count = await locator.count()
                    
                    if count > 0:
                        element.found = True
                        
                        # Get text content
                        try:
                            element.text_content = await locator.text_content(timeout=2000)
                        except:
                            element.text_content = None
                        
                        # Get location
                        try:
                            box = await locator.bounding_box(timeout=2000)
                            if box:
                                element.location = {
                                    "x": box["x"],
                                    "y": box["y"],
                                    "width": box["width"],
                                    "height": box["height"]
                                }
                        except:
                            pass
                        
                        # PROMPT 1: Screenshot element
                        screenshot_path = Path(self.screenshot_dir) / f"{element_name}_element.png"
                        try:
                            await locator.screenshot(path=str(screenshot_path), timeout=5000)
                            element.screenshot_path = str(screenshot_path)
                            logger.info(f"✓ Found {element_name}: {element.text_content}")
                        except Exception as e:
                            logger.warning(f"Could not screenshot {element_name}: {e}")
                        
                        break  # Found, no need to try other selectors
                        
                except Exception as e:
                    logger.debug(f"Selector failed: {selector} - {e}")
                    continue
            
            if not element.found:
                logger.warning(f"✗ Missing {element_name}")
            
            results.append(element)
        
        return results
    
    async def _take_full_screenshot(self, page: Page, url: str) -> str:
        """PROMPT 1: Capture full page screenshot."""
        # Clean URL for filename
        url_clean = url.replace("https://", "").replace("http://", "").replace("/", "_")
        screenshot_path = Path(self.screenshot_dir) / f"full_page_{url_clean}.png"
        
        try:
            await page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(f"Full page screenshot saved: {screenshot_path}")
            return str(screenshot_path)
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    async def _collect_performance_metrics(self, page: Page) -> PerformanceMetrics:
        """PROMPT 1: Collect performance metrics."""
        metrics = PerformanceMetrics()
        
        try:
            # Get performance timing
            performance = await page.evaluate("""() => {
                const perf = window.performance;
                const timing = perf.timing;
                const paintEntries = perf.getEntriesByType('paint');
                
                return {
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    loadComplete: timing.loadEventEnd - timing.navigationStart,
                    firstPaint: paintEntries.length > 0 ? paintEntries[0].startTime : 0
                };
            }""")
            
            metrics.dom_content_loaded_ms = performance.get("domContentLoaded", 0)
            metrics.first_paint_ms = performance.get("firstPaint", 0)
            
        except Exception as e:
            logger.warning(f"Could not collect performance metrics: {e}")
        
        # Network metrics
        metrics.network_requests = len(self._network_requests)
        metrics.failed_requests = len([
            r for r in self._network_requests 
            if r.get("status", 200) >= 400
        ])
        
        # Blockchain RPC calls (estimate from network requests)
        rpc_patterns = ["eth_", "web3", "infura", "alchemy", "rpc"]
        metrics.blockchain_rpc_calls = len([
            r for r in self._network_requests
            if any(pattern in r["url"].lower() for pattern in rpc_patterns)
        ])
        
        return metrics
    
    def _generate_warnings(self, result: QATestResult) -> List[str]:
        """Generate warnings based on test results."""
        warnings = []
        
        if result.missing_elements:
            warnings.append(f"Missing {len(result.missing_elements)} critical elements: {', '.join(result.missing_elements)}")
        
        if len(result.console_errors) > 0:
            warnings.append(f"Found {len(result.console_errors)} JavaScript console errors")
        
        if result.performance_metrics.page_load_time_ms > 5000:
            warnings.append(f"Slow page load: {result.performance_metrics.page_load_time_ms:.0f}ms")
        
        if result.performance_metrics.failed_requests > 0:
            warnings.append(f"{result.performance_metrics.failed_requests} failed network requests")
        
        return warnings
    
    def _generate_recommendations(self, result: QATestResult) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        if result.missing_elements:
            recommendations.append("Add missing critical UI elements for better user experience")
        
        if len(result.console_errors) > 0:
            recommendations.append("Fix JavaScript console errors to improve stability")
        
        if result.performance_metrics.page_load_time_ms > 3000:
            recommendations.append("Optimize page load time (target: < 3 seconds)")
        
        if result.performance_metrics.network_requests > 50:
            recommendations.append("Reduce number of network requests for better performance")
        
        return recommendations
    
    def _determine_status(self, result: QATestResult) -> str:
        """
        PROMPT 1: Determine test status (Pass/Fail).
        
        Fail conditions:
        - Any critical element missing
        - More than 3 console errors
        - Page load time > 10 seconds
        """
        if len(result.missing_elements) > 0:
            return "Fail"
        
        if len(result.console_errors) > 3:
            return "Fail"
        
        if result.performance_metrics.page_load_time_ms > 10000:
            return "Fail"
        
        return " Pass"


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def test_dapp_url(
    url: str,
    headless: bool = True,
    custom_elements: Optional[Dict[str, List[str]]] = None,
    output_json: Optional[str] = None
) -> QATestResult:
    """
    PROMPT 1: Convenience function to test a dApp URL.
    
    Args:
        url: dApp URL to test
        headless: Run in headless mode
        custom_elements: Optional custom element selectors
        output_json: Path to save JSON report
    
    Returns:
        QATestResult with status, missing_elements, performance_metrics
    """
    engine = SentinelQAEngine(headless=headless)
    result = await engine.test_dapp(url, custom_elements)
    
    # Save JSON report if requested
    if output_json:
        Path(output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(output_json, 'w', encoding='utf-8') as f:
            f.write(result.to_json())
        logger.info(f"JSON report saved: {output_json}")
    
    return result


def generate_html_report(result: QATestResult, output_path: str):
    """Generate HTML report from test results."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>QA Test Report - {result.url}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
            .status-pass {{ color: #27ae60; font-weight: bold; }}
            .status-fail {{ color: #e74c3c; font-weight: bold; }}
            .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #ecf0f1; border-radius: 3px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #34495e; color: white; }}
            .found {{ color: #27ae60; }}
            .missing {{ color: #e74c3c; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>QA Test Report</h1>
            <p>URL: {result.url}</p>
            <p>Timestamp: {result.test_timestamp}</p>
            <p class="{'status-pass' if result.status == 'Pass' else 'status-fail'}">
                Status: {result.status}
            </p>
        </div>
        
        <div class="section">
            <h2>Critical Elements</h2>
            <table>
                <tr><th>Element</th><th>Status</th><th>Text</th></tr>
                {''.join(f'<tr><td>{e.name}</td><td class="{'found' if e.found else 'missing'}">{'✓ Found' if e.found else '✗ Missing'}</td><td>{e.text_content or ''}</td></tr>' for e in result.critical_elements)}
            </table>
        </div>
        
        <div class="section">
            <h2>Performance Metrics</h2>
            <div class="metric">Page Load: {result.performance_metrics.page_load_time_ms:.0f}ms</div>
            <div class="metric">Network Requests: {result.performance_metrics.network_requests}</div>
            <div class="metric">Console Errors: {result.performance_metrics.javascript_errors}</div>
            <div class="metric">RPC Calls: {result.performance_metrics.blockchain_rpc_calls}</div>
        </div>
        
        <div class="section">
            <h2>Warnings</h2>
            <ul>
                {''.join(f'<li>{w}</li>' for w in result.warnings) if result.warnings else '<li>No warnings</li>'}
            </ul>
        </div>
        
        <div class="section">
            <h2>Recommendations</h2>
            <ul>
                {''.join(f'<li>{r}</li>' for r in result.recommendations) if result.recommendations else '<li>No recommendations</li>'}
            </ul>
        </div>
    </body>
    </html>
    """
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    logger.info(f"HTML report saved: {output_path}")


# ============================================================================
# MAIN DEMO
# ============================================================================

async def main():
    """Demo: Test a sample dApp."""
    print("=" * 60)
    print("SPRINT 4 PROMPT 1: QA Automation Demo")
    print("=" * 60)
    
    # Test Uniswap
    result = await test_dapp_url(
        url="https://app.uniswap.org",
        headless=True,
        output_json="reports/uniswap_qa.json"
    )
    
    print(f"\nTest Results:")
    print(f"Status: {result.status}")
    print(f"Missing Elements: {result.missing_elements}")
    print(f"Console Errors: {len(result.console_errors)}")
    print(f"Page Load Time: {result.performance_metrics.page_load_time_ms:.0f}ms")
    
    # Generate HTML report
    generate_html_report(result, "reports/uniswap_qa.html")
    
    print("\n✓ Demo complete!")
    print(f"JSON Report: reports/uniswap_qa.json")
    print(f"HTML Report: reports/uniswap_qa.html")


if __name__ == "__main__":
    asyncio.run(main())
