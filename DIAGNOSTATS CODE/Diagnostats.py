import os
import sys
import platform
import subprocess
import datetime
import socket
import time

class SimpleWindowsDiagnostic:
    def __init__(self):
        self.info = {}
    
    def run(self):
        """Run simple diagnostics"""
        print("\n" + "=" * 60)
        print("SIMPLE WINDOWS DIAGNOSTIC TOOL")
        print("=" * 60)
        
        self.get_system_info()
        self.get_disk_info()
        self.get_network_info()
        self.get_running_processes()
        
        self.display_report()
    
    def get_system_info(self):
        """Get basic system information"""
        print("Collecting system information...")
        
        self.info['OS'] = f"{platform.system()} {platform.release()}"
        self.info['Version'] = platform.version()
        self.info['Hostname'] = socket.gethostname()
        self.info['Architecture'] = platform.architecture()[0]
        self.info['Processor'] = platform.processor()
        
        try:
            self.info['IP Address'] = socket.gethostbyname(socket.gethostname())
        except:
            self.info['IP Address'] = "Not available"
        
        # Get memory info using wmic
        try:
            result = subprocess.run(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'], 
                                  capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                memory_bytes = int(lines[1].strip())
                self.info['Total RAM'] = f"{memory_bytes / (1024**3):.2f} GB"
        except:
            self.info['Total RAM'] = "Unknown"
    
    def get_disk_info(self):
        """Get disk information"""
        print("Collecting disk information...")
        
        self.info['Disks'] = []
        
        # Get drives using wmic
        try:
            result = subprocess.run(['wmic', 'logicaldisk', 'get', 'size,freespace,caption'], 
                                  capture_output=True, text=True, timeout=10)
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # Skip header
                parts = line.strip().split()
                if len(parts) >= 3:
                    drive = parts[0]
                    try:
                        free = int(parts[1])
                        total = int(parts[2])
                        used = total - free
                        usage_percent = (used / total) * 100 if total > 0 else 0
                        
                        disk_info = {
                            'Drive': drive,
                            'Total': f"{total / (1024**3):.2f} GB",
                            'Free': f"{free / (1024**3):.2f} GB",
                            'Used': f"{used / (1024**3):.2f} GB",
                            'Usage': f"{usage_percent:.1f}%"
                        }
                        self.info['Disks'].append(disk_info)
                    except:
                        continue
        except:
            self.info['Disks'] = [{'Error': 'Could not retrieve disk information'}]
    
    def get_network_info(self):
        """Get network information"""
        print("Collecting network information...")
        
        self.info['Network'] = []
        
        try:
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, timeout=10)
            lines = result.stdout.split('\n')
            
            current_adapter = ""
            for line in lines:
                line = line.strip()
                if line and not line.startswith('.'):
                    if 'adapter' in line.lower():
                        current_adapter = line.replace(':', '')
                    elif 'IPv4 Address' in line or 'IP Address' in line:
                        ip = line.split(':')[-1].strip()
                        if current_adapter and ip and ip != '':
                            self.info['Network'].append({
                                'Adapter': current_adapter,
                                'IP Address': ip
                            })
        except:
            self.info['Network'] = [{'Error': 'Could not retrieve network information'}]
    
    def get_running_processes(self):
        """Get running processes"""
        print("Collecting process information...")
        
        self.info['Processes'] = []
        
        try:
            result = subprocess.run(['tasklist', '/FO', 'CSV'], capture_output=True, text=True, timeout=10)
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for i, line in enumerate(lines[:15]):  # Get first 15 processes
                try:
                    # Simple CSV parsing
                    parts = line.split(',')
                    if len(parts) >= 5:
                        name = parts[0].strip('"')
                        pid = parts[1].strip('"')
                        memory = parts[4].strip('"')
                        
                        self.info['Processes'].append({
                            'Name': name[:30],
                            'PID': pid,
                            'Memory': memory
                        })
                except:
                    continue
        except:
            self.info['Processes'] = [{'Error': 'Could not retrieve process information'}]
    
    def display_report(self):
        """Display the diagnostic report"""
        print("\n" + "=" * 60)
        print("DIAGNOSTIC REPORT")
        print("=" * 60)
        print(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # System Info
        print("\n[SYSTEM INFORMATION]")
        for key, value in self.info.items():
            if key not in ['Disks', 'Network', 'Processes']:
                print(f"  {key}: {value}")
        
        # Disk Info
        print("\n[DISK INFORMATION]")
        if isinstance(self.info.get('Disks'), list):
            for disk in self.info['Disks']:
                if isinstance(disk, dict):
                    if 'Drive' in disk:
                        print(f"  Drive {disk['Drive']}:")
                        print(f"    Total: {disk.get('Total', 'N/A')}")
                        print(f"    Free: {disk.get('Free', 'N/A')}")
                        print(f"    Used: {disk.get('Used', 'N/A')}")
                        print(f"    Usage: {disk.get('Usage', 'N/A')}")
        
        # Network Info
        print("\n[NETWORK INFORMATION]")
        if isinstance(self.info.get('Network'), list):
            for net in self.info['Network']:
                if isinstance(net, dict):
                    if 'Adapter' in net:
                        print(f"  {net['Adapter']}:")
                        print(f"    IP Address: {net.get('IP Address', 'N/A')}")
        
        # Processes
        print("\n[RUNNING PROCESSES (first 15)]")
        if isinstance(self.info.get('Processes'), list):
            for proc in self.info['Processes']:
                if isinstance(proc, dict):
                    if 'Name' in proc:
                        print(f"  {proc.get('Name', 'N/A')} (PID: {proc.get('PID', 'N/A')}) - Memory: {proc.get('Memory', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("END OF REPORT")
        print("=" * 60)
        
        # Save to file
        filename = f"simple_diagnostic_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, 'w') as f:
                f.write("SIMPLE WINDOWS DIAGNOSTIC REPORT\n")
                f.write("=" * 50 + "\n")
                for section, data in self.info.items():
                    f.write(f"\n[{section.upper()}]\n")
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                for k, v in item.items():
                                    f.write(f"  {k}: {v}\n")
                            else:
                                f.write(f"  {item}\n")
                    else:
                        f.write(f"  {data}\n")
            
            print(f"\nReport saved to: {filename}")
            open_file = input("\nOpen report file? (y/n): ").lower()
            if open_file == 'y':
                os.startfile(filename)
        except Exception as e:
            print(f"Could not save report: {e}")
        
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    if platform.system() != "Windows":
        print("Error: This tool is for Windows only.")
        sys.exit(1)
    
    tool = SimpleWindowsDiagnostic()
    tool.run()
