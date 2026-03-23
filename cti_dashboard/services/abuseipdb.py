import requests
from config import Config

def query_abuseipdb(ip):
    url = "https://api.abuseipdb.com/api/v2/check"
    querystring = {'ipAddress': ip, 'maxAgeInDays': '90'}
    headers = {'Accept': 'application/json', 'Key': Config.ABUSEIPDB_API_KEY}
    response = requests.get(url, headers=headers, params=querystring)
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {})
    return None