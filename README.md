# WinBoat Disk Resizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A utility tool to resize the virtual hard disk of a running [WinBoat](https://github.com/TibixDev/winboat) container on-the-fly without needing to restart it.

---

## 📋 Prerequisites & Requirements

- **Python:** Python 3.8+
- **Container Engine:** `podman` (or `docker`)
- **WinBoat Container:** A running WinBoat container named `WinBoat` with QMP exposed (e.g., `-qmp tcp:0.0.0.0:7149,server,wait=off` mapped to host port `7149`).

Install on Arch Linux:
```bash
sudo pacman -S python podman
```

---

## ⚙️ How It Works

1. Queries Podman to discover the dynamic host port mapped to QMP (`7149`).
2. Establishes a QMP TCP session.
3. Resizes the raw/qcow2 virtual disk image on the host file system.
4. Signals the QEMU engine to notify the running Windows guest of the updated storage geometry.

---

## 🚀 Installation & Setup

### Automated Installation
```bash
git clone https://github.com/Vikyek/winboat-disk-resizer.git
cd winboat-disk-resizer
chmod +x install.sh
./install.sh
```

### Manual Installation
```bash
mkdir -p ~/.local/bin
cp winboat-disk-resizer.py ~/.local/bin/winboat-disk-resizer
chmod +x ~/.local/bin/winboat-disk-resizer
```

---

## 💻 Usage & CLI Examples

Run the script from the command line, providing the new size as an argument (e.g., `120G`, `150G`, `500G`):

```bash
# Using installed command:
winboat-disk-resizer 500G

# Or directly running the python script:
./winboat-disk-resizer.py 500G
```

### Example Output:
```bash
$ winboat-disk-resizer 500G
Current Virtual Disk Size: 100.00 GiB (107374182400 bytes)
Resizing disk to 500.00 GiB (536870912000 bytes)...
Disk resized successfully in QEMU!
```

---

## 🪟 Post-Resize Steps inside Windows

Once the script completes, the additional capacity is immediately visible to the Windows guest as **Unallocated Space**. You must extend your partition within Windows to use it:

1. Connect to your Windows instance (via RDP or web interface).
2. Right-click the **Start menu** and select **Disk Management**.
3. Locate your primary `C:` partition.
4. Right-click the partition and choose **Extend Volume...**.
5. Complete the wizard to expand the partition into the unallocated space.

> [!TIP]
> Ensure you also update the `DISK_SIZE` environment variable in your `docker-compose.yml`/`podman-compose.yml` to match (e.g. `DISK_SIZE: 500G`), so that any future restarts of the container align with the new disk size.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
