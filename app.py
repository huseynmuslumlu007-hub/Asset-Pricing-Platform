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

@app.route('/api/compare/stocks', methods=['POST'])
def compare_stocks():
    data = request.get_json()
    t1 = data.get('ticker1', '').upper().strip()
    t2 = data.get('ticker2', '').upper().strip()
    period = data.get('period', '2y')
    if not t1 or not t2:
        return jsonify({'error': 'Two tickers required'}), 400
    try:
        from modules.pricing import run_pricing
        from modules.factors import run_factors
        from modules.score import run_score
        p1 = run_pricing(t1, period)
        p2 = run_pricing(t2, period)
        f1 = run_factors(t1, period)
        f2 = run_factors(t2, period)
        s1 = run_score(t1, p1, f1)
        s2 = run_score(t2, p2, f2)
        return jsonify({
            'left':  {'ticker': t1, 'pricing': p1, 'factors': f1, 'score': s1},
            'right': {'ticker': t2, 'pricing': p2, 'factors': f2, 'score': s2},
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare/portfolios', methods=['POST'])
def compare_portfolios():
    data = request.get_json()
    period = data.get('period', '2y')
    left  = data.get('left',  [])
    right = data.get('right', [])
    if not left or not right:
        return jsonify({'error': 'Both portfolios required'}), 400
    try:
        from modules.portfolio import run_portfolio, score_portfolio
        def run(holdings):
            tickers = [h['ticker'] for h in holdings]
            weights = [h['weight'] for h in holdings]
            r = run_portfolio(tickers, weights, period)
            r['portfolio_score'] = score_portfolio(
                r['metrics'], r['holdings'],
                r['min_var_weights'], r['max_sharpe_weights'], r['corr_matrix'])
            return r
        return jsonify({'left': run(left), 'right': run(right)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/score/timeseries', methods=['POST'])
def score_timeseries():
    data = request.get_json()
    ticker = data.get('ticker', '').upper().strip()
    if not ticker:
        return jsonify({'error': 'Ticker required'}), 400
    try:
        import yfinance as yf
        import pandas as pd
        from modules.pricing import run_pricing
        from modules.factors import run_factors
        from modules.score import run_score

        # Get 2 years of data so each monthly window has enough history
        results = []
        today = pd.Timestamp.today()

        # Compute score at 12 monthly points going back 11 months
        for i in range(11, -1, -1):
            # End date = first day of each month
            end = (today - pd.DateOffset(months=i)).replace(day=1)
            label = end.strftime('%b %Y')
            try:
                # Use 1y window ending at this point
                start = end - pd.DateOffset(years=1)
                p = run_pricing(ticker, '1y', end_date=end.strftime('%Y-%m-%d'))
                f = run_factors(ticker, '1y', end_date=end.strftime('%Y-%m-%d'))
                s = run_score(ticker, p, f)
                results.append({
                    'date': label,
                    'composite': s['composite'],
                    'valuation': s['scores']['valuation'],
                    'momentum': s['scores']['momentum'],
                    'quality': s['scores']['quality'],
                    'risk_adjusted': s['scores']['risk_adjusted'],
                    'factor': s['scores']['factor'],
                })
            except Exception:
                pass

        return jsonify({'ticker': ticker, 'series': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
