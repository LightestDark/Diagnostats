# Diagnostats
# Windows System Diagnostic Tool

## Overview
A comprehensive Python tool that analyzes Windows systems and generates detailed health reports. It examines hardware, software, performance, and security status to help identify potential issues.

## Quick Start
1. Save the script as `diagnostic.py`
2. Run: `python diagnostic.py`
3. Follow prompts to generate report

## What It Checks
- **System Info**: Windows version, architecture, uptime
- **Hardware**: CPU, RAM, disks, GPU
- **Performance**: CPU/RAM usage, disk space, running processes
- **Network**: Adapters, IP addresses, traffic stats
- **Security**: Antivirus, firewall, updates, user accounts
- **Services**: Windows service status

## Output
- **Console Summary**: Quick overview with status indicators
- **Detailed Report**: Complete text file with all findings
- **Recommendations**: Actionable advice based on system state

## Requirements
- Windows 7+
- Python 3.6+
- Optional: Run as admin for full functionality

## Dependencies (Auto-installed)
- psutil
- wmi
- tabulate
- py-cpuinfo
- GPUtil

## Features
- Auto-installs missing packages
- Graceful error handling
- Read-only operation (no system changes)
- Fallback methods when admin access unavailable
- Timestamped report files

## Usage Notes
- Some features require administrator privileges
- Reports saved as text files in current directory
- First run may take longer due to package installation
- GPU detection optional

## Troubleshooting
If you get import errors:
1. Ensure Python is properly installed
2. Try: `pip install setuptools`
3. Or use the simplified version included

## Security
- Tool only reads system information
- No data transmitted externally
- Reports stored locally only
