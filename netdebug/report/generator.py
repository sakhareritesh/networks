import os
from jinja2 import Environment, FileSystemLoader
from netdebug.network import ping as pingmod, portscan as pscan, traceroute as trmod

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
     print("⚠ PDF generation skipped (WeasyPrint not available). HTML report generated instead.")