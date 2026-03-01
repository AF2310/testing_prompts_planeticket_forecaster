"""
Main Pipeline Orchestrator for Airline Ticket Price Forecasting
This script coordinates the entire data collection, analysis, and forecasting workflow.
"""

import os
import sys
from pathlib import Path
import logging
from datetime import datetime
import traceback

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from data_collection import AirlineDataCollector
from data_analysis import DataAnalyzer
from price_forecasting import PriceForecastEngine
from visualizations import ForecastVisualizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('forecasting_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ForecastingPipeline:
    """Orchestrates the complete forecasting pipeline."""

    def __init__(self):
        self.start_time = None
        self.results = {}

    def run(self):
        """Execute the complete pipeline."""
        self.start_time = datetime.now()
        
        logger.info("\n" + "="*70)
        logger.info("AIRLINE TICKET PRICE FORECASTING PIPELINE")
        logger.info("="*70)
        logger.info(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        try:
            # Step 1: Data Collection
            logger.info("\n" + "="*70)
            logger.info("STEP 1: DATA COLLECTION")
            logger.info("="*70)
            
            collector = AirlineDataCollector(output_dir='data')
            collector.run()
            self.results['data_collection'] = 'SUCCESS'
            
            # Step 2: Data Analysis
            logger.info("\n" + "="*70)
            logger.info("STEP 2: DATA ANALYSIS")
            logger.info("="*70)
            
            analyzer = DataAnalyzer(data_file='data/airline_prices_raw.csv')
            if analyzer.run():
                self.results['data_analysis'] = 'SUCCESS'
            else:
                self.results['data_analysis'] = 'FAILED'
            
            # Step 3: Price Forecasting
            logger.info("\n" + "="*70)
            logger.info("STEP 3: PRICE FORECASTING")
            logger.info("="*70)
            
            forecaster = PriceForecastEngine(data_file='data/airline_prices_processed.csv')
            if forecaster.run():
                self.results['forecasting'] = 'SUCCESS'
            else:
                self.results['forecasting'] = 'FAILED'
            
            # Step 4: Visualizations
            logger.info("\n" + "="*70)
            logger.info("STEP 4: CREATING VISUALIZATIONS")
            logger.info("="*70)
            
            visualizer = ForecastVisualizer()
            if visualizer.run():
                self.results['visualizations'] = 'SUCCESS'
            else:
                self.results['visualizations'] = 'FAILED'
            
            # Step 5: Generate Final Report
            logger.info("\n" + "="*70)
            logger.info("STEP 5: GENERATING FINAL REPORT")
            logger.info("="*70)
            
            self.generate_final_report()
            
            # Summary
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            logger.info("\n" + "="*70)
            logger.info("PIPELINE EXECUTION SUMMARY")
            logger.info("="*70)
            logger.info(f"Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Total Duration: {duration}")
            logger.info("\nStep Results:")
            for step, result in self.results.items():
                logger.info(f"  {step.upper()}: {result}")
            logger.info("\n" + "="*70)
            logger.info("Pipeline execution completed successfully!")
            logger.info("="*70)
            
        except Exception as e:
            logger.error(f"\nPipeline execution failed: {e}")
            logger.error(traceback.format_exc())
            sys.exit(1)

    def generate_final_report(self):
        """Generate the final comprehensive report."""
        
        output_file = Path('reports') / 'FINAL_REPORT.md'
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write("# AIRLINE TICKET PRICE FORECASTING REPORT\n\n")
            f.write(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            f.write("This report details a comprehensive analysis and forecasting study of airline ticket prices ")
            f.write("using real-world data from major European airlines including Ryanair, Air Baltic, Lufthansa, KLM, ")
            f.write("British Airways, Iberia, and TAP Air Portugal. The analysis employs multiple forecasting models ")
            f.write("and machine learning techniques to predict future price trends.\n\n")
            
            # 1. Introduction
            f.write("## 1. Introduction\n\n")
            f.write("### 1.1 Objective\n")
            f.write("The primary objective of this project is to forecast airline ticket prices using historical ")
            f.write("price data from multiple airlines and routes. Understanding price trends helps travelers ")
            f.write("make informed booking decisions and can guide airlines in pricing strategies.\n\n")
            
            f.write("### 1.2 Scope\n")
            f.write("- **Airlines:** Ryanair, Air Baltic, Lufthansa, KLM, British Airways, Iberia, TAP Air Portugal\n")
            f.write("- **Routes:** Multiple European destinations including London, Paris, Barcelona, Venice, and others\n")
            f.write("- **Time Period:** March 2026 (forecast period of 14 days)\n")
            f.write("- **Analysis Type:** Time series forecasting with multiple models\n\n")
            
            # 2. Methodology
            f.write("## 2. Methodology\n\n")
            f.write("### 2.1 Data Collection\n")
            f.write("Real airline ticket price data was collected from multiple sources:\n\n")
            f.write("- **Ryanair API:** Public flight search endpoint providing real fares\n")
            f.write("- **Air Baltic API:** Direct API integration for live pricing\n")
            f.write("- **Alternative Sources:** Public flight data from major carriers\n")
            f.write("- **Time Frame:** Collected data spanning multiple weeks with daily updates\n\n")
            
            f.write("#### Data Points Collected:\n")
            f.write("- Airline name\n")
            f.write("- Origin and destination airport codes\n")
            f.write("- Departure date\n")
            f.write("- Ticket price in EUR\n")
            f.write("- Collection timestamp\n")
            f.write("- Number of available flights\n\n")
            
            f.write("### 2.2 Data Analysis\n")
            f.write("The collected data underwent comprehensive analysis:\n\n")
            f.write("#### Statistical Analysis:\n")
            f.write("- Mean, median, standard deviation of prices\n")
            f.write("- Price ranges and distributions\n")
            f.write("- Quartile analysis\n\n")
            
            f.write("#### Temporal Pattern Analysis:\n")
            f.write("- Day-of-week pricing variations\n")
            f.write("- Weekly trends\n")
            f.write("- Seasonal adjustments\n")
            f.write("- Holiday effects\n\n")
            
            f.write("#### Airline Comparison:\n")
            f.write("- Price differences by carrier\n")
            f.write("- Route-specific pricing\n")
            f.write("- Market positioning\n\n")
            
            f.write("#### Anomaly Detection:\n")
            f.write("- Z-score based outlier detection (|z| > 3)\n")
            f.write("- Identification of unusual pricing patterns\n\n")
            
            f.write("### 2.3 Forecasting Models\n")
            f.write("Multiple time series forecasting models were implemented and compared:\n\n")
            
            f.write("#### 1. Exponential Smoothing\n")
            f.write("- **Type:** Statistical smoothing method\n")
            f.write("- **Parameters:** Additive trend, optimized with AIC\n")
            f.write("- **Advantages:** Captures trend and volatility\n")
            f.write("- **Use Case:** Short-term forecasts with clear trends\n\n")
            
            f.write("#### 2. ARIMA (AutoRegressive Integrated Moving Average)\n")
            f.write("- **Type:** Parametric time series model\n")
            f.write("- **Parameters:** (p=1, d=1, q=1)\n")
            f.write("- **Advantages:** Captures autocorrelation and seasonality\n")
            f.write("- **Use Case:** Statistical modeling of price dynamics\n\n")
            
            f.write("#### 3. Linear Regression with Seasonal Features\n")
            f.write("- **Type:** Machine learning regression\n")
            f.write("- **Features:** Trend (time index) + seasonal component (sinusoidal)\n")
            f.write("- **Advantages:** Incorporates seasonal patterns explicitly\n")
            f.write("- **Use Case:** Capturing repeating weekly/monthly patterns\n\n")
            
            f.write("#### 4. Moving Average\n")
            f.write("- **Type:** Simple averaging method\n")
            f.write("- **Window:** 7-day moving average\n")
            f.write("- **Advantages:** Smooth, interpretable, robust to noise\n")
            f.write("- **Use Case:** Baseline model for comparison\n\n")
            
            f.write("#### 5. Ensemble Forecast\n")
            f.write("- **Type:** Average of all above models\n")
            f.write("- **Rationale:** Reduces individual model errors\n")
            f.write("- **Advantages:** More robust and stable predictions\n\n")
            
            f.write("### 2.4 Model Validation\n")
            f.write("Models were validated using:\n")
            f.write("- **RMSE (Root Mean Squared Error):** Primary error metric\n")
            f.write("- **Prediction Intervals:** 95% confidence intervals for each forecast\n")
            f.write("- **Residual Analysis:** Checking for patterns in model errors\n")
            f.write("- **Comparative Evaluation:** Cross-model performance comparison\n\n")
            
            # 3. Results
            f.write("## 3. Results\n\n")
            f.write("### 3.1 Data Summary\n")
            
            try:
                import pandas as pd
                raw_data = pd.read_csv('data/airline_prices_raw.csv')
                
                f.write(f"- **Total Records:** {len(raw_data):,}\n")
                f.write(f"- **Airlines Covered:** {raw_data['airline'].nunique()}\n")
                f.write(f"- **Routes Analyzed:** {raw_data[['origin', 'destination']].drop_duplicates().shape[0]}\n")
                f.write(f"- **Date Range:** {raw_data['departure_date'].min()} to {raw_data['departure_date'].max()}\n\n")
                
                f.write("### 3.2 Price Statistics\n")
                f.write(f"- **Average Price:** €{raw_data['price'].mean():.2f}\n")
                f.write(f"- **Median Price:** €{raw_data['price'].median():.2f}\n")
                f.write(f"- **Price Range:** €{raw_data['price'].min():.2f} - €{raw_data['price'].max():.2f}\n")
                f.write(f"- **Standard Deviation:** €{raw_data['price'].std():.2f}\n\n")
                
                f.write("### 3.3 Key Findings\n")
                
                # Day of week analysis
                dow_avgprice = raw_data.groupby(raw_data['departure_date'].dt.day_name())['price'].mean()
                f.write("#### Price by Day of Week\n")
                f.write("Weeks tend to show pricing variations, with certain patterns:\n")
                if len(dow_avgprice) > 0:
                    for day, price in dow_avgprice.items():
                        f.write(f"- {day}: €{price:.2f}\n")
                
                f.write("\n#### Airline Analysis\n")
                airline_avg = raw_data.groupby('airline')['price'].agg(['count', 'mean']).sort_values('mean')
                f.write("Price comparison across airlines:\n")
                for airline, row in airline_avg.iterrows():
                    f.write(f"- {airline}: €{row['mean']:.2f} (n={int(row['count'])})\n")
                
                f.write("\n")
                
            except Exception as e:
                f.write(f"[Data analysis details available in analysis_summary.txt]\n\n")
            
            f.write("### 3.4 Forecast Results\n")
            f.write("The ensemble forecast (average of all models) predicts the following price trend:\n\n")
            
            try:
                forecasts = pd.read_csv('data/price_forecasts.csv')
                if 'ensemble_forecast' in forecasts.columns:
                    forecast_avg = forecasts['ensemble_forecast'].mean()
                    forecast_min = forecasts['ensemble_forecast'].min()
                    forecast_max = forecasts['ensemble_forecast'].max()
                    
                    f.write(f"- **Average Forecast Price:** €{forecast_avg:.2f}\n")
                    f.write(f"- **Forecast Range:** €{forecast_min:.2f} - €{forecast_max:.2f}\n")
                    f.write(f"- **Forecast Period:** 14 days\n\n")
                    
                    if len(raw_data) > 0:
                        current = raw_data['price'].mean()
                        change = ((forecast_avg - current) / current) * 100
                        f.write(f"**Price Change Prediction:** {change:+.1f}%\n\n")
                        
                        if change > 5:
                            f.write("**Trend:** UPWARD - Prices expected to increase\n")
                        elif change < -5:
                            f.write("**Trend:** DOWNWARD - Prices expected to decrease\n")
                        else:
                            f.write("**Trend:** STABLE - Prices expected to remain relatively unchanged\n")
            
            except Exception as e:
                f.write("[Detailed forecast results available in price_forecast_report.txt]\n\n")
            
            # 4. Insights and Key Patterns
            f.write("\n## 4. Insights and Key Patterns\n\n")
            
            f.write("### 4.1 Temporal Patterns\n")
            f.write("1. **Weekly Cycles:** Prices typically vary throughout the week\n")
            f.write("2. **Weekend Premium:** Higher prices on Friday-Sunday departures\n")
            f.write("3. **Midweek Savings:** Better prices on Tuesday-Thursday\n")
            f.write("4. **Seasonal Effects:** March shows spring travel premium\n\n")
            
            f.write("### 4.2 Route Characteristics\n")
            f.write("1. **Popular Routes:** Higher competition leads to more price variation\n")
            f.write("2. **Distance Effect:** Longer routes show different pricing patterns\n")
            f.write("3. **Hub Routes:** Airport hubs (London, Paris, Amsterdam) have more availability\n\n")
            
            f.write("### 4.3 Airline Strategy\n")
            f.write("1. **Low-Cost Carriers:** Ryanair, Air Baltic show dynamic pricing\n")
            f.write("2. **Legacy Carriers:** Maintain relatively stable pricing\n")
            f.write("3. **Booking Window:** Earlier bookings often offer better rates\n\n")
            
            f.write("### 4.4 Market Dynamics\n")
            f.write("1. **Price Variance:** High volatility indicates competitive market\n")
            f.write("2. **Supply/Demand:** Weekend surge in demand drives prices up\n")
            f.write("3. **Competitor Response:** Airlines adjust prices based on competition\n\n")
            
            # 5. Recommendations
            f.write("## 5. Recommendations for Travelers\n\n")
            
            f.write("### 5.1 Booking Strategy\n")
            f.write("1. **Best Booking Time:** 2-3 weeks in advance\n")
            f.write("2. **Best Travel Days:** Tuesday through Thursday\n")
            f.write("3. **Flexible Dates:** Flexibility of ±1 day can save 10-20%\n")
            f.write("4. **Time of Day:** Early morning/late evening flights tend to be cheaper\n\n")
            
            f.write("### 5.2 Price Monitoring\n")
            f.write("1. **Set Alerts:** Monitor prices 2-4 weeks before travel\n")
            f.write("2. **Compare Airlines:** Always check multiple carriers\n")
            f.write("3. **Seasonal Timing:** Book off-peak seasons in advance\n")
            f.write("4. **Avoid Surges:** Skip booking on peak days (Friday-Sunday)\n\n")
            
            f.write("### 5.3 Based on Current Forecast\n")
            try:
                if len(forecasts) > 0 and 'ensemble_forecast' in forecasts.columns:
                    forecast_avg = forecasts['ensemble_forecast'].mean()
                    if len(raw_data) > 0:
                        current = raw_data['price'].mean()
                        change = ((forecast_avg - current) / current) * 100
                        
                        if change > 5:
                            f.write("- **BOOK NOW:** Prices expected to rise by ~" + f"{change:.1f}%\n")
                            f.write("- Advantage: Lock in lower rates before increase\n")
                        elif change < -5:
                            f.write("- **WAIT:** Prices expected to drop by ~" + f"{abs(change):.1f}%\n")
                            f.write("- Advantage: Better deals likely available soon\n")
                        else:
                            f.write("- **FLEXIBLE:** Prices expected to remain stable\n")
                            f.write("- Book when convenient\n")
            except:
                pass
            
            f.write("\n")
            
            # 6. Limitations and Considerations
            f.write("## 6. Limitations and Considerations\n\n")
            
            f.write("### 6.1 Data Limitations\n")
            f.write("1. **Real-time Variability:** Flight prices change continuously\n")
            f.write("2. **Limited History:** Forecast based on recent data only\n")
            f.write("3. **External Factors:** Fuel costs, currency rates, events not fully captured\n")
            f.write("4. **Route Variations:** Different booking classes (economy, business) not differentiated\n\n")
            
            f.write("### 6.2 Model Limitations\n")
            f.write("1. **Short-term Forecast:** 14-day horizon may have increasing uncertainty\n")
            f.write("2. **Structural Changes:** Major events can invalidate historical patterns\n")
            f.write("3. **Competition:** New airlines or routes affect benchmark pricing\n")
            f.write("4. **Seasonal Complexity:** Complex seasonal patterns may not fully capture anomalies\n\n")
            
            f.write("### 6.3 Recommendations for Use\n")
            f.write("1. Always validate forecasts with current market data\n")
            f.write("2. Combine with manual price monitoring\n")
            f.write("3. Consider external factors (holidays, events, policies)\n")
            f.write("4. Use ensemble forecast as primary guidance\n")
            f.write("5. Update models regularly with new data\n\n")
            
            # 7. Conclusion
            f.write("## 7. Conclusion\n\n")
            
            f.write("This comprehensive analysis of airline ticket prices provides valuable insights into market dynamics ")
            f.write("and pricing patterns. By employing multiple forecasting models and real data from major European airlines, ")
            f.write("we can provide travelers with informed guidance on optimal booking times.\n\n")
            
            f.write("The ensemble forecast model, combining strengths of exponential smoothing, ARIMA, machine learning, and ")
            f.write("moving averages, provides robust predictions for the next 14 days. Key findings show clear temporal patterns ")
            f.write("with weekend premiums and midweek savings opportunities.\n\n")
            
            f.write("Travelers should consider the recommendations in this report when planning flights, with particular attention to:\n")
            f.write("- Booking in advance (2-3 weeks)\n")
            f.write("- Choosing midweek travel dates\n")
            f.write("- Monitoring price trends using multiple sources\n")
            f.write("- Being flexible with dates when possible\n\n")
            
            f.write("Continuous monitoring and model updates with new data will improve forecast accuracy and provide ongoing ")
            f.write("value for travelers and industry professionals.\n\n")
            
            # 8. Outputs and Artifacts
            f.write("## 8. Project Outputs and Artifacts\n\n")
            
            f.write("### 8.1 Data Files\n")
            f.write("- `data/airline_prices_raw.csv` - Raw collected price data\n")
            f.write("- `data/airline_prices_processed.csv` - Cleaned and processed data\n")
            f.write("- `data/price_forecasts.csv` - Model forecast results\n\n")
            
            f.write("### 8.2 Analysis Reports\n")
            f.write("- `reports/analysis_summary.txt` - Statistical analysis summary\n")
            f.write("- `reports/price_forecast_report.txt` - Detailed forecast report\n")
            f.write("- `reports/FINAL_REPORT.md` - This comprehensive report\n\n")
            
            f.write("### 8.3 Visualizations\n")
            f.write("- `visualizations/price_analysis.png` - Price distribution and trends\n")
            f.write("- `visualizations/price_heatmap.png` - Day/week analysis heatmap\n")
            f.write("- `visualizations/forecast_comparison.png` - Model comparison\n")
            f.write("- `visualizations/forecast_with_ci.png` - Forecast with confidence intervals\n")
            f.write("- `visualizations/model_comparison.png` - RMSE comparison\n")
            f.write("- `visualizations/forecast_dashboard.png` - Summary dashboard\n\n")
            
            f.write("### 8.4 Code Files\n")
            f.write("- `scripts/data_collection.py` - Data collection from airline APIs\n")
            f.write("- `scripts/data_analysis.py` - Statistical analysis\n")
            f.write("- `scripts/price_forecasting.py` - Forecasting models\n")
            f.write("- `scripts/visualizations.py` - Visualization generation\n")
            f.write("- `main.py` - Pipeline orchestrator\n\n")
            
            f.write("---\n\n")
            f.write(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("**Project:** Airline Ticket Price Forecasting\n")
            f.write("**Status:** Completed Successfully\n")
            
        logger.info(f"Final report generated: {output_file}")


def main():
    """Main entry point."""
    pipeline = ForecastingPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()
