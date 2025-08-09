import click
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
