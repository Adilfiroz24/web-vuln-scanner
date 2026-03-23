import subprocess
from config import EXPECTED_FW_POLICY

def check_firewall():
    """
    Check if iptables default policy is set to DROP or REJECT.
    Returns (status, details)
    """
    try:
        output = subprocess.check_output(['iptables', '-L'], text=True, stderr=subprocess.DEVNULL)
        lines = output.splitlines()
        for line in lines:
            if 'Chain INPUT' in line and 'policy' in line:
                policy = line.split()[3]   # Usually DROP/ACCEPT
                if policy == EXPECTED_FW_POLICY:
                    return ('PASS', f"INPUT policy is {policy}")
                else:
                    return ('FAIL', f"INPUT policy is {policy} (expected {EXPECTED_FW_POLICY})")
        return ('WARN', "Could not determine firewall policy")
    except FileNotFoundError:
        return ('FAIL', "iptables command not found – is it installed?")
    except Exception as e:
        return ('FAIL', f"Firewall check error: {e}")