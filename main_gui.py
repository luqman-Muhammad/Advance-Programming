#main_gui.py - Desktop based frontend (GUI - graphic user interface)

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
from datetime import datetime
import threading
import json

class CourierDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Courier Service Management System")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2c3e50')
        
        # Backend API URL
        self.API_BASE = "http://localhost:1234/api"
        
        # Main container
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_packages_tab()
        self.create_tracking_tab()
        self.create_drivers_tab()
        
        # Style configuration
        self.configure_styles()
        
        # Initial load and auto-refresh
        self.root.after(500, self.initial_load)
    
    def initial_load(self):
        """Load data on startup"""
        self.load_dashboard_stats()
        self.load_packages()
        self.load_drivers()
        # Start auto-refresh after initial load
        self.root.after(10000, self.auto_refresh)
    
    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TNotebook', background='#2c3e50')
        style.configure('TNotebook.Tab', background='#34495e', foreground='white', 
                       padding=[20, 10], font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#3498db')])
        
        style.configure('TFrame', background='#ecf0f1')
        style.configure('TLabel', background='#ecf0f1', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'))
        style.configure('Treeview', font=('Arial', 9), rowheight=25)
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))
    
    def extract_data(self, response_json):
        """Extract data array from response - handles both wrapped and unwrapped formats"""
        if isinstance(response_json, dict) and 'data' in response_json:
            return response_json['data']
        elif isinstance(response_json, list):
            return response_json
        else:
            return []
    
    # ==================== DASHBOARD TAB ====================
    def create_dashboard_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='📊 Dashboard')
        
        # Title
        title = tk.Label(frame, text="COURIER SERVICE DASHBOARD", 
                        font=('Arial', 20, 'bold'), bg='#3498db', fg='white', pady=15)
        title.pack(fill='x')
        
        # Stats frame
        stats_frame = tk.Frame(frame, bg='#ecf0f1')
        stats_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create stat cards
        self.total_packages_label = self.create_stat_card(stats_frame, "Total Packages", "0", '#3498db', 0, 0)
        self.pending_label = self.create_stat_card(stats_frame, "Pending", "0", '#f39c12', 0, 1)
        self.in_transit_label = self.create_stat_card(stats_frame, "In Transit", "0", '#9b59b6', 1, 0)
        self.delivered_label = self.create_stat_card(stats_frame, "Delivered", "0", '#27ae60', 1, 1)
        
        # Refresh button
        refresh_btn = tk.Button(frame, text="🔄 Refresh Stats", command=self.load_dashboard_stats,
                               bg='#2ecc71', fg='white', font=('Arial', 12, 'bold'), 
                               pady=10, cursor='hand2')
        refresh_btn.pack(pady=20)
    
    def create_stat_card(self, parent, title, value, color, row, col):
        card = tk.Frame(parent, bg=color, relief='raised', bd=3)
        card.grid(row=row, column=col, padx=15, pady=15, sticky='nsew', ipadx=30, ipady=20)
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        
        tk.Label(card, text=title, font=('Arial', 12), bg=color, fg='white').pack(pady=5)
        value_label = tk.Label(card, text=value, font=('Arial', 32, 'bold'), bg=color, fg='white')
        value_label.pack(pady=10)
        
        return value_label
    
    def load_dashboard_stats(self):
        try:
            response = requests.get(f"{self.API_BASE}/packages", timeout=5)
            
            if response.status_code == 200:
                response_json = response.json()
                packages = self.extract_data(response_json)
                
                total = len(packages)
                pending = sum(1 for p in packages if isinstance(p, dict) and p.get('status') == 'pending')
                in_transit = sum(1 for p in packages if isinstance(p, dict) and p.get('status') == 'in_transit')
                delivered = sum(1 for p in packages if isinstance(p, dict) and p.get('status') == 'delivered')
                
                self.total_packages_label.config(text=str(total))
                self.pending_label.config(text=str(pending))
                self.in_transit_label.config(text=str(in_transit))
                self.delivered_label.config(text=str(delivered))
                    
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", 
                "Cannot connect to backend!\n"
                "Make sure it's running on http://localhost:1234")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stats:\n{str(e)}")
    
    # ==================== PACKAGES TAB ====================
    def create_packages_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='📦 Packages')
        
        # Top section - Add Package Form
        form_frame = tk.LabelFrame(frame, text="Add New Package", font=('Arial', 12, 'bold'),
                                   bg='#ecf0f1', fg='#2c3e50', padx=20, pady=15)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        # Form fields
        fields_frame = tk.Frame(form_frame, bg='#ecf0f1')
        fields_frame.pack()
        
        tk.Label(fields_frame, text="Package ID:", bg='#ecf0f1', font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.package_id_entry = tk.Entry(fields_frame, width=25, font=('Arial', 10))
        self.package_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Recipient:", bg='#ecf0f1', font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.recipient_entry = tk.Entry(fields_frame, width=25, font=('Arial', 10))
        self.recipient_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Address:", bg='#ecf0f1', font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.address_entry = tk.Entry(fields_frame, width=25, font=('Arial', 10))
        self.address_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(fields_frame, text="Assigned Driver:", bg='#ecf0f1', font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky='e', padx=5, pady=5)
        self.driver_entry = tk.Entry(fields_frame, width=25, font=('Arial', 10))
        self.driver_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Add button
        add_btn = tk.Button(form_frame, text="➕ Add Package", command=self.add_package,
                           bg='#27ae60', fg='white', font=('Arial', 11, 'bold'), 
                           pady=8, cursor='hand2', width=20)
        add_btn.pack(pady=10)
        
        # Packages list
        list_frame = tk.LabelFrame(frame, text="All Packages", font=('Arial', 12, 'bold'),
                                  bg='#ecf0f1', fg='#2c3e50')
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview
        columns = ('Package ID', 'Recipient', 'Address', 'Driver', 'Created', 'Delivered')
        self.packages_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        widths = [120, 150, 250, 120, 150, 120]
        for col, width in zip(columns, widths):
            self.packages_tree.heading(col, text=col)
            self.packages_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.packages_tree.yview)
        self.packages_tree.configure(yscrollcommand=scrollbar.set)
        
        self.packages_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Buttons
        btn_frame = tk.Frame(list_frame, bg='#ecf0f1')
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text="🔄 Refresh", command=self.load_packages,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), 
                 padx=15, pady=5, cursor='hand2').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="❌ Delete Selected", command=self.delete_package,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), 
                 padx=15, pady=5, cursor='hand2').pack(side='left', padx=5)
    
    def add_package(self):
        data = {
            'package_id': self.package_id_entry.get().strip(),
            'recipient_address': self.address_entry.get().strip(),
            'assigned_driver': self.driver_entry.get().strip(),
        }
        
        # Add recipient if provided
        recipient = self.recipient_entry.get().strip()
        if recipient:
            data['recipient_name'] = recipient
        
        if not (data['package_id'] and data['recipient_address']):
            messagebox.showwarning("Warning", "Please fill Package ID and Address!")
            return
        
        try:
            response = requests.post(f"{self.API_BASE}/packages", json=data, timeout=5)
            if response.status_code == 201:
                messagebox.showinfo("Success", "Package added successfully!")
                self.clear_package_form()
                self.load_packages()
                self.load_dashboard_stats()
            else:
                messagebox.showerror("Error", f"Failed to add package:\n{response.text}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Cannot connect to backend!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add package:\n{str(e)}")
    
    def clear_package_form(self):
        self.package_id_entry.delete(0, tk.END)
        self.recipient_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.driver_entry.delete(0, tk.END)
    
    def load_packages(self):
        try:
            response = requests.get(f"{self.API_BASE}/packages", timeout=5)
            
            if response.status_code == 200:
                response_json = response.json()
                packages = self.extract_data(response_json)
                
                # Clear existing items
                for item in self.packages_tree.get_children():
                    self.packages_tree.delete(item)
                
                # Add packages
                for pkg in packages:
                    if isinstance(pkg, dict):
                        delivered = pkg.get('delivered_at', 'Not yet')
                        if delivered and delivered != 'Not yet':
                            try:
                                delivered = delivered.split('T')[0]  # Just show date
                            except:
                                pass
                        
                        self.packages_tree.insert('', 'end', values=(
                            pkg.get('package_id', 'N/A'),
                            pkg.get('recipient_name', 'N/A'),
                            pkg.get('recipient_address', 'N/A')[:40] + '...' if len(pkg.get('recipient_address', '')) > 40 else pkg.get('recipient_address', 'N/A'),
                            pkg.get('assigned_driver', 'N/A'),
                            pkg.get('created_at', 'N/A').split('T')[0] if 'T' in str(pkg.get('created_at', '')) else pkg.get('created_at', 'N/A'),
                            delivered
                        ))
                        
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Cannot connect to backend!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load packages:\n{str(e)}")
    
    def delete_package(self):
        selected = self.packages_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a package to delete!")
            return
        
        item = self.packages_tree.item(selected[0])
        pkg_id = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete package {pkg_id}?"):
            try:
                response = requests.delete(f"{self.API_BASE}/packages/{pkg_id}", timeout=5)
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Package deleted!")
                    self.load_packages()
                    self.load_dashboard_stats()
                else:
                    messagebox.showerror("Error", f"Failed to delete:\n{response.text}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete:\n{str(e)}")
    
    # ==================== TRACKING TAB ====================
    def create_tracking_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='🔍 Track Package')
        
        # Search section
        search_frame = tk.LabelFrame(frame, text="Track Your Package", font=('Arial', 14, 'bold'),
                                    bg='#ecf0f1', fg='#2c3e50', padx=30, pady=20)
        search_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(search_frame, text="Enter Package ID:", bg='#ecf0f1', 
                font=('Arial', 12, 'bold')).pack()
        
        self.tracking_search = tk.Entry(search_frame, width=40, font=('Arial', 14))
        self.tracking_search.pack(pady=10)
        
        tk.Button(search_frame, text="🔍 Track Package", command=self.track_package,
                 bg='#3498db', fg='white', font=('Arial', 12, 'bold'), 
                 pady=10, padx=30, cursor='hand2').pack(pady=10)
        
        # Results section
        self.tracking_result = scrolledtext.ScrolledText(frame, width=100, height=20, 
                                                         font=('Courier', 11), bg='#2c3e50', 
                                                         fg='#ecf0f1', wrap=tk.WORD)
        self.tracking_result.pack(fill='both', expand=True, padx=20, pady=10)
    
    def track_package(self):
        package_id = self.tracking_search.get().strip()
        if not package_id:
            messagebox.showwarning("Warning", "Please enter a Package ID!")
            return
        
        try:
            response = requests.get(f"{self.API_BASE}/packages/{package_id}", timeout=5)
            
            if response.status_code == 200:
                package = response.json()
                
                # Handle wrapped response
                if isinstance(package, dict) and 'data' in package:
                    package = package['data']
                
                if isinstance(package, dict):
                    result = f"""
╔══════════════════════════════════════════════════════════════╗
║               PACKAGE TRACKING INFORMATION                    ║
╚══════════════════════════════════════════════════════════════╝

📦 PACKAGE ID:      {package.get('package_id', 'N/A')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📥 RECIPIENT:       {package.get('recipient_name', 'N/A')}
📍 ADDRESS:         {package.get('recipient_address', 'N/A')}
🚚 ASSIGNED DRIVER: {package.get('assigned_driver', 'N/A')}
📅 CREATED:         {package.get('created_at', 'N/A')}
✅ DELIVERED:       {package.get('delivered_at', 'Not yet')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                    self.tracking_result.delete(1.0, tk.END)
                    self.tracking_result.insert(1.0, result)
                        
            elif response.status_code == 404:
                self.tracking_result.delete(1.0, tk.END)
                self.tracking_result.insert(1.0, f"\n\n❌ Package not found: {package_id}")
            else:
                messagebox.showerror("Error", f"Backend error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Cannot connect to backend!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to track package:\n{str(e)}")
    
    # ==================== DRIVERS TAB ====================
    def create_drivers_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text='🚚 Drivers')
        
        # Add driver form
        form_frame = tk.LabelFrame(frame, text="Add Driver", font=('Arial', 12, 'bold'),
                                  bg='#ecf0f1', fg='#2c3e50', padx=20, pady=15)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        fields = tk.Frame(form_frame, bg='#ecf0f1')
        fields.pack()
        
        tk.Label(fields, text="Driver ID:", bg='#ecf0f1', font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.driver_id = tk.Entry(fields, width=30, font=('Arial', 10))
        self.driver_id.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(fields, text="Name:", bg='#ecf0f1', font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.driver_name = tk.Entry(fields, width=30, font=('Arial', 10))
        self.driver_name.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(fields, text="Phone:", bg='#ecf0f1', font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.driver_phone = tk.Entry(fields, width=30, font=('Arial', 10))
        self.driver_phone.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(form_frame, text="➕ Add Driver", command=self.add_driver,
                 bg='#27ae60', fg='white', font=('Arial', 11, 'bold'), 
                 pady=8, cursor='hand2', width=20).pack(pady=10)
        
        # Drivers list
        list_frame = tk.LabelFrame(frame, text="All Drivers", font=('Arial', 12, 'bold'),
                                  bg='#ecf0f1', fg='#2c3e50')
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('Driver ID', 'Name', 'Phone', 'Status', 'Total Deliveries')
        self.drivers_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        widths = [120, 200, 150, 120, 150]
        for col, width in zip(columns, widths):
            self.drivers_tree.heading(col, text=col)
            self.drivers_tree.column(col, width=width)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.drivers_tree.yview)
        self.drivers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.drivers_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        tk.Button(list_frame, text="🔄 Refresh", command=self.load_drivers,
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), 
                 padx=15, pady=5, cursor='hand2').pack(pady=10)
    
    def add_driver(self):
        data = {
            'driver_id': self.driver_id.get().strip(),
            'name': self.driver_name.get().strip(),
            'phone': self.driver_phone.get().strip(),
            'status': 'available'
        }
        
        if not all([data['driver_id'], data['name']]):
            messagebox.showwarning("Warning", "Please fill Driver ID and Name!")
            return
        
        try:
            response = requests.post(f"{self.API_BASE}/drivers", json=data, timeout=5)
            if response.status_code == 201:
                messagebox.showinfo("Success", "Driver added successfully!")
                self.driver_id.delete(0, tk.END)
                self.driver_name.delete(0, tk.END)
                self.driver_phone.delete(0, tk.END)
                self.load_drivers()
            else:
                messagebox.showerror("Error", f"Failed to add driver:\n{response.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add driver:\n{str(e)}")
    
    def load_drivers(self):
        try:
            response = requests.get(f"{self.API_BASE}/drivers", timeout=5)
            
            if response.status_code == 200:
                response_json = response.json()
                drivers = self.extract_data(response_json)
                
                for item in self.drivers_tree.get_children():
                    self.drivers_tree.delete(item)
                
                for driver in drivers:
                    if isinstance(driver, dict):
                        self.drivers_tree.insert('', 'end', values=(
                            driver.get('driver_id', 'N/A'),
                            driver.get('name', 'N/A'),
                            driver.get('phone', 'N/A'),
                            driver.get('status', 'N/A'),
                            driver.get('total_deliveries', 0)
                        ))
                        
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Cannot connect to backend!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load drivers:\n{str(e)}")
    
    # ==================== AUTO REFRESH ====================
    def auto_refresh(self):
        """Auto refresh every 10 seconds"""
        try:
            self.load_dashboard_stats()
            self.load_packages()
            self.load_drivers()
        except:
            pass  # Silently fail on auto-refresh
        
        self.root.after(10000, self.auto_refresh)


# ==================== MAIN ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = CourierDesktopApp(root)
    root.mainloop()