# client_driver_sql.py - CLIENT SIDE 
# CLIENT SIDE - Driver Application
# This runs on the driver's device (Luqman's laptop)
# It connects to the server to get deliveries and update status

import socket
import json
import os

class DriverClient:
    """Client application for delivery drivers"""
    
    def __init__(self, host='localhost', port=5000):
        """
        Initialize the driver client
        
        Args:
            host (str): Server IP address
            port (int): Server port number
        """
        self.host = host
        self.port = port
        self.client_socket = None
        self.driver_id = None
        self.driver_name = None
        self.connected = False
    
    def connect_to_server(self):
        """Connect to the courier service server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            print(f"✓ Connected to server at {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to server: {e}")
            print(f"Make sure the server is running!")
            return False
    
    def send_request(self, action, data=None):
        """
        Send request to server and get response
        
        Args:
            action (str): Action to perform
            data (dict): Additional data for the request
        
        Returns:
            dict: Server response
        """
        try:
            request = {
                'action': action,
                'data': data or {}
            }
            
            # Send request
            self.client_socket.send(json.dumps(request).encode('utf-8'))
            
            # Receive response
            response_data = self.client_socket.recv(4096).decode('utf-8')
            response = json.loads(response_data)
            
            return response
        
        except Exception as e:
            print(f"Error communicating with server: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def login(self):
        """Driver login"""
        print("\n" + "="*50)
        print("DRIVER LOGIN")
        print("="*50)
        
        driver_id = input("Enter your Driver ID: ").strip()
        
        response = self.send_request('login', {'driver_id': driver_id})
        
        if response['status'] == 'success':
            self.driver_id = driver_id
            driver_data = response['driver']
            self.driver_name = driver_data['name']
            
            print(f"\n✓ {response['message']}")
            print(f"Status: {driver_data['status']}")
            print(f"Total Deliveries: {driver_data['total_deliveries']}")
            print(f"Current Load: {len(driver_data['assigned_packages'])} packages")
            return True
        else:
            print(f"\n✗ {response['message']}")
            return False
    
    def view_my_packages(self):
        """View packages assigned to this driver"""
        response = self.send_request('get_my_packages', {'driver_id': self.driver_id})
        
        if response['status'] == 'success':
            packages = response['packages']
            
            print(f"\n{'='*70}")
            print(f"MY ASSIGNED PACKAGES ({len(packages)})")
            print(f"{'='*70}")
            
            if not packages:
                print("No packages assigned yet.")
            else:
                print(f"{'ID':<12} {'Recipient':<20} {'Address':<25} {'Status':<15}")
                print("-" * 70)
                
                for package in packages:
                    print(f"{package['package_id']:<12} "
                          f"{package['recipient_name']:<20} "
                          f"{package['recipient_address']:<25} "
                          f"{package['status']:<15}")
            
            print("="*70 + "\n")
        else:
            print(f"✗ {response['message']}")
    
    def view_package_details(self):
        """View detailed information about a specific package"""
        package_id = input("\nEnter Package ID: ").strip()
        
        response = self.send_request('get_package_details', {'package_id': package_id})
        
        if response['status'] == 'success':
            package = response['package']
            
            print("\n" + "="*60)
            print("PACKAGE DETAILS")
            print("="*60)
            print(f"Package ID: {package['package_id']}")
            print(f"Status: {package['status']}")
            print(f"\nSender:")
            print(f"  Name: {package['sender_name']}")
            print(f"  Address: {package['sender_address']}")
            print(f"\nRecipient:")
            print(f"  Name: {package['recipient_name']}")
            print(f"  Address: {package['recipient_address']}")
            print(f"\nPackage Info:")
            print(f"  Weight: {package['weight']} kg")
            print(f"  Created: {package['created_at']}")
            
            if package['delivered_at']:
                print(f"  Delivered: {package['delivered_at']}")
            
            print("="*60 + "\n")
        else:
            print(f"✗ {response['message']}")
    
    def update_package_status(self):
        """Update the status of a package"""
        package_id = input("\nEnter Package ID: ").strip()
        
        print("\nSelect new status:")
        print("1. Picked Up")
        print("2. In Transit")
        print("3. Out for Delivery")
        
        choice = input("Enter choice (1-3): ").strip()
        
        status_map = {
            '1': 'picked_up',
            '2': 'in_transit',
            '3': 'out_for_delivery'
        }
        
        if choice in status_map:
            response = self.send_request('update_package_status', {
                'package_id': package_id,
                'status': status_map[choice]
            })
            
            if response['status'] == 'success':
                print(f"✓ {response['message']}")
            else:
                print(f"✗ {response['message']}")
        else:
            print("Invalid choice!")
    
    def complete_delivery(self):
        """Mark a delivery as complete"""
        package_id = input("\nEnter Package ID to mark as delivered: ").strip()
        
        confirm = input(f"Confirm delivery of package {package_id}? (yes/no): ").lower()
        
        if confirm == 'yes':
            response = self.send_request('complete_delivery', {'package_id': package_id})
            
            if response['status'] == 'success':
                print(f"\n🎉 {response['message']}")
                print("Great job! Delivery completed successfully.")
            else:
                print(f"✗ {response['message']}")
        else:
            print("Delivery not marked as complete.")
    
    def view_my_stats(self):
        """View personal driver statistics"""
        response = self.send_request('get_driver_info', {'driver_id': self.driver_id})
        
        if response['status'] == 'success':
            driver = response['driver']
            
            print("\n" + "="*50)
            print("MY STATISTICS")
            print("="*50)
            print(f"Driver ID: {driver['driver_id']}")
            print(f"Name: {driver['name']}")
            print(f"Phone: {driver['phone']}")
            print(f"Vehicle: {driver['vehicle_type']}")
            print(f"Status: {driver['status']}")
            print(f"Total Deliveries Completed: {driver['total_deliveries']}")
            print(f"Current Active Packages: {len(driver['assigned_packages'])}")
            print("="*50 + "\n")
        else:
            print(f"✗ {response['message']}")
    
    def display_menu(self):
        """Display main menu for driver"""
        print("\n" + "="*50)
        print(f"DRIVER MENU - {self.driver_name} ({self.driver_id})")
        print("="*50)
        print("1. View My Assigned Packages")
        print("2. View Package Details")
        print("3. Update Package Status")
        print("4. Complete Delivery")
        print("5. View My Statistics")
        print("6. Logout")
        print("-"*50)
    
    def run(self):
        """Main application loop"""
        print("""
    ╔════════════════════════════════════════════╗
    ║   COURIER SERVICE - DRIVER APPLICATION     ║
    ║         (CLIENT SIDE)                      ║
    ╚════════════════════════════════════════════╝
        """)
        
        # Connect to server
        if not self.connect_to_server():
            return
        
        # Login
        if not self.login():
            self.disconnect()
            return
        
        # Main menu loop
        while self.connected:
            try:
                self.display_menu()
                choice = input("Enter your choice: ").strip()
                
                if choice == '1':
                    self.view_my_packages()
                
                elif choice == '2':
                    self.view_package_details()
                
                elif choice == '3':
                    self.update_package_status()
                
                elif choice == '4':
                    self.complete_delivery()
                
                elif choice == '5':
                    self.view_my_stats()
                
                elif choice == '6':
                    print("\nLogging out...")
                    self.disconnect()
                    break
                
                else:
                    print("Invalid choice! Please try again.")
                
                input("\nPress Enter to continue...")
                self.clear_screen()
            
            except Exception as e:
                print(f"Error: {e}")
                break
    
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def disconnect(self):
        """Disconnect from server"""
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        self.connected = False
        print("✓ Disconnected from server")
        print("Thank you for your service!")

# Run the client
if __name__ == "__main__":
    # You can change these to connect to a different server
    SERVER_HOST = 'localhost'  # Change to server IP if on different computer
    SERVER_PORT = 5000
    
    client = DriverClient(host=SERVER_HOST, port=SERVER_PORT)
    
    try:
        client.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        client.disconnect()