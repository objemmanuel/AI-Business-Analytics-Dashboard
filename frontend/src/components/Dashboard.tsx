import React, { useState, useEffect } from 'react';
import { apiService, KPIResponse, DailyMetricsResponse, AllForecastsResponse } from '../services/api';
import KPICards from './KPICards';
import RevenueChart from './RevenueChart';
import ForecastChart from './ForecastChart';
import { CustomerDistributionChart, WeeklyComparisonChart } from './AdditionalCharts';
import ExportButtons from './ExportButtons';
import DateRangePicker from './DateRangePicker';
import { useTheme } from '../contexts/ThemeContext';

interface DashboardProps {
  user: any;
  onLogout: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ user, onLogout }) => {
  const [kpis, setKpis] = useState<KPIResponse | null>(null);
  const [dailyMetrics, setDailyMetrics] = useState<DailyMetricsResponse | null>(null);
  const [forecasts, setForecasts] = useState<AllForecastsResponse | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [forecastPeriod, setForecastPeriod] = useState(30);
  const [customDateRange, setCustomDateRange] = useState<{ start: string; end: string } | null>(null);

  const { isDarkMode, toggleDarkMode } = useTheme();

  // Fetch all data
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch KPIs and daily metrics (required)
      const [kpisData, metricsData] = await Promise.all([
        apiService.getKPIs(selectedPeriod),
        customDateRange
          ? apiService.getDailyMetrics(365, customDateRange.start, customDateRange.end)
          : apiService.getDailyMetrics(selectedPeriod),
      ]);

      setKpis(kpisData);
      setDailyMetrics(metricsData);

      // Try to fetch forecasts (optional - may fail on free tier)
      try {
        const forecastsData = await apiService.getAllForecasts(forecastPeriod);
        if (forecastsData.success) {
          setForecasts(forecastsData);
        } else {
          console.warn('Forecasting unavailable:', forecastsData.error);
          setForecasts(null);
        }
      } catch (forecastError) {
        console.warn('Forecast fetch failed:', forecastError);
        setForecasts(null);
      }
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
  }, [selectedPeriod, forecastPeriod, customDateRange]);

  // Refresh data every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      fetchData();
    }, 300000); // 5 minutes

    return () => clearInterval(interval);
  }, [selectedPeriod, forecastPeriod, customDateRange]);

  const handleDateRangeApply = (startDate: string, endDate: string) => {
    setCustomDateRange({ start: startDate, end: endDate });
  };

  const handleDateRangeReset = () => {
    setCustomDateRange(null);
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 max-w-md">
          <div className="flex items-center mb-3">
            <span className="text-2xl mr-3">⚠️</span>
            <h3 className="text-lg font-semibold text-red-900 dark:text-red-200">Error Loading Dashboard</h3>
          </div>
          <p className="text-red-700 dark:text-red-300 mb-4">{error}</p>
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
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                📊 AI Analytics Dashboard
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Welcome back, <span className="font-medium text-gray-700 dark:text-gray-300">{user?.full_name || user?.username || 'User'}</span> • Real-time business intelligence
              </p>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              {/* Dark Mode Toggle */}
              <button
                onClick={toggleDarkMode}
                className="flex items-center space-x-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-4 py-2 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors shadow-sm"
                title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              >
                <span>{isDarkMode ? '☀️' : '🌙'}</span>
                <span className="hidden sm:inline">{isDarkMode ? 'Light' : 'Dark'}</span>
              </button>

              {/* Refresh Button */}
              <button
                onClick={fetchData}
                disabled={loading}
                className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
              >
                <span>{loading ? '⏳' : '🔄'}</span>
                <span className="hidden sm:inline">{loading ? 'Loading...' : 'Refresh'}</span>
              </button>

              {/* Logout Button */}
              <button
                onClick={onLogout}
                className="flex items-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm"
                title="Logout"
              >
                <span>🚪</span>
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Controls */}
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 mb-6">
          {/* Period Selectors */}
          <div className="flex flex-wrap items-center gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mr-2">
                Historical Period:
              </label>
              <select
                value={selectedPeriod}
                onChange={(e) => {
                  setSelectedPeriod(Number(e.target.value));
                  setCustomDateRange(null);
                }}
                className="border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={60}>Last 60 days</option>
                <option value={90}>Last 90 days</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mr-2">
                Forecast Period:
              </label>
              <select
                value={forecastPeriod}
                onChange={(e) => setForecastPeriod(Number(e.target.value))}
                className="border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={7}>Next 7 days</option>
                <option value={14}>Next 14 days</option>
                <option value={30}>Next 30 days</option>
                <option value={60}>Next 60 days</option>
              </select>
            </div>
            <DateRangePicker onApply={handleDateRangeApply} onReset={handleDateRangeReset} />
          </div>

          {/* Export Buttons */}
          <ExportButtons days={selectedPeriod} />
        </div>

        {customDateRange && (
          <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <p className="text-sm text-blue-800 dark:text-blue-200">
              📅 Custom date range: {customDateRange.start} to {customDateRange.end}
            </p>
          </div>
        )}

        {/* KPI Cards */}
        <KPICards kpis={kpis?.kpis || null} loading={loading} />

        {/* Charts Grid - Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <RevenueChart data={dailyMetrics?.data || []} loading={loading} />
          {forecasts?.forecasts?.revenue ? (
            <ForecastChart
              forecastData={forecasts.forecasts.revenue}
              title="Revenue Forecast"
              loading={loading}
              color="#10b981"
              prefix="$"
            />
          ) : (
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 flex items-center justify-center">
              <div className="text-center">
                <span className="text-4xl mb-2 block">📊</span>
                <p className="text-sm text-yellow-800 dark:text-yellow-200 font-medium">
                  Forecasting temporarily unavailable
                </p>
                <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
                  (Free tier memory limitation)
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Charts Grid - Row 2: New Pie and Bar Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <CustomerDistributionChart data={dailyMetrics?.data || []} loading={loading} />
          <WeeklyComparisonChart data={dailyMetrics?.data || []} loading={loading} />
        </div>

        {/* Charts Grid - Row 3: More Forecasts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <ForecastChart
            forecastData={forecasts?.forecasts.orders || null}
            title="Orders Forecast"
            loading={loading}
            color="#3b82f6"
          />
          <ForecastChart
            forecastData={forecasts?.forecasts.customers || null}
            title="Customer Growth Forecast"
            loading={loading}
            color="#8b5cf6"
          />
        </div>

        {/* Forecast Summary */}
        {forecasts && !loading && (
          <div className="mt-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg shadow-md p-6 animate-fade-in">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              📈 Forecast Summary (Next {forecastPeriod} days)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Projected Revenue</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  ${forecasts.forecasts.summary.total_revenue.toLocaleString()}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Expected Orders</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {forecasts.forecasts.summary.total_orders.toLocaleString()}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Customers</p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {forecasts.forecasts.summary.avg_customers.toLocaleString()}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Avg Churn Rate</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {forecasts.forecasts.summary.avg_churn_rate.toFixed(2)}%
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-12 transition-colors">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500 dark:text-gray-400">
            AI Analytics Dashboard • Powered by FastAPI & Prophet ML • Last updated:{' '}
            {new Date().toLocaleString()}
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;