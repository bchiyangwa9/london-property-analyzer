
"""
Property Scraper Module for London Property Analyzer
Supports scraping from Rightmove, Zoopla, OnTheMarket, and other estate agent websites
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import random
from urllib.parse import urljoin, urlparse
import json
from typing import Dict, List, Optional, Tuple
import concurrent.futures
from threading import Lock

class PropertyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.request_lock = Lock()

        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ]

    def get_random_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid bot detection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def safe_request(self, url: str, delay: Tuple[int, int] = (2, 5)) -> Optional[requests.Response]:
        """Make a safe HTTP request with delays and error handling"""
        try:
            with self.request_lock:
                # Random delay between requests
                time.sleep(random.uniform(delay[0], delay[1]))

                response = self.session.get(
                    url, 
                    headers=self.get_random_headers(),
                    timeout=30,
                    allow_redirects=True
                )

                if response.status_code == 200:
                    return response
                else:
                    print(f"HTTP {response.status_code} for {url}")
                    return None

        except requests.RequestException as e:
            print(f"Request failed for {url}: {str(e)}")
            return None

    def extract_text_safe(self, soup, selector: str, default: str = "") -> str:
        """Safely extract text from BeautifulSoup element"""
        try:
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else default
        except Exception:
            return default

    def extract_price(self, text: str) -> Optional[int]:
        """Extract numeric price from text"""
        try:
            # Remove common price formatting and extract numbers
            price_match = re.search(r'£([\d,]+)', text.replace(',', ''))
            if price_match:
                return int(price_match.group(1).replace(',', ''))
            return None
        except Exception:
            return None

    def extract_bedrooms(self, text: str) -> Optional[int]:
        """Extract number of bedrooms from text"""
        try:
            # Look for patterns like "3 bed", "3 bedroom", "3-bed"
            bed_match = re.search(r'(\d+)\s*[-\s]?bed', text.lower())
            if bed_match:
                return int(bed_match.group(1))
            return None
        except Exception:
            return None

    def scrape_rightmove_property(self, url: str) -> Dict[str, any]:
        """Scrape individual Rightmove property page"""
        response = self.safe_request(url)
        if not response:
            return self.empty_property_dict(url, "Failed to fetch page")

        try:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract basic information
            price_text = self.extract_text_safe(soup, '.property-header-price')
            price = self.extract_price(price_text)

            # Property details
            property_type = self.extract_text_safe(soup, '.property-header-subtitle')
            bedrooms_text = self.extract_text_safe(soup, '.property-header-subtitle')
            bedrooms = self.extract_bedrooms(bedrooms_text)

            # Address and postcode
            address = self.extract_text_safe(soup, '.property-header-address')
            postcode = self.extract_postcode_from_address(address)

            # Agent information
            agent_name = self.extract_text_safe(soup, '.agent-name, .contactBranch-title')
            agent_phone = self.extract_text_safe(soup, '.agent-phone, .contactBranch-telephone')

            # Description
            description = self.extract_text_safe(soup, '.property-description')

            # Images
            images = self.extract_images_rightmove(soup)

            return {
                'property_id': f"RM_{url.split('/')[-1]}",
                'url': url,
                'price': price,
                'property_type': property_type,
                'bedrooms': bedrooms,
                'postcode': postcode,
                'address': address,
                'agent_name': agent_name,
                'agent_phone': agent_phone,
                'description': description[:500] if description else "",  # Limit length
                'images': images[:3],  # Limit to 3 images
                'source': 'Rightmove',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            return self.empty_property_dict(url, f"Parsing error: {str(e)}")

    def scrape_zoopla_property(self, url: str) -> Dict[str, any]:
        """Scrape individual Zoopla property page"""
        response = self.safe_request(url)
        if not response:
            return self.empty_property_dict(url, "Failed to fetch page")

        try:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Zoopla has different selectors
            price_text = self.extract_text_safe(soup, '.price-header, .pricing-banner-price')
            price = self.extract_price(price_text)

            property_type = self.extract_text_safe(soup, '.property-type, .property-summary-text')
            bedrooms_text = self.extract_text_safe(soup, '.property-features, .property-summary-text')
            bedrooms = self.extract_bedrooms(bedrooms_text)

            address = self.extract_text_safe(soup, '.property-address, .address-label')
            postcode = self.extract_postcode_from_address(address)

            agent_name = self.extract_text_safe(soup, '.agent-name, .branch-name')
            agent_phone = self.extract_text_safe(soup, '.agent-phone, .branch-phone')

            description = self.extract_text_safe(soup, '.property-description, .description-text')

            images = self.extract_images_zoopla(soup)

            return {
                'property_id': f"ZP_{url.split('/')[-2]}",
                'url': url,
                'price': price,
                'property_type': property_type,
                'bedrooms': bedrooms,
                'postcode': postcode,
                'address': address,
                'agent_name': agent_name,
                'agent_phone': agent_phone,
                'description': description[:500] if description else "",
                'images': images[:3],
                'source': 'Zoopla',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            return self.empty_property_dict(url, f"Parsing error: {str(e)}")

    def scrape_onthemarket_property(self, url: str) -> Dict[str, any]:
        """Scrape individual OnTheMarket property page"""
        response = self.safe_request(url)
        if not response:
            return self.empty_property_dict(url, "Failed to fetch page")

        try:
            soup = BeautifulSoup(response.content, 'html.parser')

            price_text = self.extract_text_safe(soup, '.price, .property-price')
            price = self.extract_price(price_text)

            property_type = self.extract_text_safe(soup, '.property-type, .property-details')
            bedrooms_text = self.extract_text_safe(soup, '.bedrooms, .property-icon-bed')
            bedrooms = self.extract_bedrooms(bedrooms_text)

            address = self.extract_text_safe(soup, '.address, .property-address')
            postcode = self.extract_postcode_from_address(address)

            agent_name = self.extract_text_safe(soup, '.agent-name, .branch-details')
            agent_phone = self.extract_text_safe(soup, '.agent-phone, .phone-number')

            description = self.extract_text_safe(soup, '.description, .property-description')

            images = self.extract_images_generic(soup)

            return {
                'property_id': f"OTM_{url.split('/')[-1]}",
                'url': url,
                'price': price,
                'property_type': property_type,
                'bedrooms': bedrooms,
                'postcode': postcode,
                'address': address,
                'agent_name': agent_name,
                'agent_phone': agent_phone,
                'description': description[:500] if description else "",
                'images': images[:3],
                'source': 'OnTheMarket',
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            return self.empty_property_dict(url, f"Parsing error: {str(e)}")

    def extract_postcode_from_address(self, address: str) -> Optional[str]:
        """Extract UK postcode from address string"""
        try:
            # UK postcode regex pattern
            postcode_pattern = r'[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}'
            match = re.search(postcode_pattern, address.upper())
            return match.group().strip() if match else None
        except Exception:
            return None

    def extract_images_rightmove(self, soup) -> List[str]:
        """Extract image URLs from Rightmove page"""
        try:
            images = []
            for img in soup.select('.property-image img, .carousel-image img')[:3]:
                src = img.get('src') or img.get('data-src')
                if src:
                    images.append(src)
            return images
        except Exception:
            return []

    def extract_images_zoopla(self, soup) -> List[str]:
        """Extract image URLs from Zoopla page"""
        try:
            images = []
            for img in soup.select('.gallery-image img, .image-gallery img')[:3]:
                src = img.get('src') or img.get('data-src')
                if src:
                    images.append(src)
            return images
        except Exception:
            return []

    def extract_images_generic(self, soup) -> List[str]:
        """Extract images using generic selectors"""
        try:
            images = []
            for img in soup.select('img[src*="property"], img[src*="image"]')[:3]:
                src = img.get('src')
                if src and ('property' in src.lower() or 'image' in src.lower()):
                    images.append(src)
            return images
        except Exception:
            return []

    def empty_property_dict(self, url: str, error_msg: str) -> Dict[str, any]:
        """Return empty property dictionary with error information"""
        return {
            'property_id': f"ERROR_{hash(url) % 10000}",
            'url': url,
            'price': None,
            'property_type': "",
            'bedrooms': None,
            'postcode': "",
            'address': "",
            'agent_name': "",
            'agent_phone': "",
            'description': f"Scraping failed: {error_msg}",
            'images': [],
            'source': 'Unknown',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'error': error_msg
        }

    def detect_property_site(self, url: str) -> str:
        """Detect which property site the URL belongs to"""
        url_lower = url.lower()
        if 'rightmove' in url_lower:
            return 'rightmove'
        elif 'zoopla' in url_lower:
            return 'zoopla'
        elif 'onthemarket' in url_lower:
            return 'onthemarket'
        else:
            return 'generic'

    def scrape_single_property(self, url: str) -> Dict[str, any]:
        """Scrape a single property URL - auto-detects site"""
        site = self.detect_property_site(url)

        if site == 'rightmove':
            return self.scrape_rightmove_property(url)
        elif site == 'zoopla':
            return self.scrape_zoopla_property(url)
        elif site == 'onthemarket':
            return self.scrape_onthemarket_property(url)
        else:
            return self.empty_property_dict(url, "Unsupported website")

    def scrape_multiple_properties(self, urls: List[str], max_workers: int = 3) -> List[Dict[str, any]]:
        """Scrape multiple properties in parallel with rate limiting"""
        results = []

        # Process in batches to avoid overwhelming servers
        batch_size = max_workers
        for i in range(0, len(urls), batch_size):
            batch_urls = urls[i:i + batch_size]

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {
                    executor.submit(self.scrape_single_property, url): url 
                    for url in batch_urls
                }

                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        result = future.result()
                        results.append(result)
                        print(f"✓ Scraped: {url}")
                    except Exception as e:
                        error_result = self.empty_property_dict(url, f"Thread error: {str(e)}")
                        results.append(error_result)
                        print(f"✗ Failed: {url} - {str(e)}")

            # Pause between batches
            if i + batch_size < len(urls):
                time.sleep(random.uniform(5, 10))

        return results

    def generate_search_urls(self, postcode: str, radius: int = 5, min_price: int = None, 
                           max_price: int = None, min_bedrooms: int = None, 
                           property_type: str = None) -> Dict[str, str]:
        """Generate search URLs for different property sites"""

        # Clean postcode for URL usage
        postcode_clean = postcode.replace(' ', '+')
        
        # Convert postcode to area name for OnTheMarket (basic mapping)
        # This is a simplified approach - a real implementation would use a postcode lookup service
        postcode_to_area = {
            'SE9': 'sidcup',
            'SE1': 'london-bridge', 
            'SW1': 'westminster',
            'N1': 'islington',
            'E1': 'whitechapel',
            'W1': 'oxford-street',
            'EC1': 'clerkenwell',
            'WC1': 'bloomsbury',
            'NW1': 'regents-park',
            'SE10': 'greenwich',
            'SE3': 'blackheath',
            'BR1': 'bromley',
            'DA14': 'sidcup',
            'DA15': 'sidcup'
        }
        
        # Extract the basic postcode area (e.g., SE9 from SE9 0AA)
        basic_postcode = postcode.split()[0] if ' ' in postcode else postcode[:3]
        area_name = postcode_to_area.get(basic_postcode, postcode_clean.lower())

        urls = {}

        # Rightmove search URL - Use OUTCODE format which is more reliable
        # This approach uses outcode (first part of postcode) which is more widely supported
        rightmove_params = []
        if min_price:
            rightmove_params.append(f"minPrice={min_price}")
        if max_price:
            rightmove_params.append(f"maxPrice={max_price}")
        if min_bedrooms:
            rightmove_params.append(f"minBedrooms={min_bedrooms}")
        if property_type and property_type != "Any":
            type_map = {"House": "houses", "Flat": "flats", "Bungalow": "bungalows"}
            rightmove_params.append(f"propertyTypes={type_map.get(property_type, 'houses')}")
        
        # Use locationIdentifier with OUTCODE format for better compatibility
        rightmove_params.append(f"radius={radius}")
        outcode = basic_postcode.upper()
        rightmove_url = f"https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=OUTCODE%5E{outcode}&{'&'.join(rightmove_params)}"
        urls['Rightmove'] = rightmove_url

        # Zoopla search URL (working correctly)
        zoopla_params = []
        if min_price:
            zoopla_params.append(f"price_min={min_price}")
        if max_price:
            zoopla_params.append(f"price_max={max_price}")
        if min_bedrooms:
            zoopla_params.append(f"beds_min={min_bedrooms}")

        zoopla_url = f"https://www.zoopla.co.uk/for-sale/property/{postcode_clean}/?{'&'.join(zoopla_params)}"
        urls['Zoopla'] = zoopla_url

        # OnTheMarket search URL - Use area name instead of postcode
        otm_params = []
        if min_price:
            otm_params.append(f"min-price={min_price}")
        if max_price:
            otm_params.append(f"max-price={max_price}")
        if min_bedrooms:
            otm_params.append(f"min-bedrooms={min_bedrooms}")

        # Use area name derived from postcode
        otm_url = f"https://www.onthemarket.com/for-sale/property/{area_name}/?{'&'.join(otm_params)}"
        urls['OnTheMarket'] = otm_url

        return urls
def test_scraper():
    """Test the scraper with sample URLs"""
    scraper = PropertyScraper()

    # Test URLs (replace with actual property URLs for testing)
    test_urls = [
        "https://www.rightmove.co.uk/properties/123456789",  # Replace with real URL
        "https://www.zoopla.co.uk/for-sale/details/123456789"  # Replace with real URL
    ]

    for url in test_urls:
        print(f"Testing URL: {url}")
        result = scraper.scrape_single_property(url)
        print(json.dumps(result, indent=2))
        print("-" * 50)

if __name__ == "__main__":
    test_scraper()
