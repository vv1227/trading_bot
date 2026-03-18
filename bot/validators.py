"""Input validation for trading orders."""
from typing import Optional, Tuple
from decimal import Decimal, InvalidOperation
VALID_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "SOLUSDT"]
VALID_SIDES = ["BUY", "SELL"]
VALID_ORDER_TYPES = ["MARKET", "LIMIT", "STOP_LIMIT"]
def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> Tuple[bool, str]:
    """
    Validate order parameters before submission.
    
    Args:
        symbol: Trading pair symbol.
        side: Order side (BUY/SELL).
        order_type: Order type (MARKET/LIMIT/STOP_LIMIT).
        quantity: Order quantity.
        price: Limit price (required for LIMIT and STOP_LIMIT).
        stop_price: Stop trigger price (required for STOP_LIMIT).
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    symbol = symbol.upper().strip()
    if symbol not in VALID_SYMBOLS:
        return False, f"Invalid symbol. Must be one of: {', '.join(VALID_SYMBOLS)}"
    
    side = side.upper().strip()
    if side not in VALID_SIDES:
        return False, f"Invalid side. Must be BUY or SELL"
    
    order_type = order_type.upper().strip()
    if order_type not in VALID_ORDER_TYPES:
        return False, f"Invalid order type. Must be one of: {', '.join(VALID_ORDER_TYPES)}"
    
    try:
        qty = Decimal(str(quantity))
        if qty <= 0:
            return False, "Quantity must be greater than 0"
    except (InvalidOperation, ValueError):
        return False, "Invalid quantity format"
    
    if order_type in ["LIMIT", "STOP_LIMIT"]:
        if price is None:
            return False, f"Price is required for {order_type} orders"
        try:
            p = Decimal(str(price))
            if p <= 0:
                return False, "Price must be greater than 0"
        except (InvalidOperation, ValueError):
            return False, "Invalid price format"
    
    if order_type == "STOP_LIMIT":
        if stop_price is None:
            return False, "Stop price is required for STOP_LIMIT orders"
        try:
            sp = Decimal(str(stop_price))
            if sp <= 0:
                return False, "Stop price must be greater than 0"
        except (InvalidOperation, ValueError):
            return False, "Invalid stop price format"
    
    return True, "Validation passed"
def format_quantity(symbol: str, quantity: float) -> str:
    """
    Format quantity according to symbol precision.
    
    Args:
        symbol: Trading pair symbol.
        quantity: Raw quantity value.
        
    Returns:
        Formatted quantity string.
    """
    precision_map = {
        "BTCUSDT": 3,
        "ETHUSDT": 3,
        "BNBUSDT": 2,
        "XRPUSDT": 1,
        "SOLUSDT": 2,
    }
    
    precision = precision_map.get(symbol.upper(), 3)
    return f"{quantity:.{precision}f}"

