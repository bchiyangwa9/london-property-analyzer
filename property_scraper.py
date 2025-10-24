"""
Property Scraper Module for London Property Analyzer - ENHANCED VERSION
=====================================================================

ENHANCEMENTS in this version:
- Comprehensive London postcode mapping (198 postcodes total)
- All major London areas: SE1-SE28, N1-N22, E1-E20, NW1-NW11, SW1-SW20, 
  W1-W14, BR1-BR8, DA1-DA18, EN1-EN11, HA0-HA9, IG1-IG11, RM1-RM20, EC1-EC4, WC1-WC2
- Enhanced Rightmove fallback logic with area name search
- Improved OnTheMarket area mapping with multiple fallback options
- Special handling for problem areas like Enfield (EN2, N9, N13, N14, N18, N21)
- Better URL formatting for multi-word area names

Version: 2.0 Enhanced
Date: 2025-10-23
Changes:
- Fixed Enfield postcode recognition (EN2, N9, etc.)
- Added 183 new postcode mappings
- Implemented fallback URL generation for better reliability
- Enhanced OnTheMarket area name formatting

Original functionality maintained for:
- Rightmove, Zoopla, OnTheMarket scraping
- Property data extraction
- Error handling and rate limiting
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
        """Generate search URLs for different property sites with comprehensive London postcode mapping"""

        # Clean postcode for URL usage
        postcode_clean = postcode.replace(' ', '+')

        # Comprehensive London postcode to area mapping
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
            'W1': 'oxford-street', 'W2': 'bayswater', 'W3': 'acton', 'W4': 'chiswick',
            'W5': 'ealing', 'W6': 'hammersmith', 'W7': 'hanwell', 'W8': 'kensington',
            'W9': 'maida-vale', 'W10': 'ladbroke-grove', 'W11': 'notting-hill', 'W12': 'shepherds-bush',
            'W13': 'west-ealing', 'W14': 'west-kensington',

            # BR postcodes (Bromley area: BR1-BR8)
            'BR1': 'bromley', 'BR2': 'hayes', 'BR3': 'beckenham', 'BR4': 'west-wickham',
            'BR5': 'orpington', 'BR6': 'orpington', 'BR7': 'chislehurst', 'BR8': 'swanley',

            # DA postcodes (Dartford/Bexley: DA1-DA18)
            'DA1': 'dartford', 'DA2': 'dartford', 'DA3': 'longfield', 'DA4': 'farningham',
            'DA5': 'bexley', 'DA6': 'bexleyheath', 'DA7': 'bexleyheath', 'DA8': 'erith',
            'DA9': 'greenhithe', 'DA10': 'swanscombe', 'DA11': 'northfleet', 'DA12': 'gravesend',
            'DA13': 'gravesend', 'DA14': 'sidcup', 'DA15': 'sidcup', 'DA16': 'welling',
            'DA17': 'belvedere', 'DA18': 'erith',

            # EN postcodes (Enfield: EN1-EN11)
            'EN1': 'enfield', 'EN2': 'enfield', 'EN3': 'enfield', 'EN4': 'cockfosters',
            'EN5': 'barnet', 'EN6': 'potters-bar', 'EN7': 'cheshunt', 'EN8': 'waltham-cross',
            'EN9': 'waltham-abbey', 'EN10': 'broxbourne', 'EN11': 'hoddesdon',

            # HA postcodes (Harrow: HA0-HA9)
            'HA0': 'wembley', 'HA1': 'harrow', 'HA2': 'harrow', 'HA3': 'harrow-weald',
            'HA4': 'ruislip', 'HA5': 'pinner', 'HA6': 'northwood', 'HA7': 'stanmore',
            'HA8': 'edgware', 'HA9': 'wembley',

            # IG postcodes (Ilford: IG1-IG11)
            'IG1': 'ilford', 'IG2': 'gants-hill', 'IG3': 'seven-kings', 'IG4': 'redbridge',
            'IG5': 'clayhall', 'IG6': 'barkingside', 'IG7': 'chigwell', 'IG8': 'woodford-green',
            'IG9': 'buckhurst-hill', 'IG10': 'loughton', 'IG11': 'barking',

            # RM postcodes (Romford: RM1-RM20)
            'RM1': 'romford', 'RM2': 'gidea-park', 'RM3': 'harold-wood', 'RM4': 'harold-hill',
            'RM5': 'collier-row', 'RM6': 'chadwell-heath', 'RM7': 'rush-green', 'RM8': 'dagenham',
            'RM9': 'dagenham', 'RM10': 'dagenham', 'RM11': 'hornchurch', 'RM12': 'hornchurch',
            'RM13': 'rainham', 'RM14': 'upminster', 'RM15': 'south-ockendon', 'RM16': 'purfleet',
            'RM17': 'grays', 'RM18': 'tilbury', 'RM19': 'purfleet', 'RM20': 'chafford-hundred',

            # Central postcodes (EC1-EC4, WC1-WC2)
            'EC1': 'clerkenwell', 'EC2': 'bank', 'EC3': 'tower-hill', 'EC4': 'fleet-street',
            'WC1': 'bloomsbury', 'WC2': 'covent-garden'
        }

        # Area name to postcode mapping for fallback searches
        area_to_postcode = {
            'enfield': ['EN1', 'EN2', 'EN3', 'N9', 'N13', 'N14', 'N18', 'N21'],
            'sidcup': ['SE9', 'DA14', 'DA15'],
            'orpington': ['BR5', 'BR6'],
            'bromley': ['BR1', 'BR2', 'BR3', 'BR7']
        }

        # Extract the basic postcode area (e.g., SE9 from SE9 0AA)
        basic_postcode = postcode.split()[0] if ' ' in postcode else postcode[:3]
        if len(basic_postcode) > 4:  # Handle cases like SE90AA
            basic_postcode = re.match(r'^([A-Z]{1,2}\d+)', basic_postcode.upper()).group(1) if re.match(r'^[A-Z]{1,2}\d+', basic_postcode.upper()) else basic_postcode[:3]

        basic_postcode = basic_postcode.upper()
        area_name = postcode_to_area.get(basic_postcode, basic_postcode.lower())

        urls = {}

        # Rightmove search URL with fallback logic
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

        rightmove_params.append(f"radius={radius}")

        # Primary approach: Use OUTCODE format
        outcode = basic_postcode.upper()
        rightmove_url = f"https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=OUTCODE%5E{outcode}&{'&'.join(rightmove_params)}"

        # Fallback approach: Use area name search if available
        if basic_postcode in postcode_to_area:
            area_search_params = rightmove_params.copy()
            # Remove radius for area name search as it's location-specific
            area_search_params = [p for p in area_search_params if not p.startswith('radius=')]
            rightmove_fallback_url = f"https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&searchLocation={area_name}&{'&'.join(area_search_params)}"
            urls['Rightmove_Fallback'] = rightmove_fallback_url

        urls['Rightmove'] = rightmove_url

        # Zoopla search URL (keeping existing functionality)
        zoopla_params = []
        if min_price:
            zoopla_params.append(f"price_min={min_price}")
        if max_price:
            zoopla_params.append(f"price_max={max_price}")
        if min_bedrooms:
            zoopla_params.append(f"beds_min={min_bedrooms}")
        if property_type and property_type != "Any":
            zoopla_params.append(f"property_type={property_type.lower()}")

        zoopla_url = f"https://www.zoopla.co.uk/for-sale/property/{postcode_clean}/?{'&'.join(zoopla_params)}&radius={radius}"
        urls['Zoopla'] = zoopla_url

        # OnTheMarket search URL with comprehensive area mapping and fallbacks
        otm_params = []
        if min_price:
            otm_params.append(f"min-price={min_price}")
        if max_price:
            otm_params.append(f"max-price={max_price}")
        if min_bedrooms:
            otm_params.append(f"min-bedrooms={min_bedrooms}")
        if property_type and property_type != "Any":
            # OnTheMarket uses different property type parameters
            otm_type_map = {"House": "houses", "Flat": "flats-apartments", "Bungalow": "bungalows"}
            otm_params.append(f"property-type={otm_type_map.get(property_type, 'houses')}")

        # Enhanced OnTheMarket area name handling
        def format_area_for_otm(area_name):
            """Format area name for OnTheMarket URLs"""
            # Handle multi-word area names
            formatted = area_name.lower().replace(' ', '-').replace('_', '-')
            # Handle special cases
            special_cases = {
                'new-malden': 'new-malden',
                'kingston-upon-thames': 'kingston-upon-thames',
                'richmond-upon-thames': 'richmond-upon-thames',
                'stoke-on-trent': 'stoke-on-trent'
            }
            return special_cases.get(formatted, formatted)

        # Use comprehensive area mapping with fallback
        if basic_postcode in postcode_to_area:
            formatted_area = format_area_for_otm(area_name)
            otm_url = f"https://www.onthemarket.com/for-sale/property/{formatted_area}/?{'&'.join(otm_params)}"
        else:
            # Fallback: use lowercase postcode
            fallback_area = basic_postcode.lower()
            otm_url = f"https://www.onthemarket.com/for-sale/property/{fallback_area}/?{'&'.join(otm_params)}"
            # Also add an alternative URL using full postcode
            otm_postcode_url = f"https://www.onthemarket.com/for-sale/property/{postcode_clean.lower()}/?{'&'.join(otm_params)}"
            urls['OnTheMarket_Postcode'] = otm_postcode_url

        urls['OnTheMarket'] = otm_url

        # Additional fallback URLs for problematic areas
        if basic_postcode in ['EN1', 'EN2', 'EN3', 'N9', 'N13', 'N14', 'N18', 'N21']:
            # Special handling for Enfield area
            enfield_url = f"https://www.onthemarket.com/for-sale/property/enfield/?{'&'.join(otm_params)}"
            urls['OnTheMarket_Enfield'] = enfield_url

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
