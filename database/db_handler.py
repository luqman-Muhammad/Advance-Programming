# database/db_handler.py
# Database Handler for SQL Server - Handles all database operations for the courier service

import pyodbc
from datetime import datetime

class DatabaseHandler:
    """Handles all database operations"""
    
    def __init__(self, server, database, username=None, password=None, use_windows_auth=True):
        """
        Initialize database connection
        
        Args:
            server (str): SQL Server name
            database (str): Database name
            username (str): SQL Server username (if not using Windows auth)
            password (str): SQL Server password (if not using Windows auth)
            use_windows_auth (bool): Use Windows Authentication
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.use_windows_auth = use_windows_auth
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish connection to SQL Server"""
        try:
            if self.use_windows_auth:
                connection_string = (
                    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                    f'SERVER={self.server};'
                    f'DATABASE={self.database};'
                    f'Trusted_Connection=yes;'
                )
            else:
                connection_string = (
                    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                    f'SERVER={self.server};'
                    f'DATABASE={self.database};'
                    f'UID={self.username};'
                    f'PWD={self.password};'
                )
            
            self.connection = pyodbc.connect(connection_string)
            print(f"✓ Connected to database: {self.database}")
        
        except pyodbc.Error as e:
            print(f"✗ Database connection error: {e}")
            raise
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.connection.cursor()
        
        try:
            # Create Drivers table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Drivers' AND xtype='U')
                CREATE TABLE Drivers (
                    driver_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    vehicle_type VARCHAR(20) NOT NULL,
                    status VARCHAR(20) DEFAULT 'available',
                    total_deliveries INT DEFAULT 0
                )
            """)
            
            # Create Packages table
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Packages' AND xtype='U')
                CREATE TABLE Packages (
                    package_id VARCHAR(50) PRIMARY KEY,
                    sender_name VARCHAR(100) NOT NULL,
                    sender_address VARCHAR(255) NOT NULL,
                    recipient_name VARCHAR(100) NOT NULL,
                    recipient_address VARCHAR(255) NOT NULL,
                    weight DECIMAL(10,2) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    assigned_driver VARCHAR(50),
                    created_at DATETIME DEFAULT GETDATE(),
                    delivered_at DATETIME NULL,
                    FOREIGN KEY (assigned_driver) REFERENCES Drivers(driver_id)
                )
            """)
            
            self.connection.commit()
            print("✓ Database tables created/verified")
        
        except pyodbc.Error as e:
            print(f"Error creating tables: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    # DRIVER OPERATIONS
    
    def add_driver(self, driver):
        """
        Add a new driver to database
        
        Args:
            driver: Driver object
        
        Returns:
            bool: True if successful, False otherwise
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Drivers (driver_id, name, phone, vehicle_type, status, total_deliveries)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (driver.driver_id, driver.name, driver.phone, driver.vehicle_type, 
                  driver.status, driver.total_deliveries))
            
            self.connection.commit()
            return True
        
        except pyodbc.IntegrityError:
            # Driver ID already exists
            self.connection.rollback()
            return False
        except pyodbc.Error as e:
            print(f"Error adding driver: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def get_driver(self, driver_id):
        """
        Get driver by ID
        
        Args:
            driver_id (str): Driver ID
        
        Returns:
            dict: Driver data or None
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                SELECT driver_id, name, phone, vehicle_type, status, total_deliveries
                FROM Drivers
                WHERE driver_id = ?
            """, (driver_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'driver_id': row[0],
                    'name': row[1],
                    'phone': row[2],
                    'vehicle_type': row[3],
                    'status': row[4],
                    'total_deliveries': row[5]
                }
            return None
        
        except pyodbc.Error as e:
            print(f"Error getting driver: {e}")
            return None
        finally:
            cursor.close()
    
    def get_all_drivers(self):
        """
        Get all drivers
        
        Returns:
            list: List of driver dictionaries
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                SELECT driver_id, name, phone, vehicle_type, status, total_deliveries
                FROM Drivers
            """)
            
            drivers = []
            for row in cursor.fetchall():
                drivers.append({
                    'driver_id': row[0],
                    'name': row[1],
                    'phone': row[2],
                    'vehicle_type': row[3],
                    'status': row[4],
                    'total_deliveries': row[5]
                })
            
            return drivers
        
        except pyodbc.Error as e:
            print(f"Error getting all drivers: {e}")
            return []
        finally:
            cursor.close()
    
    def update_driver_status(self, driver_id, status):
        """
        Update driver status
        
        Args:
            driver_id (str): Driver ID
            status (str): New status
        
        Returns:
            bool: True if successful
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                UPDATE Drivers
                SET status = ?
                WHERE driver_id = ?
            """, (status, driver_id))
            
            self.connection.commit()
            return cursor.rowcount > 0
        
        except pyodbc.Error as e:
            print(f"Error updating driver status: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def increment_driver_deliveries(self, driver_id):
        """
        Increment driver's total deliveries
        
        Args:
            driver_id (str): Driver ID
        
        Returns:
            bool: True if successful
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                UPDATE Drivers
                SET total_deliveries = total_deliveries + 1
                WHERE driver_id = ?
            """, (driver_id,))
            
            self.connection.commit()
            return True
        
        except pyodbc.Error as e:
            print(f"Error incrementing deliveries: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    # PACKAGE OPERATIONS
    
    def add_package(self, package):
        """
        Add a new package to database
        
        Args:
            package: Package object
        
        Returns:
            bool: True if successful, False otherwise
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO Packages (package_id, sender_name, sender_address, 
                                     recipient_name, recipient_address, weight, 
                                     status, assigned_driver, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (package.package_id, package.sender_name, package.sender_address,
                  package.recipient_name, package.recipient_address, package.weight,
                  package.status, package.assigned_driver, package.created_at))
            
            self.connection.commit()
            return True
        
        except pyodbc.IntegrityError:
            # Package ID already exists
            self.connection.rollback()
            return False
        except pyodbc.Error as e:
            print(f"Error adding package: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def get_package(self, package_id):
        """
        Get package by ID
        
        Args:
            package_id (str): Package ID
        
        Returns:
            dict: Package data or None
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                SELECT package_id, sender_name, sender_address, recipient_name,
                       recipient_address, weight, status, assigned_driver,
                       created_at, delivered_at
                FROM Packages
                WHERE package_id = ?
            """, (package_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'package_id': row[0],
                    'sender_name': row[1],
                    'sender_address': row[2],
                    'recipient_name': row[3],
                    'recipient_address': row[4],
                    'weight': float(row[5]),
                    'status': row[6],
                    'assigned_driver': row[7],
                    'created_at': row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else None,
                    'delivered_at': row[9].strftime('%Y-%m-%d %H:%M:%S') if row[9] else None
                }
            return None
        
        except pyodbc.Error as e:
            print(f"Error getting package: {e}")
            return None
        finally:
            cursor.close()
    
    def get_all_packages(self):
        """
        Get all packages
        
        Returns:
            list: List of package dictionaries
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                SELECT package_id, sender_name, sender_address, recipient_name,
                       recipient_address, weight, status, assigned_driver,
                       created_at, delivered_at
                FROM Packages
            """)
            
            packages = []
            for row in cursor.fetchall():
                packages.append({
                    'package_id': row[0],
                    'sender_name': row[1],
                    'sender_address': row[2],
                    'recipient_name': row[3],
                    'recipient_address': row[4],
                    'weight': float(row[5]),
                    'status': row[6],
                    'assigned_driver': row[7],
                    'created_at': row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else None,
                    'delivered_at': row[9].strftime('%Y-%m-%d %H:%M:%S') if row[9] else None
                })
            
            return packages
        
        except pyodbc.Error as e:
            print(f"Error getting all packages: {e}")
            return []
        finally:
            cursor.close()
    
    def get_driver_packages(self, driver_id):
        """
        Get all packages assigned to a driver
        
        Args:
            driver_id (str): Driver ID
        
        Returns:
            list: List of package dictionaries
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                SELECT package_id, sender_name, sender_address, recipient_name,
                       recipient_address, weight, status, assigned_driver,
                       created_at, delivered_at
                FROM Packages
                WHERE assigned_driver = ? AND status != 'delivered'
            """, (driver_id,))
            
            packages = []
            for row in cursor.fetchall():
                packages.append({
                    'package_id': row[0],
                    'sender_name': row[1],
                    'sender_address': row[2],
                    'recipient_name': row[3],
                    'recipient_address': row[4],
                    'weight': float(row[5]),
                    'status': row[6],
                    'assigned_driver': row[7],
                    'created_at': row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else None,
                    'delivered_at': row[9].strftime('%Y-%m-%d %H:%M:%S') if row[9] else None
                })
            
            return packages
        
        except pyodbc.Error as e:
            print(f"Error getting driver packages: {e}")
            return []
        finally:
            cursor.close()
    
    def update_package_status(self, package_id, status):
        """
        Update package status
        
        Args:
            package_id (str): Package ID
            status (str): New status
        
        Returns:
            bool: True if successful
        """
        cursor = self.connection.cursor()
        
        try:
            if status == 'delivered':
                cursor.execute("""
                    UPDATE Packages
                    SET status = ?, delivered_at = GETDATE()
                    WHERE package_id = ?
                """, (status, package_id))
            else:
                cursor.execute("""
                    UPDATE Packages
                    SET status = ?
                    WHERE package_id = ?
                """, (status, package_id))
            
            self.connection.commit()
            return cursor.rowcount > 0
        
        except pyodbc.Error as e:
            print(f"Error updating package status: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def assign_package_to_driver(self, package_id, driver_id):
        """
        Assign package to driver
        
        Args:
            package_id (str): Package ID
            driver_id (str): Driver ID
        
        Returns:
            bool: True if successful
        """
        cursor = self.connection.cursor()
        
        try:
            cursor.execute("""
                UPDATE Packages
                SET assigned_driver = ?, status = 'assigned'
                WHERE package_id = ?
            """, (driver_id, package_id))
            
            self.connection.commit()
            return cursor.rowcount > 0
        
        except pyodbc.Error as e:
            print(f"Error assigning package: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("✓ Database connection closed")