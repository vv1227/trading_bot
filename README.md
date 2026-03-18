# 🚀 Binance Futures Trading Bot (Testnet)
A professional-grade Python trading bot for Binance Futures Testnet with both CLI and web UI interfaces.
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

## ✨ Features
- **Dual Interface**: Clean CLI and modern Streamlit web UI
- **Order Types**: Market, Limit, and Stop-Limit orders
- **Real-time Status**: API connection status and account balance
- **Order History**: View recent orders directly in the app
- **Comprehensive Logging**: All actions logged for debugging and auditing
- **Input Validation**: Robust validation before order submission
- **Error Handling**: Graceful handling of API and network errors

## 📸 Screenshots
### Web UI
┌─────────────────────────────────────────────────────────┐ 
│ 🚀 Binance Futures Trading Bot                          │ 
│ Testnet Mode | No Real Funds at Risk                    │ 
├─────────────────────────────────────────────────────────┤ 
│ ┌─────────────┐ ┌─────────────────────────────────┐    │ 
│ │ ⚙️ Settings │ │ 📝 Place Order                  │    │ 
│ │              │ │                                 │    │ 
│ │ 🔌 API      │ │ 🪙 Symbol: [BTCUSDT ▼]          │    │ 
│ │ ✅ Connected │ │ 📈 Side: ○ BUY ○ SELL            │    │ 
│ │              │ │ 📊 Qty: [0.01 ]                 │    │ 
│ │ Balance:    │ │ 💵 Price: [50000.00 ]           │    │ 
│ │ $10,000.00  │ │                                 │    │ 
│ │              │ │ [🟢 Place BUY Order]            │    │ 
│ └─────────────┘ └─────────────────────────────────┘    │ 
└─────────────────────────────────────────────────────────┘



### CLI Output
┌──────────────────────────────────────┐ 
│ 🚀 Binance Futures Trading Bot       │ 
│ Testnet Mode                         │ 
└──────────────────────────────────────┘

┌─ 📋 Order Summary ───────────────────┐ 
│ Symbol    BTCUSDT                    │ 
│ Side      BUY                        │ 
│ Type      MARKET                     │ 
│ Quantity  0.01                       │ 
└──────────────────────────────────────┘

✅ Order placed successfully!

┌─ 📊 Order Result ────────────────────┐ 
│ Order ID     123456789               │ 
│ Status       FILLED                  │ 
│ Executed Qty 0.01                    │ 
│ Avg Price    50123.45                │ 
└──────────────────────────────────────┘



## 🛠️ Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/trading-bot.git
cd trading-bot
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API Keys
1. Go to [testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Create an account and generate API keys
3. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
4. Edit `.env` with your keys:
```
API_KEY=your_testnet_api_key
API_SECRET=your_testnet_api_secret
```

## 🚀 Usage

### Web UI (Recommended)
```bash
streamlit run ui/app.py
```
Then open [localhost](http://localhost:8501) in your browser.

### CLI Commands

**Check API Status:**
```bash
python cli.py status
```

**Place a Market Order:**
```bash
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

**Place a Limit Order:**
```bash
python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3000
```

**Place a Stop-Limit Order:**
```bash
python cli.py order --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 --price 51000 --stop-price 50500
```

**View Order History:**
```bash
python cli.py history --limit 10
```

**Get Help:**
```bash
python cli.py --help
python cli.py order --help
```

## 📁 Project Structure
```
trading_bot/
├── bot/                    # Core bot module
│   ├── __init__.py        # Module exports
│   ├── client.py          # Binance client setup
│   ├── orders.py          # Order execution logic
│   ├── validators.py      # Input validation
│   └── logging_config.py  # Logging setup
├── ui/
│   └── app.py             # Streamlit web interface
├── logs/
│   └── trading.log        # Application logs
├── cli.py                 # Command-line interface
├── .env                   # API credentials (not in git)
├── .env.example           # Example env file
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## ⚠️ Assumptions & Notes
- **Testnet Only**: This bot is configured for Binance Futures Testnet. Do not use with real funds without proper modifications.
- **API Rate Limits**: The bot does not implement rate limiting. For production use, add appropriate delays.
- **Symbol Precision**: Quantity precision is hardcoded for supported symbols. Add dynamic precision fetching for additional pairs.
- **No Position Management**: This bot places orders but does not track or manage open positions.
- **Authentication**: API keys are stored in .env file. For production, use a secrets manager.

## 🔒 Security
- Never commit your `.env` file
- Use environment variables in production
- Rotate API keys regularly
- Enable IP restrictions on your API keys

## 📝 License
MIT License - feel free to use this project for learning and development.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

**Built with ❤️ using Python, Streamlit, and python-binance**

---
## Quick Start Commands
After setting up the project:
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env

# Edit .env with your Binance Testnet API keys

# Run the web UI
streamlit run ui/app.py

# Or use the CLI
python cli.py status
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

This project is fully functional and ready for GitHub. The UI is visually appealing with proper spacing, emojis, and status indicators. The CLI uses Rich for beautiful terminal output. All three order types (Market, Limit, Stop-Limit) are supported as a bonus feature.

