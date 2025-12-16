# server_company_sql.py - SERVER SIDE (Company/Admin) - SQL VERSION
# SERVER SIDE - Courier Service Management System
# This runs on the company's computer
# It handles all administrative operations and serves client requests

import socket
import json
import threading
from models.driver_sql import Driver
from models.package_sql import Package
from services.courier_service_sql import CourierService
from database.db_handler import DatabaseHandler

class CourierServer:
    """Server that handles all company operations and client requests"""
    
    def __init__(self, host='0.0.0.0', port=5006):
        """
        Initialize the server
        
        Args:
            host (str): Server IP address
            port (int): Server port number
        """
        self.host = host
        self.port = port
        self.db_handler = DatabaseHandler(
            server='localhost',
            database='CourierDB',
            use_windows_auth=True
        )
        self.courier_service = CourierService(self.db_handler)
        self.server_socket = None
        self.running = False
        self.clients = []  # List of connected clients
        
        # Initialize database
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize database and create tables if they don't exist"""
        try:
            self.db_handler.create_tables()
            print("✓ Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    def start_server(self):
        """Start the server and listen for connections"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"\n{'='*60}")
            print(f"🚀 SERVER STARTED (SQL DATABASE)")
            print(f"{'='*60}")
            print(f"Server listening on {self.host}:{self.port}")
            print(f"Database: {self.db_handler.database}")
            print(f"Waiting for driver clients to connect...")
            print(f"{'='*60}\n")
            
            # Start admin interface in separate thread
            admin_thread = threading.Thread(target=self.admin_interface, daemon=True)
            admin_thread.start()
            
            # Accept client connections
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    print(f"✓ New connection from {address}")
                    
                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    self.clients.append(client_socket)
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
        
        except Exception as e:
            print(f"Error starting server: {e}")
        finally:
            self.stop_server()
    
    def handle_client(self, client_socket, address):
        """
        Handle individual client (driver) requests
        
        Args:
            client_socket: Socket connection to client
            address: Client address
        """
        try:
            while self.running:
                # Receive request from client
                data = client_socket.recv(4096).decode('utf-8')
                
                if not data:
                    break
                
                # Parse request
                request = json.loads(data)
                action = request.get('action')
                
                print(f"📨 Request from {address}: {action}")
                
                # Process request and get response
                response = self.process_request(request)
                
                # Send response back to client
                client_socket.send(json.dumps(response).encode('utf-8'))
                
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            print(f"✗ Client {address} disconnected")
    
    def process_request(self, request):
        """
        Process client request and return response
        
        Args:
            request (dict): Client request
        
        Returns:
            dict: Response to send back
        """
        action = request.get('action')
        data = request.get('data', {})
        
        try:
            # DRIVER LOGIN
            if action == 'login':
                driver_id = data.get('driver_id')
                driver = self.courier_service.get_driver(driver_id)
                
                if driver:
                    return {
                        'status': 'success',
                        'message': f'Welcome {driver.name}!',
                        'driver': driver.to_dict()
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Driver not found'
                    }
            
            # GET DRIVER'S ASSIGNED PACKAGES
            elif action == 'get_my_packages':
                driver_id = data.get('driver_id')
                packages = self.courier_service.get_driver_packages(driver_id)
                
                return {
                    'status': 'success',
                    'packages': [p.to_dict() for p in packages]
                }
            
            # UPDATE PACKAGE STATUS
            elif action == 'update_package_status':
                package_id = data.get('package_id')
                status = data.get('status')
                
                if self.courier_service.update_package_status(package_id, status):
                    return {
                        'status': 'success',
                        'message': 'Package status updated'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Failed to update status'
                    }
            
            # COMPLETE DELIVERY
            elif action == 'complete_delivery':
                package_id = data.get('package_id')
                
                if self.courier_service.complete_delivery(package_id):
                    return {
                        'status': 'success',
                        'message': 'Delivery completed!'
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Failed to complete delivery'
                    }
            
            # GET DRIVER INFO
            elif action == 'get_driver_info':
                driver_id = data.get('driver_id')
                driver = self.courier_service.get_driver(driver_id)
                
                if driver:
                    return {
                        'status': 'success',
                        'driver': driver.to_dict()
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Driver not found'
                    }
            
            # GET PACKAGE DETAILS
            elif action == 'get_package_details':
                package_id = data.get('package_id')
                package = self.courier_service.get_package(package_id)
                
                if package:
                    return {
                        'status': 'success',
                        'package': package.to_dict()
                    }
                else:
                    return {
                        'status': 'error',
                        'message': 'Package not found'
                    }
            
            else:
                return {
                    'status': 'error',
                    'message': 'Unknown action'
                }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def admin_interface(self):
        """Admin interface for company operations"""
        print("\n🏢 ADMIN INTERFACE READY")
        print("Type 'help' for available commands\n")
        
        while self.running:
            try:
                command = input("ADMIN> ").strip().lower()
                
                if command == 'help':
                    self.show_admin_help()
                
                elif command == 'add_driver':
                    self.admin_add_driver()
                
                elif command == 'list_drivers':
                    self.admin_list_drivers()
                
                elif command == 'add_package':
                    self.admin_add_package()
                
                elif command == 'list_packages':
                    self.admin_list_packages()
                
                elif command == 'assign':
                    self.admin_assign_package()
                
                elif command == 'stats':
                    self.admin_show_stats()
                
                elif command == 'clients':
                    print(f"\n✓ Connected clients: {len(self.clients)}")
                
                elif command == 'stop':
                    self.running = False
                    print("Shutting down server...")
                    break
                
                elif command:
                    print("Unknown command. Type 'help' for available commands.")
            
            except Exception as e:
                print(f"Error: {e}")
    
    def show_admin_help(self):
        """Show available admin commands"""
        print("\n" + "="*60)
        print("ADMIN COMMANDS")
        print("="*60)
        print("add_driver       - Register a new driver")
        print("list_drivers     - View all drivers")
        print("add_package      - Create a new package")
        print("list_packages    - View all packages")
        print("assign           - Assign package to driver")
        print("stats            - View system statistics")
        print("clients          - Show connected clients")
        print("stop             - Stop the server")
        print("help             - Show this help message")
        print("="*60 + "\n")
    
    def admin_add_driver(self):
        """Admin: Add a new driver"""
        print("\n--- ADD NEW DRIVER ---")
        driver_id = input("Driver ID: ")
        name = input("Name: ")
        phone = input("Phone: ")
        vehicle = input("Vehicle Type (bike/van/truck): ")
        
        driver = Driver(driver_id, name, phone, vehicle)
        
        if self.courier_service.add_driver(driver):
            print(f"✓ Driver {name} added successfully!")
        else:
            print(f"✗ Driver ID {driver_id} already exists!")
    
    def admin_list_drivers(self):
        """Admin: List all drivers"""
        drivers = self.courier_service.get_all_drivers()
        
        print(f"\n--- ALL DRIVERS ({len(drivers)}) ---")
        print(f"{'ID':<10} {'Name':<20} {'Status':<12} {'Load':<8} {'Deliveries'}")
        print("-" * 65)
        
        for driver in drivers:
            print(f"{driver.driver_id:<10} {driver.name:<20} {driver.status:<12} "
                  f"{len(driver.assigned_packages):<8} {driver.total_deliveries}")
        print()
    
    def admin_add_package(self):
        """Admin: Add a new package"""
        print("\n--- CREATE NEW PACKAGE ---")
        package_id = input("Package ID: ")
        sender_name = input("Sender Name: ")
        sender_address = input("Sender Address: ")
        recipient_name = input("Recipient Name: ")
        recipient_address = input("Recipient Address: ")
        weight = float(input("Weight (kg): "))
        
        package = Package(package_id, sender_name, sender_address,
                         recipient_name, recipient_address, weight)
        
        if self.courier_service.add_package(package):
            print(f"✓ Package {package_id} created successfully!")
        else:
            print(f"✗ Package ID {package_id} already exists!")
    
    def admin_list_packages(self):
        """Admin: List all packages"""
        packages = self.courier_service.get_all_packages()
        
        print(f"\n--- ALL PACKAGES ({len(packages)}) ---")
        print(f"{'ID':<10} {'Recipient':<20} {'Status':<15} {'Driver':<10}")
        print("-" * 60)
        
        for package in packages:
            driver_id = package.assigned_driver if package.assigned_driver else "None"
            print(f"{package.package_id:<10} {package.recipient_name:<20} "
                  f"{package.status:<15} {driver_id:<10}")
        print()
    
    def admin_assign_package(self):
        """Admin: Assign package to driver"""
        package_id = input("\nPackage ID: ")
        driver_id = input("Driver ID: ")
        
        if self.courier_service.assign_package_to_driver(package_id, driver_id):
            print("✓ Package assigned successfully!")
        else:
            print("✗ Failed to assign package!")
    
    def admin_show_stats(self):
        """Admin: Show system statistics"""
        summary = self.courier_service.get_package_summary()
        drivers = self.courier_service.get_all_drivers()
        
        print("\n" + "="*50)
        print("SYSTEM STATISTICS")
        print("="*50)
        print(f"Total Drivers: {len(drivers)}")
        print(f"Connected Clients: {len(self.clients)}")
        print(f"\nPackage Summary:")
        print(f"  Total: {summary['total']}")
        print(f"  Pending: {summary['pending']}")
        print(f"  In Transit: {summary['in_transit']}")
        print(f"  Delivered: {summary['delivered']}")
        print("="*50 + "\n")
    
    def stop_server(self):
        """Stop the server and close all connections"""
        self.running = False
        
        # Close all client connections
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
        
        # Close database connection
        self.db_handler.close()
        
        print("\n✓ Server stopped successfully")

# Run the server
if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║   COURIER SERVICE - SERVER SIDE (COMPANY)  ║
    ║          LUQMAN COURIER SERVICE            ║
    ║              SQL DATABASE VERSION          ║
    ╚════════════════════════════════════════════╝
    """)
    
    server = CourierServer(host='0.0.0.0', port=5006)
    
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        server.stop_server()