"""
API Simulator for London Property Search Analyzer
Simulates property API responses with realistic data
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np


class APISimulator:
    """
    Simulates property search APIs with realistic London property data
    """

    def __init__(self):
        # London boroughs with average price data (approximate)
        self.borough_data = {
            'Westminster': {'avg_price': 1200000, 'price_variance': 0.4},
            'Kensington and Chelsea': {'avg_price': 1100000, 'price_variance': 0.5},
            'Camden': {'avg_price': 800000, 'price_variance': 0.3},
            'Islington': {'avg_price': 750000, 'price_variance': 0.3},
            'Tower Hamlets': {'avg_price': 600000, 'price_variance': 0.4},
            'Hackney': {'avg_price': 650000, 'price_variance': 0.35},
            'Southwark': {'avg_price': 700000, 'price_variance': 0.3},
            'Lambeth': {'avg_price': 650000, 'price_variance': 0.3},
            'Wandsworth': {'avg_price': 720000, 'price_variance': 0.25},
            'Hammersmith and Fulham': {'avg_price': 800000, 'price_variance': 0.3}
        }

        # Property types and their characteristics
        self.property_types = {
            'Flat': {'size_range': (400, 1200), 'price_multiplier': 1.0},
            'House': {'size_range': (800, 2500), 'price_multiplier': 1.3},
            'Studio': {'size_range': (200, 500), 'price_multiplier': 0.7},
            'Penthouse': {'size_range': (1000, 3000), 'price_multiplier': 2.0},
            'Maisonette': {'size_range': (600, 1800), 'price_multiplier': 1.1}
        }

        # Street names for address generation
        self.street_names = [
            "Kings Road", "Queens Way", "Baker Street", "Oxford Street", 
            "Regent Street", "Piccadilly", "The Strand", "Whitehall",
            "Victoria Street", "Park Lane", "Marylebone Road", "Euston Road",
            "Commercial Street", "Brick Lane", "Shoreditch High Street",
            "Old Street", "City Road", "Goswell Road", "Rosebery Avenue",
            "Clerkenwell Road", "Theobald Road", "High Holborn",
            "Southampton Row", "Russell Square", "Tavistock Square",
            "Gower Street", "Tottenham Court Road", "Charlotte Street"
        ]

    def search_properties(self, search_params: Dict) -> List[Dict]:
        """
        Simulate property search with given parameters

        Args:
            search_params: Dictionary containing search criteria

        Returns:
            List of property dictionaries
        """
        # Simulate API delay
        time.sleep(random.uniform(0.5, 2.0))

        # Determine number of results based on search criteria
        result_count = self._calculate_result_count(search_params)

        properties = []

        for i in range(result_count):
            property_data = self._generate_property(search_params, i)
            properties.append(property_data)

        return properties

    def _calculate_result_count(self, search_params: Dict) -> int:
        """Calculate realistic number of results based on search parameters"""
        base_count = 50

        # Adjust based on price range
        price_range = search_params['max_price'] - search_params['min_price']
        if price_range < 200000:
            base_count *= 0.6  # Narrow price range = fewer results
        elif price_range > 1000000:
            base_count *= 1.4  # Wide price range = more results

        # Adjust based on bedroom range
        bedroom_range = search_params['max_bedrooms'] - search_params['min_bedrooms']
        if bedroom_range == 0:
            base_count *= 0.7  # Specific bedroom count = fewer results

        # Adjust based on borough
        if search_params['borough'] != 'All':
            base_count *= 0.8  # Specific borough = fewer results

        # Adjust based on additional filters
        if search_params.get('new_build'):
            base_count *= 0.4  # New build filter = much fewer results
        if search_params.get('garden'):
            base_count *= 0.7  # Garden requirement = fewer results
        if search_params.get('parking'):
            base_count *= 0.6  # Parking requirement = fewer results

        # Add some randomness
        final_count = int(base_count * random.uniform(0.7, 1.3))

        return max(5, min(final_count, 100))  # Between 5 and 100 results

    def _generate_property(self, search_params: Dict, index: int) -> Dict:
        """Generate a single property that matches search criteria"""

        # Select property type
        if search_params['property_type'] == 'All':
            property_type = random.choice(list(self.property_types.keys()))
        else:
            property_type = search_params['property_type']

        # Select borough
        if search_params['borough'] == 'All':
            borough = random.choice(list(self.borough_data.keys()))
        else:
            borough = search_params['borough']

        # Generate bedrooms within range
        bedrooms = random.randint(
            search_params['min_bedrooms'], 
            search_params['max_bedrooms']
        )

        # Generate size based on property type and bedrooms
        size_range = self.property_types[property_type]['size_range']
        base_size = random.randint(size_range[0], size_range[1])

        # Adjust size based on bedrooms
        bedroom_multiplier = max(0.7, 0.8 + (bedrooms * 0.15))
        square_feet = int(base_size * bedroom_multiplier)

        # Generate price
        price = self._generate_price(property_type, borough, bedrooms, square_feet, search_params)

        # Generate address
        street_number = random.randint(1, 200)
        street_name = random.choice(self.street_names)
        address = f"{street_number} {street_name}, {borough}"

        # Additional features based on search criteria
        features = []
        if search_params.get('new_build') or random.random() < 0.2:
            features.append('New Build')
        if search_params.get('garden') or random.random() < 0.4:
            features.append('Garden')
        if search_params.get('parking') or random.random() < 0.3:
            features.append('Parking')

        # Random additional features
        additional_features = ['Balcony', 'Terrace', 'Concierge', 'Gym', 'Pool', 'Security']
        for feature in additional_features:
            if random.random() < 0.15:
                features.append(feature)

        # Calculate price per square foot
        price_per_sqft = price / square_feet

        # Generate listing details
        days_on_market = random.randint(1, 120)
        listing_date = datetime.now() - timedelta(days=days_on_market)

        return {
            'id': f"prop_{index:04d}_{random.randint(1000, 9999)}",
            'address': address,
            'property_type': property_type,
            'bedrooms': bedrooms,
            'bathrooms': max(1, bedrooms + random.randint(-1, 1)),
            'price': price,
            'square_feet': square_feet,
            'price_per_sqft': round(price_per_sqft, 2),
            'borough': borough,
            'features': features,
            'days_on_market': days_on_market,
            'listing_date': listing_date.strftime('%Y-%m-%d'),
            'agent': self._generate_agent_info(),
            'description': self._generate_description(property_type, borough, bedrooms, features),
            'energy_rating': random.choice(['A', 'B', 'C', 'D', 'E']),
            'council_tax_band': random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G']),
            'lease_length': random.randint(80, 999) if property_type in ['Flat', 'Studio'] else None
        }

    def _generate_price(self, property_type: str, borough: str, bedrooms: int, 
                       square_feet: int, search_params: Dict) -> int:
        """Generate realistic price based on property characteristics"""

        # Base price from borough average
        borough_info = self.borough_data[borough]
        base_price = borough_info['avg_price']

        # Adjust for property type
        type_multiplier = self.property_types[property_type]['price_multiplier']

        # Adjust for bedrooms
        bedroom_adjustment = 1.0 + ((bedrooms - 2) * 0.2)  # 2-bed as baseline

        # Calculate base price
        calculated_price = base_price * type_multiplier * bedroom_adjustment

        # Add variance
        variance = borough_info['price_variance']
        price_variance = random.uniform(-variance, variance)
        final_price = calculated_price * (1 + price_variance)

        # Ensure price is within search range (with some flexibility)
        min_price = search_params['min_price'] * 0.95
        max_price = search_params['max_price'] * 1.05

        final_price = max(min_price, min(final_price, max_price))

        # Round to nearest £1000
        return int(round(final_price / 1000) * 1000)

    def _generate_agent_info(self) -> Dict:
        """Generate estate agent information"""
        agents = [
            {'name': 'Foxtons', 'phone': '020 7000 1234'},
            {'name': 'Rightmove Premier', 'phone': '020 7000 5678'},
            {'name': 'Savills', 'phone': '020 7000 9012'},
            {'name': 'Knight Frank', 'phone': '020 7000 3456'},
            {'name': 'Chestertons', 'phone': '020 7000 7890'},
            {'name': 'Winkworth', 'phone': '020 7000 2345'},
            {'name': 'Hamptons', 'phone': '020 7000 6789'},
            {'name': 'Marsh & Parsons', 'phone': '020 7000 0123'}
        ]

        return random.choice(agents)

    def _generate_description(self, property_type: str, borough: str, 
                           bedrooms: int, features: List[str]) -> str:
        """Generate property description"""

        descriptions = {
            'Flat': f"Modern {bedrooms}-bedroom flat in the heart of {borough}.",
            'House': f"Charming {bedrooms}-bedroom house in sought-after {borough}.",
            'Studio': f"Contemporary studio apartment in vibrant {borough}.",
            'Penthouse': f"Luxury {bedrooms}-bedroom penthouse with stunning views over {borough}.",
            'Maisonette': f"Spacious {bedrooms}-bedroom maisonette in popular {borough}."
        }

        base_description = descriptions.get(property_type, f"{bedrooms}-bedroom {property_type.lower()} in {borough}.")

        if features:
            feature_text = " Features include " + ", ".join(features[:3]).lower() + "."
            base_description += feature_text

        additions = [
            " Close to transport links.",
            " Walking distance to local amenities.",
            " Recently refurbished throughout.",
            " Available immediately.",
            " Chain free sale."
        ]

        if random.random() < 0.7:
            base_description += random.choice(additions)

        return base_description

    def get_market_statistics(self, borough: str = None) -> Dict:
        """
        Get simulated market statistics

        Args:
            borough: Specific borough or None for all London

        Returns:
            Dictionary with market statistics
        """
        time.sleep(0.5)  # Simulate API delay

        if borough and borough in self.borough_data:
            borough_info = self.borough_data[borough]
            return {
                'borough': borough,
                'average_price': borough_info['avg_price'],
                'median_price': int(borough_info['avg_price'] * 0.85),
                'price_change_1m': round(random.uniform(-2.5, 3.5), 1),
                'price_change_1y': round(random.uniform(-5.0, 8.0), 1),
                'properties_sold_1m': random.randint(50, 150),
                'average_days_on_market': random.randint(25, 80),
                'most_popular_type': random.choice(['Flat', 'House', 'Studio'])
            }
        else:
            # London-wide statistics
            all_prices = [info['avg_price'] for info in self.borough_data.values()]
            return {
                'borough': 'All London',
                'average_price': int(np.mean(all_prices)),
                'median_price': int(np.median(all_prices)),
                'price_change_1m': round(random.uniform(-1.5, 2.5), 1),
                'price_change_1y': round(random.uniform(-3.0, 6.0), 1),
                'properties_sold_1m': random.randint(800, 1500),
                'average_days_on_market': random.randint(30, 70),
                'most_popular_type': 'Flat'
            }

    def get_price_history(self, property_id: str) -> List[Dict]:
        """
        Generate simulated price history for a property

        Args:
            property_id: Property identifier

        Returns:
            List of price history entries
        """
        time.sleep(0.3)  # Simulate API delay

        # Generate 6-12 months of price history
        months = random.randint(6, 12)
        base_price = random.randint(400000, 1200000)

        history = []
        current_date = datetime.now()

        for i in range(months):
            date = current_date - timedelta(days=30 * i)

            # Simulate price changes
            if i == 0:
                price = base_price
            else:
                change = random.uniform(-0.03, 0.04)  # -3% to +4% change
                price = int(history[-1]['price'] * (1 + change))

            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': price,
                'event': random.choice(['Listed', 'Price Change', 'Back on Market']) if i > 0 else 'Listed'
            })

        return list(reversed(history))  # Chronological order


# Utility functions for testing
def test_api_simulator():
    """Test function for API simulator"""
    simulator = APISimulator()

    # Test search
    search_params = {
        'property_type': 'Flat',
        'min_price': 400000,
        'max_price': 800000,
        'min_bedrooms': 1,
        'max_bedrooms': 3,
        'borough': 'Camden',
        'new_build': False,
        'garden': False,
        'parking': False
    }

    results = simulator.search_properties(search_params)
    print(f"Found {len(results)} properties")

    if results:
        print("Sample property:", results[0])

    # Test market statistics
    stats = simulator.get_market_statistics('Camden')
    print("Market statistics:", stats)

    return results, stats
