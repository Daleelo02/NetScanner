#!/usr/bin/env python3
"""
NetScanner - Backend Flask
Scanner réseau local avec ping, ARP, DNS, ports TCP
"""

import subprocess
import socket
import threading
import json
import re
import ipaddress
import time
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

IS_WINDOWS = platform.system() == "Windows"

# Ports communs à scanner
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 135: "RPC",
    139: "NetBIOS", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5900: "VNC", 8080: "HTTP-Alt",
    8443: "HTTPS-Alt", 9100: "Imprimante"
}


def ping_host(ip: str, timeout: float = 1.0) -> bool:
    """Ping un hôte, retourne True si répond."""
    try:
        if IS_WINDOWS:
            cmd = ["ping", "-n", "1", "-w", str(int(timeout * 1000)), str(ip)]
        else:
            cmd = ["ping", "-c", "1", "-W", str(int(timeout)), str(ip)]
        result = subprocess.run(cmd, capture_output=True, timeout=timeout + 1)
        return result.returncode == 0
    except Exception:
        return False


def get_mac_address(ip: str) -> str:
    """Récupère l'adresse MAC via ARP."""
    try:
        if IS_WINDOWS:
            result = subprocess.run(["arp", "-a", str(ip)], capture_output=True, text=True, timeout=3)
            match = re.search(r'([0-9a-f]{2}[-:][0-9a-f]{2}[-:][0-9a-f]{2}[-:][0-9a-f]{2}[-:][0-9a-f]{2}[-:][0-9a-f]{2})', result.stdout, re.IGNORECASE)
        else:
            result = subprocess.run(["arp", "-n", str(ip)], capture_output=True, text=True, timeout=3)
            match = re.search(r'([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})', result.stdout, re.IGNORECASE)
        return match.group(1).upper() if match else "N/A"
    except Exception:
        return "N/A"


def get_hostname(ip: str) -> str:
    """Résolution DNS inverse."""
    try:
        return socket.gethostbyaddr(str(ip))[0]
    except Exception:
        return ""


def scan_ports(ip: str, timeout: float = 0.5) -> list:
    """Scanne les ports communs, retourne la liste des ouverts."""
    open_ports = []
    for port, service in COMMON_PORTS.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            if sock.connect_ex((str(ip), port)) == 0:
                open_ports.append({"port": port, "service": service})
            sock.close()
        except Exception:
            pass
    return open_ports


def scan_single_host(ip: str, timeout: float, scan_ports_flag: bool) -> dict | None:
    """Scanne un hôte complet. Retourne None si hors ligne."""
    if not ping_host(ip, timeout):
        return None

    host = {
        "ip": str(ip),
        "mac": get_mac_address(str(ip)),
        "hostname": get_hostname(str(ip)),
        "ports": [],
        "status": "online",
        "scan_time": time.strftime("%H:%M:%S")
    }

    if scan_ports_flag:
        host["ports"] = scan_ports(str(ip))

    return host


@app.route("/api/status")
def status():
    return jsonify({"status": "running", "platform": platform.system(), "version": "2.0"})


@app.route("/api/local-ip")
def local_ip():
    """Retourne l'IP locale et suggère une plage."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        # Suggère la plage /24
        parts = ip.rsplit(".", 1)
        suggested = f"{parts[0]}.1-254"
        return jsonify({"local_ip": ip, "suggested_range": suggested})
    except Exception:
        return jsonify({"local_ip": "127.0.0.1", "suggested_range": "192.168.1.1-254"})


@app.route("/api/scan", methods=["POST"])
def scan():
    """Scan simple (retourne tout à la fin)."""
    data = request.json or {}
    ip_range = data.get("range", "192.168.1.1-254")
    timeout = float(data.get("timeout", 1.0))
    do_ports = data.get("ports", False)
    max_threads = int(data.get("threads", 50))

    ips = parse_ip_range(ip_range)
    if not ips:
        return jsonify({"error": "Plage IP invalide"}), 400

    results = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(scan_single_host, ip, timeout, do_ports): ip for ip in ips}
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    results.sort(key=lambda x: list(map(int, x["ip"].split("."))))
    return jsonify({"hosts": results, "total": len(results), "scanned": len(ips)})


@app.route("/api/scan/stream", methods=["POST"])
def scan_stream():
    """Scan SSE - envoie chaque hôte découvert en temps réel."""
    data = request.json or {}
    ip_range = data.get("range", "192.168.1.1-254")
    timeout = float(data.get("timeout", 1.0))
    do_ports = data.get("ports", False)
    max_threads = int(data.get("threads", 50))

    ips = parse_ip_range(ip_range)
    if not ips:
        def error_gen():
            yield f"data: {json.dumps({'error': 'Plage IP invalide'})}\n\n"
        return Response(stream_with_context(error_gen()), mimetype="text/event-stream")

    def generate():
        yield f"data: {json.dumps({'type': 'start', 'total': len(ips)})}\n\n"
        found = 0
        scanned = 0
        lock = threading.Lock()

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {executor.submit(scan_single_host, ip, timeout, do_ports): ip for ip in ips}
            for future in as_completed(futures):
                result = future.result()
                with lock:
                    scanned += 1
                    if result:
                        found += 1
                        yield f"data: {json.dumps({'type': 'host', 'host': result, 'scanned': scanned, 'found': found, 'total': len(ips)})}\n\n"
                    else:
                        yield f"data: {json.dumps({'type': 'progress', 'scanned': scanned, 'found': found, 'total': len(ips)})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'scanned': scanned, 'found': found, 'total': len(ips)})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def parse_ip_range(ip_range: str) -> list:
    """Parse une plage IP : 192.168.1.1-254 ou CIDR 192.168.1.0/24."""
    ips = []
    try:
        ip_range = ip_range.strip()
        if "/" in ip_range:
            network = ipaddress.ip_network(ip_range, strict=False)
            ips = [str(ip) for ip in network.hosts()]
        elif "-" in ip_range:
            parts = ip_range.rsplit(".", 1)
            base = parts[0]
            range_part = parts[1]
            if "-" in range_part:
                start, end = range_part.split("-")
                for i in range(int(start), int(end) + 1):
                    ips.append(f"{base}.{i}")
            else:
                ips = [ip_range]
        else:
            ips = [ip_range]
    except Exception:
        pass
    return ips


if __name__ == "__main__":
    print("=" * 50)
    print("  NetScanner Backend v2.0")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
