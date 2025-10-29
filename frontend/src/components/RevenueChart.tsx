import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts';
import { DailyMetric } from '../services/api';
import { format, parseISO } from 'date-fns';

interface RevenueChartProps {
  data: DailyMetric[];
  loading?: boolean;
}

const RevenueChart: React.FC<RevenueChartProps> = ({ data, loading = false }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-80 bg-gray-100 rounded"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Trend</h3>
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  // Format data for chart
  const chartData = data.map((item) => ({
    date: format(parseISO(item.date), 'MMM dd'),
    revenue: item.daily_revenue,
    orders: item.orders,
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="text-sm font-semibold text-gray-900 mb-2">
            {payload[0].payload.date}
          </p>
          <p className="text-sm text-green-600">
            Revenue: ${payload[0].value.toLocaleString()}
          </p>
          <p className="text-sm text-blue-600">
            Orders: {payload[1].value}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 animate-slide-up">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Revenue & Orders Trend</h3>
        <span className="text-sm text-gray-500">Last {data.length} days</span>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
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
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="revenue"
            stroke="#10b981"
            fillOpacity={1}
            fill="url(#colorRevenue)"
            name="Revenue"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="orders"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ r: 3 }}
            name="Orders"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RevenueChart;