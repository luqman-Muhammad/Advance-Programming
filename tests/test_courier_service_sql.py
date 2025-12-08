# tests/test_courier_service.py
"""
Unit Tests for Courier Service System
Run with: python -m pytest tests/
OR: python -m unittest discover tests
"""

import unittest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.driver import Driver
from models.package import Package
from services.courier_service import CourierService

class TestDriver(unittest.TestCase):
    """Test cases for Driver class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.driver = Driver("D001", "John Doe", "1234567890", "van")
    
    def test_driver_creation(self):
        """Test driver object creation"""
        self.assertEqual(self.driver.driver_id, "D001")
        self.assertEqual(self.driver.name, "John Doe")
        self.assertEqual(self.driver.phone, "1234567890")
        self.assertEqual(self.driver.vehicle_type, "van")
        self.assertEqual(self.driver.status, "available")
    
    def test_assign_package(self):
        """Test assigning package to driver"""
        result = self.driver.assign_package("P001")
        self.assertTrue(result)
        self.assertIn("P001", self.driver.assigned_packages)
        self.assertEqual(self.driver.status, "busy")
    
    def test_remove_package(self):
        """Test removing package from driver"""
        self.driver.assign_package("P001")
        result = self.driver.remove_package("P001")
        self.assertTrue(result)
        self.assertNotIn("P001", self.driver.assigned_packages)
        self.assertEqual(self.driver.total_deliveries, 1)
    
    def test_update_status(self):
        """Test updating driver status"""
        result = self.driver.update_status("offline")
        self.assertTrue(result)
        self.assertEqual(self.driver.status, "offline")
    
    def test_get_current_load(self):
        """Test getting current package load"""
        self.driver.assign_package("P001")
        self.driver.assign_package("P002")
        self.assertEqual(self.driver.get_current_load(), 2)
    
    def test_driver_to_dict(self):
        """Test converting driver to dictionary"""
        driver_dict = self.driver.to_dict()
        self.assertIsInstance(driver_dict, dict)
        self.assertEqual(driver_dict['driver_id'], "D001")
        self.assertEqual(driver_dict['name'], "John Doe")
    
    def test_driver_from_dict(self):
        """Test creating driver from dictionary"""
        driver_dict = {
            'driver_id': 'D002',
            'name': 'Jane Smith',
            'phone': '0987654321',
            'vehicle_type': 'bike',
            'status': 'available',
            'assigned_packages': [],
            'total_deliveries': 0
        }
        driver = Driver.from_dict(driver_dict)
        self.assertEqual(driver.driver_id, "D002")
        self.assertEqual(driver.name, "Jane Smith")


class TestPackage(unittest.TestCase):
    """Test cases for Package class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.package = Package(
            "P001",
            "Alice",
            "123 Main St",
            "Bob",
            "456 Oak Ave",
            5.5
        )
    
    def test_package_creation(self):
        """Test package object creation"""
        self.assertEqual(self.package.package_id, "P001")
        self.assertEqual(self.package.sender_name, "Alice")
        self.assertEqual(self.package.recipient_name, "Bob")
        self.assertEqual(self.package.weight, 5.5)
        self.assertEqual(self.package.status, "pending")
    
    def test_assign_to_driver(self):
        """Test assigning package to driver"""
        result = self.package.assign_to_driver("D001")
        self.assertTrue(result)
        self.assertEqual(self.package.assigned_driver, "D001")
        self.assertEqual(self.package.status, "picked_up")
    
    def test_update_status(self):
        """Test updating package status"""
        result = self.package.update_status("in_transit")
        self.assertTrue(result)
        self.assertEqual(self.package.status, "in_transit")
    
    def test_update_invalid_status(self):
        """Test updating with invalid status"""
        result = self.package.update_status("invalid_status")
        self.assertFalse(result)
    
    def test_calculate_priority(self):
        """Test priority calculation"""
        priority = self.package.calculate_priority()
        self.assertGreater(priority, 0)
        
        # Pending packages should have higher priority
        pending_priority = self.package.calculate_priority()
        self.package.update_status("in_transit")
        transit_priority = self.package.calculate_priority()
        self.assertGreater(pending_priority, transit_priority)
    
    def test_package_to_dict(self):
        """Test converting package to dictionary"""
        package_dict = self.package.to_dict()
        self.assertIsInstance(package_dict, dict)
        self.assertEqual(package_dict['package_id'], "P001")
        self.assertEqual(package_dict['weight'], 5.5)
    
    def test_package_from_dict(self):
        """Test creating package from dictionary"""
        package_dict = {
            'package_id': 'P002',
            'sender_name': 'Charlie',
            'sender_address': '789 Pine St',
            'recipient_name': 'Diana',
            'recipient_address': '321 Elm St',
            'weight': 3.2,
            'status': 'pending',
            'assigned_driver': None,
            'created_at': '2024-01-01 10:00:00',
            'delivered_at': None
        }
        package = Package.from_dict(package_dict)
        self.assertEqual(package.package_id, "P002")
        self.assertEqual(package.weight, 3.2)


class TestCourierService(unittest.TestCase):
    """Test cases for CourierService class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = CourierService()
        self.driver = Driver("D001", "John Doe", "1234567890", "van")
        self.package = Package(
            "P001",
            "Alice",
            "123 Main St",
            "Bob",
            "456 Oak Ave",
            5.5
        )
    
    def test_add_driver(self):
        """Test adding driver to service"""
        result = self.service.add_driver(self.driver)
        self.assertTrue(result)
        self.assertEqual(len(self.service.drivers), 1)
    
    def test_add_duplicate_driver(self):
        """Test adding duplicate driver"""
        self.service.add_driver(self.driver)
        result = self.service.add_driver(self.driver)
        self.assertFalse(result)
    
    def test_get_driver(self):
        """Test getting driver by ID"""
        self.service.add_driver(self.driver)
        retrieved = self.service.get_driver("D001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "John Doe")
    
    def test_get_nonexistent_driver(self):
        """Test getting driver that doesn't exist"""
        retrieved = self.service.get_driver("D999")
        self.assertIsNone(retrieved)
    
    def test_add_package(self):
        """Test adding package to service"""
        result = self.service.add_package(self.package)
        self.assertTrue(result)
        self.assertEqual(len(self.service.packages), 1)
    
    def test_get_package(self):
        """Test getting package by ID"""
        self.service.add_package(self.package)
        retrieved = self.service.get_package("P001")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.sender_name, "Alice")
    
    def test_assign_package_to_driver(self):
        """Test assigning package to driver"""
        self.service.add_driver(self.driver)
        self.service.add_package(self.package)
        
        result = self.service.assign_package_to_driver("P001", "D001")
        self.assertTrue(result)
        
        # Check package is assigned
        package = self.service.get_package("P001")
        self.assertEqual(package.assigned_driver, "D001")
        
        # Check driver has package
        driver = self.service.get_driver("D001")
        self.assertIn("P001", driver.assigned_packages)
    
    def test_complete_delivery(self):
        """Test completing a delivery"""
        self.service.add_driver(self.driver)
        self.service.add_package(self.package)
        self.service.assign_package_to_driver("P001", "D001")
        
        result = self.service.complete_delivery("P001")
        self.assertTrue(result)
        
        # Check package is delivered
        package = self.service.get_package("P001")
        self.assertEqual(package.status, "delivered")
        self.assertIsNotNone(package.delivered_at)
        
        # Check driver stats updated
        driver = self.service.get_driver("D001")
        self.assertEqual(driver.total_deliveries, 1)
        self.assertNotIn("P001", driver.assigned_packages)
    
    def test_get_available_drivers(self):
        """Test getting available drivers"""
        driver1 = Driver("D001", "John", "111", "van")
        driver2 = Driver("D002", "Jane", "222", "bike")
        driver3 = Driver("D003", "Jack", "333", "truck")
        
        driver2.status = "offline"
        
        self.service.add_driver(driver1)
        self.service.add_driver(driver2)
        self.service.add_driver(driver3)
        
        available = self.service.get_available_drivers()
        self.assertEqual(len(available), 2)
    
    def test_get_packages_by_status(self):
        """Test filtering packages by status"""
        package1 = Package("P001", "A", "123", "B", "456", 5.0)
        package2 = Package("P002", "C", "789", "D", "012", 3.0)
        package2.status = "delivered"
        
        self.service.add_package(package1)
        self.service.add_package(package2)
        
        pending = self.service.get_packages_by_status("pending")
        delivered = self.service.get_packages_by_status("delivered")
        
        self.assertEqual(len(pending), 1)
        self.assertEqual(len(delivered), 1)
    
    def test_get_package_summary(self):
        """Test getting package summary"""
        package1 = Package("P001", "A", "123", "B", "456", 5.0)
        package2 = Package("P002", "C", "789", "D", "012", 3.0)
        package2.status = "delivered"
        
        self.service.add_package(package1)
        self.service.add_package(package2)
        
        summary = self.service.get_package_summary()
        self.assertEqual(summary['total'], 2)
        self.assertEqual(summary['pending'], 1)
        self.assertEqual(summary['delivered'], 1)
    
    def test_search_packages(self):
        """Test searching packages"""
        package1 = Package("P001", "Alice", "123", "Bob", "456", 5.0)
        package2 = Package("P002", "Charlie", "789", "Diana", "012", 3.0)
        
        self.service.add_package(package1)
        self.service.add_package(package2)
        
        results = self.service.search_packages("Alice")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].sender_name, "Alice")
    
    def test_find_best_driver(self):
        """Test finding best available driver"""
        driver1 = Driver("D001", "John", "111", "van")
        driver2 = Driver("D002", "Jane", "222", "bike")
        
        # Assign packages to driver1
        driver1.assign_package("P001")
        driver1.assign_package("P002")
        
        self.service.add_driver(driver1)
        self.service.add_driver(driver2)
        
        package = Package("P003", "A", "123", "B", "456", 5.0)
        
        best_driver = self.service.find_best_driver_for_package(package)
        
        # driver2 should be selected (has fewer packages)
        self.assertEqual(best_driver.driver_id, "D002")


# Test runner
if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)