from flask import Flask, render_template, request, jsonify
from modules.pricing import run_pricing
from modules.factors import run_factors
from modules.portfolio import run_portfolio
from modules.score import run_score

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyse', methods=['POST'])
def analyse():
    data = request.get_json()
    ticker = data.get('ticker', '').upper().strip()
    period = data.get('period', '2y')

    if not ticker:
        return jsonify({'error': 'No ticker provided'}), 400

    try:
        pricing = run_pricing(ticker, period)
        return jsonify({
            'ticker': ticker,
            'pricing': pricing,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/factors', methods=['POST'])
def factors():
    data = request.get_json()
    ticker = data.get('ticker', '').upper().strip()
    period = data.get('period', '2y')
    try:
        result = run_factors(ticker, period)
        return jsonify({'ticker': ticker, 'factors': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/score', methods=['POST'])
def score():
    data = request.get_json()
    ticker = data.get('ticker', '').upper().strip()
    period = data.get('period', '2y')
    try:
        pricing = run_pricing(ticker, period)
        factors = run_factors(ticker, period)
        result = run_score(ticker, pricing, factors)
        return jsonify({'ticker': ticker, 'score': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio', methods=['POST'])
def portfolio():
    data = request.get_json()
    tickers = data.get('tickers', [])
    weights = data.get('weights', [])
    period = data.get('period', '2y')
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    try:
        from modules.portfolio import score_portfolio
        result = run_portfolio(tickers, weights, period)
        port_score = score_portfolio(
            result["metrics"],
            result["holdings"],
            result["min_var_weights"],
            result["max_sharpe_weights"],
            result["corr_matrix"]
        )
        result["portfolio_score"] = port_score
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
