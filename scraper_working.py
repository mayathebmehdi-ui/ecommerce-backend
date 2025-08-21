import asyncio
import re
from urllib.parse import urlparse
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class EcommerceScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        })
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def scrape_website(self, url: str) -> Dict:
        """HYBRID scraper - combines requests + Playwright for best results"""
        domain = urlparse(url).netloc
        
        scraped_content = {
            'domain': domain,
            'main_url': url,
            'policy_pages': {}
        }
        
        try:
            print(f"🔍 Scraping {url}...")
            
            # STEP 1: Get main page with requests (fast)
            main_content = self._get_page_content_requests(url)
            if main_content:
                scraped_content['policy_pages']['main'] = {
                    'url': url,
                    'content': main_content
                }
                print(f"✅ Main page scraped: {len(main_content)} chars")
            
            # STEP 2: Find real policy URLs using Playwright (for JS sites)
            policy_urls = await self._find_policy_urls_playwright(url)
            print(f"🔗 Found {len(policy_urls)} policy URLs: {list(policy_urls.keys())}")
            
            # STEP 3: Scrape policy pages with requests (fast)
            for page_type, page_url in policy_urls.items():
                try:
                    content = self._get_page_content_requests(page_url)
                    if content and len(content) > 100:
                        scraped_content['policy_pages'][page_type] = {
                            'url': page_url,
                            'content': content
                        }
                        print(f"✅ Found {page_type} page: {len(content)} chars")
                        
                        # Stop after finding enough pages
                        if len(scraped_content['policy_pages']) >= 4:
                            break
                except Exception as e:
                    print(f"  ❌ Error scraping {page_url}: {e}")
                    continue
            
            # STEP 4: Try common paths if still not enough content
            if len(scraped_content['policy_pages']) <= 2:
                await self._try_common_paths(url, scraped_content)
            
            print(f"📄 Total pages scraped: {len(scraped_content['policy_pages'])}")
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
        
        return scraped_content

    async def _find_policy_urls_playwright(self, base_url: str) -> Dict[str, str]:
        """Use Playwright ONLY to find policy URLs (not scrape content)"""
        policy_urls = {}
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set headers
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Navigate with reasonable timeout
                await page.goto(base_url, timeout=20000, wait_until='domcontentloaded')
                
                # Extract all links
                links = await page.evaluate("""
                    () => {
                        const links = [];
                        document.querySelectorAll('a[href]').forEach(link => {
                            const href = link.href;
                            const text = link.textContent.toLowerCase().trim();
                            
                            // Look for policy-related links
                            if (href && (
                                text.includes('shipping') ||
                                text.includes('delivery') ||
                                text.includes('return') ||
                                text.includes('refund') ||
                                text.includes('help') ||
                                text.includes('support') ||
                                text.includes('faq') ||
                                text.includes('policy') ||
                                text.includes('customer service') ||
                                href.includes('shipping') ||
                                href.includes('return') ||
                                href.includes('help') ||
                                href.includes('policy') ||
                                href.includes('faq')
                            )) {
                                links.push({ href, text });
                            }
                        });
                        return links;
                    }
                """)
                
                await browser.close()
                
                # Categorize links
                for link in links[:15]:  # Limit to first 15 relevant links
                    href = link['href']
                    text = link['text']
                    
                    # Skip external links
                    if not href.startswith(base_url.rstrip('/')):
                        continue
                    
                    # Categorize by priority
                    if any(keyword in text.lower() or keyword in href.lower() for keyword in ['shipping', 'delivery']):
                        if 'shipping' not in policy_urls:
                            policy_urls['shipping'] = href
                    
                    if any(keyword in text.lower() or keyword in href.lower() for keyword in ['return', 'refund']):
                        if 'returns' not in policy_urls:
                            policy_urls['returns'] = href
                    
                    if any(keyword in text.lower() or keyword in href.lower() for keyword in ['help', 'support', 'faq', 'customer']):
                        if 'help' not in policy_urls:
                            policy_urls['help'] = href
                
        except Exception as e:
            print(f"  ⚠️ Playwright URL detection failed: {e}")
        
        return policy_urls

    async def _try_common_paths(self, base_url: str, scraped_content: Dict):
        """Try common policy paths if not enough content found"""
        base_domain = base_url.rstrip('/')
        
        # Extended list of common paths (including goodr.com specific patterns)
        common_paths = [
            # Shopify patterns (most common)
            '/pages/shipping',
            '/pages/returns', 
            '/pages/shipping-returns',
            '/pages/returns-exchanges',
            '/pages/returns-exchanges-and-warranties',  # goodr.com specific!
            '/pages/help',
            '/pages/faq',
            '/pages/shipping-policy',
            '/pages/return-policy',
            '/pages/delivery',
            '/pages/customer-service',
            '/pages/privacy-policy',
            
            # WooCommerce patterns
            '/shipping-info',
            '/return-info',
            '/customer-care',
            '/delivery-info',
            
            # General patterns
            '/support/shipping',
            '/support/returns',
            '/info/shipping',
            '/info/returns',
            '/help/shipping',
            '/help/returns',
            '/en/shipping',
            '/en/returns',
            '/us/shipping',
            '/us/returns'
        ]
        
        for path in common_paths:
            test_url = base_domain + path
            try:
                content = self._get_page_content_requests(test_url)
                if content and len(content) > 100:
                    page_type = 'shipping' if 'shipping' in path.lower() else 'returns' if 'return' in path.lower() else 'help'
                    
                    # Only add if we don't already have this type
                    if page_type not in scraped_content['policy_pages']:
                        scraped_content['policy_pages'][page_type] = {
                            'url': test_url,
                            'content': content
                        }
                        print(f"✅ Found {page_type} via common path: {test_url}")
                        
                        if len(scraped_content['policy_pages']) >= 4:
                            break
            except Exception:
                continue

    def _get_page_content_requests(self, url: str) -> Optional[str]:
        """Get clean text content using requests + BeautifulSoup"""
        try:
            print(f"  📥 Fetching {url}...")
            
            # Make request with longer timeout
            response = self.session.get(url, timeout=45)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript']):
                element.decompose()
            
            # Try to find main content with better selectors
            main_content = None
            content_selectors = [
                'main',
                '[role="main"]',
                '.main-content',
                '.content',
                '.policy',
                '.shipping',
                '.returns',
                '.faq',
                'article',
                '.page-content',
                '#content',
                '.container',
                '.wrapper',
                '.inner',
                '[class*="content"]',
                '[class*="policy"]',
                '[class*="shipping"]',
                '[class*="return"]'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                for element in elements:
                    text = element.get_text(strip=True)
                    if len(text) > 200:
                        main_content = element
                        break
                if main_content:
                    break
            
            # If no main content found, use body
            if not main_content:
                main_content = soup.body or soup
            
            # Extract text
            text = main_content.get_text(separator=' ', strip=True)
            
            # Clean text
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            if len(text) > 50:
                print(f"  ✅ Extracted {len(text)} chars")
                return text[:10000]  # Increased limit for more content
            else:
                print(f"  ⚠️ Content too short: {len(text)} chars")
                return None
                
        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout for {url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request error for {url}: {e}")
            return None
        except Exception as e:
            print(f"  ❌ Parse error for {url}: {e}")
            return None
