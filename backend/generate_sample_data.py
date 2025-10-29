import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_business_data(days=365):
    """
    Generate realistic business analytics data for the past year
    Includes: sales, revenue, customers, churn, orders
    """
    
    # Set seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Generate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Base metrics with growth trend
    base_customers = 1000
    customer_growth = np.linspace(0, 500, days)  # Growing customer base
    
    # Seasonal patterns (weekends lower, holidays higher)
    day_of_week = np.array([d.weekday() for d in dates])
    weekend_effect = np.where((day_of_week == 5) | (day_of_week == 6), 0.7, 1.0)
    
    # Monthly seasonality (end of month spikes)
    day_of_month = np.array([d.day for d in dates])
    month_end_effect = np.where(day_of_month >= 25, 1.3, 1.0)
    
    # Holiday spikes (simplified)
    month = np.array([d.month for d in dates])
    holiday_effect = np.where((month == 11) | (month == 12), 1.4, 1.0)
    
    # Generate CUSTOMERS
    active_customers = (base_customers + customer_growth + 
                       np.random.normal(0, 30, days)).astype(int)
    active_customers = np.maximum(active_customers, 800)  # Floor at 800
    
    # Generate ORDERS (influenced by seasonality)
    base_orders = 50
    orders = (base_orders * weekend_effect * month_end_effect * holiday_effect + 
              np.random.normal(0, 10, days))
    orders = np.maximum(orders.astype(int), 10)  # At least 10 orders/day
    
    # Generate REVENUE per order (avg $75-$125)
    avg_order_value = np.random.uniform(75, 125, days)
    daily_revenue = orders * avg_order_value
    
    # Generate SALES UNITS (items sold)
    items_per_order = np.random.uniform(1.5, 3.5, days)
    sales_units = (orders * items_per_order).astype(int)
    
    # Generate CHURN (2-5% monthly, varies by day)
    daily_churn_rate = np.random.uniform(0.001, 0.003, days)  # 0.1-0.3% daily
    churned_customers = (active_customers * daily_churn_rate).astype(int)
    
    # Generate NEW CUSTOMERS (to sustain growth)
    new_customers = churned_customers + np.random.randint(5, 20, days)
    
    # Calculate CHURN RATE (rolling 30-day)
    churn_rate_monthly = np.zeros(days)
    for i in range(30, days):
        window_churned = churned_customers[i-30:i].sum()
        window_avg_customers = active_customers[i-30:i].mean()
        churn_rate_monthly[i] = (window_churned / window_avg_customers) * 100
    
    # Fill first 30 days with reasonable values
    churn_rate_monthly[:30] = np.linspace(3.0, churn_rate_monthly[30], 30)
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'daily_revenue': daily_revenue.round(2),
        'orders': orders,
        'sales_units': sales_units,
        'active_customers': active_customers,
        'new_customers': new_customers,
        'churned_customers': churned_customers,
        'churn_rate': churn_rate_monthly.round(2),
        'avg_order_value': avg_order_value.round(2),
        'day_of_week': day_of_week,
        'is_weekend': (day_of_week >= 5).astype(int)
    })
    
    return df

def generate_weekly_aggregates(daily_df):
    """Aggregate daily data to weekly"""
    weekly = daily_df.copy()
    weekly['week'] = weekly['date'].dt.to_period('W').dt.start_time
    
    weekly_agg = weekly.groupby('week').agg({
        'daily_revenue': 'sum',
        'orders': 'sum',
        'sales_units': 'sum',
        'active_customers': 'mean',
        'new_customers': 'sum',
        'churned_customers': 'sum',
        'avg_order_value': 'mean'
    }).reset_index()
    
    weekly_agg.columns = ['week', 'weekly_revenue', 'orders', 'sales_units', 
                          'avg_customers', 'new_customers', 'churned_customers', 
                          'avg_order_value']
    
    # Calculate weekly churn rate
    weekly_agg['churn_rate'] = (
        (weekly_agg['churned_customers'] / weekly_agg['avg_customers']) * 100
    ).round(2)
    
    return weekly_agg

def print_summary_stats(df):
    """Print summary statistics"""
    print("\n" + "="*60)
    print("📊 BUSINESS ANALYTICS DATA SUMMARY")
    print("="*60)
    print(f"\n📅 Date Range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"📈 Total Days: {len(df)}")
    
    print("\n💰 REVENUE METRICS:")
    print(f"   Total Revenue: ${df['daily_revenue'].sum():,.2f}")
    print(f"   Average Daily Revenue: ${df['daily_revenue'].mean():,.2f}")
    print(f"   Min Daily Revenue: ${df['daily_revenue'].min():,.2f}")
    print(f"   Max Daily Revenue: ${df['daily_revenue'].max():,.2f}")
    
    print("\n🛒 ORDER METRICS:")
    print(f"   Total Orders: {df['orders'].sum():,}")
    print(f"   Average Daily Orders: {df['orders'].mean():.0f}")
    print(f"   Average Order Value: ${df['avg_order_value'].mean():.2f}")
    
    print("\n👥 CUSTOMER METRICS:")
    print(f"   Starting Customers: {df['active_customers'].iloc[0]:,}")
    print(f"   Ending Customers: {df['active_customers'].iloc[-1]:,}")
    print(f"   Total New Customers: {df['new_customers'].sum():,}")
    print(f"   Total Churned: {df['churned_customers'].sum():,}")
    print(f"   Average Churn Rate: {df['churn_rate'].mean():.2f}%")
    
    print("\n📦 SALES UNITS:")
    print(f"   Total Units Sold: {df['sales_units'].sum():,}")
    print(f"   Average Daily Units: {df['sales_units'].mean():.0f}")
    
    print("\n" + "="*60)

# Generate the data
if __name__ == "__main__":
    print("🔄 Generating sample business data...")
    
    # Generate daily data
    daily_data = generate_business_data(days=365)
    
    # Generate weekly aggregates
    weekly_data = generate_weekly_aggregates(daily_data)
    
    # Save to CSV
    daily_data.to_csv('app/data/daily_metrics.csv', index=False)
    weekly_data.to_csv('app/data/weekly_metrics.csv', index=False)
    
    print("✅ Data generated successfully!")
    print(f"📁 Saved to: app/data/daily_metrics.csv")
    print(f"📁 Saved to: app/data/weekly_metrics.csv")
    
    # Print summary
    print_summary_stats(daily_data)
    
    print("\n🎯 Next Steps:")
    print("   1. Run: python app/main.py")
    print("   2. Open: http://localhost:8000/docs")
    print("   3. Test the API endpoints")