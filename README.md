# CoinDCX Portfolio Analyzer

![CoinDCX Portfolio Analyzer](https://github.com/user-attachments/assets/b237c6cc-c5f2-4954-879a-ff5f2640677a)

A comprehensive web-based portfolio analyzer for CoinDCX futures trading. This application provides real-time portfolio tracking, P&L analysis, position monitoring, and risk management tools for futures traders.

## Features

### 📊 Portfolio Analytics
- **Real-time Position Tracking**: Monitor all active futures positions with live P&L calculations
- **Portfolio Overview**: Get a comprehensive view of your trading portfolio with key metrics
- **Performance Analytics**: Track best and worst performing positions
- **Interactive Charts**: Visualize P&L and position sizes with dynamic charts

### 💰 Financial Metrics
- **P&L Calculation**: Real-time profit and loss tracking for all positions
- **Margin Analysis**: Monitor locked margins and available balance
- **Liquidation Price Calculation**: Automatic calculation of liquidation prices for risk management
- **Portfolio Balance**: Track total balance, available balance, and margin utilization

### 📈 Market Data Integration
- **Live Price Updates**: Real-time price feeds from CoinDCX
- **Fear & Greed Index**: Market sentiment indicator integration
- **Multi-timeframe Analysis**: Support for various trading timeframes

### 🛡️ Risk Management
- **Stop Loss Monitoring**: Track stop loss levels for all positions
- **Take Profit Tracking**: Monitor take profit targets
- **Leverage Analysis**: View leverage ratios for each position
- **Margin Type Support**: Both isolated and cross margin support

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Plotly.js for interactive visualizations
- **API Integration**: CoinDCX Futures API
- **Environment Management**: python-dotenv
- **HTTP Requests**: requests library
- **Data Processing**: pandas

## Installation

### Prerequisites
- Python 3.7 or higher
- CoinDCX account with API access
- Git (for cloning the repository)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/CoinDCXPortfolioAnalyzer.git
   cd CoinDCXPortfolioAnalyzer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   COINDCX_API_KEY=your_api_key_here
   COINDCX_API_SECRET=your_api_secret_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the dashboard**
   
   Open your browser and navigate to: `http://127.0.0.1:5000`

## API Configuration

### Getting CoinDCX API Credentials

1. Log in to your CoinDCX account
2. Navigate to API Management section
3. Create a new API key with futures trading permissions
4. Copy the API Key and Secret
5. Add them to your `.env` file

### API Permissions Required
- **Futures Trading**: Read access to positions, orders, and trades
- **Wallet Access**: Read access to futures wallet balance
- **Market Data**: Access to real-time price feeds

## Usage

### Dashboard Overview
The main dashboard provides:
- **Portfolio Summary**: Total balance, P&L, and key metrics
- **Active Positions**: List of all open futures positions
- **Performance Charts**: Visual representation of P&L and position sizes
- **Risk Metrics**: Liquidation prices and margin utilization

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard page |
| `/api/portfolio` | GET | Get portfolio data and positions |
| `/api/charts` | GET | Get chart data for visualizations |
| `/api/fear-greed` | GET | Get Fear & Greed index data |
| `/health` | GET | Health check and API status |

### Demo Mode
If API credentials are not configured, the application runs in demo mode with sample data for testing and development purposes.

## Project Structure

```
CoinDCXPortfolioAnalyzer/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (create this)
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation
└── templates/           # HTML templates
    ├── base.html        # Base template
    ├── header.html      # Header component
    ├── footer.html      # Footer component
    ├── dashboard.html   # Main dashboard
    └── futures_dashboard.html # Futures-specific dashboard
```

## Key Classes and Components

### `CoinDCXFuturesAPI`
Handles all API communications with CoinDCX:
- Authentication and signature generation
- Position and order management
- Real-time price data fetching
- Error handling and retry logic

### `FuturesPortfolioAnalyzer`
Core analytics engine:
- Portfolio data processing
- P&L calculations
- Risk metric computations
- Demo data generation

## Features in Detail

### Position Tracking
- **Long/Short Positions**: Support for both long and short futures positions
- **Average Price Tracking**: Monitor entry prices and current market prices
- **Size Monitoring**: Track position sizes and exposure
- **Leverage Analysis**: View leverage ratios for risk assessment

### Risk Management Tools
- **Liquidation Price Calculation**: Automatic calculation based on margin type
- **Stop Loss/Take Profit**: Monitor risk management orders
- **Margin Utilization**: Track margin usage and available balance
- **Position Sizing**: Analyze position sizes relative to portfolio

### Performance Analytics
- **Real-time P&L**: Live profit and loss calculations
- **Percentage Returns**: Performance metrics as percentages
- **Best/Worst Performers**: Identify top and bottom performing positions
- **Portfolio Metrics**: Comprehensive portfolio statistics

## Development

### Running in Development Mode
```bash
python app.py
```
The application will start with debug mode enabled on `http://127.0.0.1:5000`

### Production Deployment
For production deployment, use a WSGI server like Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Security Considerations

- **API Credentials**: Never commit API keys to version control
- **Environment Variables**: Use `.env` file for sensitive configuration
- **HTTPS**: Use HTTPS in production environments
- **Rate Limiting**: Be mindful of API rate limits

## Troubleshooting

### Common Issues

1. **API Authentication Errors**
   - Verify API key and secret are correct
   - Check API permissions on CoinDCX
   - Ensure timestamp synchronization

2. **Connection Issues**
   - Check internet connectivity
   - Verify CoinDCX API status
   - Review firewall settings

3. **Data Loading Problems**
   - Check API rate limits
   - Verify account has futures positions
   - Review error logs in console

### Error Handling
The application includes comprehensive error handling:
- API failures gracefully fall back to demo mode
- Network timeouts are handled with appropriate retries
- Invalid data is filtered and logged

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and informational purposes only. Trading futures involves substantial risk and may not be suitable for all investors. Past performance is not indicative of future results. Always conduct your own research and consider consulting with a financial advisor before making trading decisions.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review CoinDCX API documentation

---

**Note**: This application requires valid CoinDCX API credentials for live data. Demo mode is available for testing without API access.
