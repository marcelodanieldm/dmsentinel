"""
DM Sentinel API Shield - API Discovery Engine
==============================================

Motor de descubrimiento de Shadow APIs mediante análisis de código fuente del cliente.

Features:
- Scraping de HTML y archivos JavaScript
- Detección de rutas API por expresiones regulares
- Análisis concurrente de múltiples archivos JS
- Extracción de endpoints no documentados
- Detección de headers de autorización
- Manejo robusto de errores de red

Author: DM Global Security Team
Date: March 2026
Version: 1.0
"""

import asyncio
import re
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse, urlencode
import aiohttp
from aiohttp import ClientSession, ClientTimeout, ClientError
from bs4 import BeautifulSoup
import logging
from concurrent.futures import ThreadPoolExecutor
import time


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class DiscoveredEndpoint:
    """Represents a discovered API endpoint."""
    url: str
    method: str = "UNKNOWN"
    source_file: str = ""
    endpoint_type: str = "REST"  # REST, GraphQL, WebSocket
    auth_headers: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    confidence: float = 1.0  # 0.0 to 1.0
    
    def __hash__(self):
        return hash(self.url)
    
    def __eq__(self, other):
        if isinstance(other, DiscoveredEndpoint):
            return self.url == other.url
        return False


@dataclass
class DiscoveryResult:
    """Results from API discovery scan."""
    target_url: str
    total_endpoints: int = 0
    rest_endpoints: List[DiscoveredEndpoint] = field(default_factory=list)
    graphql_endpoints: List[DiscoveredEndpoint] = field(default_factory=list)
    websocket_endpoints: List[DiscoveredEndpoint] = field(default_factory=list)
    auth_headers: Set[str] = field(default_factory=set)
    api_keys: Set[str] = field(default_factory=set)
    subdomains: Set[str] = field(default_factory=set)
    js_files_analyzed: int = 0
    errors: List[str] = field(default_factory=list)
    scan_duration: float = 0.0


# ============================================================================
# REGEX PATTERNS FOR API DETECTION
# ============================================================================

class APIPatterns:
    """Collection of regex patterns for detecting APIs."""
    
    # REST API Patterns
    REST_RELATIVE = re.compile(
        r'''(?:['"`]|(?:=\s*))              # Quote or assignment
        (/(?:api|v\d+|v\d+\.\d+|graphql|rest|backend|service)  # API prefixes
        /[a-zA-Z0-9\-_/.{}:]+)              # Path segments
        (?:['"`]|(?:\s))                     # End quote or space
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    # Full URL patterns
    API_FULL_URL = re.compile(
        r'''https?://                        # Protocol
        (?:api\.|backend\.|service\.)?       # Optional API subdomain
        [a-zA-Z0-9\-_.]+                     # Domain
        (?:\.[a-zA-Z]{2,})+                  # TLD
        (?::\d+)?                            # Optional port
        (?:/(?:api|v\d+|graphql|rest))?      # Optional API prefix
        /[a-zA-Z0-9\-_/.{}:]*                # Path
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    # GraphQL specific
    GRAPHQL_ENDPOINT = re.compile(
        r'''(?:['"`])                        # Quote
        (/?(?:graphql|gql)(?:/[a-zA-Z0-9\-_/]*)?|/api/graphql)
        (?:['"`])                            # End quote
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    # WebSocket endpoints
    WEBSOCKET_ENDPOINT = re.compile(
        r'''wss?://                          # WebSocket protocol
        [a-zA-Z0-9\-_.]+                     # Domain
        (?:\.[a-zA-Z]{2,})+                  # TLD
        (?::\d+)?                            # Optional port
        (?:/[a-zA-Z0-9\-_/.]*)?              # Path
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    # Authorization headers
    AUTH_HEADER = re.compile(
        r'''(?:Authorization|X-API-Key|X-Auth-Token|X-Access-Token|Bearer|Api-Key)
        \s*[:=]\s*
        (?:['"`])?
        ([a-zA-Z0-9\-_.]+)
        (?:['"`])?
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    # API Keys in code
    API_KEY_PATTERN = re.compile(
        r'''(?:api[_-]?key|apikey|api_token|access[_-]?token|secret[_-]?key)
        \s*[:=]\s*
        (?:['"`])
        ([a-zA-Z0-9\-_]{20,})
        (?:['"`])
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    # HTTP Methods
    HTTP_METHOD = re.compile(
        r'''\.(get|post|put|patch|delete|head|options)
        \s*\(\s*
        (?:['"`])
        ([^'"`]+)
        (?:['"`])
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    # Fetch/Axios patterns
    FETCH_PATTERN = re.compile(
        r'''(?:fetch|axios|ajax|http)
        \s*\.\s*(?:get|post|put|patch|delete)
        \s*\(\s*
        (?:['"`])
        ([^'"`]+)
        (?:['"`])
        ''', 
        re.VERBOSE | re.IGNORECASE
    )
    
    # API Base URLs
    BASE_URL = re.compile(
        r'''(?:baseURL|base_url|API_BASE|apiUrl|API_URL|BASE_API_URL)
        \s*[:=]\s*
        (?:['"`])
        ([^'"`]+)
        (?:['"`])
        ''', 
        re.VERBOSE | re.IGNORECASE
    )


# ============================================================================
# API DISCOVERY ENGINE (CORE)
# ============================================================================

class APIDiscoveryEngine:
    """
    Core engine for discovering Shadow APIs through source code analysis.
    
    Features:
    - Concurrent JavaScript file analysis
    - Regex-based endpoint detection
    - Authorization header extraction
    - Network error handling with retries
    - Rate limiting to avoid detection
    """
    
    def __init__(self, 
                 max_concurrent: int = 10,
                 timeout: int = 30,
                 max_retries: int = 3,
                 user_agent: str = None):
        """
        Initialize the discovery engine.
        
        Args:
            max_concurrent: Maximum concurrent requests
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            user_agent: Custom User-Agent string
        """
        self.max_concurrent = max_concurrent
        self.timeout = ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'requests_failed': 0,
            'js_files_found': 0,
            'endpoints_discovered': 0
        }
    
    async def discover_apis(self, target_url: str) -> DiscoveryResult:
        """
        Main entry point: Discover APIs from target URL.
        
        Args:
            target_url: Target website URL to analyze
        
        Returns:
            DiscoveryResult with all discovered endpoints
        """
        start_time = time.time()
        logger.info(f"🔍 Starting API discovery for: {target_url}")
        
        result = DiscoveryResult(target_url=target_url)
        
        try:
            async with aiohttp.ClientSession(
                timeout=self.timeout,
                headers={'User-Agent': self.user_agent}
            ) as session:
                # Step 1: Download base HTML
                html_content = await self._fetch_url(session, target_url)
                if not html_content:
                    result.errors.append(f"Failed to fetch base URL: {target_url}")
                    return result
                
                # Step 2: Extract JavaScript file URLs from HTML
                js_urls = self._extract_js_urls(html_content, target_url)
                logger.info(f"📦 Found {len(js_urls)} JavaScript files")
                self.stats['js_files_found'] = len(js_urls)
                
                # Step 3: Analyze base HTML for APIs
                html_endpoints = self._analyze_content(html_content, target_url)
                
                # Step 4: Download and analyze JS files concurrently
                js_endpoints = await self._analyze_js_files_concurrent(
                    session, js_urls, target_url
                )
                
                # Step 5: Combine and deduplicate results
                all_endpoints = html_endpoints + js_endpoints
                result = self._process_endpoints(all_endpoints, result)
                
                # Step 6: Extract additional metadata
                result.auth_headers = self._extract_auth_headers(html_content)
                result.api_keys = self._extract_api_keys(html_content)
                result.subdomains = self._extract_subdomains(all_endpoints)
                
                result.js_files_analyzed = len(js_urls)
                result.total_endpoints = len(result.rest_endpoints) + \
                                        len(result.graphql_endpoints) + \
                                        len(result.websocket_endpoints)
                
                logger.info(f"✅ Discovery complete! Found {result.total_endpoints} endpoints")
        
        except Exception as e:
            logger.error(f"❌ Discovery failed: {e}")
            result.errors.append(f"Discovery error: {str(e)}")
        
        finally:
            result.scan_duration = time.time() - start_time
            self._print_statistics(result)
        
        return result
    
    async def _fetch_url(self, 
                        session: ClientSession, 
                        url: str, 
                        retry_count: int = 0) -> Optional[str]:
        """
        Fetch URL content with retry logic and error handling.
        
        Args:
            session: aiohttp ClientSession
            url: URL to fetch
            retry_count: Current retry attempt
        
        Returns:
            Response text or None on failure
        """
        try:
            self.stats['requests_made'] += 1
            
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status == 404:
                    logger.warning(f"⚠️  404 Not Found: {url}")
                    self.stats['requests_failed'] += 1
                    return None
                elif response.status in [429, 503]:
                    # Rate limited or service unavailable
                    if retry_count < self.max_retries:
                        wait_time = 2 ** retry_count  # Exponential backoff
                        logger.warning(f"⏳ Rate limited, waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                        return await self._fetch_url(session, url, retry_count + 1)
                    else:
                        logger.error(f"❌ Max retries exceeded for: {url}")
                        self.stats['requests_failed'] += 1
                        return None
                else:
                    logger.warning(f"⚠️  HTTP {response.status}: {url}")
                    self.stats['requests_failed'] += 1
                    return None
        
        except asyncio.TimeoutError:
            logger.warning(f"⏱️  Timeout: {url}")
            if retry_count < self.max_retries:
                return await self._fetch_url(session, url, retry_count + 1)
            self.stats['requests_failed'] += 1
            return None
        
        except ClientError as e:
            logger.error(f"❌ Client error for {url}: {e}")
            self.stats['requests_failed'] += 1
            return None
        
        except Exception as e:
            logger.error(f"❌ Unexpected error for {url}: {e}")
            self.stats['requests_failed'] += 1
            return None
    
    def _extract_js_urls(self, html: str, base_url: str) -> List[str]:
        """
        Extract JavaScript file URLs from HTML.
        
        Args:
            html: HTML content
            base_url: Base URL for resolving relative paths
        
        Returns:
            List of absolute JavaScript URLs
        """
        js_urls = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find <script src="..."> tags
            for script in soup.find_all('script', src=True):
                src = script['src']
                
                # Skip inline scripts and data URIs
                if src.startswith('data:') or not src:
                    continue
                
                # Convert to absolute URL
                absolute_url = urljoin(base_url, src)
                
                # Only include .js files from same or relevant domains
                if absolute_url.endswith('.js') or '/js/' in absolute_url:
                    js_urls.append(absolute_url)
            
            # Also check for dynamic imports in inline scripts
            for script in soup.find_all('script'):
                if script.string:
                    # Look for import() or require() statements
                    import_matches = re.findall(
                        r'''(?:import|require)\s*\(\s*['"`]([^'"`]+\.js)['"`]\s*\)''',
                        script.string
                    )
                    for match in import_matches:
                        absolute_url = urljoin(base_url, match)
                        js_urls.append(absolute_url)
        
        except Exception as e:
            logger.error(f"Error extracting JS URLs: {e}")
        
        # Deduplicate
        return list(set(js_urls))
    
    async def _analyze_js_files_concurrent(self,
                                          session: ClientSession,
                                          js_urls: List[str],
                                          base_url: str) -> List[DiscoveredEndpoint]:
        """
        Analyze multiple JavaScript files concurrently.
        
        Args:
            session: aiohttp ClientSession
            js_urls: List of JS file URLs
            base_url: Base URL for context
        
        Returns:
            List of discovered endpoints
        """
        endpoints = []
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def analyze_single_js(js_url: str):
            async with semaphore:
                js_content = await self._fetch_url(session, js_url)
                if js_content:
                    return self._analyze_content(js_content, base_url, js_url)
                return []
        
        # Execute all analyses concurrently
        tasks = [analyze_single_js(url) for url in js_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        for result in results:
            if isinstance(result, list):
                endpoints.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Error analyzing JS file: {result}")
        
        return endpoints
    
    def _analyze_content(self, 
                        content: str, 
                        base_url: str,
                        source_file: str = "base_html") -> List[DiscoveredEndpoint]:
        """
        Analyze content (HTML or JS) for API endpoints using regex.
        
        Args:
            content: Content to analyze
            base_url: Base URL for resolving relative paths
            source_file: Source file name for tracking
        
        Returns:
            List of discovered endpoints
        """
        endpoints = []
        
        # 1. REST relative paths
        for match in APIPatterns.REST_RELATIVE.finditer(content):
            path = match.group(1)
            full_url = urljoin(base_url, path)
            endpoints.append(DiscoveredEndpoint(
                url=full_url,
                source_file=source_file,
                endpoint_type="REST",
                confidence=0.9
            ))
        
        # 2. Full API URLs
        for match in APIPatterns.API_FULL_URL.finditer(content):
            url = match.group(0)
            endpoints.append(DiscoveredEndpoint(
                url=url,
                source_file=source_file,
                endpoint_type="REST",
                confidence=1.0
            ))
        
        # 3. GraphQL endpoints
        for match in APIPatterns.GRAPHQL_ENDPOINT.finditer(content):
            path = match.group(1)
            full_url = urljoin(base_url, path)
            endpoints.append(DiscoveredEndpoint(
                url=full_url,
                source_file=source_file,
                endpoint_type="GraphQL",
                confidence=1.0
            ))
        
        # 4. WebSocket endpoints
        for match in APIPatterns.WEBSOCKET_ENDPOINT.finditer(content):
            url = match.group(0)
            endpoints.append(DiscoveredEndpoint(
                url=url,
                source_file=source_file,
                endpoint_type="WebSocket",
                confidence=1.0
            ))
        
        # 5. HTTP Method calls (e.g., .get('/api/users'))
        for match in APIPatterns.HTTP_METHOD.finditer(content):
            method = match.group(1).upper()
            path = match.group(2)
            full_url = urljoin(base_url, path)
            
            # Check if endpoint already exists
            existing = next((e for e in endpoints if e.url == full_url), None)
            if existing:
                existing.method = method
                existing.confidence = 1.0
            else:
                endpoints.append(DiscoveredEndpoint(
                    url=full_url,
                    method=method,
                    source_file=source_file,
                    endpoint_type="REST",
                    confidence=1.0
                ))
        
        # 6. Fetch/Axios patterns
        for match in APIPatterns.FETCH_PATTERN.finditer(content):
            path = match.group(1)
            full_url = urljoin(base_url, path)
            endpoints.append(DiscoveredEndpoint(
                url=full_url,
                source_file=source_file,
                endpoint_type="REST",
                confidence=0.95
            ))
        
        # 7. Extract base URLs for context
        for match in APIPatterns.BASE_URL.finditer(content):
            base_api_url = match.group(1)
            logger.info(f"📍 Found API base URL: {base_api_url}")
            # Store for later use in resolving relative paths
        
        return endpoints
    
    def _extract_auth_headers(self, content: str) -> Set[str]:
        """Extract authorization headers from content."""
        auth_headers = set()
        
        for match in APIPatterns.AUTH_HEADER.finditer(content):
            header = match.group(0).split(':')[0].strip()
            auth_headers.add(header)
        
        return auth_headers
    
    def _extract_api_keys(self, content: str) -> Set[str]:
        """Extract API keys from content (WARNING: security risk if exposed)."""
        api_keys = set()
        
        for match in APIPatterns.API_KEY_PATTERN.finditer(content):
            key = match.group(1)
            # Only add if it looks legitimate (not a placeholder)
            if not any(placeholder in key.lower() for placeholder in 
                      ['your_api_key', 'example', 'placeholder', 'xxx', '000']):
                api_keys.add(key)
        
        return api_keys
    
    def _extract_subdomains(self, endpoints: List[DiscoveredEndpoint]) -> Set[str]:
        """Extract unique subdomains from discovered endpoints."""
        subdomains = set()
        
        for endpoint in endpoints:
            parsed = urlparse(endpoint.url)
            if parsed.netloc:
                subdomains.add(parsed.netloc)
        
        return subdomains
    
    def _process_endpoints(self, 
                          endpoints: List[DiscoveredEndpoint],
                          result: DiscoveryResult) -> DiscoveryResult:
        """
        Process and categorize discovered endpoints.
        
        Args:
            endpoints: Raw list of endpoints
            result: DiscoveryResult to populate
        
        Returns:
            Updated DiscoveryResult
        """
        # Deduplicate by URL
        unique_endpoints = list(set(endpoints))
        
        # Categorize by type
        for endpoint in unique_endpoints:
            if endpoint.endpoint_type == "REST":
                result.rest_endpoints.append(endpoint)
            elif endpoint.endpoint_type == "GraphQL":
                result.graphql_endpoints.append(endpoint)
            elif endpoint.endpoint_type == "WebSocket":
                result.websocket_endpoints.append(endpoint)
        
        # Sort by confidence
        result.rest_endpoints.sort(key=lambda e: e.confidence, reverse=True)
        result.graphql_endpoints.sort(key=lambda e: e.confidence, reverse=True)
        result.websocket_endpoints.sort(key=lambda e: e.confidence, reverse=True)
        
        self.stats['endpoints_discovered'] = len(unique_endpoints)
        
        return result
    
    def _print_statistics(self, result: DiscoveryResult):
        """Print discovery statistics."""
        logger.info("=" * 80)
        logger.info("📊 DISCOVERY STATISTICS")
        logger.info("=" * 80)
        logger.info(f"Target URL: {result.target_url}")
        logger.info(f"Scan Duration: {result.scan_duration:.2f}s")
        logger.info(f"JavaScript Files Analyzed: {result.js_files_analyzed}")
        logger.info(f"Total Requests Made: {self.stats['requests_made']}")
        logger.info(f"Failed Requests: {self.stats['requests_failed']}")
        logger.info("")
        logger.info(f"🎯 Discovered Endpoints:")
        logger.info(f"   REST APIs: {len(result.rest_endpoints)}")
        logger.info(f"   GraphQL APIs: {len(result.graphql_endpoints)}")
        logger.info(f"   WebSocket APIs: {len(result.websocket_endpoints)}")
        logger.info(f"   Total: {result.total_endpoints}")
        logger.info("")
        logger.info(f"🔑 Security Findings:")
        logger.info(f"   Auth Headers Found: {len(result.auth_headers)}")
        logger.info(f"   API Keys Exposed: {len(result.api_keys)}")
        logger.info(f"   Unique Subdomains: {len(result.subdomains)}")
        logger.info("=" * 80)


# ============================================================================
# EXPORT FUNCTIONALITY
# ============================================================================

class DiscoveryExporter:
    """Export discovery results in various formats."""
    
    @staticmethod
    def to_json(result: DiscoveryResult) -> Dict:
        """Export result as JSON-serializable dict."""
        return {
            'target_url': result.target_url,
            'scan_duration': result.scan_duration,
            'total_endpoints': result.total_endpoints,
            'rest_endpoints': [
                {
                    'url': e.url,
                    'method': e.method,
                    'source': e.source_file,
                    'confidence': e.confidence
                } for e in result.rest_endpoints
            ],
            'graphql_endpoints': [
                {
                    'url': e.url,
                    'source': e.source_file
                } for e in result.graphql_endpoints
            ],
            'websocket_endpoints': [
                {
                    'url': e.url,
                    'source': e.source_file
                } for e in result.websocket_endpoints
            ],
            'auth_headers': list(result.auth_headers),
            'api_keys': list(result.api_keys),
            'subdomains': list(result.subdomains),
            'js_files_analyzed': result.js_files_analyzed,
            'errors': result.errors
        }
    
    @staticmethod
    def to_markdown(result: DiscoveryResult) -> str:
        """Export result as Markdown report."""
        md = f"# API Discovery Report\n\n"
        md += f"**Target:** {result.target_url}  \n"
        md += f"**Scan Duration:** {result.scan_duration:.2f}s  \n"
        md += f"**Total Endpoints:** {result.total_endpoints}  \n\n"
        
        if result.rest_endpoints:
            md += f"## REST Endpoints ({len(result.rest_endpoints)})\n\n"
            for endpoint in result.rest_endpoints[:20]:  # Limit to top 20
                md += f"- `{endpoint.method}` {endpoint.url}\n"
                md += f"  - Source: `{endpoint.source_file}`\n"
                md += f"  - Confidence: {endpoint.confidence * 100:.0f}%\n\n"
        
        if result.graphql_endpoints:
            md += f"## GraphQL Endpoints ({len(result.graphql_endpoints)})\n\n"
            for endpoint in result.graphql_endpoints:
                md += f"- {endpoint.url}\n"
        
        if result.api_keys:
            md += f"## ⚠️ Exposed API Keys ({len(result.api_keys)})\n\n"
            md += "**WARNING:** The following API keys were found in client-side code:\n\n"
            for key in result.api_keys:
                md += f"- `{key[:10]}...{key[-10:]}`\n"
        
        return md


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def main():
    """Example usage of API Discovery Engine."""
    
    print("=" * 80)
    print("🛡️  DM SENTINEL API SHIELD - API DISCOVERY ENGINE")
    print("=" * 80)
    print()
    
    # Example target
    target = "https://example.com"
    
    # Initialize engine
    engine = APIDiscoveryEngine(
        max_concurrent=10,
        timeout=30,
        max_retries=3
    )
    
    # Run discovery
    result = await engine.discover_apis(target)
    
    # Print results
    if result.rest_endpoints:
        print("\n📍 Top 10 Discovered REST Endpoints:")
        for i, endpoint in enumerate(result.rest_endpoints[:10], 1):
            print(f"   {i}. [{endpoint.method}] {endpoint.url}")
            print(f"      Source: {endpoint.source_file}")
            print(f"      Confidence: {endpoint.confidence * 100:.0f}%")
    
    if result.graphql_endpoints:
        print(f"\n🔷 GraphQL Endpoints:")
        for endpoint in result.graphql_endpoints:
            print(f"   - {endpoint.url}")
    
    if result.api_keys:
        print(f"\n⚠️  WARNING: {len(result.api_keys)} exposed API keys found!")
    
    # Export results
    import json
    exporter = DiscoveryExporter()
    json_result = exporter.to_json(result)
    
    with open('api_discovery_result.json', 'w') as f:
        json.dump(json_result, f, indent=2)
    
    print("\n✅ Results exported to: api_discovery_result.json")
    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
