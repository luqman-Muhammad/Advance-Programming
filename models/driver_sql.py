# models/driver_sql.py
# Driver Model - Represents a delivery driver in the courier system

from datetime import datetime

class Driver:
    """Driver class to represent a delivery driver"""
    
    def __init__(self, driver_id, name, phone, vehicle_type, 
                 status='available', total_deliveries=0, assigned_packages=None):
        """
        Initialize a Driver object
        
        Args:
            driver_id (str): Unique identifier for the driver
            name (str): Driver's full name
            phone (str): Driver's phone number
            vehicle_type (str): Type of vehicle (bike/van/truck)
            status (str): Current status (available/busy)
            total_deliveries (int): Total number of completed deliveries
            assigned_packages (list): List of currently assigned package IDs
        """
        self.driver_id = driver_id
        self.name = name
        self.phone = phone
        self.vehicle_type = vehicle_type
        self.status = status
        self.total_deliveries = total_deliveries
        self.assigned_packages = assigned_packages if assigned_packages else []
    
    def assign_package(self, package_id):
        """
        Assign a package to this driver
        
        Args:
            package_id (str): Package ID to assign
        """
        if package_id not in self.assigned_packages:
            self.assigned_packages.append(package_id)
            self.status = 'busy'
    
    def remove_package(self, package_id):
        """
        Remove a package from driver's assigned packages
        
        Args:
            package_id (str): Package ID to remove
        """
        if package_id in self.assigned_packages:
            self.assigned_packages.remove(package_id)
            
            # If no more packages, set status to available
            if len(self.assigned_packages) == 0:
                self.status = 'available'
    
    def complete_delivery(self):
        """Increment total deliveries counter"""
        self.total_deliveries += 1
    
    def to_dict(self):
        """
        Convert driver object to dictionary
        
        Returns:
            dict: Driver data as dictionary
        """
        return {
            'driver_id': self.driver_id,
            'name': self.name,
            'phone': self.phone,
            'vehicle_type': self.vehicle_type,
            'status': self.status,
            'total_deliveries': self.total_deliveries,
            'assigned_packages': self.assigned_packages
        }
    
    @staticmethod
    def from_dict(data):
        """
        Create a Driver object from dictionary
        
        Args:
            data (dict): Driver data
        
        Returns:
            Driver: Driver object
        """
        return Driver(
            driver_id=data['driver_id'],
            name=data['name'],
            phone=data['phone'],
            vehicle_type=data['vehicle_type'],
            status=data.get('status', 'available'),
            total_deliveries=data.get('total_deliveries', 0),
            assigned_packages=data.get('assigned_packages', [])
        )
    
    def __str__(self):
        """String representation of driver"""
        return f"Driver({self.driver_id}, {self.name}, {self.vehicle_type}, {self.status})"
    
    def __repr__(self):
        """Representation of driver"""
        return self.__str__()