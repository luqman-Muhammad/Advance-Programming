# app_backend.py - Backend API with Real-time Updates
# BACKEND API SERVER - Flask + SocketIO
# It provides REST API endpoints and WebSocket for real-time updates

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from datetime import datetime
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import your existing models and services
from models.driver_sql import Driver
from models.package_sql import Package
from services.courier_service_sql import CourierService
from database.db_handler import DatabaseHandler

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Enable CORS for frontend communication
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO for real-time updates with eventlet async mode
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize database and courier service
db_handler = DatabaseHandler(
    server='localhost',
    database='CourierDB',
    use_windows_auth=True
)
courier_service = CourierService(db_handler)

# Initialize database tables
try:
    db_handler.create_tables()
    print("✓ Database initialized successfully!")
except Exception as e:
    print(f"Error initializing database: {e}")

# ==================== HELPER FUNCTIONS ====================

def broadcast_update(event_type, data):
    """Broadcast updates to all connected clients"""
    socketio.emit('update', {
        'type': event_type,
        'data': data,
        'timestamp': datetime.now().isoformat()
    })

def notify_driver(driver_id, message, data=None):
    """Send notification to specific driver"""
    socketio.emit('notification', {
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }, room=f'driver_{driver_id}')

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"✓ Client connected: {request.sid}")
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"✗ Client disconnected: {request.sid}")

@socketio.on('join_driver_room')
def handle_join_driver_room(data):
    """Driver joins their personal room for notifications"""
    driver_id = data.get('driver_id')
    join_room(f'driver_{driver_id}')
    print(f"Driver {driver_id} joined their room")
    emit('joined_room', {'driver_id': driver_id})

@socketio.on('leave_driver_room')
def handle_leave_driver_room(data):
    """Driver leaves their personal room"""
    driver_id = data.get('driver_id')
    leave_room(f'driver_{driver_id}')
    print(f"Driver {driver_id} left their room")

# ==================== REST API ENDPOINTS ====================

# ========== DRIVER ENDPOINTS ==========

@app.route('/api/drivers', methods=['GET'])
def get_all_drivers():
    """Get all drivers"""
    try:
        drivers = courier_service.get_all_drivers()
        return jsonify({
            'status': 'success',
            'data': [driver.to_dict() for driver in drivers]
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/drivers/<driver_id>', methods=['GET'])
def get_driver(driver_id):
    """Get specific driver"""
    try:
        driver = courier_service.get_driver(driver_id)
        if driver:
            return jsonify({
                'status': 'success',
                'data': driver.to_dict()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Driver not found'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/drivers', methods=['POST'])
def add_driver():
    """Add new driver"""
    try:
        data = request.json
        driver = Driver(
            driver_id=data['driver_id'],
            name=data['name'],
            phone=data['phone'],
            vehicle_type=data['vehicle_type']
        )
        
        if courier_service.add_driver(driver):
            # Broadcast update to all clients
            broadcast_update('driver_added', driver.to_dict())
            
            return jsonify({
                'status': 'success',
                'message': f'Driver {driver.name} added successfully',
                'data': driver.to_dict()
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'Driver ID already exists'
            }), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/drivers/<driver_id>/status', methods=['PUT'])
def update_driver_status(driver_id):
    """Update driver status"""
    try:
        data = request.json
        status = data.get('status')
        
        if courier_service.update_driver_status(driver_id, status):
            driver = courier_service.get_driver(driver_id)
            
            # Broadcast update
            broadcast_update('driver_status_updated', {
                'driver_id': driver_id,
                'status': status
            })
            
            # Notify the driver
            notify_driver(driver_id, f'Your status has been updated to {status}')
            
            return jsonify({
                'status': 'success',
                'message': 'Driver status updated',
                'data': driver.to_dict() if driver else None
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update driver status'
            }), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/drivers/<driver_id>/packages', methods=['GET'])
def get_driver_packages(driver_id):
    """Get packages assigned to driver"""
    try:
        packages = courier_service.get_driver_packages(driver_id)
        return jsonify({
            'status': 'success',
            'data': [package.to_dict() for package in packages]
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ========== PACKAGE ENDPOINTS ==========

@app.route('/api/packages', methods=['GET'])
def get_all_packages():
    """Get all packages"""
    try:
        packages = courier_service.get_all_packages()
        return jsonify({
            'status': 'success',
            'data': [package.to_dict() for package in packages]
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/packages/<package_id>', methods=['GET'])
def get_package(package_id):
    """Get specific package"""
    try:
        package = courier_service.get_package(package_id)
        if package:
            return jsonify({
                'status': 'success',
                'data': package.to_dict()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Package not found'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/packages', methods=['POST'])
def add_package():
    """Add new package"""
    try:
        data = request.json
        package = Package(
            package_id=data['package_id'],
            sender_name=data['sender_name'],
            sender_address=data['sender_address'],
            recipient_name=data['recipient_name'],
            recipient_address=data['recipient_address'],
            weight=float(data['weight'])
        )
        
        if courier_service.add_package(package):
            # Broadcast update
            broadcast_update('package_added', package.to_dict())
            
            return jsonify({
                'status': 'success',
                'message': f'Package {package.package_id} created successfully',
                'data': package.to_dict()
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'Package ID already exists'
            }), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/packages/<package_id>/status', methods=['PUT'])
def update_package_status(package_id):
    """Update package status"""
    try:
        data = request.json
        status = data.get('status')
        
        if courier_service.update_package_status(package_id, status):
            package = courier_service.get_package(package_id)
            
            # Broadcast update
            broadcast_update('package_status_updated', {
                'package_id': package_id,
                'status': status
            })
            
            # Notify assigned driver
            if package and package.assigned_driver:
                notify_driver(
                    package.assigned_driver,
                    f'Package {package_id} status updated to {status}'
                )
            
            return jsonify({
                'status': 'success',
                'message': 'Package status updated',
                'data': package.to_dict() if package else None
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update package status'
            }), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/packages/<package_id>/assign', methods=['POST'])
def assign_package(package_id):
    """Assign package to driver"""
    try:
        data = request.json
        driver_id = data.get('driver_id')
        
        if courier_service.assign_package_to_driver(package_id, driver_id):
            package = courier_service.get_package(package_id)
            driver = courier_service.get_driver(driver_id)
            
            # Broadcast update
            broadcast_update('package_assigned', {
                'package_id': package_id,
                'driver_id': driver_id
            })
            
            # Notify driver
            notify_driver(
                driver_id,
                f'New package assigned: {package_id}',
                package.to_dict() if package else None
            )
            
            return jsonify({
                'status': 'success',
                'message': f'Package assigned to {driver.name}',
                'data': {
                    'package': package.to_dict() if package else None,
                    'driver': driver.to_dict() if driver else None
                }
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to assign package'
            }), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/packages/<package_id>/complete', methods=['POST'])
def complete_delivery(package_id):
    """Mark delivery as complete"""
    try:
        if courier_service.complete_delivery(package_id):
            package = courier_service.get_package(package_id)
            
            # Broadcast update
            broadcast_update('delivery_completed', {
                'package_id': package_id
            })
            
            # Notify driver
            if package and package.assigned_driver:
                notify_driver(
                    package.assigned_driver,
                    f'Delivery completed: {package_id}! Great job! 🎉'
                )
            
            return jsonify({
                'status': 'success',
                'message': 'Delivery completed successfully',
                'data': package.to_dict() if package else None
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to complete delivery'
            }), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ========== STATISTICS ENDPOINTS ==========

@app.route('/api/stats/packages', methods=['GET'])
def get_package_stats():
    """Get package statistics"""
    try:
        summary = courier_service.get_package_summary()
        return jsonify({
            'status': 'success',
            'data': summary
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/stats/drivers', methods=['GET'])
def get_driver_stats():
    """Get driver statistics"""
    try:
        drivers = courier_service.get_all_drivers()
        
        stats = {
            'total_drivers': len(drivers),
            'available_drivers': len([d for d in drivers if d.status == 'available']),
            'busy_drivers': len([d for d in drivers if d.status == 'busy']),
            'total_deliveries': sum(d.total_deliveries for d in drivers),
            'top_performers': sorted(
                [{'driver_id': d.driver_id, 'name': d.name, 'deliveries': d.total_deliveries} 
                 for d in drivers],
                key=lambda x: x['deliveries'],
                reverse=True
            )[:5]
        }
        
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ========== AUTHENTICATION ENDPOINT ==========

@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint for drivers"""
    try:
        data = request.json
        driver_id = data.get('driver_id')
        
        driver = courier_service.get_driver(driver_id)
        
        if driver:
            return jsonify({
                'status': 'success',
                'message': f'Welcome {driver.name}!',
                'data': driver.to_dict()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Driver not found'
            }), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'API is running',
        'timestamp': datetime.now().isoformat()
    }), 200

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════╗
    ║   COURIER SERVICE - BACKEND API SERVER     ║
    ║      WITH REAL-TIME WEBSOCKET UPDATES      ║
    ╚════════════════════════════════════════════╝
    """)
    print("✓ Starting Flask + SocketIO server...")
    print("✓ REST API: http://localhost:5006/api")
    print("✓ WebSocket: ws://localhost:5006")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run with SocketIO using eventlet
    socketio.run(app, host='0.0.0.0', port=5005, debug=True)