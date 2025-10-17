"""
Validators for London Property Search Analyzer
Contains data validation classes and functions
"""

import re
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Union, Any
import pandas as pd


class DataValidator:
    """
    Validates property data for consistency and accuracy
    """

    def __init__(self):
        # London postcodes pattern (simplified)
        self.london_postcode_pattern = r'^(E|EC|N|NW|SE|SW|W|WC)[\d]+\s?[\d]?[A-Z]{2}$'

        # Valid London boroughs
        self.valid_boroughs = {
            'Westminster', 'Kensington and Chelsea', 'Camden', 'Islington',
            'Tower Hamlets', 'Hackney', 'Southwark', 'Lambeth',
            'Wandsworth', 'Hammersmith and Fulham', 'Greenwich',
            'Lewisham', 'Newham', 'Waltham Forest', 'Haringey',
            'Enfield', 'Barnet', 'Harrow', 'Hillingdon', 'Ealing',
            'Hounslow', 'Richmond upon Thames', 'Kingston upon Thames',
            'Merton', 'Sutton', 'Croydon', 'Bromley', 'Bexley',
            'Havering', 'Redbridge', 'Barking and Dagenham'
        }

        # Valid property types
        self.valid_property_types = {
            'Flat', 'House', 'Studio', 'Penthouse', 'Maisonette',
            'Apartment', 'Terraced House', 'Semi-Detached House',
            'Detached House', 'Bungalow', 'Cottage'
        }

        # Valid energy ratings
        self.valid_energy_ratings = {'A', 'B', 'C', 'D', 'E', 'F', 'G'}

        # Valid council tax bands
        self.valid_council_tax_bands = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'}

    def validate_property(self, property_data: Dict) -> Dict:
        """
        Validate a single property record

        Args:
            property_data: Dictionary containing property information

        Returns:
            Validation result dictionary
        """

        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'cleaned_data': property_data.copy()
        }

        # Validate required fields
        required_fields = ['address', 'property_type', 'price']
        for field in required_fields:
            if field not in property_data or not property_data[field]:
                result['errors'].append(f"Missing required field: {field}")
                result['valid'] = False

        if not result['valid']:
            return result

        # Validate individual fields
        self._validate_address(property_data, result)
        self._validate_property_type(property_data, result)
        self._validate_price(property_data, result)
        self._validate_bedrooms(property_data, result)
        self._validate_bathrooms(property_data, result)
        self._validate_size(property_data, result)
        self._validate_borough(property_data, result)
        self._validate_dates(property_data, result)
        self._validate_energy_rating(property_data, result)
        self._validate_council_tax_band(property_data, result)
        self._validate_contact_info(property_data, result)

        return result

    def _validate_address(self, data: Dict, result: Dict):
        """Validate address field"""
        address = data.get('address', '')

        if not isinstance(address, str):
            result['errors'].append("Address must be a string")
            return

        address = address.strip()
        if len(address) < 10:
            result['warnings'].append("Address seems too short")

        if len(address) > 200:
            result['warnings'].append("Address seems too long")

        # Check for postcode
        postcode_match = re.search(r'([A-Z]{1,2}[0-9R][0-9A-Z]?\s?[0-9][A-Z]{2})$', address.upper())
        if postcode_match:
            postcode = postcode_match.group(1)
            if not re.match(self.london_postcode_pattern, postcode):
                result['warnings'].append("Postcode doesn't appear to be a London postcode")
        else:
            result['warnings'].append("No valid postcode found in address")

        result['cleaned_data']['address'] = address

    def _validate_property_type(self, data: Dict, result: Dict):
        """Validate property type"""
        property_type = data.get('property_type', '')

        if not isinstance(property_type, str):
            result['errors'].append("Property type must be a string")
            return

        property_type = property_type.strip().title()

        # Check against valid types
        if property_type not in self.valid_property_types:
            # Try to map common variations
            type_mapping = {
                'Apt': 'Apartment',
                'Apartment': 'Flat',
                'Condo': 'Flat',
                'Terraced': 'Terraced House',
                'Semi': 'Semi-Detached House',
                'Detached': 'Detached House'
            }

            mapped_type = type_mapping.get(property_type, property_type)
            if mapped_type in self.valid_property_types:
                property_type = mapped_type
                result['warnings'].append(f"Property type mapped from '{data['property_type']}' to '{property_type}'")
            else:
                result['warnings'].append(f"Unusual property type: '{property_type}'")

        result['cleaned_data']['property_type'] = property_type

    def _validate_price(self, data: Dict, result: Dict):
        """Validate price"""
        price = data.get('price')

        if price is None:
            result['errors'].append("Price is required")
            return

        # Convert to numeric if string
        if isinstance(price, str):
            # Remove currency symbols and commas
            price_str = re.sub(r'[£,$]', '', price.strip())
            try:
                price = float(price_str)
            except ValueError:
                result['errors'].append(f"Invalid price format: '{data['price']}'")
                return

        if not isinstance(price, (int, float)):
            result['errors'].append("Price must be numeric")
            return

        # Validate price range
        if price <= 0:
            result['errors'].append("Price must be greater than 0")
        elif price < 50000:
            result['warnings'].append("Price seems very low for London property")
        elif price > 50000000:
            result['warnings'].append("Price seems very high")

        result['cleaned_data']['price'] = int(price)

    def _validate_bedrooms(self, data: Dict, result: Dict):
        """Validate bedrooms"""
        bedrooms = data.get('bedrooms')

        if bedrooms is None:
            return  # Optional field

        if isinstance(bedrooms, str):
            try:
                bedrooms = int(bedrooms)
            except ValueError:
                result['warnings'].append(f"Invalid bedrooms format: '{data['bedrooms']}'")
                return

        if not isinstance(bedrooms, int):
            result['warnings'].append("Bedrooms must be a whole number")
            return

        if bedrooms < 0:
            result['warnings'].append("Bedrooms cannot be negative")
        elif bedrooms > 10:
            result['warnings'].append("Very high number of bedrooms")

        result['cleaned_data']['bedrooms'] = bedrooms

    def _validate_bathrooms(self, data: Dict, result: Dict):
        """Validate bathrooms"""
        bathrooms = data.get('bathrooms')

        if bathrooms is None:
            return  # Optional field

        if isinstance(bathrooms, str):
            try:
                bathrooms = float(bathrooms)
            except ValueError:
                result['warnings'].append(f"Invalid bathrooms format: '{data['bathrooms']}'")
                return

        if not isinstance(bathrooms, (int, float)):
            result['warnings'].append("Bathrooms must be numeric")
            return

        if bathrooms < 0:
            result['warnings'].append("Bathrooms cannot be negative")
        elif bathrooms > 10:
            result['warnings'].append("Very high number of bathrooms")

        result['cleaned_data']['bathrooms'] = bathrooms

    def _validate_size(self, data: Dict, result: Dict):
        """Validate square feet"""
        square_feet = data.get('square_feet')

        if square_feet is None:
            return  # Optional field

        if isinstance(square_feet, str):
            try:
                square_feet = float(square_feet)
            except ValueError:
                result['warnings'].append(f"Invalid size format: '{data['square_feet']}'")
                return

        if not isinstance(square_feet, (int, float)):
            result['warnings'].append("Size must be numeric")
            return

        if square_feet <= 0:
            result['warnings'].append("Size must be greater than 0")
        elif square_feet < 100:
            result['warnings'].append("Property size seems very small")
        elif square_feet > 10000:
            result['warnings'].append("Property size seems very large")

        # Calculate price per sq ft if price is available
        price = result['cleaned_data'].get('price')
        if price and square_feet > 0:
            price_per_sqft = price / square_feet
            result['cleaned_data']['price_per_sqft'] = round(price_per_sqft, 2)

        result['cleaned_data']['square_feet'] = int(square_feet)

    def _validate_borough(self, data: Dict, result: Dict):
        """Validate borough"""
        borough = data.get('borough')

        if not borough:
            return  # Optional field

        if not isinstance(borough, str):
            result['warnings'].append("Borough must be a string")
            return

        borough = borough.strip().title()

        # Check against valid boroughs
        if borough not in self.valid_boroughs:
            # Try to find close matches
            close_matches = [b for b in self.valid_boroughs if borough.lower() in b.lower()]
            if close_matches:
                suggested = close_matches[0]
                result['warnings'].append(f"Borough '{borough}' not recognized. Did you mean '{suggested}'?")
            else:
                result['warnings'].append(f"Borough '{borough}' not recognized as a London borough")

        result['cleaned_data']['borough'] = borough

    def _validate_dates(self, data: Dict, result: Dict):
        """Validate date fields"""
        date_fields = ['listing_date', 'available_date', 'last_updated']

        for field in date_fields:
            date_value = data.get(field)
            if not date_value:
                continue

            if isinstance(date_value, str):
                # Try to parse various date formats
                date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
                parsed_date = None

                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_value, fmt).date()
                        break
                    except ValueError:
                        continue

                if parsed_date:
                    result['cleaned_data'][field] = parsed_date.isoformat()

                    # Validate date reasonableness
                    today = date.today()
                    if parsed_date > today:
                        if field == 'listing_date':
                            result['warnings'].append(f"{field} is in the future")
                    elif (today - parsed_date).days > 365 * 5:  # 5 years
                        result['warnings'].append(f"{field} is very old")
                else:
                    result['warnings'].append(f"Invalid date format for {field}: '{date_value}'")

            elif isinstance(date_value, (date, datetime)):
                result['cleaned_data'][field] = date_value.isoformat()

    def _validate_energy_rating(self, data: Dict, result: Dict):
        """Validate energy rating"""
        energy_rating = data.get('energy_rating')

        if not energy_rating:
            return  # Optional field

        if isinstance(energy_rating, str):
            energy_rating = energy_rating.upper().strip()

            if energy_rating not in self.valid_energy_ratings:
                result['warnings'].append(f"Invalid energy rating: '{energy_rating}'")
            else:
                result['cleaned_data']['energy_rating'] = energy_rating

    def _validate_council_tax_band(self, data: Dict, result: Dict):
        """Validate council tax band"""
        council_tax_band = data.get('council_tax_band')

        if not council_tax_band:
            return  # Optional field

        if isinstance(council_tax_band, str):
            council_tax_band = council_tax_band.upper().strip()

            if council_tax_band not in self.valid_council_tax_bands:
                result['warnings'].append(f"Invalid council tax band: '{council_tax_band}'")
            else:
                result['cleaned_data']['council_tax_band'] = council_tax_band

    def _validate_contact_info(self, data: Dict, result: Dict):
        """Validate contact information"""
        # Validate phone numbers
        phone_fields = ['agent_phone', 'contact_phone', 'phone']
        phone_pattern = r'^(\+44\s?|0)(\d{2,4}\s?\d{3,4}\s?\d{4})$'

        for field in phone_fields:
            phone = data.get(field)
            if phone and isinstance(phone, str):
                phone = re.sub(r'[\s\-\(\)]', '', phone)  # Remove formatting
                if not re.match(r'^(\+44|0)\d{10}$', phone):
                    result['warnings'].append(f"Invalid UK phone number format: {field}")

        # Validate email addresses
        email_fields = ['agent_email', 'contact_email', 'email']
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        for field in email_fields:
            email = data.get(field)
            if email and isinstance(email, str):
                if not re.match(email_pattern, email):
                    result['warnings'].append(f"Invalid email format: {field}")

    def validate_bulk_properties(self, properties: List[Dict]) -> Dict:
        """
        Validate a list of properties

        Args:
            properties: List of property dictionaries

        Returns:
            Bulk validation result
        """

        bulk_result = {
            'total_properties': len(properties),
            'valid_properties': 0,
            'invalid_properties': 0,
            'properties_with_warnings': 0,
            'all_errors': [],
            'all_warnings': [],
            'cleaned_properties': [],
            'validation_summary': {}
        }

        error_counts = {}
        warning_counts = {}

        for i, property_data in enumerate(properties):
            validation_result = self.validate_property(property_data)

            if validation_result['valid']:
                bulk_result['valid_properties'] += 1
                bulk_result['cleaned_properties'].append(validation_result['cleaned_data'])
            else:
                bulk_result['invalid_properties'] += 1

            if validation_result['warnings']:
                bulk_result['properties_with_warnings'] += 1

            # Collect errors and warnings
            for error in validation_result['errors']:
                error_with_index = f"Property {i+1}: {error}"
                bulk_result['all_errors'].append(error_with_index)
                error_counts[error] = error_counts.get(error, 0) + 1

            for warning in validation_result['warnings']:
                warning_with_index = f"Property {i+1}: {warning}"
                bulk_result['all_warnings'].append(warning_with_index)
                warning_counts[warning] = warning_counts.get(warning, 0) + 1

        # Create summary of most common issues
        bulk_result['validation_summary'] = {
            'most_common_errors': sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'most_common_warnings': sorted(warning_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'success_rate': (bulk_result['valid_properties'] / bulk_result['total_properties']) * 100
        }

        return bulk_result


class SearchValidator:
    """
    Validates search parameters and filters
    """

    def __init__(self):
        self.valid_property_types = [
            'All', 'Flat', 'House', 'Studio', 'Penthouse', 'Maisonette'
        ]

        self.valid_boroughs = [
            'All', 'Westminster', 'Kensington and Chelsea', 'Camden', 
            'Islington', 'Tower Hamlets', 'Hackney', 'Southwark', 
            'Lambeth', 'Wandsworth', 'Hammersmith and Fulham'
        ]

    def validate_search_params(self, search_params: Dict) -> Dict:
        """
        Validate search parameters

        Args:
            search_params: Dictionary of search parameters

        Returns:
            Validation result dictionary
        """

        result = {
            'valid': True,
            'message': '',
            'errors': [],
            'warnings': [],
            'cleaned_params': search_params.copy()
        }

        # Validate property type
        if 'property_type' in search_params:
            if search_params['property_type'] not in self.valid_property_types:
                result['errors'].append(f"Invalid property type: {search_params['property_type']}")

        # Validate price range
        self._validate_price_range(search_params, result)

        # Validate bedroom range
        self._validate_bedroom_range(search_params, result)

        # Validate borough
        if 'borough' in search_params:
            if search_params['borough'] not in self.valid_boroughs:
                result['warnings'].append(f"Unusual borough: {search_params['borough']}")

        # Validate boolean filters
        boolean_fields = ['new_build', 'garden', 'parking']
        for field in boolean_fields:
            if field in search_params and not isinstance(search_params[field], bool):
                result['errors'].append(f"{field} must be a boolean value")

        # Set overall validity
        if result['errors']:
            result['valid'] = False
            result['message'] = f"Validation failed: {'; '.join(result['errors'])}"
        elif result['warnings']:
            result['message'] = f"Validation passed with warnings: {'; '.join(result['warnings'])}"
        else:
            result['message'] = "All parameters are valid"

        return result

    def _validate_price_range(self, search_params: Dict, result: Dict):
        """Validate price range parameters"""
        min_price = search_params.get('min_price')
        max_price = search_params.get('max_price')

        if min_price is not None:
            if not isinstance(min_price, (int, float)) or min_price < 0:
                result['errors'].append("min_price must be a positive number")
            elif min_price > 10000000:
                result['warnings'].append("min_price is very high")

        if max_price is not None:
            if not isinstance(max_price, (int, float)) or max_price < 0:
                result['errors'].append("max_price must be a positive number")
            elif max_price > 50000000:
                result['warnings'].append("max_price is very high")

        if (min_price is not None and max_price is not None and 
            isinstance(min_price, (int, float)) and isinstance(max_price, (int, float))):
            if min_price >= max_price:
                result['errors'].append("min_price must be less than max_price")
            elif (max_price - min_price) < 50000:
                result['warnings'].append("Price range is very narrow")

    def _validate_bedroom_range(self, search_params: Dict, result: Dict):
        """Validate bedroom range parameters"""
        min_bedrooms = search_params.get('min_bedrooms')
        max_bedrooms = search_params.get('max_bedrooms')

        if min_bedrooms is not None:
            if not isinstance(min_bedrooms, int) or min_bedrooms < 0:
                result['errors'].append("min_bedrooms must be a non-negative integer")
            elif min_bedrooms > 10:
                result['warnings'].append("min_bedrooms is very high")

        if max_bedrooms is not None:
            if not isinstance(max_bedrooms, int) or max_bedrooms < 0:
                result['errors'].append("max_bedrooms must be a non-negative integer")
            elif max_bedrooms > 15:
                result['warnings'].append("max_bedrooms is very high")

        if (min_bedrooms is not None and max_bedrooms is not None and
            isinstance(min_bedrooms, int) and isinstance(max_bedrooms, int)):
            if min_bedrooms > max_bedrooms:
                result['errors'].append("min_bedrooms must be less than or equal to max_bedrooms")

    def validate_filters(self, filters: Dict) -> Dict:
        """
        Validate additional search filters

        Args:
            filters: Dictionary of additional filters

        Returns:
            Validation result dictionary
        """

        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }

        # Validate date filters
        if 'listed_after' in filters:
            if not self._is_valid_date(filters['listed_after']):
                result['errors'].append("listed_after must be a valid date")

        if 'listed_before' in filters:
            if not self._is_valid_date(filters['listed_before']):
                result['errors'].append("listed_before must be a valid date")

        # Validate numeric filters
        numeric_filters = ['min_size', 'max_size', 'max_days_on_market']
        for filter_name in numeric_filters:
            if filter_name in filters:
                if not isinstance(filters[filter_name], (int, float)) or filters[filter_name] < 0:
                    result['errors'].append(f"{filter_name} must be a positive number")

        # Validate list filters
        if 'excluded_agents' in filters:
            if not isinstance(filters['excluded_agents'], list):
                result['errors'].append("excluded_agents must be a list")

        if result['errors']:
            result['valid'] = False

        return result

    def _is_valid_date(self, date_value: Any) -> bool:
        """Check if a value is a valid date"""
        if isinstance(date_value, (date, datetime)):
            return True

        if isinstance(date_value, str):
            date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
            for fmt in date_formats:
                try:
                    datetime.strptime(date_value, fmt)
                    return True
                except ValueError:
                    continue

        return False


# Utility functions for testing
def test_validators():
    """Test function for validators"""

    # Test data validator
    data_validator = DataValidator()

    test_property = {
        'address': '123 Baker Street, London, NW1 6XE',
        'property_type': 'Flat',
        'price': 750000,
        'bedrooms': 2,
        'bathrooms': 1,
        'square_feet': 850,
        'borough': 'Westminster'
    }

    validation_result = data_validator.validate_property(test_property)
    print("Data validation result:", validation_result)

    # Test search validator
    search_validator = SearchValidator()

    test_search = {
        'property_type': 'Flat',
        'min_price': 400000,
        'max_price': 800000,
        'min_bedrooms': 1,
        'max_bedrooms': 3,
        'borough': 'Camden'
    }

    search_result = search_validator.validate_search_params(test_search)
    print("Search validation result:", search_result)

    return validation_result, search_result
