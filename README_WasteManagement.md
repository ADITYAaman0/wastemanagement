# 🌱 Smart Waste Management System

A comprehensive web application for intelligent waste management, built with Python and Streamlit. This system facilitates efficient waste collection, tracking, and management while promoting environmental sustainability through gamification and community engagement.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit] https://wastemanagement-pdxmbg8lubf6r6zlj33vdy.streamlit.app/
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [User Guide](#-user-guide)
- [Technologies Used](#-technologies-used)
- [Database Schema](#-database-schema)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🏠 For Citizens
- **Schedule Waste Collection**: Book waste pickup with location tracking
- **Real-time Tracking**: Monitor collection status and vehicle locations
- **Complaint Management**: Report issues with photo uploads
- **Reward System**: Earn points for proper waste segregation
- **Eco Shop**: Redeem points for eco-friendly products
- **Training Modules**: Interactive learning about waste management
- **QR Code Generation**: Unique waste ID for each user

### 👨‍💼 For Administrators
- **Dashboard Analytics**: Real-time statistics and KPIs
- **User Management**: Complete user directory and management
- **Facility Management**: Track and manage waste processing facilities
- **Vehicle Tracking**: Live GPS tracking of collection vehicles
- **Report Generation**: Comprehensive reports with data export
- **3D Visualizations**: Advanced data visualization capabilities

### 👷 For Workers
- **Collection Management**: View and update daily collection schedules
- **Route Optimization**: Efficient route planning with maps
- **Vehicle Status Updates**: Real-time vehicle location updates
- **Performance Tracking**: Monitor collection efficiency

## 🏗️ System Architecture

```
smart-waste-management/
│
├── web_app_wastemanagement.py    # Main application file
├── waste_management.db            # SQLite database (auto-generated)
├── README_WasteManagement.md      # This documentation
└── requirements.txt               # Python dependencies
```

### Core Components

1. **Authentication System**: Custom authentication with role-based access control
2. **Database Layer**: SQLite with structured tables for all entities
3. **Visualization Engine**: Plotly for interactive charts and 3D visualizations
4. **Mapping System**: Folium for interactive maps and location tracking
5. **Reward System**: Gamification to encourage proper waste segregation

## 💻 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Windows/Linux/macOS operating system

### Step 1: Create Project Directory

```bash
# Windows
mkdir "C:\SmartWaste"
cd "C:\SmartWaste"

# Linux/Mac
mkdir ~/smart-waste
cd ~/smart-waste
```

### Step 2: Create Requirements File

Create a file named `requirements.txt` with the following content:

```txt
streamlit>=1.49.0
pandas>=2.3.0
numpy>=2.3.0
plotly>=5.24.0
folium>=0.19.0
streamlit-folium>=0.22.0
streamlit-option-menu>=0.3.13
qrcode>=8.0
Pillow>=11.0.0
scikit-learn>=1.5.0
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Or install individually
pip install streamlit pandas numpy plotly folium streamlit-folium streamlit-option-menu qrcode Pillow scikit-learn
```

### Step 4: Verify Installation

```bash
# Check Python version
python --version

# Check Streamlit installation
streamlit version
```

## 🚀 Quick Start

### Running the Application

```bash
# Navigate to project directory
cd "C:\New Folder"  # or your project directory

# Run the application
python -m streamlit run web_app_wastemanagement.py

# Alternative command
streamlit run web_app_wastemanagement.py
```

The application will automatically:
- Open in your default browser at `http://localhost:8501`
- Create a SQLite database if it doesn't exist
- Populate sample data for testing

### Default Login Credentials

#### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Access**: Full system control

#### Sample User Accounts
- **Username**: `user1` | **Password**: `user1123`
- **Username**: `user2` | **Password**: `user2123`
- **Username**: `user3` | **Password**: `user3123`
- ... up to `user10`

## 📖 User Guide

### For Citizens

#### 1. Registration Process
1. Click "Register" on the login page
2. Enter required information:
   - Username (unique)
   - Email address
   - Password
   - Full name
   - Phone number
   - Address
   - Ward number
3. System generates unique waste ID
4. Receive QR code for identification
5. Start with bonus registration points

#### 2. Scheduling Waste Collection
1. Login with credentials
2. Navigate to "Schedule Collection"
3. Fill collection details:
   - Select waste type (Wet/Dry/Hazardous/E-waste)
   - Enter estimated weight (kg)
   - Choose collection date
   - Mark segregation status
   - Provide location coordinates
4. Submit request
5. Earn points based on:
   - Proper segregation: 10 points
   - Without segregation: 5 points

#### 3. Tracking Collections
- View all collections on interactive map
- Check status: Scheduled/Collected/Processed
- Monitor collection history
- Track total waste contributed
- View earned points balance

#### 4. Filing Complaints
1. Go to "Complaints" section
2. Select complaint type:
   - Missed Collection
   - Overflowing Bins
   - Improper Disposal
   - Vehicle Issues
   - Facility Problems
3. Provide description and location
4. Upload supporting images (optional)
5. Track complaint status

#### 5. Eco Shop
- Browse eco-friendly products
- Filter by category:
  - Equipment
  - Composting
  - Accessories
  - Garden
  - Technology
  - Safety
- View product details and points required
- Redeem points for products
- Check stock availability

#### 6. Training Modules
Complete interactive training to earn points:
- **Waste Classification**: 50 points (30 min)
- **Source Segregation**: 75 points (45 min)
- **Home Composting**: 100 points (60 min)
- **Plastic Management**: 80 points (40 min)

### For Administrators

#### Dashboard Features
- **Total Users**: Monitor registered users
- **Waste Collected**: Track total weight in kg
- **Active Complaints**: View pending issues
- **Facilities**: Monitor processing centers

#### User Management
- View complete user directory
- Filter by:
  - User type (citizen/worker/admin)
  - Ward number
  - Registration date
- Monitor user points and activity
- Export user data

#### Facility Management
- Add new facilities with:
  - Name and type
  - Address and coordinates
  - Capacity (TPD)
  - Contact information
  - Operational hours
- View facilities on map
- Monitor capacity utilization

#### Vehicle Management
- Track all vehicles in real-time
- Monitor status:
  - Collecting (Active)
  - Idle
  - Maintenance
- View vehicle details:
  - Vehicle number
  - Type and capacity
  - Driver information
  - Current location

#### Reports & Analytics
- Generate date-range reports
- View collection trends
- Analyze ward-wise performance
- Export data as CSV
- 3D visualizations:
  - Waste distribution by ward
  - Facility capacity analysis
  - Collection pattern surfaces

### For Workers

#### Daily Collections
- View assigned collections
- Update collection status
- Add vehicle information
- Mark completions

#### Vehicle Tracking
- Update GPS location
- Change vehicle status
- View assigned routes
- Monitor capacity

## 🛠️ Technologies Used

### Core Technologies
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Backend programming |
| Streamlit | 1.49+ | Web framework |
| SQLite3 | Built-in | Database |
| Pandas | 2.3+ | Data manipulation |
| NumPy | 2.3+ | Numerical operations |

### Visualization & UI
| Technology | Purpose |
|------------|---------|
| Plotly | Interactive charts & 3D visualizations |
| Folium | Interactive maps |
| Streamlit-Folium | Map integration |
| Streamlit-Option-Menu | Navigation menu |
| QRCode | QR code generation |
| PIL (Pillow) | Image processing |

### Security
| Technology | Purpose |
|------------|---------|
| Hashlib | SHA-256 password hashing |
| Secrets | Token generation |
| Base64 | Data encoding |

## 🗄️ Database Schema

### Users Table
```sql
users (
    id, username, email, password_hash, full_name,
    phone, address, user_type, ward_number,
    unique_waste_id, registration_date,
    training_completed, points
)
```

### Waste Collections Table
```sql
waste_collections (
    id, user_id, collection_date, waste_type,
    weight_kg, segregated, collected_by,
    vehicle_number, status, latitude, longitude
)
```

### Complaints Table
```sql
complaints (
    id, user_id, complaint_type, description,
    location, latitude, longitude, status,
    created_date, resolved_date
)
```

### Facilities Table
```sql
facilities (
    id, name, facility_type, address,
    latitude, longitude, capacity_tpd,
    contact_number, operational_hours
)
```

### Vehicles Table
```sql
vehicles (
    id, vehicle_number, vehicle_type, capacity_tons,
    current_latitude, current_longitude,
    driver_name, driver_phone, status, last_updated
)
```

### Rewards Table
```sql
rewards (
    id, user_id, reward_type, points_earned,
    description, earned_date
)
```

## 🔧 Configuration

### Environment Settings

Default coordinates (Delhi, India):
- Latitude: 28.6139
- Longitude: 77.2090

### Points System
| Action | Points |
|--------|--------|
| Registration Bonus | 50 |
| Segregated Collection | 10 |
| Non-segregated Collection | 5 |
| Complaint Reporting | 5 |
| Training Module Completion | 50-100 |

### Waste Types
- Wet (Organic/Biodegradable)
- Dry (Recyclable)
- Hazardous (Dangerous materials)
- E-waste (Electronic items)

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. ImportError: No module named 'streamlit'
```bash
# Solution
pip install streamlit
```

#### 2. Database Locked Error
```bash
# Solution: Restart the application
# The app uses check_same_thread=False to minimize this
```

#### 3. Port Already in Use
```bash
# Use different port
streamlit run web_app_wastemanagement.py --server.port 8502
```

#### 4. Map Not Loading
- Check internet connection (required for map tiles)
- Verify folium is installed: `pip install folium streamlit-folium`

#### 5. Login Failed
- Verify credentials (case-sensitive)
- Check if database exists
- Try default admin account

#### 6. Bytes Conversion Error
- Fixed in latest version
- Ensures proper data type conversion for segregated field

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### How to Contribute
1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Add docstrings to functions
- Comment complex logic
- Update documentation

### Areas for Contribution
- Mobile app development
- IoT sensor integration
- Machine learning for route optimization
- SMS/Email notifications
- Multi-language support
- API development

## 📈 Performance Tips

1. **Database Optimization**
   - Add indexes for frequently queried columns
   - Regular database maintenance
   - Implement connection pooling

2. **Caching**
   - Use `@st.cache_data` for data functions
   - Cache expensive computations
   - Implement session state properly

3. **UI/UX Improvements**
   - Lazy loading for large datasets
   - Pagination for tables
   - Progressive web app features

## 🎯 Future Roadmap

### Phase 1 (Q1 2025)
- [ ] Mobile application (React Native)
- [ ] Push notifications
- [ ] Offline mode support

### Phase 2 (Q2 2025)
- [ ] IoT sensor integration
- [ ] Smart bin monitoring
- [ ] Automated alerts

### Phase 3 (Q3 2025)
- [ ] Machine learning predictions
- [ ] Route optimization AI
- [ ] Demand forecasting

### Phase 4 (Q4 2025)
- [ ] Blockchain rewards
- [ ] Multi-city support
- [ ] API marketplace

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025 Smart Waste Management System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

## 👥 Team & Support

### Development Team
- **Lead Developer**: Smart Waste Solutions Team
- **UI/UX Design**: Modern Interface Design
- **Database Architecture**: Optimized Schema Design
- **Testing**: Comprehensive Coverage

### Support Channels
- **Email**: support@smartwaste.example.com
- **Documentation**: This README
- **Issues**: GitHub Issues section
- **Community**: Discord/Slack channel

## 🙏 Acknowledgments

- Streamlit team for the excellent framework
- Open-source community contributors
- Environmental organizations for domain expertise
- Beta testers for valuable feedback
- All users helping make waste management smarter

---

**Version**: 1.0.0  
**Last Updated**: September 2025  
**Status**: Active Development  
**Made with ❤️ for a cleaner, greener future**

