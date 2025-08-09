import asyncio
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
