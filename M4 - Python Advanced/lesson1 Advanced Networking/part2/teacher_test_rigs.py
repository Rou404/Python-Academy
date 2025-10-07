"""
TEACHER TEST RIGS — Text-only protocols to validate student exercises
Run these on your machine; students run the complementary parts from student_skeleton.py.
All defaults bind to 0.0.0.0 for LAN access; change host to your LAN IP if desired.
"""

from __future__ import annotations
import argparse, socket, json, random

# ---------- Utilities ----------
def get_lan_ip_guess():
    try:
        import socket as _s
        with _s.socket(_s.AF_INET, _s.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

# ---------- Ex1: Teacher server (TCP Fib challenge) ----------

def server_tcp_fib(host: str, port: int) -> None:
    def fib_mod(n: int,) -> int:
        a, b = 0, 1
        for _ in range(n):
            a, b = b, (a + b)
        return a

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port)); s.listen()
        print(f"[FibSrv] Listening on {host}:{port} (LAN hint: {get_lan_ip_guess()}:{port})")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"[FibSrv] {addr} connected")
                n = random.randint(20, 30)
                conn.sendall(f"N={n}\n".encode())
                # read answer line
                buf = bytearray()
                while True:
                    ch = conn.recv(1)
                    if not ch or ch == b"\n":
                        break
                    buf.extend(ch)
                try:
                    val = int(bytes(buf).decode().strip() or "-1")
                    ok = (val == fib_mod(n))
                    conn.sendall(b"OK\n" if ok else b"ERR\n")
                    print(f"[FibSrv] N={n} got={val} -> {'OK' if ok else 'ERR'}")
                except ValueError:
                    conn.sendall(b"ERR\n")

# ---------- Ex2: Teacher server (UDP affine, TEXT) ----------

def server_udp_affine(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        print(f"[AffSrv] UDP on {host}:{port} (LAN hint: {get_lan_ip_guess()}:{port})")
        while True:
            data, addr = s.recvfrom(1024)
            try:
                txt = data.decode().strip()
                # Expect: "ID <id> X <x>"
                parts = txt.split()
                if len(parts) != 4 or parts[0].upper() != "ID" or parts[2].upper() != "X":
                    continue
                _id = int(parts[1]); x = int(parts[3])
                y = (3 * (x & 0xFFFFFFFF) + 1) & 0xFFFFFFFF
                reply = f"ID {_id} Y {y}\n".encode()
                s.sendto(reply, addr)
                print(f"[AffSrv] {addr} id={_id} x={x} -> y={y}")
            except Exception:
                # ignore malformed
                pass

# ---------- Ex3: Teacher client (TCP WordCount, TEXT terminator) ----------

def client_tcp_wordcount(host: str, port: int) -> None:
    payload_lines = [
        "To be, or not to be, that is the question:",
        "Whether 'tis nobler in the mind to suffer",
        "The slings and arrows of outrageous fortune,",
    ]
    with socket.create_connection((host, port), timeout=5) as s:
        for line in payload_lines:
            s.sendall((line + "\n").encode("utf-8"))
        s.sendall(b"---END---\n")  # terminator
        # read reply line
        buf = bytearray()
        while True:
            ch = s.recv(1)
            if not ch or ch == b"\n":
                break
            buf.extend(ch)
    print("[WordCount] reply:", bytes(buf).decode().strip())

# ---------- Ex4: Teacher client (UDP checksum) ----------

def client_udp_checksum(host: str, port: int) -> None:
    samples = [b"hello", b"networking", b"\x00\x01\x02\x03"]
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(2.0)
        for p in samples:
            s.sendto(p, (host, port))
            try:
                data, _ = s.recvfrom(128)
                print("[Checksum] sent", p, "got", data.decode().strip())
            except socket.timeout:
                print("[Checksum] timeout (no reply)")

# ---------- Ex5: Teacher RPC client (TCP) ----------

def client_tcp_rpc(host: str, port: int) -> None:
    reqs = [
        {"op":"reverse","s":"stressed"},
        {"op":"sum","xs":[1,2,3,4]},
        {"op":"uniq","xs":[1,1,2,3,3,2,4,4]},
        {"op":"oops"},  # should return ok:false
    ]
    with socket.create_connection((host, port), timeout=5) as s:
        for r in reqs:
            s.sendall((json.dumps(r) + "\n").encode())
            # read one response line
            buf = bytearray()
            while True:
                ch = s.recv(1)
                if not ch or ch == b"\n":
                    break
                buf.extend(ch)
            print("[RPC] ->", r, "| <-", bytes(buf).decode().strip())

# ---------- CLI ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", required=True, choices=[
        "server_tcp_fib","server_udp_affine","client_tcp_wordcount",
        "client_udp_checksum","client_tcp_rpc"
    ])
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=7001)
    args = ap.parse_args()

    if args.demo == "server_tcp_fib":
        server_tcp_fib(args.host, args.port)
    elif args.demo == "server_udp_affine":
        server_udp_affine(args.host, args.port)
    elif args.demo == "client_tcp_wordcount":
        client_tcp_wordcount(args.host, args.port)
    elif args.demo == "client_udp_checksum":
        client_udp_checksum(args.host, args.port)
    elif args.demo == "client_tcp_rpc":
        client_tcp_rpc(args.host, args.port)

if __name__ == "__main__":
    main()

"""
# Exercise 1 — start TCP Fib challenge (teacher = server)
python teacher_test_rigs.py --demo server_tcp_fib --host 0.0.0.0 --port 7001

# Exercise 2 — start UDP affine (teacher = server)
python teacher_test_rigs.py --demo server_udp_affine --host 0.0.0.0 --port 7002

# Exercise 3 — test student WordCount (teacher = client)
python teacher_test_rigs.py --demo client_tcp_wordcount --host <STUDENT_IP> --port 7003

# Exercise 4 — test student UDP checksum (teacher = client)
python teacher_test_rigs.py --demo client_udp_checksum --host <STUDENT_IP> --port 7004

# Exercise 5 — test student RPC server (teacher = client)
python teacher_test_rigs.py --demo client_tcp_rpc --host <STUDENT_IP> --port 7005
"""