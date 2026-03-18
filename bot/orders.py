"""Order execution module for Binance Futures."""
from typing import Optional, Dict, Any, List
from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance.enums import (
    SIDE_BUY,
    SIDE_SELL,
    ORDER_TYPE_MARKET,
    ORDER_TYPE_LIMIT,
    FUTURE_ORDER_TYPE_STOP,
    TIME_IN_FORCE_GTC,
)
from .validators import validate_order_params, format_quantity
from .logging_config import get_logger
def place_order(
    client: Client,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Place an order on Binance Futures Testnet.
    
    Args:
        client: Binance client instance.
        symbol: Trading pair symbol (e.g., BTCUSDT).
        side: Order side (BUY/SELL).
        order_type: Order type (MARKET/LIMIT/STOP_LIMIT).
        quantity: Order quantity.
        price: Limit price (required for LIMIT/STOP_LIMIT).
        stop_price: Stop trigger price (required for STOP_LIMIT).
        
    Returns:
        Dictionary with order result or error information.
    """
    logger = get_logger()
    
    is_valid, error_msg = validate_order_params(
        symbol, side, order_type, quantity, price, stop_price
    )
    
    if not is_valid:
        logger.error(f"Validation failed: {error_msg}")
        return {"success": False, "error": error_msg}
    
    symbol = symbol.upper()
    side = side.upper()
    order_type = order_type.upper()
    
    logger.info(
        f"Placing {order_type} {side} order: {quantity} {symbol}"
        + (f" @ {price}" if price else "")
        + (f" (stop: {stop_price})" if stop_price else "")
    )
    
    try:
        order_params = {
            "symbol": symbol,
            "side": SIDE_BUY if side == "BUY" else SIDE_SELL,
            "quantity": format_quantity(symbol, quantity),
        }
        
        if order_type == "MARKET":
            order_params["type"] = ORDER_TYPE_MARKET
            
        elif order_type == "LIMIT":
            order_params["type"] = ORDER_TYPE_LIMIT
            order_params["price"] = str(price)
            order_params["timeInForce"] = TIME_IN_FORCE_GTC
            
        elif order_type == "STOP_LIMIT":
            order_params["type"] = FUTURE_ORDER_TYPE_STOP
            order_params["price"] = str(price)
            order_params["stopPrice"] = str(stop_price)
            order_params["timeInForce"] = TIME_IN_FORCE_GTC
        
        response = client.futures_create_order(**order_params)
        
        result = {
            "success": True,
            "order_id": response.get("orderId"),
            "symbol": response.get("symbol"),
            "side": response.get("side"),
            "type": response.get("type"),
            "status": response.get("status"),
            "quantity": response.get("origQty"),
            "executed_qty": response.get("executedQty"),
            "price": response.get("price"),
            "avg_price": response.get("avgPrice"),
            "stop_price": response.get("stopPrice"),
            "time": response.get("updateTime"),
        }
        
        logger.info(
            f"Order placed successfully: ID={result['order_id']} | "
            f"Status={result['status']} | Executed={result['executed_qty']}"
        )
        
        return result
        
    except BinanceAPIException as e:
        logger.error(f"Binance API Error: {e.message} (Code: {e.code})")
        return {
            "success": False,
            "error": e.message,
            "error_code": e.code,
        }
        
    except Exception as e:
        logger.error(f"Unexpected error placing order: {e}")
        return {
            "success": False,
            "error": str(e),
        }
def get_recent_orders(
    client: Client,
    symbol: Optional[str] = None,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Fetch recent orders from the account.
    
    Args:
        client: Binance client instance.
        symbol: Filter by symbol (optional).
        limit: Maximum number of orders to return.
        
    Returns:
        List of recent orders.
    """
    logger = get_logger()
    
    try:
        params = {"limit": limit}
        if symbol:
            params["symbol"] = symbol.upper()
        
        orders = client.futures_get_all_orders(**params)
        
        formatted_orders = []
        for order in orders[-limit:]:
            formatted_orders.append({
                "order_id": order.get("orderId"),
                "symbol": order.get("symbol"),
                "side": order.get("side"),
                "type": order.get("type"),
                "status": order.get("status"),
                "quantity": order.get("origQty"),
                "executed_qty": order.get("executedQty"),
                "price": order.get("price"),
                "time": order.get("updateTime"),
            })
        
        logger.info(f"Retrieved {len(formatted_orders)} recent orders")
        return formatted_orders
        
    except BinanceAPIException as e:
        logger.error(f"Error fetching orders: {e.message}")
        return []
        
    except Exception as e:
        logger.error(f"Unexpected error fetching orders: {e}")
        return []

def get_order_status(client: Client, symbol: str, order_id: int) -> Dict[str, Any]:
    """
    Get updated status for specific order.
    
    Args:
        client: Binance client
        symbol: Trading pair
        order_id: Order ID
        
    Returns:
        Order status dict
    """
    logger = get_logger()
    
    try:
        order = client.futures_get_order(symbol=symbol.upper(), orderId=order_id)
        return {
            "status": order.get("status"),
            "executed_qty": order.get("executedQty", "0"),
            "avg_price": order.get("avgPrice", "0"),
            "price": order.get("price"),
        }
    except BinanceAPIException as e:
        logger.error(f"Error getting order status: {e.message}")
        return {"error": e.message}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"error": str(e)}


