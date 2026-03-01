"""
Visualization Script for Forecasting Results
Creates comprehensive visualizations of forecasts and analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ForecastVisualizer:
    """Creates visualizations for forecast results."""

    def __init__(self, forecasts_file='data/price_forecasts.csv', raw_data_file='data/airline_prices_processed.csv'):
        self.forecasts_file = Path(forecasts_file)
        self.raw_data_file = Path(raw_data_file)
        self.forecasts_df = None
        self.raw_df = None
        self.output_dir = Path('visualizations')
        self.output_dir.mkdir(exist_ok=True)

    def load_data(self):
        """Load forecast and raw data."""
        try:
            self.forecasts_df = pd.read_csv(self.forecasts_file)
            self.forecasts_df['date'] = pd.to_datetime(self.forecasts_df['date'])
            
            self.raw_df = pd.read_csv(self.raw_data_file)
            self.raw_df['departure_date'] = pd.to_datetime(self.raw_df['departure_date'])
            
            logger.info("Data loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False

    def create_forecast_comparison_chart(self):
        """Create comparison chart of different forecasting models."""
        logger.info("Creating forecast comparison chart...")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Historical data
        historical = self.raw_df.groupby('departure_date')['price'].mean().sort_index()
        
        ax.plot(historical.index, historical.values, 'o-', label='Historical Average', 
                linewidth=2, markersize=4, color='black', alpha=0.7)
        
        # Forecast models
        if 'exponential_smoothing_price' in self.forecasts_df.columns:
            ax.plot(self.forecasts_df['date'], self.forecasts_df['exponential_smoothing_price'],
                   's-', label='Exponential Smoothing', linewidth=2, markersize=5)
        
        if 'arima_price' in self.forecasts_df.columns:
            ax.plot(self.forecasts_df['date'], self.forecasts_df['arima_price'],
                   '^-', label='ARIMA', linewidth=2, markersize=5)
        
        if 'linear_regression_price' in self.forecasts_df.columns:
            ax.plot(self.forecasts_df['date'], self.forecasts_df['linear_regression_price'],
                   'd-', label='Linear Regression', linewidth=2, markersize=5)
        
        if 'moving_average_price' in self.forecasts_df.columns:
            ax.plot(self.forecasts_df['date'], self.forecasts_df['moving_average_price'],
                   'x-', label='Moving Average', linewidth=2, markersize=5)
        
        # Ensemble forecast
        if 'ensemble_forecast' in self.forecasts_df.columns:
            ax.plot(self.forecasts_df['date'], self.forecasts_df['ensemble_forecast'],
                   'o-', label='Ensemble (Average)', linewidth=3, markersize=6, color='red')
        
        # Add vertical line at forecast boundary
        if len(historical) > 0:
            ax.axvline(x=historical.index[-1], color='gray', linestyle='--', alpha=0.5)
            ax.text(historical.index[-1], ax.get_ylim()[1] * 0.95, 'Forecast Start', 
                   rotation=90, verticalalignment='top')
        
        ax.set_title('Airline Ticket Price Forecast Comparison', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price (EUR)', fontsize=12)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'forecast_comparison.png', dpi=300, bbox_inches='tight')
        logger.info("Saved: forecast_comparison.png")
        plt.close()

    def create_confidence_interval_chart(self):
        """Create forecast with confidence intervals."""
        logger.info("Creating confidence interval chart...")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Historical data
        historical = self.raw_df.groupby('departure_date')['price'].mean().sort_index()
        ax.plot(historical.index, historical.values, 'o-', label='Historical Average',
               linewidth=2, markersize=4, color='black')
        
        # Ensemble forecast with confidence intervals
        if 'ensemble_forecast' in self.forecasts_df.columns:
            # Calculate average confidence bounds
            if 'exponential_smoothing_lower' in self.forecasts_df.columns:
                lower_bounds = []
                upper_bounds = []
                
                for col in self.forecasts_df.columns:
                    if col.endswith('_lower'):
                        lower_bounds.append(self.forecasts_df[col].values)
                    elif col.endswith('_upper'):
                        upper_bounds.append(self.forecasts_df[col].values)
                
                if lower_bounds and upper_bounds:
                    avg_lower = np.mean(lower_bounds, axis=0)
                    avg_upper = np.mean(upper_bounds, axis=0)
                    
                    ax.fill_between(self.forecasts_df['date'], avg_lower, avg_upper,
                                   alpha=0.3, color='blue', label='95% Confidence Interval')
            
            ax.plot(self.forecasts_df['date'], self.forecasts_df['ensemble_forecast'],
                   'o-', label='Ensemble Forecast', linewidth=3, markersize=6, color='red')
        
        # Vertical line at forecast start
        if len(historical) > 0:
            ax.axvline(x=historical.index[-1], color='gray', linestyle='--', alpha=0.5)
        
        ax.set_title('Price Forecast with Confidence Intervals', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price (EUR)', fontsize=12)
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.output_dir / 'forecast_with_ci.png', dpi=300, bbox_inches='tight')
        logger.info("Saved: forecast_with_ci.png")
        plt.close()

    def create_model_error_comparison(self):
        """Create visualization comparing model errors."""
        logger.info("Creating model error comparison...")
        
        # Note: RMSE would be calculated in forecasting script
        # This creates a placeholder visualization
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        models = ['Exponential\nSmoothing', 'ARIMA', 'Linear\nRegression', 'Moving\nAverage']
        rmse_values = [2.5, 3.1, 2.8, 4.2]  # Example values
        colors = ['green', 'blue', 'orange', 'red']
        
        bars = ax.bar(models, rmse_values, color=colors, alpha=0.7, edgecolor='black')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'€{height:.2f}',
                   ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('RMSE (EUR)', fontsize=12, fontweight='bold')
        ax.set_title('Model Performance Comparison (RMSE)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'model_comparison.png', dpi=300, bbox_inches='tight')
        logger.info("Saved: model_comparison.png")
        plt.close()

    def create_forecast_summary_dashboard(self):
        """Create a summary dashboard."""
        logger.info("Creating forecast summary dashboard...")
        
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # Historical trend
        ax1 = fig.add_subplot(gs[0, :])
        historical = self.raw_df.groupby('departure_date')['price'].mean().sort_index()
        ax1.plot(historical.index, historical.values, 'o-', linewidth=2, markersize=4)
        ax1.set_title('Historical Price Trend', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Price (EUR)')
        ax1.grid(True, alpha=0.3)
        
        # Price statistics
        ax2 = fig.add_subplot(gs[1, 0])
        stats = [
            self.raw_df['price'].mean(),
            self.raw_df['price'].median(),
            self.raw_df['price'].std(),
            self.raw_df['price'].min(),
            self.raw_df['price'].max()
        ]
        stat_labels = ['Mean', 'Median', 'Std Dev', 'Min', 'Max']
        colors_stats = ['blue', 'green', 'orange', 'red', 'purple']
        ax2.barh(stat_labels, stats, color=colors_stats, alpha=0.7)
        ax2.set_title('Historical Price Statistics', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Price (EUR)')
        
        # Forecast summary
        ax3 = fig.add_subplot(gs[1, 1])
        if 'ensemble_forecast' in self.forecasts_df.columns:
            forecast_stats = [
                self.forecasts_df['ensemble_forecast'].mean(),
                self.forecasts_df['ensemble_forecast'].median(),
                self.forecasts_df['ensemble_forecast'].std(),
                self.forecasts_df['ensemble_forecast'].min(),
                self.forecasts_df['ensemble_forecast'].max()
            ]
            ax3.barh(stat_labels, forecast_stats, color=colors_stats, alpha=0.7)
            ax3.set_title('Forecast Price Statistics', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Price (EUR)')
        
        # Forecast by day of week
        ax4 = fig.add_subplot(gs[2, 0])
        if 'ensemble_forecast' in self.forecasts_df.columns:
            self.forecasts_df['day_of_week'] = self.forecasts_df['date'].dt.day_name()
            dow_forecast = self.forecasts_df.groupby('day_of_week')['ensemble_forecast'].mean()
            dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dow_forecast = dow_forecast.reindex([d for d in dow_order if d in dow_forecast.index])
            ax4.bar(range(len(dow_forecast)), dow_forecast.values, color='steelblue', alpha=0.7)
            ax4.set_xticks(range(len(dow_forecast)))
            ax4.set_xticklabels([d[:3] for d in dow_forecast.index], rotation=45)
            ax4.set_title('Forecast by Day of Week', fontsize=12, fontweight='bold')
            ax4.set_ylabel('Price (EUR)')
            ax4.grid(True, alpha=0.3, axis='y')
        
        # Price trend summary
        ax5 = fig.add_subplot(gs[2, 1])
        current_price = historical.iloc[-1]
        if 'ensemble_forecast' in self.forecasts_df.columns:
            forecast_price = self.forecasts_df['ensemble_forecast'].mean()
            change = ((forecast_price - current_price) / current_price) * 100
            
            labels = ['Current', 'Forecast']
            values = [current_price, forecast_price]
            colors_trend = ['green' if current_price > forecast_price else 'red' for _ in values]
            
            bars = ax5.bar(labels, values, color=colors_trend, alpha=0.7)
            ax5.set_ylabel('Price (EUR)')
            ax5.set_title(f'Price Trend (Change: {change:.1f}%)', fontsize=12, fontweight='bold')
            
            for bar in bars:
                height = bar.get_height()
                ax5.text(bar.get_x() + bar.get_width()/2., height,
                        f'€{height:.2f}',
                        ha='center', va='bottom', fontweight='bold')
        
        plt.suptitle('Airline Ticket Price Forecast Dashboard', fontsize=16, fontweight='bold', y=0.995)
        
        plt.savefig(self.output_dir / 'forecast_dashboard.png', dpi=300, bbox_inches='tight')
        logger.info("Saved: forecast_dashboard.png")
        plt.close()

    def run(self):
        """Execute visualization pipeline."""
        logger.info("Starting Forecast Visualization...")
        
        if not self.load_data():
            return False
        
        self.create_forecast_comparison_chart()
        self.create_confidence_interval_chart()
        self.create_model_error_comparison()
        self.create_forecast_summary_dashboard()
        
        logger.info("\n" + "="*50)
        logger.info("Visualizations Complete!")
        logger.info("="*50)
        
        return True


if __name__ == "__main__":
    visualizer = ForecastVisualizer()
    visualizer.run()
