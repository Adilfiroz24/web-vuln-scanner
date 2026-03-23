import requests
import time
from .logger import setup_logger

logger = setup_logger('geoip')

geoip_cache = {}
last_request_time = 0
RATE_LIMIT_DELAY = 0.1

def get_geoip_info(ip_address):
    if is_private_ip(ip_address):
        return {
            'country': 'Private',
            'country_code': 'XX',
            'lat': 0,
            'lon': 0
        }
    
    if ip_address in geoip_cache:
        return geoip_cache[ip_address]
    
    global last_request_time
    current_time = time.time()
    if current_time - last_request_time < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY)
    
    try:
        response = requests.get(f'http://ipapi.co/{ip_address}/json/', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            geo_info = {
                'country': data.get('country_name', 'Unknown'),
                'country_code': data.get('country_code', 'XX'),
                'lat': data.get('latitude', 0),
                'lon': data.get('longitude', 0),
                'city': data.get('city', 'Unknown'),
                'region': data.get('region', 'Unknown'),
                'org': data.get('org', 'Unknown')
            }
            
            geoip_cache[ip_address] = geo_info
            last_request_time = time.time()
            
            return geo_info
            
        else:
            logger.warning(f"GeoIP API returned status {response.status_code} for {ip_address}")
            
    except Exception as e:
        logger.error(f"GeoIP lookup failed for {ip_address}: {e}")
    
    return {
        'country': 'Unknown',
        'country_code': 'XX',
        'lat': 0,
        'lon': 0
    }

def is_private_ip(ip):
    private_ranges = [
        '10.', '192.168.', '172.16.', '172.17.', '172.18.', '172.19.',
        '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
        '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.',
        '127.0.0.1', '::1'
    ]
    
    return any(ip.startswith(prefix) for prefix in private_ranges)