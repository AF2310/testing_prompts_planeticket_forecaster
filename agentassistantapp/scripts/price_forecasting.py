"""
Airline Ticket Price Forecasting Script
Implements multiple forecasting models including ARIMA, Prophet, and Machine Learning approaches.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
import pickle
import warnings

warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PriceForecastEngine:
    """Forecasts airline ticket prices using multiple models."""

    def __init__(self, data_file='data/airline_prices_processed.csv'):
        self.data_file = Path(data_file)
        self.df = None
        self.forecasts = {}
        self.models = {}

    def load_data(self):
        """Load processed data."""
        try:
            self.df = pd.read_csv(self.data_file)
            self.df['departure_date'] = pd.to_datetime(self.df['departure_date'])
            logger.info(f"Loaded {len(self.df)} records for forecasting")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False

    def prepare_timeseries_data(self, group_by=None):
        """Prepare time series data for forecasting."""
        if group_by is None:
            # Overall market trend
            ts_data = self.df.groupby('departure_date')['price'].mean().sort_index()
        else:
            # Grouped time series (by airline or route)
            grouped = self.df.groupby(group_by + ['departure_date'])['price'].mean()
            ts_data = grouped
        
        return ts_data

    def forecast_exponential_smoothing(self, ts_data, forecast_periods=14):
        """Simple Exponential Smoothing forecast."""
        logger.info(f"Forecasting with Exponential Smoothing (periods: {forecast_periods})...")
        
        try:
            from statsmodels.tsa.holtwinters import ExponentialSmoothing
            
            # Fit model
            model = ExponentialSmoothing(ts_data, trend='add', seasonal=None, initialization_method='estimated')
            fitted = model.fit(optimized=True)
            
            # Forecast
            forecast = fitted.forecast(steps=forecast_periods)
            
            # Calculate confidence intervals
            conf_int = self._calculate_confidence_intervals(ts_data, forecast)
            
            return {
                'model': 'Exponential Smoothing',
                'forecast': forecast,
                'confidence_intervals': conf_int,
                'fitted_model': fitted,
                'rmse': self._calculate_rmse(ts_data, fitted.fittedvalues)
            }
        except Exception as e:
            logger.error(f"Error in Exponential Smoothing: {e}")
            return None

    def forecast_arima(self, ts_data, forecast_periods=14):
        """ARIMA time series forecast."""
        logger.info(f"Forecasting with ARIMA (periods: {forecast_periods})...")
        
        try:
            from statsmodels.tsa.arima.model import ARIMA
            
            # Fit ARIMA model
            model = ARIMA(ts_data, order=(1, 1, 1))
            fitted = model.fit()
            
            # Forecast
            forecast_result = fitted.get_forecast(steps=forecast_periods)
            forecast = forecast_result.predicted_mean
            conf_int_df = forecast_result.conf_int()
            
            return {
                'model': 'ARIMA',
                'forecast': forecast,
                'confidence_intervals': {
                    'lower': conf_int_df.iloc[:, 0].values,
                    'upper': conf_int_df.iloc[:, 1].values
                },
                'fitted_model': fitted,
                'rmse': self._calculate_rmse(ts_data, fitted.fittedvalues)
            }
        except Exception as e:
            logger.error(f"Error in ARIMA: {e}")
            return None

    def forecast_linear_regression(self, ts_data, forecast_periods=14):
        """Linear regression based forecast with seasonal features."""
        logger.info(f"Forecasting with Linear Regression (periods: {forecast_periods})...")
        
        try:
            from sklearn.linear_model import LinearRegression
            
            # Prepare features
            X = np.arange(len(ts_data)).reshape(-1, 1)
            y = ts_data.values
            
            # Add cyclical features for seasonality
            day_of_year = pd.Series(range(len(ts_data)), index=ts_data.index).apply(
                lambda x: np.sin(2 * np.pi * x / 365)
            ).values.reshape(-1, 1)
            
            X_features = np.hstack([X, day_of_year])
            
            # Fit model
            model = LinearRegression()
            model.fit(X_features, y)
            
            # Forecast
            future_X = np.arange(len(ts_data), len(ts_data) + forecast_periods).reshape(-1, 1)
            future_day = pd.Series(range(len(ts_data), len(ts_data) + forecast_periods)).apply(
                lambda x: np.sin(2 * np.pi * x / 365)
            ).values.reshape(-1, 1)
            
            future_X_features = np.hstack([future_X, future_day])
            forecast = model.predict(future_X_features)
            
            # Calculate prediction intervals
            residuals = y - model.predict(X_features)
            std_error = np.std(residuals)
            
            return {
                'model': 'Linear Regression with Seasonal Features',
                'forecast': forecast,
                'confidence_intervals': {
                    'lower': forecast - 1.96 * std_error,
                    'upper': forecast + 1.96 * std_error
                },
                'fitted_model': model,
                'rmse': self._calculate_rmse(y, model.predict(X_features))
            }
        except Exception as e:
            logger.error(f"Error in Linear Regression: {e}")
            return None

    def forecast_moving_average(self, ts_data, forecast_periods=14, window=7):
        """Moving average forecast."""
        logger.info(f"Forecasting with Moving Average (window: {window}, periods: {forecast_periods})...")
        
        try:
            # Calculate moving average
            ma = ts_data.rolling(window=window).mean()
            
            # Use last MA value as forecast
            last_ma = ma.iloc[-1]
            forecast = np.array([last_ma] * forecast_periods)
            
            # Confidence intervals based on historical volatility
            volatility = ts_data.std()
            
            return {
                'model': f'Moving Average (window={window})',
                'forecast': forecast,
                'confidence_intervals': {
                    'lower': forecast - 1.96 * volatility,
                    'upper': forecast + 1.96 * volatility
                },
                'fitted_model': None,
                'rmse': self._calculate_rmse(ts_data.iloc[window:], ma.iloc[window:])
            }
        except Exception as e:
            logger.error(f"Error in Moving Average: {e}")
            return None

    def _calculate_rmse(self, actual, predicted):
        """Calculate Root Mean Squared Error."""
        if len(actual) > len(predicted):
            actual = actual[:len(predicted)]
        elif len(predicted) > len(actual):
            predicted = predicted[:len(actual)]
        
        return np.sqrt(np.mean((actual - predicted) ** 2))

    def _calculate_confidence_intervals(self, actual, forecast, confidence=0.95):
        """Calculate confidence intervals."""
        residuals = actual.iloc[-len(forecast):].values - forecast if len(forecast) <= len(actual) else np.zeros(len(forecast))
        std_error = np.std(residuals) if len(residuals) > 0 else actual.std()
        z_score = 1.96 if confidence == 0.95 else 2.576
        
        return {
            'lower': forecast - z_score * std_error,
            'upper': forecast + z_score * std_error
        }

    def run_forecasts(self):
        """Execute all forecasting models."""
        logger.info("\n" + "="*50)
        logger.info("RUNNING PRICE FORECASTS")
        logger.info("="*50)
        
        if not self.load_data():
            return False
        
        # Prepare time series data
        ts_data = self.prepare_timeseries_data()
        
        # Run multiple forecasting models
        forecast_period = 14  # Forecast 14 days ahead
        
        # Model 1: Exponential Smoothing
        es_forecast = self.forecast_exponential_smoothing(ts_data, forecast_period)
        if es_forecast:
            self.forecasts['exponential_smoothing'] = es_forecast
        
        # Model 2: ARIMA
        arima_forecast = self.forecast_arima(ts_data, forecast_period)
        if arima_forecast:
            self.forecasts['arima'] = arima_forecast
        
        # Model 3: Linear Regression
        lr_forecast = self.forecast_linear_regression(ts_data, forecast_period)
        if lr_forecast:
            self.forecasts['linear_regression'] = lr_forecast
        
        # Model 4: Moving Average
        ma_forecast = self.forecast_moving_average(ts_data, forecast_period)
        if ma_forecast:
            self.forecasts['moving_average'] = ma_forecast
        
        return True

    def create_forecast_report(self):
        """Create detailed forecast report."""
        logger.info("\nGenerating forecast report...")
        
        if not self.forecasts:
            logger.warning("No forecasts available!")
            return
        
        output_file = Path('reports') / 'price_forecast_report.txt'
        output_file.parent.mkdir(exist_ok=True)
        
        ts_data = self.prepare_timeseries_data()
        future_dates = pd.date_range(
            start=ts_data.index[-1] + timedelta(days=1),
            periods=14
        )
        
        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("AIRLINE TICKET PRICE FORECAST REPORT\n")
            f.write("="*70 + "\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Current Market Average Price: €{ts_data.iloc[-1]:.2f}\n")
            f.write(f"Forecast Period: {future_dates[0].date()} to {future_dates[-1].date()}\n\n")
            
            f.write("="*70 + "\n")
            f.write("MODEL COMPARISON\n")
            f.write("="*70 + "\n\n")
            
            forecast_summary = []
            
            for model_name, forecast_data in self.forecasts.items():
                f.write(f"MODEL: {forecast_data['model']}\n")
                f.write(f"RMSE: €{forecast_data['rmse']:.2f}\n\n")
                
                f.write("Forecast Values (EUR):\n")
                f.write("-"*70 + "\n")
                
                forecast_avg = forecast_data['forecast'].mean()
                forecast_max = forecast_data['forecast'].max()
                forecast_min = forecast_data['forecast'].min()
                
                f.write(f"Average Forecast: €{forecast_avg:.2f}\n")
                f.write(f"Max Forecast: €{forecast_max:.2f}\n")
                f.write(f"Min Forecast: €{forecast_min:.2f}\n")
                f.write(f"Confidence Interval (95%):\n")
                f.write(f"  Lower Bound: €{forecast_data['confidence_intervals']['lower'].mean():.2f}\n")
                f.write(f"  Upper Bound: €{forecast_data['confidence_intervals']['upper'].mean():.2f}\n\n")
                
                forecast_summary.append({
                    'Model': forecast_data['model'],
                    'Average': forecast_avg,
                    'RMSE': forecast_data['rmse']
                })
                
                f.write("Daily Forecast:\n")
                for i, date in enumerate(future_dates):
                    f.write(f"  {date.date()}: €{forecast_data['forecast'][i]:.2f}\n")
                
                f.write("\n" + "-"*70 + "\n\n")
            
            # Ensemble forecast (average of all models)
            f.write("="*70 + "\n")
            f.write("ENSEMBLE FORECAST (Average of All Models)\n")
            f.write("="*70 + "\n\n")
            
            ensemble_forecast = np.mean([f['forecast'] for f in self.forecasts.values()], axis=0)
            
            f.write(f"Average Forecast: €{ensemble_forecast.mean():.2f}\n")
            f.write(f"Max Forecast: €{ensemble_forecast.max():.2f}\n")
            f.write(f"Min Forecast: €{ensemble_forecast.min():.2f}\n\n")
            
            f.write("Daily Forecast:\n")
            for i, date in enumerate(future_dates):
                f.write(f"  {date.date()}: €{ensemble_forecast[i]:.2f}\n")
            
            # Recommendations
            f.write("\n" + "="*70 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("="*70 + "\n\n")
            
            current_price = ts_data.iloc[-1]
            forecast_avg = ensemble_forecast.mean()
            price_change = ((forecast_avg - current_price) / current_price) * 100
            
            if price_change > 5:
                f.write("• PRICE INCREASE EXPECTED\n")
                f.write(f"  Expected increase: {price_change:.1f}%\n")
                f.write("  Recommendation: Book flights now if planning to travel in next 14 days\n\n")
            elif price_change < -5:
                f.write("• PRICE DECREASE EXPECTED\n")
                f.write(f"  Expected decrease: {abs(price_change):.1f}%\n")
                f.write("  Recommendation: Consider waiting before booking\n\n")
            else:
                f.write("• STABLE PRICING EXPECTED\n")
                f.write(f"  Expected change: {price_change:.1f}%\n")
                f.write("  Recommendation: Book when convenient\n\n")
            
            f.write("• General Best Practices:\n")
            f.write("  - Midweek flights (Tuesday-Thursday) tend to be cheaper\n")
            f.write("  - Book 2-3 weeks in advance for better prices\n")
            f.write("  - Monitor prices trends over time before booking\n")
            f.write("  - Be flexible with travel dates when possible\n")
        
        logger.info(f"Forecast report saved to {output_file}")

    def save_forecasts(self):
        """Save forecast results to CSV."""
        if not self.forecasts:
            logger.warning("No forecasts to save!")
            return
        
        future_dates = pd.date_range(
            start=pd.to_datetime(self.df['departure_date'].max()) + timedelta(days=1),
            periods=14
        )
        
        forecast_df = pd.DataFrame({'date': future_dates})
        
        for model_name, forecast_data in self.forecasts.items():
            forecast_df[f'{model_name}_price'] = forecast_data['forecast']
            forecast_df[f'{model_name}_lower'] = forecast_data['confidence_intervals']['lower']
            forecast_df[f'{model_name}_upper'] = forecast_data['confidence_intervals']['upper']
        
        # Add ensemble forecast
        ensemble = np.mean([f['forecast'] for f in self.forecasts.values()], axis=0)
        forecast_df['ensemble_forecast'] = ensemble
        
        output_file = Path('data') / 'price_forecasts.csv'
        forecast_df.to_csv(output_file, index=False)
        logger.info(f"Forecasts saved to {output_file}")

    def run(self):
        """Execute complete forecasting pipeline."""
        self.run_forecasts()
        self.save_forecasts()
        self.create_forecast_report()


if __name__ == "__main__":
    forecaster = PriceForecastEngine()
    forecaster.run()
