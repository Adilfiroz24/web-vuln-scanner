import re
from datetime import datetime

def parse_ssh_log(filepath):
    """
    Parse SSH log (e.g., auth.log) and return a list of events.
    Each event: {'ip': str, 'timestamp': datetime, 'type': 'ssh_failed'}
    """
    events = []
    # Pattern for failed password attempts (both for invalid user and valid user)
    pattern = re.compile(
        r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+).*sshd.*Failed password for (?:\w+ )?(?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+)'
    )
    with open(filepath, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                # Parse timestamp (simplified, assumes current year)
                ts_str = match.group('timestamp')
                # Convert to datetime object; year is not in log, we can set to current year
                # Here we just store the string for simplicity
                # For actual detection, we might need time windows; we'll keep string for now.
                events.append({
                    'ip': match.group('ip'),
                    'timestamp': ts_str,
                    'type': 'ssh_failed'
                })
    return events

def parse_apache_log(filepath):
    """
    Parse Apache access log (common or combined format) and return events.
    Each event: {'ip': str, 'timestamp': str, 'status': int, 'type': 'http_failed'}
    We'll count 401 status as failed authentication.
    """
    events = []
    # Common Log Format: ip - - [timestamp] "method path protocol" status size
    pattern = re.compile(
        r'(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<timestamp>[^\]]+)\] "\S+ \S+ \S+" (?P<status>\d+)'
    )
    with open(filepath, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                status = int(match.group('status'))
                if status == 401:   # Failed authentication
                    events.append({
                        'ip': match.group('ip'),
                        'timestamp': match.group('timestamp'),
                        'type': 'http_failed',
                        'status': status
                    })
    return events