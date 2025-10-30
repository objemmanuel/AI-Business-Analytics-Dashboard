from fastapi import APIRouter, Depends
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from io import BytesIO
import os
import sys

# Add services directory to path
sys.path.append(os.path.dirname(__file__))

# Import auth functions
try:
    from auth import (
        authenticate_user,
        create_access_token,
        get_current_active_user,
        Token,
        User,
        ACCESS_TOKEN_EXPIRE_MINUTES
    )
    AUTH_ENABLED = True
    print("✅ Authentication module loaded successfully")
except ImportError as e:
    print(f"⚠️ Warning: Authentication module not found: {e}")
    print("⚠️ Running without authentication")
    AUTH_ENABLED = False
    User = None
    get_current_active_user = lambda: None

# Import forecaster
try:
    from services.ml_forecasting import forecaster
    print("✅ Forecasting module loaded successfully")
except ImportError as e:
    print(f"⚠️ Warning: Forecasting module not found: {e}")
    forecaster = None

# Import PDF generator
try:
    from services.pdf_generator import pdf_generator
    print("✅ PDF generator loaded successfully")
except ImportError as e:
    print(f"⚠️ Warning: PDF generator not found: {e}")
    pdf_generator = None

app = FastAPI(
    title="AI Analytics Dashboard API",
    description="Business analytics API with ML forecasting",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "ai-business-analytics-dashboard-ik6.vercel.app/", 
        "https://*.vercel.app",  # Allow all Vercel deployments
        "*"  # Remove this in production and specify exact URL
    ],
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
    else:
        print(f"⚠️ Warning: {daily_path} not found")
    
    if os.path.exists(weekly_path):
        weekly_df = pd.read_csv(weekly_path)
        weekly_df['week'] = pd.to_datetime(weekly_df['week'])
        print(f"✅ Loaded {len(weekly_df)} weekly records")
    else:
        print(f"⚠️ Warning: {weekly_path} not found")

@app.get("/")
async def root():
    """API health check"""
    return {
        "status": "healthy",
        "message": "AI Analytics Dashboard API",
        "version": "1.0.0",
        "authentication": "enabled" if AUTH_ENABLED else "disabled",
        "endpoints": [
            "/api/auth/login",
            "/api/auth/me",
            "/api/metrics/daily",
            "/api/metrics/weekly",
            "/api/metrics/kpis",
            "/api/forecast/revenue",
            "/api/forecast/orders",
            "/api/forecast/customers",
            "/api/forecast/churn",
            "/api/forecast/all",
            "/docs"
        ]
    }

# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

if AUTH_ENABLED:
    @app.post("/api/auth/login", response_model=Token)
    async def login(form_data: OAuth2PasswordRequestForm = Depends()):
        """
        Login endpoint to get JWT token
        
        Demo credentials:
        - Username: admin, Password: admin123
        - Username: demo, Password: demo123
        """
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            }
        }

    @app.get("/api/auth/me")
    async def read_users_me(current_user: User = Depends(get_current_active_user)):
        """Get current user info"""
        return {
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name
        }
else:
    # Fallback endpoints when auth is disabled
    @app.post("/api/auth/login")
    async def login_disabled():
        return {"error": "Authentication is disabled. Install required packages."}
    
    @app.get("/api/auth/me")
    async def me_disabled():
        return {"error": "Authentication is disabled"}

# ============================================
# METRICS ENDPOINTS
# ============================================

@app.get("/api/metrics/daily")
async def get_daily_metrics(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(30, description="Number of recent days to return"),
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
    """Get daily metrics (revenue, orders, customers, etc.)"""
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
    limit: int = Query(12, description="Number of recent weeks to return"),
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
    """Get weekly aggregated metrics"""
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
    days: int = Query(30, description="Number of days to calculate KPIs"),
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
    """Get Key Performance Indicators (KPIs)"""
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
async def get_summary(
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
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

# ============================================
# FORECASTING ENDPOINTS
# ============================================

forecast_router = APIRouter(prefix="/api/forecast", tags=["Forecasting"])

@forecast_router.get("/revenue")
async def forecast_revenue(
    periods: int = Query(30, description="Number of days to forecast"),
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
    """Forecast future revenue"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        if forecaster is None:
            raise HTTPException(status_code=500, detail="Forecaster not available")
        forecast_data = forecaster.forecast_revenue(daily_df, periods)
        return {"success": True, "metric": "daily_revenue", "forecast": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@forecast_router.get("/orders")
async def forecast_orders(
    periods: int = Query(30),
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
    """Forecast future orders"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        if forecaster is None:
            raise HTTPException(status_code=500, detail="Forecaster not available")
        forecast_data = forecaster.forecast_orders(daily_df, periods)
        return {"success": True, "metric": "orders", "forecast": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@forecast_router.get("/customers")
async def forecast_customers(
    periods: int = Query(30),
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
    """Forecast active customers"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        if forecaster is None:
            raise HTTPException(status_code=500, detail="Forecaster not available")
        forecast_data = forecaster.forecast_customers(daily_df, periods)
        return {"success": True, "metric": "active_customers", "forecast": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@forecast_router.get("/churn")
async def forecast_churn(
    periods: int = Query(30),
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
    """Forecast churn rate"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        if forecaster is None:
            raise HTTPException(status_code=500, detail="Forecaster not available")
        forecast_data = forecaster.forecast_churn_rate(daily_df, periods)
        return {"success": True, "metric": "churn_rate", "forecast": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@forecast_router.get("/all")
async def forecast_all(
    periods: int = Query(30),
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
    """Comprehensive forecast for all key metrics"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        if forecaster is None:
            raise HTTPException(status_code=500, detail="Forecaster not available")
        result = forecaster.get_forecast_summary(daily_df, periods)
        return {"success": True, "forecasts": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@forecast_router.get("/accuracy")
async def forecast_accuracy(
    metric: str = Query("daily_revenue"),
    test_days: int = Query(14),
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
    """Calculate forecast accuracy using recent data"""
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Daily data not loaded")
        if forecaster is None:
            raise HTTPException(status_code=500, detail="Forecaster not available")
        result = forecaster.backtest_forecast(daily_df, metric=metric, test_days=test_days)
        return {"success": True, "metric": metric, "accuracy": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Register forecast router
app.include_router(forecast_router)

# ============================================
# EXPORT ENDPOINTS
# ============================================

@app.get("/api/export/pdf")
async def export_pdf(
    days: int = Query(30, description="Number of days to include in report"),
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
    """
    Export dashboard data as PDF report
    """
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Data not loaded")
        if pdf_generator is None:
            raise HTTPException(status_code=500, detail="PDF generator not available")
        
        # Get data
        current_data = daily_df.tail(days)
        previous_data = daily_df.tail(days * 2).head(days)
        
        # Calculate KPIs
        def calculate_change(current, previous):
            if previous == 0:
                return 0
            return ((current - previous) / previous) * 100
        
        kpis = {
            'total_revenue': {
                'value': current_data['daily_revenue'].sum(),
                'change_percent': calculate_change(
                    current_data['daily_revenue'].sum(),
                    previous_data['daily_revenue'].sum()
                ),
                'previous_value': previous_data['daily_revenue'].sum()
            },
            'total_orders': {
                'value': int(current_data['orders'].sum()),
                'change_percent': calculate_change(
                    current_data['orders'].sum(),
                    previous_data['orders'].sum()
                ),
                'previous_value': int(previous_data['orders'].sum())
            },
            'active_customers': {
                'value': int(current_data['active_customers'].mean()),
                'change_percent': calculate_change(
                    current_data['active_customers'].mean(),
                    previous_data['active_customers'].mean()
                ),
                'previous_value': int(previous_data['active_customers'].mean())
            },
            'avg_order_value': {
                'value': current_data['avg_order_value'].mean(),
                'change_percent': calculate_change(
                    current_data['avg_order_value'].mean(),
                    previous_data['avg_order_value'].mean()
                ),
                'previous_value': previous_data['avg_order_value'].mean()
            },
            'churn_rate': {
                'value': current_data['churn_rate'].mean(),
                'change_percent': calculate_change(
                    current_data['churn_rate'].mean(),
                    previous_data['churn_rate'].mean()
                ),
                'previous_value': previous_data['churn_rate'].mean()
            }
        }
        
        # Get daily metrics as list
        daily_metrics = current_data.to_dict('records')
        
        # Get forecast summary if available
        forecast_summary = None
        if forecaster:
            forecast_data = forecaster.get_forecast_summary(daily_df, periods=30)
            forecast_summary = forecast_data['summary']
        
        # Generate PDF
        pdf_buffer = pdf_generator.generate_report(
            kpis=kpis,
            daily_metrics=daily_metrics,
            forecast_summary=forecast_summary,
            period_days=days
        )
        
        # Return as downloadable file
        filename = f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")

@app.get("/api/export/csv")
async def export_csv(
    days: int = Query(30, description="Number of days to export"),
    current_user: User = Depends(get_current_active_user) if AUTH_ENABLED else None
):
    """
    Export daily metrics as CSV file
    """
    try:
        if daily_df is None:
            raise HTTPException(status_code=500, detail="Data not loaded")
        
        # Get data
        export_data = daily_df.tail(days).copy()
        export_data['date'] = export_data['date'].dt.strftime('%Y-%m-%d')
        
        # Convert to CSV
        csv_buffer = BytesIO()
        export_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # Return as downloadable file
        filename = f"dashboard_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        return StreamingResponse(
            csv_buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("🚀 Starting AI Analytics Dashboard API")
    print("="*60)
    print(f"✅ Authentication: {'Enabled' if AUTH_ENABLED else 'Disabled'}")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Interactive API: http://localhost:8000/redoc")
    if AUTH_ENABLED:
        print("\n🔐 Demo Credentials:")
        print("   Admin: admin / admin123")
        print("   Demo:  demo / demo123")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000)