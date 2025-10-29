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
  ComposedChart,
} from 'recharts';
import { ForecastData } from '../services/api';
import { format, parseISO } from 'date-fns';

interface ForecastChartProps {
  forecastData: ForecastData | null;
  title: string;
  loading?: boolean;
  color?: string;
  prefix?: string;
  suffix?: string;
}

const ForecastChart: React.FC<ForecastChartProps> = ({
  forecastData,
  title,
  loading = false,
  color = '#3b82f6',
  prefix = '',
  suffix = '',
}) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-80 bg-gray-100 rounded"></div>
      </div>
    );
  }

  if (!forecastData || forecastData.dates.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
        <p className="text-gray-500">No forecast data available</p>
      </div>
    );
  }

  // Format data for chart
  const chartData = forecastData.dates.map((date, index) => ({
    date: format(parseISO(date), 'MMM dd'),
    prediction: forecastData.predictions[index],
    lowerBound: forecastData.lower_bound[index],
    upperBound: forecastData.upper_bound[index],
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="text-sm font-semibold text-gray-900 mb-2">{data.date}</p>
          <p className="text-sm" style={{ color }}>
            Prediction: {prefix}
            {typeof data.prediction === 'number'
              ? data.prediction.toLocaleString()
              : data.prediction}
            {suffix}
          </p>
          <p className="text-sm text-gray-500">
            Range: {prefix}
            {data.lowerBound.toLocaleString()} - {data.upperBound.toLocaleString()}
            {suffix}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 animate-slide-up">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <div className="flex items-center space-x-2">
          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
            {forecastData.dates.length}-day forecast
          </span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={chartData}>
          <defs>
            <linearGradient id={`gradient-${title}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.1} />
              <stop offset="95%" stopColor={color} stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            tickFormatter={(value) => {
              if (value >= 1000) {
                return `${prefix}${(value / 1000).toFixed(0)}k${suffix}`;
              }
              return `${prefix}${value}${suffix}`;
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Area
            type="monotone"
            dataKey="upperBound"
            stroke="none"
            fill={`url(#gradient-${title})`}
            fillOpacity={0.3}
            name="Upper Bound"
          />
          <Area
            type="monotone"
            dataKey="lowerBound"
            stroke="none"
            fill={`url(#gradient-${title})`}
            fillOpacity={0.3}
            name="Lower Bound"
          />
          <Line
            type="monotone"
            dataKey="prediction"
            stroke={color}
            strokeWidth={3}
            dot={{ r: 3, fill: color }}
            name="Prediction"
          />
        </ComposedChart>
      </ResponsiveContainer>
      <div className="mt-4 flex items-center justify-center space-x-6 text-sm">
        <div className="flex items-center">
          <div
            className="w-3 h-3 rounded-full mr-2"
            style={{ backgroundColor: color }}
          ></div>
          <span className="text-gray-600">Forecast</span>
        </div>
        <div className="flex items-center">
          <div
            className="w-3 h-3 rounded-full mr-2 opacity-30"
            style={{ backgroundColor: color }}
          ></div>
          <span className="text-gray-600">Confidence Interval</span>
        </div>
      </div>
    </div>
  );
};

export default ForecastChart;