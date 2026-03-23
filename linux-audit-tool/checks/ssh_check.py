import config
from pathlib import Path

def check_ssh():
    sshd_config = Path('/etc/ssh/sshd_config')
    if not sshd_config.exists():
        return ('FAIL', "SSH config not found")

    with open(sshd_config) as f:
        content = f.read().splitlines()

    issues = []
    # Check PermitRootLogin
    for line in content:
        # Skip comments
        if line.strip().startswith('#'):
            continue
        if line.startswith('PermitRootLogin'):
            parts = line.split()
            if len(parts) >= 2:
                value = parts[1]
                if value != config.SSH_PERMIT_ROOT_LOGIN:
                    issues.append(f"PermitRootLogin is {value} (should be {config.SSH_PERMIT_ROOT_LOGIN})")
        if line.startswith('PasswordAuthentication'):
            parts = line.split()
            if len(parts) >= 2:
                value = parts[1]
                if value != config.SSH_PASSWORD_AUTH:
                    issues.append(f"PasswordAuthentication is {value} (should be {config.SSH_PASSWORD_AUTH})")
        if line.startswith('Protocol'):
            parts = line.split()
            if len(parts) >= 2:
                value = parts[1]
                if value != config.SSH_PROTOCOL:
                    issues.append(f"Protocol is {value} (should be {config.SSH_PROTOCOL})")

    if issues:
        return ('FAIL', "; ".join(issues))
    return ('PASS', "SSH configuration is secure")