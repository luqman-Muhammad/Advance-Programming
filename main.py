# main_sql.py - Courier Service Management System - SQL VERSION
"""
This is the main file that runs the courier service application.
It uses SQL database instead of flat files
"""

from models.driver_sql import Driver
from models.package_sql import Package
from services.courier_service_sql import CourierService
from database.db_handler import DatabaseHandler
import os

class CourierApp:
    """Main application class that handles the user interface"""
    
    def __init__(self):
        """Initialize the application with courier service"""
        self.db_handler = DatabaseHandler(
            server='localhost',
            database='CourierDB',
            use_windows_auth=True
        )
        self.courier_service = CourierService(self.db_handler)
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize database tables"""
        try:
            self.db_handler.create_tables()
            print("✓ Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_menu(self):
        """Display main menu options"""
        print("\n" + "="*50)
        print("    LUQMAN COURIER SERVICE MANAGEMENT SYSTEM")
        print("              (SQL DATABASE VERSION)")
        print("="*50)
        print("\n1. Driver Management")
        print("2. Package Management")
        print("3. Delivery Operations")
        print("4. Reports & Analytics")
        print("5. Exit")
        print("-"*50)
    
    def driver_management_menu(self):
        """Handle driver-related operations"""
        while True:
            print("\n--- DRIVER MANAGEMENT ---")
            print("1. Register New Driver")
            print("2. View All Drivers")
            print("3. View Driver Details")
            print("4. Update Driver Status")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.register_driver()
            elif choice == '2':
                self.view_all_drivers()
            elif choice == '3':
                self.view_driver_details()
            elif choice == '4':
                self.update_driver_status()
            elif choice == '5':
                break
            else:
                print("Invalid choice! Please try again.")
    
    def register_driver(self):
        """Register a new driver in the system"""
        print("\n--- REGISTER NEW DRIVER ---")
        driver_id = input("Enter Driver ID: ")
        name = input("Enter Driver Name: ")
        phone = input("Enter Phone Number: ")
        vehicle_type = input("Enter Vehicle Type (bike/van/truck): ")
        
        driver = Driver(driver_id, name, phone, vehicle_type)
        
        if self.courier_service.add_driver(driver):
            print(f"✓ Driver {name} registered successfully!")
        else:
            print(f"✗ Driver with ID {driver_id} already exists!")
    
    def view_all_drivers(self):
        """Display all registered drivers"""
        print("\n--- ALL DRIVERS ---")
        drivers = self.courier_service.get_all_drivers()
        
        if not drivers:
            print("No drivers registered yet.")
            return
        
        print(f"\n{'ID':<10} {'Name':<20} {'Phone':<15} {'Vehicle':<10} {'Status':<10} {'Deliveries':<12}")
        print("-"*85)
        for driver in drivers:
            print(f"{driver.driver_id:<10} {driver.name:<20} {driver.phone:<15} "
                  f"{driver.vehicle_type:<10} {driver.status:<10} {driver.total_deliveries:<12}")
    
    def view_driver_details(self):
        """View detailed information about a specific driver"""
        driver_id = input("\nEnter Driver ID: ")
        driver = self.courier_service.get_driver(driver_id)
        
        if driver:
            print("\n--- DRIVER DETAILS ---")
            print(f"ID: {driver.driver_id}")
            print(f"Name: {driver.name}")
            print(f"Phone: {driver.phone}")
            print(f"Vehicle Type: {driver.vehicle_type}")
            print(f"Status: {driver.status}")
            print(f"Total Deliveries: {driver.total_deliveries}")
            print(f"Current Load: {len(driver.assigned_packages)} packages")
            
            if driver.assigned_packages:
                print(f"\nAssigned Packages: {', '.join(driver.assigned_packages)}")
        else:
            print(f"✗ Driver with ID {driver_id} not found!")
    
    def update_driver_status(self):
        """Update driver availability status"""
        driver_id = input("\nEnter Driver ID: ")
        print("1. Available")
        print("2. Busy")
        
        status_choice = input("Select new status: ")
        status_map = {'1': 'available', '2': 'busy'}
        
        if status_choice in status_map:
            if self.courier_service.update_driver_status(driver_id, status_map[status_choice]):
                print("✓ Driver status updated successfully!")
            else:
                print("✗ Failed to update driver status!")
        else:
            print("Invalid choice!")
    
    def package_management_menu(self):
        """Handle package-related operations"""
        while True:
            print("\n--- PACKAGE MANAGEMENT ---")
            print("1. Create New Package")
            print("2. View All Packages")
            print("3. Track Package")
            print("4. Update Package Status")
            print("5. Back to Main Menu")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.create_package()
            elif choice == '2':
                self.view_all_packages()
            elif choice == '3':
                self.track_package()
            elif choice == '4':
                self.update_package_status()
            elif choice == '5':
                break
            else:
                print("Invalid choice! Please try again.")
    
    def create_package(self):
        """Create a new package entry"""
        print("\n--- CREATE NEW PACKAGE ---")
        package_id = input("Enter Package ID: ")
        sender_name = input("Enter Sender Name: ")
        sender_address = input("Enter Sender Address: ")
        recipient_name = input("Enter Recipient Name: ")
        recipient_address = input("Enter Recipient Address: ")
        weight = float(input("Enter Package Weight (kg): "))
        
        package = Package(package_id, sender_name, sender_address, 
                         recipient_name, recipient_address, weight)
        
        if self.courier_service.add_package(package):
            print(f"✓ Package {package_id} created successfully!")
        else:
            print(f"✗ Package with ID {package_id} already exists!")
    
    def view_all_packages(self):
        """Display all packages in the system"""
        print("\n--- ALL PACKAGES ---")
        packages = self.courier_service.get_all_packages()
        
        if not packages:
            print("No packages in the system.")
            return
        
        print(f"\n{'ID':<10} {'Sender':<15} {'Recipient':<15} {'Weight':<8} {'Status':<15} {'Driver':<10}")
        print("-"*90)
        for package in packages:
            driver_id = package.assigned_driver if package.assigned_driver else "None"
            print(f"{package.package_id:<10} {package.sender_name:<15} "
                  f"{package.recipient_name:<15} {package.weight:<8.2f} "
                  f"{package.status:<15} {driver_id:<10}")
    
    def track_package(self):
        """Track a specific package"""
        package_id = input("\nEnter Package ID to track: ")
        package = self.courier_service.get_package(package_id)
        
        if package:
            print("\n--- PACKAGE TRACKING ---")
            print(f"Package ID: {package.package_id}")
            print(f"Status: {package.status}")
            print(f"Sender: {package.sender_name}")
            print(f"Sender Address: {package.sender_address}")
            print(f"Recipient: {package.recipient_name}")
            print(f"Recipient Address: {package.recipient_address}")
            print(f"Weight: {package.weight} kg")
            print(f"Assigned Driver: {package.assigned_driver if package.assigned_driver else 'Not assigned yet'}")
            print(f"Created At: {package.created_at}")
            
            if package.delivered_at:
                print(f"Delivered At: {package.delivered_at}")
        else:
            print(f"✗ Package with ID {package_id} not found!")
    
    def update_package_status(self):
        """Update package status"""
        package_id = input("\nEnter Package ID: ")
        print("1. Pending")
        print("2. Assigned")
        print("3. In Transit")
        print("4. Delivered")
        
        status_choice = input("Select new status: ")
        status_map = {
            '1': 'pending',
            '2': 'assigned',
            '3': 'in_transit',
            '4': 'delivered'
        }
        
        if status_choice in status_map:
            if self.courier_service.update_package_status(package_id, status_map[status_choice]):
                print("✓ Package status updated successfully!")
            else:
                print("✗ Failed to update package status!")
        else:
            print("Invalid choice!")
    
    def delivery_operations_menu(self):
        """Handle delivery operations"""
        while True:
            print("\n--- DELIVERY OPERATIONS ---")
            print("1. Assign Package to Driver")
            print("2. View Driver's Assigned Packages")
            print("3. Mark Delivery as Complete")
            print("4. Back to Main Menu")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.assign_package_to_driver()
            elif choice == '2':
                self.view_driver_packages()
            elif choice == '3':
                self.complete_delivery()
            elif choice == '4':
                break
            else:
                print("Invalid choice! Please try again.")
    
    def assign_package_to_driver(self):
        """Assign a package to an available driver"""
        package_id = input("\nEnter Package ID: ")
        driver_id = input("Enter Driver ID: ")
        
        if self.courier_service.assign_package_to_driver(package_id, driver_id):
            print("✓ Package assigned to driver successfully!")
        else:
            print("✗ Failed to assign package. Check if package and driver exist.")
    
    def view_driver_packages(self):
        """View all packages assigned to a driver"""
        driver_id = input("\nEnter Driver ID: ")
        packages = self.courier_service.get_driver_packages(driver_id)
        
        if packages:
            print(f"\n--- PACKAGES FOR DRIVER {driver_id} ---")
            print(f"{'Package ID':<12} {'Recipient':<20} {'Address':<30} {'Status':<15}")
            print("-"*80)
            for package in packages:
                print(f"{package.package_id:<12} {package.recipient_name:<20} "
                      f"{package.recipient_address[:30]:<30} {package.status:<15}")
        else:
            print(f"No packages assigned to driver {driver_id}")
    
    def complete_delivery(self):
        """Mark a delivery as complete"""
        package_id = input("\nEnter Package ID: ")
        
        if self.courier_service.complete_delivery(package_id):
            print("✓ Delivery marked as complete!")
        else:
            print("✗ Failed to complete delivery!")
    
    def reports_menu(self):
        """Generate reports and analytics"""
        while True:
            print("\n--- REPORTS & ANALYTICS ---")
            print("1. Total Packages Summary")
            print("2. Driver Performance")
            print("3. Back to Main Menu")
            
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.total_packages_summary()
            elif choice == '2':
                self.driver_performance()
            elif choice == '3':
                break
            else:
                print("Invalid choice! Please try again.")
    
    def total_packages_summary(self):
        """Display summary of all packages"""
        summary = self.courier_service.get_package_summary()
        print("\n--- PACKAGE SUMMARY ---")
        print(f"Total Packages: {summary['total']}")
        print(f"Pending: {summary['pending']}")
        print(f"Assigned: {summary['assigned']}")
        print(f"In Transit: {summary['in_transit']}")
        print(f"Delivered: {summary['delivered']}")
    
    def driver_performance(self):
        """Show performance metrics for all drivers"""
        print("\n--- DRIVER PERFORMANCE ---")
        drivers = self.courier_service.get_all_drivers()
        
        if not drivers:
            print("No drivers in the system.")
            return
        
        # Sort drivers by total deliveries
        sorted_drivers = sorted(drivers, key=lambda x: x.total_deliveries, reverse=True)
        
        print(f"{'Driver ID':<12} {'Name':<20} {'Total Deliveries':<18} {'Current Load':<15}")
        print("-"*70)
        for driver in sorted_drivers:
            print(f"{driver.driver_id:<12} {driver.name:<20} "
                  f"{driver.total_deliveries:<18} {len(driver.assigned_packages):<15}")
    
    def run(self):
        """Main application loop"""
        print("""
    ╔════════════════════════════════════════════╗
    ║   LUQMAN COURIER SERVICE - SQL VERSION     ║
    ║        MANAGEMENT SYSTEM (ADMIN)           ║
    ╚════════════════════════════════════════════╝
        """)
        
        while True:
            self.display_menu()
            choice = input("\nEnter your choice: ")
            
            if choice == '1':
                self.driver_management_menu()
            elif choice == '2':
                self.package_management_menu()
            elif choice == '3':
                self.delivery_operations_menu()
            elif choice == '4':
                self.reports_menu()
            elif choice == '5':
                self.db_handler.close()
                print("\nThank you for using Luqman Courier Service Management System!")
                print("Goodbye!")
                break
            else:
                print("Invalid choice! Please try again.")
            
            input("\nPress Enter to continue...")

# Run the application
if __name__ == "__main__":
    app = CourierApp()
    app.run()