import requests
from config import Config

def query_virustotal(ioc):
    url = f"https://www.virustotal.com/api/v3/search?query={ioc}"
    headers = {"x-apikey": Config.VIRUSTOTAL_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('data'):
            attributes = data['data'][0]['attributes']
            last_analysis_stats = attributes.get('last_analysis_stats', {})
            return {
                'malicious': last_analysis_stats.get('malicious', 0),
                'suspicious': last_analysis_stats.get('suspicious', 0),
                'harmless': last_analysis_stats.get('harmless', 0),
                'undetected': last_analysis_stats.get('undetected', 0)
            }
    return None