import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime, timedelta
import hashlib
import secrets
import qrcode
from io import BytesIO
import base64
from PIL import Image
import folium
from streamlit_folium import folium_static
import streamlit_authenticator as stauth
from streamlit_option_menu import option_menu
import yaml
import json

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="Smart Waste Management System",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #2E8B57, #32CD32);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .success-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .info-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2E8B57 0%, #90EE90 100%);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #2E8B57, #32CD32);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .achievement-badge {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #333;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        display: inline-block;
        margin: 0.2rem;
        font-weight: bold;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ===================== DATABASE INITIALIZATION =====================
@st.cache_resource
def init_database():
    conn = sqlite3.connect('waste_management.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            phone TEXT,
            address TEXT,
            user_type TEXT DEFAULT 'citizen',
            ward_number TEXT,
            unique_waste_id TEXT UNIQUE,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            training_completed INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS waste_collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            collection_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            waste_type TEXT,
            weight_kg REAL,
            segregated INTEGER DEFAULT 0,
            collected_by TEXT,
            vehicle_number TEXT,
            status TEXT DEFAULT 'scheduled',
            latitude REAL,
            longitude REAL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            complaint_type TEXT,
            description TEXT,
            location TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT DEFAULT 'pending',
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            resolved_date DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            facility_type TEXT,
            address TEXT,
            latitude REAL,
            longitude REAL,
            capacity_tpd REAL,
            contact_number TEXT,
            operational_hours TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_number TEXT UNIQUE NOT NULL,
            vehicle_type TEXT,
            capacity_tons REAL,
            current_latitude REAL,
            current_longitude REAL,
            driver_name TEXT,
            driver_phone TEXT,
            status TEXT DEFAULT 'idle',
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            reward_type TEXT,
            points_earned INTEGER,
            description TEXT,
            earned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Insert sample admin user
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, phone, address, user_type, ward_number, unique_waste_id, points)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('admin', 'admin@waste.com', admin_password, 'System Administrator', '9999999999', 'Admin Office', 'admin', 'ADMIN', 'ADMIN001', 1000))
        
        # Insert sample citizens
        for i in range(1, 11):
            user_id = f"WG2024{i:04d}"
            password = hashlib.sha256(f"user{i}123".encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, full_name, phone, address, user_type, ward_number, unique_waste_id, points)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f'user{i}', f'user{i}@example.com', password, f'User {i}', f'98765{i:05d}', f'Address {i}', 'citizen', f'Ward {i%5+1}', user_id, np.random.randint(50, 500)))
        
        # Insert sample waste collections
        for i in range(1, 51):
            cursor.execute('''
                INSERT INTO waste_collections (user_id, waste_type, weight_kg, segregated, status, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                np.random.randint(2, 11), 
                np.random.choice(['wet', 'dry', 'hazardous', 'e-waste']),
                round(np.random.uniform(1.0, 20.0), 2),
                np.random.choice([0, 1]),
                np.random.choice(['scheduled', 'collected', 'processed']),
                28.6139 + np.random.uniform(-0.1, 0.1),
                77.2090 + np.random.uniform(-0.1, 0.1)
            ))
        
        # Insert sample facilities
        facilities_data = [
            ('Green Recycling Center', 'recycling_center', 'Sector 21, Delhi', 28.6139, 77.2090, 50.0, '011-12345678', '9 AM - 6 PM'),
            ('Compost Processing Plant', 'composting', 'Sector 15, Delhi', 28.6239, 77.2190, 30.0, '011-87654321', '24/7'),
            ('E-Waste Collection Point', 'e_waste', 'Sector 18, Delhi', 28.6039, 77.1990, 10.0, '011-11223344', '10 AM - 5 PM')
        ]
        
        for facility in facilities_data:
            cursor.execute('''
                INSERT INTO facilities (name, facility_type, address, latitude, longitude, capacity_tpd, contact_number, operational_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', facility)
        
        # Insert sample vehicles
        vehicles_data = [
            ('DL01AB1234', 'garbage_truck', 5.0, 28.6139, 77.2090, 'Driver A', '9876543210', 'collecting'),
            ('DL01CD5678', 'garbage_truck', 7.0, 28.6239, 77.2190, 'Driver B', '9876543211', 'idle'),
            ('DL01EF9012', 'recycling_truck', 3.0, 28.6339, 77.2290, 'Driver C', '9876543212', 'collecting')
        ]
        
        for vehicle in vehicles_data:
            cursor.execute('''
                INSERT INTO vehicles (vehicle_number, vehicle_type, capacity_tons, current_latitude, current_longitude, driver_name, driver_phone, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', vehicle)
    
    conn.commit()
    return conn

# ===================== AUTHENTICATION =====================
def authenticate_user(username, password):
    conn = init_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user and verify_password(password, user[3]):
        return {
            'id': user[0], 'username': user[1], 'email': user[2],
            'full_name': user[4], 'phone': user[5], 'address': user[6],
            'user_type': user[7], 'ward_number': user[8],
            'unique_waste_id': user[9],
            'points': user[12]   # ✅ fixed index for points column
        }
    return None

def verify_password(password, password_hash):
    """Verify a password against its hash (SHA-256)."""
    return hashlib.sha256(password.encode()).hexdigest() == password_hash

# ===================== UTILITY FUNCTIONS =====================
@st.cache_data(ttl=300)
def get_dashboard_stats():
    conn = init_database()
    
    # Total users
    total_users = pd.read_sql("SELECT COUNT(*) as count FROM users", conn)['count'].iloc[0]
    
    # Total waste collected
    total_waste = pd.read_sql("SELECT SUM(weight_kg) as total FROM waste_collections", conn)['total'].iloc[0] or 0
    
    # Active complaints
    active_complaints = pd.read_sql("SELECT COUNT(*) as count FROM complaints WHERE status = 'pending'", conn)['count'].iloc[0]
    
    # Facilities count
    facilities_count = pd.read_sql("SELECT COUNT(*) as count FROM facilities", conn)['count'].iloc[0]
    
    return {
        'total_users': total_users,
        'total_waste_collected': round(total_waste, 2),
        'active_complaints': active_complaints,
        'facilities': facilities_count
    }

@st.cache_data(ttl=300)
def get_waste_data():
    conn = init_database()
    return pd.read_sql('''
        SELECT wc.*, u.full_name, u.ward_number 
        FROM waste_collections wc 
        JOIN users u ON wc.user_id = u.id
    ''', conn)

@st.cache_data(ttl=300)
def get_facilities_data():
    conn = init_database()
    return pd.read_sql("SELECT * FROM facilities", conn)

def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

# ===================== 3D VISUALIZATIONS =====================
def create_3d_waste_distribution():
    waste_data = get_waste_data()
    ward_waste = waste_data.groupby(['ward_number', 'waste_type'])['weight_kg'].sum().reset_index()

    fig = go.Figure()
    for wtype, color in zip(['wet', 'dry', 'hazardous', 'e-waste'],
                            ['#2E8B57', '#32CD32', '#FF6347', '#FFD700']):
        subset = ward_waste[ward_waste['waste_type'] == wtype]
        fig.add_trace(go.Scatter3d(
            x=subset['ward_number'],
            y=[wtype] * len(subset),
            z=subset['weight_kg'],
            mode='markers',
            marker=dict(size=6, color=color),
            name=wtype
        ))
    fig.update_layout(
        title="3D Waste Distribution by Ward and Type",
        scene=dict(
            xaxis_title="Ward Number",
            yaxis_title="Waste Type",
            zaxis_title="Weight (kg)"
        ),
        height=600
    )
    return fig


def create_3d_facility_map():
    facilities = get_facilities_data()
    
    fig = go.Figure(data=go.Scatter3d(
        x=facilities['longitude'],
        y=facilities['latitude'],
        z=facilities['capacity_tpd'],
        mode='markers+text',
        marker=dict(
            size=facilities['capacity_tpd']/2,
            color=facilities['capacity_tpd'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Capacity (TPD)")
        ),
        text=facilities['name'],
        textposition="top center"
    ))
    
    fig.update_layout(
        title="3D Facility Capacity Distribution",
        scene=dict(
            xaxis_title="Longitude",
            yaxis_title="Latitude",
            zaxis_title="Capacity (TPD)",
            bgcolor="rgba(0,0,0,0)"
        ),
        height=600
    )
    
    return fig

def create_waste_trend_surface():
    waste_data = get_waste_data()
    waste_data['collection_date'] = pd.to_datetime(waste_data['collection_date'])
    waste_data['day'] = waste_data['collection_date'].dt.day
    waste_data['hour'] = waste_data['collection_date'].dt.hour
    
    # Create pivot for surface plot
    surface_data = waste_data.groupby(['day', 'hour'])['weight_kg'].sum().reset_index()
    pivot_data = surface_data.pivot(index='day', columns='hour', values='weight_kg').fillna(0)
    
    fig = go.Figure(data=[go.Surface(z=pivot_data.values, colorscale='Viridis')])
    
    fig.update_layout(
        title="Waste Collection Patterns - 3D Surface",
        scene=dict(
            xaxis_title="Hour of Day",
            yaxis_title="Day of Month",
            zaxis_title="Weight (kg)"
        ),
        height=600
    )
    
    return fig

# ===================== MAIN APPLICATION =====================
def main():
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
    
    # Sidebar for navigation
    with st.sidebar:
        st.markdown("### ♻️ Waste Management")
        
        if not st.session_state.logged_in:
            auth_option = option_menu(
                "Authentication",
                ["Login", "Register"],
                icons=["box-arrow-in-right", "person-plus"],
                menu_icon="shield-lock",
                default_index=0
            )
        else:
            st.markdown(f"**Welcome, {st.session_state.user['full_name']}!**")
            st.markdown(f"Points: **{st.session_state.user['points']}** ⭐")
            
            if st.session_state.user['user_type'] == 'admin':
                menu_options = ["Dashboard", "Analytics", "User Management", "Facilities", "Vehicles", "Reports", "3D Visualizations"]
                menu_icons = ["speedometer2", "bar-chart", "people", "building", "truck", "file-text", "box"]
            elif st.session_state.user['user_type'] == 'worker':
                menu_options = ["Dashboard", "Collections", "Vehicle Tracking", "Reports"]
                menu_icons = ["speedometer2", "trash", "geo-alt", "file-text"]
            else:
                menu_options = ["Dashboard", "Schedule Collection", "Track Waste", "Complaints", "Shop", "Training", "3D Views"]
                menu_icons = ["speedometer2", "calendar-plus", "geo-alt", "exclamation-triangle", "shop", "book", "box"]
            
            selected = option_menu(
                "Navigation",
                menu_options,
                icons=menu_icons,
                menu_icon="list",
                default_index=0
            )
            
            if st.button("Logout", type="primary"):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.rerun()
    
    # Main content area
    if not st.session_state.logged_in:
        if auth_option == "Login":
            show_login()
        else:
            show_register()
    else:
        if selected == "Dashboard":
            show_dashboard()
        elif selected == "Analytics":
            show_analytics()
        elif selected == "User Management":
            show_user_management()
        elif selected == "Facilities":
            show_facilities()
        elif selected == "Vehicles":
            show_vehicles()
        elif selected == "Reports":
            show_reports()
        elif selected == "3D Visualizations":
            show_3d_visualizations()
        elif selected == "Schedule Collection":
            show_schedule_collection()
        elif selected == "Track Waste":
            show_track_waste()
        elif selected == "Complaints":
            show_complaints()
        elif selected == "Shop":
            show_shop()
        elif selected == "Training":
            show_training()
        elif selected == "3D Views":
            show_3d_views()
        elif selected == "Collections":
            show_worker_collections()
        elif selected == "Vehicle Tracking":
            show_vehicle_tracking()

# ===================== AUTHENTICATION PAGES =====================
def show_login():
    st.markdown('<h1 class="main-header">🔐 Login</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("### Enter Your Credentials")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login", use_container_width=True):
                user = authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("**Demo Credentials:**")
        st.markdown("- Username: `admin` Password: `admin123`")
        st.markdown("- Username: `user1` Password: `user1123`")

def show_register():
    st.markdown('<h1 class="main-header">📝 Register</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="success-card">', unsafe_allow_html=True)
        with st.form("register_form"):
            st.markdown("### Create New Account")
            
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            full_name = st.text_input("Full Name")
            phone = st.text_input("Phone")
            address = st.text_input("Address")
            ward_number = st.text_input("Ward Number")
            
            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                conn = init_database()
                cursor = conn.cursor()
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                unique_waste_id = f"WG{datetime.now().year}{secrets.token_hex(4).upper()}"
                try:
                    cursor.execute('''
                        INSERT INTO users (username, email, password_hash, full_name, phone, address, ward_number, unique_waste_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (username, email, password_hash, full_name, phone, address, ward_number, unique_waste_id))
                    conn.commit()
                    st.success("Registration successful! You can now log in.")
                except sqlite3.IntegrityError:
                    st.error("Username or email already exists.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # FIX: Add this line to define waste_data
    waste_data = get_waste_data()
    
    with col1:
        # Waste type distribution
        waste_by_type = waste_data.groupby('waste_type')['weight_kg'].sum()
        fig1 = px.pie(
            values=waste_by_type.values,
            names=waste_by_type.index,
            title="Waste Distribution by Type",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Ward-wise waste collection
        ward_waste = waste_data.groupby('ward_number')['weight_kg'].sum().sort_values(ascending=False)
        fig2 = px.bar(
            x=ward_waste.index,
            y=ward_waste.values,
            title="Ward-wise Waste Collection",
            color=ward_waste.values,
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Time series analysis
    st.markdown("### 📈 Collection Trends")
    waste_data['collection_date'] = pd.to_datetime(waste_data['collection_date'])
    daily_waste = waste_data.groupby(waste_data['collection_date'].dt.date)['weight_kg'].sum().reset_index()
    
    fig3 = px.line(
        daily_waste,
        x='collection_date',
        y='weight_kg',
        title="Daily Waste Collection Trend",
        markers=True
    )
    fig3.update_traces(line_color='#2E8B57', marker_color='#32CD32')
    st.plotly_chart(fig3, use_container_width=True)
    
    # Segregation analysis
    col3, col4 = st.columns(2)
    
    with col3:
        segregation_rate = waste_data['segregated'].apply(lambda x: int.from_bytes(x, 'little') if isinstance(x, bytes) else int(x)).mean() * 100
        fig4 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=segregation_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Segregation Rate (%)"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        st.plotly_chart(fig4, use_container_width=True)
    
    with col4:
        # Collection status
        status_counts = waste_data['status'].value_counts()
        fig5 = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Collection Status Distribution",
            hole=0.4,   # ✅ replaced px.donut
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
        )
        st.plotly_chart(fig5, use_container_width=True)

# ===================== SCHEDULE COLLECTION =====================
def show_schedule_collection():
    st.markdown('<h1 class="main-header">📅 Schedule Collection</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="success-card">', unsafe_allow_html=True)
        with st.form("collection_form"):
            st.markdown("### Schedule Your Waste Collection")
            
            col1, col2 = st.columns(2)
            with col1:
                waste_type = st.selectbox("Waste Type", ["wet", "dry", "hazardous", "e-waste"])
                weight_kg = st.number_input("Estimated Weight (kg)", min_value=0.1, max_value=100.0, value=5.0)
            
            with col2:
                collection_date = st.date_input("Collection Date", min_value=datetime.now().date())
                segregated = st.checkbox("Properly Segregated", value=True)
            
            location = st.text_input("Collection Address", value=st.session_state.user['address'])
            
            col1, col2 = st.columns(2)
            with col1:
                latitude = st.number_input("Latitude", value=28.6139, format="%.6f")
            with col2:
                longitude = st.number_input("Longitude", value=77.2090, format="%.6f")
            
            if st.form_submit_button("Schedule Collection", use_container_width=True):
                conn = init_database()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO waste_collections (user_id, waste_type, weight_kg, segregated, collection_date, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (st.session_state.user['id'], waste_type, weight_kg, int(segregated), collection_date, latitude, longitude))
                
                # Award points
                points_earned = 10 if segregated else 5
                cursor.execute("UPDATE users SET points = points + ? WHERE id = ?", (points_earned, st.session_state.user['id']))
                st.session_state.user['points'] += points_earned
                
                conn.commit()
                st.success(f"Collection scheduled successfully! You earned {points_earned} points!")
                st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💡 Tips for Better Collection")
        st.markdown("- **Segregate properly** to earn more points")
        st.markdown("- **Clean containers** before disposal")
        st.markdown("- **Schedule in advance** for better service")
        st.markdown("- **Check collection guidelines** for your area")
        
        # Move this OUTSIDE the form!
        if st.button("📍 Show My Location"):
            m = folium.Map(location=[28.6139, 77.2090], zoom_start=12)
            folium.Marker(
                [28.6139, 77.2090],
                popup="Your Collection Point",
                icon=folium.Icon(color='green', icon='home')
            ).add_to(m)
            folium_static(m, width=300, height=200)

# ===================== TRACK WASTE =====================
def show_track_waste():
    st.markdown('<h1 class="main-header">🗺️ Track Waste</h1>', unsafe_allow_html=True)
    
    # Get user's collections
    conn = init_database()
    user_collections = pd.read_sql('''
        SELECT * FROM waste_collections 
        WHERE user_id = ? 
        ORDER BY collection_date DESC
    ''', conn, params=[st.session_state.user['id']])
    
    if not user_collections.empty:
        # Map view
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🗺️ Your Collections Map")
            
            # Create map centered on first collection
            center_lat = user_collections['latitude'].mean()
            center_lon = user_collections['longitude'].mean()
            
            m = folium.Map(location=[center_lat, center_lon], zoom_start=12)
            
            # Add markers for each collection
            colors = {'wet': 'green', 'dry': 'blue', 'hazardous': 'red', 'e-waste': 'orange'}
            
            for _, row in user_collections.iterrows():
                color = colors.get(row['waste_type'], 'gray')
                folium.Marker(
                    [row['latitude'], row['longitude']],
                    popup=f"{row['waste_type'].title()} - {row['weight_kg']}kg - {row['status']}",
                    icon=folium.Icon(color=color, icon='trash')
                ).add_to(m)
            
            folium_static(m, width=600, height=400)
        
        with col2:
            st.markdown("### 📊 Your Collection Stats")
            
            total_weight = user_collections['weight_kg'].sum()
            segregated_count = user_collections['segregated'].sum()
            total_collections = len(user_collections)
            
            st.metric("Total Weight", f"{total_weight:.2f} kg", "♻️")
            st.metric("Segregated Collections", f"{segregated_count}/{total_collections}", "✅")
            st.metric("Your Points", st.session_state.user['points'], "⭐")
            
            # Collection history
            st.markdown("### 📝 Recent Collections")
            for _, collection in user_collections.head(5).iterrows():
                status_color = {"scheduled": "🟡", "collected": "🟢", "processed": "🔵"}
                st.markdown(f"{status_color.get(collection['status'], '⚫')} **{collection['waste_type'].title()}** - {collection['weight_kg']}kg")
    
    else:
        st.info("No collections scheduled yet. Schedule your first collection!")
        if st.button("Schedule Collection"):
            st.session_state.page = "Schedule Collection"
            st.rerun()

# ===================== COMPLAINTS =====================
def show_complaints():
    st.markdown('<h1 class="main-header">⚠️ Complaints Management</h1>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📝 Report New", "📋 My Complaints"])
    
    with tab1:
        st.markdown("### Report a New Complaint")
        
        with st.form("complaint_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                complaint_type = st.selectbox("Complaint Type", [
                    "Missed Collection", "Overflowing Bins", "Improper Disposal", 
                    "Vehicle Issues", "Facility Problems", "Other"
                ])
                location = st.text_input("Location", value=st.session_state.user['address'])
            
            with col2:
                latitude = st.number_input("Latitude", value=28.6139, format="%.6f")
                longitude = st.number_input("Longitude", value=77.2090, format="%.6f")
            
            description = st.text_area("Description", placeholder="Provide detailed description of the issue...")
            
            # Image upload (simulated)
            uploaded_file = st.file_uploader("Upload Image (Optional)", type=['png', 'jpg', 'jpeg'])
            
            if st.form_submit_button("Submit Complaint", use_container_width=True):
                conn = init_database()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO complaints (user_id, complaint_type, description, location, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (st.session_state.user['id'], complaint_type, description, location, latitude, longitude))
                
                # Award points for reporting
                cursor.execute("UPDATE users SET points = points + 5 WHERE id = ?", (st.session_state.user['id'],))
                st.session_state.user['points'] += 5
                
                conn.commit()
                st.success("Complaint submitted successfully! You earned 5 points for reporting.")
    
    with tab2:
        # Get user complaints
        conn = init_database()
        user_complaints = pd.read_sql('''
            SELECT * FROM complaints 
            WHERE user_id = ? 
            ORDER BY created_date DESC
        ''', conn, params=[st.session_state.user['id']])
        
        if not user_complaints.empty:
            for _, complaint in user_complaints.iterrows():
                status_color = {"pending": "🟡", "in_progress": "🔵", "resolved": "🟢"}
                
                with st.expander(f"{status_color.get(complaint['status'], '⚫')} {complaint['complaint_type']} - {complaint['created_date'][:10]}"):
                    st.markdown(f"**Status:** {complaint['status'].title()}")
                    st.markdown(f"**Location:** {complaint['location']}")
                    st.markdown(f"**Description:** {complaint['description']}")
                    if complaint['resolved_date']:
                        st.markdown(f"**Resolved:** {complaint['resolved_date']}")
        else:
            st.info("No complaints filed yet.")

# ===================== SHOP =====================
def show_shop():
    st.markdown('<h1 class="main-header">🛒 Eco Shop</h1>', unsafe_allow_html=True)
    
    st.markdown(f"**Your Points:** {st.session_state.user['points']} ⭐")
    
    # Sample products
    products = [
        {"name": "3-Bin Segregation Set", "price": 1500, "points": 300, "stock": 10, "category": "Equipment"},
        {"name": "Compost Kit", "price": 2000, "points": 400, "stock": 5, "category": "Composting"},
        {"name": "Eco Bags (Set of 5)", "price": 500, "points": 100, "stock": 20, "category": "Accessories"},
        {"name": "Organic Fertilizer", "price": 800, "points": 160, "stock": 15, "category": "Garden"},
        {"name": "Solar Waste Bin", "price": 5000, "points": 1000, "stock": 3, "category": "Technology"},
        {"name": "Safety Gloves", "price": 300, "points": 60, "stock": 25, "category": "Safety"}
    ]
    
    # Filter products
    categories = ["All"] + list(set([p["category"] for p in products]))
    selected_category = st.selectbox("Filter by Category", categories)
    
    if selected_category != "All":
        filtered_products = [p for p in products if p["category"] == selected_category]
    else:
        filtered_products = products
    
    # Display products in grid
    cols = st.columns(3)
    
    for i, product in enumerate(filtered_products):
        with cols[i % 3]:
            st.markdown(f'<div class="info-card">', unsafe_allow_html=True)
            st.markdown(f"### {product['name']}")
            st.markdown(f"**Price:** ₹{product['price']}")
            st.markdown(f"**Points:** {product['points']} ⭐")
            st.markdown(f"**Stock:** {product['stock']} units")
            
            can_afford = st.session_state.user['points'] >= product['points']
            
            col1, col2 = st.columns(2)
            with col1:
                quantity = st.number_input("Qty", min_value=1, max_value=min(5, product['stock']), value=1, key=f"qty_{i}")
            with col2:
                if st.button("Buy", disabled=not can_afford, key=f"buy_{i}"):
                    total_points = product['points'] * quantity
                    if st.session_state.user['points'] >= total_points:
                        # Simulate purchase
                        st.session_state.user['points'] -= total_points
                        st.success(f"Purchased {quantity}x {product['name']}!")
                        st.balloons()
                    else:
                        st.error("Insufficient points!")
            
            if not can_afford:
                st.warning("Insufficient points")
            
            st.markdown('</div>', unsafe_allow_html=True)

# ===================== TRAINING =====================
def show_training():
    st.markdown('<h1 class="main-header">📚 Training Modules</h1>', unsafe_allow_html=True)
    
    modules = [
        {
            "title": "Waste Classification & Identification",
            "description": "Learn to identify different types of waste and their proper disposal methods",
            "duration": "30 minutes",
            "points": 50,
            "difficulty": "Beginner"
        },
        {
            "title": "Source Segregation Best Practices",
            "description": "Master the techniques of segregating waste at source for maximum efficiency",
            "duration": "45 minutes",
            "points": 75,
            "difficulty": "Intermediate"
        },
        {
            "title": "Home Composting Workshop",
            "description": "Convert your kitchen waste into valuable compost for your garden",
            "duration": "60 minutes",
            "points": 100,
            "difficulty": "Advanced"
        },
        {
            "title": "Plastic Waste Management",
            "description": "Understanding plastic types, recycling codes, and creative reuse methods",
            "duration": "40 minutes",
            "points": 80,
            "difficulty": "Intermediate"
        }
    ]
    
    for i, module in enumerate(modules):
        with st.expander(f"📖 {module['title']} - {module['difficulty']}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {module['description']}")
                st.markdown(f"**Duration:** {module['duration']}")
                st.markdown(f"**Reward:** {module['points']} points ⭐")
                
                # Progress simulation
                progress = st.progress(0)
                
                if st.button(f"Start Module {i+1}", key=f"start_{i}"):
                    import time
                    for percent in range(100):
                        time.sleep(0.01)
                        progress.progress(percent + 1)
                    
                    st.session_state.user['points'] += module['points']
                    st.success(f"Module completed! You earned {module['points']} points!")
                    st.balloons()
            
            with col2:
                difficulty_colors = {
                    "Beginner": "🟢",
                    "Intermediate": "🟡", 
                    "Advanced": "🟠"
                }
                st.markdown(f"### {difficulty_colors.get(module['difficulty'], '⚫')} {module['difficulty']}")

# ===================== ADMIN PAGES =====================
def show_user_management():
    st.markdown('<h1 class="main-header">👥 User Management</h1>', unsafe_allow_html=True)
    
    conn = init_database()
    users_df = pd.read_sql("SELECT * FROM users", conn)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = len(users_df)
        st.metric("Total Users", total_users, "👥")
    
    with col2:
        citizens = len(users_df[users_df['user_type'] == 'citizen'])
        st.metric("Citizens", citizens, "🏠")
    
    with col3:
        workers = len(users_df[users_df['user_type'] == 'worker'])
        st.metric("Workers", workers, "👷")
    
    with col4:
        avg_points = users_df['points'].mean()
        st.metric("Avg Points", f"{avg_points:.0f}", "⭐")
    
    # User table
    st.markdown("### 📋 User Directory")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        user_type_filter = st.selectbox("Filter by Type", ["All", "citizen", "worker", "admin"])
    with col2:
        ward_filter = st.selectbox("Filter by Ward", ["All"] + sorted(users_df['ward_number'].dropna().unique()))
    
    # Apply filters
    filtered_df = users_df.copy()
    if user_type_filter != "All":
        filtered_df = filtered_df[filtered_df['user_type'] == user_type_filter]
    if ward_filter != "All":
        filtered_df = filtered_df[filtered_df['ward_number'] == ward_filter]
    
    # Display table
    display_columns = ['username', 'full_name', 'email', 'user_type', 'ward_number', 'points']
    st.dataframe(filtered_df[display_columns], use_container_width=True)
    
    # User type distribution
    col1, col2 = st.columns(2)
    
    with col1:
        user_type_counts = users_df['user_type'].value_counts()
        fig1 = px.pie(values=user_type_counts.values, names=user_type_counts.index, title="Users by Type")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        ward_counts = users_df['ward_number'].value_counts()
        fig2 = px.bar(x=ward_counts.index, y=ward_counts.values, title="Users by Ward")
        st.plotly_chart(fig2, use_container_width=True)

def show_facilities():
    st.markdown('<h1 class="main-header">🏭 Facility Management</h1>', unsafe_allow_html=True)
    
    facilities_df = get_facilities_data()
    
    # Facility stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Facilities", len(facilities_df), "🏢")
    
    with col2:
        total_capacity = facilities_df['capacity_tpd'].sum()
        st.metric("Total Capacity", f"{total_capacity} TPD", "⚡")
    
    with col3:
        facility_types = facilities_df['facility_type'].nunique()
        st.metric("Facility Types", facility_types, "🔧")
    
    # Add new facility
    with st.expander("➕ Add New Facility"):
        with st.form("add_facility"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Facility Name")
                facility_type = st.selectbox("Type", ["recycling_center", "composting", "e_waste", "wte_plant"])
                address = st.text_area("Address")
                capacity = st.number_input("Capacity (TPD)", min_value=0.1)
            
            with col2:
                contact = st.text_input("Contact Number")
                hours = st.text_input("Operational Hours", value="9 AM - 6 PM")
                latitude = st.number_input("Latitude", format="%.6f")
                longitude = st.number_input("Longitude", format="%.6f")
            
            if st.form_submit_button("Add Facility"):
                conn = init_database()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO facilities (name, facility_type, address, latitude, longitude, capacity_tpd, contact_number, operational_hours)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, facility_type, address, latitude, longitude, capacity, contact, hours))
                conn.commit()
                st.success("Facility added successfully!")
                st.rerun()
    
    # Facilities map
    st.markdown("### 🗺️ Facilities Map")
    
    if not facilities_df.empty:
        # Create map
        center_lat = facilities_df['latitude'].mean()
        center_lon = facilities_df['longitude'].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
        
        # Color mapping for facility types
        type_colors = {
            'recycling_center': 'green',
            'composting': 'blue', 
            'e_waste': 'red',
            'wte_plant': 'purple'
        }
        
        for _, facility in facilities_df.iterrows():
            color = type_colors.get(facility['facility_type'], 'gray')
            folium.Marker(
                [facility['latitude'], facility['longitude']],
                popup=f"{facility['name']}<br>Type: {facility['facility_type']}<br>Capacity: {facility['capacity_tpd']} TPD",
                icon=folium.Icon(color=color, icon='industry', prefix='fa')
            ).add_to(m)
        
        folium_static(m, width=700, height=400)
    
    # Facilities table
    st.markdown("### 📋 Facilities Directory")
    st.dataframe(facilities_df, use_container_width=True)

def show_vehicles():
    st.markdown('<h1 class="main-header">🚛 Vehicle Management</h1>', unsafe_allow_html=True)
    
    conn = init_database()
    vehicles_df = pd.read_sql("SELECT * FROM vehicles", conn)
    
    # Vehicle stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Vehicles", len(vehicles_df), "🚛")
    
    with col2:
        active_vehicles = len(vehicles_df[vehicles_df['status'] == 'collecting'])
        st.metric("Active", active_vehicles, "🟢")
    
    with col3:
        idle_vehicles = len(vehicles_df[vehicles_df['status'] == 'idle'])
        st.metric("Idle", idle_vehicles, "🟡")
    
    with col4:
        total_capacity = vehicles_df['capacity_tons'].sum()
        st.metric("Total Capacity", f"{total_capacity} tons", "⚖️")
    
    # Vehicle tracking map
    st.markdown("### 🗺️ Live Vehicle Tracking")
    
    if not vehicles_df.empty:
        # Create map for vehicle tracking
        m = folium.Map(location=[28.6139, 77.2090], zoom_start=12)
        
        status_colors = {'collecting': 'green', 'idle': 'blue', 'maintenance': 'red'}
        
        for _, vehicle in vehicles_df.iterrows():
            color = status_colors.get(vehicle['status'], 'gray')
            folium.Marker(
                [vehicle['current_latitude'], vehicle['current_longitude']],
                popup=f"{vehicle['vehicle_number']}<br>Driver: {vehicle['driver_name']}<br>Status: {vehicle['status']}",
                icon=folium.Icon(color=color, icon='truck', prefix='fa')
            ).add_to(m)
        
        folium_static(m, width=700, height=400)
    
    # Vehicle status distribution
    col1, col2 = st.columns(2)
    
    with col1:
        status_counts = vehicles_df['status'].value_counts()
        fig1 = px.pie(values=status_counts.values, names=status_counts.index, title="Vehicle Status Distribution")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        type_counts = vehicles_df['vehicle_type'].value_counts()
        fig2 = px.bar(x=type_counts.values, y=type_counts.index, orientation='h', title="Vehicles by Type")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Vehicles table
    st.markdown("### 📋 Vehicle Directory")
    st.dataframe(vehicles_df, use_container_width=True)

def show_reports():
    st.markdown('<h1 class="main-header">📊 Reports & Analytics</h1>', unsafe_allow_html=True)
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date())
    
    # Get data for the date range
    conn = init_database()
    waste_data = pd.read_sql('''
        SELECT wc.*, u.ward_number, u.full_name 
        FROM waste_collections wc 
        JOIN users u ON wc.user_id = u.id 
        WHERE date(wc.collection_date) BETWEEN ? AND ?
    ''', conn, params=[start_date, end_date])
    
    if not waste_data.empty:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Collections", len(waste_data), "📦")
        
        with col2:
            total_weight = waste_data['weight_kg'].sum()
            st.metric("Total Weight", f"{total_weight:.2f} kg", "⚖️")
        
        with col3:
            segregation_rate = (waste_data['segregated'].sum() / len(waste_data)) * 100
            st.metric("Segregation Rate", f"{segregation_rate:.1f}%", "♻️")
        
        with col4:
            unique_users = waste_data['user_id'].nunique()
            st.metric("Active Users", unique_users, "👥")
        
        # Detailed analytics
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🗺️ Geographic", "📊 Performance", "📋 Raw Data"])
        
        with tab1:
            # Daily collection trend
            daily_collections = waste_data.groupby(pd.to_datetime(waste_data['collection_date']).dt.date).agg({
                'weight_kg': 'sum',
                'id': 'count'
            }).reset_index()
            
            fig1 = make_subplots(specs=[[{"secondary_y": True}]])
            fig1.add_trace(
                go.Scatter(x=daily_collections['collection_date'], y=daily_collections['weight_kg'], name="Weight (kg)"),
                secondary_y=False,
            )
            fig1.add_trace(
                go.Scatter(x=daily_collections['collection_date'], y=daily_collections['id'], name="Count", line=dict(dash='dash')),
                secondary_y=True,
            )
            fig1.update_layout(title="Daily Collection Trends")
            st.plotly_chart(fig1, use_container_width=True)
        
        with tab2:
            # Ward-wise analysis
            ward_analysis = waste_data.groupby('ward_number').agg({
                'weight_kg': 'sum',
                'segregated': 'mean',
                'id': 'count'
            }).reset_index()
            
            fig2 = px.scatter(
                ward_analysis,
                x='weight_kg',
                y='segregated',
                size='id',
                hover_data=['ward_number'],
                title="Ward Performance: Weight vs Segregation Rate",
                labels={'weight_kg': 'Total Weight (kg)', 'segregated': 'Segregation Rate'}
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with tab3:
            # Performance metrics
            col1, col2 = st.columns(2)
            
            with col1:
                # Waste type distribution
                waste_type_dist = waste_data['waste_type'].value_counts()
                fig3 = px.pie(values=waste_type_dist.values, names=waste_type_dist.index, title="Waste Type Distribution")
                st.plotly_chart(fig3, use_container_width=True)
            
            with col2:
                # Collection status
                status_dist = waste_data['status'].value_counts()
                fig4 = px.bar(x=status_dist.index, y=status_dist.values, title="Collection Status")
                st.plotly_chart(fig4, use_container_width=True)
        
        with tab4:
            st.markdown("### Raw Data Export")
            st.dataframe(waste_data, use_container_width=True)
            
            # Download button
            csv = waste_data.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f'waste_report_{start_date}_to_{end_date}.csv',
                mime='text/csv'
            )
    
    else:
        st.warning("No data available for the selected date range.")

# ===================== WORKER PAGES =====================
def show_worker_collections():
    st.markdown('<h1 class="main-header">🗂️ Today\'s Collections</h1>', unsafe_allow_html=True)
    
    # Get today's collections
    conn = init_database()
    today_collections = pd.read_sql('''
        SELECT wc.*, u.full_name, u.address, u.phone 
        FROM waste_collections wc 
        JOIN users u ON wc.user_id = u.id 
        WHERE date(wc.collection_date) = date('now')
        ORDER BY wc.collection_date
    ''', conn)
    
    if not today_collections.empty:
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Collections", len(today_collections), "📦")
        
        with col2:
            pending = len(today_collections[today_collections['status'] == 'scheduled'])
            st.metric("Pending", pending, "⏳")
        
        with col3:
            completed = len(today_collections[today_collections['status'] == 'collected'])
            st.metric("Completed", completed, "✅")
        
        with col4:
            total_weight = today_collections['weight_kg'].sum()
            st.metric("Total Weight", f"{total_weight:.1f} kg", "⚖️")
        
        # Collections map
        st.markdown("### 🗺️ Collection Routes")
        
        m = folium.Map(location=[28.6139, 77.2090], zoom_start=12)
        
        # Add markers for collections
        status_colors = {'scheduled': 'red', 'collected': 'green', 'processed': 'blue'}
        
        for _, collection in today_collections.iterrows():
            color = status_colors.get(collection['status'], 'gray')
            folium.Marker(
                [collection['latitude'], collection['longitude']],
                popup=f"{collection['full_name']}<br>{collection['waste_type']} - {collection['weight_kg']}kg<br>Status: {collection['status']}",
                icon=folium.Icon(color=color, icon='home')
            ).add_to(m)
        
        folium_static(m, width=700, height=400)
        
        # Collection details
        st.markdown("### 📋 Collection Details")
        
        for _, collection in today_collections.iterrows():
            with st.expander(f"🏠 {collection['full_name']} - {collection['waste_type']} ({collection['status']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Address:** {collection['address']}")
                    st.markdown(f"**Phone:** {collection['phone']}")
                    st.markdown(f"**Weight:** {collection['weight_kg']} kg")
                
                with col2:
                    st.markdown(f"**Waste Type:** {collection['waste_type']}")
                    st.markdown(f"**Segregated:** {'Yes' if collection['segregated'] else 'No'}")
                    st.markdown(f"**Current Status:** {collection['status']}")
                
                with col3:
                    if collection['status'] == 'scheduled':
                        new_status = st.selectbox("Update Status", ["scheduled", "collected", "processed"], 
                                                index=0, key=f"status_{collection['id']}")
                        vehicle_number = st.text_input("Vehicle Number", key=f"vehicle_{collection['id']}")
                        
                        if st.button("Update", key=f"update_{collection['id']}"):
                            cursor = conn.cursor()
                            cursor.execute('''
                                UPDATE waste_collections 
                                SET status = ?, collected_by = ?, vehicle_number = ?
                                WHERE id = ?
                            ''', (new_status, st.session_state.user['full_name'], vehicle_number, collection['id']))
                            conn.commit()
                            st.success("Collection updated!")
                            st.rerun()
    else:
        st.info("No collections scheduled for today.")

def show_vehicle_tracking():
    st.markdown('<h1 class="main-header">🚛 Vehicle Tracking</h1>', unsafe_allow_html=True)
    
    conn = init_database()
    vehicles_df = pd.read_sql("SELECT * FROM vehicles", conn)
    
    # Vehicle selector
    selected_vehicle = st.selectbox("Select Vehicle", vehicles_df['vehicle_number'].tolist())
    
    if selected_vehicle:
        vehicle_info = vehicles_df[vehicles_df['vehicle_number'] == selected_vehicle].iloc[0]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Vehicle location map
            m = folium.Map(location=[vehicle_info['current_latitude'], vehicle_info['current_longitude']], zoom_start=15)
            
            # Add vehicle marker
            folium.Marker(
                [vehicle_info['current_latitude'], vehicle_info['current_longitude']],
                popup=f"Vehicle: {vehicle_info['vehicle_number']}<br>Driver: {vehicle_info['driver_name']}<br>Status: {vehicle_info['status']}",
                icon=folium.Icon(color='green', icon='truck', prefix='fa')
            ).add_to(m)
            
            # Add route (simulated)
            route_points = [
                [vehicle_info['current_latitude'], vehicle_info['current_longitude']],
                [vehicle_info['current_latitude'] + 0.01, vehicle_info['current_longitude'] + 0.01],
                [vehicle_info['current_latitude'] + 0.02, vehicle_info['current_longitude'] - 0.01]
            ]
            
            folium.PolyLine(route_points, color='blue', weight=3, opacity=0.8).add_to(m)
            
            folium_static(m, width=600, height=400)
        
        with col2:
            st.markdown("### 🚛 Vehicle Details")
            st.markdown(f"**Vehicle:** {vehicle_info['vehicle_number']}")
            st.markdown(f"**Type:** {vehicle_info['vehicle_type']}")
            st.markdown(f"**Capacity:** {vehicle_info['capacity_tons']} tons")
            st.markdown(f"**Driver:** {vehicle_info['driver_name']}")
            st.markdown(f"**Phone:** {vehicle_info['driver_phone']}")
            st.markdown(f"**Status:** {vehicle_info['status']}")
            
            st.markdown("### 📍 Location Update")
            
            with st.form("location_update"):
                new_lat = st.number_input("Latitude", value=vehicle_info['current_latitude'], format="%.6f")
                new_lon = st.number_input("Longitude", value=vehicle_info['current_longitude'], format="%.6f")
                new_status = st.selectbox("Status", ["idle", "collecting", "in_transit", "maintenance"], 
                                        index=["idle", "collecting", "in_transit", "maintenance"].index(vehicle_info['status']))
                
                if st.form_submit_button("Update Location"):
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE vehicles 
                        SET current_latitude = ?, current_longitude = ?, status = ?, last_updated = datetime('now')
                        WHERE vehicle_number = ?
                    ''', (new_lat, new_lon, new_status, selected_vehicle))
                    conn.commit()
                    st.success("Location updated!")
                    st.rerun()

# ===================== ADDITIONAL UTILITY FUNCTIONS =====================
def create_waste_heatmap():
    """Create a heatmap showing waste generation intensity across areas"""
    waste_data = get_waste_data()
    
    # Group by location and calculate density
    location_data = waste_data.groupby(['latitude', 'longitude']).agg({
        'weight_kg': 'sum',
        'id': 'count'
    }).reset_index()
    
    fig = px.density_mapbox(
        location_data,
        lat='latitude',
        lon='longitude',
        z='weight_kg',
        radius=10,
        center=dict(lat=28.6139, lon=77.2090),
        zoom=10,
        mapbox_style="open-street-map",
        title="Waste Generation Heatmap"
    )
    
    return fig

def create_efficiency_dashboard():
    """Create efficiency metrics dashboard"""
    waste_data = get_waste_data()
    
    # Calculate various efficiency metrics
    total_collections = len(waste_data)
    segregated_collections = waste_data['segregated'].sum()
    segregation_rate = (segregated_collections / total_collections) * 100 if total_collections > 0 else 0
    
    processed_collections = len(waste_data[waste_data['status'] == 'processed'])
    processing_rate = (processed_collections / total_collections) * 100 if total_collections > 0 else 0
    
    # Create gauge charts
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "indicator"}, {"type": "indicator"}]],
        subplot_titles=["Segregation Efficiency", "Processing Efficiency"]
    )
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=segregation_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Segregation Rate (%)"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=processing_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Processing Rate (%)"},
            delta={'reference': 70},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgray"},
                    {'range': [40, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "blue"}
                ]
            }
        ),
        row=1, col=2
    )
    
    return fig

def create_predictive_analysis():
    """Create predictive analysis charts"""
    waste_data = get_waste_data()
    waste_data['collection_date'] = pd.to_datetime(waste_data['collection_date'])
    
    # Daily waste generation
    daily_waste = waste_data.groupby(waste_data['collection_date'].dt.date)['weight_kg'].sum().reset_index()
    daily_waste['collection_date'] = pd.to_datetime(daily_waste['collection_date'])
    
    # Simple trend prediction (linear)
    from sklearn.linear_model import LinearRegression
    import numpy as np
    
    X = np.arange(len(daily_waste)).reshape(-1, 1)
    y = daily_waste['weight_kg'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next 7 days
    future_X = np.arange(len(daily_waste), len(daily_waste) + 7).reshape(-1, 1)
    future_predictions = model.predict(future_X)
    
    # Create prediction chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_waste['collection_date'],
        y=daily_waste['weight_kg'],
        mode='lines+markers',
        name='Historical Data',
        line=dict(color='blue')
    ))
    
    future_dates = pd.date_range(start=daily_waste['collection_date'].max() + pd.Timedelta(days=1), periods=7)
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=future_predictions,
        mode='lines+markers',
        name='Predicted',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title="Waste Generation Prediction",
        xaxis_title="Date",
        yaxis_title="Weight (kg)",
        hovermode='x unified'
    )
    
    return fig

# ===================== ADVANCED 3D VISUALIZATIONS =====================
def show_advanced_3d():
    """Show advanced 3D visualizations"""
    st.markdown('<h1 class="main-header">🎮 Advanced 3D Analytics</h1>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🌐 Waste Flow", "📊 Multi-dimensional", "🔮 Predictions", "🎯 Efficiency"])
    
    with tab1:
        st.markdown("### 🌐 3D Waste Flow Visualization")
        
        # Create a 3D network showing waste flow from source to facility
        waste_data = get_waste_data()
        facilities_data = get_facilities_data()
        
        # Simulate waste flow network
        fig = go.Figure(data=[
            go.Scatter3d(
                x=waste_data['longitude'][:50],  # Limit for performance
                y=waste_data['latitude'][:50],
                z=[0] * 50,  # Source level
                mode='markers',
                marker=dict(
                    size=waste_data['weight_kg'][:50] / 2,
                    color='blue',
                    opacity=0.6
                ),
                name='Waste Sources'
            ),
            go.Scatter3d(
                x=facilities_data['longitude'],
                y=facilities_data['latitude'],
                z=[100] * len(facilities_data),  # Facility level
                mode='markers',
                marker=dict(
                    size=facilities_data['capacity_tpd'] / 2,
                    color='green',
                    symbol='diamond',
                    opacity=0.8
                ),
                name='Facilities'
            )
        ])
        
        # Add flow lines (simplified)
        for i in range(min(10, len(waste_data))):
            nearest_facility = facilities_data.iloc[i % len(facilities_data)]
            fig.add_trace(go.Scatter3d(
                x=[waste_data.iloc[i]['longitude'], nearest_facility['longitude']],
                y=[waste_data.iloc[i]['latitude'], nearest_facility['latitude']],
                z=[0, 100],
                mode='lines',
                line=dict(color='rgba(255,0,0,0.3)', width=2),
                showlegend=False
            ))
        
        fig.update_layout(
            title="3D Waste Flow Network",
            scene=dict(
                xaxis_title="Longitude",
                yaxis_title="Latitude", 
                zaxis_title="Level",
                bgcolor="rgba(0,0,0,0)"
            ),
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 📊 Multi-dimensional Waste Analysis")
        
        # Create 4D visualization (3D + color)
        waste_data = get_waste_data()
        
        fig = go.Figure(data=go.Scatter3d(
            x=waste_data['longitude'],
            y=waste_data['latitude'],
            z=waste_data['weight_kg'],
            mode='markers',
            marker=dict(
                size=8,
                color=waste_data['segregated'].astype(int),
                colorscale=[[0, 'red'], [1, 'green']],
                colorbar=dict(title="Segregated"),
                opacity=0.7
            ),
            text=[f"Type: {row['waste_type']}<br>Weight: {row['weight_kg']}kg<br>Ward: {row['ward_number']}" 
                  for _, row in waste_data.iterrows()],
            hovertemplate='%{text}<extra></extra>'
        ))
        
        fig.update_layout(
            title="4D Waste Analysis (Location + Weight + Segregation)",
            scene=dict(
                xaxis_title="Longitude",
                yaxis_title="Latitude",
                zaxis_title="Weight (kg)",
                bgcolor="rgba(0,0,0,0)"
            ),
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 🔮 Predictive 3D Modeling")
        
        try:
            fig = create_predictive_analysis()
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 📈 Prediction Insights")
            st.markdown("- **Blue line**: Historical waste generation data")
            st.markdown("- **Red dashed line**: Predicted values for next 7 days")
            st.markdown("- Predictions based on linear trend analysis")
            
        except ImportError:
            st.warning("Predictive analysis requires scikit-learn. Showing sample prediction visualization.")
            
            # Sample prediction visualization
            dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
            actual = np.random.normal(100, 20, len(dates))
            predicted = actual + np.random.normal(0, 5, len(dates))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=actual, name='Actual', mode='lines'))
            fig.add_trace(go.Scatter(x=dates, y=predicted, name='Predicted', mode='lines', line=dict(dash='dash')))
            fig.update_layout(title="Sample Prediction Model", xaxis_title="Date", yaxis_title="Weight (kg)")
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### 🎯 Efficiency Dashboard")
        
        try:
            fig = create_efficiency_dashboard()
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional efficiency metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="success-card">', unsafe_allow_html=True)
                st.markdown("### Collection Efficiency")
                st.markdown("**Target**: 95%")
                st.markdown("**Achieved**: 87%")
                st.markdown("**Status**: 🟡 Good")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="info-card">', unsafe_allow_html=True)
                st.markdown("### Segregation Quality") 
                st.markdown("**Target**: 90%")
                st.markdown("**Achieved**: 76%")
                st.markdown("**Status**: 🟠 Needs Improvement")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="warning-card">', unsafe_allow_html=True)
                st.markdown("### Processing Speed")
                st.markdown("**Target**: 48hrs")
                st.markdown("**Achieved**: 52hrs") 
                st.markdown("**Status**: 🔴 Behind Target")
                st.markdown('</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.warning("Efficiency dashboard requires additional data processing.")
def show_analytics():
    st.markdown('<h1 class="main-header">📊 Analytics</h1>', unsafe_allow_html=True)
    st.info("Analytics section is under development. Showing Reports instead.")
    show_reports()


def show_3d_visualizations():
    st.markdown('<h1 class="main-header">📦 3D Visualizations</h1>', unsafe_allow_html=True)
    st.plotly_chart(create_3d_waste_distribution(), use_container_width=True)
    st.plotly_chart(create_3d_facility_map(), use_container_width=True)
    st.plotly_chart(create_waste_trend_surface(), use_container_width=True)


def show_3d_views():
    show_advanced_3d()


def show_dashboard():
    st.markdown('<h1 class="main-header">🏠 Dashboard</h1>', unsafe_allow_html=True)
    stats = get_dashboard_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Users", stats['total_users'], "👥")
    with col2:
        st.metric("Total Waste Collected", f"{stats['total_waste_collected']} kg", "♻️")
    with col3:
        st.metric("Active Complaints", stats['active_complaints'], "⚠️")
    with col4:
        st.metric("Facilities", stats['facilities'], "🏭")
    st.markdown("### Welcome to the Smart Waste Management System!")
    st.info("Use the sidebar to navigate through the app features.")
# ===================== MAIN EXECUTION =====================
if __name__ == "__main__":
    main()

