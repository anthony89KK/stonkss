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

# Custom CSS for fixed Bloomberg terminal-like design
st.markdown("""
<style>
    /* Base styles and dark theme */
    .stApp {
        background-color: #000000;
        max-width: 100%;
        margin: 0;
        padding: 0;
        font-family: 'Courier New', monospace;
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
        display: flex;
        justify-content: space-between;
        padding: 10px 18px;
        font-size: 18px;
        color: #00ff00;
        border-bottom: 1px solid #003300;
        background: #000000;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 100;
        font-family: 'Courier New', monospace;
        height: 50px;
    }
    
    /* Main content area */
    .main-content {
        position: fixed;
        top: 50px;
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
        font-family: 'Courier New', monospace;
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
        font-family: 'Courier New', monospace;
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
        font-family: 'Courier New', monospace;
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
        font-family: 'Courier New', monospace;
    }
    
    .stock-price {
        font-size: 32px;
        font-weight: bold;
        color: #00ff00;
        margin: 12px 0;
        font-family: 'Courier New', monospace;
    }
    
    .price-change-positive {
        color: #00ff00;
        font-weight: bold;
        font-size: 20px;
        font-family: 'Courier New', monospace;
    }
    
    .price-change-negative {
        color: #ff0000;
        font-weight: bold;
        font-size: 20px;
        font-family: 'Courier New', monospace;
    }
    
    .stock-details {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 12px;
        font-size: 16px;
        font-family: 'Courier New', monospace;
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
        font-family: 'Courier New', monospace;
    }
    
    .detail-value {
        color: #00ff00;
        font-weight: bold;
        font-size: 18px;
        font-family: 'Courier New', monospace;
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
        font-family: 'Courier New', monospace;
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
        font-family: 'Courier New', monospace;
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
        font-family: 'Courier New', monospace !important;
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
        font-family: 'Courier New', monospace !important;
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
        font-family: 'Courier New', monospace !important;
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
        font-family: 'Courier New', monospace !important;
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
        padding: 8px 0;
        background: #000000;
        border-top: 1px solid #003300;
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 80px;
        z-index: 100;
    }
    
    .nav-item {
        display: flex;
        flex-direction: column;
        align-items: center;
        color: #00ff00;
        font-size: 16px;
        padding: 4px 8px;
        font-family: 'Courier New', monospace;
    }
    
    .nav-icon {
        font-size: 24px;
        margin-bottom: 4px;
    }
    
    .nav-text {
        font-size: 16px;
        font-family: 'Courier New', monospace;
    }
    
    .nav-item.active {
        background: #001100;
        border: 1px solid #003300;
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
</style>
""", unsafe_allow_html=True)

# API configuration
API_KEY = "d655f228ca6cf8d390a7319c52b3ce486a5b085a"

# Session state initialization
if 'last_updated' not in st.session_state:
    st.session_state.last_updated = None
if 'history' not in st.session_state:
    st.session_state.history = []

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

# Status bar
current_time = get_current_time()
st.markdown(f'''
<div class="status-bar">
    <span>4G</span>
    <span>{current_time}</span>
    <span>100%</span>
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

# Display current stock if available
if st.session_state.history:
    current_stock = st.session_state.history[0]
    
    st.markdown(f'<div class="stock-card current-stock">', unsafe_allow_html=True)
    
    # Symbol and last updated
    st.markdown(f'''
    <div class="stock-symbol">
        <span>{current_stock["symbol"]}</span>
        <span class="timestamp">Updated {current_stock.get("timestamp", "now")}</span>
    </div>
    ''', unsafe_allow_html=True)
    
    # Price
    st.markdown(f'<div class="stock-price">${current_stock["price"]:.2f}</div>', unsafe_allow_html=True)
    
    # Price change
    change_class = "price-change-positive" if current_stock['percent_change'] >= 0 else "price-change-negative"
    change_symbol = "▲" if current_stock['percent_change'] >= 0 else "▼"
    price_diff = abs(current_stock["price"] - current_stock["prev_close"])
    st.markdown(f'<div class="{change_class}">{change_symbol} ${price_diff:.2f} ({abs(current_stock["percent_change"]):.2f}%)</div>', unsafe_allow_html=True)
    
    # Divider
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Additional stock details
    st.markdown('''
    <div class="stock-details">
        <div class="detail-item">
            <span class="detail-label">Prev Close</span>
            <span class="detail-value">$''' + f"{current_stock['prev_close']:.2f}" + '''</span>
        </div>
    ''', unsafe_allow_html=True)
    
    # Day high
    if "high" in current_stock and current_stock["high"]:
        st.markdown('''
        <div class="detail-item">
            <span class="detail-label">High</span>
            <span class="detail-value">$''' + f"{current_stock['high']:.2f}" + '''</span>
        </div>
        ''', unsafe_allow_html=True)
    
    # Day low
    if "low" in current_stock and current_stock["low"]:
        st.markdown('''
        <div class="detail-item">
            <span class="detail-label">Low</span>
            <span class="detail-value">$''' + f"{current_stock['low']:.2f}" + '''</span>
        </div>
        ''', unsafe_allow_html=True)
    
    # Volume
    if "volume" in current_stock and current_stock["volume"]:
        st.markdown('''
        <div class="detail-item">
            <span class="detail-label">Volume</span>
            <span class="detail-value">''' + format_large_number(current_stock["volume"]) + '''</span>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close details
    st.markdown('</div>', unsafe_allow_html=True)  # Close card

# Recent searches section
if len(st.session_state.history) > 1:
    st.markdown('<div class="section-header">Recent</div>', unsafe_allow_html=True)
    
    for stock in st.session_state.history[1:]:
        st.markdown('<div class="stock-card">', unsafe_allow_html=True)
        
        # Symbol
        st.markdown(f'<div class="stock-symbol">{stock["symbol"]}</div>', unsafe_allow_html=True)
        
        # Price and change in one row
        change_class = "price-change-positive" if stock['percent_change'] >= 0 else "price-change-negative"
        change_symbol = "▲" if stock['percent_change'] >= 0 else "▼"
        
        st.markdown(f'''
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="stock-price" style="margin: 0; font-size: 22px;">${stock["price"]:.2f}</div>
            <div class="{change_class}">{change_symbol} {abs(stock["percent_change"]):.2f}%</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Footer with mobile-like navigation bar
st.markdown('''
<div class="nav-bar">
    <div class="nav-item active">
        <div class="nav-icon">📈</div>
        <div>Markets</div>
    </div>
    <div class="nav-item">
        <div class="nav-icon">💼</div>
        <div>Portfolio</div>
    </div>
    <div class="nav-item">
        <a href="https://www.linkedin.com/in/elmehdi-khouriss" target="_blank" style="text-decoration: none; color: inherit; display: flex; flex-direction: column; align-items: center; margin-top: 4px;">
            <div class="nav-icon" style="display: flex; justify-content: center; width: 100%;">
                <img src="data:image/png;base64,''' + base64.b64encode(open("linkedin.png", "rb").read()).decode() + '''" style="width: 28px; height: 28px;">
            </div>
            <div class="nav-text">LinkedIn</div>
        </a>
    </div>
    <div class="nav-item">
        <div class="nav-icon">⚙️</div>
        <div>Settings</div>
    </div>
</div>

<div class="app-footer"></div>
''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close mobile container
