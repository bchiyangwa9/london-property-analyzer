"""
London Property Analyzer - API Simulator
========================================

Mock API simulator for external services including Google Maps, Ofsted, TfL, and Grammar Schools.
Provides realistic mock data for development and testing purposes with reference postcode support.

Author: AI Assistant
Version: 2.0 - Dual Mode System
"""

import random
import time
from typing import Dict, List, Any, Optional, Tuple
import math
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockGoogleMapsAPI:
    """
    Mock Google Maps API for commute time and distance calculations.
    Uses realistic London geography and transport patterns.
    """

    def __init__(self):
        """Initialize with London postcode coordinate mappings."""
        # Approximate coordinates for key London areas (lat, lon)
        self.postcode_coords = {
            # Central London
            'SE1 9SP': (51.5074, -0.0886),  # London Bridge (reference)
            'SW1Y 5HX': (51.5074, -0.1372), # Marlborough House
            'EC2V 7AN': (51.5155, -0.0922), # City of London
            'WC2N 5DU': (51.5098, -0.1241), # Covent Garden

            # South East London
            'SE9 3JD': (51.4394, 0.0755),   # Sidcup
            'SE9 1SZ': (51.4269, 0.0745),   # New Eltham
            'BR6 0NZ': (51.3562, 0.0956),   # Orpington
            'BR7 5EA': (51.4053, 0.0364),   # Chislehurst
            'SE18 1JJ': (51.4934, 0.0670),  # Woolwich
            'DA14 4DX': (51.4500, 0.1167),  # Sidcup
            'DA15 7HD': (51.4333, 0.1500),  # Bexley
            'BR1 2TW': (51.3706, 0.0106),   # Bromley

            # Transport hubs
            'SE10 9HT': (51.4826, -0.0077), # Greenwich
            'SE13 7SD': (51.4615, -0.0157), # Lewisham
            'SE6 4RU': (51.4406, -0.0208),  # Catford
            'SE12 8RZ': (51.4298, 0.0188),  # Lee
            'SE3 9DS': (51.4639, 0.0105),   # Blackheath
        }

        # Station connections and typical journey times
        self.station_data = {
            'SE9 3JD': {'station': 'Sidcup', 'line': 'Bexleyheath Line', 'walk_min': 8},
            'BR6 0NZ': {'station': 'Orpington', 'line': 'Main Line', 'walk_min': 12},
            'BR7 5EA': {'station': 'Elmstead Woods', 'line': 'Main Line', 'walk_min': 15},
            'SE18 1JJ': {'station': 'Woolwich Arsenal', 'line': 'DLR/Elizabeth Line', 'walk_min': 10},
            'DA14 4DX': {'station': 'Sidcup', 'line': 'Bexleyheath Line', 'walk_min': 6},
            'DA15 7HD': {'station': 'Bexley', 'line': 'Bexleyheath Line', 'walk_min': 9},
        }

        # Base journey times to central London (minutes)
        self.base_journey_times = {
            'Sidcup': 35,
            'Orpington': 28,
            'Elmstead Woods': 32,
            'Woolwich Arsenal': 25,
            'Bexley': 40,
            'New Eltham': 30,
            'Chislehurst': 25,
        }

    def get_commute_time(self, from_postcode: str, to_postcode: str = "SE1 9SP", 
                        transport_mode: str = "transit") -> Dict[str, Any]:
        """
        Calculate commute time between postcodes using public transport.

        Args:
            from_postcode: Starting postcode
            to_postcode: Destination postcode (default: London Bridge)
            transport_mode: Transport mode (transit, driving, walking)

        Returns:
            Dictionary with commute information
        """
        try:
            # Simulate API delay
            time.sleep(random.uniform(0.1, 0.3))

            # Get coordinates
            from_coords = self.postcode_coords.get(from_postcode.upper())
            to_coords = self.postcode_coords.get(to_postcode.upper(), (51.5074, -0.0886))

            if not from_coords:
                # Estimate based on similar postcodes
                duration_minutes = random.randint(35, 55)
                distance_km = random.uniform(15, 25)
            else:
                # Calculate realistic journey time based on location
                distance_km = self._calculate_distance(from_coords, to_coords)

                if from_postcode.upper() in self.station_data:
                    station_info = self.station_data[from_postcode.upper()]
                    base_time = self.base_journey_times.get(station_info['station'], 40)
                    walk_time = station_info['walk_min']

                    # Add variability for peak/off-peak
                    variability = random.uniform(-5, 10)  # Peak times can add delays
                    duration_minutes = base_time + walk_time + variability
                else:
                    # Estimate based on distance
                    duration_minutes = distance_km * 2.5 + random.uniform(5, 15)

            # Ensure realistic bounds
            duration_minutes = max(15, min(75, duration_minutes))

            return {
                'duration_minutes': round(duration_minutes),
                'distance_km': round(distance_km, 1),
                'mode': transport_mode,
                'route_summary': self._generate_route_summary(from_postcode, to_postcode),
                'peak_time_addition': random.randint(5, 12),
                'reliability_score': random.uniform(0.7, 0.95),
                'last_updated': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculating commute time: {str(e)}")
            return {
                'duration_minutes': 45,  # Default fallback
                'distance_km': 20.0,
                'mode': transport_mode,
                'route_summary': f"{from_postcode} to {to_postcode}",
                'error': str(e)
            }

    def get_nearest_station(self, postcode: str) -> Dict[str, Any]:
        """
        Get nearest train station information.

        Args:
            postcode: Property postcode

        Returns:
            Dictionary with station information
        """
        try:
            time.sleep(random.uniform(0.1, 0.2))

            if postcode.upper() in self.station_data:
                station_info = self.station_data[postcode.upper()]
                return {
                    'name': station_info['station'],
                    'distance_km': round(station_info['walk_min'] * 0.08, 1),  # ~0.08km per minute walk
                    'walk_time_minutes': station_info['walk_min'],
                    'line': station_info['line'],
                    'zones': self._get_zone_info(station_info['station']),
                    'services': self._get_station_services(station_info['station'])
                }
            else:
                # Generate reasonable estimates for unknown postcodes
                stations = ['Sidcup', 'Orpington', 'New Eltham', 'Woolwich Arsenal', 'Bexley']
                station = random.choice(stations)
                return {
                    'name': station,
                    'distance_km': round(random.uniform(0.5, 2.0), 1),
                    'walk_time_minutes': random.randint(6, 25),
                    'line': 'Main Line',
                    'zones': '4-5',
                    'services': ['National Rail']
                }

        except Exception as e:
            logger.error(f"Error getting station info: {str(e)}")
            return {'name': 'Unknown', 'distance_km': 1.0, 'error': str(e)}

    def _calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """Calculate distance between two coordinates using Haversine formula."""
        lat1, lon1 = coord1
        lat2, lon2 = coord2

        # Haversine formula
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c

    def _generate_route_summary(self, from_postcode: str, to_postcode: str) -> str:
        """Generate a realistic route summary."""
        if from_postcode.upper() in self.station_data:
            station = self.station_data[from_postcode.upper()]['station']
            return f"Walk to {station} → {station} to London Bridge → Walk to destination"
        else:
            return f"{from_postcode} → London Bridge via public transport"

    def _get_zone_info(self, station: str) -> str:
        """Get London transport zone information."""
        zone_map = {
            'Sidcup': '5',
            'Orpington': '5-6',
            'Elmstead Woods': '4',
            'Woolwich Arsenal': '4',
            'Bexley': '6',
            'New Eltham': '4',
            'Chislehurst': '5'
        }
        return zone_map.get(station, '4-5')

    def _get_station_services(self, station: str) -> List[str]:
        """Get available transport services at station."""
        services_map = {
            'Sidcup': ['National Rail', 'Bexleyheath Line'],
            'Orpington': ['National Rail', 'Thameslink'],
            'Woolwich Arsenal': ['DLR', 'Elizabeth Line', 'National Rail'],
            'Bexley': ['National Rail', 'Bexleyheath Line']
        }
        return services_map.get(station, ['National Rail'])


class MockOfstedAPI:
    """
    Mock Ofsted API for school ratings and information.
    """

    def __init__(self):
        """Initialize with realistic school data for London areas."""
        # Mock school data for different postcodes
        self.schools_database = {
            'SE9': [
                {'name': 'Sidcup Primary School', 'type': 'Primary', 'rating': 'Good', 'distance': 0.3},
                {'name': 'Longlands Primary School', 'type': 'Primary', 'rating': 'Outstanding', 'distance': 0.8},
                {'name': 'Chislehurst & Sidcup Grammar School', 'type': 'Secondary', 'rating': 'Outstanding', 'distance': 1.2},
            ],
            'BR6': [
                {'name': 'Orpington Primary School', 'type': 'Primary', 'rating': 'Good', 'distance': 0.4},
                {'name': 'Newstead Wood School', 'type': 'Secondary', 'rating': 'Outstanding', 'distance': 0.6},
                {'name': 'St Olave's Grammar School', 'type': 'Secondary', 'rating': 'Outstanding', 'distance': 2.1},
            ],
            'BR7': [
                {'name': 'Elmstead Primary School', 'type': 'Primary', 'rating': 'Good', 'distance': 0.5},
                {'name': 'Bromley High School', 'type': 'Secondary', 'rating': 'Good', 'distance': 1.8},
            ],
            'SE18': [
                {'name': 'Woolwich Polytechnic School', 'type': 'Secondary', 'rating': 'Good', 'distance': 0.7},
                {'name': 'St Peter's Catholic Primary School', 'type': 'Primary', 'rating': 'Outstanding', 'distance': 0.9},
            ],
            'DA14': [
                {'name': 'Sidcup Community Primary School', 'type': 'Primary', 'rating': 'Good', 'distance': 0.4},
                {'name': 'Hurstmere School', 'type': 'Secondary', 'rating': 'Requires Improvement', 'distance': 1.1},
            ],
            'DA15': [
                {'name': 'Bexley Primary School', 'type': 'Primary', 'rating': 'Good', 'distance': 0.6},
                {'name': 'Bexleyheath Academy', 'type': 'Secondary', 'rating': 'Good', 'distance': 1.5},
            ]
        }

        # Ofsted rating distribution (realistic)
        self.rating_weights = {
            'Outstanding': 0.2,
            'Good': 0.6,
            'Requires Improvement': 0.15,
            'Inadequate': 0.05
        }

    def get_school_info(self, postcode: str, school_type: str = "Primary") -> Dict[str, Any]:
        """
        Get information about nearest schools.

        Args:
            postcode: Property postcode
            school_type: Type of school (Primary, Secondary, All)

        Returns:
            Dictionary with school information
        """
        try:
            time.sleep(random.uniform(0.2, 0.4))

            # Extract postcode prefix
            postcode_prefix = postcode.upper()[:3] if len(postcode) >= 3 else postcode.upper()

            # Get schools for area
            schools = self.schools_database.get(postcode_prefix, [])

            if not schools:
                # Generate realistic mock data for unknown areas
                schools = self._generate_mock_schools(postcode_prefix)

            # Filter by type if specified
            if school_type != "All":
                schools = [s for s in schools if s['type'] == school_type]

            if not schools:
                # Fallback - generate a school
                schools = [self._generate_single_school(postcode_prefix, school_type)]

            # Return nearest school
            nearest_school = min(schools, key=lambda x: x['distance'])

            return {
                'name': nearest_school['name'],
                'ofsted_rating': nearest_school['rating'],
                'school_type': nearest_school['type'],
                'distance_km': nearest_school['distance'],
                'postcode_area': postcode_prefix,
                'last_inspection': self._get_mock_inspection_date(),
                'pupil_count': random.randint(180, 450),
                'all_schools_nearby': schools[:3],  # Top 3 nearest
                'data_source': 'Ofsted Mock API'
            }

        except Exception as e:
            logger.error(f"Error getting school info: {str(e)}")
            return {
                'name': 'Unknown School',
                'ofsted_rating': 'Requires Improvement',
                'school_type': school_type,
                'distance_km': 1.0,
                'error': str(e)
            }

    def _generate_mock_schools(self, postcode_prefix: str) -> List[Dict[str, Any]]:
        """Generate realistic mock schools for unknown areas."""
        schools = []

        # Generate 2-4 schools
        for i in range(random.randint(2, 4)):
            school_type = random.choice(['Primary', 'Secondary'])
            rating = self._weighted_random_rating()

            schools.append({
                'name': f"{postcode_prefix} {school_type} School",
                'type': school_type,
                'rating': rating,
                'distance': round(random.uniform(0.2, 2.0), 1)
            })

        return schools

    def _generate_single_school(self, postcode_prefix: str, school_type: str) -> Dict[str, Any]:
        """Generate a single mock school."""
        return {
            'name': f"{postcode_prefix} {school_type} School",
            'type': school_type,
            'rating': self._weighted_random_rating(),
            'distance': round(random.uniform(0.3, 1.5), 1)
        }

    def _weighted_random_rating(self) -> str:
        """Get a weighted random Ofsted rating."""
        rand = random.random()
        cumulative = 0

        for rating, weight in self.rating_weights.items():
            cumulative += weight
            if rand <= cumulative:
                return rating

        return 'Good'  # Fallback

    def _get_mock_inspection_date(self) -> str:
        """Generate a realistic inspection date."""
        # Ofsted inspections happen every 3-7 years
        days_ago = random.randint(30, 2555)  # Up to 7 years
        inspection_date = datetime.now() - timedelta(days=days_ago)
        return inspection_date.strftime('%Y-%m-%d')


class MockGrammarSchoolAPI:
    """
    Mock API for Grammar School catchment area information.
    """

    def __init__(self):
        """Initialize with Grammar School data for London/Kent areas."""
        # Real Grammar Schools in the target areas
        self.grammar_schools = {
            'Bexley Grammar School': {
                'catchment_postcodes': ['DA5', 'DA6', 'DA7', 'DA14', 'DA15'],
                'type': 'Boys',
                'location': 'Welling',
                'entry_requirements': '11+ exam'
            },
            'Chislehurst & Sidcup Grammar School': {
                'catchment_postcodes': ['SE9', 'DA14', 'DA15', 'BR7'],
                'type': 'Boys',
                'location': 'Sidcup',
                'entry_requirements': '11+ exam'
            },
            'Newstead Wood School': {
                'catchment_postcodes': ['BR6', 'BR2', 'SE9', 'DA14'],
                'type': 'Girls',
                'location': 'Orpington',
                'entry_requirements': '11+ exam'
            },
            'St Olave's Grammar School': {
                'catchment_postcodes': ['BR6', 'SE9', 'BR7', 'DA16'],
                'type': 'Boys',
                'location': 'Orpington',
                'entry_requirements': '11+ exam'
            },
            'Townley Grammar School': {
                'catchment_postcodes': ['DA6', 'DA7', 'SE18', 'DA14'],
                'type': 'Girls',
                'location': 'Bexleyheath',
                'entry_requirements': '11+ exam'
            }
        }

    def check_grammar_schools(self, postcode: str) -> Dict[str, Any]:
        """
        Check Grammar School catchment areas for postcode.

        Args:
            postcode: Property postcode

        Returns:
            Dictionary with grammar school information
        """
        try:
            time.sleep(random.uniform(0.1, 0.3))

            postcode_prefix = postcode.upper()[:3] if len(postcode) >= 3 else postcode.upper()

            # Find matching grammar schools
            matching_schools = []
            for school_name, school_info in self.grammar_schools.items():
                if any(postcode_prefix.startswith(cp) for cp in school_info['catchment_postcodes']):
                    matching_schools.append({
                        'name': school_name,
                        'type': school_info['type'],
                        'location': school_info['location'],
                        'distance_estimate': self._estimate_distance(postcode_prefix, school_info['location'])
                    })

            # Determine catchment status
            in_catchment = "Yes" if matching_schools else "No"

            # Add probability for borderline cases
            if not matching_schools and random.random() < 0.1:  # 10% chance of borderline
                in_catchment = "Possible"
                matching_schools = [self._get_nearest_grammar_school(postcode_prefix)]

            return {
                'in_catchment': in_catchment,
                'schools': matching_schools,
                'total_grammar_schools_nearby': len(matching_schools),
                'postcode_area': postcode_prefix,
                'selection_process': '11+ examination',
                'application_deadline': 'October 31st annually',
                'notes': self._get_catchment_notes(in_catchment, matching_schools)
            }

        except Exception as e:
            logger.error(f"Error checking grammar schools: {str(e)}")
            return {
                'in_catchment': 'Unknown',
                'schools': [],
                'error': str(e)
            }

    def _estimate_distance(self, postcode_prefix: str, location: str) -> float:
        """Estimate distance to grammar school."""
        # Simple distance estimates based on known locations
        distance_map = {
            ('SE9', 'Sidcup'): 2.1,
            ('BR6', 'Orpington'): 1.5,
            ('DA14', 'Welling'): 3.2,
            ('SE18', 'Bexleyheath'): 2.8
        }

        key = (postcode_prefix, location)
        if key in distance_map:
            return distance_map[key]
        else:
            return round(random.uniform(2.0, 8.0), 1)

    def _get_nearest_grammar_school(self, postcode_prefix: str) -> Dict[str, Any]:
        """Get nearest grammar school for borderline cases."""
        return {
            'name': 'Nearest Grammar School',
            'type': 'Mixed',
            'location': 'Nearby',
            'distance_estimate': round(random.uniform(5.0, 12.0), 1)
        }

    def _get_catchment_notes(self, in_catchment: str, schools: List[Dict[str, Any]]) -> str:
        """Generate helpful notes about catchment status."""
        if in_catchment == "Yes" and schools:
            return f"Within catchment for {len(schools)} grammar school(s). 11+ exam required."
        elif in_catchment == "Possible":
            return "Borderline catchment area. Contact schools directly for admission criteria."
        else:
            return "Outside typical grammar school catchment areas for this postcode."


class APISimulator:
    """
    Main API Simulator that coordinates all mock APIs.
    Provides a unified interface for all external API calls.
    """

    def __init__(self, reference_postcode: str = "SE1 9SP"):
        """
        Initialize API simulator with reference postcode.

        Args:
            reference_postcode: Default reference postcode for calculations
        """
        self.reference_postcode = reference_postcode
        self.google_maps = MockGoogleMapsAPI()
        self.ofsted = MockOfstedAPI()
        self.grammar_schools = MockGrammarSchoolAPI()

        # API call statistics
        self.call_count = {'maps': 0, 'ofsted': 0, 'grammar': 0}
        self.start_time = datetime.now()

    def get_commute_time(self, from_postcode: str, to_postcode: Optional[str] = None) -> Dict[str, Any]:
        """
        Get commute time using Google Maps API simulator.

        Args:
            from_postcode: Starting postcode
            to_postcode: Destination postcode (uses reference if not provided)

        Returns:
            Commute information dictionary
        """
        self.call_count['maps'] += 1
        destination = to_postcode or self.reference_postcode
        return self.google_maps.get_commute_time(from_postcode, destination)

    def get_nearest_station(self, postcode: str) -> Dict[str, Any]:
        """
        Get nearest train station information.

        Args:
            postcode: Property postcode

        Returns:
            Station information dictionary
        """
        return self.google_maps.get_nearest_station(postcode)

    def get_school_info(self, postcode: str, school_type: str = "Primary") -> Dict[str, Any]:
        """
        Get school information using Ofsted API simulator.

        Args:
            postcode: Property postcode
            school_type: Type of school to search for

        Returns:
            School information dictionary
        """
        self.call_count['ofsted'] += 1
        return self.ofsted.get_school_info(postcode, school_type)

    def check_grammar_schools(self, postcode: str) -> Dict[str, Any]:
        """
        Check grammar school catchment areas.

        Args:
            postcode: Property postcode

        Returns:
            Grammar school information dictionary
        """
        self.call_count['grammar'] += 1
        return self.grammar_schools.check_grammar_schools(postcode)

    def get_comprehensive_property_data(self, postcode: str) -> Dict[str, Any]:
        """
        Get all available data for a property postcode in one call.

        Args:
            postcode: Property postcode

        Returns:
            Comprehensive property data dictionary
        """
        try:
            logger.info(f"Fetching comprehensive data for {postcode}")

            # Get all data in parallel (simulated)
            commute_data = self.get_commute_time(postcode)
            station_data = self.get_nearest_station(postcode)
            primary_school_data = self.get_school_info(postcode, "Primary")
            secondary_school_data = self.get_school_info(postcode, "Secondary")
            grammar_data = self.check_grammar_schools(postcode)

            return {
                'postcode': postcode.upper(),
                'commute': commute_data,
                'transport': station_data,
                'primary_schools': primary_school_data,
                'secondary_schools': secondary_school_data,
                'grammar_schools': grammar_data,
                'data_completeness': self._calculate_data_completeness({
                    'commute': commute_data,
                    'transport': station_data,
                    'schools': primary_school_data,
                    'grammar': grammar_data
                }),
                'fetched_at': datetime.now().isoformat(),
                'reference_postcode': self.reference_postcode
            }

        except Exception as e:
            logger.error(f"Error fetching comprehensive data: {str(e)}")
            return {'postcode': postcode, 'error': str(e)}

    def _calculate_data_completeness(self, data: Dict[str, Any]) -> float:
        """Calculate completeness score for fetched data."""
        total_fields = 0
        valid_fields = 0

        for category, category_data in data.items():
            if isinstance(category_data, dict):
                for key, value in category_data.items():
                    total_fields += 1
                    if value and value != 'Unknown' and 'error' not in str(value).lower():
                        valid_fields += 1

        return round((valid_fields / total_fields) * 100, 1) if total_fields > 0 else 0.0

    def get_api_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics."""
        runtime = datetime.now() - self.start_time

        return {
            'total_calls': sum(self.call_count.values()),
            'calls_by_api': self.call_count.copy(),
            'runtime_seconds': runtime.total_seconds(),
            'calls_per_minute': sum(self.call_count.values()) / max(runtime.total_seconds() / 60, 1),
            'reference_postcode': self.reference_postcode,
            'start_time': self.start_time.isoformat()
        }

    def reset_statistics(self):
        """Reset API call statistics."""
        self.call_count = {'maps': 0, 'ofsted': 0, 'grammar': 0}
        self.start_time = datetime.now()


# Factory function for easy import
def create_api_simulator(reference_postcode: str = "SE1 9SP") -> APISimulator:
    """
    Factory function to create an API simulator instance.

    Args:
        reference_postcode: Reference postcode for calculations

    Returns:
        APISimulator instance
    """
    return APISimulator(reference_postcode)


if __name__ == "__main__":
    # Example usage
    api_sim = create_api_simulator()

    # Test with a sample postcode
    test_postcode = "SE9 3JD"

    print("API Simulator Test:")
    print(f"Testing with postcode: {test_postcode}")

    # Get comprehensive data
    data = api_sim.get_comprehensive_property_data(test_postcode)

    print(f"Commute Time: {data['commute']['duration_minutes']} minutes")
    print(f"Nearest Station: {data['transport']['name']}")
    print(f"School Rating: {data['primary_schools']['ofsted_rating']}")
    print(f"Grammar Schools: {data['grammar_schools']['in_catchment']}")
    print(f"Data Completeness: {data['data_completeness']}%")

    # Show statistics
    stats = api_sim.get_api_statistics()
    print(f"API Calls Made: {stats['total_calls']}")
