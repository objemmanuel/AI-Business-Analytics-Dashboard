import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface KPI {
  value: number;
  change_percent: number;
  previous_value: number;
  unit?: string;
}

export interface KPIResponse {
  success: boolean;
  period_days: number;
  kpis: {
    total_revenue: KPI;
    total_orders: KPI;
    active_customers: KPI;
    avg_order_value: KPI;
    churn_rate: KPI;
  };
}

export interface DailyMetric {
  date: string;
  daily_revenue: number;
  orders: number;
  sales_units: number;
  active_customers: number;
  new_customers: number;
  churned_customers: number;
  churn_rate: number;
  avg_order_value: number;
}

export interface DailyMetricsResponse {
  success: boolean;
  count: number;
  data: DailyMetric[];
}

export interface ForecastData {
  dates: string[];
  predictions: number[];
  lower_bound: number[];
  upper_bound: number[];
  uncertainty: number[];
}

export interface ForecastResponse {
  success: boolean;
  metric: string;
  forecast: ForecastData;
}

export interface AllForecastsResponse {
  success: boolean;
  forecasts: {
    forecast_period_days: number;
    revenue: ForecastData;
    orders: ForecastData;
    customers: ForecastData;
    churn_rate: ForecastData;
    summary: {
      total_revenue: number;
      total_orders: number;
      avg_customers: number;
      avg_churn_rate: number;
    };
  };
}

// API Functions
export const apiService = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/');
    return response.data;
  },

  // Get KPIs
  getKPIs: async (days: number = 30): Promise<KPIResponse> => {
    const response = await api.get('/api/metrics/kpis', {
      params: { days },
    });
    return response.data;
  },

  // Get daily metrics
  getDailyMetrics: async (
    limit: number = 30,
    startDate?: string,
    endDate?: string
  ): Promise<DailyMetricsResponse> => {
    const response = await api.get('/api/metrics/daily', {
      params: { limit, start_date: startDate, end_date: endDate },
    });
    return response.data;
  },

  // Get weekly metrics
  getWeeklyMetrics: async (limit: number = 12) => {
    const response = await api.get('/api/metrics/weekly', {
      params: { limit },
    });
    return response.data;
  },

  // Get summary
  getSummary: async () => {
    const response = await api.get('/api/metrics/summary');
    return response.data;
  },

  // Forecast revenue
  forecastRevenue: async (periods: number = 30): Promise<ForecastResponse> => {
    const response = await api.get('/api/forecast/revenue', {
      params: { periods },
    });
    return response.data;
  },

  // Forecast orders
  forecastOrders: async (periods: number = 30): Promise<ForecastResponse> => {
    const response = await api.get('/api/forecast/orders', {
      params: { periods },
    });
    return response.data;
  },

  // Forecast customers
  forecastCustomers: async (periods: number = 30): Promise<ForecastResponse> => {
    const response = await api.get('/api/forecast/customers', {
      params: { periods },
    });
    return response.data;
  },

  // Forecast churn
  forecastChurn: async (periods: number = 30): Promise<ForecastResponse> => {
    const response = await api.get('/api/forecast/churn', {
      params: { periods },
    });
    return response.data;
  },

  // Get all forecasts
  getAllForecasts: async (periods: number = 30): Promise<AllForecastsResponse> => {
    const response = await api.get('/api/forecast/all', {
      params: { periods },
    });
    return response.data;
  },

  // Get forecast accuracy
  getForecastAccuracy: async (metric: string = 'daily_revenue', testDays: number = 14) => {
    const response = await api.get('/api/forecast/accuracy', {
      params: { metric, test_days: testDays },
    });
    return response.data;
  },
};

export default api;