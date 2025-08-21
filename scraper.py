
import asyncio
import re
from urllib.parse import urlparse
from typing import Dict, Optional, List
import requests
from bs4 import BeautifulSoup
from complete_crawler import find_policy_links

class EcommerceScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        })
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def scrape_website(self, url: str) -> Dict:
        """NEW OPTIMIZED scraper - uses complete_crawler to find ALL links first"""
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
            
            # STEP 2: Smart URL discovery with help domain check + AI prioritization
            print(f"  🔄 Finding policy URLs for domain: {domain}")
            policy_urls = await self._get_prioritized_policy_urls(domain)
            print(f"🔗 Found {len(policy_urls)} prioritized policy URLs")
            
            # STEP 3: SCRAPE ALL PAGES - let AI decide what's useful
            scraped_count = 0
            max_pages = 10  # Scrape more pages for better AI analysis
            
            print(f"  📚 Scraping ALL policy pages for comprehensive AI analysis...")
            
            for i, page_url in enumerate(policy_urls, 1):
                # ONLY stop if we hit the limit
                if scraped_count >= max_pages:
                    print(f"  ⏹️ Reached limit of {max_pages} pages")
                    break
                    
                try:
                    print(f"  📄 [{i}/{len(policy_urls)}] Scraping: {page_url}")
                    
                    # USE PLAYWRIGHT FOR ALL SITES - no more BeautifulSoup corruption
                    print(f"    🎭 Using Playwright for clean content extraction...")
                    content = await self._get_clean_content_playwright(page_url)
                    
                    if content and len(content) > 200:  # Minimum content threshold
                        page_type = self._classify_page_type(page_url, content)
                        
                        # STORE ALL PAGES - no skipping duplicates, let AI choose
                        page_key = f"{page_type}_{i}" if page_type in scraped_content['policy_pages'] else page_type
                        
                        scraped_content['policy_pages'][page_key] = {
                            'url': page_url,
                            'content': content
                        }
                        scraped_count += 1
                        
                        print(f"    📝 Stored as: {page_key} ({len(content)} chars)")
                        
                        # Add human-like delay between requests
                        import time
                        time.sleep(1.5)  # 1.5 second delay to avoid being flagged as bot
                        
                except Exception as e:
                    print(f"  ❌ Error scraping {page_url}: {e}")
                    continue
            
            print(f"📄 Total pages scraped: {len(scraped_content['policy_pages'])}")
            print(f"📚 ALL pages will be sent to AI for comprehensive analysis")
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
        
        return scraped_content

    def _classify_page_type(self, url: str, content: str) -> str:
        """Classify page type based on URL and content"""
        url_lower = url.lower()
        content_lower = content.lower()
        
        # Check URL patterns first
        if any(kw in url_lower for kw in ['shipping', 'delivery', 'fulfillment']):
            return 'shipping'
        elif any(kw in url_lower for kw in ['return', 'refund', 'exchange']):
            return 'returns'
        elif any(kw in url_lower for kw in ['faq', 'help', 'support']):
            return 'help'
        elif any(kw in url_lower for kw in ['contact', 'about']):
            return 'contact'
        
        # Check content patterns
        shipping_score = sum(1 for kw in ['shipping', 'delivery', 'fulfillment', 'ship'] if kw in content_lower)
        returns_score = sum(1 for kw in ['return', 'refund', 'exchange'] if kw in content_lower)
        
        if shipping_score > returns_score and shipping_score > 2:
            return 'shipping'
        elif returns_score > 2:
            return 'returns'
        else:
            return 'policy'
    
    def _extract_text_from_json(self, data) -> str:
        """Extract all text content from JSON data (general approach)"""
        text_content = ""
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 10:
                    # Check if this text contains policy-related content
                    if any(keyword in value.lower() for keyword in ['shipping', 'return', 'policy', 'delivery', 'refund', 'exchange', 'final sale', 'free shipping']):
                        text_content += f"{key}: {value}\n"
                elif isinstance(value, (dict, list)):
                    text_content += self._extract_text_from_json(value)
        elif isinstance(data, list):
            for item in data:
                text_content += self._extract_text_from_json(item)
        
        return text_content
    
    async def _get_prioritized_policy_urls(self, domain: str) -> List[str]:
        """Get policy URLs prioritized by AI and help domain checks"""
        import openai
        import os
        
        all_urls = []
        
        # STEP 1: Check help/support subdomains first (most likely to have policies)
        help_domains = [
            f"https://help.{domain}",
            f"https://support.{domain}",
            f"https://faq.{domain}",
            f"https://care.{domain}"
        ]
        
        print("  🔍 Checking help/support domains...")
        for help_url in help_domains:
            if await self._domain_exists(help_url):
                print(f"    ✅ Found active help domain: {help_url}")
                # Get URLs from this help domain
                help_urls = await find_policy_links(help_url.replace('https://', ''), limit=10, max_pages=50)
                all_urls.extend(help_urls[:10])  # Take top 10 from help domain
                break  # Stop at first working help domain
        
        # STEP 2: If no help domain, crawl main domain with fallback
        if not all_urls:
            print("  🔄 No help domain found, crawling main domain...")
            try:
                # Check if it's a Shopify site (common rate limiting)
                if await self._is_shopify_site(domain):
                    print("  🛍️ Shopify site detected, using smart approach...")
                    main_urls = await self._get_shopify_policy_urls(domain)
                else:
                    main_urls = await find_policy_links(domain, limit=20, max_pages=100)
                all_urls.extend(main_urls)
            except Exception as e:
                print(f"  ⚠️ Crawling failed ({e}), using fallback URLs...")
                # FALLBACK: Common policy URLs if crawling fails
                fallback_urls = self._get_fallback_policy_urls(domain)
                all_urls.extend(fallback_urls)
        
        # STEP 3: Use OpenAI to prioritize URLs by relevance
        if len(all_urls) > 5 and os.getenv("OPENAI_API_KEY"):
            print("  🤖 Using AI to prioritize URLs...")
            prioritized_urls = await self._ai_prioritize_urls(all_urls)
            return prioritized_urls[:10]  # Top 10 most relevant
        
        return all_urls[:10]  # Fallback: take first 10
    
    async def _domain_exists(self, url: str) -> bool:
        """Check if domain/subdomain exists and responds"""
        try:
            response = self.session.head(url, timeout=5)
            return response.status_code < 400
        except:
            return False
    
    async def _ai_prioritize_urls(self, urls: List[str]) -> List[str]:
        """Use OpenAI to prioritize URLs by relevance for shipping/returns policies"""
        import openai
        import os
        
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            urls_text = "\n".join([f"{i+1}. {url}" for i, url in enumerate(urls)])
            
            prompt = f"""Prioritize these URLs by relevance for finding shipping and return policies. 
Return ONLY the numbers (1-{len(urls)}) in order of priority, comma-separated.
Focus on: shipping, delivery, returns, refunds, exchanges, FAQ, help, support, policy pages.

URLs:
{urls_text}

Priority order (numbers only):"""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0
            )
            
            # Parse AI response
            priority_nums = response.choices[0].message.content.strip()
            priority_indices = [int(x.strip()) - 1 for x in priority_nums.split(',') if x.strip().isdigit()]
            
            # Reorder URLs based on AI priority
            prioritized = []
            for idx in priority_indices:
                if 0 <= idx < len(urls):
                    prioritized.append(urls[idx])
            
            # Add any missed URLs
            for url in urls:
                if url not in prioritized:
                    prioritized.append(url)
            
            print(f"    🎯 AI prioritized {len(prioritized)} URLs")
            return prioritized
            
        except Exception as e:
            print(f"    ⚠️ AI prioritization failed: {e}")
            return urls
    
    def _get_fallback_policy_urls(self, domain: str) -> List[str]:
        """Get common policy URLs as fallback when crawling fails"""
        base_url = f"https://{domain}"
        
        fallback_paths = [
            '/pages/shipping-policy', '/pages/shipping-information', '/pages/shipping',
            '/pages/return-policy', '/pages/returns-exchanges', '/pages/returns',
            '/pages/faq', '/pages/help', '/pages/support', '/pages/customer-service',
            '/help', '/support', '/faq', '/shipping', '/returns', '/policies',
            '/customer-service', '/customer-care', '/contact-us', '/about-us'
        ]
        
        return [f"{base_url}{path}" for path in fallback_paths]
    
    async def _is_shopify_site(self, domain: str) -> bool:
        """Detect if site is Shopify using multiple reliable signals"""
        base_url = f"https://{domain}"
        
        try:
            # 1) Headers check - most reliable
            response = self.session.head(base_url, timeout=12)
            headers = {k.lower(): v for k, v in response.headers.items()}
            
            if any(k.startswith("x-shopify") or k.startswith("x-sorting-hat") for k in headers):
                print(f"    🛍️ Shopify detected via headers")
                return True
            
            # 2) Cookies check
            set_cookie = response.headers.get("set-cookie", "").lower()
            if any(k in set_cookie for k in ["_shopify_", "cart_sig"]):
                print(f"    🛍️ Shopify detected via cookies")
                return True
            
        except Exception:
            pass

        # 3) Shopify endpoints check
        for path in ["/cart.js", "/products.json"]:
            try:
                response = self.session.get(base_url + path, timeout=12, headers={"Accept": "application/json"})
                if response.status_code == 200 and "application/json" in response.headers.get("content-type", ""):
                    print(f"    🛍️ Shopify detected via endpoint {path}")
                    return True
                time.sleep(1)  # Delay between endpoint checks
            except Exception:
                pass

        # 4) HTML content check (last resort)
        try:
            response = self.session.get(base_url, timeout=12)
            text = response.text
            if any(signal in text for signal in ["window.Shopify", "ShopifyAnalytics", "cdn.shopify.com", "/s/files/1/"]):
                print(f"    🛍️ Shopify detected via HTML content")
                return True
        except Exception:
            pass

        return False
    
    async def _get_shopify_policy_urls(self, domain: str) -> List[str]:
        """Get policy URLs for Shopify sites using known patterns + Playwright for JS content"""
        base_url = f"https://{domain}"
        
        # Shopify canonical URLs (highest priority)
        shopify_paths = [
            '/policies/shipping-policy', '/policies/refund-policy', '/policies/return-policy',
            '/policies/terms-of-service', '/policies/privacy-policy',
            '/pages/shipping-policy', '/pages/shipping-information', '/pages/shipping',
            '/pages/return-policy', '/pages/returns-exchanges', '/pages/returns',
            '/pages/refund-policy', '/pages/exchange-policy',
            '/pages/faq', '/pages/help', '/pages/customer-service'
        ]
        
        # Quick test for existing URLs
        valid_urls = []
        for path in shopify_paths[:8]:  # Test top 8 only
            try:
                url = f"{base_url}{path}"
                response = self.session.head(url, timeout=5)
                if response.status_code == 200:
                    valid_urls.append(url)
                    print(f"    ✅ Found Shopify page: {path}")
                
                import time
                time.sleep(1.5)  # Faster for URL testing
                
            except Exception:
                continue
        
        return valid_urls
    
    async def _get_clean_content_playwright(self, url: str) -> Optional[str]:
        """Extract clean content using Playwright (for ALL sites - no BeautifulSoup corruption)"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Set realistic headers
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                # Navigate and wait for content
                await page.goto(url, timeout=15000, wait_until='domcontentloaded')
                await page.wait_for_timeout(3000)  # Wait for JS to load content
                
                # Extract PERFECT clean text content
                content = await page.evaluate('''() => {
                    // Remove all problematic elements
                    const elementsToRemove = document.querySelectorAll('script, style, nav, header, footer, aside, noscript');
                    elementsToRemove.forEach(el => el.remove());
                    
                    // Get main content with priority selectors
                    const selectors = [
                        'main', '[role="main"]', '.main-content', '.content',
                        '.policy-content', '.page-content', '.rte', '.shopify-policy__container',
                        'article', '.article', '[class*="policy"]', '[class*="shipping"]', '[class*="return"]'
                    ];
                    
                    let mainElement = null;
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element && element.innerText.length > 200) {
                            mainElement = element;
                            break;
                        }
                    }
                    
                    // Fallback to body
                    const targetElement = mainElement || document.body;
                    
                    // Get clean text - no HTML, no corruption
                    return targetElement.innerText || targetElement.textContent || '';
                }''')
                
                await browser.close()
                
                if content and len(content) > 100:
                    print(f"    ✅ Playwright extracted {len(content)} chars")
                    return content[:10000]
                else:
                    print(f"    ⚠️ Playwright content too short: {len(content) if content else 0} chars")
                    return None
                    
        except Exception as e:
            print(f"    ❌ Playwright error: {e}")
            return None

    def _get_page_content_requests(self, url: str) -> Optional[str]:
        """Get page content using requests + BeautifulSoup"""
        try:
            print(f"  📥 Fetching {url}...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # SIMPLE AND EFFECTIVE cleaning (like the working version)
            import re
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Try to find main content area
            main_content = None
            content_selectors = [
                'main', '[role="main"]', '.main-content', '.content',
                '.policy-content', '.page-content', '.rte', '.shopify-policy__container',
                'article', '.article', '[class*="policy"]', '[class*="shipping"]', '[class*="return"]'
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
            
            # Extract text (SIMPLE approach like working version)
            text = main_content.get_text(separator=' ', strip=True)
            
            # Clean text (SIMPLE like working version)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            if len(text) > 50:
                print(f"  ✅ Extracted {len(text)} chars")
                return text[:10000]  # Limit for performance
            else:
                print(f"  ⚠️ Content too short: {len(text)} chars")
                return None
                
        except Exception as e:
            print(f"  ❌ Error fetching {url}: {e}")
            return None
