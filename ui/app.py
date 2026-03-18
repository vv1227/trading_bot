"""Streamlit UI for Binance Futures Trading Bot."""
import streamlit as st
import json
from datetime import datetime
from pathlib import Path
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
import time
st.set_page_config(
    page_title="Binance Futures Trading Bot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
    .stAlert {
        margin-top: 1rem;
    }
    .order-result {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)
def init_session_state():
    """Initialize session state variables."""
    if "client" not in st.session_state:
        st.session_state.client = None
    if "api_status" not in st.session_state:
        st.session_state.api_status = None
    if "order_result" not in st.session_state:
        st.session_state.order_result = None
def connect_client():
    """Connect to Binance Futures Testnet."""
    setup_logging()
    st.session_state.client = get_futures_client()
    if st.session_state.client:
        for attempt in range(3):
            status = check_api_status(st.session_state.client)
            if status.get("connected"):
                st.session_state.api_status = status
                return
            time.sleep(1)
        st.session_state.api_status = {"connected": False, "error": "Connection failed after retries"}
def render_sidebar():
    """Render the sidebar with connection status and settings."""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        st.markdown("---")
        
        st.subheader("🔌 API Connection")
        
        if st.button("🔄 Connect / Refresh", use_container_width=True):
            with st.spinner("Connecting..."):
                connect_client()
        
        if st.session_state.api_status:
            status = st.session_state.api_status
            if status.get("connected"):
                st.success("✅ Connected")
                st.metric("Available Balance", f"${status.get('available_balance', 0):,.2f}")
            else:
                st.error(f"❌ Disconnected")
                st.caption(status.get("error", "Unknown error"))
        else:
            st.info("Click Connect to start")
        
        st.markdown("---")
        
        st.subheader("📋 Order Type")
        order_type = st.radio(
            "Select order type:",
            options=["MARKET", "LIMIT", "STOP_LIMIT"],
            help="MARKET: Execute immediately at current price\n"
                 "LIMIT: Execute at specified price or better\n"
                 "STOP_LIMIT: Trigger limit order at stop price",
        )
        
        st.markdown("---")
        
        st.caption("🧪 Testnet Mode")
        st.caption("No real funds at risk")
        
    return order_type
def render_order_form(order_type: str):
    """Render the main order form."""
    
    st.header("📝 Place Order")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.selectbox(
            "🪙 Trading Pair",
            options=["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT"],
            help="Select the trading pair",
        )
        
        quantity = st.number_input(
            "📊 Quantity",
            min_value=0.001,
            value=0.01,
            step=0.001,
            format="%.3f",
            help="Order quantity",
        )
    
    with col2:
        side = st.radio(
            "📈 Side",
            options=["BUY", "SELL"],
            horizontal=True,
            help="BUY (Long) or SELL (Short)",
        )
        
        if order_type in ["LIMIT", "STOP_LIMIT"]:
            price = st.number_input(
                "💵 Limit Price",
                min_value=0.01,
                value=50000.0 if "BTC" in symbol else 3000.0,
                step=0.01,
                format="%.2f",
                help="Price at which to execute the order",
            )
        else:
            price = None
        
        if order_type == "STOP_LIMIT":
            stop_price = st.number_input(
                "🛑 Stop Price",
                min_value=0.01,
                value=49000.0 if "BTC" in symbol else 2900.0,
                step=0.01,
                format="%.2f",
                help="Price at which to trigger the limit order",
            )
        else:
            stop_price = None
    
    st.markdown("---")
    
    with st.container():
        st.subheader("📋 Order Preview")
        
        preview_cols = st.columns(4)
        preview_cols[0].metric("Symbol", symbol)
        preview_cols[1].metric("Side", side)
        preview_cols[2].metric("Type", order_type)
        preview_cols[3].metric("Quantity", f"{quantity}")
        
        if price:
            st.info(f"💵 Limit Price: **{price:,.2f}** USDT")
        if stop_price:
            st.warning(f"🛑 Stop Price: **{stop_price:,.2f}** USDT")
    
    st.markdown("---")
    
    is_valid, error_msg = validate_order_params(
        symbol, side, order_type, quantity, price, stop_price
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    
    with col_btn2:
        button_color = "primary" if side == "BUY" else "secondary"
        button_text = f"{'🟢' if side == 'BUY' else '🔴'} Place {side} Order"
        
        if st.button(
            button_text,
            use_container_width=True,
            type="primary",
            disabled=not st.session_state.client,
        ):
            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                with st.spinner("Placing order..."):
                    result = place_order(
                        client=st.session_state.client,
                        symbol=symbol,
                        side=side,
                        order_type=order_type,
                        quantity=quantity,
                        price=price,
                        stop_price=stop_price,
                    )
                    if result.get("success"):
                        # Poll for updated status
                        order_id = result["order_id"]
                        st.info("Order placed - checking status...")
                        for i in range(10):
                            status = get_order_status(st.session_state.client, symbol, order_id)
                            if status.get("error"):
                                break
                            st.metric("Current Status", status["status"])
                            st.metric("Executed Qty", status["executed_qty"])
                            st.metric("Avg Price", status["avg_price"])
                            time.sleep(2)
                            if st.session_state.order_result != result:  # Rerun
                                break
                        st.session_state.order_result = {**result, "final_status": status}
                    else:
                        st.session_state.order_result = result
    
    if not st.session_state.client:
        st.warning("⚠️ Please connect to the API first (see sidebar)")
def render_order_result():
    """Render the order result section."""
    if st.session_state.order_result:
        result = st.session_state.order_result
        
        st.markdown("---")
        st.header("📊 Order Result")
        
        if result.get("success"):
            st.success("✅ Order placed successfully!")
            
            result_cols = st.columns(4)
            result_cols[0].metric("Order ID", result.get("order_id", "N/A"))
            result_cols[1].metric("Status", result.get("status", "N/A"))
            result_cols[2].metric("Executed Qty", result.get("executed_qty", "N/A"))
            result_cols[3].metric("Avg Price", result.get("avg_price", "N/A"))
            
            with st.expander("📄 Full Response"):
                st.json(result)
        else:
            st.error(f"❌ Order failed: {result.get('error', 'Unknown error')}")
            if result.get("error_code"):
                st.caption(f"Error code: {result.get('error_code')}")
def render_recent_orders():
    """Render the recent orders section."""
    st.markdown("---")
    st.header("📜 Recent Orders")
    
    if not st.session_state.client:
        st.info("Connect to view order history")
        return
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", key="refresh_orders"):
            pass
    
    with st.spinner("Loading orders..."):
        orders = get_recent_orders(st.session_state.client, limit=10)
    
    if not orders:
        st.info("No orders found")
        return
    
    for order in reversed(orders[-5:]):
        side_emoji = "🟢" if order["side"] == "BUY" else "🔴"
        status_color = "green" if order["status"] == "FILLED" else "orange"
        
        with st.container():
            cols = st.columns([1, 2, 1, 1, 1, 2])
            cols[0].write(f"{side_emoji} **{order['side']}**")
            cols[1].write(f"**{order['symbol']}**")
            cols[2].write(order["type"])
            cols[3].write(f"Qty: {order['quantity']}")
            cols[4].write(f":{status_color}[{order['status']}]")
            cols[5].write(f"`ID: {order['order_id']}`")
def render_logs():
    """Render the logs preview section."""
    st.markdown("---")
    st.header("📝 Recent Logs")
    
    log_file = Path("logs/trading.log")
    
    if log_file.exists():
        with open(log_file, "r") as f:
            lines = f.readlines()
            recent_logs = lines[-20:] if len(lines) > 20 else lines
        
        if recent_logs:
            log_text = "".join(recent_logs)
            st.code(log_text, language="log")
        else:
            st.info("No logs yet")
    else:
        st.info("Log file not created yet. Place an order to generate logs.")
def main():
    """Main application entry point."""
    init_session_state()
    
    st.title("🚀 Binance Futures Trading Bot")
    st.caption("Testnet Mode | No Real Funds at Risk")
    
    order_type = render_sidebar()
    
    tab1, tab2, tab3 = st.tabs(["📝 Trade", "📜 History", "📝 Logs"])
    
    with tab1:
        render_order_form(order_type)
        render_order_result()
    
    with tab2:
        render_recent_orders()
    
    with tab3:
        render_logs()
if __name__ == "__main__":
    main()

