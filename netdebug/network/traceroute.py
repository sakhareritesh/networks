import platform, subprocess

def traceroute(host: str, max_hops: int = 30):
    system = platform.system().lower()
    if 'windows' in system:
        cmd = ["tracert", "-h", str(max_hops), host]
    else:
        cmd = ["traceroute", "-m", str(max_hops), host]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout + p.stderr
