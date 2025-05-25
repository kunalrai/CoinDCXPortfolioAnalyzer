import os
import hmac
import hashlib
import json
import time
import requests
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import plotly.graph_objects as go
import plotly.express as px
from plotly.utils import PlotlyJSONEncoder

load_dotenv()
app = Flask(__name__)

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

analyzer = FuturesPortfolioAnalyzer(
    os.getenv('COINDCX_API_KEY'),
    os.getenv('COINDCX_API_SECRET')
)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

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
        
        pnl_fig = go.Figure(data=[
            go.Bar(
                x=[p['pair'].replace('B-', '') for p in data['positions']],
                y=[p['pnl'] for p in data['positions']],
                marker_color=['green' if x > 0 else 'red' for x in [p['pnl'] for p in data['positions']]],
                text=[f"{p['pnl']:.2f}" for p in data['positions']],
                textposition='auto'
            )
        ])
        pnl_fig.update_layout(title="PnL by Position", yaxis_title="PnL (USDT)")
        
        size_fig = go.Figure(data=[
            go.Bar(
                x=[p['pair'].replace('B-', '') for p in data['positions']],
                y=[abs(p['active_pos']) for p in data['positions']],
                marker_color=['blue' if p['active_pos'] > 0 else 'orange' for p in data['positions']],
                text=[f"{'Long' if p['active_pos'] > 0 else 'Short'}" for p in data['positions']],
                textposition='auto'
            )
        ])
        size_fig.update_layout(title="Position Sizes", yaxis_title="Size")
        
        return jsonify({
            'pnl': json.loads(json.dumps(pnl_fig, cls=PlotlyJSONEncoder)),
            'positions': json.loads(json.dumps(size_fig, cls=PlotlyJSONEncoder))
        })
    except Exception as e:
        print(f"Charts API Error: {e}")
        return jsonify({'error': 'Failed to generate charts'}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'type': 'futures',
        'api_configured': bool(os.getenv('COINDCX_API_KEY') and os.getenv('COINDCX_API_SECRET')),
        'timestamp': int(time.time())
    })

if __name__ == '__main__':
    print("Starting CoinDCX Futures Portfolio Analyzer...")
    print(f"API Key configured: {bool(os.getenv('COINDCX_API_KEY'))}")
    print(f"API Secret configured: {bool(os.getenv('COINDCX_API_SECRET'))}")
    app.run(debug=True, host='127.0.0.1', port=5000)