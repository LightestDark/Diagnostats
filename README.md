# Diagnostats
# Windows System Diagnostic Tool


# Change Log

 Version 1.3
- Made the whole program look much better with a clean, easy-to-use graphical interface. Now you can see all your system information in organized tabs, watch the scan progress in real time, and the program will automatically install anything it needs to run properly.

 Version 1.2
- Added the ability to save detailed reports as text files so you can share them or keep them for later. Also improved security checking to tell you if your antivirus, firewall, and remote desktop are turned on or off.

 Version 1.1
- Now shows you how your computer is performing right now - how hard your processor is working, how much memory you're using, and how fast your disks are reading and writing. Also checks your network connections and internet activity.

Version 1.0
- First version that checks your computer's basic information: what Windows version you have, what hardware is inside, how long since your last restart, how much storage space you have left, and what your processor and memory look like.

## Overview
A comprehensive Python tool that analyzes Windows systems and generates detailed health reports. It examines hardware, software, performance, and security status to help identify potential issues.

 Quick Start
1. Save the script as `diagnostic.py`
2. Run: `python diagnostic.py`
3. Follow prompts to generate report

 What It Checks
- System Info: Windows version, architecture, uptime
- Hardware: CPU, RAM, disks, GPU
- Performance: CPU/RAM usage, disk space, running processes
- Network: Adapters, IP addresses, traffic stats
- Security: Antivirus, firewall, updates, user accounts
- Services: Windows service status

 Output
- Console Summary: Quick overview with status indicators
- **Detailed Report**: Complete text file with all findings
- Recommendations: Actionable advice based on system state

 Requirements
- Windows 7+
- Python 3.6+
- Optional: Run as admin for full functionality

## Dependencies (Auto-installed)
- psutil
- wmi
- tabulate
- py-cpuinfo
- GPUtil

 Features
- Auto-installs missing package
- Read-only operation (no system changes)
- Timestamped report files

## Usage Notes
- Some features require administrator privileges


## Troubleshooting
If you get import errors:
1. Ensure Python is properly installed
2. Try: `pip install setuptools`


## Security
- Tool only reads system information
- No data transmitted externally
- Reports stored locally only
