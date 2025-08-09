# 🛠️ NetDebug Toolkit

A Python-based CLI (Command Line Interface) tool for performing essential network diagnostics like `ping`, `traceroute`, and `TCP port scanning`, with the ability to generate clean, human-readable HTML reports.

---

## 📌 Features

- ✅ Ping a host and collect packet loss + latency stats
- 🌐 Perform a `traceroute` to visualize the path to a host
- 🔎 Scan TCP ports (e.g., 22, 80, 443) to check open/closed status
- 📝 Generate a detailed HTML report of the results
- ⚙️ Asynchronous scanning using `asyncio` for fast performance
- 📦 Clean, modular Python code structure

---

## 🚀 CLI Usage

```bash
python -m netdebug.cli [command] [options]
