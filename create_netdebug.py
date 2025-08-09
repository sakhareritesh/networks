import os

# Folder structure
structure = [
    "netdebug",
    "netdebug/network",
    "netdebug/report",
    "netdebug/report/templates",
    "netdebug/utils",
]

files_content = {
    # __init__.py files
    "netdebug/__init__.py": "",
    "netdebug/network/__init__.py": "",
    "netdebug/report/__init__.py": "",
    "netdebug/utils/__init__.py": "",

    # cli.py
    "netdebug/cli.py": """import click
from netdebug.network import ping as pingmod
from netdebug.network import portscan as pscan
from netdebug.network import traceroute as trmod
from netdebug.report.generator import generate_report
from rich.console import Console

console = Console()

@click.group()
def cli():
    '''NetDebug: simple network debugging toolkit.'''
    pass

@cli.command()
@click.argument("host")
@click.option("--count", default=4, help="Number of ping packets")
def ping(host, count):
    console.print(f"[bold]Pinging[/bold] {host} ({count} packets)...")
    res = pingmod.ping_host(host, count=count)
    console.print(res)

@cli.command()
@click.argument("host")
@click.option("--ports", default="22,80,443", help="Comma or dash-separated ports or ranges")
@click.option("--concurrency", default=200)
def portscan(host, ports, concurrency):
    ports_list = pscan.parse_ports(ports)
    console.print(f"Scanning {host} ports: {ports_list[:20]} ...")
    results = pscan.scan_ports(host, ports_list, concurrency)
    console.print(results)

@cli.command()
@click.argument("host")
@click.option("--tasks", default="ping,portscan,traceroute")
@click.option("--out", default="report.html")
@click.option("--pdf", is_flag=True)
def report(host, tasks, out, pdf):
    tasks = tasks.split(",")
    generate_report(host, tasks, out, pdf)
    console.print(f"Report saved to {out}")

if __name__ == "__main__":
    cli()
""",

    # ping.py
    "netdebug/network/ping.py": """import platform
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
    loss_match = re.search(r"(\\d+)% packet loss", output)
    if loss_match:
        result["packet_loss_percent"] = int(loss_match.group(1))
    rtt_match = re.search(r"rtt min/avg/max/mdev = ([\\d\\.]+)/([\\d\\.]+)/([\\d\\.]+)", output)
    if rtt_match:
        result["rtt_min"], result["rtt_avg"], result["rtt_max"] = map(float, rtt_match.groups()[:3])
    return result
""",

    # portscan.py
    "netdebug/network/portscan.py": """import asyncio
from typing import List, Dict

def parse_ports(ports_str: str) -> List[int]:
    parts = ports_str.split(",")
    res = set()
    for part in parts:
        part = part.strip()
        if "-" in part:
            a,b = part.split("-")
            res.update(range(int(a), int(b)+1))
        else:
            res.add(int(part))
    return sorted(res)

async def _scan_port(host: str, port: int, timeout: float = 1.0) -> (int, bool):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
        writer.close()
        await writer.wait_closed()
        return port, True
    except Exception:
        return port, False

async def _scan_all(host: str, ports: List[int], concurrency: int = 500) -> Dict[int,bool]:
    sem = asyncio.Semaphore(concurrency)
    results = {}
    async def sem_scan(p):
        async with sem:
            port, ok = await _scan_port(host, p)
            results[port] = ok
    await asyncio.gather(*(sem_scan(p) for p in ports))
    return results

def scan_ports(host: str, ports: List[int], concurrency: int = 500) -> Dict[int,bool]:
    return asyncio.run(_scan_all(host, ports, concurrency))
""",

    # traceroute.py
    "netdebug/network/traceroute.py": """import platform, subprocess

def traceroute(host: str, max_hops: int = 30):
    system = platform.system().lower()
    if 'windows' in system:
        cmd = ["tracert", "-h", str(max_hops), host]
    else:
        cmd = ["traceroute", "-m", str(max_hops), host]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout + p.stderr
""",

    # generator.py
    "netdebug/report/generator.py": """import os
from jinja2 import Environment, FileSystemLoader
from netdebug.network import ping as pingmod, portscan as pscan, traceroute as trmod
from weasyprint import HTML  # optional

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def generate_report(host: str, tasks: list, out_html: str = "report.html", pdf: bool = False):
    data = {"host": host, "tasks": {}}
    if "ping" in tasks:
        data["tasks"]["ping"] = pingmod.ping_host(host)
    if "portscan" in tasks:
        ports = pscan.parse_ports("22,80,443,8080")
        data["tasks"]["portscan"] = pscan.scan_ports(host, ports)
    if "traceroute" in tasks:
        data["tasks"]["traceroute"] = trmod.traceroute(host)
    template = env.get_template("report.html.j2")
    html = template.render(data=data)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    if pdf:
        HTML(string=html).write_pdf(out_html.replace(".html", ".pdf"))
""",

    # HTML template
    "netdebug/report/templates/report.html.j2": """<!doctype html>
<html>
<head><meta charset="utf-8"><title>NetDebug Report - {{ data.host }}</title></head>
<body>
  <h1>NetDebug Report: {{ data.host }}</h1>
  {% if data.tasks.ping %}
    <h2>Ping</h2>
    <pre>{{ data.tasks.ping.raw }}</pre>
  {% endif %}
  {% if data.tasks.portscan %}
    <h2>Port Scan</h2>
    <ul>
    {% for port, open in data.tasks.portscan.items() %}
      <li>{{ port }} : {{ "OPEN" if open else "closed" }}</li>
    {% endfor %}
    </ul>
  {% endif %}
  {% if data.tasks.traceroute %}
    <h2>Traceroute</h2>
    <pre>{{ data.tasks.traceroute }}</pre>
  {% endif %}
</body>
</html>
""",

    # requirements.txt
    "requirements.txt": """click
jinja2
rich
weasyprint
"""
}

# Create folders
for folder in structure:
    os.makedirs(folder, exist_ok=True)

# Create files
for path, content in files_content.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("✅ NetDebug Toolkit folder structure & files created successfully!")
print("Next steps:")
print("1) cd to this folder")
print("2) python -m venv venv && source venv/bin/activate (or venv\\Scripts\\activate on Windows)")
print("3) pip install -r requirements.txt")
print("4) python -m netdebug.cli ping google.com")