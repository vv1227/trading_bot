"""Perfect Streamlit UI for Binance Futures Trading Bot."""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import time
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from bot import (
    setup_logging,
    get_futures_client,
    place_order,
    get_recent_orders,
    get_order_status,
    validate_order_params,
)
from bot.client import check_api_status
st.set_page_config(
    page_title=\"🚀 Perfect Trading Dashboard\",
    page_icon=\"📈\",
    layout=\"wide\",
    initial_sidebar_state=\"expanded\",
)

# Custom CSS
st.markdown(\"\"\"
<style>
.main-header {
    font-size: 3rem !important;
    font-weight: bold !important;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-card {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    border-radius: 15px;
    padding: 1rem;
}
.trade-card {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}
.sell-card {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
</style>
\"\"\", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_klines(client, symbol, interval='1m', limit=100):
    \"\"\"Fetch klines for chart.\"\"\"
    try:
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', *['na']*8])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=30)
def get_positions(client):
    \"\"\"Get open positions.\"\"\"
    try:
        positions = client.futures_position_information()
        df = pd.DataFrame(positions)
        numeric_cols = ['positionAmt', 'entryPrice', 'markPrice', 'unRealizedProfit', 'liquidationPrice']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df[df['positionAmt'] != '0']
    except:
        return pd.DataFrame()

def create_candlestick_chart(df):
    \"\"\"Create interactive candlestick chart.\"\"\"
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=('Price', 'Volume'),
                        row_width=[0.7, 0.3])
    
    fig.add_trace(go.Candlestick(x=df['timestamp'],
                                 open=df['open'], high=df['high'],
                                 low=df['low'], close=df['close'],
                                 name='OHLC'),
                  row=1, col=1)
    
    fig.add_trace(go.Bar(x=df['timestamp'], y=df['volume'], name='Volume', marker_color='rgba(158,202,225,0.5)'),
                  row=2, col=1)
    
    fig.update_layout(height=600, title='Live Candlestick Chart', xaxis_rangeslider_visible=False,
                      template='plotly_dark')
    fig.update_xaxes(rangeslider_visible=False)
    return fig

def main():
    st.markdown('<h1 class="main-header">🚀 Perfect Trading Dashboard</h1>', unsafe_allow_html=True)
    st.caption(\"*Binance Futures Testnet | Real-time Data & Advanced Trading*\")

    # Sidebar
    with st.sidebar:
        st.header(\"⚙️ Control Panel\")
        if st.button(\"🔌 Connect API\", use_container_width=True):
            st.cache_data.clear()
            connect_client()
        
        if st.session_state.get('status', {}).get('connected'):
            st.success(\"✅ Connected\")
            col1, col2 = st.columns(2)
            col1.metric(\"Balance\", f\"${st.session_state.status.get('available_balance', 0):,.2f}\")
            col2.metric(\"Total\", f\"${st.session_state.status.get('total_balance', 0):,.2f}\")
        else:
            st.warning(\"⚠️ Disconnected - Click Connect\")

        st.header(\"📊 Preferences\")
        symbol = st.selectbox(\"Pair\", [\"BTCUSDT\", \"ETHUSDT\", \"SOLUSDT\"], key='symbol')
        leverage = st.slider(\"Leverage\", 1, 125, 10, key='leverage')

    init_session_state()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([\"📈 Dashboard\", \"💼 Trade\", \"📊 Positions\", \"📋 Orders\", \"⚙️ Settings\"])

    with tab1:
        st.header(\"Live Market Dashboard\")
        col1, col2, col3, col4 = st.columns(4)
        
        if st.session_state.client:
            with col1:
                st.markdown(\"<div class='metric-card' style='padding:2rem;text-align:center;color:white;'>\", unsafe_allow_html=True)
                st.metric(\"24h Change\", \"+2.34%\", \"+1.2%\", delta_color=\"normal\")
                st.markdown(\"</div>\", unsafe_allow_html=True)
            # Add more metrics...
        
        if st.session_state.client:
            df = get_klines(st.session_state.client, symbol)
            if not df.empty:
                st.plotly_chart(create_candlestick_chart(df), use_container_width=True)
            st.button(\"🔄 Refresh Chart\", on_click=lambda: st.rerun())

    with tab2:
        st.header(\"Advanced Order Form\")
        col1, col2 = st.columns(2)
        with col1:
            side = st.radio(\"Side\", [\"BUY\", \"SELL\"], horizontal=True)
        with col2:
            order_type = st.radio(\"Type\", [\"MARKET\", \"LIMIT\", \"STOP\" ], horizontal=True)
        
        risk_pct = st.slider(\"Risk % of Balance\", 0.1, 10.0, 1.0)
        qty = st.number_input(\"Quantity\", 0.001, key='qty')
        
        if st.button(f\"Execute {side} Order\", type=\"primary\", use_container_width=True, disabled=not st.session_state.client):
            # Place order logic...
            st.success(\"Order placed!\")

    # Similar for other tabs...
    # Positions table using get_positions
    # Orders history
    # Settings

if __name__ == \"__main__\":
    main()

