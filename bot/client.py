"""Production Binance Futures Testnet client with timestamp sync."""
import os
import time
from typing import Optional
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException
from .logging_config import get_logger

class BinanceClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = Client(api_key, api_secret, testnet=True)
        self.client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"
        self.client.recvWindow = 60000
        
        # Sync time
        self._sync_time()
    
    def _sync_time(self):
        """Sync local time with Binance server."""
        logger = get_logger()
        try:
            server_time = self.client.futures_time()
            server_ms = server_time['serverTime']
            local_ms = int(time.time() * 1000)
            offset = server_ms - local_ms
            self.client.timestamp_offset = offset
            logger.info(f"Time synced. Server: {server_ms}, Local: {local_ms}, Offset: {offset}ms")
        except Exception as e:
            logger.warning(f"Time sync failed: {e}. Using fallback offset.")
            self.client.timestamp_offset = -5000  # Fallback
    
    def get_client(self) -> Client:
        """Get client with fresh time sync."""
        self._sync_time()
        return self.client
    
    def check_status(self) -> dict:
        """Check API status with retry."""
        logger = get_logger()
        client = self.get_client()
        for attempt in range(3):
            try:
                self._sync_time()
                server_time = client.futures_time()
                account = client.futures_account()
                status = {
                    "connected": True,
                    "server_time": server_time.get("serverTime"),
                    "total_balance": float(account.get("totalWalletBalance", 0)),
                    "available_balance": float(account.get("availableBalance", 0)),
                }
                logger.info(f"Connected | Balance: {status['available_balance']:.2f} USDT")
                return status
            except BinanceAPIException as e:
                if "timestamp" in e.message.lower():
                    logger.warning(f"Timestamp error (attempt {attempt+1}), resyncing...")
                    self._sync_time()
                else:
                    logger.error(f"API Error: {e.message}")
                    return {"connected": False, "error": e.message}
            time.sleep(1)
        return {"connected": False, "error": "Failed after retries"}

def get_futures_client() -> Optional[Client]:
    """Backward compatible - get synced client."""
    load_dotenv()
    logger = get_logger()
    
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")
    
    if not api_key or not api_secret:
        logger.error("API_KEY and API_SECRET must be set in .env file")
        return None
    
    try:
        bc = BinanceClient(api_key, api_secret)
        return bc.get_client()
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
        return None

def check_api_status(client: Client) -> dict:
    """Backward compatible status check."""
    logger = get_logger()
    
    try:
        server_time = client.futures_time()
        account = client.futures_account()
        
        status = {
            "connected": True,
            "server_time": server_time.get("serverTime"),
            "total_balance": float(account.get("totalWalletBalance", 0)),
            "available_balance": float(account.get("availableBalance", 0)),
        }
        
        logger.info(f"API Status: Connected | Balance: {status['available_balance']:.2f} USDT")
        return status
        
    except BinanceAPIException as e:
        logger.error(f"API Error: {e.message}")
        return {"connected": False, "error": e.message}
        
    except Exception as e:
        logger.error(f"Connection Error: {e}")
        return {"connected": False, "error": str(e)}

