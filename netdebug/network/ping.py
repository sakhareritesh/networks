import platform
import subprocess
import re
from typing import Dict

def ping_host(host: str, count: int = 4, timeout: int = 2) -> Dict:
    system = platform.system().lower()
    if 'windows' in system:
        cmd = ["ping", "-n", str(count), "-w", str(int(timeout*1000)), host]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]

    p = subprocess.run(cmd, capture_output=True, text=True)
    out = p.stdout + p.stderr
    return parse_ping_output(out, system)

def parse_ping_output(output: str, system: str):
    result = {"raw": output}
    loss_match = re.search(r"(\d+)% packet loss", output)
    if loss_match:
        result["packet_loss_percent"] = int(loss_match.group(1))
    rtt_match = re.search(r"rtt min/avg/max/mdev = ([\d\.]+)/([\d\.]+)/([\d\.]+)", output)
    if rtt_match:
        result["rtt_min"], result["rtt_avg"], result["rtt_max"] = map(float, rtt_match.groups()[:3])
    return result
