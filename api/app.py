"""
Stock Market Data API
A RESTful API for accessing stock market data stored in PostgreSQL.
"""
import os
from flask import Flask, request
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import redis
from .database import get_db_connection, close_db_connection
from .models import get_stock_data, get_stock_symbols, get_stock_data_by_date_range

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Redis for caching
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_client = redis.Redis(host=redis_host, port=6379, db=0)

# Setup Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Stock Market Data API', version='1.0.0')

# Request counters
endpoints_counter = metrics.counter(
    'api_endpoints_calls', 'Number of calls to API endpoints',
    labels={'endpoint': lambda: request.endpoint}
)

# Initialize API
api = Api(
    app,
    version='1.0.0',
    title='Stock Market Data API',
    description='A RESTful API for accessing stock market data',
    doc='/docs'
)

# Define namespaces
ns_stocks = api.namespace('stocks', description='Stock operations')

# Define models
stock_model = api.model('Stock', {
    'id': fields.Integer(readonly=True, description='Stock data ID'),
    'symbol': fields.String(required=True, description='Stock symbol'),
    'date': fields.Date(required=True, description='Date of the stock data'),
    'open': fields.Float(description='Opening price'),
    'high': fields.Float(description='Highest price'),
    'low': fields.Float(description='Lowest price'),
    'close': fields.Float(description='Closing price'),
    'volume': fields.Integer(description='Trading volume')
})

# Routes
@ns_stocks.route('/')
class StockList(Resource):
    @endpoints_counter
    @api.doc('list_stocks')
    @api.marshal_list_with(stock_model)
    def get(self):
        """List all stock data with pagination"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        symbol = request.args.get('symbol', None)
        
        # Check cache first
        cache_key = f"stocks:list:{symbol}:{page}:{per_page}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            return eval(cached_data)
        
        # Get data from database
        conn = get_db_connection()
        data = get_stock_data(conn, symbol, page, per_page)
        close_db_connection(conn)
        
        # Cache the result for 5 minutes
        redis_client.setex(cache_key, 300, str(data))
        
        return data

@ns_stocks.route('/symbols')
class StockSymbols(Resource):
    @endpoints_counter
    @api.doc('list_symbols')
    def get(self):
        """List all available stock symbols"""
        # Check cache first
        cache_key = "stocks:symbols"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            return eval(cached_data)
        
        # Get data from database
        conn = get_db_connection()
        symbols = get_stock_symbols(conn)
        close_db_connection(conn)
        
        result = {'symbols': symbols}
        
        # Cache the result for 1 hour
        redis_client.setex(cache_key, 3600, str(result))
        
        return result

@ns_stocks.route('/<string:symbol>')
@api.doc(params={'symbol': 'The stock symbol'})
class Stock(Resource):
    @endpoints_counter
    @api.doc('get_stock')
    @api.marshal_with(stock_model)
    def get(self, symbol):
        """Get the latest stock data for a specific symbol"""
        # Check cache first
        cache_key = f"stocks:latest:{symbol}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            return eval(cached_data)
        
        # Get data from database
        conn = get_db_connection()
        data = get_stock_data(conn, symbol, 1, 1)
        close_db_connection(conn)
        
        if not data:
            api.abort(404, f"Stock {symbol} not found")
        
        # Cache the result for 5 minutes
        redis_client.setex(cache_key, 300, str(data[0]))
        
        return data[0]

@ns_stocks.route('/<string:symbol>/history')
@api.doc(params={
    'symbol': 'The stock symbol',
    'start_date': 'Start date (YYYY-MM-DD)',
    'end_date': 'End date (YYYY-MM-DD)'
})
class StockHistory(Resource):
    @endpoints_counter
    @api.doc('get_stock_history')
    @api.marshal_list_with(stock_model)
    def get(self, symbol):
        """Get historical stock data for a specific symbol within a date range"""
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # Check cache first
        cache_key = f"stocks:history:{symbol}:{start_date}:{end_date}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            return eval(cached_data)
        
        # Get data from database
        conn = get_db_connection()
        data = get_stock_data_by_date_range(conn, symbol, start_date, end_date)
        close_db_connection(conn)
        
        if not data:
            api.abort(404, f"No data found for {symbol} in the specified date range")
        
        # Cache the result for 10 minutes
        redis_client.setex(cache_key, 600, str(data))
        
        return data

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)