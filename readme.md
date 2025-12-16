# Luqman Courier Service Management System

## Setup Instructions

1. **Database Setup:**
   - Open SQL Server Management Studio
   - Run `database/CA2_database.sql`

2. **Install Dependencies:**
```bash
   pip install -r requirements.txt
```

3. **Run Backend Server:**
```bash
   python app_backend.py
```
   Server will run on: http://localhost:5003     ##port 5000 or port 1234 can be used as well

4. **Access Web Interfaces:**
   - Admin Dashboard: Open `admin_dashboard_frontend.html` in browser
   - Driver Dashboard: Open `driver_dashboard_frontend.html` in browser

## Testing

Run unit tests:
```bash
python tests/test_suite.py
```

## Project Structure
- `server and backend` - Server-side code
- `client and frontend` - Desktop/console clients & Web interfaces 
- `database/` - Database setup
- `models/` - Data models
- `services/` - Business logic

- `tests/` - Unit tests
