#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HGLRC C1 Type-C recovery helper for Windows.

What it does:
1) Detects CH340/CH341 serial ports.
2) Lets you select the C1 COM port.
3) Backs up the entire 4MB ESP32 flash.
4) Keeps the ESP32 stub bootloader active after backup.
5) Writes the C1 stock application image to 0x10000.
6) Verifies the flashed image, then resets the ESP32 normally.

Safety:
- Does NOT run erase_flash / erase-flash.
- Does NOT write the stock application image to 0x0.
- Requires the firmware file to exist in stock/ next to this script.
"""

from __future__ import annotations

import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

FIRMWARE_REL = Path("stock") / "HGLRC-C1_DRAGON-V2.0_community-stock-dump.bin"
FLASH_SIZE = "0x400000"  # 4 MiB
APP_OFFSET = "0x10000"
BAUD = "460800"


def die(msg: str, code: int = 1) -> None:
    print(f"\n[ERROR] {msg}")
    input("\nPress Enter to exit...")
    raise SystemExit(code)


def run(cmd: list[str], check: bool = True) -> int:
    print("\n> " + " ".join(cmd))
    p = subprocess.run(cmd)
    if check and p.returncode != 0:
        die(f"Command failed with exit code {p.returncode}")
    return p.returncode


def ensure_dependencies() -> None:
    missing = []
    try:
        import serial  # noqa: F401
    except Exception:
        missing.append("pyserial")
    try:
        import esptool  # noqa: F401
    except Exception:
        missing.append("esptool")

    if missing:
        print("Missing Python packages: " + ", ".join(missing))
        ans = input("Install them now with pip? [Y/n]: ").strip().lower()
        if ans in ("", "y", "yes"):
            run([sys.executable, "-m", "pip", "install", "-U", *missing])
        else:
            die("Required packages are not installed.")


def detect_ports():
    from serial.tools import list_ports

    ports = list(list_ports.comports())
    ch_ports = []
    for p in ports:
        text = " ".join(
            str(x or "") for x in [p.device, p.description, p.manufacturer, p.hwid]
        ).lower()
        if any(k in text for k in ["ch340", "ch341", "wch", "usb-serial"]):
            ch_ports.append(p)
    return ports, ch_ports


def choose_port() -> str:
    ports, ch_ports = detect_ports()

    if not ports:
        die("No serial ports found. Reconnect the C1 Type-C cable and try again.")

    print("\nDetected serial ports:")
    for i, p in enumerate(ports, 1):
        mark = "  <== likely C1/CH340" if p in ch_ports else ""
        print(f"  {i}. {p.device:8}  {p.description}{mark}")

    if len(ch_ports) == 1:
        port = ch_ports[0].device
        ans = input(f"\nUse detected CH340 port {port}? [Y/n]: ").strip().lower()
        if ans in ("", "y", "yes"):
            return port

    raw = input("\nEnter the C1 COM port, e.g. COM6: ").strip().upper()
    if not raw.startswith("COM"):
        die("Invalid COM port name.")
    return raw


def main() -> None:
    os.system("title HGLRC C1 Type-C Recovery")
    base = Path(__file__).resolve().parent
    firmware = base / FIRMWARE_REL

    print("=" * 62)
    print(" HGLRC C1 Type-C Recovery Tool")
    print(" Backup 4MB -> keep stub active -> flash at 0x10000 -> verify")
    print("=" * 62)
    print("\nWARNING:")
    print("- This stock image is a community dump from a DRAGON_V2.0 C1.")
    print("- It is not an official HGLRC release package.")
    print("- Do not disconnect USB while backup/flashing is in progress.")
    print("- This tool does NOT erase the whole flash.")

    if not firmware.exists():
        die(f"Firmware not found: {firmware}")

    ensure_dependencies()
    port = choose_port()

    print(f"\nSelected port: {port}")
    print(f"Firmware: {firmware.name}")

    ans = input("\nRun ESP32 chip-id test first? [Y/n]: ").strip().lower()
    if ans in ("", "y", "yes"):
        run([
            sys.executable, "-m", "esptool",
            "--port", port,
            "--after", "no-reset",
            "chip-id",
        ])

    backup_dir = base / "backups"
    backup_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"C1_fullflash_{port}_{stamp}.bin"

    print("\nStep 1/3: backing up the entire 4MB flash...")
    run([
        sys.executable, "-m", "esptool",
        "--port", port,
        "--baud", BAUD,
        "--after", "no-reset-stub",
        "read-flash", "0x0", FLASH_SIZE,
        str(backup),
    ])

    if not backup.exists() or backup.stat().st_size != 0x400000:
        die("Backup size is not exactly 4MB. Flashing has been cancelled.")

    print(f"\nBackup OK: {backup}")
    print("ESP32 stub has been intentionally left active for the next step.")
    confirm = input(
        "\nStep 2/3 will write the stock application image to 0x10000.\n"
        "Type FLASH to continue: "
    ).strip().upper()
    if confirm != "FLASH":
        die("Cancelled by user.", 0)

    print("\nStep 2/3: flashing stock image to 0x10000...")
    run([
        sys.executable, "-m", "esptool",
        "--port", port,
        "--baud", BAUD,
        "--before", "no-reset-no-sync",
        "--after", "no-reset-stub",
        "write-flash", APP_OFFSET,
        str(firmware),
    ])

    print("\nStep 3/3: verifying flashed image...")
    run([
        sys.executable, "-m", "esptool",
        "--port", port,
        "--before", "no-reset-no-sync",
        "--after", "hard-reset",
        "verify-flash", APP_OFFSET,
        str(firmware),
    ])

    print("\n" + "=" * 62)
    print(" FLASH + VERIFY SUCCESS")
    print("=" * 62)
    print(f"Backup saved at: {backup}")
    print("\nNext:")
    print("1) Disconnect Type-C.")
    print("2) Power off the C1 for a few seconds.")
    print("3) Power it on normally.")
    print("4) Test sticks/buttons first, then ELRS Wi-Fi/binding.")
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
