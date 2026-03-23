import os
import sys
from parser import parse_ssh_log, parse_apache_log
from detector import detect_ssh_bruteforce, detect_http_bruteforce
from report import generate_report

def main():
    # Paths (adjust if needed)
    logs_dir = "logs"
    ssh_log = os.path.join(logs_dir, "ssh.log")
    apache_log = os.path.join(logs_dir, "apache.log")
    report_file = "reports/report.txt"

    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)

    print("[*] Parsing SSH log...")
    ssh_events = parse_ssh_log(ssh_log)
    print(f"[*] Found {len(ssh_events)} SSH failed events")

    print("[*] Parsing Apache log...")
    apache_events = parse_apache_log(apache_log)
    print(f"[*] Found {len(apache_events)} HTTP 401 events")

    print("[*] Detecting SSH brute force...")
    ssh_suspicious = detect_ssh_bruteforce(ssh_events, threshold=5)
    print(f"[*] {len(ssh_suspicious)} suspicious IPs in SSH")

    print("[*] Detecting HTTP brute force...")
    http_suspicious = detect_http_bruteforce(apache_events, threshold=10)
    print(f"[*] {len(http_suspicious)} suspicious IPs in HTTP")

    print("[*] Generating report...")
    generate_report(ssh_suspicious, http_suspicious, report_file)
    print(f"[*] Report saved to {report_file}")

if __name__ == "__main__":
    main()