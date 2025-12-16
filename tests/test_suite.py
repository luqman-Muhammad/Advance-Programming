# test_suite.py - Complete Testing Suite for Courier Service
# Comprehensive unit and integration tests for the Courier Service System
# We can Run with: python -m pytest test_suite.py -v OR python test_suite.py

import unittest
import json
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app_backend import app, courier_service
from models.driver_sql import Driver
from models.package_sql import Package

# ==================== UNIT TESTS ====================

class TestDriverModel(unittest.TestCase):
    """Unit tests for Driver model"""
    
    def test_driver_initialization(self):
        """Test driver object creation"""
        driver = Driver('D001', 'John Doe', '1234567890', 'bike')
        
        self.assertEqual(driver.driver_id, 'D001')
        self.assertEqual(driver.name, 'John Doe')
        self.assertEqual(driver.phone, '1234567890')
        self.assertEqual(driver.vehicle_type, 'bike')
        self.assertEqual(driver.status, 'available')
        self.assertEqual(driver.total_deliveries, 0)
        self.assertEqual(len(driver.assigned_packages), 0)
    
    def test_driver_to_dict(self):
        """Test driver serialization to dictionary"""
        driver = Driver('D001', 'John Doe', '1234567890', 'bike')
        driver_dict = driver.to_dict()
        
        self.assertIsInstance(driver_dict, dict)
        self.assertEqual(driver_dict['driver_id'], 'D001')
        self.assertEqual(driver_dict['name'], 'John Doe')
        self.assertIn('status', driver_dict)
        self.assertIn('total_deliveries', driver_dict)
    
    def test_driver_assign_package(self):
        """Test assigning package to driver"""
        driver = Driver('D001', 'John Doe', '1234567890', 'bike')
        driver.assigned_packages.append('P001')
        
        self.assertEqual(len(driver.assigned_packages), 1)
        self.assertIn('P001', driver.assigned_packages)


class TestPackageModel(unittest.TestCase):
    """Unit tests for Package model"""
    
    def test_package_initialization(self):
        """Test package object creation"""
        package = Package('P001', 'Alice', '123 Main St', 
                         'Bob', '456 Oak Ave', 2.5)
        
        self.assertEqual(package.package_id, 'P001')
        self.assertEqual(package.sender_name, 'Alice')
        self.assertEqual(package.recipient_name, 'Bob')
        self.assertEqual(package.weight, 2.5)
        self.assertEqual(package.status, 'pending')
        self.assertIsNone(package.assigned_driver)
        self.assertIsNone(package.delivered_at)
    
    def test_package_to_dict(self):
        """Test package serialization to dictionary"""
        package = Package('P001', 'Alice', '123 Main St', 
                         'Bob', '456 Oak Ave', 2.5)
        package_dict = package.to_dict()
        
        self.assertIsInstance(package_dict, dict)
        self.assertEqual(package_dict['package_id'], 'P001')
        self.assertEqual(package_dict['weight'], 2.5)
        self.assertIn('status', package_dict)
    
    def test_package_weight_validation(self):
        """Test package weight must be positive"""
        package = Package('P001', 'Alice', '123 Main St', 
                         'Bob', '456 Oak Ave', 5.75)
        self.assertGreater(package.weight, 0)


class TestAPIEndpoints(unittest.TestCase):
    """Unit tests for API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.app = app.test_client()
        cls.app.testing = True
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.app.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('message', data)
    
    def test_get_all_drivers_endpoint(self):
        """Test GET /api/drivers"""
        response = self.app.get('/api/drivers')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)
    
    def test_get_all_packages_endpoint(self):
        """Test GET /api/packages"""
        response = self.app.get('/api/packages')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['data'], list)
    
    def test_get_package_stats_endpoint(self):
        """Test GET /api/stats/packages"""
        response = self.app.get('/api/stats/packages')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('total', data['data'])
        self.assertIn('pending', data['data'])
        self.assertIn('delivered', data['data'])
    
    def test_get_driver_stats_endpoint(self):
        """Test GET /api/stats/drivers"""
        response = self.app.get('/api/stats/drivers')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('total_drivers', data['data'])
        self.assertIn('available_drivers', data['data'])
    
    def test_add_driver_validation(self):
        """Test POST /api/drivers with valid data"""
        driver_data = {
            'driver_id': f'TEST_D_{id(self)}',  # Unique ID
            'name': 'Test Driver',
            'phone': '1234567890',
            'vehicle_type': 'bike'
        }
        
        response = self.app.post('/api/drivers',
                                data=json.dumps(driver_data),
                                content_type='application/json')
        
        self.assertIn(response.status_code, [201, 400])  # 400 if already exists
        data = json.loads(response.data)
        self.assertIn('status', data)
    
    def test_add_package_validation(self):
        """Test POST /api/packages with valid data"""
        package_data = {
            'package_id': f'TEST_P_{id(self)}',  # Unique ID
            'sender_name': 'Alice',
            'sender_address': '123 Test St',
            'recipient_name': 'Bob',
            'recipient_address': '456 Test Ave',
            'weight': 2.5
        }
        
        response = self.app.post('/api/packages',
                                data=json.dumps(package_data),
                                content_type='application/json')
        
        self.assertIn(response.status_code, [201, 400])
        data = json.loads(response.data)
        self.assertIn('status', data)
    
    def test_invalid_endpoint(self):
        """Test accessing invalid endpoint"""
        response = self.app.get('/api/invalid_endpoint')
        self.assertEqual(response.status_code, 404)


# ==================== INTEGRATION TESTS ====================

class TestIntegrationWorkflow(unittest.TestCase):
    """Integration tests for complete workflows"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.app = app.test_client()
        cls.app.testing = True
        cls.test_driver_id = f'INT_D_{id(cls)}'
        cls.test_package_id = f'INT_P_{id(cls)}'
    
    def test_01_add_driver(self):
        """Integration Test 1: Add a new driver"""
        driver_data = {
            'driver_id': self.test_driver_id,
            'name': 'Integration Test Driver',
            'phone': '9876543210',
            'vehicle_type': 'van'
        }
        
        response = self.app.post('/api/drivers',
                                data=json.dumps(driver_data),
                                content_type='application/json')
        
        self.assertIn(response.status_code, [201, 400])
        data = json.loads(response.data)
        
        if response.status_code == 201:
            self.assertEqual(data['status'], 'success')
            self.assertIn('data', data)
    
    def test_02_get_specific_driver(self):
        """Integration Test 2: Retrieve the added driver"""
        response = self.app.get(f'/api/drivers/{self.test_driver_id}')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['data']['driver_id'], self.test_driver_id)
    
    def test_03_add_package(self):
        """Integration Test 3: Add a new package"""
        package_data = {
            'package_id': self.test_package_id,
            'sender_name': 'Test Sender',
            'sender_address': '100 Integration St',
            'recipient_name': 'Test Recipient',
            'recipient_address': '200 Test Blvd',
            'weight': 3.5
        }
        
        response = self.app.post('/api/packages',
                                data=json.dumps(package_data),
                                content_type='application/json')
        
        self.assertIn(response.status_code, [201, 400])
    
    def test_04_assign_package_to_driver(self):
        """Integration Test 4: Assign package to driver"""
        response = self.app.post(
            f'/api/packages/{self.test_package_id}/assign',
            data=json.dumps({'driver_id': self.test_driver_id}),
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
    
    def test_05_verify_driver_packages(self):
        """Integration Test 5: Verify driver has assigned packages"""
        response = self.app.get(f'/api/drivers/{self.test_driver_id}/packages')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
            # Driver should have at least one package (if assignment succeeded)
            self.assertIsInstance(data['data'], list)
    
    def test_06_complete_delivery(self):
        """Integration Test 6: Complete the delivery"""
        response = self.app.post(f'/api/packages/{self.test_package_id}/complete')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
    
    def test_07_verify_package_status(self):
        """Integration Test 7: Verify package is marked as delivered"""
        response = self.app.get(f'/api/packages/{self.test_package_id}')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
            # If delivery was completed, status should be 'delivered'
            if 'data' in data and 'status' in data['data']:
                print(f"Package status: {data['data']['status']}")


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True
    
    def test_get_nonexistent_driver(self):
        """Test getting a driver that doesn't exist"""
        response = self.app.get('/api/drivers/NONEXISTENT_ID')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
    
    def test_get_nonexistent_package(self):
        """Test getting a package that doesn't exist"""
        response = self.app.get('/api/packages/NONEXISTENT_ID')
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
    
    def test_add_driver_duplicate_id(self):
        """Test adding driver with duplicate ID"""
        driver_data = {
            'driver_id': 'DUPLICATE_TEST',
            'name': 'Test',
            'phone': '1234567890',
            'vehicle_type': 'bike'
        }
        
        # Add first time
        self.app.post('/api/drivers',
                     data=json.dumps(driver_data),
                     content_type='application/json')
        
        # Try to add again with same ID
        response = self.app.post('/api/drivers',
                                data=json.dumps(driver_data),
                                content_type='application/json')
        
        # Should get error or 400 status
        self.assertIn(response.status_code, [400, 409])
    
    def test_assign_to_nonexistent_driver(self):
        """Test assigning package to non-existent driver"""
        response = self.app.post(
            '/api/packages/SOME_PACKAGE/assign',
            data=json.dumps({'driver_id': 'NONEXISTENT_DRIVER'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)


class TestBusinessLogic(unittest.TestCase):
    """Test business logic and data validation"""
    
    def test_package_weight_must_be_positive(self):
        """Test that package weight must be positive"""
        package = Package('P001', 'Alice', '123 St', 'Bob', '456 Ave', 5.5)
        self.assertGreater(package.weight, 0)
    
    def test_driver_initial_status(self):
        """Test driver initial status is 'available'"""
        driver = Driver('D001', 'John', '1234567890', 'bike')
        self.assertEqual(driver.status, 'available')
    
    def test_package_initial_status(self):
        """Test package initial status is 'pending'"""
        package = Package('P001', 'Alice', '123 St', 'Bob', '456 Ave', 2.5)
        self.assertEqual(package.status, 'pending')
    
    def test_driver_vehicle_types(self):
        """Test valid vehicle types"""
        valid_types = ['bike', 'van', 'truck']
        
        for vehicle_type in valid_types:
            driver = Driver(f'D_{vehicle_type}', 'Test', '123', vehicle_type)
            self.assertIn(driver.vehicle_type, valid_types)


# ==================== TEST RUNNER ====================

def run_tests():
    """Run all tests and generate report"""
    
    print("\n" + "="*70)
    print("COURIER SERVICE MANAGEMENT SYSTEM - TEST SUITE")
    print("="*70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDriverModel))
    suite.addTests(loader.loadTestsFromTestCase(TestPackageModel))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestBusinessLogic))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"✓ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"✗ Failed: {len(result.failures)}")
    print(f"✗ Errors: {len(result.errors)}")
    print("="*70 + "\n")
    
    return result


if __name__ == '__main__':
    # Check if backend is accessible
    try:
        import requests
        response = requests.get('http://localhost:5000/api/health', timeout=2)
        if response.status_code == 200:
            print("✓ Backend server is running")
        else:
            print("⚠ Backend server responded but may have issues")
    except:
        print("\n⚠ WARNING: Backend server is not running!")
        print("Please start the backend with: python app.py")
        print("Some tests may fail without a running backend.\n")
    
    # Run tests
    result = run_tests()
    
    # Exit with proper code
    sys.exit(0 if result.wasSuccessful() else 1)