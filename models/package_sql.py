# models/package.py
"""
Package Model
Represents a delivery package in the courier system
"""

from datetime import datetime

class Package:
    """Package class to represent a delivery package"""
    
    def __init__(self, package_id, sender_name, sender_address,
                 recipient_name, recipient_address, weight,
                 status='pending', assigned_driver=None,
                 created_at=None, delivered_at=None):
        """
        Initialize a Package object
        
        Args:
            package_id (str): Unique identifier for the package
            sender_name (str): Name of the sender
            sender_address (str): Address of the sender
            recipient_name (str): Name of the recipient
            recipient_address (str): Address of the recipient
            weight (float): Weight of the package in kg
            status (str): Current status of the package
            assigned_driver (str): ID of assigned driver
            created_at (str): Timestamp when package was created
            delivered_at (str): Timestamp when package was delivered
        """
        self.package_id = package_id
        self.sender_name = sender_name
        self.sender_address = sender_address
        self.recipient_name = recipient_name
        self.recipient_address = recipient_address
        self.weight = weight
        self.status = status
        self.assigned_driver = assigned_driver
        self.created_at = created_at if created_at else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.delivered_at = delivered_at
    
    def assign_to_driver(self, driver_id):
        """
        Assign this package to a driver
        
        Args:
            driver_id (str): Driver ID to assign to
        """
        self.assigned_driver = driver_id
        self.status = 'assigned'
    
    def update_status(self, new_status):
        """
        Update package status
        
        Args:
            new_status (str): New status for the package
        """
        self.status = new_status
        
        # If delivered, set delivery timestamp
        if new_status == 'delivered' and not self.delivered_at:
            self.delivered_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def to_dict(self):
        """
        Convert package object to dictionary
        
        Returns:
            dict: Package data as dictionary
        """
        return {
            'package_id': self.package_id,
            'sender_name': self.sender_name,
            'sender_address': self.sender_address,
            'recipient_name': self.recipient_name,
            'recipient_address': self.recipient_address,
            'weight': self.weight,
            'status': self.status,
            'assigned_driver': self.assigned_driver,
            'created_at': self.created_at,
            'delivered_at': self.delivered_at
        }
    
    @staticmethod
    def from_dict(data):
        """
        Create a Package object from dictionary
        
        Args:
            data (dict): Package data
        
        Returns:
            Package: Package object
        """
        return Package(
            package_id=data['package_id'],
            sender_name=data['sender_name'],
            sender_address=data['sender_address'],
            recipient_name=data['recipient_name'],
            recipient_address=data['recipient_address'],
            weight=data['weight'],
            status=data.get('status', 'pending'),
            assigned_driver=data.get('assigned_driver'),
            created_at=data.get('created_at'),
            delivered_at=data.get('delivered_at')
        )
    
    def __str__(self):
        """String representation of package"""
        return f"Package({self.package_id}, {self.recipient_name}, {self.status})"
    
    def __repr__(self):
        """Representation of package"""
        return self.__str__()