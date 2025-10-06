"""
Networking in Python — Sockets, IPs & Ports (Complete Lesson in One File)
Python: 3.9+

USAGE (pick one of the demos to run)
------------------------------------
# Terminal examples (run in separate shells for server/client when noted)
python networking_in_python_lesson.py --demo echo_server --port 5000
python networking_in_python_lesson.py --demo echo_client --host 127.0.0.1 --port 5000 --message "hello"

python networking_in_python_lesson.py --demo udp_time_server --port 5001
python networking_in_python_lesson.py --demo udp_time_client --host 127.0.0.1 --port 5001

python networking_in_python_lesson.py --demo rpc_server --port 6000
# use netcat or any language as a client, send one JSON line:
# {"op":"add","args":[2,3]}

python networking_in_python_lesson.py --demo http_by_hand --host example.com --port 80 --path /

# Flask browser game (LAN number guessing)
# (First time) pip install flask
python networking_in_python_lesson.py --demo guess_game --port 8080

# Then, on other devices on the same Wi‑Fi/LAN: http://<your-LAN-IP>:8080/

---------------------------------------------------------------
READ ME FIRST — THEORY (quick, friendly, and accurate)
---------------------------------------------------------------
WHAT IS "NETWORKING"?
- It's how programs talk to each other across a network (your laptop, a LAN, or the internet).
- The fundamental tool is a SOCKET: a programmatic "plug" you read from and write to.
  In Python, a socket behaves like a file descriptor for network I/O.

KEY TERMS
- IP address: numeric address of a device on a network. IPv4 looks like 192.168.1.42.
  - 127.0.0.1 is localhost (this machine only).
  - 0.0.0.0 means "all interfaces" when binding a server (listen on all your IPs).
- Port: a numbered “door” (0–65535) a service uses on a host.
  - 22 (SSH), 80 (HTTP), 443 (HTTPS). Below 1024 often require admin on Unix.
- Client vs Server:
  - Server: waits (listens) for connections on a port.
  - Client: initiates a connection to a server's IP:port.
- TCP vs UDP:
  - TCP gives a reliable, ordered byte stream. Great for web, APIs, file transfer.
  - UDP sends individual packets (datagrams) with low overhead. Faster but can drop or reorder.
- DNS: translates names like "example.com" to an IP address.
- Blocking vs Non‑blocking:
  - Blocking recv() waits until data arrives. Simple to understand.
  - Non‑blocking / multiplexing uses select(), selectors, or asyncio to serve many sockets efficiently.
- HTTP as text over TCP:
  - A browser "speaks" HTTP, which is a protocol made of human‑readable headers and body over a TCP connection.

SECURITY & PRACTICAL NOTES
- Keep demos on a trusted LAN. Don’t expose class demos to the public internet.
- Wi‑Fi isolation settings may block peer‑to‑peer traffic on school networks.
- Firewalls might require allowing inbound on your chosen port.
- Never run unknown code that listens on 0.0.0.0 on a public network.

LEARNING OBJECTIVES
1) Explain IP, port, TCP vs UDP, client vs server, sockets.
2) Open a TCP socket in Python, send/receive bytes, handle multiple clients.
3) See HTTP as text over TCP and why frameworks exist.
4) Call a Python function from another app over the network (tiny JSON-RPC).
5) Build an engaging LAN guessing game accessible from phones/laptops.

----------------------------------------------------------------------
STRUCTURE OF THIS FILE
----------------------------------------------------------------------
- Each demo is a function you can run via --demo <name>
- "TODO" comments are exercises for you.
- Code is runnable out‑of‑the‑box (except Flask game requires "pip install flask").
- Keep this single file for the whole lesson to reduce friction.
"""

from __future__ import annotations   # Type hints (lets us use forward references; faster imports)

import argparse                      # Parse command-line flags like --demo, --port
import json                          # Encode/decode JSON messages (e.g., our tiny RPC protocol)
import socket                        # Low-level networking: TCP/UDP sockets, bind/listen/accept/connect/recv/send
import sys                           # Access argv/exit and other interpreter/runtime details
import threading                     # Handle multiple clients concurrently with threads
import time                          # Timestamps, sleep, simple timing in demos (e.g., UDP time server)
from dataclasses import dataclass    # Lightweight class boilerplate for CLI args container
from typing import Callable, Dict, Tuple  # Static typing: function signatures and data structures


# ---------- Utility helpers ----------

def get_lan_ip_guess() -> str:
    """
    Try to guess the LAN IP by opening a dummy UDP socket. This never sends real traffic.
    Useful for knowing what address to use to reach your server on the LAN.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # connect() on UDP doesn't send packets but binds to the right interface
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


# ---------- DEMO 1: Minimal TCP Echo Server (Blocking) ----------

def demo_echo_server(host: str, port: int) -> None:
    """
    A minimal TCP echo server. Accepts one client at a time (blocking).

    THEORY:
    - socket.socket(AF_INET, SOCK_STREAM) -> TCP over IPv4.
    - bind((host, port)) attaches the socket to OS networking.
    - listen() starts the server "queue" for incoming connections.
    - accept() blocks until a client connects; returns (conn, addr).
    - recv() reads bytes; sendall() writes bytes.
    - 'with conn:' ensures the connection is closed when done.

    TODOs (exercises):
    - Add a timestamp before each echoed message.
    - Add a quit command: if client sends 'quit', close the connection.
    - Limit message size and handle overflow gracefully.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        print(f"[echo_server] Listening on {host}:{port} (LAN hint: {get_lan_ip_guess()}:{port})")
        while True:
            conn, addr = s.accept()  # blocking
            print(f"[echo_server] Connected by {addr}")
            with conn:
                while True:
                    data = conn.recv(1024)  # blocking until data or client closes
                    if not data:
                        print("[echo_server] Client closed connection.")
                        break
                    print(f"[echo_server] <- {data!r}")
                    conn.sendall(data)      # echo back
                    print(f"[echo_server] -> echoed {len(data)} bytes")


def demo_echo_client(host: str, port: int, message: str) -> None:
    """
    A minimal TCP echo client. Connects to the echo server, sends one message, prints reply.

    TODOs:
    - Turn this into an interactive loop that reads from input() until 'quit'.
    - Add sock.settimeout(2) and handle socket.timeout exceptions.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))  # TCP handshake happens here
        print(f"[echo_client] Connected to {host}:{port}")
        sock.sendall(message.encode())
        print(f"[echo_client] -> sent {message!r}")
        reply = sock.recv(1024)
        print(f"[echo_client] <- received {reply!r}")


# ---------- DEMO 2: Concurrent Echo Server (Thread per client) ----------

def demo_echo_server_threads(host: str, port: int) -> None:
    """
    Serve multiple clients concurrently by using a thread per connection.

    THEORY:
    - Each client gets its own thread running 'handle_client'.
    - Pros: easy to reason about; Cons: many threads can exhaust resources.
    - Alternative: asyncio/selectors for scalable concurrency.

    TODOs:
    - Log the current number of connected clients.
    - Add per‑client message counters or rate limits.
    """
    def handle_client(conn: socket.socket, addr: Tuple[str, int]) -> None:
        print(f"[threads] Connected by {addr}")
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    print(f"[threads] {addr} disconnected")
                    break
                msg = data.decode(errors="replace")
                resp = f"[you said] {msg}".encode()
                conn.sendall(resp)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        print(f"[threads] Listening on {host}:{port} (LAN hint: {get_lan_ip_guess()}:{port})")
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()


# ---------- DEMO 3: Tiny JSON-RPC-ish Server (call Python functions) ----------

def add(a: float, b: float) -> float:
    return a + b

def mul(a: float, b: float) -> float:
    return a * b

FUNCTIONS: Dict[str, Callable[..., float]] = {
    "add": add,
    "mul": mul,
    # TODO: add "pow", "avg", etc. Validate input types!
}

def demo_rpc_server(host: str, port: int) -> None:
    """
    A newline‑delimited JSON protocol. Each line is a JSON request:
      {"op":"add","args":[2,3]}

    Server returns a JSON response on the same line:
      {"ok": true, "result": 5}

    THEORY:
    - This demonstrates "calling a Python function from other applications" over TCP.
    - Protocol design: pick framing (we use '\n' delimited JSON).
    - Robustness: validate ops and arity; return structured errors.
    """
    def handle(conn: socket.socket, addr: Tuple[str, int]) -> None:
        print(f"[rpc] client {addr} connected")
        buf = b""
        with conn:
            while True:
                chunk = conn.recv(4096)
                if not chunk:
                    print(f"[rpc] client {addr} disconnected")
                    break
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    try:
                        req = json.loads(line.decode())
                        op = req.get("op")
                        args = req.get("args", [])
                        if op not in FUNCTIONS:
                            raise ValueError(f"unknown op {op!r}")
                        result = FUNCTIONS[op](*args)
                        resp = {"ok": True, "result": result}
                    except Exception as e:
                        resp = {"ok": False, "error": str(e)}
                    conn.sendall((json.dumps(resp) + "\n").encode())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        print(f"[rpc] Listening on {host}:{port} (LAN hint: {get_lan_ip_guess()}:{port}) | ops={list(FUNCTIONS)}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle, args=(conn, addr), daemon=True).start()


# ---------- DEMO 4: UDP time server/client ----------

def demo_udp_time_server(host: str, port: int) -> None:
    """
    UDP server that replies with the current UNIX timestamp.

    THEORY:
    - SOCK_DGRAM -> UDP.
    - No handshake; each recvfrom() gives you data and sender address.
    - You reply with sendto().

    TODOs:
    - Send a human‑readable time string.
    - Add basic packet loss simulation (drop every Nth packet) to illustrate unreliability.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        print(f"[udp_server] Listening on {host}:{port} (LAN hint: {get_lan_ip_guess()}:{port})")
        while True:
            data, addr = s.recvfrom(512)
            print(f"[udp_server] from {addr} -> {data!r}")
            s.sendto(str(time.time()).encode(), addr)


def demo_udp_time_client(host: str, port: int) -> None:
    """
    UDP client that asks the server for the time and prints it.

    TODOs:
    - Measure round‑trip time (RTT) by timing send/recv.
    - Try sending multiple requests quickly; observe unordered arrival.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2.0)
        s.sendto(b"time?", (host, port))
        try:
            data, _ = s.recvfrom(512)
            print(f"[udp_client] server time: {data.decode()}")
        except socket.timeout:
            print("[udp_client] timed out waiting for reply")


# ---------- DEMO 5: HTTP by hand over raw TCP ----------

def demo_http_by_hand(host: str, port: int, path: str) -> None:
    """
    Open a TCP socket, send a minimal HTTP/1.1 GET request, print the response head.

    THEORY:
    - Browsers and libraries usually do this for you, but it's just text over TCP.
    - Required header: Host: <domain>
    """
    request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
    with socket.create_connection((host, port), timeout=5) as s:
        s.sendall(request.encode())
        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
    head = response.split(b"\r\n\r\n", 1)[0]
    print(head.decode(errors="replace"))

    # TODOs:
    # - Parse the status code and headers into a dict.
    # - Save the body to a file when status is 200 OK.


# ---------- DEMO 6: Flask LAN Guessing Game ----------

def demo_guess_game(host: str, port: int) -> None:
    """
    A light web app you can hit from your phone/laptop on the same LAN.
    You'll submit a guess; when host clicks REVEAL, the app shows who was closest.

    NOTE: Requires Flask. If missing, pip install flask

    THEORY:
    - Shows how HTTP sits atop TCP (we use a framework so you don't hand‑roll routing).
    - Demonstrates shared state and locking for thread safety.
    """
    try:
        from flask import Flask, request, redirect, render_template_string
    except Exception as e:
        print("[guess_game] Flask is required. Run: pip install flask")
        print(f"Import error: {e}")
        return

    app = Flask(__name__)
    lock = threading.Lock()
    state = {
        "target": _new_target(),
        "revealed": False,
        "guesses": {},  # name/ip -> int
    }

    PAGE = """
    <!doctype html>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LAN Guessing Game</title>
    <style>
      body { font-family: system-ui, sans-serif; max-width: 700px; margin: 2rem auto; padding: 0 1rem; }
      h1,h2 { margin: 0.2rem 0 0.8rem }
      form { margin-bottom: 1rem }
      input, button { font-size: 1rem; padding: 0.4rem 0.6rem; }
      ol { padding-left: 1.2rem }
      .muted { color: #555 }
    </style>
    <h1>Guess the number (1–100)</h1>
    <p class="muted">Connected from: {{ ip }}</p>
    {% if not revealed %}
      <form method="POST" action="/guess">
        <label>Your name: <input name="name" required></label>
        <label>Your guess: <input name="guess" type="number" min="1" max="100" required></label>
        <button type="submit">Submit</button>
      </form>
      <p>{{ status }}</p>
    {% else %}
      <h2>Revealed number: {{ target }}</h2>
      <ol>
      {% for row in ranking %}
        <li>{{ row[0] }} — guessed {{ row[1] }} (Δ={{ row[2] }})</li>
      {% endfor %}
      </ol>
    {% endif %}

    <hr>
    <form method="POST" action="/reveal">
      <button type="submit">Reveal (teacher)</button>
    </form>
    <form method="POST" action="/reset">
      <button type="submit">Reset game (teacher)</button>
    </form>
    """

    def user_name(req) -> str:
        name = (req.form.get("name") or "").strip()
        if not name:
            # Use IP as fallback id
            name = req.headers.get("X-Forwarded-For", req.remote_addr or "?")
        return name

    @app.route("/", methods=["GET"])
    def index():
        with lock:
            ip = request.headers.get("X-Forwarded-For", request.remote_addr or "?")
            status = f"{len(state['guesses'])} guesses so far."
            if state["revealed"]:
                ranking = sorted(
                    [(k, v, abs(v - state["target"])) for k, v in state["guesses"].items()],
                    key=lambda x: x[2]
                )
                return render_template_string(
                    PAGE, revealed=True, target=state["target"], ranking=ranking, ip=ip
                )
            return render_template_string(
                PAGE, revealed=False, status=status, ip=ip
            )

    @app.route("/guess", methods=["POST"])
    def guess():
        try:
            g = int(request.form["guess"])
            if not (1 <= g <= 100):
                raise ValueError
        except Exception:
            return redirect("/")
        name = user_name(request)
        with lock:
            state["guesses"][name] = g
        return redirect("/")

    @app.route("/reveal", methods=["POST"])
    def reveal():
        # Allow only requests originating from the same machine (localhost)
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return "Forbidden: admin action allowed only from localhost", 403
        with lock:
            state["revealed"] = True
        return redirect("/")

    @app.route("/reset", methods=["POST"])
    def reset():
        # Allow only requests originating from the same machine (localhost)
        if request.remote_addr not in ("127.0.0.1", "::1"):
            return "Forbidden: admin action allowed only from localhost", 403
        with lock:
            state["target"] = _new_target()
            state["revealed"] = False
            state["guesses"].clear()
        return redirect("/")

    print(f"[guess_game] Open http://{get_lan_ip_guess()}:{port}/ on devices in your LAN")
    app.run(host=host, port=port, debug=False)


def _new_target() -> int:
    # Local import to avoid relying on secrets module at top-level if not needed
    import random
    return random.randint(1, 100)


# ---------- Stretch: selectors/asyncio pointers (theory only) ----------
# THEORY:
# For many concurrent clients, threads can become heavy. Two scalable options:
# 1) selectors module: multiplex sockets in one thread by reacting to readiness events.
# 2) asyncio: high-level, single-threaded cooperative multitasking using await/async def.



# ---------- Exercise Bank ----------

EXERCISES = r"""
EXERCISE A — Echo client loop
- Turn demo_echo_client into a loop: read from input(), send to server, print reply, until 'quit'.

EXERCISE B — Timeouts
- Add sock.settimeout(2) to the echo client. Handle socket.timeout and show a friendly message.

EXERCISE C — UDP “ping” RTT
- Modify UDP client to send N requests quickly, time each round-trip, and compute min/avg/max.

EXERCISE D — Concurrent echo features
- Add a counter per client and include it in the echoed message: "[#3] you said ..."
- Add a cap: after 100 messages, politely close the connection.

EXERCISE E — JSON-RPC ops & validation
- Add "pow" (a**b) but only accept integers 0..10 to avoid huge numbers.
- Return {"ok":False,"error":"..."} for invalid inputs with clear messages.

EXERCISE F — HTTP by hand (headers/body)
- Parse headers into a dict. If Content-Length exists, read exactly that many bytes.
- Save the body to 'download.bin' when status is 200.

EXERCISE G — Guessing game enhancements
- Add per‑person latest guess time and show a "fastest correct guess" ribbon.
- Prevent duplicate names by appending a suffix or using IP as a stable key.
- Add input rate limiting (e.g., ignore guesses faster than 1/sec per IP).
"""


# ---------- CLI glue ----------

@dataclass
class Args:
    demo: str
    host: str = "0.0.0.0"
    port: int = 5000
    message: str = "hello"
    path: str = "/"


def parse_args(argv) -> Args:
    p = argparse.ArgumentParser(description="Networking in Python — one‑file lesson & demos")
    p.add_argument("--demo", required=True, choices=[
        "echo_server",
        "echo_client",
        "echo_server_threads",
        "rpc_server",
        "udp_time_server",
        "udp_time_client",
        "http_by_hand",
        "guess_game",
        "print_exercises",
    ], help="Which demo to run")
    p.add_argument("--host", default="0.0.0.0", help="Host/IP to bind/connect")
    p.add_argument("--port", type=int, default=5000, help="Port number")
    p.add_argument("--message", default="hello", help="Message for echo_client")
    p.add_argument("--path", default="/", help="Path for http_by_hand")
    ns = p.parse_args(argv)
    return Args(**vars(ns))


def main(argv=None) -> None:
    args = parse_args(argv or sys.argv[1:])
    if args.demo == "echo_server":
        demo_echo_server(args.host, args.port)
    elif args.demo == "echo_client":
        demo_echo_client(args.host, args.port, args.message)
    elif args.demo == "echo_server_threads":
        demo_echo_server_threads(args.host, args.port)
    elif args.demo == "rpc_server":
        demo_rpc_server(args.host, args.port)
    elif args.demo == "udp_time_server":
        demo_udp_time_server(args.host, args.port)
    elif args.demo == "udp_time_client":
        demo_udp_time_client(args.host, args.port)
    elif args.demo == "http_by_hand":
        demo_http_by_hand(args.host, args.port, args.path)
    elif args.demo == "guess_game":
        demo_guess_game(args.host, args.port)
    elif args.demo == "print_exercises":
        print(EXERCISES)
    else:
        raise SystemExit("Unknown demo")

if __name__ == "__main__":
    main()
