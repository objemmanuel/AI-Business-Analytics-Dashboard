from fastapi import APIRouter
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import os
import sys

# Add services directory to path
sys.path.append(os.path.dirname(__file__))
from services.ml_forecasting import forecaster

app = FastAPI(
    title="AI Analytics Dashboard API",
    description="Business analytics API with ML forecasting",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data at startup
DATA_DIR = "app/data"
daily_df = None
weekly_df = None

@app.on_event("startup")
async def load_data():
    """Load CSV data on startup"""
    global daily_df, weekly_df
    
    daily_path = os.path.join(DATA_DIR, "daily_metrics.csv")
    weekly_path = os.path.join(DATA_DIR, "weekly_metrics.csv")
    
    if os.path.exists(daily_path):
        daily_df = pd.read_csv(daily_path)
        daily_df['date'] = pd.to_datetime(daily_df['date'])
        print(f"✅ Loaded {len(daily_df)} daily records")
    
    if os.path.exists(weekly_path):
        weekly_df = pd.read_csv(weekly_path)
        weekly_df['week'] = pd.to_datetime(weekly_df['week'])
        print(f"✅ Loaded {len(weekly_df)} weekly records")

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "healthy",
        "message": "AI Analytics Dashboard API",
        "version": "1.0.0",
        "endpoints": [
            "/api/metrics/daily",
            "/api/metrics/weekly",
            "/api/metrics/kpis",
            "/docs"
        ]
    }

@app.get("/api/metrics/daily")
async def get_daily_metrics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(30, description="Number of recent days to return")
):
    """
    Get daily metrics (revenue, orders, customers, etc.)
    
    - **start_date**: Filter from this date
    - **end_date**: Filter to this date
    - **limit**: Number of recent days (default: 30)
    """
    if daily_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    df = daily_df.copy()
    
    # Apply date filters
    if start_date:
        df = df[df['date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['date'] <= pd.to_datetime(end_date)]
    
    # Apply limit (most recent days)
    df = df.tail(limit)
    
    # Convert to JSON-friendly format
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    return {
        "success": True,
        "count": len(df),
        "data": df.to_dict(orient='records')
    }

@app.get("/api/metrics/weekly")
async def get_weekly_metrics(
    limit: int = Query(12, description="Number of recent weeks to return")
):
    """
    Get weekly aggregated metrics
    
    - **limit**: Number of recent weeks (default: 12)
    """
    if weekly_df is None:
        raise HTTPException(status_code=500, detail="Weekly data not loaded")
    
    df = weekly_df.tail(limit).copy()
    df['week'] = df['week'].dt.strftime('%Y-%m-%d')
    
    return {
        "success": True,
        "count": len(df),
        "data": df.to_dict(orient='records')
    }

@app.get("/api/metrics/kpis")
async def get_kpis(
    days: int = Query(30, description="Number of days to calculate KPIs")
):
    """
    Get Key Performance Indicators (KPIs)
    
    Returns current metrics with comparison to previous period
    """
    if daily_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    # Current period
    current_data = daily_df.tail(days)
    
    # Previous period (same length)
    previous_data = daily_df.tail(days * 2).head(days)
    
    # Calculate KPIs
    def calculate_change(current, previous):
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    
    # Total Revenue
    current_revenue = current_data['daily_revenue'].sum()
    previous_revenue = previous_data['daily_revenue'].sum()
    revenue_change = calculate_change(current_revenue, previous_revenue)
    
    # Total Orders
    current_orders = current_data['orders'].sum()
    previous_orders = previous_data['orders'].sum()
    orders_change = calculate_change(current_orders, previous_orders)
    
    # Active Customers (average)
    current_customers = current_data['active_customers'].mean()
    previous_customers = previous_data['active_customers'].mean()
    customers_change = calculate_change(current_customers, previous_customers)
    
    # Average Order Value
    current_aov = current_data['avg_order_value'].mean()
    previous_aov = previous_data['avg_order_value'].mean()
    aov_change = calculate_change(current_aov, previous_aov)
    
    # Churn Rate (average)
    current_churn = current_data['churn_rate'].mean()
    previous_churn = previous_data['churn_rate'].mean()
    churn_change = calculate_change(current_churn, previous_churn)
    
    return {
        "success": True,
        "period_days": days,
        "kpis": {
            "total_revenue": {
                "value": round(current_revenue, 2),
                "change_percent": round(revenue_change, 2),
                "previous_value": round(previous_revenue, 2)
            },
            "total_orders": {
                "value": int(current_orders),
                "change_percent": round(orders_change, 2),
                "previous_value": int(previous_orders)
            },
            "active_customers": {
                "value": int(current_customers),
                "change_percent": round(customers_change, 2),
                "previous_value": int(previous_customers)
            },
            "avg_order_value": {
                "value": round(current_aov, 2),
                "change_percent": round(aov_change, 2),
                "previous_value": round(previous_aov, 2)
            },
            "churn_rate": {
                "value": round(current_churn, 2),
                "change_percent": round(churn_change, 2),
                "previous_value": round(previous_churn, 2),
                "unit": "%"
            }
        }
    }

@app.get("/api/metrics/summary")
async def get_summary():
    """Get overall summary statistics"""
    if daily_df is None:
        raise HTTPException(status_code=500, detail="Data not loaded")
    
    return {
        "success": True,
        "date_range": {
            "start": daily_df['date'].min().strftime('%Y-%m-%d'),
            "end": daily_df['date'].max().strftime('%Y-%m-%d'),
            "total_days": len(daily_df)
        },
        "totals": {
            "revenue": round(daily_df['daily_revenue'].sum(), 2),
            "orders": int(daily_df['orders'].sum()),
            "sales_units": int(daily_df['sales_units'].sum()),
            "new_customers": int(daily_df['new_customers'].sum()),
            "churned_customers": int(daily_df['churned_customers'].sum())
        },
        "averages": {
            "daily_revenue": round(daily_df['daily_revenue'].mean(), 2),
            "daily_orders": round(daily_df['orders'].mean(), 2),
            "active_customers": int(daily_df['active_customers'].mean()),
            "churn_rate": round(daily_df['churn_rate'].mean(), 2)
        }
    }
forecast_router = APIRouter(prefix="/api/forecast", tags=["Forecasting"])

@forecast_router.get("/revenue")
async def forecast_revenue(periods: int = Query(30, description="Number of days to forecast")):
    """Forecast future revenue"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        forecast_data = forecaster.forecast_revenue(daily_df, periods)
        return {"success": True, "metric": "daily_revenue", "forecast": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@forecast_router.get("/orders")
async def forecast_orders(periods: int = Query(30)):
    """Forecast future orders"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        forecast_data = forecaster.forecast_orders(daily_df, periods)
        return {"success": True, "metric": "orders", "forecast": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@forecast_router.get("/customers")
async def forecast_customers(periods: int = Query(30)):
    """Forecast active customers"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        forecast_data = forecaster.forecast_customers(daily_df, periods)
        return {"success": True, "metric": "active_customers", "forecast": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@forecast_router.get("/churn")
async def forecast_churn(periods: int = Query(30)):
    """Forecast churn rate"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        forecast_data = forecaster.forecast_churn_rate(daily_df, periods)
        return {"success": True, "metric": "churn_rate", "forecast": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@forecast_router.get("/all")
async def forecast_all(periods: int = Query(30)):
    """Comprehensive forecast for all key metrics"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        result = forecaster.get_forecast_summary(daily_df, periods)
        return {"success": True, "forecasts": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@forecast_router.get("/accuracy")
async def forecast_accuracy(metric: str = Query("daily_revenue"), test_days: int = Query(14)):
    """Calculate forecast accuracy using recent data"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        result = forecaster.backtest_forecast(daily_df, metric=metric, test_days=test_days)
        return {"success": True, "metric": metric, "accuracy": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Register forecast router
app.include_router(forecast_router)
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Analytics Dashboard API...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Interactive API: http://localhost:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000)