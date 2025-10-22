"""
London Property Analyzer - Automation Engine
===========================================

Core automation engine for property scoring, validation, and API integration.
Handles all scoring calculations across 7 categories with reference postcode system.

Author: AI Assistant
Version: 2.0 - Dual Mode System
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyScoringEngine:
    """
    Core engine for calculating property scores across all 7 categories.
    Uses reference postcode system for distance/commute calculations.
    """

    def __init__(self, reference_postcode: str = "SE1 9SP"):
        """
        Initialize the scoring engine with reference postcode.

        Args:
            reference_postcode: Home/work postcode for distance calculations
        """
        self.reference_postcode = reference_postcode
        self.scoring_weights = {
            'price': 20,        # Max 20 points
            'commute': 20,      # Max 20 points  
            'property_type': 15, # Max 15 points
            'bedrooms': 15,     # Max 15 points
            'outdoor_space': 10, # Max 10 points
            'schools': 10,      # Max 10 points
            'grammar_bonus': 10  # Max 10 points bonus
        }

    def calculate_total_score(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate total property score across all 7 categories.

        Args:
            property_data: Dictionary containing property information

        Returns:
            Dictionary with individual scores and total score
        """
        try:
            scores = {}

            # Calculate each category score
            scores['price_score'] = self._calculate_price_score(property_data.get('price', 0))
            scores['commute_score'] = self._calculate_commute_score(property_data.get('commute_time', 60))
            scores['property_type_score'] = self._calculate_property_type_score(property_data.get('property_type', 'Flat'))
            scores['bedrooms_score'] = self._calculate_bedrooms_score(property_data.get('bedrooms', 2))
            scores['outdoor_space_score'] = self._calculate_outdoor_space_score(property_data.get('outdoor_space', 'None'))
            scores['schools_score'] = self._calculate_schools_score(property_data.get('nearest_school_ofsted', 'Requires Improvement'))
            scores['grammar_bonus_score'] = self._calculate_grammar_bonus_score(property_data.get('grammar_school_proximity', 'No'))

            # Calculate total score
            scores['total_score'] = sum(scores.values())

            # Add breakdown for display
            scores['breakdown'] = {
                'Price': f"{scores['price_score']}/{self.scoring_weights['price']}",
                'Commute': f"{scores['commute_score']}/{self.scoring_weights['commute']}",
                'Property Type': f"{scores['property_type_score']}/{self.scoring_weights['property_type']}",
                'Bedrooms': f"{scores['bedrooms_score']}/{self.scoring_weights['bedrooms']}",
                'Outdoor Space': f"{scores['outdoor_space_score']}/{self.scoring_weights['outdoor_space']}",
                'Schools': f"{scores['schools_score']}/{self.scoring_weights['schools']}",
                'Grammar Bonus': f"{scores['grammar_bonus_score']}/{self.scoring_weights['grammar_bonus']}"
            }

            logger.info(f"Calculated total score: {scores['total_score']}/100")
            return scores

        except Exception as e:
            logger.error(f"Error calculating property score: {str(e)}")
            return self._get_default_scores()

    def _calculate_price_score(self, price: float) -> float:
        """
        Calculate price score based on budget range £300k-£420k.
        Lower prices get higher scores within budget.
        """
        try:
            price = float(price)

            if price <= 0:
                return 0

            # Budget range: £300k-£420k optimal
            if 300000 <= price <= 350000:
                return 20  # Perfect score for £300k-£350k
            elif 350000 < price <= 380000:
                return 15  # Good score for £350k-£380k
            elif 380000 < price <= 420000:
                return 10  # Acceptable for £380k-£420k
            elif price < 300000:
                return 18  # Slightly lower for below budget (might have issues)
            elif 420000 < price <= 450000:
                return 5   # Over budget but might consider
            else:
                return 0   # Too expensive

        except (ValueError, TypeError):
            return 0

    def _calculate_commute_score(self, commute_time: float) -> float:
        """
        Calculate commute score. Max 60 minutes acceptable.
        """
        try:
            commute_time = float(commute_time)

            if commute_time <= 0:
                return 0

            if commute_time <= 30:
                return 20  # Excellent commute
            elif commute_time <= 40:
                return 15  # Good commute
            elif commute_time <= 50:
                return 10  # Acceptable commute
            elif commute_time <= 60:
                return 5   # Maximum acceptable
            else:
                return 0   # Too long

        except (ValueError, TypeError):
            return 0

    def _calculate_property_type_score(self, property_type: str) -> float:
        """
        Calculate property type score based on preferences.
        """
        try:
            property_type = str(property_type).lower()

            type_scores = {
                'detached': 15,     # Best - most space and privacy
                'semi-detached': 12, # Good - balance of space and price
                'terraced': 10,     # Good - character but less privacy
                'end of terrace': 11, # Slightly better than mid-terrace
                'townhouse': 12,    # Good - usually more space
                'maisonette': 8,    # Acceptable - can be good value
                'flat': 5,          # Lower preference - less space
                'apartment': 5,     # Similar to flat
                'studio': 2,        # Not suitable for family
                'bungalow': 13      # Good for accessibility
            }

            # Try to match property type
            for type_key, score in type_scores.items():
                if type_key in property_type:
                    return score

            return 7  # Default for unknown types

        except Exception:
            return 7

    def _calculate_bedrooms_score(self, bedrooms: int) -> float:
        """
        Calculate bedrooms score. Need 3+ bedrooms.
        """
        try:
            bedrooms = int(bedrooms)

            if bedrooms >= 4:
                return 15  # Perfect - 4+ bedrooms
            elif bedrooms == 3:
                return 12  # Good - meets minimum requirement
            elif bedrooms == 2:
                return 5   # Below requirement but might consider
            elif bedrooms == 1:
                return 2   # Really not suitable
            else:
                return 0   # Studio or no bedrooms

        except (ValueError, TypeError):
            return 0

    def _calculate_outdoor_space_score(self, outdoor_space: str) -> float:
        """
        Calculate outdoor space score.
        """
        try:
            outdoor_space = str(outdoor_space).lower()

            if any(term in outdoor_space for term in ['large garden', 'big garden', 'spacious garden']):
                return 10
            elif any(term in outdoor_space for term in ['garden', 'yard', 'patio']):
                return 8
            elif any(term in outdoor_space for term in ['small garden', 'courtyard', 'terrace']):
                return 6
            elif any(term in outdoor_space for term in ['balcony', 'roof terrace']):
                return 4
            elif any(term in outdoor_space for term in ['none', 'no', 'n/a']):
                return 0
            else:
                return 3  # Unknown but assume some outdoor space

        except Exception:
            return 3

    def _calculate_schools_score(self, ofsted_rating: str) -> float:
        """
        Calculate schools score based on nearest school Ofsted rating.
        """
        try:
            rating = str(ofsted_rating).lower()

            if 'outstanding' in rating:
                return 10
            elif 'good' in rating:
                return 8
            elif 'requires improvement' in rating:
                return 5
            elif 'inadequate' in rating:
                return 2
            else:
                return 6  # Unknown - assume average

        except Exception:
            return 6

    def _calculate_grammar_bonus_score(self, grammar_proximity: str) -> float:
        """
        Calculate grammar school bonus score.
        """
        try:
            proximity = str(grammar_proximity).lower()

            if any(term in proximity for term in ['yes', 'close', 'within catchment', 'nearby']):
                return 10  # Full bonus
            elif any(term in proximity for term in ['possible', 'maybe', 'borderline']):
                return 5   # Partial bonus
            else:
                return 0   # No bonus

        except Exception:
            return 0

    def _get_default_scores(self) -> Dict[str, Any]:
        """Return default zero scores in case of calculation errors."""
        return {
            'price_score': 0,
            'commute_score': 0,
            'property_type_score': 0,
            'bedrooms_score': 0,
            'outdoor_space_score': 0,
            'schools_score': 0,
            'grammar_bonus_score': 0,
            'total_score': 0,
            'breakdown': {
                'Price': '0/20',
                'Commute': '0/20',
                'Property Type': '0/15',
                'Bedrooms': '0/15',
                'Outdoor Space': '0/10',
                'Schools': '0/10',
                'Grammar Bonus': '0/10'
            }
        }

    def get_score_color(self, score: float) -> str:
        """
        Get color coding for scores.

        Args:
            score: Score value

        Returns:
            Color name for display
        """
        if score >= 70:
            return 'green'
        elif score >= 50:
            return 'orange'
        else:
            return 'red'

    def get_score_emoji(self, score: float) -> str:
        """
        Get emoji for score visualization.

        Args:
            score: Score value

        Returns:
            Emoji string
        """
        if score >= 85:
            return '🏆'  # Trophy
        elif score >= 70:
            return '⭐'   # Star
        elif score >= 50:
            return '👍'   # Thumbs up
        else:
            return '⚠️'    # Warning


class PropertyValidator:
    """
    Validates property data and ensures data quality.
    """

    def __init__(self):
        """Initialize validator with validation rules."""
        self.required_fields = [
            'property_id', 'price', 'bedrooms', 'postcode', 'property_type'
        ]

        self.postcode_pattern = re.compile(r'^[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][A-Z]{2}$')

    def validate_property(self, property_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate property data.

        Args:
            property_data: Property data dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        for field in self.required_fields:
            if field not in property_data or not property_data[field]:
                errors.append(f"Missing required field: {field}")

        # Validate price
        try:
            price = float(property_data.get('price', 0))
            if price <= 0:
                errors.append("Price must be greater than 0")
            elif price > 2000000:
                errors.append("Price seems unrealistic (>£2M)")
        except (ValueError, TypeError):
            errors.append("Price must be a valid number")

        # Validate bedrooms
        try:
            bedrooms = int(property_data.get('bedrooms', 0))
            if bedrooms < 0 or bedrooms > 10:
                errors.append("Bedrooms must be between 0 and 10")
        except (ValueError, TypeError):
            errors.append("Bedrooms must be a valid number")

        # Validate postcode
        postcode = str(property_data.get('postcode', '')).upper().strip()
        if postcode and not self.postcode_pattern.match(postcode):
            errors.append("Postcode format is invalid")

        is_valid = len(errors) == 0
        return is_valid, errors

    def clean_property_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and normalize property data.

        Args:
            property_data: Raw property data

        Returns:
            Cleaned property data
        """
        cleaned = property_data.copy()

        # Clean price
        if 'price' in cleaned:
            try:
                # Remove currency symbols and commas
                price_str = str(cleaned['price']).replace('£', '').replace(',', '').strip()
                cleaned['price'] = float(price_str)
            except (ValueError, TypeError):
                cleaned['price'] = 0

        # Clean bedrooms
        if 'bedrooms' in cleaned:
            try:
                cleaned['bedrooms'] = int(cleaned['bedrooms'])
            except (ValueError, TypeError):
                cleaned['bedrooms'] = 0

        # Clean postcode
        if 'postcode' in cleaned:
            cleaned['postcode'] = str(cleaned['postcode']).upper().strip()

        # Clean property type
        if 'property_type' in cleaned:
            cleaned['property_type'] = str(cleaned['property_type']).title().strip()

        return cleaned


class AutomationEngine:
    """
    Main automation engine that coordinates scoring, validation, and API integration.
    """

    def __init__(self, reference_postcode: str = "SE1 9SP"):
        """
        Initialize automation engine.

        Args:
            reference_postcode: Reference postcode for calculations
        """
        self.reference_postcode = reference_postcode
        self.scorer = PropertyScoringEngine(reference_postcode)
        self.validator = PropertyValidator()
        self.api_cache = {}  # Simple caching for API calls

    def process_property(self, property_data: Dict[str, Any], api_simulator=None) -> Dict[str, Any]:
        """
        Process a property through validation, API enrichment, and scoring.

        Args:
            property_data: Raw property data
            api_simulator: Optional API simulator instance

        Returns:
            Processed property data with scores
        """
        try:
            # Step 1: Clean data
            cleaned_data = self.validator.clean_property_data(property_data)

            # Step 2: Validate data
            is_valid, errors = self.validator.validate_property(cleaned_data)
            if not is_valid:
                logger.warning(f"Property validation errors: {errors}")
                cleaned_data['validation_errors'] = errors

            # Step 3: Enrich with API data (if simulator provided)
            if api_simulator:
                enriched_data = self._enrich_with_api_data(cleaned_data, api_simulator)
            else:
                enriched_data = cleaned_data

            # Step 4: Calculate scores
            scores = self.scorer.calculate_total_score(enriched_data)

            # Step 5: Combine all data
            result = {**enriched_data, **scores}
            result['processed_at'] = datetime.now().isoformat()
            result['reference_postcode'] = self.reference_postcode

            return result

        except Exception as e:
            logger.error(f"Error processing property: {str(e)}")
            return {**property_data, 'processing_error': str(e)}

    def _enrich_with_api_data(self, property_data: Dict[str, Any], api_simulator) -> Dict[str, Any]:
        """
        Enrich property data using API simulator.

        Args:
            property_data: Property data
            api_simulator: API simulator instance

        Returns:
            Enriched property data
        """
        enriched = property_data.copy()
        postcode = property_data.get('postcode', '')

        if not postcode:
            return enriched

        try:
            # Get commute time
            if 'commute_time' not in enriched or not enriched['commute_time']:
                commute_data = api_simulator.get_commute_time(
                    from_postcode=postcode,
                    to_postcode=self.reference_postcode
                )
                enriched['commute_time'] = commute_data.get('duration_minutes', 60)
                enriched['commute_distance'] = commute_data.get('distance_km', 'Unknown')

            # Get distance to station
            if 'distance_to_station' not in enriched or not enriched['distance_to_station']:
                station_data = api_simulator.get_nearest_station(postcode)
                enriched['distance_to_station'] = station_data.get('distance_km', 'Unknown')
                enriched['nearest_station'] = station_data.get('name', 'Unknown')

            # Get school data
            if 'nearest_school_ofsted' not in enriched or not enriched['nearest_school_ofsted']:
                school_data = api_simulator.get_school_info(postcode)
                enriched['nearest_school_ofsted'] = school_data.get('ofsted_rating', 'Unknown')
                enriched['nearest_school_name'] = school_data.get('name', 'Unknown')

            # Get grammar school proximity
            if 'grammar_school_proximity' not in enriched or not enriched['grammar_school_proximity']:
                grammar_data = api_simulator.check_grammar_schools(postcode)
                enriched['grammar_school_proximity'] = grammar_data.get('in_catchment', 'No')
                enriched['grammar_schools_nearby'] = grammar_data.get('schools', [])

        except Exception as e:
            logger.error(f"Error enriching property data: {str(e)}")

        return enriched

    def batch_process_properties(self, properties: List[Dict[str, Any]], api_simulator=None) -> List[Dict[str, Any]]:
        """
        Process multiple properties in batch.

        Args:
            properties: List of property data dictionaries
            api_simulator: Optional API simulator instance

        Returns:
            List of processed properties
        """
        processed = []

        for i, property_data in enumerate(properties):
            logger.info(f"Processing property {i+1}/{len(properties)}")
            processed_property = self.process_property(property_data, api_simulator)
            processed.append(processed_property)

        return processed

    def get_top_properties(self, properties: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Get top N properties by score.

        Args:
            properties: List of processed properties
            top_n: Number of top properties to return

        Returns:
            Top N properties sorted by total score
        """
        # Sort by total score descending
        sorted_properties = sorted(
            properties, 
            key=lambda x: x.get('total_score', 0), 
            reverse=True
        )

        return sorted_properties[:top_n]

    def generate_property_summary(self, property_data: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary of a property.

        Args:
            property_data: Processed property data

        Returns:
            Summary string
        """
        try:
            price = property_data.get('price', 0)
            bedrooms = property_data.get('bedrooms', 0)
            property_type = property_data.get('property_type', 'Unknown')
            postcode = property_data.get('postcode', 'Unknown')
            total_score = property_data.get('total_score', 0)

            summary = f"£{price:,.0f} {property_type} with {bedrooms} bedroom{'s' if bedrooms != 1 else ''} in {postcode}. "
            summary += f"Overall score: {total_score:.0f}/100 {self.scorer.get_score_emoji(total_score)}"

            return summary

        except Exception as e:
            return f"Property summary unavailable: {str(e)}"


# Factory function for easy import
def create_automation_engine(reference_postcode: str = "SE1 9SP") -> AutomationEngine:
    """
    Factory function to create an automation engine instance.

    Args:
        reference_postcode: Reference postcode for calculations

    Returns:
        AutomationEngine instance
    """
    return AutomationEngine(reference_postcode)


if __name__ == "__main__":
    # Example usage
    engine = create_automation_engine()

    # Example property data
    sample_property = {
        'property_id': 'TEST001',
        'price': 350000,
        'bedrooms': 3,
        'property_type': 'Semi-Detached',
        'postcode': 'SE9 3JD',
        'outdoor_space': 'Garden',
        'commute_time': 35,
        'nearest_school_ofsted': 'Good',
        'grammar_school_proximity': 'Yes'
    }

    # Process property
    result = engine.process_property(sample_property)

    print("Property Processing Example:")
    print(f"Total Score: {result.get('total_score', 0)}/100")
    print(f"Summary: {engine.generate_property_summary(result)}")
