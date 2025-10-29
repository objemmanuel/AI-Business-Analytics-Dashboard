import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class BusinessForecaster:
    """ML Forecasting service using Facebook Prophet"""
    
    def __init__(self):
        self.models = {}
    
    def prepare_data(self, df, date_col, value_col):
        """
        Prepare data in Prophet format (ds, y)
        
        Args:
            df: DataFrame with historical data
            date_col: Name of date column
            value_col: Name of value column to forecast
        
        Returns:
            DataFrame with 'ds' and 'y' columns
        """
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(df[date_col]),
            'y': df[value_col]
        })
        return prophet_df
    
    def forecast_metric(self, df, date_col, value_col, periods=30, freq='D'):
        """
        Forecast a single metric
        
        Args:
            df: Historical data
            date_col: Date column name
            value_col: Value column to forecast
            periods: Number of periods to forecast
            freq: Frequency ('D' for daily, 'W' for weekly)
        
        Returns:
            Dictionary with forecast data
        """
        # Prepare data
        prophet_df = self.prepare_data(df, date_col, value_col)
        
        # Initialize and train model
        model = Prophet(
            daily_seasonality=True if freq == 'D' else False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05,  # Flexibility of trend changes
            seasonality_prior_scale=10.0    # Flexibility of seasonality
        )
        
        model.fit(prophet_df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=periods, freq=freq)
        
        # Make predictions
        forecast = model.predict(future)
        
        # Extract relevant columns
        result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
        
        # Calculate confidence interval width (uncertainty metric)
        result['uncertainty'] = result['yhat_upper'] - result['yhat_lower']
        
        return {
            'dates': result['ds'].dt.strftime('%Y-%m-%d').tolist(),
            'predictions': result['yhat'].round(2).tolist(),
            'lower_bound': result['yhat_lower'].round(2).tolist(),
            'upper_bound': result['yhat_upper'].round(2).tolist(),
            'uncertainty': result['uncertainty'].round(2).tolist()
        }
    
    def forecast_revenue(self, daily_df, periods=30):
        """Forecast daily revenue"""
        return self.forecast_metric(
            df=daily_df,
            date_col='date',
            value_col='daily_revenue',
            periods=periods,
            freq='D'
        )
    
    def forecast_orders(self, daily_df, periods=30):
        """Forecast daily orders"""
        forecast = self.forecast_metric(
            df=daily_df,
            date_col='date',
            value_col='orders',
            periods=periods,
            freq='D'
        )
        
        # Ensure orders are positive integers
        forecast['predictions'] = [max(0, int(x)) for x in forecast['predictions']]
        forecast['lower_bound'] = [max(0, int(x)) for x in forecast['lower_bound']]
        forecast['upper_bound'] = [max(0, int(x)) for x in forecast['upper_bound']]
        
        return forecast
    
    def forecast_customers(self, daily_df, periods=30):
        """Forecast active customers"""
        forecast = self.forecast_metric(
            df=daily_df,
            date_col='date',
            value_col='active_customers',
            periods=periods,
            freq='D'
        )
        
        # Ensure customers are positive integers
        forecast['predictions'] = [max(0, int(x)) for x in forecast['predictions']]
        forecast['lower_bound'] = [max(0, int(x)) for x in forecast['lower_bound']]
        forecast['upper_bound'] = [max(0, int(x)) for x in forecast['upper_bound']]
        
        return forecast
    
    def forecast_churn_rate(self, daily_df, periods=30):
        """Forecast churn rate"""
        # Only use recent data for churn (last 90 days) as it's more volatile
        recent_df = daily_df.tail(90)
        
        forecast = self.forecast_metric(
            df=recent_df,
            date_col='date',
            value_col='churn_rate',
            periods=periods,
            freq='D'
        )
        
        # Ensure churn rate is between 0 and 100
        forecast['predictions'] = [max(0, min(100, x)) for x in forecast['predictions']]
        forecast['lower_bound'] = [max(0, min(100, x)) for x in forecast['lower_bound']]
        forecast['upper_bound'] = [max(0, min(100, x)) for x in forecast['upper_bound']]
        
        return forecast
    
    def get_forecast_summary(self, daily_df, periods=30):
        """
        Get comprehensive forecast summary for all metrics
        
        Returns:
            Dictionary with forecasts for revenue, orders, customers, churn
        """
        print(f"📊 Generating {periods}-day forecast...")
        
        revenue_forecast = self.forecast_revenue(daily_df, periods)
        orders_forecast = self.forecast_orders(daily_df, periods)
        customers_forecast = self.forecast_customers(daily_df, periods)
        churn_forecast = self.forecast_churn_rate(daily_df, periods)
        
        # Calculate summary statistics
        total_forecasted_revenue = sum(revenue_forecast['predictions'])
        total_forecasted_orders = sum(orders_forecast['predictions'])
        avg_forecasted_customers = np.mean(customers_forecast['predictions'])
        avg_forecasted_churn = np.mean(churn_forecast['predictions'])
        
        return {
            'forecast_period_days': periods,
            'revenue': revenue_forecast,
            'orders': orders_forecast,
            'customers': customers_forecast,
            'churn_rate': churn_forecast,
            'summary': {
                'total_revenue': round(total_forecasted_revenue, 2),
                'total_orders': int(total_forecasted_orders),
                'avg_customers': int(avg_forecasted_customers),
                'avg_churn_rate': round(avg_forecasted_churn, 2)
            }
        }
    
    def calculate_accuracy_metrics(self, actual, predicted):
        """
        Calculate forecast accuracy metrics
        
        Returns:
            MAPE (Mean Absolute Percentage Error) and RMSE
        """
        actual = np.array(actual)
        predicted = np.array(predicted)
        
        # MAPE
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        
        # RMSE
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        # MAE
        mae = np.mean(np.abs(actual - predicted))
        
        return {
            'mape': round(mape, 2),
            'rmse': round(rmse, 2),
            'mae': round(mae, 2)
        }
    
    def backtest_forecast(self, daily_df, metric='daily_revenue', test_days=30):
        """
        Backtest forecast accuracy using last N days
        
        Args:
            daily_df: Historical data
            metric: Column name to test
            test_days: Number of days to hold out for testing
        
        Returns:
            Accuracy metrics
        """
        # Split data
        train_df = daily_df[:-test_days]
        test_df = daily_df[-test_days:]
        
        # Make forecast
        prophet_df = self.prepare_data(train_df, 'date', metric)
        
        model = Prophet(daily_seasonality=True, weekly_seasonality=True)
        model.fit(prophet_df)
        
        future = model.make_future_dataframe(periods=test_days, freq='D')
        forecast = model.predict(future)
        
        # Get predictions for test period
        predictions = forecast['yhat'].tail(test_days).values
        actuals = test_df[metric].values
        
        # Calculate metrics
        accuracy = self.calculate_accuracy_metrics(actuals, predictions)
        
        return {
            'metric': metric,
            'test_days': test_days,
            'accuracy': accuracy,
            'actual_values': actuals.tolist(),
            'predicted_values': predictions.tolist()
        }

# Create global instance
forecaster = BusinessForecaster()