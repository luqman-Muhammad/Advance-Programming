# services/courier_service_sql.py
"""
Courier Service - Business Logic Layer
Handles all business operations for the courier service
Works with SQL database through DatabaseHandler
"""

from models.driver_sql import Driver
from models.package_sql import Package

class CourierService:
    """Service class that handles all courier business logic"""
    
    def __init__(self, db_handler):
        """
        Initialize courier service with database handler
        
        Args:
            db_handler: DatabaseHandler instance
        """
        self.db = db_handler
    
    # DRIVER OPERATIONS
    
    def add_driver(self, driver):
        """
        Add a new driver to the system
        
        Args:
            driver (Driver): Driver object to add
        
        Returns:
            bool: True if successful, False if driver already exists
        """
        return self.db.add_driver(driver)
    
    def get_driver(self, driver_id):
        """
        Get driver by ID
        
        Args:
            driver_id (str): Driver ID
        
        Returns:
            Driver: Driver object or None
        """
        driver_data = self.db.get_driver(driver_id)
        
        if driver_data:
            # Get assigned packages for this driver
            packages = self.db.get_driver_packages(driver_id)
            assigned_package_ids = [p['package_id'] for p in packages]
            driver_data['assigned_packages'] = assigned_package_ids
            
            return Driver.from_dict(driver_data)
        
        return None
    
    def get_all_drivers(self):
        """
        Get all drivers in the system
        
        Returns:
            list: List of Driver objects
        """
        drivers_data = self.db.get_all_drivers()
        drivers = []
        
        for driver_data in drivers_data:
            # Get assigned packages for each driver
            packages = self.db.get_driver_packages(driver_data['driver_id'])
            assigned_package_ids = [p['package_id'] for p in packages]
            driver_data['assigned_packages'] = assigned_package_ids
            
            drivers.append(Driver.from_dict(driver_data))
        
        return drivers
    
    def update_driver_status(self, driver_id, status):
        """
        Update driver availability status
        
        Args:
            driver_id (str): Driver ID
            status (str): New status (available/busy)
        
        Returns:
            bool: True if successful
        """
        return self.db.update_driver_status(driver_id, status)
    
    # PACKAGE OPERATIONS
    
    def add_package(self, package):
        """
        Add a new package to the system
        
        Args:
            package (Package): Package object to add
        
        Returns:
            bool: True if successful, False if package already exists
        """
        return self.db.add_package(package)
    
    def get_package(self, package_id):
        """
        Get package by ID
        
        Args:
            package_id (str): Package ID
        
        Returns:
            Package: Package object or None
        """
        package_data = self.db.get_package(package_id)
        
        if package_data:
            return Package.from_dict(package_data)
        
        return None
    
    def get_all_packages(self):
        """
        Get all packages in the system
        
        Returns:
            list: List of Package objects
        """
        packages_data = self.db.get_all_packages()
        return [Package.from_dict(p) for p in packages_data]
    
    def get_driver_packages(self, driver_id):
        """
        Get all packages assigned to a specific driver
        
        Args:
            driver_id (str): Driver ID
        
        Returns:
            list: List of Package objects
        """
        packages_data = self.db.get_driver_packages(driver_id)
        return [Package.from_dict(p) for p in packages_data]
    
    def update_package_status(self, package_id, status):
        """
        Update package status
        
        Args:
            package_id (str): Package ID
            status (str): New status
        
        Returns:
            bool: True if successful
        """
        return self.db.update_package_status(package_id, status)
    
    # DELIVERY OPERATIONS
    
    def assign_package_to_driver(self, package_id, driver_id):
        """
        Assign a package to a driver
        
        Args:
            package_id (str): Package ID
            driver_id (str): Driver ID
        
        Returns:
            bool: True if successful
        """
        # Check if package and driver exist
        package = self.get_package(package_id)
        driver = self.get_driver(driver_id)
        
        if not package or not driver:
            return False
        
        # Assign package in database
        if self.db.assign_package_to_driver(package_id, driver_id):
            # Update driver status to busy
            self.db.update_driver_status(driver_id, 'busy')
            return True
        
        return False
    
    def complete_delivery(self, package_id):
        """
        Mark a delivery as complete
        
        Args:
            package_id (str): Package ID
        
        Returns:
            bool: True if successful
        """
        # Get package to find assigned driver
        package = self.get_package(package_id)
        
        if not package:
            return False
        
        # Update package status to delivered
        if self.db.update_package_status(package_id, 'delivered'):
            # Increment driver's delivery count
            if package.assigned_driver:
                self.db.increment_driver_deliveries(package.assigned_driver)
                
                # Check if driver has any more packages
                remaining_packages = self.db.get_driver_packages(package.assigned_driver)
                
                # If no more packages, set driver to available
                if len(remaining_packages) == 0:
                    self.db.update_driver_status(package.assigned_driver, 'available')
            
            return True
        
        return False
    
    # REPORTING & ANALYTICS
    
    def get_package_summary(self):
        """
        Get summary statistics for packages
        
        Returns:
            dict: Package statistics
        """
        all_packages = self.get_all_packages()
        
        summary = {
            'total': len(all_packages),
            'pending': 0,
            'assigned': 0,
            'in_transit': 0,
            'delivered': 0
        }
        
        for package in all_packages:
            if package.status == 'pending':
                summary['pending'] += 1
            elif package.status == 'assigned':
                summary['assigned'] += 1
            elif package.status in ['in_transit', 'picked_up', 'out_for_delivery']:
                summary['in_transit'] += 1
            elif package.status == 'delivered':
                summary['delivered'] += 1
        
        return summary
    
    def get_driver_performance(self):
        """
        Get performance metrics for all drivers
        
        Returns:
            list: List of driver performance data
        """
        drivers = self.get_all_drivers()
        
        performance = []
        for driver in drivers:
            performance.append({
                'driver_id': driver.driver_id,
                'name': driver.name,
                'total_deliveries': driver.total_deliveries,
                'current_load': len(driver.assigned_packages),
                'status': driver.status
            })
        
        # Sort by total deliveries (highest first)
        performance.sort(key=lambda x: x['total_deliveries'], reverse=True)
        
        return performance
    
    def get_available_drivers(self):
        """
        Get all available drivers
        
        Returns:
            list: List of available Driver objects
        """
        all_drivers = self.get_all_drivers()
        return [d for d in all_drivers if d.status == 'available']
    
    def get_pending_packages(self):
        """
        Get all pending packages (not yet assigned)
        
        Returns:
            list: List of pending Package objects
        """
        all_packages = self.get_all_packages()
        return [p for p in all_packages if p.status == 'pending']