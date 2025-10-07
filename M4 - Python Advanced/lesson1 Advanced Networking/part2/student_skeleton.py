"""
STUDENT

How to use: Trainer will run a test server/client. You implement the missing parts here.

Exercises overview
------------------
1) Client (TCP) – Challenge/Response Fibonacci
   - Connect to teacher server (host/port given).
   - Protocol:
       Teacher -> You: "N=<int>\n"
       You -> Teacher: "<fib(N)\n"
       Teacher -> You: "OK\n" or "ERR\n"
   - Implement: `student_client_tcp_fib(host, port)`

2) Client (UDP) – ID math service (TEXT)
   - You send one line: "ID <id> X <x>\n"  (id and x are integers)
   - Teacher replies one line: "ID <id> Y <y>\n" where y = (3*x + 1) mod 2^32
   - Implement: `student_client_udp_affine(host, port, x)` returning y (int)

3) Server (TCP) – WordCount (TEXT with terminator)
   - You listen on a port; teacher connects and sends multiple lines of UTF-8 text
   - The final line is a terminator: "---END---\n"
   - You respond with: "words=<w>,lines=<l>,chars=<c>\n"
   - Implement: `student_server_tcp_wordcount(host, port)`

4) Server (UDP) – Simple checksum
   - You listen UDP on a port. For any datagram, compute:
       n = length of the payload
       s = sum of all byte values modulo 65536
   - Reply: "LEN=<n> SUM=<s>\n" (ASCII).
   - Implement: `student_server_udp_checksum(host, port)`

5) RPC Server (TCP) – JSON per line (same as before)
   - Newline-delimited JSON requests/response on a single TCP connection.
   - Teacher will send requests like:
       {"op":"reverse","s":"hello"}\n  -> {"ok":true,"result":"olleh"}\n
       {"op":"sum","xs":[1,2,3]}\n     -> {"ok":true,"result":6}\n
       {"op":"uniq","xs":[1,1,2,3,3]}\n-> {"ok":true,"result":[1,2,3]}\n
   - On any error, respond {"ok":false,"error":"message"}\n
   - Implement: `student_server_tcp_rpc(host, port)`

Tips
----
- For TCP line I/O, you can wrap with: f = sock.makefile("rwb", buffering=0)
- For exercise 3, read lines until you see the exact line "---END---\n".
- For UDP, use sendto/recvfrom with text (bytes).

Run this file for quick local tests:
    python student_skeleton.py --demo client_tcp_fib --host 127.0.0.1 --port 7001
    python student_skeleton.py --demo client_udp_affine --host 127.0.0.1 --port 7002 --x 42
    python student_skeleton.py --demo server_tcp_wordcount --host 0.0.0.0 --port 7003
    python student_skeleton.py --demo server_udp_checksum --host 0.0.0.0 --port 7004
    python student_skeleton.py --demo server_tcp_rpc --host 0.0.0.0 --port 7005
"""

from __future__ import annotations
import argparse, socket, json, threading, sys, random

# ---------- Helpers ----------

def recv_line(sock: socket.socket) -> bytes:
    """Read until a newline (\\n). Returns the line excluding the trailing newline."""
    buf = bytearray()
    while True:
        ch = sock.recv(1)
        if not ch:
            break
        if ch == b"\n":
            break
        buf.extend(ch)
    return bytes(buf)

# ---------- Exercise 1: Client (TCP) Fibonacci ----------

def student_client_tcp_fib(host: str, port: int) -> None:
    """
    TODO: Connect to (host, port). Read a line like: N=<int>
          Compute fib(N) (iterative).
          Send back "<number>\\n". Print the final server line.
    """
    # Your code here
    raise NotImplementedError

# ---------- Exercise 2: Client (UDP) affine transform (TEXT) ----------

def student_client_udp_affine(host: str, port: int, x: int) -> int:
    """
    TODO: Create a UDP socket. Choose a random id (or 1234).
          Send line: f"ID {id} X {x}\\n" to (host,port).
          Receive a line: "ID <id> Y <y>". Check id matches. Return y as int.
    """
    # Your code here
    raise NotImplementedError

# ---------- Exercise 3: Server (TCP) WordCount (TEXT with terminator) ----------

def student_server_tcp_wordcount(host: str, port: int) -> None:
    """
    TODO: Bind/listen. Accept ONE client, read UTF-8 lines until a line equals '---END---'.
          Compute counts and respond with: f"words={w},lines={l},chars={c}\\n"
          Then exit.
    """
    # Your code here
    raise NotImplementedError

# ---------- Exercise 4: Server (UDP) Simple checksum ----------

def student_server_udp_checksum(host: str, port: int) -> None:
    """
    TODO: Bind a UDP socket. For each datagram:
          n = len(payload); s = sum(payload) % 65536
          Reply with ASCII line: f"LEN={n} SUM={s}\\n"
          Handle forever (Ctrl+C to stop).
    """
    # Your code here
    raise NotImplementedError

# ---------- Exercise 5: Server (TCP) JSON-RPC ----------

def student_server_tcp_rpc(host: str, port: int) -> None:
    """
    TODO: Bind/listen. For EACH accepted client, handle newline-delimited JSON:
          Request forms:
            {"op":"reverse","s":"hello"}
            {"op":"sum","xs":[1,2,3]}
            {"op":"uniq","xs":[1,1,2,3,3]}
          Respond with {"ok":true,"result":...} or {"ok":false,"error":"..."} + '\\n'.
          Handle multiple clients using threads.
    """
    # Your code here
    raise NotImplementedError

# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", required=True, choices=[
        "client_tcp_fib","client_udp_affine","server_tcp_wordcount","server_udp_checksum","server_tcp_rpc"
    ])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=7001)
    ap.add_argument("--x", type=int, default=42)
    args = ap.parse_args()

    if args.demo == "client_tcp_fib":
        student_client_tcp_fib(args.host, args.port)
    elif args.demo == "client_udp_affine":
        y = student_client_udp_affine(args.host, args.port, args.x)
        print(y)
    elif args.demo == "server_tcp_wordcount":
        student_server_tcp_wordcount(args.host, args.port)
    elif args.demo == "server_udp_checksum":
        student_server_udp_checksum(args.host, args.port)
    elif args.demo == "server_tcp_rpc":
        student_server_tcp_rpc(args.host, args.port)

if __name__ == "__main__":
    main()
