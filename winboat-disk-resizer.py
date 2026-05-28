#!/usr/bin/env python3
import sys
import socket
import json
import re
import subprocess

def get_qmp_address():
    try:
        out = subprocess.check_output(["podman", "port", "WinBoat", "7149"], stderr=subprocess.DEVNULL).decode().strip()
        host, port = out.split(":")
        return host, int(port)
    except Exception:
        print("Error: Could not retrieve QMP port. Is the WinBoat container running?")
        sys.exit(1)

def send_qmp_commands(host, port, commands):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    try:
        s.connect((host, port))
    except Exception as e:
        print(f"Error: Failed to connect to QMP at {host}:{port}: {e}")
        sys.exit(1)

    # Read greeting
    greeting = s.recv(4096)
    
    # Negotiate capabilities
    s.sendall(b'{"execute": "qmp_capabilities"}\n')
    capabilities_resp = json.loads(s.recv(4096).decode())
    if "error" in capabilities_resp:
        print("Error during QMP capabilities negotiation:", capabilities_resp["error"])
        s.close()
        sys.exit(1)

    responses = []
    for cmd in commands:
        s.sendall(json.dumps(cmd).encode() + b'\n')
        resp = b""
        while True:
            chunk = s.recv(4096)
            resp += chunk
            if len(chunk) < 4096:
                break
        responses.append(json.loads(resp.decode()))
    
    s.close()
    return responses

def parse_size(size_str):
    m = re.match(r'^(\d+(?:\.\d+)?)\s*([a-zA-Z]*)$', size_str.strip())
    if not m:
        raise ValueError(f"Invalid size format: {size_str}")
    val = float(m.group(1))
    unit = m.group(2).upper()
    if unit in ("", "B", "BYTE", "BYTES"):
        return int(val)
    elif unit in ("K", "KB", "KIB"):
        return int(val * 1024)
    elif unit in ("M", "MB", "MIB"):
        return int(val * 1024**2)
    elif unit in ("G", "GB", "GIB"):
        return int(val * 1024**3)
    elif unit in ("T", "TB", "TIB"):
        return int(val * 1024**4)
    else:
        raise ValueError(f"Unknown unit: {unit}")

def format_bytes(size_bytes):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PiB"

def main():
    host, port = get_qmp_address()

    # First, query current block devices
    responses = send_qmp_commands(host, port, [{"execute": "query-block"}])
    block_devices = responses[0].get("return", [])
    
    data_dev = None
    for dev in block_devices:
        if dev.get("device") == "data3":
            data_dev = dev
            break
            
    if not data_dev:
        print("Error: Could not find disk device 'data3' in the running VM.")
        sys.exit(1)
        
    current_size = data_dev["inserted"]["image"]["virtual-size"]
    print(f"Current Virtual Disk Size: {format_bytes(current_size)} ({current_size} bytes)")

    if len(sys.argv) < 2:
        print("\nUsage: ./winboat-disk-resizer.py <new_size>")
        print("Example: ./winboat-disk-resizer.py 120G")
        return

    new_size_str = sys.argv[1]
    try:
        new_size_bytes = parse_size(new_size_str)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    if new_size_bytes <= current_size:
        print(f"Error: New size ({format_bytes(new_size_bytes)}) must be larger than current size ({format_bytes(current_size)}).")
        sys.exit(1)

    print(f"Resizing disk to {format_bytes(new_size_bytes)} ({new_size_bytes} bytes)...")
    
    resize_cmd = {
        "execute": "block_resize",
        "arguments": {
            "device": "data3",
            "size": new_size_bytes
        }
    }
    
    responses = send_qmp_commands(host, port, [resize_cmd])
    result = responses[0]
    
    if "error" in result:
        print("Error resizing disk:", result["error"])
        sys.exit(1)
        
    print("Disk resized successfully in QEMU!")
    print("\nNext steps:")
    print("1. Connect to your Windows instance via Web interface or RDP.")
    print("2. Open 'Disk Management' (right-click the Start menu and select 'Disk Management').")
    print("3. Locate the 'C:' partition, right-click it, and select 'Extend Volume'.")
    print("4. Follow the wizard to allocate the newly available unallocated space.")

if __name__ == "__main__":
    main()
