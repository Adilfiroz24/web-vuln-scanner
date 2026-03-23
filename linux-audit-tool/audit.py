#!/usr/bin/env python3
"""
Linux Hardening Audit Tool
Runs security checks and generates reports (TXT + HTML).
"""

import os
from datetime import datetime
from config import COLORS
from checks import firewall, ssh_check, permissions, services

def run_audit():
    print(f"\n{'='*50}")
    print("🔍 Linux Hardening Audit Tool")
    print(f"{'='*50}\n")

    # Run all checks
    results = []
    results.append(("Firewall", firewall.check_firewall()))
    results.append(("SSH", ssh_check.check_ssh()))
    results.append(("Permissions", permissions.check_world_writable()))
    results.append(("Services", services.check_disabled_services()))

    # Print to terminal with colors
    for name, (status, message) in results:
        color = COLORS.get(status, COLORS['ENDC'])
        print(f"{name:15} [{color}{status:5}{COLORS['ENDC']}] {message}")

    # Generate reports
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_report = f"reports/audit_report_{timestamp}.txt"
    html_report = f"reports/audit_report_{timestamp}.html"

    # Text report
    with open(txt_report, 'w') as f:
        f.write(f"Linux Hardening Audit Report - {timestamp}\n")
        f.write("="*50 + "\n")
        for name, (status, message) in results:
            f.write(f"{name:15} [{status:5}] {message}\n")
    print(f"\n📄 Text report saved to: {txt_report}")

    # HTML report (using external template)
    generate_html_report(results, html_report, timestamp)
    print(f"📊 HTML report saved to: {html_report}")

def generate_html_report(results, filename, timestamp):
    """Generate styled HTML report from template."""
    template_path = "templates/report_template.html"
    try:
        with open(template_path, 'r') as f:
            html_template = f.read()
    except FileNotFoundError:
        print(f"❌ Template not found at {template_path}. Using inline fallback.")
        # Fallback minimal HTML if template missing
        html_template = """
        <!DOCTYPE html><html><head><title>Audit Report</title>
        <style>body{{font-family:Arial;}} .PASS{{color:green;}} .FAIL{{color:red;}} .WARN{{color:orange;}}</style>
        </head><body><h1>Audit Report - {{timestamp}}</h1><table>{{rows}}</table></body></html>
        """

    rows_html = ""
    for name, (status, message) in results:
        badge_class = f"badge-{status}"
        rows_html += f"""
        <tr>
            <td>{name}</td>
            <td><span class="status-badge {badge_class}">{status}</span></td>
            <td class="message">{message}</td>
        </tr>
        """

    final_html = html_template.replace("{{timestamp}}", timestamp).replace("{{rows}}", rows_html)
    with open(filename, 'w') as f:
        f.write(final_html)

if __name__ == "__main__":
    if not os.path.exists("reports"):
        os.makedirs("reports")
    run_audit()