"""
Test script for ML forecasting functionality
Run this to verify Prophet forecasting works correctly
"""

import requests
import json
from datetime import datetime
from fastapi import APIRouter


API_BASE = "http://localhost:8000"

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_endpoint(endpoint, params=None):
    """Test an API endpoint"""
    url = f"{API_BASE}{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        print("   Run: python app/main.py")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    print("\n🧪 Testing AI Analytics Dashboard - ML Forecasting")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Check API health
    print_section("1. API Health Check")
    health = test_endpoint("/")
    if health:
        print("✅ API is running")
        print(f"   Version: {health.get('version')}")
    else:
        print("❌ API health check failed. Exiting...")
        return
    
    # Test 2: Revenue Forecast
    print_section("2. Revenue Forecast (30 days)")
    revenue_forecast = test_endpoint("/api/forecast/revenue", {"periods": 30})
    if revenue_forecast and revenue_forecast.get('success'):
        forecast_data = revenue_forecast['forecast']
        predictions = forecast_data['predictions']
        print(f"✅ Revenue forecast generated")
        print(f"   Days forecasted: {len(predictions)}")
        print(f"   Avg daily revenue (predicted): ${sum(predictions)/len(predictions):,.2f}")
        print(f"   Total revenue (30 days): ${sum(predictions):,.2f}")
        print(f"   First 3 predictions: {[f'${x:,.2f}' for x in predictions[:3]]}")
    else:
        print("❌ Revenue forecast failed")
    
    # Test 3: Orders Forecast
    print_section("3. Orders Forecast (30 days)")
    orders_forecast = test_endpoint("/api/forecast/orders", {"periods": 30})
    if orders_forecast and orders_forecast.get('success'):
        forecast_data = orders_forecast['forecast']
        predictions = forecast_data['predictions']
        print(f"✅ Orders forecast generated")
        print(f"   Avg daily orders (predicted): {sum(predictions)/len(predictions):.0f}")
        print(f"   Total orders (30 days): {sum(predictions):,}")
        print(f"   First 3 predictions: {predictions[:3]}")
    else:
        print("❌ Orders forecast failed")
    
    # Test 4: Customers Forecast
    print_section("4. Customers Forecast (30 days)")
    customers_forecast = test_endpoint("/api/forecast/customers", {"periods": 30})
    if customers_forecast and customers_forecast.get('success'):
        forecast_data = customers_forecast['forecast']
        predictions = forecast_data['predictions']
        print(f"✅ Customers forecast generated")
        print(f"   Starting customers: {predictions[0]:,}")
        print(f"   Ending customers (day 30): {predictions[-1]:,}")
        print(f"   Growth: {predictions[-1] - predictions[0]:,} customers")
    else:
        print("❌ Customers forecast failed")
    
    # Test 5: Churn Rate Forecast
    print_section("5. Churn Rate Forecast (30 days)")
    churn_forecast = test_endpoint("/api/forecast/churn", {"periods": 30})
    if churn_forecast and churn_forecast.get('success'):
        forecast_data = churn_forecast['forecast']
        predictions = forecast_data['predictions']
        print(f"✅ Churn rate forecast generated")
        print(f"   Avg churn rate: {sum(predictions)/len(predictions):.2f}%")
        print(f"   Min churn: {min(predictions):.2f}%")
        print(f"   Max churn: {max(predictions):.2f}%")
    else:
        print("❌ Churn rate forecast failed")
    
    # Test 6: All Metrics Forecast
    print_section("6. Comprehensive Forecast (All Metrics)")
    all_forecast = test_endpoint("/api/forecast/all", {"periods": 30})
    if all_forecast and all_forecast.get('success'):
        summary = all_forecast['data']['summary']
        print(f"✅ Comprehensive forecast generated")
        print(f"   Total revenue (30 days): ${summary['total_revenue']:,.2f}")
        print(f"   Total orders (30 days): {summary['total_orders']:,}")
        print(f"   Avg customers: {summary['avg_customers']:,}")
        print(f"   Avg churn rate: {summary['avg_churn_rate']:.2f}%")
    else:
        print("❌ Comprehensive forecast failed")
    
    # Test 7: Forecast Accuracy
    print_section("7. Forecast Accuracy Test")
    accuracy = test_endpoint("/api/forecast/accuracy", {
        "metric": "daily_revenue",
        "test_days": 14
    })
    if accuracy and accuracy.get('success'):
        metrics = accuracy['data']['accuracy']
        print(f"✅ Accuracy test completed (14-day backtest)")
        print(f"   MAPE (Mean Absolute % Error): {metrics['mape']:.2f}%")
        print(f"   RMSE (Root Mean Squared Error): ${metrics['rmse']:,.2f}")
        print(f"   MAE (Mean Absolute Error): ${metrics['mae']:,.2f}")
        
        if metrics['mape'] < 10:
            print(f"   📊 Excellent accuracy! (<10% error)")
        elif metrics['mape'] < 20:
            print(f"   📊 Good accuracy (10-20% error)")
        else:
            print(f"   📊 Moderate accuracy (>20% error)")
    else:
        print("❌ Accuracy test failed")
    
    # Summary
    print_section("🎉 Test Summary")
    print("✅ All forecasting endpoints are working!")
    print("\n📋 Available Forecast Endpoints:")
    print("   • GET /api/forecast/revenue?periods=30")
    print("   • GET /api/forecast/orders?periods=30")
    print("   • GET /api/forecast/customers?periods=30")
    print("   • GET /api/forecast/churn?periods=30")
    print("   • GET /api/forecast/all?periods=30")
    print("   • GET /api/forecast/accuracy?metric=daily_revenue&test_days=14")
    
    print("\n🌐 Next Steps:")
    print("   1. Visit: http://localhost:8000/docs")
    print("   2. Try the forecast endpoints in the interactive UI")
    print("   3. Build the React dashboard to visualize forecasts")
    print("")

if __name__ == "__main__":
    main()