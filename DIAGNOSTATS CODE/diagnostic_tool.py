import os
import sys
import platform
from datetime import datetime
import time

# Try to load what we need, but don't crash if something's missing
try:
    import psutil
    has_psutil = True
except ImportError:
    has_psutil = False
    print("Note: psutil not found, some features limited")

try:
    import wmi
    has_wmi = True
except ImportError:
    has_wmi = False

try:
    from tkinter import *
    from tkinter import ttk, messagebox, filedialog
    import tkinter.scrolledtext as st
    has_tk = True
except ImportError:
    has_tk = False
    print("No tkinter - need GUI version of Python")

# Colors I like using
BG = '#f5f5f5'
ACCENT = '#2a5caa'
WARN = '#ff9900'
BAD = '#cc3333'
GOOD = '#339966'

class DiagTool:
    def __init__(self, master):
        self.master = master
        master.title("PC Check")
        master.geometry("950x650")
        master.configure(bg=BG)
        
        # Center it
        master.update_idletasks()
        w = master.winfo_width()
        h = master.winfo_height()
        x = (master.winfo_screenwidth() // 2) - (w // 2)
        y = (master.winfo_screenheight() // 2) - (h // 2)
        master.geometry(f'950x650+{x}+{y}')
        
        # Some state
        self.scanning = False
        self.last_scan = None
        self.data = {}
        
        self.setup_gui()
        
        # Check if we're admin (sorta)
        self.check_admin()
        
        # Load initial system info
        self.load_basic_info()
    
    def setup_gui(self):
        # Top bar
        top_frame = Frame(self.master, bg=ACCENT, height=70)
        top_frame.pack(fill=X)
        top_frame.pack_propagate(0)
        
        Label(top_frame, text="PC Diagnostic Tool", 
              font=('Segoe UI', 18, 'bold'), 
              bg=ACCENT, fg='white').pack(side=LEFT, padx=25, pady=20)
        
        # Status label
        self.status_label = Label(top_frame, text="Ready", 
                                 font=('Segoe UI', 10), 
                                 bg=ACCENT, fg='#cccccc')
        self.status_label.pack(side=RIGHT, padx=25)
        
        # Main area
        main = Frame(self.master, bg=BG)
        main.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Left side - controls
        left = Frame(main, bg=BG, width=250)
        left.pack(side=LEFT, fill=Y)
        left.pack_propagate(0)
        
        # Scan button
        self.scan_btn = Button(left, text="▶ Run Full Scan", 
                             font=('Segoe UI', 11, 'bold'),
                             bg=GOOD, fg='white',
                             height=2,
                             command=self.do_scan)
        self.scan_btn.pack(fill=X, pady=(0, 15))
        
        # Quick buttons frame
        quick_frame = Frame(left, bg=BG)
        quick_frame.pack(fill=X, pady=(0, 20))
        
        Button(quick_frame, text="System Info", 
               command=self.show_system,
               bg='#e0e0e0').pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        Button(quick_frame, text="Disks", 
               command=self.show_disks,
               bg='#e0e0e0').pack(side=LEFT, fill=X, expand=True)
        
        # Progress
        self.prog = ttk.Progressbar(left, mode='indeterminate', length=100)
        self.prog.pack(fill=X, pady=(0, 10))
        
        # Report button
        Button(left, text="Save Report", 
               command=self.save_report,
               bg=ACCENT, fg='white').pack(fill=X, pady=(0, 25))
        
        # Info box
        info_frame = Frame(left, bg='white', relief=SOLID, borderwidth=1)
        info_frame.pack(fill=BOTH, expand=True)
        
        Label(info_frame, text="Quick Info", 
              font=('Segoe UI', 11, 'bold'),
              bg='#555555', fg='white').pack(fill=X, padx=1, pady=8)
        
        self.info_text = st.ScrolledText(info_frame, height=12,
                                       font=('Consolas', 9),
                                       wrap=WORD,
                                       bg='white',
                                       relief=FLAT)
        self.info_text.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))
        self.info_text.insert(END, "Click Scan to start...")
        self.info_text.config(state=DISABLED)
        
        # Right side - tabs
        right = Frame(main, bg=BG)
        right.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Notebook for tabs
        self.tabs = ttk.Notebook(right)
        self.tabs.pack(fill=BOTH, expand=True)
        
        # Create a few tabs
        self.tab_frames = {}
        tab_names = ['Overview', 'Hardware', 'Storage', 'Running', 'Network']
        
        for name in tab_names:
            frame = Frame(self.tabs, bg='white')
            self.tab_frames[name] = frame
            self.tabs.add(frame, text=name)
            
            # Add text area to each
            text = st.ScrolledText(frame, font=('Consolas', 9),
                                 wrap=WORD, bg='white')
            text.pack(fill=BOTH, expand=True, padx=10, pady=10)
            text.insert(END, f"{name} info will show here")
            text.config(state=DISABLED)
            
            self.tab_frames[f"{name}_text"] = text
        
        # Bottom status
        bottom = Frame(self.master, bg='#333333', height=30)
        bottom.pack(side=BOTTOM, fill=X)
        bottom.pack_propagate(0)
        
        self.bottom_label = Label(bottom, text="", 
                                 font=('Segoe UI', 9),
                                 bg='#333333', fg='#aaaaaa')
        self.bottom_label.pack(side=LEFT, padx=15)
    
    def check_admin(self):
        # Simple admin check
        try:
            import ctypes
            admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if admin:
                self.bottom_label.config(text="Running as Admin")
            else:
                self.bottom_label.config(text="User mode - some info may be limited")
        except:
            self.bottom_label.config(text="")
    
    def load_basic_info(self):
        # Just get OS and hostname for now
        self.data['os'] = f"{platform.system()} {platform.release()}"
        self.data['host'] = platform.node()
        self.data['arch'] = platform.machine()
        
        # Show in info box
        text = f"OS: {self.data['os']}\n"
        text += f"Computer: {self.data['host']}\n"
        text += f"Arch: {self.data['arch']}\n"
        
        self.update_info(text)
    
    def update_info(self, text):
        self.info_text.config(state=NORMAL)
        self.info_text.delete(1.0, END)
        self.info_text.insert(END, text)
        self.info_text.config(state=DISABLED)
    
    def update_tab(self, name, text):
        if f"{name}_text" in self.tab_frames:
            widget = self.tab_frames[f"{name}_text"]
            widget.config(state=NORMAL)
            widget.delete(1.0, END)
            widget.insert(END, text)
            widget.config(state=DISABLED)
    
    def do_scan(self):
        if self.scanning:
            return
        
        self.scanning = True
        self.scan_btn.config(state=DISABLED, text="Scanning...")
        self.prog.start()
        self.status_label.config(text="Scanning system...")
        
        # Run in thread to keep UI responsive
        import threading
        t = threading.Thread(target=self._scan_thread)
        t.daemon = True
        t.start()
    
    def _scan_thread(self):
        try:
            # Get system info
            self.status_label.config(text="Getting system details...")
            sys_info = self.get_sys_info()
            
            # Hardware
            self.status_label.config(text="Checking hardware...")
            hw_info = self.get_hardware_info()
            
            # Disks
            self.status_label.config(text="Checking disks...")
            disk_info = self.get_disk_info()
            
            # Processes
            self.status_label.config(text="Checking running programs...")
            proc_info = self.get_proc_info()
            
            # Network
            self.status_label.config(text="Checking network...")
            net_info = self.get_net_info()
            
            # Update UI
            self.master.after(0, self._update_ui, sys_info, hw_info, disk_info, proc_info, net_info)
            
            self.status_label.config(text="Scan complete")
            self.last_scan = datetime.now()
            
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {e}"))
            self.status_label.config(text="Scan failed")
        finally:
            self.master.after(0, self._scan_done)
    
    def _scan_done(self):
        self.scanning = False
        self.scan_btn.config(state=NORMAL, text="▶ Run Full Scan")
        self.prog.stop()
    
    def get_sys_info(self):
        info = {}
        
        try:
            # Basic stuff
            info['OS'] = f"{platform.system()} {platform.release()}"
            info['Version'] = platform.version()
            
            # Windows edition from registry
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                edition = winreg.QueryValueEx(key, "ProductName")[0]
                winreg.CloseKey(key)
                info['Edition'] = edition
            except:
                info['Edition'] = "Unknown"
            
            # Uptime
            if has_psutil:
                boot = datetime.fromtimestamp(psutil.boot_time())
                uptime = datetime.now() - boot
                days = uptime.days
                hours = uptime.seconds // 3600
                mins = (uptime.seconds % 3600) // 60
                info['Uptime'] = f"{days}d {hours}h {mins}m"
            
            # Python version
            info['Python'] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            
        except Exception as e:
            info['Error'] = str(e)
        
        return info
    
    def get_hardware_info(self):
        info = {}
        
        if not has_psutil:
            info['Error'] = "Need psutil for hardware info"
            return info
        
        try:
            # CPU
            info['CPU Cores'] = psutil.cpu_count(logical=True)
            info['CPU Physical'] = psutil.cpu_count(logical=False)
            
            # CPU usage
            usage = psutil.cpu_percent(interval=0.5)
            info['CPU Usage'] = f"{usage:.1f}%"
            
            # CPU freq if available
            freq = psutil.cpu_freq()
            if freq:
                info['CPU Speed'] = f"{freq.current:.0f} MHz"
            
            # Memory
            mem = psutil.virtual_memory()
            info['Total RAM'] = f"{mem.total / (1024**3):.1f} GB"
            info['Used RAM'] = f"{mem.used / (1024**3):.1f} GB"
            info['RAM %'] = f"{mem.percent}%"
            
            # Swap
            swap = psutil.swap_memory()
            if swap.total > 0:
                info['Swap'] = f"{swap.used / (1024**3):.1f} / {swap.total / (1024**3):.1f} GB"
            
        except Exception as e:
            info['Error'] = f"Hardware error: {e}"
        
        return info
    
    def get_disk_info(self):
        info = []
        
        if not has_psutil:
            return [{"Error": "psutil needed for disk info"}]
        
        try:
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disk = {
                        'drive': part.device,
                        'mount': part.mountpoint,
                        'type': part.fstype,
                        'total_gb': usage.total / (1024**3),
                        'used_gb': usage.used / (1024**3),
                        'free_gb': usage.free / (1024**3),
                        'percent': usage.percent
                    }
                    info.append(disk)
                except:
                    # Can't access this drive
                    pass
        except Exception as e:
            info.append({'error': str(e)})
        
        return info
    
    def get_proc_info(self):
        procs = []
        
        if not has_psutil:
            return [{"name": "Need psutil for process list"}]
        
        try:
            # Get top 10 by memory
            all_procs = []
            for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    all_procs.append(p.info)
                except:
                    pass
            
            # Sort by memory and take top
            all_procs.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
            for p in all_procs[:15]:
                procs.append({
                    'pid': p['pid'],
                    'name': p['name'][:30],  # truncate long names
                    'mem': p['memory_percent']
                })
        except Exception as e:
            procs.append({'error': str(e)})
        
        return procs
    
    def get_net_info(self):
        info = {}
        
        if not has_psutil:
            info['Error'] = "Need psutil for network info"
            return info
        
        try:
            # Network stats
            net = psutil.net_io_counters()
            info['Sent'] = f"{net.bytes_sent / (1024**2):.1f} MB"
            info['Recv'] = f"{net.bytes_recv / (1024**2):.1f} MB"
            
            # IP addresses
            import socket
            try:
                host = socket.gethostname()
                ip = socket.gethostbyname(host)
                info['IP'] = ip
            except:
                info['IP'] = "Unknown"
            
        except Exception as e:
            info['Error'] = str(e)
        
        return info
    
    def _update_ui(self, sys_info, hw_info, disk_info, proc_info, net_info):
        # Store data
        self.data.update({
            'sys': sys_info,
            'hw': hw_info,
            'disks': disk_info,
            'procs': proc_info,
            'net': net_info
        })
        
        # Update overview tab
        overview = "=== System Overview ===\n\n"
        for k, v in sys_info.items():
            overview += f"{k}: {v}\n"
        
        overview += "\n=== Hardware ===\n"
        for k, v in hw_info.items():
            if k != 'Error':
                overview += f"{k}: {v}\n"
        
        self.update_tab('Overview', overview)
        
        # Hardware tab
        hw_text = "=== Hardware Details ===\n\n"
        for k, v in hw_info.items():
            hw_text += f"{k:15}: {v}\n"
        
        self.update_tab('Hardware', hw_text)
        
        # Storage tab
        disk_text = "=== Disk Drives ===\n\n"
        for d in disk_info:
            if 'drive' in d:
                disk_text += f"{d['drive']} ({d['type']})\n"
                disk_text += f"  Mount: {d['mount']}\n"
                disk_text += f"  Size: {d['total_gb']:.1f} GB\n"
                disk_text += f"  Used: {d['used_gb']:.1f} GB ({d['percent']}%)\n"
                disk_text += f"  Free: {d['free_gb']:.1f} GB\n\n"
        
        self.update_tab('Storage', disk_text)
        
        # Processes tab
        proc_text = "=== Top Processes (by memory) ===\n\n"
        proc_text += "PID       Name                          Memory %\n"
        proc_text += "-" * 50 + "\n"
        
        for p in proc_info:
            if 'pid' in p:
                proc_text += f"{p['pid']:8}  {p['name']:30}  {p.get('mem', 0):6.2f}\n"
        
        self.update_tab('Running', proc_text)
        
        # Network tab
        net_text = "=== Network ===\n\n"
        for k, v in net_info.items():
            net_text += f"{k:10}: {v}\n"
        
        self.update_tab('Network', net_text)
        
        # Update info box with summary
        info_text = f"Last scan: {datetime.now().strftime('%H:%M:%S')}\n"
        info_text += f"OS: {sys_info.get('OS', '?')}\n"
        
        if 'Total RAM' in hw_info:
            info_text += f"RAM: {hw_info['Total RAM']}\n"
        
        if disk_info and 'total_gb' in disk_info[0]:
            total = sum(d['total_gb'] for d in disk_info if 'total_gb' in d)
            info_text += f"Total disk: {total:.1f} GB\n"
        
        self.update_info(info_text)
        
        # Show completion
        messagebox.showinfo("Done", "System scan completed!")
    
    def show_system(self):
        # Quick system view
        info = self.get_sys_info()
        text = "=== System Info ===\n\n"
        for k, v in info.items():
            text += f"{k}: {v}\n"
        
        self.update_info(text)
        self.tabs.select(0)  # Overview tab
        self.status_label.config(text="System info loaded")
    
    def show_disks(self):
        # Quick disk view
        disks = self.get_disk_info()
        text = "=== Disks ===\n\n"
        
        for d in disks:
            if 'drive' in d:
                text += f"{d['drive']}: {d.get('percent', 0)}% used\n"
                text += f"  Free: {d.get('free_gb', 0):.1f} GB\n\n"
        
        self.update_info(text)
        self.tabs.select(2)  # Storage tab
        self.status_label.config(text="Disk info loaded")
    
    def save_report(self):
        if not self.data or 'sys' not in self.data:
            messagebox.showwarning("No Data", "Run a scan first to get data")
            return
        
        # Ask where to save
        default_name = f"pc_check_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        
        fname = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=default_name
        )
        
        if not fname:
            return
        
        try:
            with open(fname, 'w', encoding='utf-8') as f:
                f.write("PC Diagnostic Report\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Computer: {self.data.get('host', 'Unknown')}\n")
                f.write("=" * 50 + "\n\n")
                
                # System
                f.write("SYSTEM\n")
                f.write("-" * 30 + "\n")
                for k, v in self.data.get('sys', {}).items():
                    f.write(f"{k}: {v}\n")
                
                # Hardware
                f.write("\n\nHARDWARE\n")
                f.write("-" * 30 + "\n")
                for k, v in self.data.get('hw', {}).items():
                    if k != 'Error':
                        f.write(f"{k}: {v}\n")
                
                # Disks
                f.write("\n\nSTORAGE\n")
                f.write("-" * 30 + "\n")
                for d in self.data.get('disks', []):
                    if 'drive' in d:
                        f.write(f"{d['drive']}: {d.get('percent', 0)}% used\n")
                        f.write(f"  Free: {d.get('free_gb', 0):.1f} GB\n")
                
                # Recommendations
                f.write("\n\nNOTES\n")
                f.write("-" * 30 + "\n")
                notes = self._get_notes()
                for note in notes:
                    f.write(f"• {note}\n")
            
            self.status_label.config(text=f"Saved: {os.path.basename(fname)}")
            
            # Ask to open
            if messagebox.askyesno("Saved", f"Report saved to:\n{fname}\n\nOpen it now?"):
                os.startfile(fname)
                
        except Exception as e:
            messagebox.showerror("Error", f"Couldn't save: {e}")
    
    def _get_notes(self):
        notes = []
        
        # Check disk space
        disks = self.data.get('disks', [])
        for d in disks:
            if 'percent' in d and d['percent'] > 90:
                notes.append(f"Drive {d.get('drive', '?')} is almost full ({d['percent']}%)")
            elif 'percent' in d and d['percent'] > 80:
                notes.append(f"Drive {d.get('drive', '?')} is getting full ({d['percent']}%)")
        
        # Check RAM
        hw = self.data.get('hw', {})
        if 'RAM %' in hw:
            try:
                ram_pct = float(hw['RAM %'].strip('%'))
                if ram_pct > 90:
                    notes.append(f"High RAM usage ({ram_pct}%) - might need more memory")
            except:
                pass
        
        if not notes:
            notes.append("System looks okay")
        
        notes.append("Keep Windows updated")
        notes.append("Back up important files regularly")
        
        return notes

def run_app():
    """Start the app"""
    if not has_tk:
        print("Tkinter not available. Need Python with GUI support.")
        input("Press enter...")
        return
    
    root = Tk()
    app = DiagTool(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nClosing...")
    except Exception as e:
        print(f"Error: {e}")
        input("Press enter...")

# If run directly
if __name__ == "__main__":
    run_app()
