# WinBoat Disk Resizer

A utility tool to resize the virtual hard disk of a running [WinBoat](https://github.com/TibixDev/winboat) container on-the-fly without needing to restart it.

## Overview

WinBoat runs a Windows guest virtual machine inside a Docker/Podman container using QEMU. Usually, resizing the disk requires stopping the container, modifying the `DISK_SIZE` environment variable, restarting, and extending the filesystem.

This tool uses the **QEMU Machine Protocol (QMP)** to communicate with the active QEMU instance and dynamically resize the block device at runtime.

---

## How It Works

1. Queries Podman to discover the dynamic host port mapped to QMP (`7149`).
2. Establishes a QMP TCP session.
3. Resizes the raw/qcow2 virtual disk image on the host file system.
4. Signals the QEMU engine to notify the running Windows guest of the updated storage geometry.

---

## Prerequisites

- Python 3.x
- Podman (or Docker)
- A running WinBoat container named `WinBoat` with QMP exposed (e.g., `-qmp tcp:0.0.0.0:7149,server,wait=off` and mapped to a host port).

---

## Usage

Run the script from the command line, providing the new size as an argument (e.g., `120G`, `150G`, `500G`):

```bash
./winboat-disk-resizer.py <new_size>
```

### Example:

```bash
$ ./winboat-disk-resizer.py 500G
Current Virtual Disk Size: 100.00 GiB (107374182400 bytes)
Resizing disk to 500.00 GiB (536870912000 bytes)...
Disk resized successfully in QEMU!
```

---

## Post-Resize Steps inside Windows

Once the script completes, the additional capacity is immediately visible to the Windows guest as **Unallocated Space**. You must extend your partition within Windows to use it:

1. Connect to your Windows instance (via RDP or web interface).
2. Right-click the **Start menu** and select **Disk Management**.
3. Locate your primary `C:` partition.
4. Right-click the partition and choose **Extend Volume...**.
5. Complete the wizard to expand the partition into the unallocated space.

> [!TIP]
   Ensure you also update the `DISK_SIZE` environment variable in your `docker-compose.yml`/`podman-compose.yml` to match (e.g. `DISK_SIZE: 500G`), so that any future restarts of the container align with the new disk size.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
