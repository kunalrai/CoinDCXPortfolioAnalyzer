# CoinDCX Portfolio Analyzer

![Dashboard Screenshot](https://github.com/user-attachments/assets/310efa60-6ef0-4ac0-a02a-eea5f78c627c)

A powerful web-based tool for analyzing and managing your CoinDCX futures trading portfolio. Get real-time insights, performance analytics, and risk management features—all in one dashboard.

---

## 🚀 Features

### Portfolio Analytics
- **Live Position Tracking:** Monitor all open futures positions with up-to-date P&L
- **Comprehensive Overview:** View key portfolio metrics and performance highlights
- **Performance Insights:** Identify your best and worst trades
- **Interactive Charts:** Visualize P&L and position sizes with dynamic Plotly.js charts

### Financial Metrics
- **Real-Time P&L:** Track profit and loss for every position
- **Margin Monitoring:** See locked/available margin and utilization
- **Liquidation Price Calculation:** Automatic risk assessment for each position
- **Balance Overview:** Total, available, and margin balances at a glance

### Market Data Integration
- **Live Price Feeds:** Real-time data from CoinDCX
- **Fear & Greed Index:** Integrated market sentiment indicator
- **Multi-Timeframe Support:** Analyze positions across different timeframes

### Risk Management
- **Stop Loss & Take Profit:** Monitor risk management levels for all trades
- **Leverage Analysis:** View leverage ratios and margin types (isolated/cross)
- **Position Sizing:** Assess exposure and risk per trade

---

## 🛠️ Technology Stack

- **Backend:** Python (Flask)
- **Frontend:** HTML5, CSS3, JavaScript
- **Charts:** Plotly.js
- **API Integration:** CoinDCX Futures API
- **Environment:** python-dotenv
- **HTTP Requests:** requests
- **Data Processing:** pandas

---

## ⚡ Getting Started

### Prerequisites
- Python 3.7+
- CoinDCX account with API access
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/CoinDCXPortfolioAnalyzer.git
   cd CoinDCXPortfolioAnalyzer
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file:
   ```
   COINDCX_API_KEY=your_api_key_here
   COINDCX_API_SECRET=your_api_secret_here
   SUPABASE_URL=url
   SUPABASE_ANON_KEY=anon_key
   SECRET_KEY=key

   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open the dashboard**
   Visit [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔑 API Setup

1. Log in to your CoinDCX account
2. Navigate to API Management
3. Create new API key with futures trading permissions
4. Copy API Key and Secret
5. Add to your `.env` file

Required permissions:
- **Futures Trading:** Read positions, orders, trades
- **Wallet Access:** Read futures wallet balance
- **Market Data:** Real-time price feeds

---

## 🖥️ Usage

### Dashboard Overview
- Portfolio summary and key metrics
- Active positions and P&L
- Performance charts
- Risk management metrics

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/portfolio` | GET | Portfolio data |
| `/api/charts` | GET | Chart data |
| `/api/fear-greed` | GET | Fear & Greed index |
| `/health` | GET | Health check |

### Demo Mode
Available when running without API credentials.

---

## 📁 Project Structure

```
CoinDCXPortfolioAnalyzer/
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── templates/
    ├── base.html
    ├── header.html
    ├── footer.html
    ├── dashboard.html
    └── futures_dashboard.html
```

---

## 🧩 Core Components

### CoinDCXFuturesAPI
- API authentication
- Position and order management
- Price data fetching
- Error handling

### FuturesPortfolioAnalyzer
- Portfolio processing
- P&L calculations
- Risk metrics
- Demo data generation

---

## 🏗️ Development

Development mode:
```bash
python app.py
```

Production deployment:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 🔒 Security Best Practices

- Never commit API keys
- Use `.env` for configuration
- Enable HTTPS in production
- Monitor API rate limits

---

## 🛠️ Troubleshooting

Common issues and solutions:

1. **API Authentication**
   - Check credentials
   - Verify permissions
   - Check system time

2. **Connection Issues**
   - Check internet
   - Verify API status
   - Check firewall

3. **Data Problems**
   - Monitor rate limits
   - Check account status
   - Review error logs

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

## 📄 License

MIT License - see LICENSE file

---

## ⚠️ Disclaimer

This tool is for educational purposes only. Futures trading carries significant risk. Always conduct proper research and consult financial advisors before trading.

---

## 💬 Support

- Open GitHub issues
- Check troubleshooting
- Review API docs

---

**Note**: Requires valid CoinDCX API credentials for live data. Demo mode available for testing.
