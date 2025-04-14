import streamlit as st
import requests
import time
from datetime import datetime, timedelta
import base64
from datetime import timezone

# App configuration - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="StockTracker",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide the Streamlit footer and menu
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# Custom CSS for Bloomberg terminal-like design
st.markdown("""
<style>
    /* Base styles and dark theme */
    .stApp {
        background-color: #000000;
        max-width: 100%;
        margin: 0;
        padding: 0;
        font-family: 'JetBrains Mono', monospace;
        height: 100vh;
        overflow: hidden;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
    }
    
    /* Terminal container */
    .mobile-container {
        background-color: #000000;
        color: #00ff00;
        padding: 0;
        border-radius: 0;
        overflow: hidden;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        height: 100vh;
        width: 100%;
        margin: 0;
        border: none;
        display: flex;
        flex-direction: column;
    }
    
    /* Status bar */
    .status-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 50;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 16px;
        height: 32px;
        background: #000000;
        border-bottom: 1px solid #003300;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 6px;
        color: #00ff00;
    }
    
    .status-text {
        font-size: 13px;
        color: #00ff00;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .status-time {
        font-size: 13px;
        font-weight: 500;
        color: #00ff00;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .signal-icon, .battery-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 16px;
        height: 16px;
    }
    
    /* Weather widget */
    .weather-widget {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 6px 0;
        background: #000000;
        border-bottom: 1px solid #003300;
        font-family: 'JetBrains Mono', monospace;
        height: 30px;
    }
    
    .weather-icon {
        font-size: 18px;
        color: #00ff00;
    }
    
    .weather-temp {
        font-size: 16px;
        font-weight: bold;
        color: #00ff00;
        letter-spacing: 1px;
    }
    
    .weather-location {
        font-size: 14px;
        color: #00ff00;
        opacity: 0.8;
    }
    
    /* Main content area */
    .main-content {
        position: fixed;
        top: 15px;
        left: 0;
        right: 0;
        bottom: 80px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        padding: 4px;
    }
    
    /* App header */
    .app-header {
        font-size: 32px;
        font-weight: bold;
        color: #00ff00;
        padding: 12px 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #000000;
        border-bottom: 1px solid #003300;
        font-family: 'JetBrains Mono', monospace;
        height: 60px;
    }
    
    .app-header span:first-child {
        font-size: 40px;
        padding-left: 8px;
        padding-top: 4px;
    }
    
    .app-header span:last-child {
        font-size: 32px;
        padding-right: 16px;
    }
    
    /* Search container */
    .search-container {
        background: #000000;
        border-radius: 0;
        padding: 4px;
        margin-bottom: 4px;
        border: 1px solid #003300;
        font-family: 'JetBrains Mono', monospace;
        height: 40px;
    }
    
    /* Stock cards container */
    .stock-cards-container {
        flex: 1;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        gap: 2px;
        height: calc(100vh - 120px);
    }
    
    /* Stock cards */
    .stock-card {
        background: #000000;
        border-radius: 0;
        padding: 12px;
        margin-bottom: 8px;
        border: 1px solid #003300;
        font-family: 'JetBrains Mono', monospace;
        min-height: 100px;
    }
    
    .current-stock {
        background: #000000;
        border-left: 2px solid #00ff00;
    }
    
    .stock-symbol {
        font-size: 24px;
        font-weight: bold;
        color: #00ff00;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stock-price {
        font-size: 32px;
        font-weight: bold;
        color: #00ff00;
        margin: 12px 0;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .price-change-positive {
        color: #00ff00;
        font-weight: bold;
        font-size: 20px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .price-change-negative {
        color: #ff0000;
        font-weight: bold;
        font-size: 20px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stock-details {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 12px;
        font-size: 16px;
        font-family: 'JetBrains Mono', monospace;
        background: #000000;
    }
    
    .detail-item {
        display: flex;
        flex-direction: column;
        background: #000000;
        padding: 8px;
        border-radius: 0;
        border: 1px solid #003300;
    }
    
    .detail-label {
        color: #00ff00;
        font-size: 14px;
        margin-bottom: 4px;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .detail-value {
        color: #00ff00;
        font-weight: bold;
        font-size: 18px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .divider {
        height: 1px;
        background: #003300;
        margin: 8px 0;
    }
    
    .timestamp {
        color: #00ff00;
        font-size: 14px;
        text-align: right;
        margin-top: 4px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Section headers */
    .section-header {
        font-size: 12px;
        font-weight: bold;
        color: #00ff00;
        margin: 4px 0 2px 0;
        padding: 2px 4px;
        background: #000000;
        border-bottom: 1px solid #003300;
        font-family: 'JetBrains Mono', monospace;
        height: 20px;
    }
    
    /* Streamlit component overrides */
    .stTextInput > div > div > input {
        background-color: #001100 !important;
        border: 1px solid #003300 !important;
        border-radius: 0 !important;
        color: #00ff00 !important;
        font-size: 18px !important;
        padding: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        height: 40px !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #666666 !important;
    }
    
    .stTextInput > div > div > input:focus {
        border: 1px solid #00ff00 !important;
        box-shadow: none !important;
    }
    
    .stTextInput > label {
        color: #00ff00 !important;
        font-size: 16px !important;
        margin-bottom: 4px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Hide the "press enter to apply" text */
    .stTextInput > div > div > div[data-testid="stMarkdownContainer"] {
        display: none !important;
    }
    
    .stButton > button {
        background: #001100 !important;
        color: #00ff00 !important;
        border: 1px solid #003300 !important;
        border-radius: 0 !important;
        padding: 2px 0 !important;
        font-weight: bold !important;
        width: 100% !important;
        font-size: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
        height: 20px !important;
    }
    
    .stButton > button:hover {
        background: #002200 !important;
        border-color: #00ff00 !important;
    }
    
    .stButton > button:active {
        background: #003300 !important;
    }
    
    .stCheckbox > label {
        color: #00ff00 !important;
        font-size: 10px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    div.stCheckbox > label > div[role="checkbox"] {
        background-color: #001100 !important;
        border: 1px solid #003300 !important;
        width: 12px !important;
        height: 12px !important;
    }
    
    /* Navigation bar */
    .nav-bar {
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 8px 0;
        background: #000000;
        border-top: 1px solid #003300;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 64px;
        z-index: 100;
    }
    
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        color: #00ff00;
        font-size: 16px;
        padding: 4px 8px;
        font-family: 'JetBrains Mono', monospace;
        gap: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .nav-item:hover {
        background: #001100;
        border: 1px solid #003300;
    }
    
    .nav-item.active {
        background: #001100;
        border: 1px solid #003300;
    }
    
    .nav-icon {
        font-size: 20px;
        color: #00ff00;
    }
    
    .nav-text {
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
        color: #00ff00;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Hide Streamlit branding and components */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Hide the spinner/loading indicator */
    .stSpinner > div {
        display: none !important;
    }
    
    /* Hide the spinner container */
    .stSpinner {
        display: none !important;
    }
    
    ::-webkit-scrollbar {
        display: none;
    }
    
    /* Terminal cursor effect */
    .stTextInput > div > div > input::after {
        content: '|';
        animation: blink 1s step-end infinite;
        color: #00ff00;
    }
    
    @keyframes blink {
        from, to { opacity: 1; }
        50% { opacity: 0; }
    }
    
    /* Price ticker effect */
    .stock-price {
        animation: ticker 0.5s ease-in-out;
    }
    
    @keyframes ticker {
        0% { color: #00ff00; }
        50% { color: #ffffff; }
        100% { color: #00ff00; }
    }
    
    .music-player {
        position: fixed;
        bottom: 100px;
        right: 20px;
        background: #000000;
        border: 1px solid #003300;
        padding: 10px;
        z-index: 1000;
    }
    .music-controls {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .music-button {
        background: #001100;
        color: #00ff00;
        border: 1px solid #003300;
        padding: 5px 10px;
        cursor: pointer;
        font-family: 'Courier New', monospace;
    }
    .music-button:hover {
        background: #002200;
        border-color: #00ff00;
    }
    .music-status {
        color: #00ff00;
        font-size: 12px;
        margin-top: 5px;
    }
    
    /* Remove the old app-footer class */
    .app-footer {
        display: none;
    }
    
    /* Bloomberg terminal navigation bar */
    .bloomberg-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        display: flex;
        justify-content: space-around;
        align-items: center;
        height: 64px;
        background: #000000;
        border-top: 1px solid #003300;
        z-index: 1000;
    }
    
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 8px 12px;
        gap: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .nav-item.active {
        background: #001100;
        border: 1px solid #003300;
    }
    
    .nav-icon {
        font-size: 20px;
        color: #00ff00;
        line-height: 1;
    }
    
    .nav-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #00ff00;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        line-height: 1;
    }
    
    .nav-link {
        text-decoration: none;
        color: inherit;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 4px;
    }
    
    .nav-item:hover {
        background: #001100;
        border: 1px solid #003300;
    }
    
    /* Remove old navigation styles */
    .nav-bar, .nav-text, .app-footer {
        display: none;
    }
    
    /* LinkedIn icon specific styles */
    .linkedin-icon {
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        font-size: 16px;
        color: #00ff00;
        background: #000000;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #00ff00;
        border-radius: 2px;
        line-height: 1;
    }
    
    /* Navigation icons specific styles */
    .chart-icon, .briefcase-icon, .settings-icon, .linkedin-icon {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .linkedin-icon {
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        font-size: 16px;
        color: #00ff00;
        background: #000000;
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #00ff00;
        border-radius: 2px;
        line-height: 1;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_KEY = "d655f228ca6cf8d390a7319c52b3ce486a5b085a"

# Session state initialization
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = None
if 'history' not in st.session_state:
    st.session_state.history = []

# Your Weatherstack API key
WEATHER_API_KEY = '8e2d499cf0adc59768e1a98a721985f5'

# Function to fetch weather based on location
def get_weather(location):
    url = f'http://api.weatherstack.com/current?access_key={WEATHER_API_KEY}&query={location}'
    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        return None
    return data

def get_current_time():
    """Get current time plus one hour"""
    return (datetime.now() + timedelta(hours=1)).strftime("%H:%M")

def get_stock_data(symbol):
    """Fetch real-time stock data from Tiingo IEX API"""
    url = f"https://api.tiingo.com/iex/{symbol}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {API_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            item = data[0]
            real_time_price = item.get("tngoLast")
            prev_close = item.get("prevClose")
            percent_change = ((real_time_price - prev_close) / prev_close) * 100 if prev_close else 0
            return {
                "symbol": symbol,
                "price": real_time_price,
                "prev_close": prev_close,
                "percent_change": percent_change,
                "timestamp": get_current_time(),
                "high": item.get("high", 0),
                "low": item.get("low", 0),
                "volume": item.get("volume", 0)
            }
        else:
            st.error(f"No data found for {symbol}")
            return None
    
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def update_history(stock_data):
    """Update the search history"""
    existing = [item for item in st.session_state.history if item['symbol'] == stock_data['symbol']]
    if existing:
        st.session_state.history = [item for item in st.session_state.history if item['symbol'] != stock_data['symbol']]
    st.session_state.history.insert(0, stock_data)
    st.session_state.history = st.session_state.history[:5]

def format_large_number(num):
    """Format large numbers in a readable way"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:.0f}"

# Start mobile container
st.markdown('<div class="mobile-container">', unsafe_allow_html=True)

# Fetch weather data for Casablanca
weather_data = get_weather("Casablanca, Morocco")
weather_temp = weather_data['current']['temperature'] if weather_data else "N/A"
weather_icon = "🌤️"  # Default icon, you could map this based on weather condition

# Status bar
current_time = get_current_time()
st.markdown(f'''
<div class="status-bar">
    <div class="status-item">
        <svg viewBox="0 0 24 24" width="12" height="12" class="signal-icon">
            <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M2 20h.01"/>
            <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M7 20v-4"/>
            <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 20V8"/>
            <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M17 20V4"/>
        </svg>
        <span class="status-text">5G</span>
    </div>
    <span class="status-time">{current_time}</span>
    <div class="status-item">
        <svg viewBox="0 0 24 24" width="14" height="14" class="battery-icon">
            <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M22 13v-2"/>
            <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M2 7h18a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2z"/>
            <path fill="#00ff00" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 9h14v6H4z"/>
        </svg>
    </div>
</div>
''', unsafe_allow_html=True)

# Weather widget
st.markdown(f'''
<div class="weather-widget">
    <span class="weather-icon">{weather_icon}</span>
    <span class="weather-temp">{weather_temp}°C</span>
    <span class="weather-location">CASABLANCA</span>
</div>
''', unsafe_allow_html=True)

# App header
st.markdown('''
<div class="app-header">
    <span>📈</span>
    <span>الأسهم</span>
</div>
''', unsafe_allow_html=True)

# Search container
st.markdown('<div class="search-container">', unsafe_allow_html=True)
symbol = st.text_input(
    "Enter symbol",
    key="stock_symbol",
    placeholder="e.g. AAPL, MSFT"
).strip().upper()

search_clicked = st.button("Search", key="fetch_button")
st.markdown('</div>', unsafe_allow_html=True)

# Process search
if search_clicked:
    if symbol:
        with st.spinner(f"Loading {symbol}..."):
            stock_data = get_stock_data(symbol)
            if stock_data:
                st.session_state.last_updated = datetime.now()
                update_history(stock_data)
    else:
        st.warning("Please enter a stock symbol")

# Display default AAPL stock if no search has been made
if not st.session_state.history:
    with st.spinner("Loading AAPL..."):
        default_stock = get_stock_data("AAPL")
        if default_stock:
            st.session_state.history = [default_stock]

# Display current stocks in a row
if st.session_state.history:
    cols = st.columns(len(st.session_state.history))
    for idx, stock in enumerate(st.session_state.history):
        with cols[idx]:
            st.markdown(f'<div class="stock-card {"current-stock" if idx == 0 else ""}">', unsafe_allow_html=True)
            
            # Symbol and last updated
            st.markdown(f'''
            <div class="stock-symbol">
                <span>{stock["symbol"]}</span>
                <span class="timestamp">Updated {stock.get("timestamp", "now")}</span>
            </div>
            ''', unsafe_allow_html=True)
            
            # Price
            st.markdown(f'<div class="stock-price">${stock["price"]:.2f}</div>', unsafe_allow_html=True)
            
            # Price change
            change_class = "price-change-positive" if stock['percent_change'] >= 0 else "price-change-negative"
            change_symbol = "▲" if stock['percent_change'] >= 0 else "▼"
            price_diff = abs(stock["price"] - stock["prev_close"])
            st.markdown(f'<div class="{change_class}">{change_symbol} ${price_diff:.2f} ({abs(stock["percent_change"]):.2f}%)</div>', unsafe_allow_html=True)
            
            # Divider
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            # Additional stock details
            st.markdown('''
            <div class="stock-details">
                <div class="detail-item">
                    <span class="detail-label">Prev Close</span>
                    <span class="detail-value">$''' + f"{stock['prev_close']:.2f}" + '''</span>
                </div>
            ''', unsafe_allow_html=True)
            
            # Day high
            if "high" in stock and stock["high"]:
                st.markdown('''
                <div class="detail-item">
                    <span class="detail-label">High</span>
                    <span class="detail-value">$''' + f"{stock['high']:.2f}" + '''</span>
                </div>
                ''', unsafe_allow_html=True)
            
            # Day low
            if "low" in stock and stock["low"]:
                st.markdown('''
                <div class="detail-item">
                    <span class="detail-label">Low</span>
                    <span class="detail-value">$''' + f"{stock['low']:.2f}" + '''</span>
                </div>
                ''', unsafe_allow_html=True)
            
            # Volume
            if "volume" in stock and stock["volume"]:
                st.markdown('''
                <div class="detail-item">
                    <span class="detail-label">Volume</span>
                    <span class="detail-value">''' + format_large_number(stock["volume"]) + '''</span>
                </div>
                ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close details
            st.markdown('</div>', unsafe_allow_html=True)  # Close card

# Footer with Bloomberg terminal navigation bar
st.markdown('''
<nav class="bloomberg-nav">
    <div class="nav-item active">
        <div class="nav-icon">
            <svg viewBox="0 0 24 24" width="20" height="20" class="chart-icon">
                <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M3 3v18h18"/>
                <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
            </svg>
        </div>
        <span class="nav-label">Markets</span>
    </div>
    <div class="nav-item">
        <div class="nav-icon">
            <svg viewBox="0 0 24 24" width="20" height="20" class="briefcase-icon">
                <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M20 7H4a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2Z"/>
                <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
            </svg>
        </div>
        <span class="nav-label">Portfolio</span>
    </div>
    <div class="nav-item">
        <a href="https://www.linkedin.com/in/elmehdi-khouriss" target="_blank" class="nav-link">
            <div class="nav-icon">
                <svg viewBox="0 0 24 24" width="20" height="20" class="linkedin-icon">
                    <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>
                    <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M2 9h4v12H2z"/>
                    <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"/>
                </svg>
            </div>
            <span class="nav-label">LinkedIn</span>
        </a>
    </div>
    <div class="nav-item">
        <div class="nav-icon">
            <svg viewBox="0 0 24 24" width="20" height="20" class="settings-icon">
                <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
                <path fill="none" stroke="#00ff00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M9 12a3 3 0 1 0 6 0 3 3 0 0 0-6 0z"/>
            </svg>
        </div>
        <span class="nav-label">Settings</span>
    </div>
</nav>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close mobile container
