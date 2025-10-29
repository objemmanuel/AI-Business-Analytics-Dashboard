import React, { useState, useEffect } from 'react';
import { apiService, KPIResponse, DailyMetricsResponse, AllForecastsResponse } from '../services/api';
import KPICards from './KPICards';
import RevenueChart from './RevenueChart';
import ForecastChart from './ForecastChart';

const Dashboard: React.FC = () => {
  const [kpis, setKpis] = useState<KPIResponse | null>(null);
  const [dailyMetrics, setDailyMetrics] = useState<DailyMetricsResponse | null>(null);
  const [forecasts, setForecasts] = useState<AllForecastsResponse | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [forecastPeriod, setForecastPeriod] = useState(30);

  // Fetch all data
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch KPIs, daily metrics, and forecasts in parallel
      const [kpisData, metricsData, forecastsData] = await Promise.all([
        apiService.getKPIs(selectedPeriod),
        apiService.getDailyMetrics(selectedPeriod),
        apiService.getAllForecasts(forecastPeriod),
      ]);

      setKpis(kpisData);
      setDailyMetrics(metricsData);
      setForecasts(forecastsData);
    } catch (err: any) {
      console.error('Error fetching data:', err);
      setError(err.message || 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [selectedPeriod, forecastPeriod]);

  // Refresh data every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData();
    }, 300000); // 5 minutes

    return () => clearInterval(interval);
  }, [selectedPeriod, forecastPeriod]);

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <div className="flex items-center mb-3">
            <span className="text-2xl mr-3">⚠️</span>
            <h3 className="text-lg font-semibold text-red-900">Error Loading Dashboard</h3>
          </div>
          <p className="text-red-700 mb-4">{error}</p>
          <button
            onClick={fetchData}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                📊 AI Analytics Dashboard
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Real-time business intelligence with ML forecasting
              </p>
            </div>
            <button
              onClick={fetchData}
              disabled={loading}
              className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span>{loading ? '⏳' : '🔄'}</span>
              <span>{loading ? 'Loading...' : 'Refresh'}</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Period Selector */}
        <div className="flex items-center space-x-4 mb-6">
          <div>
            <label className="text-sm font-medium text-gray-700 mr-2">
              Historical Period:
            </label>
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(Number(e.target.value))}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={60}>Last 60 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mr-2">
              Forecast Period:
            </label>
            <select
              value={forecastPeriod}
              onChange={(e) => setForecastPeriod(Number(e.target.value))}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>Next 7 days</option>
              <option value={14}>Next 14 days</option>
              <option value={30}>Next 30 days</option>
              <option value={60}>Next 60 days</option>
            </select>
          </div>
        </div>

        {/* KPI Cards */}
        <KPICards kpis={kpis?.kpis || null} loading={loading} />

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Revenue Chart */}
          <RevenueChart
            data={dailyMetrics?.data || []}
            loading={loading}
          />

          {/* Revenue Forecast */}
          <ForecastChart
            forecastData={forecasts?.forecasts.revenue || null}
            title="Revenue Forecast"
            loading={loading}
            color="#10b981"
            prefix="$"
          />
        </div>

        {/* More Forecast Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Orders Forecast */}
          <ForecastChart
            forecastData={forecasts?.forecasts.orders || null}
            title="Orders Forecast"
            loading={loading}
            color="#3b82f6"
          />

          {/* Customers Forecast */}
          <ForecastChart
            forecastData={forecasts?.forecasts.customers || null}
            title="Customer Growth Forecast"
            loading={loading}
            color="#8b5cf6"
          />
        </div>

        {/* Forecast Summary */}
        {forecasts && !loading && (
          <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow-md p-6 animate-fade-in">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              📈 Forecast Summary (Next {forecastPeriod} days)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Projected Revenue</p>
                <p className="text-2xl font-bold text-green-600">
                  ${forecasts.forecasts.summary.total_revenue.toLocaleString()}
                </p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Expected Orders</p>
                <p className="text-2xl font-bold text-blue-600">
                  {forecasts.forecasts.summary.total_orders.toLocaleString()}
                </p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Avg Customers</p>
                <p className="text-2xl font-bold text-purple-600">
                  {forecasts.forecasts.summary.avg_customers.toLocaleString()}
                </p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-1">Avg Churn Rate</p>
                <p className="text-2xl font-bold text-red-600">
                  {forecasts.forecasts.summary.avg_churn_rate.toFixed(2)}%
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            AI Analytics Dashboard • Powered by FastAPI & Prophet ML • Last updated:{' '}
            {new Date().toLocaleString()}
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;