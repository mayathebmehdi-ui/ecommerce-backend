#!/usr/bin/env python3
"""
Complete site crawler: Extract ALL links first, then filter by keywords.
Works with any domain to find policy/help pages.
"""

import asyncio
import json
import logging
import re
import sys
import time
from typing import List, Set, Dict, Tuple, Optional
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser
import gzip

import httpx
from lxml import etree, html

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# Keywords for filtering and scoring
KEYWORDS_PRIMARY = [
    "shipping", "delivery", "returns", "return", "refund", "exchange", "exchanges",
    "warranty", "guarantee", "shipping-policy", "return-policy", "shipping-info"
]

KEYWORDS_SECONDARY = [
    "policy", "policies", "help", "support", "faq", "faqs", "customer-service",
    "customer-care", "care", "assistance", "contact", "about"
]

PATH_KEYWORDS = [
    "return-policy", "returns-policy", "shipping-policy", "delivery-policy",
    "how-to-return", "howtoreturn", "returns-exchanges", "shipping-delivery",
    "help-center", "customer-care", "customer-service", "support-center"
]

# Noise patterns to avoid
NOISE_PATTERNS = [
    "/products/", "/product/", "/collections/", "/cart", "/checkout",
    "/search", "/account", "/signin", "/login", "/signup", "/register",
    "/blogs/", "/blog/", "/news/", "/press/", "?", "#", "/archive/"
]

# Non-English locales to skip
NON_EN_LOCALES = [
    "/fr/", "/es/", "/de/", "/it/", "/jp/", "/zh/", "/pt/", "/ru/",
    "/mx/", "/cl/", "/cr/", "/ar/", "/br/", "/co/", "/pe/", "/uy/",
    "/ve/", "/uk/", "/tr/", "/kz/", "/kh/", "/nl/", "/sv/", "/da/"
]


class CompleteCrawler:
    def __init__(self, domain: str, max_pages: int = 1000):
        self.domain = domain
        self.max_pages = max_pages
        self.base_url = f"https://{domain}"
        self.found_urls: Set[str] = set()
        self.crawled_urls: Set[str] = set()
        self.policy_urls: List[Tuple[int, str]] = []
        self.request_delays = {}  # Track delays per domain
        self.last_request_time = {}  # Track last request time per domain
        
    def is_same_domain(self, url: str) -> bool:
        """Check if URL belongs to same domain."""
        try:
            parsed = urlparse(url)
            return self.domain.lower() in parsed.netloc.lower()
        except:
            return False
    
    def is_english_url(self, url: str) -> bool:
        """Check if URL is likely English (avoid non-EN locales)."""
        url_lower = url.lower()
        return not any(locale in url_lower for locale in NON_EN_LOCALES)
    
    def is_us_url(self, url: str) -> bool:
        """Check if URL is US-specific or generic (no country code)."""
        url_lower = url.lower()
        
        # Allowed US patterns
        us_patterns = [
            "/us/", "/en-us/", "/us-en/", "/en_us/", "/us_en/",
        ]
        
        # Forbidden non-US patterns  
        non_us_patterns = [
            "/en-gb/", "/en-au/", "/en-ca/", "/en-nz/", "/en-eu/", 
            "/en-it/", "/en-ch/", "/gb/", "/au/", "/ca/", "/nz/",
            "/fr/", "/fr-", "/de/", "/es/", "/it/", "/pt/", "/ru/",
            "/zh/", "/jp/", "/kr/", "/mx/", "/br/", "/ar/", "/in/"
        ]
        
        # If has US pattern, it's US
        if any(pattern in url_lower for pattern in us_patterns):
            return True
            
        # If has non-US pattern, it's not US
        if any(pattern in url_lower for pattern in non_us_patterns):
            return False
            
        # If no country indicators, assume US (generic)
        return True
    
    def score_url(self, url: str) -> int:
        """Score URL relevance for policy/help pages."""
        url_lower = url.lower()
        score = 0
        
        # Primary keywords (high value)
        for kw in KEYWORDS_PRIMARY:
            if kw in url_lower:
                score += 5
        
        # Secondary keywords
        for kw in KEYWORDS_SECONDARY:
            if kw in url_lower:
                score += 3
        
        # Path-specific keywords
        for kw in PATH_KEYWORDS:
            if kw in url_lower:
                score += 4
        
        # Bonus for common policy paths
        if any(path in url_lower for path in ["/pages/", "/help/", "/support/", "/policies/"]):
            score += 2
        
        # Extra bonus for US-specific URLs
        if "/us/" in url_lower or "/en-us/" in url_lower:
            score += 3
        
        # Penalty for noise
        for noise in NOISE_PATTERNS:
            if noise in url_lower:
                score -= 2
        
        return max(0, score)
    
    async def fetch_url(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        """Fetch URL content with intelligent rate limiting."""
        import time
        
        # Get domain for rate limiting
        domain = urlparse(url).netloc
        current_time = time.time()
        
        # Check if we need to wait (rate limiting)
        if domain in self.last_request_time:
            time_since_last = current_time - self.last_request_time[domain]
            min_delay = self.request_delays.get(domain, 2.0)  # Default 2s delay
            
            if time_since_last < min_delay:
                wait_time = min_delay - time_since_last
                logger.debug(f"Rate limiting {domain}: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
        
        self.last_request_time[domain] = time.time()
        
        try:
            response = await client.get(url, follow_redirects=True)
            
            # Handle 429 Too Many Requests
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    delay = int(retry_after)
                    logger.warning(f"429 rate limit for {domain}, waiting {delay}s")
                    self.request_delays[domain] = max(delay, 5.0)  # At least 5s
                    await asyncio.sleep(delay)
                else:
                    # Exponential backoff
                    delay = self.request_delays.get(domain, 2.0) * 2
                    delay = min(delay, 30.0)  # Max 30s
                    logger.warning(f"429 rate limit for {domain}, backoff {delay}s")
                    self.request_delays[domain] = delay
                    await asyncio.sleep(delay)
                
                # Retry once
                response = await client.get(url, follow_redirects=True)
            
            if response.status_code == 200:
                return response.text
                
        except Exception as e:
            logger.debug(f"Failed to fetch {url}: {e}")
        return None
    
    async def fetch_sitemap_urls(self, client: httpx.AsyncClient) -> Set[str]:
        """Extract URLs from sitemaps."""
        urls = set()
        
        # Try robots.txt first
        robots_url = f"{self.base_url}/robots.txt"
        robots_content = await self.fetch_url(client, robots_url)
        sitemap_urls = []
        
        if robots_content:
            for line in robots_content.splitlines():
                if line.lower().startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    sitemap_urls.append(sitemap_url)
        
        # Fallback sitemap locations
        if not sitemap_urls:
            sitemap_urls = [
                f"{self.base_url}/sitemap.xml",
                f"{self.base_url}/sitemap_index.xml",
                f"{self.base_url}/sitemap.xml.gz"
            ]
        
        # Process each sitemap
        for sitemap_url in sitemap_urls:
            await self.process_sitemap(client, sitemap_url, urls)
        
        logger.info(f"Found {len(urls)} URLs from sitemaps")
        return urls
    
    async def process_sitemap(self, client: httpx.AsyncClient, sitemap_url: str, urls: Set[str]):
        """Process a single sitemap file."""
        try:
            response = await client.get(sitemap_url, follow_redirects=True)
            if response.status_code != 200:
                return
            
            content = response.content
            
            # Handle gzipped content
            if sitemap_url.endswith('.gz'):
                try:
                    content = gzip.decompress(content)
                except:
                    pass
            
            # Parse XML
            root = etree.fromstring(content)
            
            # Extract URLs from sitemap
            for loc in root.xpath("//*[local-name()='loc']/text()"):
                url = loc.strip()
                if url and self.is_same_domain(url) and self.is_english_url(url) and self.is_us_url(url):
                    urls.add(url)
            
            # Check for sitemap index (nested sitemaps)
            for sitemap_loc in root.xpath("//*[local-name()='sitemap']/*[local-name()='loc']/text()"):
                nested_url = sitemap_loc.strip()
                if nested_url and nested_url != sitemap_url:
                    await self.process_sitemap(client, nested_url, urls)
        
        except Exception as e:
            logger.debug(f"Failed to process sitemap {sitemap_url}: {e}")
    
    def extract_links_from_html(self, html_content: str, base_url: str) -> Set[str]:
        """Extract all links from HTML content."""
        links = set()
        try:
            doc = html.fromstring(html_content)
            
            # Find all links
            for element in doc.xpath('.//a[@href]'):
                href = element.get('href')
                if href:
                    # Convert relative URLs to absolute
                    full_url = urljoin(base_url, href)
                    # Clean fragment and query params for crawling
                    parsed = urlparse(full_url)
                    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                    
                    if (self.is_same_domain(clean_url) and 
                        self.is_english_url(clean_url) and 
                        self.is_us_url(clean_url) and
                        clean_url not in self.crawled_urls):
                        links.add(clean_url)
        
        except Exception as e:
            logger.debug(f"Failed to extract links from HTML: {e}")
        
        return links
    
    async def crawl_page(self, client: httpx.AsyncClient, url: str) -> Set[str]:
        """Crawl a single page and extract links."""
        if url in self.crawled_urls or len(self.crawled_urls) >= self.max_pages:
            return set()
        
        self.crawled_urls.add(url)
        logger.debug(f"Crawling: {url}")
        
        html_content = await self.fetch_url(client, url)
        if not html_content:
            return set()
        
        # Extract new links from this page
        new_links = self.extract_links_from_html(html_content, url)
        
        return new_links
    
    async def run_complete_crawl(self) -> List[str]:
        """Run complete crawl: sitemaps + page crawling."""
        timeout = httpx.Timeout(15.0)
        
        # REALISTIC headers to avoid bot detection
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Referer': f'https://{self.domain}/',
        }
        
        # CONSERVATIVE connection limits to avoid overwhelming servers
        limits = httpx.Limits(
            max_connections=2,        # Max 2 concurrent connections
            max_keepalive_connections=1  # Keep only 1 alive
        )
        
        async with httpx.AsyncClient(
            headers=headers, 
            timeout=timeout, 
            follow_redirects=True,
            limits=limits
        ) as client:
            
            # Step 1: Get URLs from sitemaps
            logger.info("Extracting URLs from sitemaps...")
            sitemap_urls = await self.fetch_sitemap_urls(client)
            self.found_urls.update(sitemap_urls)
            
            # Step 2: Crawl starting from homepage
            logger.info("Starting page crawling...")
            to_crawl = {self.base_url}
            self.found_urls.add(self.base_url)
            
            while to_crawl and len(self.crawled_urls) < self.max_pages:
                # Take batch of URLs to crawl
                current_batch = list(to_crawl)[:10]  # Process 10 at a time
                to_crawl = to_crawl - set(current_batch)
                
                # Crawl batch concurrently
                tasks = [self.crawl_page(client, url) for url in current_batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Collect new links
                for result in results:
                    if isinstance(result, set):
                        new_links = result - self.found_urls
                        self.found_urls.update(new_links)
                        to_crawl.update(new_links)
                
                logger.info(f"Crawled: {len(self.crawled_urls)}, Found: {len(self.found_urls)}, Queue: {len(to_crawl)}")
                
                # INTELLIGENT delay based on domain behavior
                base_delay = self.request_delays.get(self.domain, 3.0)
                await asyncio.sleep(base_delay)  # Adaptive delay per domain
        
        # Step 3: Score and filter URLs
        logger.info("Scoring and filtering URLs...")
        for url in self.found_urls:
            score = self.score_url(url)
            if score > 0:  # Only keep URLs with positive scores
                self.policy_urls.append((score, url))
        
        # Sort by score (highest first)
        self.policy_urls.sort(key=lambda x: (-x[0], x[1]))
        
        return [url for score, url in self.policy_urls]


async def find_policy_links(domain: str, limit: int = 20, max_pages: int = 500) -> List[str]:
    """Find policy/help links for a domain."""
    crawler = CompleteCrawler(domain, max_pages)
    all_policy_links = await crawler.run_complete_crawl()
    
    logger.info(f"Found {len(all_policy_links)} policy-related URLs")
    
    return all_policy_links[:limit]


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Find policy/help pages for any domain')
    parser.add_argument('--domain', help='Target domain')
    parser.add_argument('--limit', type=int, default=30, help='Max URLs to return')
    parser.add_argument('--max-pages', type=int, default=300, help='Max pages to crawl')
    parser.add_argument('--quiet', action='store_true', help='Only show URLs, no logs')
    
    args = parser.parse_args()
    
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    # Get domain from user
    if args.domain:
        domain = args.domain
    else:
        try:
            domain = input('Enter domain (e.g., example.com): ').strip()
        except KeyboardInterrupt:
            return
    
    if not domain:
        print('Domain is required.', file=sys.stderr)
        return
    
    if not args.quiet:
        print(f"\n🔍 Crawling {domain} for policy/help pages...\n")
    
    start_time = time.time()
    
    try:
        policy_links = await find_policy_links(domain, limit=args.limit, max_pages=args.max_pages)
        
        if args.quiet:
            for url in policy_links:
                print(url)
        else:
            print(f"\n✅ Found {len(policy_links)} policy/help URLs (sorted by relevance):\n")
            
            for i, url in enumerate(policy_links, 1):
                print(f"{i:2d}. {url}")
        
            elapsed = time.time() - start_time
            print(f"\n⏱️  Completed in {elapsed:.1f}s")
        
    except Exception as e:
        logger.error(f"Crawling failed: {e}")


if __name__ == '__main__':
    asyncio.run(main())
