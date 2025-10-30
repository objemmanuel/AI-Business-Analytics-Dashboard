import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { DailyMetric } from '../services/api';

// Color palettes
const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

interface CustomerDistributionChartProps {
  data: DailyMetric[];
  loading?: boolean;
}

export const CustomerDistributionChart: React.FC<CustomerDistributionChartProps> = ({
  data,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-80 bg-gray-100 rounded"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Status</h3>
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  const latestData = data[data.length - 1];
  const pieData = [
    { name: 'Active Customers', value: latestData.active_customers },
    { name: 'New Customers', value: latestData.new_customers },
    { name: 'Churned', value: latestData.churned_customers },
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="text-sm font-semibold text-gray-900 mb-1">
            {payload[0].name}
          </p>
          <p className="text-sm" style={{ color: payload[0].fill }}>
            Count: {payload[0].value.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500">
            {((payload[0].value / pieData.reduce((a, b) => a + b.value, 0)) * 100).toFixed(1)}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 animate-slide-up">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Customer Distribution</h3>
        <span className="text-sm text-gray-500">Current Status</span>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={pieData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }: any) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
          >
            {pieData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

interface WeeklyComparisonChartProps {
  data: DailyMetric[];
  loading?: boolean;
}

export const WeeklyComparisonChart: React.FC<WeeklyComparisonChartProps> = ({
  data,
  loading = false,
}) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-80 bg-gray-100 rounded"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Comparison</h3>
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  // Group by week (last 4 weeks)
  const weeks = [];
  for (let i = 0; i < 4; i++) {
    const weekData = data.slice(i * 7, (i + 1) * 7);
    if (weekData.length > 0) {
      weeks.unshift({
        week: `Week ${4 - i}`,
        revenue: weekData.reduce((sum, day) => sum + day.daily_revenue, 0),
        orders: weekData.reduce((sum, day) => sum + day.orders, 0),
      });
    }
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="text-sm font-semibold text-gray-900 mb-2">{payload[0].payload.week}</p>
          <p className="text-sm text-green-600">Revenue: ${payload[0].value.toLocaleString()}</p>
          <p className="text-sm text-blue-600">Orders: {payload[1].value}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 animate-slide-up">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Weekly Performance</h3>
        <span className="text-sm text-gray-500">Last 4 Weeks</span>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={weeks}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="week" tick={{ fontSize: 12 }} stroke="#6b7280" />
          <YAxis
            yAxisId="left"
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar yAxisId="left" dataKey="revenue" fill="#10b981" name="Revenue" />
          <Bar yAxisId="right" dataKey="orders" fill="#3b82f6" name="Orders" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};