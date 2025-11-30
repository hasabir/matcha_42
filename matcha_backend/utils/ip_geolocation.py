"""
IP Geolocation utility to detect user location from IP address
Uses a free IP geolocation API as fallback when GPS is denied
"""
import requests
import logging

logger = logging.getLogger(__name__)


def normalize_country_name(country):
    """
    Normalize country names to handle different languages and variations
    Maps common variations to standard English names
    
    Args:
        country: Country name in any language
    
    Returns:
        str: Normalized country name in English
    """
    if not country:
        return country
    
    # Convert to lowercase for comparison
    country_lower = country.lower().strip()
    
    # Country name mappings (local names -> English names)
    country_mappings = {
        # Morocco variations
        'maroc': 'Morocco',
        'marruecos': 'Morocco',
        'المغرب': 'Morocco',
        
        # France variations
        'france': 'France',
        'francia': 'France',
        
        # Spain variations
        'españa': 'Spain',
        'espagne': 'Spain',
        
        # Germany variations
        'deutschland': 'Germany',
        'allemagne': 'Germany',
        
        # Italy variations
        'italia': 'Italy',
        'italie': 'Italy',
        
        # United Kingdom variations
        'united kingdom': 'United Kingdom',
        'royaume-uni': 'United Kingdom',
        'uk': 'United Kingdom',
        
        # United States variations
        'united states': 'United States',
        'usa': 'United States',
        'états-unis': 'United States',
        
        # Canada variations
        'canada': 'Canada',
        'canadá': 'Canada',
    }
    
    # Return mapped name if found, otherwise return original with proper capitalization
    return country_mappings.get(country_lower, country.title())


def get_location_from_ip(ip_address):
    """
    Get location data from an IP address using ip-api.com (free, no key required)
    
    Args:
        ip_address: IP address to geolocate
    
    Returns:
        dict: Location data with keys: latitude, longitude, city, country
        None: If geolocation fails
    """
    try:
        # Skip localhost/private IPs (RFC 1918 and Docker networks)
        private_ranges = [
            '127.0.0.1', 'localhost', '::1',
            '192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.',
            '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
            '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.'
        ]
        
        is_private = ip_address in ['127.0.0.1', 'localhost', '::1']
        if not is_private:
            for prefix in private_ranges:
                if ip_address.startswith(prefix):
                    is_private = True
                    break
        
        if is_private:
            logger.warning(f"IP geolocation failed: private range")
            logger.info(f"Skipping geolocation for local/private IP: {ip_address}")
            # Return None for development - let the frontend handle this gracefully
            return None
        
        # Call ip-api.com API (free tier: 45 requests/minute)
        api_url = f'http://ip-api.com/json/{ip_address}?fields=status,message,country,city,lat,lon'
        
        response = requests.get(api_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                latitude = data.get('lat')
                longitude = data.get('lon')
                
                location = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'city': data.get('city'),
                    'country': normalize_country_name(data.get('country')),
                    'source': 'ip'
                }
                
                # Get neighborhood-level detail using reverse geocoding
                try:
                    neighborhood_data = get_neighborhood_from_coords(latitude, longitude)
                    if neighborhood_data:
                        location['neighborhood'] = neighborhood_data
                        logger.info(f"Successfully geolocated IP {ip_address}: {location['city']}, {location.get('neighborhood', 'N/A')}, {location['country']}")
                    else:
                        logger.info(f"Successfully geolocated IP {ip_address}: {location['city']}, {location['country']} (no neighborhood data)")
                except Exception as e:
                    logger.warning(f"Could not get neighborhood data: {e}")
                    logger.info(f"Successfully geolocated IP {ip_address}: {location['city']}, {location['country']}")
                
                return location
            else:
                logger.warning(f"IP geolocation failed: {data.get('message')}")
                return None
        else:
            logger.error(f"IP geolocation API returned status {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("IP geolocation API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"IP geolocation API request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_location_from_ip: {e}")
        return None


def get_client_ip(request):
    """
    Extract client IP address from Flask request
    Handles proxies and load balancers
    
    Args:
        request: Flask request object
    
    Returns:
        str: Client IP address
    """
    # Check for common proxy headers
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For can contain multiple IPs, take the first one
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    
    return ip


def get_neighborhood_from_coords(latitude, longitude):
    """
    Get neighborhood-level location information from GPS coordinates
    Uses Nominatim OpenStreetMap API (free, no API key required)
    Implements neighborhood-level GPS positioning as per subject requirements
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns:
        str: Neighborhood name or None if not available
    """
    try:
        # Validate coordinates
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            logger.error(f"Invalid coordinates for neighborhood lookup: lat={latitude}, lon={longitude}")
            return None
        
        # Use Nominatim API with zoom level for neighborhood precision
        api_url = f'https://nominatim.openstreetmap.org/reverse'
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'addressdetails': 1,
            'zoom': 17,  # Zoom level 17-18 gives neighborhood/suburb level detail
            'accept-language': 'en'
        }
        headers = {
            'User-Agent': 'Matcha-Dating-App/1.0'  # Required by Nominatim usage policy
        }
        
        response = requests.get(api_url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            # Try to extract neighborhood (priority order for precision)
            neighborhood = (
                address.get('neighbourhood') or  # British spelling
                address.get('neighborhood') or   # American spelling
                address.get('suburb') or
                address.get('quarter') or
                address.get('district') or
                address.get('subdistrict') or
                address.get('borough') or
                address.get('city_district')
            )
            
            if neighborhood:
                logger.info(f"✅ Found neighborhood for ({latitude}, {longitude}): {neighborhood}")
                return neighborhood
            else:
                logger.warning(f"⚠️ No neighborhood data available for ({latitude}, {longitude})")
                return None
        else:
            logger.error(f"Neighborhood lookup API returned status {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("Neighborhood lookup API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Neighborhood lookup API request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in get_neighborhood_from_coords: {e}")
        return None


def reverse_geocode(latitude, longitude):
    """
    Reverse geocode GPS coordinates to get city, country, and neighborhood
    Uses Nominatim OpenStreetMap API (free, no API key required)
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns:
        dict: Location data with keys: city, country, neighborhood (optional)
        None: If reverse geocoding fails
    """
    try:
        # Validate coordinates
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            logger.error(f"Invalid coordinates for reverse geocoding: lat={latitude}, lon={longitude}")
            return None
        
        # Use Nominatim API (OpenStreetMap's free reverse geocoding service)
        # Be respectful: include User-Agent and don't hammer the API
        api_url = f'https://nominatim.openstreetmap.org/reverse'
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'addressdetails': 1,
            'zoom': 17,  # Get neighborhood-level detail
            'accept-language': 'en'  # Get results in English
        }
        headers = {
            'User-Agent': 'Matcha-Dating-App/1.0'  # Required by Nominatim usage policy
        }
        
        response = requests.get(api_url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            
            # Extract city (try multiple possible fields)
            city = (
                address.get('city') or 
                address.get('town') or 
                address.get('village') or 
                address.get('municipality') or
                address.get('county')
            )
            
            # Extract country
            country = address.get('country')
            
            # Extract neighborhood (as per subject requirements)
            neighborhood = (
                address.get('neighbourhood') or
                address.get('neighborhood') or
                address.get('suburb') or
                address.get('quarter') or
                address.get('district')
            )
            
            result = {
                'city': city,
                'country': normalize_country_name(country)
            }
            
            if neighborhood:
                result['neighborhood'] = neighborhood
            
            if city and country:
                logger.info(f"✅ Reverse geocoded ({latitude}, {longitude}) -> {city}, {neighborhood or 'N/A'}, {country}")
                return result
            else:
                logger.warning(f"⚠️ Reverse geocoding incomplete for ({latitude}, {longitude}): city={city}, country={country}")
                return result if (city or country) else None
        else:
            logger.error(f"Reverse geocoding API returned status {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("Reverse geocoding API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Reverse geocoding API request failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in reverse_geocode: {e}")
        return None
