import socket, threading
HOST = "0.0.0.0"
PORT = 2323
FLAG = "FLAG{tcp}"
BANNER = b"DEMO-BANNER 1.0\r\nType HELP for commands.\r\n> "
def handle(conn, addr):
    conn.sendall(BANNER)
    try:
        while True:
            data = conn.recv(1024)
            if not data: break
            cmd = data.strip().upper()
            if cmd == b"HELP":
                conn.sendall(b"Commands: HELP, HELLO, FLAG\r\n> ")
            elif cmd == b"HELLO":
                conn.sendall(b"Hello there.\r\n> ")
            elif cmd == b"FLAG":
                conn.sendall(FLAG.encode() + b"\r\n> ")
            else:
                conn.sendall(b"Unknown command.\r\n> ")
    finally:
        conn.close()
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"Listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
if __name__ == "__main__":
    main()
