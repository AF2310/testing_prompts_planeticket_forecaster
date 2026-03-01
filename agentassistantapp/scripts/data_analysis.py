"""
Data Analysis and Preprocessing Script
Analyzes airline ticket price data and prepares it for forecasting.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataAnalyzer:
    """Analyzes and preprocesses airline ticket price data."""

    def __init__(self, data_file='data/airline_prices_raw.csv'):
        self.data_file = Path(data_file)
        self.df = None
        self.analysis_results = {}

    def load_data(self):
        """Load raw data from CSV."""
        try:
            self.df = pd.read_csv(self.data_file)
            self.df['departure_date'] = pd.to_datetime(self.df['departure_date'])
            self.df['collection_date'] = pd.to_datetime(self.df['collection_date'])
            logger.info(f"Loaded {len(self.df)} records")
            logger.info(f"Date range: {self.df['departure_date'].min()} to {self.df['departure_date'].max()}")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return False

    def basic_statistics(self):
        """Calculate basic statistics."""
        logger.info("\n" + "="*50)
        logger.info("BASIC STATISTICS")
        logger.info("="*50)
        
        stats = {
            'total_records': len(self.df),
            'airlines': self.df['airline'].nunique(),
            'routes': self.df[['origin', 'destination']].drop_duplicates().shape[0],
            'price_mean': self.df['price'].mean(),
            'price_median': self.df['price'].median(),
            'price_std': self.df['price'].std(),
            'price_min': self.df['price'].min(),
            'price_max': self.df['price'].max(),
        }
        
        logger.info(f"Total Records: {stats['total_records']}")
        logger.info(f"Airlines: {stats['airlines']}")
        logger.info(f"Routes: {stats['routes']}")
        logger.info(f"\nPrice Statistics (EUR):")
        logger.info(f"  Mean: €{stats['price_mean']:.2f}")
        logger.info(f"  Median: €{stats['price_median']:.2f}")
        logger.info(f"  Std Dev: €{stats['price_std']:.2f}")
        logger.info(f"  Min: €{stats['price_min']:.2f}")
        logger.info(f"  Max: €{stats['price_max']:.2f}")
        
        self.analysis_results['basic_stats'] = stats
        return stats

    def analyze_by_airline(self):
        """Analyze prices by airline."""
        logger.info("\n" + "="*50)
        logger.info("ANALYSIS BY AIRLINE")
        logger.info("="*50)
        
        airline_stats = self.df.groupby('airline')['price'].agg([
            'count', 'mean', 'median', 'std', 'min', 'max'
        ]).round(2)
        
        logger.info("\n" + airline_stats.to_string())
        self.analysis_results['airline_stats'] = airline_stats
        return airline_stats

    def analyze_temporal_patterns(self):
        """Analyze price patterns over time and by day of week."""
        logger.info("\n" + "="*50)
        logger.info("TEMPORAL PATTERNS")
        logger.info("="*50)
        
        self.df['day_of_week'] = self.df['departure_date'].dt.day_name()
        self.df['week_of_year'] = self.df['departure_date'].dt.isocalendar().week
        
        # Day of week analysis
        dow_stats = self.df.groupby('day_of_week')['price'].agg([
            'count', 'mean', 'median', 'std'
        ]).round(2)
        
        logger.info("\nPrice by Day of Week:")
        logger.info(dow_stats.to_string())
        
        # Weekly analysis
        weekly_stats = self.df.groupby('week_of_year')['price'].agg([
            'count', 'mean', 'median'
        ]).round(2)
        
        logger.info("\nPrice by Week of Year:")
        logger.info(weekly_stats.to_string())
        
        self.analysis_results['dow_stats'] = dow_stats
        self.analysis_results['weekly_stats'] = weekly_stats

    def identify_anomalies(self):
        """Identify price anomalies."""
        logger.info("\n" + "="*50)
        logger.info("ANOMALY DETECTION")
        logger.info("="*50)
        
        # Calculate z-scores for outlier detection
        self.df['price_zscore'] = np.abs((self.df['price'] - self.df['price'].mean()) / self.df['price'].std())
        
        anomalies = self.df[self.df['price_zscore'] > 3]
        
        logger.info(f"Found {len(anomalies)} potential anomalies (z-score > 3)")
        
        if len(anomalies) > 0:
            logger.info("\nTop Anomalies:")
            for idx, row in anomalies.head(5).iterrows():
                logger.info(f"  {row['airline']}: {row['origin']}-{row['destination']} "
                           f"on {row['departure_date'].date()} - €{row['price']:.2f} (z-score: {row['price_zscore']:.2f})")
        
        self.analysis_results['anomalies'] = anomalies

    def analyze_routes(self):
        """Analyze top routes and pricing."""
        logger.info("\n" + "="*50)
        logger.info("TOP ROUTES ANALYSIS")
        logger.info("="*50)
        
        route_stats = self.df.groupby(['origin', 'destination', 'airline'])['price'].agg([
            'count', 'mean', 'std', 'min', 'max'
        ]).round(2).sort_values('count', ascending=False).head(10)
        
        logger.info("\nTop 10 Routes by Record Count:")
        logger.info(route_stats.to_string())
        
        self.analysis_results['route_stats'] = route_stats

    def create_visualizations(self):
        """Create analysis visualizations."""
        logger.info("\nCreating visualizations...")
        
        output_dir = Path('visualizations')
        output_dir.mkdir(exist_ok=True)
        
        plt.style.use('seaborn-v0_8-darkgrid')
        
        # 1. Price distribution
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Histogram
        axes[0, 0].hist(self.df['price'], bins=50, color='steelblue', edgecolor='black')
        axes[0, 0].set_title('Price Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel('Price (EUR)')
        axes[0, 0].set_ylabel('Frequency')
        
        # Box plot by airline
        airlines_to_plot = self.df['airline'].value_counts().head(5).index
        self.df[self.df['airline'].isin(airlines_to_plot)].boxplot(
            column='price', by='airline', ax=axes[0, 1]
        )
        axes[0, 1].set_title('Price by Airline (Top 5)', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlabel('Airline')
        axes[0, 1].set_ylabel('Price (EUR)')
        
        # Time series
        daily_avg = self.df.groupby('departure_date')['price'].mean()
        axes[1, 0].plot(daily_avg.index, daily_avg.values, color='green', linewidth=2)
        axes[1, 0].fill_between(daily_avg.index, daily_avg.values, alpha=0.3, color='green')
        axes[1, 0].set_title('Average Daily Price Trend', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel('Date')
        axes[1, 0].set_ylabel('Price (EUR)')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Day of week analysis
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_data = self.df.groupby('day_of_week')['price'].mean().reindex(dow_order)
        colors = ['red' if day in ['Saturday', 'Sunday'] else 'steelblue' for day in dow_order]
        axes[1, 1].bar(range(len(dow_order)), dow_data.values, color=colors)
        axes[1, 1].set_xticks(range(len(dow_order)))
        axes[1, 1].set_xticklabels([d[:3] for d in dow_order], rotation=45)
        axes[1, 1].set_title('Average Price by Day of Week', fontsize=12, fontweight='bold')
        axes[1, 1].set_ylabel('Price (EUR)')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'price_analysis.png', dpi=300, bbox_inches='tight')
        logger.info(f"Saved visualization: price_analysis.png")
        plt.close()
        
        # 2. Heatmap of prices by day of week and week
        fig, ax = plt.subplots(figsize=(14, 8))
        
        pivot_data = self.df.pivot_table(
            values='price', 
            index='day_of_week', 
            columns='week_of_year', 
            aggfunc='mean'
        )
        
        # Reorder rows
        dow_order_short = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_data = pivot_data.reindex([d for d in dow_order_short if d in pivot_data.index])
        
        sns.heatmap(pivot_data, annot=False, fmt='.0f', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Price (EUR)'})
        ax.set_title('Price Heatmap: Day of Week vs Week of Year', fontsize=14, fontweight='bold')
        ax.set_xlabel('Week of Year')
        ax.set_ylabel('Day of Week')
        
        plt.tight_layout()
        plt.savefig(output_dir / 'price_heatmap.png', dpi=300, bbox_inches='tight')
        logger.info(f"Saved visualization: price_heatmap.png")
        plt.close()

    def save_processed_data(self):
        """Save processed data for forecasting."""
        output_file = Path('data') / 'airline_prices_processed.csv'
        self.df.to_csv(output_file, index=False)
        logger.info(f"Processed data saved to {output_file}")

    def generate_summary_report(self):
        """Generate text summary report."""
        output_file = Path('reports') / 'analysis_summary.txt'
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("AIRLINE TICKET PRICE ANALYSIS - SUMMARY REPORT\n")
            f.write("="*70 + "\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("DATA OVERVIEW\n")
            f.write("-"*70 + "\n")
            f.write(f"Total Records: {len(self.df)}\n")
            f.write(f"Airlines: {self.df['airline'].nunique()}\n")
            f.write(f"Routes: {self.df[['origin', 'destination']].drop_duplicates().shape[0]}\n")
            f.write(f"Date Range: {self.df['departure_date'].min().date()} to {self.df['departure_date'].max().date()}\n\n")
            
            f.write("PRICE STATISTICS (EUR)\n")
            f.write("-"*70 + "\n")
            f.write(f"Mean: €{self.df['price'].mean():.2f}\n")
            f.write(f"Median: €{self.df['price'].median():.2f}\n")
            f.write(f"Std Dev: €{self.df['price'].std():.2f}\n")
            f.write(f"Min: €{self.df['price'].min():.2f}\n")
            f.write(f"Max: €{self.df['price'].max():.2f}\n\n")
            
            f.write("KEY FINDINGS\n")
            f.write("-"*70 + "\n")
            f.write("1. Price Distribution:\n")
            f.write(f"   - Most prices range between €{self.df['price'].quantile(0.25):.2f} and €{self.df['price'].quantile(0.75):.2f}\n")
            f.write(f"   - Skewness: {self.df['price'].skew():.3f}\n\n")
            
            f.write("2. Temporal Patterns:\n")
            dow_avg = self.df.groupby('day_of_week')['price'].mean()
            f.write(f"   - Weekend prices are typically higher\n")
            f.write(f"   - Most expensive day: {dow_avg.idxmax()} (€{dow_avg.max():.2f})\n")
            f.write(f"   - Cheapest day: {dow_avg.idxmin()} (€{dow_avg.min():.2f})\n\n")
            
            f.write("3. Airline Comparison:\n")
            airline_avg = self.df.groupby('airline')['price'].mean().sort_values()
            for airline, price in airline_avg.items():
                f.write(f"   - {airline}: €{price:.2f}\n")
            
        logger.info(f"Summary report saved to {output_file}")

    def run(self):
        """Execute analysis pipeline."""
        logger.info("Starting Data Analysis...")
        
        if not self.load_data():
            return False
        
        self.basic_statistics()
        self.analyze_by_airline()
        self.analyze_temporal_patterns()
        self.analyze_routes()
        self.identify_anomalies()
        self.create_visualizations()
        self.save_processed_data()
        self.generate_summary_report()
        
        logger.info("\n" + "="*50)
        logger.info("Analysis Complete!")
        logger.info("="*50)
        
        return True


if __name__ == "__main__":
    analyzer = DataAnalyzer()
    analyzer.run()
