USE master;
GO

-- Close all connections to CourierDB
ALTER DATABASE CourierDB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
GO

-- Now drop the database
DROP DATABASE CourierDB;
GO

-- Create fresh database
CREATE DATABASE CourierDB;
GO

USE CourierDB;
GO

---------------------------------------------------
-- Create Tables
---------------------------------------------------

-- Drivers table (FIXED to match Python code)
CREATE TABLE Drivers (
    driver_id VARCHAR(50) PRIMARY KEY,  -- Changed from INT to VARCHAR
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL CHECK (vehicle_type IN ('bike','van','truck')),
    status VARCHAR(20) DEFAULT 'available',  -- Changed from 'availability BIT' to 'status VARCHAR'
    total_deliveries INT DEFAULT 0  -- ADDED: Missing in your schema
);

-- Packages table (FIXED to match Python code)
CREATE TABLE Packages (
    package_id VARCHAR(50) PRIMARY KEY,  -- Changed from INT to VARCHAR
    sender_name VARCHAR(100) NOT NULL,
    sender_address VARCHAR(255) NOT NULL,
    recipient_name VARCHAR(100) NOT NULL,
    recipient_address VARCHAR(255) NOT NULL,
    weight DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- ADDED: Missing in your schema
    assigned_driver VARCHAR(50),  -- Changed from 'driver_id INT' to 'assigned_driver VARCHAR'
    created_at DATETIME DEFAULT GETDATE(),  -- ADDED: Missing in your schema
    delivered_at DATETIME NULL,  -- ADDED: Missing in your schema
    FOREIGN KEY (assigned_driver) REFERENCES Drivers(driver_id) ON DELETE SET NULL
);

-- JobEvents table (Optional - for tracking)
CREATE TABLE JobEvents (
    event_id INT IDENTITY(1,1) PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL,  -- Changed to VARCHAR
    timestamp DATETIME DEFAULT GETDATE(),
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('created','assigned','in_transit','delivered','cancelled')),
    metadata VARCHAR(255),
    FOREIGN KEY (job_id) REFERENCES Packages(package_id) ON DELETE CASCADE
);

-- DeliveryProof table (Optional)
CREATE TABLE DeliveryProof (
    proof_id INT IDENTITY(1,1) PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL,  -- Changed to VARCHAR
    recipient_name VARCHAR(100),
    delivered_at DATETIME DEFAULT GETDATE(),
    note VARCHAR(255),
    photo_ref VARCHAR(255),
    FOREIGN KEY (job_id) REFERENCES Packages(package_id) ON DELETE CASCADE
);

---------------------------------------------------
-- Insert Sample Data
---------------------------------------------------

-- Insert Drivers (using VARCHAR driver_id)
INSERT INTO Drivers (driver_id, name, phone, vehicle_type, status, total_deliveries) VALUES
('D001', 'Ramesh Kumar', '2581473695', 'truck', 'available', 0),
('D002', 'Anita Sharma', '9876543210', 'bike', 'available', 0),
('D003', 'John O''Connor', '8765432109', 'van', 'available', 0),
('D004', 'Priya Nair', '7418529630', 'truck', 'available', 0),
('D005', 'Ahmed Khan', '9632587410', 'bike', 'available', 0),
('D006', 'Maria Lopez', '8521479632', 'van', 'available', 0),
('D007', 'Chen Wei', '9517538426', 'truck', 'available', 0),
('D008', 'Sarah Johnson', '7894561230', 'bike', 'available', 0),
('D009', 'David Murphy', '6547893210', 'van', 'available', 0),
('D010', 'Kavita Singh', '3216549870', 'truck', 'available', 0);

-- Insert Packages (using VARCHAR package_id)
INSERT INTO Packages (package_id, sender_name, sender_address, recipient_name, recipient_address, weight, status, assigned_driver) VALUES
('P100', 'Ruben Dsouza', '123 Main Street, Dublin 1, D01 A1B2', 'Ruth Dsouza', '456 Oak Avenue, Dublin 22, D22 G5E6', 5.0, 'pending', NULL),
('P101', 'Sophie Martin', '78 River Road, Galway, H91 D5E6', 'Ethan Kelly', '23 Pine Lane, Limerick, V94 F7G8', 2.1, 'pending', NULL),
('P102', 'Lucas Wright', '56 College Street, Waterford, X91 H2J3', 'Chloe Evans', '67 Birch Grove, Dublin 14, D14 K9L0', 6.8, 'pending', NULL),
('P103', 'Isabella Moore', '34 Castle Road, Kilkenny, R95 M4N5', 'Daniel Hughes', '89 Willow Drive, Dublin 6, D06 P7Q8', 3.4, 'pending', NULL),
('P104', 'Benjamin Scott', '90 Harbour Street, Belfast, BT1 3AB', 'Grace Foster', '12 Rosewood Avenue, Dublin 11, D11 R2S3', 5.9, 'pending', NULL),
('P105', 'Amelia Turner', '21 Station Road, Sligo, F91 T4U5', 'Matthew Hall', '77 Maple Street, Dublin 16, D16 V8W9', 7.2, 'pending', NULL),
('P106', 'Jack Wilson', '88 Church Lane, Tralee, V92 D6E7', 'Lily Adams', '101 Cedar Grove, Dublin 5, D05 X9Y0', 1.7, 'pending', NULL),
('P107', 'Emily Carter', '33 Market Street, Dundalk, A91 B4C5', 'Ryan Bennett', '65 Elm Crescent, Dublin 19, D19 Z2X3', 8.0, 'pending', NULL),
('P108', 'Henry Walker', '67 High Street, Athlone, N37 Y5Z6', 'Zoe Mitchell', '50 Rose Lane, Dublin 10, D10 Y3Z4', 2.9, 'pending', NULL),
('P109', 'Charlotte Green', '45 Park Road, Ennis, V95 C7D8', 'Thomas Edwards', '14 Sycamore Drive, Dublin 21, D21 H4J5', 5.3, 'pending', NULL);

-- Insert initial JobEvents
INSERT INTO JobEvents (job_id, event_type, metadata) VALUES
('P100', 'created', 'Package created'),
('P101', 'created', 'Package created'),
('P102', 'created', 'Package created'),
('P103', 'created', 'Package created'),
('P104', 'created', 'Package created'),
('P105', 'created', 'Package created'),
('P106', 'created', 'Package created'),
('P107', 'created', 'Package created'),
('P108', 'created', 'Package created'),
('P109', 'created', 'Package created');

---------------------------------------------------
-- Verify Installation
---------------------------------------------------
PRINT '---------------------------------------------------';
PRINT 'Database Setup Complete!';
PRINT '---------------------------------------------------';

-- Show table counts
SELECT 'Drivers' AS TableName, COUNT(*) AS RecordCount FROM Drivers
UNION ALL
SELECT 'Packages', COUNT(*) FROM Packages
UNION ALL
SELECT 'JobEvents', COUNT(*) FROM JobEvents
UNION ALL
SELECT 'DeliveryProof', COUNT(*) FROM DeliveryProof;

PRINT '';
PRINT 'Tables created successfully:';
PRINT '? Drivers (10 records, status VARCHAR, total_deliveries added)';
PRINT '? Packages (10 records, status column added, VARCHAR IDs)';
PRINT '? JobEvents (10 records)';
PRINT '? DeliveryProof (empty)';
PRINT '';
PRINT 'Schema is now compatible with Python application!';
GO