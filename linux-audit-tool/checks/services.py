import subprocess
import config

def check_disabled_services():
    running = []
    for svc in config.DISABLED_SERVICES:
        try:
            result = subprocess.run(['systemctl', 'is-active', svc],
                                    capture_output=True, text=True)
            if result.returncode == 0:   # service is active
                running.append(svc)
        except FileNotFoundError:
            # systemctl not available – maybe not systemd
            return ('WARN', "systemctl not found – cannot check services")
        except Exception:
            pass
    if running:
        return ('FAIL', f"Dangerous services running: {', '.join(running)}")
    return ('PASS', "No dangerous services are active")