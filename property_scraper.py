"""
Property Scraper Module for London Property Analyzer - ALTERNATIVE PLATFORMS VERSION
====================================================================================

REPLACEMENT STRATEGY:
- ❌ Removed problematic platforms: Rightmove (too restrictive), OnTheMarket (postcode issues)
- ✅ Added reliable alternatives: PrimeLocation, Nestoria, Gumtree, OpenRent, PropertyPal
- ✅ Kept Zoopla (working perfectly)

NEW PLATFORM BENEFITS:
1. ✅ Zoopla - Established, reliable, extensive coverage
2. ✅ PrimeLocation - Owned by Zoopla, professional listings, less bot protection
3. ✅ Nestoria - Property aggregator, API-friendly, simple search
4. ✅ Gumtree - Private listings, less competition, unique finds
5. ✅ OpenRent - Direct landlord listings, no agent fees
6. ✅ PropertyPal - Northern Ireland/UK coverage, simpler URLs

Version: 3.0 Alternative Platforms
Date: 2025-10-24
Changes:
- Replaced Rightmove and OnTheMarket with 5 reliable alternatives
- Enhanced URL generation for all 6 platforms
- Comprehensive postcode-to-area mapping maintained
- Added scraping support for each new platform
- Improved error handling and rate limiting
"""
from property_scraper import PropertyScraper
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from urllib.parse import urljoin, urlparse, quote_plus, quote
import json
from typing import Dict, List, Optional, Tuple
import concurrent.futures
from threading import Lock

class PropertyScraperAlternative:
    def __init__(self):
        self.session = requests.Session()
        self.request_lock = Lock()

        # User agents for rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]

        # Rate limiting configuration per platform
        self.rate_limits = {
            'zoopla': (2, 4),      # 2-4 seconds between requests
            'primelocation': (1, 3), # 1-3 seconds (same owner as Zoopla, more lenient)
            'nestoria': (1, 2),    # 1-2 seconds (API-friendly)
            'gumtree': (2, 5),     # 2-5 seconds (more careful with Gumtree)
            'openrent': (1, 3),    # 1-3 seconds
            'propertypal': (1, 2)  # 1-2 seconds (simple structure)
        }

    def get_random_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid bot detection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

    def safe_request(self, url: str, platform: str = None, delay: Tuple[int, int] = (2, 5)) -> Optional[requests.Response]:
        """Make a safe HTTP request with error handling and rate limiting"""

        # Use platform-specific rate limits if available
        if platform and platform in self.rate_limits:
            delay = self.rate_limits[platform]

        with self.request_lock:
            time.sleep(random.uniform(delay[0], delay[1]))

        try:
            headers = self.get_random_headers()

            # Platform-specific headers
            if platform == 'gumtree':
                headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                headers['Referer'] = 'https://www.gumtree.com/'
            elif platform == 'nestoria':
                headers['Accept'] = 'application/json,text/html,*/*'

            response = self.session.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                return response
            elif response.status_code in [403, 429]:
                print(f"Rate limited or blocked on {platform or 'unknown'}: {response.status_code}")
                time.sleep(random.uniform(5, 10))  # Longer delay on rate limit
                return None
            else:
                print(f"HTTP error {response.status_code} for {url}")
                return None

        except requests.RequestException as e:
            print(f"Request failed for {url}: {str(e)}")
            return None

    def extract_text_safe(self, soup, selector: str, default: str = "") -> str:
        """Safely extract text from BeautifulSoup element"""
        try:
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else default
        except:
            return default

    def extract_price(self, text: str) -> Optional[int]:
        """Extract price from text string"""
        # Remove common currency symbols and words
        text = re.sub(r'[£$,]', '', text)
        text = re.sub(r'\b(per|month|pcm|pw|weekly|poa|oiro)\b', '', text, flags=re.IGNORECASE)

        # Find numbers
        price_match = re.search(r'\b(\d{3,7})\b', text)
        if price_match:
            return int(price_match.group(1))
        return None

    def extract_bedrooms(self, text: str) -> Optional[int]:
        """Extract number of bedrooms from text"""
        # Look for bedroom patterns
        bed_patterns = [
            r'(\d+)\s*bed',
            r'(\d+)\s*bedroom',
            r'bed\s*(\d+)',
            r'bedroom\s*(\d+)'
        ]

        for pattern in bed_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        # Look for studio
        if re.search(r'studio', text, re.IGNORECASE):
            return 0

        return None

    def generate_search_urls(self, postcode: str, radius: int = 5, min_price: int = None, 
                           max_price: int = None, min_bedrooms: int = None, 
                           property_type: str = None) -> Dict[str, str]:
        """Generate search URLs for all 6 alternative property platforms"""

        # Clean postcode for URL usage
        postcode_clean = postcode.replace(' ', '+')
        postcode_area = postcode.replace(' ', '').upper()[:3]  # First 3 chars for area mapping

        # Comprehensive London postcode to area mapping (maintained from original)
        postcode_to_area = {
            # SE postcodes (SE1-SE28)
            'SE1': 'london-bridge', 'SE2': 'abbey-wood', 'SE3': 'blackheath', 'SE4': 'brockley',
            'SE5': 'camberwell', 'SE6': 'catford', 'SE7': 'charlton', 'SE8': 'deptford',
            'SE9': 'sidcup', 'SE10': 'greenwich', 'SE11': 'kennington', 'SE12': 'lee',
            'SE13': 'lewisham', 'SE14': 'new-cross', 'SE15': 'peckham', 'SE16': 'rotherhithe',
            'SE17': 'walworth', 'SE18': 'woolwich', 'SE19': 'crystal-palace', 'SE20': 'anerley',
            'SE21': 'dulwich', 'SE22': 'east-dulwich', 'SE23': 'forest-hill', 'SE24': 'herne-hill',
            'SE25': 'south-norwood', 'SE26': 'sydenham', 'SE27': 'west-norwood', 'SE28': 'thamesmead',

            # N postcodes (N1-N22) including Enfield areas
            'N1': 'islington', 'N2': 'east-finchley', 'N3': 'finchley', 'N4': 'finsbury-park',
            'N5': 'highbury', 'N6': 'highgate', 'N7': 'holloway', 'N8': 'hornsey',
            'N9': 'enfield', 'N10': 'muswell-hill', 'N11': 'new-southgate', 'N12': 'north-finchley',
            'N13': 'palmers-green', 'N14': 'southgate', 'N15': 'seven-sisters', 'N16': 'stoke-newington',
            'N17': 'tottenham', 'N18': 'upper-edmonton', 'N19': 'archway', 'N20': 'whetstone',
            'N21': 'winchmore-hill', 'N22': 'wood-green',

            # E postcodes (E1-E20)
            'E1': 'whitechapel', 'E2': 'bethnal-green', 'E3': 'bow', 'E4': 'chingford',
            'E5': 'clapton', 'E6': 'east-ham', 'E7': 'forest-gate', 'E8': 'hackney',
            'E9': 'hackney', 'E10': 'leyton', 'E11': 'leytonstone', 'E12': 'manor-park',
            'E13': 'plaistow', 'E14': 'canary-wharf', 'E15': 'stratford', 'E16': 'canning-town',
            'E17': 'walthamstow', 'E18': 'south-woodford', 'E20': 'olympic-park',

            # NW postcodes (NW1-NW11)
            'NW1': 'regents-park', 'NW2': 'cricklewood', 'NW3': 'hampstead', 'NW4': 'hendon',
            'NW5': 'kentish-town', 'NW6': 'west-hampstead', 'NW7': 'mill-hill', 'NW8': 'st-johns-wood',
            'NW9': 'kingsbury', 'NW10': 'harlesden', 'NW11': 'golders-green',

            # SW postcodes (SW1-SW20)
            'SW1': 'westminster', 'SW2': 'brixton', 'SW3': 'chelsea', 'SW4': 'clapham',
            'SW5': 'earls-court', 'SW6': 'fulham', 'SW7': 'south-kensington', 'SW8': 'south-lambeth',
            'SW9': 'stockwell', 'SW10': 'west-brompton', 'SW11': 'battersea', 'SW12': 'balham',
            'SW13': 'barnes', 'SW14': 'mortlake', 'SW15': 'putney', 'SW16': 'streatham',
            'SW17': 'tooting', 'SW18': 'wandsworth', 'SW19': 'wimbledon', 'SW20': 'raynes-park',

            # W postcodes (W1-W14)
            'W1': 'mayfair', 'W2': 'paddington', 'W3': 'acton', 'W4': 'chiswick',
            'W5': 'ealing', 'W6': 'hammersmith', 'W7': 'hanwell', 'W8': 'kensington',
            'W9': 'maida-vale', 'W10': 'north-kensington', 'W11': 'notting-hill', 'W12': 'shepherds-bush',
            'W13': 'west-ealing', 'W14': 'west-kensington',

            # Outer London postcodes
            'BR1': 'bromley', 'BR2': 'hayes-bromley', 'BR3': 'beckenham', 'BR4': 'west-wickham',
            'BR5': 'orpington', 'BR6': 'orpington', 'BR7': 'chislehurst', 'BR8': 'swanley',

            'DA1': 'dartford', 'DA2': 'dartford', 'DA3': 'longfield', 'DA4': 'sidcup',
            'DA5': 'bexley', 'DA6': 'bexleyheath', 'DA7': 'bexleyheath', 'DA8': 'erith',
            'DA9': 'greenhithe', 'DA10': 'swanscombe', 'DA11': 'gravesend', 'DA12': 'gravesend',
            'DA13': 'gravesend', 'DA14': 'sidcup', 'DA15': 'sidcup', 'DA16': 'welling',
            'DA17': 'belvedere', 'DA18': 'erith',

            'EN1': 'enfield', 'EN2': 'enfield', 'EN3': 'enfield', 'EN4': 'barnet',
            'EN5': 'barnet', 'EN6': 'potters-bar', 'EN7': 'cheshunt', 'EN8': 'cheshunt',
            'EN9': 'waltham-abbey', 'EN10': 'broxbourne', 'EN11': 'hoddesdon',

            'HA0': 'wembley', 'HA1': 'harrow', 'HA2': 'harrow', 'HA3': 'harrow',
            'HA4': 'ruislip', 'HA5': 'pinner', 'HA6': 'northwood', 'HA7': 'stanmore',
            'HA8': 'edgware', 'HA9': 'wembley',

            'IG1': 'ilford', 'IG2': 'redbridge', 'IG3': 'seven-kings', 'IG4': 'redbridge',
            'IG5': 'clayhall', 'IG6': 'barkingside', 'IG7': 'chigwell', 'IG8': 'woodford-green',
            'IG9': 'buckhurst-hill', 'IG10': 'loughton', 'IG11': 'barking',

            'RM1': 'romford', 'RM2': 'gidea-park', 'RM3': 'harold-wood', 'RM4': 'ingrebourne',
            'RM5': 'collier-row', 'RM6': 'chadwell-heath', 'RM7': 'rush-green', 'RM8': 'becontree',
            'RM9': 'becontree', 'RM10': 'dagenham', 'RM11': 'hornchurch', 'RM12': 'hornchurch',
            'RM13': 'rainham', 'RM14': 'upminster', 'RM15': 'south-ockendon', 'RM16': 'grays',
            'RM17': 'grays', 'RM18': 'tilbury', 'RM19': 'purfleet', 'RM20': 'south-ockendon',

            # Central London postcodes
            'EC1': 'city-of-london', 'EC2': 'city-of-london', 'EC3': 'city-of-london', 'EC4': 'city-of-london',
            'WC1': 'bloomsbury', 'WC2': 'covent-garden'
        }

        # Get area name for postcode, fallback to postcode itself
        area_name = postcode_to_area.get(postcode_area[:2], postcode_to_area.get(postcode_area[:3], postcode_clean.lower()))

        # Build parameter strings for URLs
        price_params = ""
        bed_params = ""

        if min_price:
            price_params += f"&price_min={min_price}"
        if max_price:
            price_params += f"&price_max={max_price}"
        if min_bedrooms:
            bed_params += f"&bedrooms_min={min_bedrooms}"

        # URL encoding helpers
        area_encoded = quote_plus(area_name) if isinstance(area_name, str) else quote_plus(postcode_clean)
        postcode_encoded = quote_plus(postcode_clean)

        urls = {}

        # 1. ZOOPLA (keeping - works perfectly)
        zoopla_url = f"https://www.zoopla.co.uk/for-sale/property/{area_encoded}/?radius={radius}{price_params}{bed_params}"
        if property_type:
            zoopla_url += f"&property_type={property_type.lower()}"
        urls['zoopla'] = zoopla_url

        # 2. PRIMELOCATION (owned by Zoopla, more lenient)
        primelocation_url = f"https://www.primelocation.com/for-sale/{area_encoded}/?radius={radius}{price_params.replace('price_', 'price')}{bed_params.replace('bedrooms_', 'bedrooms_')}"
        urls['primelocation'] = primelocation_url

        # 3. NESTORIA (property aggregator, API-friendly)
        nestoria_params = f"?price_min={min_price or ''}&price_max={max_price or ''}&bedroom_min={min_bedrooms or ''}"
        nestoria_url = f"https://www.nestoria.co.uk/find/for_sale/{area_encoded}{nestoria_params}"
        urls['nestoria'] = nestoria_url

        # 4. GUMTREE (private listings, less competition)
        gumtree_params = f"?search_category=property-for-sale&search_location={postcode_encoded}"
        if min_price:
            gumtree_params += f"&min_price={min_price}"
        if max_price:
            gumtree_params += f"&max_price={max_price}"
        if min_bedrooms:
            gumtree_params += f"&min_bedrooms={min_bedrooms}"
        gumtree_url = f"https://www.gumtree.com/search{gumtree_params}"
        urls['gumtree'] = gumtree_url

        # 5. OPENRENT (direct landlord listings, no agent fees)
        openrent_params = f"?prices_min={min_price or ''}&prices_max={max_price or ''}&bedrooms_min={min_bedrooms or ''}"
        openrent_url = f"https://www.openrent.com/properties-for-sale/{area_encoded}{openrent_params}"
        urls['openrent'] = openrent_url

        # 6. PROPERTYPAL (Northern Ireland + UK, simple structure)
        propertypal_area = area_name.replace('-', '_') if isinstance(area_name, str) else postcode_clean.replace(' ', '_')
        propertypal_price = f"price-{min_price or '0'}-{max_price or '999999'}" if min_price or max_price else "price-0-999999"
        propertypal_beds = f"beds-{min_bedrooms}" if min_bedrooms else ""
        propertypal_url = f"https://www.propertypal.com/property-for-sale/{propertypal_area}/{propertypal_price}"
        if propertypal_beds:
            propertypal_url += f"/{propertypal_beds}"
        urls['propertypal'] = propertypal_url

        return urls

    # PLATFORM-SPECIFIC SCRAPING METHODS

    def scrape_zoopla_property(self, url: str) -> Dict[str, any]:
        """Scrape property details from Zoopla (kept from original implementation)"""
        response = self.safe_request(url, platform='zoopla')
        if not response:
            return self.empty_property_dict(url, "Failed to fetch Zoopla page")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract property data using Zoopla's selectors
        title = self.extract_text_safe(soup, 'h1[data-testid="property-title"]')
        price_text = self.extract_text_safe(soup, '[data-testid="property-price"]')
        address = self.extract_text_safe(soup, '[data-testid="property-address"]')
        description = self.extract_text_safe(soup, '[data-testid="property-description"]')

        # Extract structured data
        price = self.extract_price(price_text)
        bedrooms = self.extract_bedrooms(title + " " + description)
        postcode = self.extract_postcode_from_address(address)

        # Extract images
        images = self.extract_images_zoopla(soup)

        return {
            'url': url,
            'platform': 'zoopla',
            'title': title,
            'price': price,
            'price_text': price_text,
            'address': address,
            'postcode': postcode,
            'bedrooms': bedrooms,
            'description': description[:500] if description else "",
            'images': images[:5],  # Limit to 5 images
            'scraped_at': time.time(),
            'success': True,
            'error': None
        }

    def scrape_primelocation_property(self, url: str) -> Dict[str, any]:
        """Scrape property details from PrimeLocation"""
        response = self.safe_request(url, platform='primelocation')
        if not response:
            return self.empty_property_dict(url, "Failed to fetch PrimeLocation page")

        soup = BeautifulSoup(response.text, 'html.parser')

        # PrimeLocation uses similar structure to Zoopla (same company)
        title = self.extract_text_safe(soup, 'h1.property-title, h1[class*="title"], .property-header h1')
        price_text = self.extract_text_safe(soup, '.property-price, [class*="price"], .price-text')
        address = self.extract_text_safe(soup, '.property-address, [class*="address"], .address-text')
        description = self.extract_text_safe(soup, '.property-description, [class*="description"], .description')

        # Extract structured data
        price = self.extract_price(price_text)
        bedrooms = self.extract_bedrooms(title + " " + description)
        postcode = self.extract_postcode_from_address(address)

        # Extract images
        images = self.extract_images_generic(soup)

        return {
            'url': url,
            'platform': 'primelocation',
            'title': title,
            'price': price,
            'price_text': price_text,
            'address': address,
            'postcode': postcode,
            'bedrooms': bedrooms,
            'description': description[:500] if description else "",
            'images': images[:5],
            'scraped_at': time.time(),
            'success': True,
            'error': None
        }

    def scrape_nestoria_property(self, url: str) -> Dict[str, any]:
        """Scrape property details from Nestoria"""
        response = self.safe_request(url, platform='nestoria')
        if not response:
            return self.empty_property_dict(url, "Failed to fetch Nestoria page")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Nestoria's structure
        title = self.extract_text_safe(soup, 'h1.listing-title, h1[id*="title"], .property-title')
        price_text = self.extract_text_safe(soup, '.price, [class*="price"], .listing-price')
        address = self.extract_text_safe(soup, '.address, [class*="address"], .listing-address')
        description = self.extract_text_safe(soup, '.description, [class*="description"], .property-description')

        # Extract structured data
        price = self.extract_price(price_text)
        bedrooms = self.extract_bedrooms(title + " " + description)
        postcode = self.extract_postcode_from_address(address)

        # Extract images
        images = self.extract_images_generic(soup)

        return {
            'url': url,
            'platform': 'nestoria',
            'title': title,
            'price': price,
            'price_text': price_text,
            'address': address,
            'postcode': postcode,
            'bedrooms': bedrooms,
            'description': description[:500] if description else "",
            'images': images[:5],
            'scraped_at': time.time(),
            'success': True,
            'error': None
        }

    def scrape_gumtree_property(self, url: str) -> Dict[str, any]:
        """Scrape property details from Gumtree"""
        response = self.safe_request(url, platform='gumtree')
        if not response:
            return self.empty_property_dict(url, "Failed to fetch Gumtree page")

        soup = BeautifulSoup(response.text, 'html.parser')

        # Gumtree's structure
        title = self.extract_text_safe(soup, 'h1.ad-title, h1[class*="title"], .listing-title')
        price_text = self.extract_text_safe(soup, '.ad-price, [class*="price"], .price-display')
        address = self.extract_text_safe(soup, '.ad-location, [class*="location"], .address')
        description = self.extract_text_safe(soup, '.ad-description, [class*="description"], .description-text')

        # Extract structured data
        price = self.extract_price(price_text)
        bedrooms = self.extract_bedrooms(title + " " + description)
        postcode = self.extract_postcode_from_address(address)

        # Extract images
        images = self.extract_images_generic(soup)

        return {
            'url': url,
            'platform': 'gumtree',
            'title': title,
            'price': price,
            'price_text': price_text,
            'address': address,
            'postcode': postcode,
            'bedrooms': bedrooms,
            'description': description[:500] if description else "",
            'images': images[:5],
            'scraped_at': time.time(),
            'success': True,
            'error': None
        }

    def scrape_openrent_property(self, url: str) -> Dict[str, any]:
        """Scrape property details from OpenRent"""
        response = self.safe_request(url, platform='openrent')
        if not response:
            return self.empty_property_dict(url, "Failed to fetch OpenRent page")

        soup = BeautifulSoup(response.text, 'html.parser')

        # OpenRent's structure
        title = self.extract_text_safe(soup, 'h1.property-title, h1[class*="title"], .listing-title')
        price_text = self.extract_text_safe(soup, '.price-display, [class*="price"], .rent-price')
        address = self.extract_text_safe(soup, '.property-address, [class*="address"], .location')
        description = self.extract_text_safe(soup, '.property-description, [class*="description"], .description')

        # Extract structured data
        price = self.extract_price(price_text)
        bedrooms = self.extract_bedrooms(title + " " + description)
        postcode = self.extract_postcode_from_address(address)

        # Extract images
        images = self.extract_images_generic(soup)

        return {
            'url': url,
            'platform': 'openrent',
            'title': title,
            'price': price,
            'price_text': price_text,
            'address': address,
            'postcode': postcode,
            'bedrooms': bedrooms,
            'description': description[:500] if description else "",
            'images': images[:5],
            'scraped_at': time.time(),
            'success': True,
            'error': None
        }

    def scrape_propertypal_property(self, url: str) -> Dict[str, any]:
        """Scrape property details from PropertyPal"""
        response = self.safe_request(url, platform='propertypal')
        if not response:
            return self.empty_property_dict(url, "Failed to fetch PropertyPal page")

        soup = BeautifulSoup(response.text, 'html.parser')

        # PropertyPal's structure
        title = self.extract_text_safe(soup, 'h1.property-title, h1[class*="title"], .listing-title')
        price_text = self.extract_text_safe(soup, '.price, [class*="price"], .property-price')
        address = self.extract_text_safe(soup, '.address, [class*="address"], .property-address')
        description = self.extract_text_safe(soup, '.description, [class*="description"], .property-description')

        # Extract structured data
        price = self.extract_price(price_text)
        bedrooms = self.extract_bedrooms(title + " " + description)
        postcode = self.extract_postcode_from_address(address)

        # Extract images
        images = self.extract_images_generic(soup)

        return {
            'url': url,
            'platform': 'propertypal',
            'title': title,
            'price': price,
            'price_text': price_text,
            'address': address,
            'postcode': postcode,
            'bedrooms': bedrooms,
            'description': description[:500] if description else "",
            'images': images[:5],
            'scraped_at': time.time(),
            'success': True,
            'error': None
        }

    # HELPER METHODS (from original implementation)

    def extract_postcode_from_address(self, address: str) -> Optional[str]:
        """Extract UK postcode from address string"""
        # UK postcode pattern
        postcode_pattern = r'\b[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}\b'
        match = re.search(postcode_pattern, address.upper())
        return match.group(0) if match else None

    def extract_images_zoopla(self, soup) -> List[str]:
        """Extract image URLs from Zoopla property page"""
        images = []
        # Zoopla image selectors
        img_selectors = [
            'img[data-testid*="image"]',
            '.property-image img',
            '[class*="gallery"] img',
            '[class*="carousel"] img'
        ]

        for selector in img_selectors:
            elements = soup.select(selector)
            for img in elements:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and 'http' in src and len(images) < 10:
                    images.append(src)

        return list(set(images))  # Remove duplicates

    def extract_images_generic(self, soup) -> List[str]:
        """Extract image URLs from generic property page"""
        images = []
        # Generic image selectors
        img_selectors = [
            '.property-image img', '.listing-image img', '.gallery img',
            '[class*="image"] img', '[class*="photo"] img', '[class*="picture"] img',
            'img[alt*="property"]', 'img[alt*="bedroom"]', 'img[alt*="kitchen"]'
        ]

        for selector in img_selectors:
            elements = soup.select(selector)
            for img in elements:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and 'http' in src and len(images) < 10:
                    images.append(src)

        return list(set(images))  # Remove duplicates

    def empty_property_dict(self, url: str, error_msg: str) -> Dict[str, any]:
        """Return empty property dictionary with error information"""
        return {
            'url': url,
            'platform': 'unknown',
            'title': '',
            'price': None,
            'price_text': '',
            'address': '',
            'postcode': None,
            'bedrooms': None,
            'description': '',
            'images': [],
            'scraped_at': time.time(),
            'success': False,
            'error': error_msg
        }

    def detect_property_site(self, url: str) -> str:
        """Detect which property site a URL belongs to"""
        url_lower = url.lower()
        if 'zoopla.co.uk' in url_lower:
            return 'zoopla'
        elif 'primelocation.com' in url_lower:
            return 'primelocation'
        elif 'nestoria.co.uk' in url_lower:
            return 'nestoria'
        elif 'gumtree.com' in url_lower:
            return 'gumtree'
        elif 'openrent.com' in url_lower:
            return 'openrent'
        elif 'propertypal.com' in url_lower:
            return 'propertypal'
        else:
            return 'unknown'

    def scrape_single_property(self, url: str) -> Dict[str, any]:
        """Scrape a single property from any supported platform"""
        platform = self.detect_property_site(url)

        try:
            if platform == 'zoopla':
                return self.scrape_zoopla_property(url)
            elif platform == 'primelocation':
                return self.scrape_primelocation_property(url)
            elif platform == 'nestoria':
                return self.scrape_nestoria_property(url)
            elif platform == 'gumtree':
                return self.scrape_gumtree_property(url)
            elif platform == 'openrent':
                return self.scrape_openrent_property(url)
            elif platform == 'propertypal':
                return self.scrape_propertypal_property(url)
            else:
                return self.empty_property_dict(url, f"Unsupported platform: {platform}")

        except Exception as e:
            return self.empty_property_dict(url, f"Scraping error: {str(e)}")

    def scrape_multiple_properties(self, urls: List[str], max_workers: int = 3) -> List[Dict[str, any]]:
        """Scrape multiple properties concurrently"""
        results = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all scraping tasks
            future_to_url = {
                executor.submit(self.scrape_single_property, url): url 
                for url in urls
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f'URL {url} generated an exception: {exc}')
                    results.append(self.empty_property_dict(url, f"Concurrent scraping error: {str(exc)}"))

        return results

    def get_platform_benefits(self) -> Dict[str, Dict[str, str]]:
        """Return comparison table of platform benefits"""
        return {
            'zoopla': {
                'name': 'Zoopla',
                'coverage': 'UK-wide, extensive database',
                'benefits': 'Established, reliable, comprehensive data',
                'unique_features': 'Property price history, area statistics',
                'scraping_difficulty': 'Medium - established selectors'
            },
            'primelocation': {
                'name': 'PrimeLocation',
                'coverage': 'UK-wide, premium properties',
                'benefits': 'Professional listings, less bot protection',
                'unique_features': 'High-end properties, same owner as Zoopla',
                'scraping_difficulty': 'Low - more lenient than Zoopla'
            },
            'nestoria': {
                'name': 'Nestoria',
                'coverage': 'Property aggregator, multiple sources',
                'benefits': 'API-friendly, simple search, aggregated data',
                'unique_features': 'Combines listings from multiple sites',
                'scraping_difficulty': 'Very Low - designed to be accessed'
            },
            'gumtree': {
                'name': 'Gumtree',
                'coverage': 'UK-wide, private sellers focus',
                'benefits': 'Private listings, unique finds, less competition',
                'unique_features': 'Direct seller contact, no agent fees',
                'scraping_difficulty': 'Medium - general classifieds site'
            },
            'openrent': {
                'name': 'OpenRent',
                'coverage': 'Growing UK coverage, London-focused',
                'benefits': 'No agent fees, direct landlord contact',
                'unique_features': 'Transparent pricing, landlord-friendly',
                'scraping_difficulty': 'Low - modern, simple structure'
            },
            'propertypal': {
                'name': 'PropertyPal',
                'coverage': 'Northern Ireland + UK regions',
                'benefits': 'Simple URLs, regional focus, good coverage',
                'unique_features': 'Strong in Northern Ireland, simple structure',
                'scraping_difficulty': 'Very Low - straightforward design'
            }
        }


# MAIN USAGE EXAMPLE
def example_usage():
    """Example usage of the PropertyScraperAlternative class"""
    scraper = PropertyScraperAlternative()

    # Generate search URLs for a postcode
    print("=== GENERATING SEARCH URLS ===")
    urls = scraper.generate_search_urls(
        postcode="SE9 1AB",
        min_price=300000,
        max_price=500000,
        min_bedrooms=2
    )

    for platform, url in urls.items():
        print(f"{platform.upper():15} | {url}")

    print("\n=== PLATFORM BENEFITS ===")
    benefits = scraper.get_platform_benefits()
    for platform, details in benefits.items():
        print(f"\n{details['name']} ({platform})")
        print(f"  Coverage: {details['coverage']}")
        print(f"  Benefits: {details['benefits']}")
        print(f"  Unique: {details['unique_features']}")
        print(f"  Scraping: {details['scraping_difficulty']}")


if __name__ == "__main__":
    example_usage()
