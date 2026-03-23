import os

class Config:
    VIRUSTOTAL_API_KEY = os.environ.get('VIRUSTOTAL_API_KEY', '823325ed5a7607bf8e05e8edc299c9c04c10d438b922bcd5f0e71b695cdce28b')
    ABUSEIPDB_API_KEY = os.environ.get('ABUSEIPDB_API_KEY', '00f09bab589ea5d7a585966b5d8ca0bc5ac3e55df9e0aa9dc638d419fe08a42fc561612b0b330e23')
    DATABASE_FILE = 'cti.db'