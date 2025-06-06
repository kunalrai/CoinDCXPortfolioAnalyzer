import os
import hmac
import hashlib
import json
import time
import requests
from flask import Flask, render_template, jsonify, session, request, redirect, url_for
from dotenv import load_dotenv
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder
from supabase import create_client, Client
from functools import wraps
import sqlite3
from datetime import datetime, timedelta
import threading
from typing import Dict, List, Optional

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-super-secret-key-change-this-in-production-12345')

# Initialize Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated via session
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

class CoinDCXFuturesAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.coindcx.com"
        
    def _generate_signature(self, payload):
        if not self.api_secret:
            raise ValueError("API secret not configured")
        secret_bytes = bytes(self.api_secret, encoding='utf-8')
        return hmac.new(secret_bytes, payload.encode(), hashlib.sha256).hexdigest()
    
    def _make_request(self, endpoint, data=None, method='POST'):
        if not self.api_key or not self.api_secret:
            raise ValueError("API credentials not configured")
            
        if data is None:
            data = {}
        data['timestamp'] = int(round(time.time() * 1000))
        json_body = json.dumps(data, separators=(',', ':'))
        signature = self._generate_signature(json_body)
        
        headers = {
            'Content-Type': 'application/json',
            'X-AUTH-APIKEY': self.api_key,
            'X-AUTH-SIGNATURE': signature
        }
        
        try:
            if method == 'GET':
                response = requests.get(f"{self.base_url}{endpoint}", data=json_body, headers=headers, timeout=10)
            else:
                response = requests.post(f"{self.base_url}{endpoint}", data=json_body, headers=headers, timeout=10)
                
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
    
    def get_futures_positions(self, margin_currency="USDT"):
        return self._make_request('/exchange/v1/derivatives/futures/positions', {
            'page': '1',
            'size': '100',
            'margin_currency_short_name': [margin_currency]
        })
    
    def get_futures_orders(self, status="open,filled,cancelled", margin_currency="USDT"):
        return self._make_request('/exchange/v1/derivatives/futures/orders', {
            'status': status,
            'side': 'buy',
            'page': '1',
            'size': '100',
            'margin_currency_short_name': [margin_currency]
        })
    
    def get_futures_trades(self, pair=None, margin_currency="USDT"):
        from datetime import datetime, timedelta
        to_date = datetime.now().strftime('%Y-%m-%d')
        from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = {
            'from_date': from_date,
            'to_date': to_date,
            'page': '1',
            'size': '100',
            'margin_currency_short_name': [margin_currency]
        }
        if pair:
            data['pair'] = pair
            
        return self._make_request('/exchange/v1/derivatives/futures/trades', data)
    
    def get_futures_wallet(self):
        return self._make_request('/exchange/v1/derivatives/futures/wallets', method='GET')
    
    def get_current_prices(self):
        try:
            response = requests.get(f"https://public.coindcx.com/market_data/v3/current_prices/futures/rt", timeout=10)
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException as e:
            print(f"Price Error: {e}")
            return None

class FuturesPortfolioAnalyzer:
    def __init__(self, api_key, api_secret):
        self.api = CoinDCXFuturesAPI(api_key, api_secret) if api_key and api_secret else None
        self.current_prices = {}
        
    def _update_prices(self):
        if not self.api:
            return
        price_data = self.api.get_current_prices()
        if price_data and 'prices' in price_data:
            for pair, data in price_data['prices'].items():
                if 'ls' in data:
                    self.current_prices[pair] = float(data['ls'])
    
    def get_portfolio_data(self):
        if not self.api:
            return self._get_demo_data()
            
        try:
            positions = self.api.get_futures_positions()
            wallet = self.api.get_futures_wallet()
            self._update_prices()
            
            if not positions:
                return self._get_demo_data()
                
            return self._process_futures_data(positions, wallet)
        except Exception as e:
            print(f"Portfolio Error: {e}")
            return self._get_demo_data()
    
    def _get_demo_data(self):
        return {
            'positions': [
                {
                    'pair': 'B-BTC_USDT',
                    'active_pos': 0.1,
                    'avg_price': 45000,
                    'current_price': 47000,
                    'pnl': 200,
                    'pnl_percent': 4.44,
                    'locked_margin': 4500,
                    'leverage': 10,
                    'margin_type': 'crossed',
                    'liquidation_price': 41000,
                    'stop_loss_trigger': 42000,
                    'take_profit_trigger': 50000
                },
                {
                    'pair': 'B-ETH_USDT',
                    'active_pos': -2,
                    'avg_price': 3000,
                    'current_price': 2950,
                    'pnl': 100,
                    'pnl_percent': 1.67,
                    'locked_margin': 600,
                    'leverage': 10,
                    'margin_type': 'isolated',
                    'liquidation_price': 3300,
                    'stop_loss_trigger': None,
                    'take_profit_trigger': 2800
                }
            ],
            'wallet': {
                'total_balance': 10000,
                'available_balance': 5000,
                'total_pnl': 300,
                'margin_ratio': 0.05
            },
            'metrics': {
                'total_positions': 2,
                'long_positions': 1,
                'short_positions': 1,
                'total_pnl': 300,
                'best_performer': {'pair': 'B-BTC_USDT', 'pnl_percent': 4.44},
                'worst_performer': {'pair': 'B-ETH_USDT', 'pnl_percent': 1.67}
            }
        }
    
    def _calculate_liquidation_price(self, position, current_price):
        try:
            active_pos = float(position.get('active_pos', 0))
            avg_price = float(position.get('avg_price', 0))
            leverage = float(position.get('leverage', 1))
            locked_margin = float(position.get('locked_margin', 0))
            margin_type = position.get('margin_type', 'isolated')
            
            if active_pos == 0 or avg_price == 0:
                return 0
            
            if margin_type == 'isolated':
                if position.get('liquidation_price'):
                    return float(position.get('liquidation_price', 0))
                
                maintenance_margin_rate = 0.005
                
                if active_pos > 0:
                    liquidation_price = avg_price * (1 - (1/leverage) + maintenance_margin_rate)
                else:
                    liquidation_price = avg_price * (1 + (1/leverage) - maintenance_margin_rate)
                
                return max(0, liquidation_price)
            else:
                return 0
        except:
            return 0
    
    def _process_futures_data(self, positions, wallet):
        portfolio = {
            'positions': [],
            'wallet': {},
            'metrics': {}
        }
        
        active_positions = [p for p in positions if p.get('active_pos', 0) != 0]
        total_pnl = 0
        long_count = 0
        short_count = 0
        
        for pos in active_positions:
            pair = pos.get('pair', '')
            active_pos = float(pos.get('active_pos', 0))
            avg_price = float(pos.get('avg_price', 0))
            current_price = self._get_current_price(pair)
            
            if active_pos > 0:
                pnl = active_pos * (current_price - avg_price)
                long_count += 1
            else:
                pnl = abs(active_pos) * (avg_price - current_price)
                short_count += 1
            
            pnl_percent = (pnl / (abs(active_pos) * avg_price) * 100) if avg_price > 0 else 0
            total_pnl += pnl
            
            liquidation_price = self._calculate_liquidation_price(pos, current_price)
            
            portfolio['positions'].append({
                'pair': pair,
                'active_pos': active_pos,
                'avg_price': avg_price,
                'current_price': current_price,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'locked_margin': float(pos.get('locked_margin', 0)),
                'leverage': float(pos.get('leverage', 1)),
                'margin_type': pos.get('margin_type', 'isolated'),
                'liquidation_price': liquidation_price,
                'stop_loss_trigger': float(pos.get('stop_loss_trigger', 0)) if pos.get('stop_loss_trigger') else None,
                'take_profit_trigger': float(pos.get('take_profit_trigger', 0)) if pos.get('take_profit_trigger') else None
            })
        
        wallet_balance = 0
        available_balance = 0
        if wallet and len(wallet) > 0:
            wallet_data = wallet[0]
            wallet_balance = float(wallet_data.get('balance', 0)) + float(wallet_data.get('locked_balance', 0))
            available_balance = float(wallet_data.get('balance', 0))
        
        portfolio['wallet'] = {
            'total_balance': wallet_balance,
            'available_balance': available_balance,
            'total_pnl': total_pnl,
            'margin_ratio': 0
        }
        
        portfolio['metrics'] = {
            'total_positions': len(active_positions),
            'long_positions': long_count,
            'short_positions': short_count,
            'total_pnl': total_pnl,
            'best_performer': max(portfolio['positions'], key=lambda x: x['pnl_percent']) if portfolio['positions'] else None,
            'worst_performer': min(portfolio['positions'], key=lambda x: x['pnl_percent']) if portfolio['positions'] else None
        }
        
        return portfolio
    
    def _get_current_price(self, pair):
        if pair in self.current_prices:
            return self.current_prices[pair]
        return 0

# SQLite database initialization
def init_db():
    with sqlite3.connect('price_history.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                pair TEXT,
                price REAL,
                timestamp DATETIME,
                PRIMARY KEY (pair, timestamp)
            )
        ''')
        conn.commit()

def store_price(pair: str, price: float):
    """Store a price point in the database"""
    now = datetime.utcnow()
    with sqlite3.connect('price_history.db') as conn:
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO price_history (pair, price, timestamp) VALUES (?, ?, ?)',
                     (pair, price, now))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

def get_price_history(pair: str, limit: int = 96) -> List[float]:
    """Get historical prices for a pair"""
    with sqlite3.connect('price_history.db') as conn:
        c = conn.cursor()
        try:
            c.execute('''
                SELECT price FROM price_history 
                WHERE pair = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (pair, limit))
            prices = [row[0] for row in c.fetchall()]
            return prices[::-1]  # Reverse to get chronological order
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

def cleanup_old_prices():
    """Remove price data older than 24 hours"""
    cutoff = datetime.utcnow() - timedelta(hours=24)
    with sqlite3.connect('price_history.db') as conn:
        c = conn.cursor()
        try:
            c.execute('DELETE FROM price_history WHERE timestamp < ?', (cutoff,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database cleanup error: {e}")

@app.before_first_request
def initialize_database():
    init_db()
    
# Price update background task
def update_prices_task():
    while True:
        try:
            # Get all unique pairs from active positions
            pairs = get_active_pairs()  # You'll need to implement this based on your data structure
            
            for pair in pairs:
                try:
                    # Fetch current price from CoinDCX API
                    price = fetch_current_price(pair)  # You'll need to implement this
                    if price:
                        store_price(pair, price)
                except Exception as e:
                    print(f"Error updating price for {pair}: {e}")
            
            # Cleanup old data
            cleanup_old_prices()
            
        except Exception as e:
            print(f"Price update error: {e}")
        
        time.sleep(15)  # Wait 15 seconds before next update

# Start the background task
price_update_thread = threading.Thread(target=update_prices_task, daemon=True)
price_update_thread.start()

analyzer = FuturesPortfolioAnalyzer(
    os.getenv('COINDCX_API_KEY'),
    os.getenv('COINDCX_API_SECRET')
)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    # If user is already logged in, redirect to dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html', supabase_url=supabase_url, supabase_key=supabase_key)

@app.route('/signup')
def signup():
    # If user is already logged in, redirect to dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('signup.html', supabase_url=supabase_url, supabase_key=supabase_key)

@app.route('/auth/callback')
def auth_callback():
    return render_template('auth_callback.html', supabase_url=supabase_url, supabase_key=supabase_key)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/api/auth/session', methods=['POST'])
def set_session():
    """Set user session from frontend authentication"""
    try:
        data = request.get_json()
        if data and 'user' in data:
            session['user'] = data['user']
            session['access_token'] = data.get('access_token')
            return jsonify({'success': True})
        return jsonify({'error': 'Invalid session data'}), 400
    except Exception as e:
        print(f"Session error: {e}")
        return jsonify({'error': 'Failed to set session'}), 500

@app.route('/api/auth/user')
def get_user():
    """Get current user from session"""
    if 'user' in session:
        return jsonify({'user': session['user']})
    return jsonify({'user': None})

@app.route('/dashboard')

def dashboard():
    return render_template('dashboard.html', user=session.get('user'))

@app.route('/api/fear-greed')
def get_fear_greed_index():
    try:
        response = requests.get("https://api.alternative.me/fng/")
        data = response.json()
        index_data = data['data'][0]
        return jsonify({
            'value': int(index_data['value']),
            'classification': index_data['value_classification'],
            'timestamp': int(index_data['timestamp'])
        })
    except Exception as e:
        print(f"Fear & Greed API Error: {e}")
        return jsonify({'error': 'Failed to fetch index'}), 500

@app.route('/api/portfolio')
def get_portfolio():
    try:
        data = analyzer.get_portfolio_data()
        return jsonify(data)
    except Exception as e:
        print(f"Portfolio API Error: {e}")
        return jsonify({'error': 'Failed to fetch portfolio data'}), 500

@app.route('/api/charts')
def get_charts():
    try:
        data = analyzer.get_portfolio_data()
        positions = data['positions']
        
        # Create a figure for position sizes (needed for pairs list)
        size_fig = go.Figure(data=[
            go.Bar(
                x=[p['pair'].replace('B-', '') for p in positions],
                y=[abs(p['active_pos']) for p in positions],
                marker_color=['blue' if p['active_pos'] > 0 else 'orange' for p in positions],
                text=[f"{'Long' if p['active_pos'] > 0 else 'Short'}" for p in positions],
                textposition='auto'
            )
        ])
        
        # Extract price data for each position
        price_data = {
            'entry': [p['avg_price'] for p in positions],
            'current': [p['current_price'] for p in positions],
            'liquidation': [p.get('liquidation_price', None) for p in positions],
            'stopLoss': [p.get('stop_loss_trigger', None) for p in positions],
            'takeProfit': [p.get('take_profit_trigger', None) for p in positions]
        }
        
        return jsonify({
            'positions': json.loads(json.dumps(size_fig, cls=PlotlyJSONEncoder)),
            'prices': price_data
        })
    except Exception as e:
        print(f"Charts API Error: {e}")
        return jsonify({'error': 'Failed to generate charts'}), 500

@app.route('/api/price-history/<pair>')
def get_pair_history(pair):
    try:
        prices = get_price_history(pair)
        return jsonify({
            'success': True,
            'prices': prices
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/current-prices', methods=['POST'])
def get_current_prices():
    try:
        data = request.get_json()
        pairs = data.get('pairs', [])
        
        result = {}
        for pair in pairs:
            try:
                current_price = fetch_current_price(pair)  # Implement based on your data source
                historical_prices = get_price_history(pair)
                
                result[pair] = {
                    'current': current_price,
                    'historical': historical_prices
                }
            except Exception as e:
                print(f"Error fetching price for {pair}: {e}")
                result[pair] = {
                    'error': str(e)
                }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'type': 'futures',
        'api_configured': bool(os.getenv('COINDCX_API_KEY') and os.getenv('COINDCX_API_SECRET')),
        'timestamp': int(time.time())
    })

def get_active_pairs() -> List[str]:
    """Get list of trading pairs from active positions"""
    try:
        # Get positions from your existing portfolio endpoint
        positions = get_portfolio()  # Implement based on your data structure
        if positions and 'positions' in positions:
            return [pos['pair'] for pos in positions['positions']]
        return []
    except Exception as e:
        print(f"Error getting active pairs: {e}")
        return []

def fetch_current_price(pair: str) -> Optional[float]:
    """Fetch current price for a trading pair from CoinDCX API"""
    try:
        # Replace with your actual API endpoint
        response = requests.get(f'https://api.coindcx.com/exchange/ticker')
        if response.status_code == 200:
            data = response.json()
            # Find the matching pair in the response
            pair_data = next((item for item in data if item['market'] == pair), None)
            if pair_data:
                return float(pair_data['last_price'])
        return None
    except Exception as e:
        print(f"Error fetching price for {pair}: {e}")
        return None

def get_portfolio():
    """Get portfolio data from your existing implementation"""
    # This should return your existing portfolio data structure
    # Implement based on your current portfolio fetching logic
    pass

if __name__ == '__main__':
    print("Starting CoinDCX Futures Portfolio Analyzer...")
    print(f"API Key configured: {bool(os.getenv('COINDCX_API_KEY'))}")
    print(f"API Secret configured: {bool(os.getenv('COINDCX_API_SECRET'))}")
    app.run(debug=True, host='127.0.0.1', port=5000)
