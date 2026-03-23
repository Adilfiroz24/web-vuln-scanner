from datetime import datetime

def generate_report(ssh_suspicious, http_suspicious, output_file):
    """
    Write a comprehensive report to output_file.
    """
    with open(output_file, 'w') as f:
        f.write("INCIDENT REPORT\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")

        if ssh_suspicious:
            f.write("SSH BRUTE FORCE DETECTIONS\n")
            f.write("-" * 25 + "\n")
            for ip, count in sorted(ssh_suspicious.items(), key=lambda x: x[1], reverse=True):
                f.write(f"IP: {ip} - Failed attempts: {count}\n")
            f.write("\n")
        else:
            f.write("No SSH brute force attempts detected.\n\n")

        if http_suspicious:
            f.write("HTTP AUTHENTICATION FAILURES (401)\n")
            f.write("-" * 35 + "\n")
            for ip, count in sorted(http_suspicious.items(), key=lambda x: x[1], reverse=True):
                f.write(f"IP: {ip} - 401 responses: {count}\n")
            f.write("\n")
        else:
            f.write("No HTTP 401 failures detected.\n\n")

        f.write("END OF REPORT\n")