# config.py

# Paths to scan for world-writable files
WORLD_WRITABLE_PATHS = ['/etc', '/bin', '/sbin', '/usr']

# SSH hardening rules (CIS inspired)
SSH_PERMIT_ROOT_LOGIN = 'no'
SSH_PASSWORD_AUTH = 'no'
SSH_PROTOCOL = '2'

# Services that should be disabled
DISABLED_SERVICES = ['telnet', 'rsh', 'rlogin', 'ftp']

# Firewall expected default policy
EXPECTED_FW_POLICY = 'DROP'   # iptables default policy

# Terminal colors
COLORS = {
    'PASS': '\033[92m',   # Green
    'FAIL': '\033[91m',   # Red
    'WARN': '\033[93m',   # Yellow
    'ENDC': '\033[0m',    # Reset
}