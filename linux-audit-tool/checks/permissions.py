import os
import stat
import config

def check_world_writable():
    findings = []
    for path in config.WORLD_WRITABLE_PATHS:
        if not os.path.exists(path):
            continue
        for root, dirs, files in os.walk(path):
            for name in files:
                full = os.path.join(root, name)
                try:
                    # Skip symlinks to avoid following them
                    if os.path.islink(full):
                        continue
                    mode = os.stat(full).st_mode
                    if mode & stat.S_IWOTH:   # world-writable
                        findings.append(full)
                except (OSError, PermissionError):
                    pass
    if findings:
        # Show only first 5 to keep report readable
        sample = ', '.join(findings[:5])
        if len(findings) > 5:
            sample += f" ... and {len(findings)-5} more"
        return ('WARN', f"World-writable files found: {sample}")
    return ('PASS', "No world-writable files in critical paths")