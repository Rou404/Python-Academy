# Scans ALL TCP ports (1..65535), lists open ports, then calls functions to retrieve two flags (web + TCP).

import asyncio, socket, re, sys, urllib.request, urllib.error
from contextlib import suppress

HOST = "192.168.1.23"  # <-- CHANGE THIS to your IP
TIMEOUT = 0.35         # seconds per connection (LAN-friendly)
CONCURRENCY = 512      # async connections at once (tune down if needed)
FLAG_RE = re.compile(r"FLAG\{[A-Za-z0-9_\-]+\}")

# ---------- STUDENT TODO #1 ----------
def try_http_flag(host: str, port: int):
    """
    TODO: Implement a minimal HTTP probe that:
      1) Requests:  http://{host}:{port}/
         - If this fails with a URL error or looks non-HTTP, just return None.
      2) Requests:  http://{host}:{port}/note?id=0
         - If body contains 'FLAG{...}', return the matched flag string; else None.

    Hints:
      - Use urllib.request.urlopen with a short timeout.
      - Decode bytes with UTF-8 (ignore errors).
      - A quick way to check 'is HTTP' is: does / return a 200/404 and some HTML/text?
    """
    # Example (pseudo):
    # try:
    #     with urllib.request.urlopen(f"http://{host}:{port}/", timeout=2.0) as r:
    #         _ = r.read()  # we don't need it, it's just a reachability/fingerprint
    return None
# -------------------------------------


# ---------- STUDENT TODO #2 ----------
def try_tcp_flag(host: str, port: int):
    """
    TODO: Implement a minimal line-based TCP dialogue that:
      1) Connects to (host, port) with socket.create_connection((host, port),timeout=2).
      2) Reads initial banner (s.recv(1024)).
      3) Sends a help-like command (e.g., 'HELP\\r\\n'), reads response.
      4) Sends another short command (e.g., 'FLAG\\r\\n'), reads response.
      5) If any text contains 'FLAG{...}', return the flag string.

    Hints:
      - Remember to send CRLF (\\r\\n) at the end of each command.
      - Decode bytes with ASCII (ignore errors).
    """
# -------------------------------------


# ====== below this line is ready-to-run infrastructure ======

async def check_port(sema, host, port):
    async with sema:
        loop = asyncio.get_event_loop()
        with suppress(Exception):
            fut = loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            await loop.run_in_executor(None, fut)  # resolve
        try:
            conn = asyncio.open_connection(host, port)
            r, w = await asyncio.wait_for(conn, timeout=TIMEOUT)
            w.close()
            with suppress(Exception):
                await w.wait_closed()
            return port
        except Exception:
            return None

async def scan_all_ports(host):
    sema = asyncio.Semaphore(CONCURRENCY)
    tasks = [asyncio.create_task(check_port(sema, host, p)) for p in range(1, 65536)]
    open_ports = []
    for i, t in enumerate(asyncio.as_completed(tasks), 1):
        res = await t
        if res:
            open_ports.append(res)
            print(f"OPEN {res}")
        # (Optional) a tiny progress cue every few thousand completions:
        if i % 5000 == 0:
            print(f"...checked {i} ports")
    return sorted(open_ports)

def classify_and_hunt(host, port):
    # Try HTTP path first
    flag = try_http_flag(host, port)
    if flag:
        return ("WEB", flag)
    # Then try a simple line-based TCP dialogue
    flag = try_tcp_flag(host, port)
    if flag:
        return ("TCP", flag)
    return (None, None)

def main():
    print(f"[+] Target: {HOST}")
    print("[+] Scanning all TCP ports (1..65535). This should be quick on a LAN...")
    open_ports = asyncio.run(scan_all_ports(HOST))
    if not open_ports:
        print("[-] No open ports found.")
        return

    print("\n[+] Open ports:")
    print(", ".join(map(str, open_ports)))

    web_flag = None
    tcp_flag = None
    for p in open_ports:
        kind, flag = classify_and_hunt(HOST, p)
        if kind == "WEB" and not web_flag:
            web_flag = (flag, p); print(f"[WEB] port {p} -> {flag}")
        elif kind == "TCP" and not tcp_flag:
            tcp_flag = (flag, p); print(f"[TCP] port {p} -> {flag}")
        if web_flag and tcp_flag:
            break

    print("\n=== RESULTS ===")
    print(f"WEB FLAG: {web_flag[0]} (port {web_flag[1]})" if web_flag else "WEB FLAG: not found")
    print(f"TCP FLAG: {tcp_flag[0]} (port {tcp_flag[1]})" if tcp_flag else "TCP FLAG: not found")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
