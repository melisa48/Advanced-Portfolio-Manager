import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from scipy.optimize import minimize

class AdvancedPortfolioManager:
    def __init__(self, initial_capital, risk_tolerance, tax_status='standard'):
        self.initial_capital = initial_capital
        self.risk_tolerance = risk_tolerance
        self.tax_status = tax_status
        self.portfolio = {}
        self.historical_data = {}
        self.transaction_history = []
    
    def fetch_market_data(self, tickers, period='5y'):
        """Fetch historical market data for given tickers"""
        try:
            data = {}
            for ticker in tickers:
                stock = yf.Ticker(ticker)
                history = stock.history(period=period)
                
                if not history.empty:
                    data[ticker] = history['Close']
                else:
                    print(f"No data found for {ticker}")
            
            return pd.DataFrame(data)
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return pd.DataFrame()
    
    def calculate_tax_efficiency(self, returns):
        """
        Calculate tax implications of portfolio
        
        :param returns: Portfolio returns
        :return: Tax efficiency score
        """
        annual_returns = returns.mean() * 252  # Annualized returns
        tax_rates = {
            'standard': 0.15,  # Default capital gains tax rate
            'retirement': 0,    # Tax-advantaged accounts
            'high_income': 0.20 # Higher tax bracket
        }
        
        tax_rate = tax_rates.get(self.tax_status, 0.15)
        
        # Calculate potential tax liability
        tax_liability = annual_returns * tax_rate
        
        # Tax efficiency score (lower is better)
        tax_efficiency_score = tax_liability
        
        return tax_efficiency_score
    
    def perform_loss_harvesting(self, returns):
        """
        Identify opportunities for tax loss harvesting
        
        :param returns: Asset returns
        :return: Recommended rebalancing
        """
        # Calculate cumulative returns for each asset
        cumulative_returns = (1 + returns).cumprod() - 1
        
        # Identify assets with unrealized losses
        loss_candidates = {}
        for column in cumulative_returns.columns:
            total_loss = cumulative_returns[column].iloc[-1]
            if total_loss < -0.1:  # More than 10% loss
                loss_candidates[column] = {
                    'action': 'sell',
                    'loss_percentage': total_loss * 100,
                    'reason': 'Tax loss harvesting'
                }
        
        return loss_candidates
    
    def calculate_portfolio_risk(self, returns):
        """
        Advanced risk calculation with multiple metrics
        
        :param returns: Portfolio returns
        :return: Comprehensive risk profile
        """
        risk_metrics = {
            'volatility': returns.std() * np.sqrt(252),  # Annualized
            'sharp_ratio': self._calculate_sharpe_ratio(returns),
            'max_drawdown': self._calculate_max_drawdown(returns),
            'value_at_risk': self._calculate_var(returns)
        }
        
        return risk_metrics
    
    def _calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """Calculate Sharpe Ratio"""
        return (returns.mean() * 252 - risk_free_rate) / (returns.std() * np.sqrt(252))
    
    def _calculate_max_drawdown(self, returns):
        """Calculate Maximum Drawdown"""
        cumulative_returns = (1 + returns).cumprod()
        peak = cumulative_returns.cummax()
        drawdown = (cumulative_returns - peak) / peak
        return drawdown.min()
    
    def _calculate_var(self, returns, confidence_level=0.95):
        """Calculate Value at Risk"""
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    def optimize_portfolio(self, tickers):
        """
        Advanced portfolio optimization with tax and risk considerations
        
        :param tickers: List of potential investment tickers
        :return: Optimized portfolio weights
        """
        data = self.fetch_market_data(tickers)
        returns = data.pct_change().dropna()
        
        # Mean-variance optimization
        def portfolio_variance(weights, cov_matrix):
            return np.dot(weights.T, np.dot(cov_matrix, weights))
        
        def portfolio_return(weights, expected_returns):
            return np.sum(expected_returns * weights)
        
        # Optimization constraints
        num_assets = len(tickers)
        constraints = (
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # weights sum to 1
        )
        bounds = tuple((0, 1) for _ in range(num_assets))
        
        # Initial guess: equal weights
        initial_weights = np.array([1/num_assets] * num_assets)
        
        # Expected returns and covariance
        expected_returns = returns.mean()
        cov_matrix = returns.cov()
        
        # Optimize
        result = minimize(
            lambda weights: portfolio_variance(weights, cov_matrix),
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        # Create portfolio dictionary
        portfolio_weights = {
            ticker: weight for ticker, weight in zip(tickers, result.x)
        }
        
        # Calculate additional metrics
        tax_efficiency = self.calculate_tax_efficiency(returns)
        loss_harvesting = self.perform_loss_harvesting(returns)
        risk_profile = self.calculate_portfolio_risk(returns)
        
        return {
            'weights': portfolio_weights,
            'tax_efficiency': tax_efficiency,
            'loss_harvesting': loss_harvesting,
            'risk_profile': risk_profile
        }

# Example usage
if __name__ == "__main__":
    # Initialize advanced portfolio manager
    manager = AdvancedPortfolioManager(
        initial_capital=10000,
        risk_tolerance=5,
        tax_status='standard'
    )
    
    # Define investment universe
    investment_universe = [
        'AAPL', 'GOOGL', 'MSFT', 'AMZN',  # Tech giants
        'JNJ', 'PG', 'KO',                # Consumer staples
        'BND', 'AGG',                     # Bond ETFs
        'VTI', 'SPY'                      # Broad market ETFs
    ]
    
    # Optimize portfolio
    result = manager.optimize_portfolio(investment_universe)
    
    # Print results
    print("Portfolio Weights:", result['weights'])
    print("\nTax Efficiency Score:", result['tax_efficiency'])
    print("\nLoss Harvesting Recommendations:", result['loss_harvesting'])
    print("\nRisk Profile:", result['risk_profile'])