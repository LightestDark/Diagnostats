# diagnostic_tool.py
import os
import sys
import platform
import subprocess
import psutil
import datetime
import socket
import winreg
import time
from tkinter import *
from tkinter import ttk, scrolledtext, messagebox, filedialog

class SimpleDiagnosticTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows Diagnostic Tool")
        self.root.geometry("1000x700")
        
        # Make window appear on top initially
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(self.root.attributes, '-topmost', False)
        
        # Set window icon (optional)
        try:
            self.root.iconbitmap(default='')
        except:
            pass
        
        # Variables
        self.is_scanning = False
        self.system_data = {}
        
        # Setup UI
        self.setup_ui()
        
        # Show welcome message
        self.show_welcome()
    
    def setup_ui(self):
        # Configure styles
        self.root.configure(bg='#f0f0f0')
        
        # Main container
        main_frame = Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = Frame(main_frame, bg='#2c3e50', height=60)
        header.pack(fill=X, pady=(0, 20))
        header.pack_propagate(False)
        
        Label(header, text="Windows System Diagnostic", 
              font=('Segoe UI', 18, 'bold'), 
              bg='#2c3e50', fg='white').pack(side=LEFT, padx=20, pady=15)
        
        # Content area
        content = Frame(main_frame, bg='#f0f0f0')
        content.pack(fill=BOTH, expand=True)
        
        # Left panel - Controls
        left_panel = Frame(content, bg='#f0f0f0', width=300)
        left_panel.pack(side=LEFT, fill=Y, padx=(0, 20))
        left_panel.pack_propagate(False)
        
        # Control buttons
        control_frame = Frame(left_panel, bg='white', relief=SOLID, borderwidth=1)
        control_frame.pack(fill=X, pady=(0, 20))
        
        Label(control_frame, text="Diagnostic Controls", 
              font=('Segoe UI', 12, 'bold'), 
              bg='#3498db', fg='white', 
              anchor='w').pack(fill=X, padx=10, pady=10)
        
        # Run button
        self.run_btn = Button(control_frame, text="Start System Scan", 
                             font=('Segoe UI', 10, 'bold'),
                             bg='#27ae60', fg='white',
                             height=2,
                             command=self.start_scan)
        self.run_btn.pack(fill=X, padx=20, pady=10)
        
        # Quick buttons
        quick_frame = Frame(control_frame, bg='white')
        quick_frame.pack(fill=X, padx=20, pady=(0, 20))
        
        Button(quick_frame, text="System Info", 
               command=self.quick_system).pack(side=LEFT, fill=X, expand=True, padx=2)
        Button(quick_frame, text="Disk Check", 
               command=self.quick_disk).pack(side=LEFT, fill=X, expand=True, padx=2)
        
        # Progress
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.pack(fill=X, padx=20, pady=(0, 10))
        
        self.status_label = Label(control_frame, text="Ready", 
                                  font=('Segoe UI', 9), bg='white')
        self.status_label.pack(fill=X, padx=20, pady=(0, 20))
        
        # Report button
        Button(control_frame, text="Generate Report", 
               command=self.generate_report,
               bg='#2980b9', fg='white').pack(fill=X, padx=20, pady=(0, 20))
        
        # System summary
        summary_frame = Frame(left_panel, bg='white', relief=SOLID, borderwidth=1)
        summary_frame.pack(fill=BOTH, expand=True)
        
        Label(summary_frame, text="System Summary", 
              font=('Segoe UI', 12, 'bold'), 
              bg='#34495e', fg='white', 
              anchor='w').pack(fill=X, padx=10, pady=10)
        
        # Summary text area
        self.summary_text = scrolledtext.ScrolledText(summary_frame, 
                                                     height=15,
                                                     font=('Consolas', 9),
                                                     wrap=WORD,
                                                     bg='white',
                                                     relief=FLAT)
        self.summary_text.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        self.summary_text.insert(END, "No scan data available.\nClick 'Start System Scan' to begin.")
        self.summary_text.config(state=DISABLED)
        
        # Right panel - Results
        right_panel = Frame(content, bg='#f0f0f0')
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Create tabs
        self.tabs = {}
        tab_names = ["System", "Performance", "Storage", "Security", "Processes"]
        
        for name in tab_names:
            frame = Frame(self.notebook, bg='white')
            self.tabs[name] = frame
            self.notebook.add(frame, text=name)
            
            # Add text widget to each tab
            text = scrolledtext.ScrolledText(frame, 
                                           font=('Consolas', 9),
                                           wrap=WORD,
                                           bg='white',
                                           relief=FLAT)
            text.pack(fill=BOTH, expand=True, padx=10, pady=10)
            text.insert(END, f"{name} information will appear here after scan.")
            text.config(state=DISABLED)
            
            # Store reference
            self.tabs[f"{name}_text"] = text
        
        # Status bar
        status_bar = Frame(self.root, bg='#34495e', height=30)
        status_bar.pack(side=BOTTOM, fill=X)
        status_bar.pack_propagate(False)
        
        self.status_msg = Label(status_bar, text="Ready", 
                               font=('Segoe UI', 9), 
                               bg='#34495e', fg='white')
        self.status_msg.pack(side=LEFT, padx=10)
        
        # Check admin status
        self.check_admin()
    
    def show_welcome(self):
        """Show welcome message"""
        welcome_text = """Welcome to Windows Diagnostic Tool

This tool will help you analyze your system's:
• Hardware specifications
• Performance metrics
• Storage usage
• Security status
• Running processes

Click 'Start System Scan' to begin."""
        
        # Show in summary
        self.summary_text.config(state=NORMAL)
        self.summary_text.delete(1.0, END)
        self.summary_text.insert(END, welcome_text)
        self.summary_text.config(state=DISABLED)
    
    def check_admin(self):
        """Check if running as administrator"""
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin:
                self.status_msg.config(text="Running as Administrator")
            else:
                self.status_msg.config(text="Standard User - Some features limited")
        except:
            pass
    
    def update_status(self, message):
        """Update status message"""
        self.status_msg.config(text=message)
        self.root.update()
    
    def update_text_widget(self, widget, text):
        """Update a text widget with new content"""
        widget.config(state=NORMAL)
        widget.delete(1.0, END)
        widget.insert(END, text)
        widget.config(state=DISABLED)
    
    def start_scan(self):
        """Start full system scan"""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.run_btn.config(state=DISABLED, text="Scanning...")
        self.progress.start()
        
        # Clear previous results
        for name in ["System", "Performance", "Storage", "Security", "Processes"]:
            self.update_text_widget(self.tabs[f"{name}_text"], f"Scanning {name.lower()}...")
        
        # Run scan in thread
        import threading
        thread = threading.Thread(target=self.run_scan_thread)
        thread.daemon = True
        thread.start()
    
    def run_scan_thread(self):
        """Thread function for scanning"""
        try:
            # Step 1: System info
            self.update_status("Collecting system information...")
            self.system_data = self.collect_system_info()
            
            # Step 2: Performance
            self.update_status("Checking performance...")
            perf_data = self.collect_performance_info()
            self.system_data.update(perf_data)
            
            # Step 3: Storage
            self.update_status("Analyzing storage...")
            disk_data = self.collect_disk_info()
            
            # Step 4: Security
            self.update_status("Checking security...")
            sec_data = self.collect_security_info()
            self.system_data.update(sec_data)
            
            # Step 5: Processes
            self.update_status("Scanning processes...")
            proc_data = self.collect_process_info()
            
            # Update UI
            self.root.after(0, self.update_scan_results, disk_data, proc_data)
            
            self.update_status("Scan complete!")
            
        except Exception as e:
            error_msg = f"Scan error: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            self.update_status("Scan failed")
        finally:
            self.root.after(0, self.scan_complete)
    
    def scan_complete(self):
        """Clean up after scan"""
        self.is_scanning = False
        self.run_btn.config(state=NORMAL, text="Start System Scan")
        self.progress.stop()
    
    def collect_system_info(self):
        """Collect basic system information"""
        data = {}
        
        try:
            # OS info
            data['OS'] = f"{platform.system()} {platform.release()}"
            data['Version'] = platform.version()
            data['Architecture'] = platform.architecture()[0]
            data['Hostname'] = socket.gethostname()
            
            # Windows edition
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                edition, _ = winreg.QueryValueEx(key, "ProductName")
                winreg.CloseKey(key)
                data['Edition'] = edition
            except:
                data['Edition'] = "Unknown"
            
            # CPU info
            data['Processor'] = platform.processor()
            data['CPU Cores'] = f"{psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical"
            
            # Memory
            mem = psutil.virtual_memory()
            data['Total RAM'] = f"{mem.total / (1024**3):.1f} GB"
            
            # Uptime
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            data['Uptime'] = str(uptime).split('.')[0]  # Remove microseconds
            
            # IP address
            try:
                data['IP Address'] = socket.gethostbyname(socket.gethostname())
            except:
                data['IP Address'] = "Not available"
                
        except Exception as e:
            data['Error'] = f"System info error: {str(e)}"
        
        return data
    
    def collect_performance_info(self):
        """Collect performance metrics"""
        data = {}
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            data['CPU Usage'] = f"{cpu_percent}%"
            
            # CPU frequency
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                data['CPU Frequency'] = f"{cpu_freq.current:.0f} MHz"
            
            # Memory usage
            mem = psutil.virtual_memory()
            data['Memory Usage'] = f"{mem.percent}%"
            data['Available RAM'] = f"{mem.available / (1024**3):.1f} GB"
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            data['Disk Read'] = f"{disk_io.read_bytes / (1024**2):.1f} MB"
            data['Disk Write'] = f"{disk_io.write_bytes / (1024**2):.1f} MB"
            
        except Exception as e:
            data['Perf Error'] = f"Performance error: {str(e)}"
        
        return data
    
    def collect_disk_info(self):
        """Collect disk information"""
        disks = []
        
        try:
            partitions = psutil.disk_partitions()
            for part in partitions:
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disk = {
                        'Device': part.device,
                        'Mount': part.mountpoint,
                        'Type': part.fstype,
                        'Total': f"{usage.total / (1024**3):.1f} GB",
                        'Used': f"{usage.used / (1024**3):.1f} GB",
                        'Free': f"{usage.free / (1024**3):.1f} GB",
                        'Percent': f"{usage.percent}%"
                    }
                    disks.append(disk)
                except:
                    continue
        except Exception as e:
            disks.append({'Error': f"Disk error: {str(e)}"})
        
        return disks
    
    def collect_security_info(self):
        """Collect security information"""
        data = {}
        
        try:
            # Windows Defender
            try:
                result = subprocess.run(['powershell', '-Command', 
                                       'Get-MpComputerStatus | Select-Object -ExpandProperty AntivirusEnabled'],
                                      capture_output=True, text=True, timeout=5)
                data['Windows Defender'] = "Enabled" if 'True' in result.stdout else "Disabled"
            except:
                data['Windows Defender'] = "Unknown"
            
            # Firewall
            try:
                result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles'],
                                      capture_output=True, text=True, timeout=5)
                data['Firewall'] = "Enabled" if 'ON' in result.stdout else "Disabled"
            except:
                data['Firewall'] = "Unknown"
            
            # Remote Desktop
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SYSTEM\CurrentControlSet\Control\Terminal Server")
                value, _ = winreg.QueryValueEx(key, "fDenyTSConnections")
                winreg.CloseKey(key)
                data['Remote Desktop'] = "Enabled" if value == 0 else "Disabled"
            except:
                data['Remote Desktop'] = "Unknown"
            
            # Current user
            import getpass
            data['Current User'] = getpass.getuser()
            
        except Exception as e:
            data['Security Error'] = f"Security error: {str(e)}"
        
        return data
    
    def collect_process_info(self):
        """Collect process information"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    if info['memory_percent']:  # Only include if we have memory info
                        processes.append({
                            'pid': info['pid'],
                            'name': info['name'],
                            'cpu': info['cpu_percent'],
                            'memory': info['memory_percent']
                        })
                except:
                    continue
            
            # Sort by memory usage and take top 15
            processes.sort(key=lambda x: x['memory'], reverse=True)
            processes = processes[:15]
            
        except Exception as e:
            processes.append({'Error': f"Process error: {str(e)}"})
        
        return processes
    
    def update_scan_results(self, disk_data, proc_data):
        """Update UI with scan results"""
        
        # Update summary
        summary_text = "=== SYSTEM SUMMARY ===\n\n"
        for key, value in self.system_data.items():
            if key not in ['Error', 'Perf Error', 'Security Error']:
                summary_text += f"{key}: {value}\n"
        
        self.update_text_widget(self.summary_text, summary_text)
        
        # Update System tab
        sys_text = "=== SYSTEM INFORMATION ===\n\n"
        for key, value in self.system_data.items():
            if not key.endswith('Error') and not key in ['CPU Usage', 'Memory Usage']:
                sys_text += f"{key:20}: {value}\n"
        
        self.update_text_widget(self.tabs["System_text"], sys_text)
        
        # Update Performance tab
        perf_text = "=== PERFORMANCE METRICS ===\n\n"
        perf_keys = ['CPU Usage', 'CPU Frequency', 'Memory Usage', 'Available RAM', 
                    'Disk Read', 'Disk Write']
        for key in perf_keys:
            if key in self.system_data:
                perf_text += f"{key:20}: {self.system_data[key]}\n"
        
        self.update_text_widget(self.tabs["Performance_text"], perf_text)
        
        # Update Storage tab
        storage_text = "=== STORAGE INFORMATION ===\n\n"
        if disk_data and isinstance(disk_data, list):
            for disk in disk_data:
                if isinstance(disk, dict) and 'Device' in disk:
                    storage_text += f"Drive: {disk['Device']}\n"
                    storage_text += f"  Mount: {disk.get('Mount', 'N/A')}\n"
                    storage_text += f"  Type: {disk.get('Type', 'N/A')}\n"
                    storage_text += f"  Total: {disk.get('Total', 'N/A')}\n"
                    storage_text += f"  Used: {disk.get('Used', 'N/A')} ({disk.get('Percent', 'N/A')})\n"
                    storage_text += f"  Free: {disk.get('Free', 'N/A')}\n\n"
        
        self.update_text_widget(self.tabs["Storage_text"], storage_text)
        
        # Update Security tab
        sec_text = "=== SECURITY STATUS ===\n\n"
        sec_keys = ['Windows Defender', 'Firewall', 'Remote Desktop', 'Current User']
        for key in sec_keys:
            if key in self.system_data:
                status = self.system_data[key]
                icon = "✓" if status == "Enabled" else "✗" if status == "Disabled" else "?"
                sec_text += f"{icon} {key:20}: {status}\n"
        
        self.update_text_widget(self.tabs["Security_text"], sec_text)
        
        # Update Processes tab
        proc_text = "=== TOP PROCESSES (by memory) ===\n\n"
        if proc_data and isinstance(proc_data, list):
            proc_text += f"{'PID':>8}  {'Name':<30}  {'CPU %':>8}  {'Mem %':>8}\n"
            proc_text += "-" * 60 + "\n"
            for proc in proc_data:
                if isinstance(proc, dict) and 'pid' in proc:
                    proc_text += f"{proc['pid']:>8}  {proc.get('name', 'N/A')[:30]:<30}  "
                    proc_text += f"{proc.get('cpu', 0):>8.1f}  {proc.get('memory', 0):>8.2f}\n"
        
        self.update_text_widget(self.tabs["Processes_text"], proc_text)
        
        # Select first tab
        self.notebook.select(0)
        
        # Show completion message
        messagebox.showinfo("Scan Complete", "System scan completed successfully!")
    
    def quick_system(self):
        """Quick system check"""
        self.update_status("Quick system check...")
        data = self.collect_system_info()
        
        text = "=== QUICK SYSTEM CHECK ===\n\n"
        for key, value in data.items():
            text += f"{key}: {value}\n"
        
        self.update_text_widget(self.summary_text, text)
        self.update_text_widget(self.tabs["System_text"], text)
        self.notebook.select(0)
        self.update_status("Quick system check complete")
    
    def quick_disk(self):
        """Quick disk check"""
        self.update_status("Quick disk check...")
        disks = self.collect_disk_info()
        
        text = "=== QUICK DISK CHECK ===\n\n"
        if disks and isinstance(disks, list):
            for disk in disks:
                if isinstance(disk, dict) and 'Device' in disk:
                    text += f"{disk['Device']}: {disk.get('Percent', 'N/A')} used\n"
                    text += f"  Free space: {disk.get('Free', 'N/A')}\n\n"
        
        self.update_text_widget(self.summary_text, text)
        self.update_text_widget(self.tabs["Storage_text"], text)
        self.notebook.select(2)  # Storage tab
        self.update_status("Quick disk check complete")
    
    def generate_report(self):
        """Generate a report file"""
        if not self.system_data:
            messagebox.showwarning("No Data", "Please run a scan first to collect data.")
            return
        
        # Create filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_report_{timestamp}.txt"
        
        # Ask for save location
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=filename
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("WINDOWS SYSTEM DIAGNOSTIC REPORT\n")
                f.write("=" * 60 + "\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Computer: {self.system_data.get('Hostname', 'Unknown')}\n")
                f.write("=" * 60 + "\n\n")
                
                # Write all data
                f.write("SYSTEM INFORMATION\n")
                f.write("-" * 40 + "\n")
                for key, value in self.system_data.items():
                    f.write(f"{key}: {value}\n")
                
                # Add recommendations
                f.write("\n\nRECOMMENDATIONS\n")
                f.write("-" * 40 + "\n")
                recs = self.get_recommendations()
                for i, rec in enumerate(recs, 1):
                    f.write(f"{i}. {rec}\n")
            
            self.update_status(f"Report saved: {os.path.basename(filepath)}")
            
            # Ask to open the file
            if messagebox.askyesno("Report Generated", 
                                  f"Report saved to:\n{filepath}\n\nOpen report now?"):
                os.startfile(filepath)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {str(e)}")
    
    def get_recommendations(self):
        """Generate recommendations"""
        recs = []
        
        # Check disk usage from summary text
        summary = self.summary_text.get(1.0, END)
        if "Disk" in summary:
            for line in summary.split('\n'):
                if '% used' in line:
                    try:
                        percent = float(line.split('%')[0].split()[-1])
                        if percent > 90:
                            recs.append(f"Disk critically full ({percent}%). Free up space immediately.")
                        elif percent > 80:
                            recs.append(f"Disk getting full ({percent}%). Consider cleaning up files.")
                    except:
                        pass
        
        # Check memory usage
        if 'Memory Usage' in self.system_data:
            try:
                mem_usage = float(self.system_data['Memory Usage'].strip('%'))
                if mem_usage > 90:
                    recs.append(f"High memory usage ({mem_usage}%). Consider closing applications.")
            except:
                pass
        
        # Security recommendations
        if self.system_data.get('Windows Defender') == 'Disabled':
            recs.append("Enable Windows Defender for antivirus protection.")
        
        if self.system_data.get('Firewall') == 'Disabled':
            recs.append("Enable Windows Firewall for network security.")
        
        if not recs:
            recs.append("System appears to be running normally.")
        
        recs.append("Keep Windows updated for security and performance.")
        recs.append("Regularly back up important data.")
        
        return recs

def main():
    """Main entry point"""
    # Check platform
    if platform.system() != "Windows":
        print("Error: This tool requires Windows.")
        return
    
    # Create and run the GUI
    root = Tk()
    
    # Center window
    root.update_idletasks()
    width = 1000
    height = 700
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Create app
    app = SimpleDiagnosticTool(root)
    
    # Start main loop
    root.mainloop()

# Alternative console version if GUI fails
def console_version():
    """Fallback console version"""
    print("\n" + "="*60)
    print("WINDOWS DIAGNOSTIC TOOL - CONSOLE VERSION")
    print("="*60)
    
    print("\nChecking system...")
    
    try:
        # Basic system info
        print(f"\nOS: {platform.system()} {platform.release()}")
        print(f"Version: {platform.version()}")
        print(f"Hostname: {socket.gethostname()}")
        
        # CPU
        print(f"\nCPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical")
        print(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")
        
        # Memory
        mem = psutil.virtual_memory()
        print(f"\nTotal RAM: {mem.total / (1024**3):.1f} GB")
        print(f"Available RAM: {mem.available / (1024**3):.1f} GB")
        print(f"Memory Usage: {mem.percent}%")
        
        # Disks
        print("\nDISKS:")
        partitions = psutil.disk_partitions()
        for part in partitions:
            try:
                usage = psutil.disk_usage(part.mountpoint)
                print(f"  {part.device}: {usage.percent}% used ({usage.free / (1024**3):.1f} GB free)")
            except:
                print(f"  {part.device}: Access denied")
        
        print("\n" + "="*60)
        input("\nPress Enter to exit...")
        
    except Exception as e:
        print(f"\nError: {e}")
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"GUI failed: {e}")
        console_version()