import React from 'react';
import { KPI } from '../services/api';

interface KPICardProps {
  title: string;
  value: string | number;
  change: number;
  icon: string;
  color: string;
  prefix?: string;
  suffix?: string;
}

const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  change,
  icon,
  color,
  prefix = '',
  suffix = '',
}) => {
  const isPositive = change >= 0;
  const isNegative = change < 0;

  // For churn rate, negative is good
  const isChurn = title.toLowerCase().includes('churn');
  const textColorClass = isChurn
    ? isNegative
      ? 'text-green-600'
      : 'text-red-600'
    : isPositive
    ? 'text-green-600'
    : 'text-red-600';

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-300 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <h3 className="text-2xl font-bold text-gray-900">
            {prefix}
            {typeof value === 'number' ? value.toLocaleString() : value}
            {suffix}
          </h3>
          <div className="flex items-center mt-2">
            <span className={`text-sm font-semibold ${textColorClass} flex items-center`}>
              {isPositive ? '↑' : '↓'} {Math.abs(change).toFixed(1)}%
            </span>
            <span className="text-xs text-gray-500 ml-2">vs last period</span>
          </div>
        </div>
        <div className={`text-4xl ${color}`}>{icon}</div>
      </div>
    </div>
  );
};

interface KPICardsProps {
  kpis: {
    total_revenue: KPI;
    total_orders: KPI;
    active_customers: KPI;
    avg_order_value: KPI;
    churn_rate: KPI;
  } | null;
  loading?: boolean;
}

const KPICards: React.FC<KPICardsProps> = ({ kpis, loading = false }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white rounded-lg shadow-md p-6 animate-pulse"
          >
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-1/3"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!kpis) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-8">
        <p className="text-yellow-800">No KPI data available</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <KPICard
        title="Total Revenue"
        value={kpis.total_revenue.value.toFixed(2)}
        change={kpis.total_revenue.change_percent}
        icon="💰"
        color="text-green-500"
        prefix="$"
      />
      <KPICard
        title="Total Orders"
        value={kpis.total_orders.value}
        change={kpis.total_orders.change_percent}
        icon="🛒"
        color="text-blue-500"
      />
      <KPICard
        title="Active Customers"
        value={kpis.active_customers.value}
        change={kpis.active_customers.change_percent}
        icon="👥"
        color="text-purple-500"
      />
      <KPICard
        title="Churn Rate"
        value={kpis.churn_rate.value.toFixed(2)}
        change={kpis.churn_rate.change_percent}
        icon="📉"
        color="text-red-500"
        suffix="%"
      />
    </div>
  );
};

export default KPICards;