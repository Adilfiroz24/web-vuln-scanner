from collections import defaultdict

def detect_bruteforce(events, threshold=5):
    """
    Count failures per IP and return dict of IP -> count for those exceeding threshold.
    """
    counts = defaultdict(int)
    for event in events:
        counts[event['ip']] += 1

    suspicious = {ip: cnt for ip, cnt in counts.items() if cnt >= threshold}
    return suspicious

def detect_ssh_bruteforce(ssh_events, threshold=5):
    return detect_bruteforce(ssh_events, threshold)

def detect_http_bruteforce(http_events, threshold=10):
    return detect_bruteforce(http_events, threshold)